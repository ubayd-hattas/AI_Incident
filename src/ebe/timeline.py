"""Deterministic conditional released-trace timeline queries.

This module models only supported DSE mutations in the validated E05 export.  It
does not claim to reconstruct historical HTTP responses.  Carry-forward is the
explicit released-trace assumption that no unobserved intervening mutation
occurred.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from itertools import combinations, permutations
from bisect import bisect_right
from typing import Iterable, Iterator, Literal

from .schema import (
    EventRecord,
    NormalizedExport,
    ObservedEventSemantics,
    RelationEdge,
    RevisionRecord,
    SourceLocation,
)


HORIZON_START = datetime(2026, 5, 24, tzinfo=timezone.utc)
HORIZON_END = datetime(2026, 7, 15, tzinfo=timezone.utc)
MODEL_ID = "conditional-released-trace-v0.1"
CARRY_ASSUMPTION = "no-unobserved-intervening-mutation"


class TimelineError(RuntimeError):
    """Base class for explicit timeline failures."""


class OutOfHorizonError(TimelineError):
    """A query attempted to extrapolate outside the frozen horizon."""


class UnsupportedMutationError(TimelineError):
    """A source mutation cannot safely be assigned frozen E06 semantics."""


class AmbiguityLimitError(TimelineError):
    """Complete alternatives exceed the configured resource limit."""


class StateKind(str, Enum):
    UNKNOWN = "unknown"
    LIVE_BODY = "live_body_ref"
    LIVE_BODY_UNKNOWN = "live_body_unknown"
    DELETED = "deleted"


class TransitionKind(str, Enum):
    HELD_SAVE = "held_save"
    SUCCESSFUL_DELETION = "successful_deletion"
    BODY_UNKNOWN_MUTATION = "body_unknown_mutation"


@dataclass(frozen=True, slots=True)
class BodyReference:
    """An exact immutable E05 revision body and its source provenance."""

    rev_id: str
    body_sha256: str
    source_bytes: bytes
    source_encoding: str
    body: str
    source: SourceLocation


@dataclass(frozen=True, slots=True)
class PageState:
    kind: StateKind
    body_ref: BodyReference | None = None

    def __post_init__(self) -> None:
        if (self.kind is StateKind.LIVE_BODY) != (self.body_ref is not None):
            raise ValueError("only live(body_ref) may carry a body reference")


UNKNOWN = PageState(StateKind.UNKNOWN)
BODY_UNKNOWN = PageState(StateKind.LIVE_BODY_UNKNOWN)
DELETED = PageState(StateKind.DELETED)


@dataclass(frozen=True, slots=True)
class TimingWindow:
    selected_time: datetime
    earliest: datetime
    latest: datetime
    uncertainty_seconds: int
    convention: str


@dataclass(frozen=True, slots=True)
class TransitionProvenance:
    event_id: str
    revision_id: str | None
    page_key: str
    transition_kind: TransitionKind
    source: SourceLocation
    revision_source: SourceLocation | None
    body_sha256: str | None
    timing: TimingWindow
    relation_edges: tuple[RelationEdge, ...]
    relation_effect: Literal["none"] = "none"
    model_classification: str = "SAFE_ONLY_UNDER_RELEASED_TRACE_MODEL"


@dataclass(frozen=True, slots=True)
class AppliedTransition:
    provenance: TransitionProvenance
    predecessor: PageState
    successor: PageState
    episode_before: str | None
    episode_after: str | None


@dataclass(frozen=True, slots=True)
class TrajectoryConstraint:
    """A stable handle describing one admissible history prefix at a read."""

    trajectory_id: str
    applied_event_ids: tuple[str, ...]
    pending_event_ids: tuple[str, ...]
    ordering_choices: tuple[tuple[str, ...], ...]
    timing_convention: str


@dataclass(frozen=True, slots=True)
class Censoring:
    left_censored: bool
    observation_end: bool
    live_episode_right_censored: bool
    post_deletion_observation_censored: bool


@dataclass(frozen=True, slots=True)
class StateAlternative:
    state: PageState
    trajectory: TrajectoryConstraint
    transitions: tuple[AppliedTransition, ...]
    current_episode_id: str | None
    last_ended_episode_id: str | None
    censoring: Censoring
    carry_forward_assumption: str


@dataclass(frozen=True, slots=True)
class StateQuery:
    page_key: str
    timestamp: datetime
    mode: Literal["nominal", "uncertainty"]
    model_id: str
    alternatives: tuple[StateAlternative, ...]
    ambiguity_reasons: tuple[str, ...]

    @property
    def is_ambiguous(self) -> bool:
        return len(self.alternatives) > 1


@dataclass(frozen=True, slots=True)
class IgnoredMarker:
    marker_type: Literal["archival_clock"]
    timestamp: datetime
    revision_id: str
    source: SourceLocation
    reason: str = "archival clocks have no state-transition effect"


@dataclass(frozen=True, slots=True)
class _Mutation:
    event: EventRecord
    revision: RevisionRecord | None
    kind: TransitionKind
    state: PageState
    timing: TimingWindow

    @property
    def event_id(self) -> str:
        return self.event.event_id


@dataclass(frozen=True, slots=True)
class _Branch:
    state: PageState = UNKNOWN
    transitions: tuple[AppliedTransition, ...] = ()
    current_episode: str | None = None
    last_ended_episode: str | None = None
    ordering_choices: tuple[tuple[str, ...], ...] = ()
    pending: tuple[str, ...] = ()


class PageTimeline:
    """One opaque logical title's immutable mutation timeline."""

    def __init__(
        self,
        page_key: str,
        mutations: tuple[_Mutation, ...],
        ignored_markers: tuple[IgnoredMarker, ...],
        *,
        max_trajectories: int,
    ) -> None:
        self.page_key = page_key
        self._mutations = mutations
        self._selected_times = tuple(item.timing.selected_time for item in mutations)
        self._nominal_cache: dict[int, tuple[tuple[_Branch, ...], tuple[str, ...]]] = {}
        self.ignored_markers = ignored_markers
        self.max_trajectories = max_trajectories

    @property
    def transitions(self) -> tuple[TransitionProvenance, ...]:
        """Supported source mutations, serialized by time then ID only for inspection."""

        return tuple(_provenance(item) for item in self._mutations)

    def state_at(
        self, timestamp: datetime, *, mode: Literal["nominal", "uncertainty"] = "nominal"
    ) -> StateQuery:
        timestamp = _query_time(timestamp)
        if mode == "nominal":
            branches, reasons = self._nominal(timestamp)
        elif mode == "uncertainty":
            branches, reasons = self._uncertainty(timestamp)
        else:
            raise ValueError("mode must be 'nominal' or 'uncertainty'")
        return _query(self.page_key, timestamp, mode, branches, reasons)

    def _nominal(self, timestamp: datetime) -> tuple[list[_Branch], list[str]]:
        prefix = bisect_right(self._selected_times, timestamp)
        cached = self._nominal_cache.get(prefix)
        if cached is not None:
            branches, reasons = cached
            return list(branches), list(reasons)
        eligible = self._mutations[:prefix]
        branches = [_Branch()]
        reasons: list[str] = []
        index = 0
        while index < len(eligible):
            boundary = eligible[index].timing.selected_time
            end = index + 1
            while end < len(eligible) and eligible[end].timing.selected_time == boundary:
                end += 1
            group = eligible[index:end]
            orders = self._orders(group, timestamp, uncertainty=False)
            if len(orders) > 1:
                reasons.append(f"same-time group at {boundary.isoformat()} has source-permitted orderings")
            branches = self._extend(branches, orders, pending=())
            index = end
        self._nominal_cache[prefix] = (tuple(branches), tuple(reasons))
        return branches, reasons

    def nominal_interval_key(self, timestamp: datetime) -> int:
        """Return the immutable selected-time prefix containing ``timestamp``."""

        timestamp = _query_time(timestamp)
        return bisect_right(self._selected_times, timestamp)

    def _uncertainty(self, timestamp: datetime) -> tuple[list[_Branch], list[str]]:
        branches = [_Branch()]
        reasons: list[str] = []
        for group in _overlap_groups(self._mutations):
            if min(item.timing.earliest for item in group) > timestamp:
                continue
            required = tuple(item for item in group if item.timing.latest <= timestamp)
            optional = tuple(
                item for item in group
                if item.timing.earliest <= timestamp < item.timing.latest
            )
            impossible = tuple(item for item in group if item.timing.earliest > timestamp)
            orders: list[tuple[_Mutation, ...]] = []
            pending_by_order: list[tuple[str, ...]] = []
            for subset in _subsets(optional):
                occurred = required + subset
                excluded = tuple(item for item in optional if item not in subset) + impossible
                if any(
                    future.timing.latest < past.timing.earliest
                    for future in excluded for past in occurred
                ):
                    continue
                for order in self._orders(occurred, timestamp, uncertainty=True):
                    orders.append(order)
                    pending_by_order.append(tuple(sorted(item.event_id for item in excluded)))
            if not orders:
                raise UnsupportedMutationError("no admissible uncertainty trajectory for mutation group")
            if len(orders) > 1 or optional:
                reasons.append(
                    "closed uncertainty windows admit different occurred sets/orderings near "
                    f"{timestamp.isoformat()}"
                )
            expanded: list[_Branch] = []
            for branch in branches:
                for order, pending in zip(orders, pending_by_order):
                    updated = branch
                    for mutation in order:
                        updated = _apply(updated, mutation)
                    expanded.append(
                        replace(
                            updated,
                            ordering_choices=updated.ordering_choices + (tuple(x.event_id for x in order),),
                            pending=tuple(sorted(set(updated.pending).union(pending))),
                        )
                    )
                    self._check_limit(len(expanded))
            branches = expanded
        return branches, reasons

    def _orders(
        self, group: Iterable[_Mutation], timestamp: datetime, *, uncertainty: bool
    ) -> list[tuple[_Mutation, ...]]:
        members = tuple(group)
        if len(members) <= 1:
            return [members]
        if _factorial_over_limit(len(members), self.max_trajectories):
            raise AmbiguityLimitError(
                f"mutation group of {len(members)} may exceed limit {self.max_trajectories}"
            )
        output: list[tuple[_Mutation, ...]] = []
        for order in permutations(members):
            if uncertainty and not _feasible_order(order, timestamp):
                continue
            output.append(order)
            self._check_limit(len(output))
        return output

    def _extend(
        self, branches: list[_Branch], orders: list[tuple[_Mutation, ...]], *, pending: tuple[str, ...]
    ) -> list[_Branch]:
        output: list[_Branch] = []
        for branch in branches:
            for order in orders:
                updated = branch
                for mutation in order:
                    updated = _apply(updated, mutation)
                output.append(
                    replace(
                        updated,
                        ordering_choices=updated.ordering_choices + (tuple(x.event_id for x in order),),
                        pending=pending,
                    )
                )
                self._check_limit(len(output))
        return output

    def _check_limit(self, count: int) -> None:
        if count > self.max_trajectories:
            raise AmbiguityLimitError(
                f"complete ambiguity requires more than {self.max_trajectories} trajectories"
            )


