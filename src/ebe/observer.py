"""Frozen content-free observer over the private E06 released-trace model.

This is a modeled monitored-wiki interface, not a reconstruction of historical
DSEWiki HTTP or API behaviour.  Collector-visible values intentionally contain
no E05/E06 provenance objects.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Literal

from .accounting import (
    MICROSECONDS_PER_HOUR,
    canonical_array,
    canonical_jsonl,
    elapsed_microseconds,
    format_timestamp,
    require_utc,
)
from .schema import NormalizedExport, ObservedEventSemantics
from .timeline import (
    HORIZON_END,
    HORIZON_START,
    AmbiguityLimitError,
    StateKind,
    TraceModel,
    UnsupportedMutationError,
)


class ObserverError(RuntimeError):
    """Base class for invalid observer operations."""


class PollScheduleError(ObserverError):
    """A feed poll was not on the frozen common schedule."""


class ObserverTimeError(ObserverError):
    """An observer operation was outside the modeled horizon/order."""


class DirectoryAmbiguityError(ObserverError):
    """Terminal live-directory membership was not uniquely supported."""


class BodyOutcome(str, Enum):
    BODY = "body"
    MISSING = "missing"
    UNKNOWN = "unknown"
    BODY_UNKNOWN = "body_unknown"
    AMBIGUOUS = "ambiguous"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True, slots=True)
class ObserverConfig:
    feed_publication_lag_us: int = 5_000_000
    feed_poll_interval_us: int = 60_000_000
    get_response_delay_us: int = 0

    def __post_init__(self) -> None:
        for name in (
            "feed_publication_lag_us",
            "feed_poll_interval_us",
            "get_response_delay_us",
        ):
            value = getattr(self, name)
            if type(value) is not int or value < 0:
                raise ValueError(f"{name} must be a nonnegative integer")
        if self.feed_poll_interval_us == 0:
            raise ValueError("feed_poll_interval_us must be positive")


@dataclass(frozen=True, slots=True)
class FeedRecord:
    action: Literal["live_change", "delete"]
    event_time: datetime
    page_key: str

    def __post_init__(self) -> None:
        require_utc(self.event_time, "event_time")
        if self.action not in {"live_change", "delete"}:
            raise ValueError("feed action is not frozen")
        if not isinstance(self.page_key, str):
            raise TypeError("page_key must be an opaque string")

    def as_dict(self) -> dict[str, str]:
        return {
            "action": self.action,
            "event_time": format_timestamp(self.event_time),
            "page_key": self.page_key,
        }

    @property
    def canonical_bytes(self) -> bytes:
        return canonical_jsonl(self.as_dict())


@dataclass(frozen=True, slots=True)
class FeedPollResult:
    poll_time: datetime
    records: tuple[FeedRecord, ...]
    response_bytes: bytes


@dataclass(frozen=True, slots=True)
class BodyResponse:
    page_key: str
    request_seq: int
    request_time: datetime
    response_time: datetime
    outcome: BodyOutcome
    header_bytes: bytes
    body: bytes | None


@dataclass(frozen=True, slots=True)
class PendingBodyRequest:
    page_key: str
    request_seq: int
    request_time: datetime
    response_time: datetime


@dataclass(frozen=True, slots=True)
class DirectoryResponse:
    request_time: datetime
    page_keys: tuple[str, ...]
    response_bytes: bytes


@dataclass(frozen=True, slots=True)
class ObserverAuditRecord:
    request_seq: int
    page_key: str
    request_time: datetime
    response_time: datetime | None
    outcome: str | None
    header_bytes: int
    body_bytes: int | None
    disposition: Literal["no_body", "available", "pending", "review_required"]


@dataclass(frozen=True, slots=True)
class ObserverCosts:
    feed_requests: int
    directory_requests: int
    body_requests: int
    successful_body_responses: int
    missing_responses: int
    unknown_responses: int
    body_unknown_responses: int
    ambiguous_responses: int
    unsupported_responses: int
    pending_body_requests: int
    downloaded_metadata_bytes: int
    downloaded_known_body_bytes: int
    unknown_body_byte_attempts: int
    known_downloaded_byte_lower_bound: int
    downloaded_total_bytes: int | None
    retained_shared_metadata_bytes: int
    peak_shared_metadata_bytes: int
    final_shared_metadata_bytes: int
    shared_metadata_byte_microseconds: int

    @property
    def shared_metadata_byte_hours(self) -> float:
        return self.shared_metadata_byte_microseconds / MICROSECONDS_PER_HOUR


@dataclass(frozen=True, slots=True)
class _FeedEntry:
    record: FeedRecord
    publication_time: datetime
    stable_index: int


class Observer:
    """Stateful feed/discovery/GET boundary hiding all TraceModel internals."""

    def __init__(self, export: NormalizedExport, *, config: ObserverConfig | None = None) -> None:
        self.config = config or ObserverConfig()
        self._trace = TraceModel(export)
        entries: list[_FeedEntry] = []
        lag = timedelta(microseconds=self.config.feed_publication_lag_us)
        candidate_keys: set[str] = set()
        for stable_index, event in enumerate(export.events):
            if event.wiki != "dse" or event.page_key is None:
                continue
            if event.observed_semantics is ObservedEventSemantics.NON_MUTATION_PROBE:
                continue
            if event.observed_semantics is ObservedEventSemantics.SUCCESSFUL_DELETION:
                action: Literal["live_change", "delete"] = "delete"
            elif event.observed_semantics in {
                ObservedEventSemantics.HELD_BODY_SAVE,
                ObservedEventSemantics.BODY_UNKNOWN_FORM_EDIT,
            }:
                action = "live_change"
            else:
                raise ObserverError(f"unsupported mutation semantics at source row {stable_index}")
            record = FeedRecord(action, event.time.utc, event.page_key)
            entries.append(_FeedEntry(record, event.time.utc + lag, stable_index))
            candidate_keys.add(event.page_key)
        self._feed = tuple(sorted(
            entries,
            key=lambda item: (
                item.publication_time,
                item.record.event_time,
                item.record.page_key,
                item.record.action,
                item.stable_index,
            ),
        ))
        self._candidate_keys = tuple(sorted(candidate_keys))
        self._feed_cursor = 0
        self._last_poll: datetime | None = None
        self._last_dispatch: datetime | None = None
        self._discovered: set[str] = set()
        self._request_seq = 0
        self._feed_requests = 0
        self._directory_requests = 0
        self._body_requests = 0
        self._outcomes = {outcome: 0 for outcome in BodyOutcome}
        self._pending = 0
        self._downloaded_metadata = 0
        self._non_body_metadata = 0
        self._downloaded_body = 0
        self._unknown_body_attempts = 0
        self._shared_metadata = 0
        self._peak_shared_metadata = 0
        self._metadata_byte_microseconds = 0
        self._metadata_time = HORIZON_START
        self._audit: list[ObserverAuditRecord] = []

    @property
    def discovered_titles(self) -> tuple[str, ...]:
        return tuple(sorted(self._discovered))

    @property
    def audit_records(self) -> tuple[ObserverAuditRecord, ...]:
        """Evaluator-only facts; collectors must not use these as retained state."""

        return tuple(self._audit)

    def _horizon_time(self, value: datetime, field: str) -> datetime:
        value = require_utc(value, field)
        if value < HORIZON_START or value > HORIZON_END:
            raise ObserverTimeError(f"{field} is outside the frozen replay horizon")
        return value

    def _advance_metadata(self, timestamp: datetime) -> None:
        delta = elapsed_microseconds(self._metadata_time, timestamp)
        if delta < 0:
            raise ObserverTimeError("metadata operations cannot move backward in time")
        self._metadata_byte_microseconds += self._shared_metadata * delta
        self._metadata_time = timestamp

    def _is_poll_time(self, timestamp: datetime) -> bool:
        offset = elapsed_microseconds(HORIZON_START, timestamp)
        return offset >= 0 and offset % self.config.feed_poll_interval_us == 0

    def poll_feed(self, poll_time: datetime) -> FeedPollResult:
        poll_time = self._horizon_time(poll_time, "poll_time")
        if not self._is_poll_time(poll_time):
            raise PollScheduleError("poll_time is not on the frozen epoch-aligned schedule")
        if self._last_poll is not None and poll_time <= self._last_poll:
            raise PollScheduleError("feed polls must be strictly increasing and deliver once")
        if self._directory_requests:
            raise ObserverError("terminal-directory and continuous-feed access cannot be mixed")
        self._advance_metadata(poll_time)
        self._last_poll = poll_time
        self._feed_requests += 1
        visible: list[FeedRecord] = []
        while self._feed_cursor < len(self._feed):
            entry = self._feed[self._feed_cursor]
            if entry.publication_time > poll_time:
                break
            visible.append(entry.record)
            self._feed_cursor += 1
        visible.sort(key=lambda item: (item.event_time, item.page_key, item.action))
        payload_values = [record.as_dict() for record in visible]
        response = canonical_array(payload_values)
        self._downloaded_metadata += len(response)
        self._non_body_metadata += len(response)
        for record in visible:
            self._discovered.add(record.page_key)
            self._shared_metadata += len(record.canonical_bytes)
        self._peak_shared_metadata = max(self._peak_shared_metadata, self._shared_metadata)
        return FeedPollResult(poll_time, tuple(visible), response)

    def _canonical_body(self, state_body_ref: object) -> bytes:
        source_bytes = state_body_ref.source_bytes  # type: ignore[attr-defined]
        encoding = state_body_ref.source_encoding  # type: ignore[attr-defined]
        if encoding == "ascii":
            text = source_bytes.decode("ascii", errors="strict")
        elif encoding in {"utf8", "utf-8"}:
            text = source_bytes.decode("utf-8", errors="strict")
        elif encoding in {"latin1", "latin-1"}:
            text = source_bytes.decode("latin-1", errors="strict")
        else:
            raise ObserverError(f"unsupported validated source body encoding {encoding!r}")
        return text.encode("utf-8")

    def _observe_state(self, page_key: str, response_time: datetime) -> tuple[BodyOutcome, bytes | None]:
        try:
            query = self._trace.state_at(page_key, response_time, mode="nominal")
        except (UnsupportedMutationError, AmbiguityLimitError):
            return BodyOutcome.UNSUPPORTED, None
        possibilities: set[tuple[BodyOutcome, bytes | None]] = set()
        for alternative in query.alternatives:
            state = alternative.state
            if state.kind is StateKind.LIVE_BODY:
                assert state.body_ref is not None
                possibilities.add((BodyOutcome.BODY, self._canonical_body(state.body_ref)))
            elif state.kind is StateKind.DELETED:
                possibilities.add((BodyOutcome.MISSING, None))
            elif state.kind is StateKind.LIVE_BODY_UNKNOWN:
                possibilities.add((BodyOutcome.BODY_UNKNOWN, None))
            else:
                possibilities.add((BodyOutcome.UNKNOWN, None))
        if len(possibilities) != 1:
            return BodyOutcome.AMBIGUOUS, None
        return next(iter(possibilities))

    def get_body(self, page_key: str, request_time: datetime) -> BodyResponse | PendingBodyRequest:
        if not isinstance(page_key, str):
            raise TypeError("page_key must be an opaque string")
        request_time = self._horizon_time(request_time, "request_time")
        if self._last_dispatch is not None and request_time < self._last_dispatch:
            raise ObserverTimeError("body requests must be dispatched in nondecreasing time order")
        if self._last_poll is not None and request_time < self._last_poll:
            raise ObserverTimeError(
                "body requests cannot be dispatched earlier than the most recent feed poll "
                "-- a caller must not use knowledge from a poll that, causally, has not happened yet"
            )
        self._last_dispatch = request_time
        self._request_seq += 1
        self._body_requests += 1
        request_seq = self._request_seq
        response_time = request_time + timedelta(microseconds=self.config.get_response_delay_us)
        if response_time > HORIZON_END:
            self._pending += 1
            self._audit.append(ObserverAuditRecord(
                request_seq, page_key, request_time, None, None, 0, None, "pending"
            ))
            return PendingBodyRequest(page_key, request_seq, request_time, response_time)

        if page_key not in self._discovered:
            outcome, body = BodyOutcome.UNKNOWN, None
        else:
            outcome, body = self._observe_state(page_key, response_time)
        header = canonical_jsonl({"outcome": outcome.value})
        self._outcomes[outcome] += 1
        self._downloaded_metadata += len(header)
        if outcome is BodyOutcome.BODY:
            assert body is not None
            self._downloaded_body += len(body)
            disposition: Literal["no_body", "available", "pending", "review_required"] = "available"
            body_length: int | None = len(body)
        elif outcome is BodyOutcome.MISSING:
            disposition = "no_body"
            body_length = 0
        else:
            disposition = "review_required" if outcome in {BodyOutcome.AMBIGUOUS, BodyOutcome.UNSUPPORTED} else "no_body"
            body_length = None
            self._unknown_body_attempts += 1
        self._audit.append(ObserverAuditRecord(
            request_seq, page_key, request_time, response_time, outcome.value,
            len(header), body_length, disposition,
        ))
        return BodyResponse(page_key, request_seq, request_time, response_time, outcome, header, body)

    def terminal_directory(self, request_time: datetime = HORIZON_END) -> DirectoryResponse:
        request_time = self._horizon_time(request_time, "request_time")
        if request_time != HORIZON_END:
            raise ObserverTimeError("the frozen directory exists only at terminal checkpoint T")
        if self._feed_requests:
            raise ObserverError("terminal-directory and continuous-feed access cannot be mixed")
        self._advance_metadata(request_time)
        live: list[str] = []
        for page_key in self._candidate_keys:
            query = self._trace.state_at(page_key, HORIZON_END, mode="nominal")
            memberships = {
                alternative.state.kind in {StateKind.LIVE_BODY, StateKind.LIVE_BODY_UNKNOWN}
                for alternative in query.alternatives
            }
            if len(memberships) != 1:
                raise DirectoryAmbiguityError(f"directory membership is ambiguous for {page_key!r}")
            if True in memberships:
                live.append(page_key)
        page_keys = tuple(sorted(set(live)))
        response = canonical_array(list(page_keys))
        self._directory_requests += 1
        self._downloaded_metadata += len(response)
        self._non_body_metadata += len(response)
        self._shared_metadata += len(response)
        self._peak_shared_metadata = max(self._peak_shared_metadata, self._shared_metadata)
        self._discovered.update(page_keys)
        return DirectoryResponse(request_time, page_keys, response)

    def costs(self, checkpoint: datetime | None = None) -> ObserverCosts:
        accrued = self._metadata_byte_microseconds
        if checkpoint is not None:
            checkpoint = self._horizon_time(checkpoint, "checkpoint")
            delta = elapsed_microseconds(self._metadata_time, checkpoint)
            if delta < 0:
                raise ObserverTimeError("checkpoint precedes retained metadata")
            accrued += self._shared_metadata * delta

        if checkpoint is None:
            # No checkpoint given: report the observer's own full, unconditional
            # history (unchanged from before -- every dispatched request that has
            # actually completed by HORIZON_END is counted).
            outcomes = self._outcomes
            pending = self._pending
            downloaded_metadata = self._downloaded_metadata
            downloaded_body = self._downloaded_body
            unknown = self._unknown_body_attempts
        else:
            # A response dispatched before `checkpoint` can still resolve strictly
            # after it (nonzero get_response_delay_us). From the checkpoint's own
            # vantage point that request is still PENDING -- not yet a known outcome,
            # not yet a downloaded byte -- even though the observer has, by now,
            # already computed and cached the real (later) outcome internally.
            # Recompute every checkpoint-sensitive field from the per-request audit
            # trail rather than trusting the eager, checkpoint-blind running
            # counters above, which only ever compared against HORIZON_END.
            outcomes = {outcome: 0 for outcome in BodyOutcome}
            pending = 0
            downloaded_metadata = self._non_body_metadata
            downloaded_body = 0
            unknown = 0
            for record in self._audit:
                if record.response_time is None or record.response_time > checkpoint:
                    pending += 1
                    continue
                outcome = BodyOutcome(record.outcome)
                outcomes[outcome] += 1
                downloaded_metadata += record.header_bytes
                if outcome is BodyOutcome.BODY:
                    downloaded_body += record.body_bytes or 0
                elif outcome is not BodyOutcome.MISSING:
                    unknown += 1

        lower = downloaded_metadata + downloaded_body
        return ObserverCosts(
            self._feed_requests,
            self._directory_requests,
            self._body_requests,
            outcomes[BodyOutcome.BODY],
            outcomes[BodyOutcome.MISSING],
            outcomes[BodyOutcome.UNKNOWN],
            outcomes[BodyOutcome.BODY_UNKNOWN],
            outcomes[BodyOutcome.AMBIGUOUS],
            outcomes[BodyOutcome.UNSUPPORTED],
            pending,
            downloaded_metadata,
            downloaded_body,
            unknown,
            lower,
            None if unknown else lower,
            self._shared_metadata,
            self._peak_shared_metadata,
            self._shared_metadata,
            accrued,
        )


__all__ = [
    "BodyOutcome", "BodyResponse", "DirectoryAmbiguityError", "DirectoryResponse",
    "FeedPollResult", "FeedRecord", "Observer", "ObserverAuditRecord", "ObserverConfig",
    "ObserverCosts", "ObserverError", "ObserverTimeError", "PendingBodyRequest",
    "PollScheduleError",
]
