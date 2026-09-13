"""Conservative, deterministic support-interval compilation for U-stable."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Mapping, Any

UTC = timezone.utc


def _us(value: datetime) -> int:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamps must be timezone-aware")
    return int(value.timestamp() * 1_000_000)


@dataclass(frozen=True, slots=True)
class SupportState:
    support_id: str
    page_key: str
    body_sha256: str | None
    event_time: datetime
    uncertainty_us: int = 0
    state: str = "body"


@dataclass(frozen=True, slots=True)
class StableSupportInterval:
    support_id: str
    page_key: str
    body_sha256: str | None
    start_us: int | None
    end_us: int | None
    eligible: bool
    reason: str

    def contains(self, capture_time: datetime) -> bool:
        point = _us(capture_time)
        return bool(self.eligible and self.start_us is not None and
                    point >= self.start_us and (self.end_us is None or point < self.end_us))


def compile_stable_support_intervals(states: Iterable[SupportState], *,
                                     checkpoint: datetime | None = None) -> tuple[StableSupportInterval, ...]:
    ordered = sorted(states, key=lambda x: (x.page_key, _us(x.event_time), x.support_id))
    by_page: dict[str, list[SupportState]] = {}
    for item in ordered:
        if type(item.uncertainty_us) is not int or item.uncertainty_us < 0:
            raise ValueError("uncertainty_us must be a nonnegative integer")
        by_page.setdefault(item.page_key, []).append(item)
    cutoff = _us(checkpoint) if checkpoint else None
    result: list[StableSupportInterval] = []
    for page, items in sorted(by_page.items()):
        for index, item in enumerate(items):
            if item.state in {"unsupported", "incompatible"}:
                result.append(StableSupportInterval(item.support_id, page, item.body_sha256,
                    None, None, False, f"{item.state.upper()}_CHRONOLOGY"))
                continue
            if item.state != "body" or not item.body_sha256:
                result.append(StableSupportInterval(item.support_id, page, item.body_sha256,
                    None, None, False, "UNCERTIFIABLE_SUPPORT_IDENTITY"))
                continue
            start = _us(item.event_time) + item.uncertainty_us
            end: int | None = cutoff
            if index + 1 < len(items):
                nxt = items[index + 1]
                if nxt.state == "body" and nxt.body_sha256 == item.body_sha256:
                    # Equal canonical text certifies identity through the uncertain boundary.
                    end = _us(nxt.event_time) + nxt.uncertainty_us
                else:
                    end = _us(nxt.event_time) - nxt.uncertainty_us
            if cutoff is not None:
                end = cutoff if end is None else min(end, cutoff)
            eligible = end is None or start < end
            result.append(StableSupportInterval(item.support_id, page, item.body_sha256,
                start if eligible else None, end if eligible else None, eligible,
                "STABLE_EQUAL_TEXT_OR_SEPARATED_INTERVAL" if eligible else "EMPTY_UNCERTAINTY_INTERSECTION"))
    return tuple(result)


def write_stable_support_intervals(path: Path, intervals: Iterable[StableSupportInterval]) -> str:
    values = sorted(intervals, key=lambda x: (x.support_id, x.page_key, x.start_us or -1))
    payload = b"".join(json.dumps(asdict(value), ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode("utf-8") + b"\n" for value in values)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def mask_allows(intervals: Mapping[str, tuple[StableSupportInterval, ...]],
                support_id: str, capture_time: datetime) -> bool:
    return any(interval.contains(capture_time) for interval in intervals.get(support_id, ()))


def load_stable_mask(path: Path) -> dict[str, tuple[tuple[int, int | None], ...]]:
    result: dict[str, list[tuple[int, int | None]]] = {}
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            row=json.loads(line)
            if row.get("eligible"):
                result.setdefault(row["support_id"],[]).append((row["start_us"],row["end_us"]))
    return {key:tuple(sorted(value)) for key,value in result.items()}


def generate_stable_mask(repo: Path, output: Path) -> tuple[StableSupportInterval, ...]:
    """Derive occurrence intervals without collector outcomes or policy labels."""
    repo = repo.resolve()
    by_page: dict[str, list[SupportState]] = {}
    with (repo / "data/raw/export/revisions.jsonl").open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            if row.get("wiki") != "dse":
                continue
            raw = row["body"].encode("latin-1")
            codec = {"ascii": "ascii", "utf8": "utf-8", "latin1": "latin-1"}[
                row.get("body_encoding", "ascii")]
            canonical_hash = hashlib.sha256(
                raw.decode(codec, errors="strict").encode("utf-8")).hexdigest()
            event_time = datetime.fromisoformat(row["time"].replace("Z", "+00:00"))
            item = SupportState(
                row["rev_id"], row["page_key"], canonical_hash, event_time,
                int(row.get("uncertainty_seconds") or 0) * 1_000_000,
            )
            by_page.setdefault(row["page_key"], []).append(item)
    checkpoint = datetime.fromisoformat("2026-07-15T00:00:00+00:00")
    by_revision: dict[str, StableSupportInterval] = {}
    for states in by_page.values():
        for interval in compile_stable_support_intervals(states, checkpoint=checkpoint):
            by_revision[interval.support_id] = interval
    identities: list[tuple[str, str]] = []
    with (repo / "annotations/occurrences.jsonl").open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            identities.append((row["occurrence_id"], row["rev_id"]))
    with (repo / "annotations/context_occurrences.jsonl").open(encoding="utf-8") as stream:
        for index, line in enumerate(stream, 1):
            row = json.loads(line)
            identities.append((f"CTXOCC-{index:04d}:{row['context_fragment_id']}", row["rev_id"]))
    result: list[StableSupportInterval] = []
    for support_id, rev_id in sorted(identities):
        base = by_revision.get(rev_id)
        if base is None:
            item = StableSupportInterval(support_id, "", None, None, None, False,
                                         "UNSUPPORTED_SOURCE_REFERENCE")
        else:
            item = StableSupportInterval(support_id, base.page_key, base.body_sha256,
                base.start_us, base.end_us, base.eligible, base.reason)
        result.append(item)
    write_stable_support_intervals(output, result)
    return tuple(result)


__all__ = ["StableSupportInterval", "SupportState", "compile_stable_support_intervals",
           "generate_stable_mask", "load_stable_mask", "mask_allows", "write_stable_support_intervals"]