class TraceModel:
    """Offline index over E05 records for conditional released-trace queries."""

    def __init__(self, export: NormalizedExport, *, max_trajectories: int = 10_000) -> None:
        if max_trajectories < 1:
            raise ValueError("max_trajectories must be positive")
        mutations: dict[str, list[_Mutation]] = {}
        markers: dict[str, list[IgnoredMarker]] = {}
        for event in export.events:
            if event.wiki != "dse" or event.page_key is None:
                continue
            mutation = _mutation(event, export)
            if mutation is not None:
                mutations.setdefault(event.page_key, []).append(mutation)
        for revision in export.revisions:
            if revision.wiki != "dse":
                continue
            markers.setdefault(revision.page_key, []).append(
                IgnoredMarker(
                    "archival_clock", revision.archived_at.utc, revision.rev_id, revision.source
                )
            )
        keys = set(mutations) | set(markers)
        self._timelines = {
            key: PageTimeline(
                key,
                tuple(sorted(mutations.get(key, ()), key=lambda x: (x.timing.selected_time, x.event_id))),
                tuple(sorted(markers.get(key, ()), key=lambda x: (x.timestamp, x.revision_id))),
                max_trajectories=max_trajectories,
            )
            for key in keys
        }
        self.max_trajectories = max_trajectories

    def timeline(self, page_key: str) -> PageTimeline:
        if not isinstance(page_key, str):
            raise TypeError("page_key must be an opaque string")
        return self._timelines.get(
            page_key, PageTimeline(page_key, (), (), max_trajectories=self.max_trajectories)
        )

    def state_at(
        self,
        page_key: str,
        timestamp: datetime,
        *,
        mode: Literal["nominal", "uncertainty"] = "nominal",
    ) -> StateQuery:
        return self.timeline(page_key).state_at(timestamp, mode=mode)

    def nominal_interval_key(self, page_key: str, timestamp: datetime) -> int:
        """Identify an exact nominal state interval without reconstructing it."""

        return self.timeline(page_key).nominal_interval_key(timestamp)


