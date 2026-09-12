"""Frozen E09 periodic collectors over the neutral E08 observer boundary.

This module intentionally knows nothing about trace records, revisions, relations,
annotations, evidence units, or semantic importance.  Its only view of the modeled
world is the public :class:`ebe.observer.Observer` API.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Iterator

from .accounting import elapsed_microseconds, require_utc
from .observer import (
    BodyOutcome,
    BodyResponse,
    FeedPollResult,
    Observer,
    ObserverCosts,
    PendingBodyRequest,
)
from .storage import (
    AdmissionResult,
    Capture,
    CaptureStore,
    RetainedCapture,
    StorageSnapshot,
)
from .timeline import HORIZON_END, HORIZON_START


class CollectorError(RuntimeError):
    """Base class for invalid E09 collector configurations."""


class PeriodicPolicy(str, Enum):
    P = "P"
    PD = "PD"
    PCD = "PCD"


class _Belief(str, Enum):
    LIVE = "live"
    DELETED = "deleted"
    MIXED = "mixed"


@dataclass(frozen=True, slots=True)
class PeriodicConfig:
    policy: PeriodicPolicy
    interval_us: int
    phase_us: int = 0
    capacity_bytes: int | None = None
    checkpoint: datetime = HORIZON_END

    def __post_init__(self) -> None:
        if not isinstance(self.policy, PeriodicPolicy):
            raise TypeError("policy must be a PeriodicPolicy")
        if type(self.interval_us) is not int or self.interval_us <= 0:
            raise ValueError("interval_us must be a positive integer")
        if type(self.phase_us) is not int or not 0 <= self.phase_us < self.interval_us:
            raise ValueError("phase_us must be an integer in [0, interval_us)")
        if self.capacity_bytes is not None and (
            type(self.capacity_bytes) is not int or self.capacity_bytes < 0
        ):
            raise ValueError("capacity_bytes must be a nonnegative integer or None")
        checkpoint = require_utc(self.checkpoint, "checkpoint")
        if not HORIZON_START < checkpoint <= HORIZON_END:
            raise ValueError("checkpoint must be in (HORIZON_START, HORIZON_END]")


@dataclass(frozen=True, slots=True)
class CaptureAttempt:
    capture: Capture
    admission: AdmissionResult


@dataclass(frozen=True, slots=True)
class CollectorResult:
    config: PeriodicConfig
    feed_polls: tuple[FeedPollResult, ...]
    sweep_times: tuple[datetime, ...]
    body_results: tuple[BodyResponse | PendingBodyRequest, ...]
    capture_attempts: tuple[CaptureAttempt, ...]
    retained_captures: tuple[RetainedCapture, ...]
    storage_snapshot: StorageSnapshot
    observer_costs: ObserverCosts
    discovered_titles: tuple[str, ...]
    peak_discovered_titles: int
    peak_dirty_titles: int

    @property
    def requests_made(self) -> int:
        costs = self.observer_costs
        return costs.feed_requests + costs.directory_requests + costs.body_requests

    @property
    def captures_attempted(self) -> int:
        return len(self.capture_attempts)

    @property
    def captures_admitted(self) -> int:
        return sum(item.admission.disposition == "admitted" for item in self.capture_attempts)

    @property
    def outcome_counts(self) -> tuple[tuple[str, int], ...]:
        counts = {outcome.value: 0 for outcome in BodyOutcome}
        counts["pending"] = 0
        for result in self.body_results:
            if isinstance(result, PendingBodyRequest):
                counts["pending"] += 1
            else:
                counts[result.outcome.value] += 1
        return tuple(sorted(counts.items()))

    @property
    def body_request_schedule(self) -> tuple[tuple[datetime, int, str], ...]:
        return tuple(
            (item.request_time, item.request_seq, item.page_key)
            for item in self.body_results
        )


def periodic_sweep_times(
    interval_us: int,
    phase_us: int = 0,
    *,
    checkpoint: datetime = HORIZON_END,
) -> Iterator[datetime]:
    """Yield the global, t0-relative periodic schedule in ``[t0, checkpoint)``."""

    if type(interval_us) is not int or interval_us <= 0:
        raise ValueError("interval_us must be a positive integer")
    if type(phase_us) is not int or not 0 <= phase_us < interval_us:
        raise ValueError("phase_us must be an integer in [0, interval_us)")
    checkpoint = require_utc(checkpoint, "checkpoint")
    if not HORIZON_START < checkpoint <= HORIZON_END:
        raise ValueError("checkpoint must be in (HORIZON_START, HORIZON_END]")
    offset = phase_us
    horizon_us = elapsed_microseconds(HORIZON_START, checkpoint)
    while offset < horizon_us:
        yield HORIZON_START + timedelta(microseconds=offset)
        offset += interval_us


class PeriodicCollector:
    """Run P, PD, or PCD using only an already-constructed E08 observer."""

    def __init__(self, observer: Observer, config: PeriodicConfig) -> None:
        if not isinstance(observer, Observer):
            raise TypeError("observer must be an E08 Observer")
        self.observer = observer
        self.config = config

    def run(self) -> CollectorResult:
        config = self.config
        deduplicate = config.policy is not PeriodicPolicy.P
        store = CaptureStore(
            config.capacity_bytes,
            deduplicate=deduplicate,
            start_time=HORIZON_START,
        )
        beliefs: dict[str, _Belief] = {}
        dirty: set[str] = set()
        polls: list[FeedPollResult] = []
        sweeps: list[datetime] = []
        body_results: list[BodyResponse | PendingBodyRequest] = []
        peak_discovered = 0
        peak_dirty = 0

        sweep_iter = iter(periodic_sweep_times(
            config.interval_us, config.phase_us, checkpoint=config.checkpoint
        ))
        next_sweep = next(sweep_iter, None)
        next_poll = HORIZON_START
        poll_step = timedelta(microseconds=self.observer.config.feed_poll_interval_us)

        while next_poll <= config.checkpoint or next_sweep is not None:
            # Frozen common-instant order: feed delivery/knowledge update precedes reads.
            if next_poll <= config.checkpoint and (
                next_sweep is None or next_poll <= next_sweep
            ):
                poll = self.observer.poll_feed(next_poll)
                polls.append(poll)
                self._apply_feed_batch(poll, beliefs, dirty)
                peak_discovered = max(peak_discovered, len(beliefs))
                peak_dirty = max(peak_dirty, len(dirty))
                next_poll += poll_step
                continue

            assert next_sweep is not None
            sweeps.append(next_sweep)
            if config.policy is PeriodicPolicy.PCD:
                eligible = sorted(
                    page_key
                    for page_key in dirty
                    if beliefs[page_key] in {_Belief.LIVE, _Belief.MIXED}
                )
            else:
                eligible = sorted(
                    page_key
                    for page_key, belief in beliefs.items()
                    if belief in {_Belief.LIVE, _Belief.MIXED}
                )
            for page_key in eligible:
                body_results.append(self.observer.get_body(page_key, next_sweep))
            if config.policy is PeriodicPolicy.PCD:
                # A sweep is the frozen service point. Every eligible dirty title was
                # attempted; confirmed deletes were already removed on feed delivery.
                dirty.difference_update(eligible)
            next_sweep = next(sweep_iter, None)

        attempts: list[CaptureAttempt] = []
        completed = sorted(
            (
                result for result in body_results
                if isinstance(result, BodyResponse)
                and result.outcome is BodyOutcome.BODY
                and result.response_time <= config.checkpoint
            ),
            key=lambda item: (item.response_time, item.request_seq, item.page_key),
        )
        for response in completed:
            assert response.body is not None
            capture = Capture(
                response.page_key,
                response.response_time,
                response.request_seq,
                response.body,
            )
            attempts.append(CaptureAttempt(capture, store.admit(capture)))

        snapshot = store.snapshot(config.checkpoint)
        return CollectorResult(
            config,
            tuple(polls),
            tuple(sweeps),
            tuple(body_results),
            tuple(attempts),
            store.retained_captures,
            snapshot,
            self.observer.costs(config.checkpoint),
            self.observer.discovered_titles,
            peak_discovered,
            peak_dirty,
        )

    @staticmethod
    def _apply_feed_batch(
        poll: FeedPollResult,
        beliefs: dict[str, _Belief],
        dirty: set[str],
    ) -> None:
        index = 0
        records = poll.records
        while index < len(records):
            record = records[index]
            end = index + 1
            while (
                end < len(records)
                and records[end].event_time == record.event_time
                and records[end].page_key == record.page_key
            ):
                end += 1
            group = records[index:end]
            actions = {item.action for item in group}
            page_key = record.page_key
            if actions == {"delete"}:
                beliefs[page_key] = _Belief.DELETED
                dirty.discard(page_key)
            elif actions == {"live_change"}:
                beliefs[page_key] = _Belief.LIVE
                dirty.add(page_key)
            else:
                # Same-time feed order conveys no chronology. Mixed knowledge is
                # request-eligible and cannot be collapsed to confirmed deletion.
                beliefs[page_key] = _Belief.MIXED
                dirty.add(page_key)
            index = end


def run_periodic(observer: Observer, config: PeriodicConfig) -> CollectorResult:
    """Convenience entry point for one deterministic E09 periodic run."""

    return PeriodicCollector(observer, config).run()


__all__ = [
    "CaptureAttempt",
    "CollectorError",
    "CollectorResult",
    "PeriodicCollector",
    "PeriodicConfig",
    "PeriodicPolicy",
    "periodic_sweep_times",
    "run_periodic",
]
