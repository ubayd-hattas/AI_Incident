"""V07 independent reference implementation of the conditional released-trace
state model, reasoned from ``docs/E06_IMPLEMENTATION_CONTRACT.md`` and the raw
pinned Collusion Wiki export directly.

Independence statement (recorded here, not hidden): this module imports
nothing from ``ebe`` -- no ``ebe.timeline``, no ``ebe.schema``, no
``TraceModel``, no shared helper of any kind. It re-parses the raw JSONL
itself and re-derives pinned-hash verification independently. The author
(Sam / this audit) had, in an earlier session, already read
``src/ebe/timeline.py`` in full while auditing it directly -- so this is not
a blind-from-birth implementation in the strictest possible sense, and that
exposure is disclosed in ``audit/V07_BLIND_VALIDATION.md``. What this module
does NOT do is import, call, wrap, or delegate to any part of the main
implementation. Every transition rule below is re-derived from the contract
text and cross-checked against raw records, not copied from Ubayd's code.

This module intentionally implements no collector, storage, evidence-scoring,
or policy-simulation behavior. It answers exactly one question: given the
raw pinned export, what does the conditional released-trace model say the
state of a page was at a given timestamp.
"""

from __future__ import annotations

import gzip
import hashlib
import itertools
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Literal

HORIZON_START = datetime(2026, 5, 24, tzinfo=timezone.utc)
HORIZON_END = datetime(2026, 7, 15, tzinfo=timezone.utc)

PINNED_HASHES = {
    "pages.jsonl": "92b296170b496b836cdf5ef783bed9465d2d75db7e1a0becec1c36c8b7c42cfd",
    "revisions.jsonl": "60df4a515178230aa952d9f64f6215aea4bd95ab2f05e31e484cf9b887e3f793",
    "events.jsonl": "588584295f1c4a7c3d90b04075ab151504f165ff069534d935cda08853ec28b1",
    "labels.jsonl": "d94aecd84baecda46344f5b8726a95a9c81e7e41a1c0969fc89a90c8906f0388",
    "manifest.json": "b6d53e16b5d9a6a0a98d4577238835ee7a574d7d10a8f1312330b4e626c6ba2b",
}


class ReplayError(RuntimeError):
    """Raised for any input this independent reference will not model."""


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_jsonl(path: Path) -> list[dict]:
    opener = gzip.open if path.suffix == ".gz" else open
    rows: list[dict] = []
    with opener(path, "rt", encoding="utf-8") as handle:  # type: ignore[arg-type]
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


# --------------------------------------------------------------------------
# State model -- independently defined, not imported from ebe.
# --------------------------------------------------------------------------

StateKind = Literal["unknown", "live_body_ref", "live_body_unknown", "deleted"]


@dataclass(frozen=True)
class ReplayState:
    kind: StateKind
    rev_id: str | None = None
    body_sha256: str | None = None

    def __post_init__(self) -> None:
        if (self.kind == "live_body_ref") != (self.rev_id is not None):
            raise ValueError("only live_body_ref carries a revision reference")


UNKNOWN = ReplayState("unknown")
DELETED = ReplayState("deleted")
BODY_UNKNOWN = ReplayState("live_body_unknown")


@dataclass(frozen=True)
class Mutation:
    event_id: str
    page_key: str
    selected_time: datetime
    uncertainty_seconds: int
    kind: Literal["held_save", "successful_deletion", "body_unknown_mutation"]
    result_state: ReplayState

    @property
    def earliest(self) -> datetime:
        return self.selected_time - timedelta(seconds=self.uncertainty_seconds)

    @property
    def latest(self) -> datetime:
        return self.selected_time + timedelta(seconds=self.uncertainty_seconds)


@dataclass(frozen=True)
class ArchiveMarker:
    """An inspectable no-op. Never consulted by state_at."""

    rev_id: str
    timestamp: datetime


@dataclass(frozen=True)
class Alternative:
    state: ReplayState
    episode_active: bool
    """True iff a live/body-unknown episode is currently open on this branch."""
    episode_started_at: str | None
    """event_id of the mutation that (re)opened the current episode, or None."""
    applied_order: tuple[str, ...]
    """event_ids in the order this branch actually applied them -- provenance,
    never used to pick a winner."""


