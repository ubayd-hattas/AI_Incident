"""Frozen E09/E10 collectors over the neutral E08 observer boundary.

This module intentionally knows nothing about trace records, revisions, relations,
annotations, evidence units, or semantic importance.  Its only view of the modeled
world is the public :class:`ebe.observer.Observer` API.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Iterator, Literal

from .accounting import MICROSECONDS_PER_HOUR, elapsed_microseconds, require_utc
from .accounting import canonical_jsonl
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
    RetainedStoreExport,
    StorageSnapshot,
)
from .timeline import HORIZON_END, HORIZON_START


EVENT_DISPATCH_INTERVAL_US = 60_000_000


class CollectorError(RuntimeError):
    """Base class for invalid collector configurations."""


class PeriodicPolicy(str, Enum):
    P = "P"
    PD = "PD"
    PCD = "PCD"
    PCD_R = "PCD-R"


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
    service_order: Literal["forward", "reverse"] = "forward"

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
        if self.service_order not in ("forward", "reverse"):
            raise ValueError("service_order must be forward or reverse")


@dataclass(frozen=True, slots=True)
class EventDerivedConfig:
    """Frozen bounded event-derived configuration; ``q`` is attempts per hour."""

    q: int
    capacity_bytes: int | None = None
    checkpoint: datetime = HORIZON_END
    reverse_title_ties: bool = False

    def __post_init__(self) -> None:
        if type(self.q) is not int or self.q <= 0:
            raise ValueError("q must be a positive integer number of attempts per hour")
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
class RetainedEvidenceUnit:
    """A body genuinely retained by ``CaptureStore`` at the final checkpoint snapshot.

    This is the ONLY body-bearing surface a future evidence-coverage evaluator (E12)
    may treat as retained state. ``CollectorResult.body_results`` and
    ``.capture_attempts`` are diagnostic/audit history only -- they include every
    dispatched response and every attempted capture, oversize/evicted/rejected ones
    included, and must never be used as a stand-in for what the store actually kept.
    Built exclusively from ``CaptureStore.retained_captures`` plus
    ``CaptureStore.body_for_capture`` (which itself refuses to return a body for
    anything not currently retained), so it cannot structurally leak a body the cap
    ultimately rejected.
    """

    page_key: str
    capture_time: datetime
    request_seq: int
    body_sha256: str
    body: bytes


@dataclass(frozen=True, slots=True)
class EventDerivedStats:
    dispatch_times: tuple[datetime, ...]
    max_queue_depth: int
    coalesced_updates: int
    token_starved_dispatch_opportunities: int
    pending_dirty_pages: tuple[tuple[datetime, str], ...]
    final_token_credit_numerator: int
    token_denominator: int = MICROSECONDS_PER_HOUR


@dataclass(frozen=True, slots=True)
class CollectorResult:
    config: PeriodicConfig | EventDerivedConfig
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
    event_stats: EventDerivedStats | None = None
    retained_evidence: tuple[RetainedEvidenceUnit, ...] = ()
    retained_export: RetainedStoreExport | None = None
    repair_metadata_peak_bytes: int | None = None
    body_request_count: int | None = None
    capture_attempt_count: int | None = None
    capture_admitted_count: int | None = None

    @property
    def requests_made(self) -> int:
        costs = self.observer_costs
        return costs.feed_requests + costs.directory_requests + costs.body_requests

    @property
    def captures_attempted(self) -> int:
        return (len(self.capture_attempts) if self.capture_attempt_count is None
                else self.capture_attempt_count)

    @property
    def captures_admitted(self) -> int:
        return (sum(item.admission.disposition == "admitted" for item in self.capture_attempts)
                if self.capture_admitted_count is None else self.capture_admitted_count)

    @property
    def outcome_counts(self) -> tuple[tuple[str, int], ...]:
        # A response dispatched before the checkpoint can still resolve strictly
        # after it; from the checkpoint's own vantage point it is not yet a known
        # outcome. Bucket those as "pending" here too, matching the same fix in
        # Observer.costs(checkpoint) -- this property must not disagree with it.
        counts = {outcome.value: 0 for outcome in BodyOutcome}
        counts["pending"] = 0
        for result in self.body_results:
            if isinstance(result, PendingBodyRequest) or result.response_time > self.config.checkpoint:
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

    def __init__(self, observer: Observer, config: PeriodicConfig, *, compact: bool = False) -> None:
        if not isinstance(observer, Observer):
            raise TypeError("observer must be an E08 Observer")
        self.observer = observer
        self.config = config
        self.compact = compact

    def run(self) -> CollectorResult:
        config = self.config
        if config.policy is PeriodicPolicy.PCD_R:
            return self._run_repair()
        deduplicate = config.policy is not PeriodicPolicy.P
        store = CaptureStore(
            config.capacity_bytes,
            deduplicate=deduplicate,
            start_time=HORIZON_START,
            retain_history=not self.compact,
        )
        beliefs: dict[str, _Belief] = {}
        dirty: set[str] = set()
        polls: list[FeedPollResult] = []
        sweeps: list[datetime] = []
        body_results: list[BodyResponse | PendingBodyRequest] = []
        peak_discovered = 0
        peak_dirty = 0
        capture_attempt_count = 0
        capture_admitted_count = 0

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
                if not self.compact or poll.records:
                    polls.append(poll)
                self._apply_feed_batch(poll, beliefs, dirty)
                peak_discovered = max(peak_discovered, len(beliefs))
                peak_dirty = max(peak_dirty, len(dirty))
                next_poll += poll_step
                continue

            assert next_sweep is not None
            if not self.compact:
                sweeps.append(next_sweep)
            if config.policy in {PeriodicPolicy.PCD, PeriodicPolicy.PCD_R}:
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
            if config.service_order == "reverse":
                eligible.reverse()
            for page_key in eligible:
                response = self.observer.get_body(page_key, next_sweep)
                if self.compact and isinstance(response, BodyResponse):
                    if response.outcome is BodyOutcome.BODY:
                        assert response.body is not None
                        capture = Capture(response.page_key, response.response_time,
                                          response.request_seq, response.body)
                        admission = store.admit(capture)
                        capture_attempt_count += 1
                        capture_admitted_count += admission.disposition == "admitted"
                else:
                    body_results.append(response)
            if config.policy in {PeriodicPolicy.PCD, PeriodicPolicy.PCD_R}:
                # A sweep is the frozen service point. Every eligible dirty title was
                # attempted; confirmed deletes were already removed on feed delivery.
                dirty.difference_update(eligible)
            next_sweep = next(sweep_iter, None)

        revealed = {item.request_seq: item for item in self.observer.complete_due(config.checkpoint)}
        body_results = [revealed.get(item.request_seq, item) if isinstance(item, PendingBodyRequest)
                        else item for item in body_results]
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
            admission = store.admit(capture)
            if self.compact:
                capture_attempt_count += 1
                capture_admitted_count += admission.disposition == "admitted"
            else:
                attempts.append(CaptureAttempt(capture, admission))
        if not self.compact:
            capture_attempt_count = len(attempts)
            capture_admitted_count = sum(
                item.admission.disposition == "admitted" for item in attempts
            )

        snapshot = store.snapshot(config.checkpoint)
        retained_evidence = tuple(
            RetainedEvidenceUnit(
                rc.page_key, rc.capture_time, rc.request_seq, rc.body_sha256,
                store.body_for_capture(rc.request_seq),
            )
            for rc in store.retained_captures
        )
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
            retained_evidence=retained_evidence,
            retained_export=store.export_retained(config.checkpoint),
            body_request_count=self.observer.costs(config.checkpoint).body_requests,
            capture_attempt_count=capture_attempt_count,
            capture_admitted_count=capture_admitted_count,
        )

    def _run_repair(self) -> CollectorResult:
        """Frozen online PCD-R control, including synthetic delayed completions."""
        config = self.config
        store = CaptureStore(config.capacity_bytes, deduplicate=True, start_time=HORIZON_START,
                             retain_history=not self.compact)
        beliefs: dict[str, _Belief] = {}; dirty: set[str] = set()
        # Content-free repair metadata: last completed known hash and byte length.
        last_known: dict[str, tuple[str, int]] = {}
        pending_by_seq: dict[int, PendingBodyRequest] = {}
        pending_by_title: dict[str, int] = {}
        result_indexes: dict[int, int] = {}
        polls=[]; sweeps=[]; results=[]; attempts=[]
        peak_discovered=peak_dirty=metadata_peak=0
        # dispatch_count always equals what len(results) would be, in both
        # modes; kept explicit so compact mode need not grow that list just
        # to compute the prospective request_seq used for the cap pre-check.
        dispatch_count=0
        capture_attempt_count=0
        capture_admitted_count=0
        # Incremental mirror of "is (page_key, body_sha256) currently one of
        # store.retained_captures", kept exactly in step with every admission
        # and eviction below. Replaces an O(known pages x retained packets)
        # linear rescan of store.retained_captures on every sweep, which is
        # what actually made PCD-R infeasible (not per-request diagnostic
        # history, which the compact path above already addresses).
        retained_hash_count: dict[tuple[str, str], int] = {}
        retained_page_hash_by_seq: dict[int, tuple[str, str]] = {}

        def _note_evictions(evicted_request_seqs: tuple[int, ...]) -> None:
            for seq in evicted_request_seqs:
                key = retained_page_hash_by_seq.pop(seq, None)
                if key is None:
                    continue
                remaining = retained_hash_count[key] - 1
                if remaining:
                    retained_hash_count[key] = remaining
                else:
                    del retained_hash_count[key]

        sweep_iter=iter(periodic_sweep_times(config.interval_us, config.phase_us,
                                             checkpoint=config.checkpoint))
        next_sweep=next(sweep_iter,None); next_poll=HORIZON_START
        poll_step=timedelta(microseconds=self.observer.config.feed_poll_interval_us)

        def apply_completion(response: BodyResponse) -> None:
            nonlocal metadata_peak, capture_attempt_count, capture_admitted_count
            pending = pending_by_seq.pop(response.request_seq, None)
            if pending is not None:
                remaining = pending_by_title[pending.page_key] - 1
                if remaining:
                    pending_by_title[pending.page_key] = remaining
                else:
                    del pending_by_title[pending.page_key]
                if not self.compact:
                    results[result_indexes[response.request_seq]] = response
            if response.outcome is BodyOutcome.BODY:
                assert response.body is not None
                capture=Capture(response.page_key,response.response_time,
                                response.request_seq,response.body)
                admission=store.admit(capture)
                _note_evictions(admission.evicted_request_seqs)
                if admission.disposition == "admitted":
                    key = (capture.page_key, capture.body_sha256)
                    retained_hash_count[key] = retained_hash_count.get(key, 0) + 1
                    retained_page_hash_by_seq[capture.request_seq] = key
                if self.compact:
                    capture_attempt_count += 1
                    capture_admitted_count += admission.disposition == "admitted"
                else:
                    attempts.append(CaptureAttempt(capture,admission))
                last_known[response.page_key]=(capture.body_sha256,len(capture.body))
            else:
                # Every unavailable completed outcome disables repair until a
                # later known-body completion for this title.
                last_known.pop(response.page_key,None)
            metadata_peak=max(metadata_peak,len(canonical_jsonl({
                page:[digest,length] for page,(digest,length) in sorted(last_known.items())})))

        while next_poll<=config.checkpoint or next_sweep is not None or pending_by_seq:
            next_completion=min((item.response_time for item in pending_by_seq.values()),
                                default=None)
            candidates=[value for value in (next_poll if next_poll<=config.checkpoint else None,
                                              next_completion, next_sweep)
                        if value is not None]
            if not candidates:
                break
            now=min(candidates)
            if now>config.checkpoint:
                break

            # At a common instant the frozen order is feed update, due
            # completion, then the new periodic reads.
            if next_poll<=config.checkpoint and next_poll==now:
                poll=self.observer.poll_feed(next_poll)
                if not self.compact or poll.records:
                    polls.append(poll)
                self._apply_feed_batch(poll,beliefs,dirty)
                peak_discovered=max(peak_discovered,len(beliefs)); peak_dirty=max(peak_dirty,len(dirty))
                next_poll+=poll_step
            if next_completion==now:
                for response in self.observer.complete_due(now):
                    apply_completion(response)
            if next_sweep!=now:
                continue

            assert next_sweep is not None
            if not self.compact:
                sweeps.append(next_sweep)
            ordinary={p for p in dirty if beliefs[p] in {_Belief.LIVE,_Belief.MIXED}}
            repairs=set()
            prospective=dispatch_count+1
            for page_key,(body_hash,body_len) in last_known.items():
                if beliefs.get(page_key) not in {_Belief.LIVE,_Belief.MIXED}: continue
                if pending_by_title.get(page_key,0): continue
                if retained_hash_count.get((page_key, body_hash), 0) > 0: continue
                dummy=Capture(page_key,next_sweep,prospective,b"x"*body_len)
                if config.capacity_bytes is None or len(dummy.packet_bytes)+body_len<=config.capacity_bytes:
                    repairs.add(page_key)
            eligible=sorted(ordinary|repairs, reverse=config.service_order=="reverse")
            for page_key in eligible:
                is_ordinary=page_key in ordinary
                if not is_ordinary:
                    body_len=last_known[page_key][1]
                    dummy=Capture(page_key,next_sweep,dispatch_count+1,b"x"*body_len)
                    if config.capacity_bytes is not None and len(dummy.packet_bytes)+body_len>config.capacity_bytes:
                        continue
                response=self.observer.get_body(page_key,next_sweep)
                dispatch_count+=1
                if not self.compact:
                    results.append(response)
                    result_indexes[response.request_seq]=len(results)-1
                if isinstance(response,PendingBodyRequest):
                    pending_by_seq[response.request_seq]=response
                    pending_by_title[page_key]=pending_by_title.get(page_key,0)+1
                else:
                    apply_completion(response)
            dirty.difference_update(ordinary)
            metadata_peak=max(metadata_peak,len(canonical_jsonl({
                page:[digest,length] for page,(digest,length) in sorted(last_known.items())})))
            next_sweep=next(sweep_iter,None)
        if not self.compact:
            capture_attempt_count=len(attempts)
            capture_admitted_count=sum(item.admission.disposition == "admitted" for item in attempts)
        snapshot=store.snapshot(config.checkpoint)
        retained_evidence=tuple(RetainedEvidenceUnit(
            rc.page_key,rc.capture_time,rc.request_seq,rc.body_sha256,
            store.body_for_capture(rc.request_seq)) for rc in store.retained_captures)
        return CollectorResult(config,tuple(polls),tuple(sweeps),tuple(results),tuple(attempts),
            store.retained_captures,snapshot,self.observer.costs(config.checkpoint),
            self.observer.discovered_titles,peak_discovered,peak_dirty,
            retained_evidence=retained_evidence,
            retained_export=store.export_retained(config.checkpoint),
            repair_metadata_peak_bytes=metadata_peak,
            body_request_count=self.observer.costs(config.checkpoint).body_requests,
            capture_attempt_count=capture_attempt_count,
            capture_admitted_count=capture_admitted_count)

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


def run_periodic(observer: Observer, config: PeriodicConfig, *, compact: bool = False) -> CollectorResult:
    """Convenience entry point for one deterministic E09 periodic run."""

    return PeriodicCollector(observer, config, compact=compact).run()


class EventDerivedCollector:
    """Run bounded E(q) using only the content-free E08 observer interface."""

    def __init__(self, observer: Observer, config: EventDerivedConfig) -> None:
        if not isinstance(observer, Observer):
            raise TypeError("observer must be an E08 Observer")
        if not isinstance(config, EventDerivedConfig):
            raise TypeError("config must be an EventDerivedConfig")
        self.observer = observer
        self.config = config

    def run(self) -> CollectorResult:
        config = self.config
        store = CaptureStore(
            config.capacity_bytes,
            deduplicate=True,
            start_time=HORIZON_START,
        )
        dirty: dict[str, datetime] = {}
        polls: list[FeedPollResult] = []
        body_results: list[BodyResponse | PendingBodyRequest] = []
        dispatch_times: list[datetime] = []
        peak_discovered = 0
        peak_dirty = 0
        coalesced = 0
        starved = 0

        # Credit is represented as numerator / MICROSECONDS_PER_HOUR tokens.
        # This makes continuous q/hour refill and consumption exact integers.
        capacity_credit = config.q * MICROSECONDS_PER_HOUR
        token_credit = capacity_credit
        last_refill = HORIZON_START
        poll_step = timedelta(microseconds=self.observer.config.feed_poll_interval_us)
        dispatch_step = timedelta(microseconds=EVENT_DISPATCH_INTERVAL_US)
        next_poll = HORIZON_START
        next_dispatch = HORIZON_START

        while next_poll <= config.checkpoint or next_dispatch < config.checkpoint:
            if next_poll <= config.checkpoint and (
                next_dispatch >= config.checkpoint or next_poll <= next_dispatch
            ):
                poll = self.observer.poll_feed(next_poll)
                polls.append(poll)
                batch_coalesced = self._apply_feed_batch(poll, dirty)
                coalesced += batch_coalesced
                peak_discovered = max(peak_discovered, len(self.observer.discovered_titles))
                peak_dirty = max(peak_dirty, len(dirty))
                next_poll += poll_step
                continue

            dispatch_time = next_dispatch
            dispatch_times.append(dispatch_time)
            elapsed = elapsed_microseconds(last_refill, dispatch_time)
            token_credit = min(capacity_credit, token_credit + config.q * elapsed)
            last_refill = dispatch_time

            while dirty and token_credit >= MICROSECONDS_PER_HOUR:
                oldest = min(value for value in dirty.values())
                tied = [key for key, value in dirty.items() if value == oldest]
                page_key = (max(tied) if config.reverse_title_ties else min(tied))
                del dirty[page_key]
                body_results.append(self.observer.get_body(page_key, dispatch_time))
                token_credit -= MICROSECONDS_PER_HOUR
            if dirty and token_credit < MICROSECONDS_PER_HOUR:
                starved += 1
            next_dispatch += dispatch_step

        revealed = {item.request_seq: item for item in self.observer.complete_due(config.checkpoint)}
        body_results = [revealed.get(item.request_seq, item) if isinstance(item, PendingBodyRequest)
                        else item for item in body_results]
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
        # Refill through the checkpoint for an auditable terminal bucket state,
        # without creating a forbidden dispatch opportunity at the checkpoint.
        token_credit = min(
            capacity_credit,
            token_credit + config.q * elapsed_microseconds(last_refill, config.checkpoint),
        )
        pending = tuple(sorted(
            ((pending_time, page_key) for page_key, pending_time in dirty.items()),
            key=lambda item: (item[0], item[1]),
        ))
        stats = EventDerivedStats(
            tuple(dispatch_times), peak_dirty, coalesced, starved, pending, token_credit
        )
        retained_evidence = tuple(
            RetainedEvidenceUnit(
                rc.page_key, rc.capture_time, rc.request_seq, rc.body_sha256,
                store.body_for_capture(rc.request_seq),
            )
            for rc in store.retained_captures
        )
        return CollectorResult(
            config,
            tuple(polls),
            (),
            tuple(body_results),
            tuple(attempts),
            store.retained_captures,
            snapshot,
            self.observer.costs(config.checkpoint),
            self.observer.discovered_titles,
            peak_discovered,
            peak_dirty,
            stats,
            retained_evidence=retained_evidence,
            retained_export=store.export_retained(config.checkpoint),
        )

    @staticmethod
    def _apply_feed_batch(
        poll: FeedPollResult,
        dirty: dict[str, datetime],
    ) -> int:
        """Apply same-time groups without treating feed serialization as chronology."""

        coalesced = 0
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
            live_updates = sum(item.action == "live_change" for item in group)
            if actions == {"delete"}:
                dirty.pop(page_key, None)
            else:
                if page_key in dirty:
                    coalesced += live_updates
                else:
                    dirty[page_key] = record.event_time
                    coalesced += max(0, live_updates - 1)
            index = end
        return coalesced


def run_event_derived(observer: Observer, config: EventDerivedConfig) -> CollectorResult:
    """Convenience entry point for one deterministic bounded E(q) run."""

    return EventDerivedCollector(observer, config).run()


__all__ = [
    "CaptureAttempt",
    "CollectorError",
    "CollectorResult",
    "EventDerivedCollector",
    "EventDerivedConfig",
    "EventDerivedStats",
    "EVENT_DISPATCH_INTERVAL_US",
    "PeriodicCollector",
    "PeriodicConfig",
    "PeriodicPolicy",
    "RetainedEvidenceUnit",
    "periodic_sweep_times",
    "run_periodic",
    "run_event_derived",
]