def build_timeline(
    export: NormalizedExport, page_key: str, *, max_trajectories: int = 10_000
) -> PageTimeline:
    return TraceModel(export, max_trajectories=max_trajectories).timeline(page_key)


def _mutation(event: EventRecord, export: NormalizedExport) -> _Mutation | None:
    revision: RevisionRecord | None = None
    if event.observed_semantics is ObservedEventSemantics.NON_MUTATION_PROBE:
        return None
    if event.observed_semantics is ObservedEventSemantics.HELD_BODY_SAVE:
        if event.revision_ref is None or event.revision_ref not in export.revisions_by_id:
            raise UnsupportedMutationError(f"{event.event_id}: held save has no resolvable revision")
        revision = export.revisions_by_id[event.revision_ref]
        uncertainty = revision.uncertainty_seconds
        kind = TransitionKind.HELD_SAVE
        state = PageState(
            StateKind.LIVE_BODY,
            BodyReference(
                revision.rev_id,
                revision.body_sha256,
                revision.source_body_bytes,
                revision.body_encoding.value,
                revision.body,
                revision.source,
            ),
        )
    elif event.observed_semantics is ObservedEventSemantics.SUCCESSFUL_DELETION:
        if event.success_observed is not True or event.request_action != "delete":
            raise UnsupportedMutationError(f"{event.event_id}: deletion outcome/action is unsupported")
        uncertainty = event.uncertainty_seconds
        kind = TransitionKind.SUCCESSFUL_DELETION
        state = DELETED
    elif event.observed_semantics is ObservedEventSemantics.BODY_UNKNOWN_FORM_EDIT:
        if not (
            event.success_observed is True
            and event.request_action == "form_edit"
            and event.revision_ref is None
        ):
            raise UnsupportedMutationError(f"{event.event_id}: bodyless mutation is not audited")
        uncertainty = event.uncertainty_seconds
        kind = TransitionKind.BODY_UNKNOWN_MUTATION
        state = BODY_UNKNOWN
    else:
        raise UnsupportedMutationError(f"{event.event_id}: unsupported observed semantics")
    if uncertainty is None or isinstance(uncertainty, bool) or uncertainty < 0:
        raise UnsupportedMutationError(f"{event.event_id}: uncertainty is review-required")
    selected = event.time.utc
    delta = timedelta(seconds=uncertainty)
    return _Mutation(
        event,
        revision,
        kind,
        state,
        TimingWindow(selected, selected - delta, selected + delta, uncertainty, "closed-project-sensitivity"),
    )