@dataclass(frozen=True)
class ReplayQuery:
    page_key: str
    timestamp: datetime
    mode: Literal["nominal", "uncertainty"]
    alternatives: tuple[Alternative, ...]

    @property
    def is_ambiguous(self) -> bool:
        return len({(a.state.kind, a.state.rev_id) for a in self.alternatives}) > 1

    @property
    def distinct_states(self) -> set[tuple[str, str | None]]:
        return {(a.state.kind, a.state.rev_id) for a in self.alternatives}


class Export:
    """Raw pinned records, parsed independently. No ebe types anywhere."""

    def __init__(self, root: Path, *, verify_pinned: bool = True) -> None:
        self.root = Path(root)
        if verify_pinned:
            for name, expected in PINNED_HASHES.items():
                path = self.root / name
                if not path.is_file():
                    raise ReplayError(f"missing pinned file: {path}")
                actual = _sha256_file(path)
                if actual != expected:
                    raise ReplayError(f"{name}: hash mismatch (expected {expected}, got {actual})")
        self.revisions = _read_jsonl(self.root / "revisions.jsonl")
        self.events = _read_jsonl(self.root / "events.jsonl")
        self._revisions_by_id = {r["rev_id"]: r for r in self.revisions}

    def revision(self, rev_id: str) -> dict:
        return self._revisions_by_id[rev_id]


class ReplayModel:
    """Independent conditional released-trace model over a raw ``Export``."""

    def __init__(self, export: Export, *, max_branches: int = 5000) -> None:
        self.export = export
        self.max_branches = max_branches
        self._mutations: dict[str, list[Mutation]] = {}
        self._markers: dict[str, list[ArchiveMarker]] = {}
        self._build()

    # -- construction --------------------------------------------------

    def _build(self) -> None:
        for event in self.export.events:
            if event.get("wiki") != "dse":
                continue
            page_key = event.get("page_key")
            if page_key is None:
                continue  # probes and any page-less record are not mutations
            mutation = self._classify(event)
            if mutation is not None:
                self._mutations.setdefault(page_key, []).append(mutation)
        for revision in self.export.revisions:
            if revision.get("wiki") != "dse":
                continue
            archived = revision.get("archived_at")
            if archived is None:
                continue
            self._markers.setdefault(revision["page_key"], []).append(
                ArchiveMarker(revision["rev_id"], _parse_time(archived))
            )
        for key, muts in self._mutations.items():
            muts.sort(key=lambda m: (m.selected_time, m.event_id))

    def _classify(self, event: dict) -> Mutation | None:
        event_type = event.get("event_type")
        page_key = event["page_key"]
        event_id = event["event_id"]
        selected_time = _parse_time(event["time"])

        if event_type == "probe":
            return None

        if event_type == "save":
            rev_id = event.get("revision_ref")
            if not rev_id:
                raise ReplayError(f"{event_id}: save with no revision_ref")
            revision = self.export.revision(rev_id)
            uncertainty = revision.get("uncertainty_seconds")
            if not isinstance(uncertainty, int) or isinstance(uncertainty, bool) or uncertainty < 0:
                raise ReplayError(f"{event_id}: revision uncertainty is not a usable non-negative int")
            return Mutation(
                event_id, page_key, selected_time, uncertainty, "held_save",
                ReplayState("live_body_ref", rev_id, revision["body_sha256"]),
            )

        if event_type == "delete":
            if event.get("success_observed") is not True or event.get("request_action") != "delete":
                raise ReplayError(f"{event_id}: delete without confirmed successful delete action")
            uncertainty = event.get("uncertainty_seconds")
            if not isinstance(uncertainty, int) or isinstance(uncertainty, bool) or uncertainty < 0:
                raise ReplayError(f"{event_id}: event uncertainty is not a usable non-negative int")
            return Mutation(event_id, page_key, selected_time, uncertainty, "successful_deletion", DELETED)

        if event_type == "revert":
            if not (
                event.get("success_observed") is True
                and event.get("request_action") == "form_edit"
                and event.get("revision_ref") is None
            ):
                raise ReplayError(f"{event_id}: 'revert' event does not match the audited bodyless mutation shape")
            uncertainty = event.get("uncertainty_seconds")
            if not isinstance(uncertainty, int) or isinstance(uncertainty, bool) or uncertainty < 0:
                raise ReplayError(f"{event_id}: event uncertainty is not a usable non-negative int")
            return Mutation(event_id, page_key, selected_time, uncertainty, "body_unknown_mutation", BODY_UNKNOWN)

        raise ReplayError(f"{event_id}: unrecognized event_type {event_type!r} -- fail closed, do not guess")

    # -- public API ------------------------------------------------------

    def markers(self, page_key: str) -> tuple[ArchiveMarker, ...]:
        return tuple(sorted(self._markers.get(page_key, ()), key=lambda m: (m.timestamp, m.rev_id)))

    def state_at(
        self, page_key: str, timestamp: datetime, *, mode: Literal["nominal", "uncertainty"] = "nominal"
    ) -> ReplayQuery:
        if timestamp.tzinfo is None:
            raise ReplayError("timestamp must be timezone-aware")
        timestamp = timestamp.astimezone(timezone.utc)
        if timestamp < HORIZON_START or timestamp > HORIZON_END:
            raise ReplayError(f"query {timestamp.isoformat()} is outside the frozen horizon")
        mutations = self._mutations.get(page_key, [])
        if mode == "nominal":
            alts = self._nominal(mutations, timestamp)
        elif mode == "uncertainty":
            alts = self._uncertainty(mutations, timestamp)
        else:
            raise ValueError("mode must be 'nominal' or 'uncertainty'")
        return ReplayQuery(page_key, timestamp, mode, tuple(alts))

    # -- nominal mode ------------------------------------------------------
    #
    # Only mutations with selected_time <= timestamp are eligible. They are
    # applied in ascending-time groups; within one exact-same-timestamp
    # group every source-permitted ordering is admissible (never resolved by
    # event ID, seq, or any other identifier). A later mutation always fully
    # replaces the state -- there is no partial/merge update anywhere in
    # this model -- so intra-group order only matters for (a) which member
    # ends up "last" within its own group and (b) episode bookkeeping, which
    # depends on the state each member sees as its immediate predecessor.

    def _nominal(self, mutations: list[Mutation], timestamp: datetime) -> list[Alternative]:
        eligible = [m for m in mutations if m.selected_time <= timestamp]
        branches: list[Alternative] = [Alternative(UNKNOWN, False, None, ())]
        for group in _group_by_exact_time(eligible):
            branches = self._advance(branches, group)
        return _dedupe(branches)

    def _advance(self, branches: list[Alternative], group: list[Mutation]) -> list[Alternative]:
        if len(group) > 8:
            raise ReplayError(
                f"same-time group of {len(group)} mutations exceeds this reference's explicit review limit"
            )
        out: list[Alternative] = []
        for branch in branches:
            for order in itertools.permutations(group):
                updated = branch
                for mutation in order:
                    updated = _apply(updated, mutation)
                out.append(updated)
                if len(out) > self.max_branches:
                    raise ReplayError("branch explosion past configured review limit")
        return _dedupe(out)

    # -- uncertainty mode --------------------------------------------------
    #
    # Each mutation may have actually occurred anywhere in its own closed
    # [selected-u, selected+u] window. This reference only needs to support
    # small, mostly-isolated windows (the released fixtures have at most one
    # ambiguous deletion in flight at a time), so it merges mutations whose
    # windows transitively overlap, enumerates admissible occurred/excluded
    # splits against the query timestamp, and re-applies the same nominal
    # per-group permutation logic to each admissible occurred subsequence.

    def _uncertainty(self, mutations: list[Mutation], timestamp: datetime) -> list[Alternative]:
        groups = _overlap_groups(mutations)
        branches: list[Alternative] = [Alternative(UNKNOWN, False, None, ())]
        for group in groups:
            if min(m.earliest for m in group) > timestamp:
                continue
            forced = [m for m in group if m.latest <= timestamp]
            optional = [m for m in group if m.earliest <= timestamp < m.latest]
            excluded_always = [m for m in group if m.earliest > timestamp]
            admissible_orders: list[tuple[Mutation, ...]] = []
            for chosen in _power_set(optional):
                occurred = forced + list(chosen)
                not_occurred = [m for m in optional if m not in chosen] + excluded_always
                if any(nm.latest < om.earliest for nm in not_occurred for om in occurred):
                    continue  # a "not yet occurred" mutation whose deadline already
                    # passed before an "occurred" one could even start is a
                    # temporal contradiction -- discard this split.
                for order in itertools.permutations(occurred):
                    if _order_feasible(order, timestamp):
                        admissible_orders.append(order)
            if not admissible_orders:
                raise ReplayError("no admissible ordering for an overlapping mutation group")
            out: list[Alternative] = []
            for branch in branches:
                for order in admissible_orders:
                    updated = branch
                    for mutation in order:
                        updated = _apply(updated, mutation)
                    out.append(updated)
                    if len(out) > self.max_branches:
                        raise ReplayError("branch explosion past configured review limit")
            branches = _dedupe(out)
        return branches