def _provenance(mutation: _Mutation) -> TransitionProvenance:
    return TransitionProvenance(
        mutation.event_id,
        mutation.revision.rev_id if mutation.revision else None,
        mutation.event.page_key or "",
        mutation.kind,
        mutation.event.source,
        mutation.revision.source if mutation.revision else None,
        mutation.revision.body_sha256 if mutation.revision else None,
        mutation.timing,
        mutation.event.relations.edges,
    )


def _apply(branch: _Branch, mutation: _Mutation) -> _Branch:
    predecessor = branch.state
    before = branch.current_episode
    current = before
    ended = branch.last_ended_episode
    if mutation.kind is TransitionKind.SUCCESSFUL_DELETION:
        if current is not None:
            ended = current
        current = None
    elif predecessor.kind in {StateKind.UNKNOWN, StateKind.DELETED}:
        current = f"episode:{mutation.event_id}"
    transition = AppliedTransition(
        _provenance(mutation), predecessor, mutation.state, before, current
    )
    return _Branch(
        mutation.state,
        branch.transitions + (transition,),
        current,
        ended,
        branch.ordering_choices,
        branch.pending,
    )


def _overlap_groups(mutations: tuple[_Mutation, ...]) -> Iterator[tuple[_Mutation, ...]]:
    ordered = sorted(mutations, key=lambda x: (x.timing.earliest, x.event_id))
    index = 0
    while index < len(ordered):
        group = [ordered[index]]
        latest = ordered[index].timing.latest
        index += 1
        while index < len(ordered) and ordered[index].timing.earliest <= latest:
            group.append(ordered[index])
            latest = max(latest, ordered[index].timing.latest)
            index += 1
        yield tuple(group)