def _apply(branch: Alternative, mutation: Mutation) -> Alternative:
    predecessor_open = branch.episode_active
    if mutation.kind == "successful_deletion":
        episode_active = False
        episode_started_at = None
    else:
        episode_active = True
        episode_started_at = branch.episode_started_at if predecessor_open else mutation.event_id
    return Alternative(
        mutation.result_state, episode_active, episode_started_at,
        branch.applied_order + (mutation.event_id,),
    )


def _dedupe(branches: Iterable[Alternative]) -> list[Alternative]:
    seen: dict[tuple, Alternative] = {}
    for branch in branches:
        key = (branch.state.kind, branch.state.rev_id, branch.episode_active, branch.episode_started_at)
        seen.setdefault(key, branch)
    return list(seen.values())


def _group_by_exact_time(mutations: list[Mutation]) -> Iterable[list[Mutation]]:
    ordered = sorted(mutations, key=lambda m: (m.selected_time, m.event_id))
    index = 0
    while index < len(ordered):
        boundary = ordered[index].selected_time
        end = index + 1
        while end < len(ordered) and ordered[end].selected_time == boundary:
            end += 1
        yield ordered[index:end]
        index = end


def _overlap_groups(mutations: list[Mutation]) -> list[list[Mutation]]:
    ordered = sorted(mutations, key=lambda m: (m.earliest, m.event_id))
    groups: list[list[Mutation]] = []
    for mutation in ordered:
        if groups and mutation.earliest <= max(m.latest for m in groups[-1]):
            groups[-1].append(mutation)
        else:
            groups.append([mutation])
    return groups


def _power_set(items: list[Mutation]) -> Iterable[tuple[Mutation, ...]]:
    for size in range(len(items) + 1):
        yield from itertools.combinations(items, size)


def _order_feasible(order: tuple[Mutation, ...], timestamp: datetime) -> bool:
    cursor: datetime | None = None
    for mutation in order:
        candidate = mutation.earliest if cursor is None else max(cursor, mutation.earliest)
        if candidate > min(mutation.latest, timestamp):
            return False
        cursor = candidate
    return True


# --------------------------------------------------------------------------
# CLI: run this file directly to sanity-check load + a handful of queries
# against the pinned export, independent of any ebe import.
# --------------------------------------------------------------------------

def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw_dir", type=Path)
    parser.add_argument("page_key")
    parser.add_argument("timestamp", help="ISO-8601 UTC, e.g. 2026-06-19T15:46:37Z")
    parser.add_argument("--mode", choices=["nominal", "uncertainty"], default="nominal")
    args = parser.parse_args()

    export = Export(args.raw_dir)
    model = ReplayModel(export)
    query = model.state_at(args.page_key, _parse_time(args.timestamp), mode=args.mode)
    print(f"page_key={query.page_key} t={query.timestamp.isoformat()} mode={query.mode}")
    print(f"is_ambiguous={query.is_ambiguous} n_alternatives={len(query.alternatives)}")
    for alt in query.alternatives:
        print(f"  state={alt.state.kind} rev_id={alt.state.rev_id} episode_active={alt.episode_active}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