def _subsets(items: tuple[_Mutation, ...]) -> Iterator[tuple[_Mutation, ...]]:
    for length in range(len(items) + 1):
        yield from combinations(items, length)


def _feasible_order(order: tuple[_Mutation, ...], timestamp: datetime) -> bool:
    cursor: datetime | None = None
    for item in order:
        selected = item.timing.earliest if cursor is None else max(cursor, item.timing.earliest)
        if selected > min(item.timing.latest, timestamp):
            return False
        cursor = selected
    return True


def _factorial_over_limit(size: int, limit: int) -> bool:
    product = 1
    for value in range(2, size + 1):
        product *= value
        if product > limit:
            return True
    return False


def _query_time(value: datetime) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError("timestamp must be a timezone-aware UTC datetime")
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError("timestamp must be timezone-aware UTC")
    value = value.astimezone(timezone.utc)
    if value < HORIZON_START or value > HORIZON_END:
        raise OutOfHorizonError(
            f"query {value.isoformat()} outside [{HORIZON_START.isoformat()}, {HORIZON_END.isoformat()}]"
        )
    return value


def _query(
    page_key: str,
    timestamp: datetime,
    mode: Literal["nominal", "uncertainty"],
    branches: list[_Branch],
    reasons: list[str],
) -> StateQuery:
    observation_end = timestamp == HORIZON_END
    alternatives: list[StateAlternative] = []
    for branch in branches:
        event_ids = tuple(item.provenance.event_id for item in branch.transitions)
        payload = repr((mode, event_ids, branch.pending, branch.ordering_choices)).encode("utf-8")
        trajectory = TrajectoryConstraint(
            "trajectory:" + sha256(payload).hexdigest()[:24],
            event_ids,
            branch.pending,
            branch.ordering_choices,
            "selected-time" if mode == "nominal" else "closed-plus-or-minus-u-project-sensitivity",
        )
        alternatives.append(
            StateAlternative(
                branch.state,
                trajectory,
                branch.transitions,
                branch.current_episode,
                branch.last_ended_episode,
                Censoring(
                    left_censored=True,
                    observation_end=observation_end,
                    live_episode_right_censored=observation_end
                    and branch.state.kind in {StateKind.LIVE_BODY, StateKind.LIVE_BODY_UNKNOWN},
                    post_deletion_observation_censored=observation_end
                    and branch.state.kind is StateKind.DELETED,
                ),
                CARRY_ASSUMPTION,
            )
        )
    alternatives.sort(key=lambda x: x.trajectory.trajectory_id)
    return StateQuery(page_key, timestamp, mode, MODEL_ID, tuple(alternatives), tuple(dict.fromkeys(reasons)))


__all__ = [
    "AmbiguityLimitError", "BODY_UNKNOWN", "BodyReference", "CARRY_ASSUMPTION",
    "DELETED", "HORIZON_END", "HORIZON_START", "IgnoredMarker", "MODEL_ID",
    "OutOfHorizonError", "PageState", "PageTimeline", "StateAlternative", "StateKind",
    "StateQuery", "TimelineError", "TraceModel", "TransitionKind", "TransitionProvenance",
    "UNKNOWN", "UnsupportedMutationError", "build_timeline",
]
