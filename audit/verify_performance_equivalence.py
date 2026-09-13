#!/usr/bin/env python3
"""Outcome-blind exact checks for the X13 performance-only execution path."""
from __future__ import annotations

import json
import sys
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ebe import collectors as collectors_module
from ebe.accounting import synchronized_accounting
from ebe.collectors import (EventDerivedConfig, PeriodicConfig, PeriodicPolicy,
                            run_event_derived, run_periodic)
from ebe.ingest import load_export
from ebe.observer import BodyOutcome, Observer, ObserverConfig
from ebe.storage import Capture, CaptureStore
from ebe.timeline import HORIZON_START, PageTimeline, _Branch, _apply


class RecordingObserver(Observer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.get_schedule: list[tuple[datetime, int, str]] = []
        self.poll_schedule: list[datetime] = []

    def poll_feed(self, poll_time):
        self.poll_schedule.append(poll_time)
        return super().poll_feed(poll_time)

    def get_body(self, page_key, request_time):
        result = super().get_body(page_key, request_time)
        self.get_schedule.append((request_time, result.request_seq, page_key))
        return result


def legacy_nominal(self: PageTimeline, timestamp: datetime):
    """The pre-repair replay implementation, retained only inside this verifier."""
    eligible = [item for item in self._mutations if item.timing.selected_time <= timestamp]
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
        output = []
        for branch in branches:
            for order in orders:
                updated = branch
                for mutation in order:
                    updated = _apply(updated, mutation)
                from dataclasses import replace
                output.append(replace(
                    updated,
                    ordering_choices=updated.ordering_choices +
                    (tuple(item.event_id for item in order),),
                    pending=(),
                ))
                self._check_limit(len(output))
        branches = output
        index = end
    return branches, reasons


class LegacyObserver(RecordingObserver):
    """Observer read path before immutable interval/content caches."""
    def _canonical_body(self, ref):
        codec = {"ascii": "ascii", "utf8": "utf-8", "utf-8": "utf-8",
                 "latin1": "latin-1", "latin-1": "latin-1"}.get(ref.source_encoding)
        if codec is None:
            return super()._canonical_body(ref)
        return ref.source_bytes.decode(codec, errors="strict").encode("utf-8")

    def _observe_state(self, page_key, response_time):
        query = self._trace.state_at(page_key, response_time, mode="nominal")
        possibilities = set()
        for alternative in query.alternatives:
            state = alternative.state
            if state.kind.value == "live_body_ref":
                possibilities.add((BodyOutcome.BODY, self._canonical_body(state.body_ref)))
            elif state.kind.value == "deleted":
                possibilities.add((BodyOutcome.MISSING, None))
            elif state.kind.value == "live_body_unknown":
                possibilities.add((BodyOutcome.BODY_UNKNOWN, None))
            else:
                possibilities.add((BodyOutcome.UNKNOWN, None))
        return ((BodyOutcome.AMBIGUOUS, None) if len(possibilities) != 1
                else next(iter(possibilities)))


@contextmanager
def pre_repair_timeline():
    current = PageTimeline._nominal
    PageTimeline._nominal = legacy_nominal
    try:
        yield
    finally:
        PageTimeline._nominal = current


def combined(result):
    s_points = result.retained_export.accounting_points
    m_points = result.observer_costs.accounting_points
    times = sorted({t for t, _ in s_points} | {t for t, _ in m_points})
    s = m = 0
    si = mi = 0
    points = []
    for when in times:
        while si < len(s_points) and s_points[si][0] == when:
            s = s_points[si][1]; si += 1
        while mi < len(m_points) and m_points[mi][0] == when:
            m = m_points[mi][1]; mi += 1
        points.append((when, s, m))
    return synchronized_accounting(points, result.config.checkpoint)


def projection(result, observer):
    export = result.retained_export
    return {
        "poll_schedule": tuple(observer.poll_schedule),
        "get_schedule": tuple(observer.get_schedule),
        "request_count": result.requests_made,
        "outcomes": result.observer_costs,
        "packets": export.packets,
        "objects": export.body_objects,
        "snapshot": result.storage_snapshot,
        "evicted_bytes": (result.storage_snapshot.evicted_packet_bytes,
                           result.storage_snapshot.evicted_body_bytes),
        "oversize": result.storage_snapshot.rejected_oversize_packets,
        "feed_m": (result.observer_costs.feed_metadata_bytes,
                   result.observer_costs.final_shared_metadata_bytes),
        "combined": combined(result),
    }


def run_policy(export, name: str, checkpoint: datetime, *, legacy: bool, compact: bool,
               delay_us: int = 0):
    observer_type = LegacyObserver if legacy else RecordingObserver
    observer = observer_type(export, config=ObserverConfig(get_response_delay_us=delay_us),
                             retain_diagnostics=not compact)
    if name == "E":
        result = run_event_derived(observer, EventDerivedConfig(30, 1_048_576, checkpoint))
    else:
        cfg = PeriodicConfig(PeriodicPolicy(name), 900_000_000, 0, 1_048_576, checkpoint)
        result = run_periodic(observer, cfg, compact=compact)
    return result, observer


def verify_storage_fixtures() -> int:
    failures = 0
    fixture_dir = ROOT / "tests" / "fixtures" / "accounting"
    for name in ("C_duplicate.json", "D_nondedup.json", "E_fifo.json",
                 "F_oversize.json", "G_shared_fifo.json"):
        fixture = json.loads((fixture_dir / name).read_text(encoding="utf-8"))
        body_hexes = fixture.get("body_utf8_hex_in_request_order") or [
            fixture["body_utf8_hex"]
        ] * len(fixture["canonical_packets"])
        captures = []
        for packet_text, body_hex in zip(fixture["canonical_packets"], body_hexes):
            packet = json.loads(packet_text)
            captures.append(Capture(
                packet["page_key"],
                datetime.fromisoformat(packet["capture_time"].replace("Z", "+00:00")),
                packet["request_seq"], bytes.fromhex(body_hex),
            ))
        start = captures[0].capture_time
        legacy = CaptureStore(fixture["capacity_bytes"], deduplicate=fixture["deduplicate"],
                              start_time=start)
        compact = CaptureStore(fixture["capacity_bytes"], deduplicate=fixture["deduplicate"],
                               start_time=start, retain_history=False)
        left = [legacy.admit(c) for c in captures]
        right = [compact.admit(c) for c in captures]
        checkpoint = datetime.fromisoformat(fixture["checkpoint"].replace("Z", "+00:00"))
        ok = (left == right and legacy.snapshot(checkpoint) == compact.snapshot(checkpoint)
              and legacy.retained_captures == compact.retained_captures
              and synchronized_accounting([(t, s, 17) for t, s in legacy.accounting_points], checkpoint)
              == synchronized_accounting([(t, s, 17) for t, s in compact.accounting_points], checkpoint))
        print(f"{'PASS' if ok else 'FAIL'} synthetic storage {name}")
        failures += not ok
    # Explicit empty/non-ASCII bodies and request-sequence decimal-width boundary.
    when = HORIZON_START
    captures = [Capture("dse~é", when, 9, "é".encode()),
                Capture("dse~é", when, 10, b"")]
    a = CaptureStore(None, deduplicate=True, start_time=when)
    b = CaptureStore(None, deduplicate=True, start_time=when, retain_history=False)
    ok = [a.admit(c) for c in captures] == [b.admit(c) for c in captures]
    ok = ok and a.snapshot(when) == b.snapshot(when)
    print(f"{'PASS' if ok else 'FAIL'} synthetic non-ASCII/empty/seq-width")
    return failures + (not ok)


def main() -> int:
    export = load_export(ROOT / "data" / "raw" / "export")
    failures = verify_storage_fixtures()
    windows = {"P": 3, "PD": 3, "PCD": 5, "PCD-R": 5, "E": 5}
    for policy, days in windows.items():
        checkpoint = HORIZON_START + timedelta(days=days)
        with pre_repair_timeline():
            legacy, legacy_observer = run_policy(export, policy, checkpoint,
                                                 legacy=True, compact=False)
        compact = policy in {"P", "PD", "PCD"}
        optimized, optimized_observer = run_policy(export, policy, checkpoint,
                                                   legacy=False, compact=compact)
        ok = projection(legacy, legacy_observer) == projection(optimized, optimized_observer)
        print(f"{'PASS' if ok else 'FAIL'} real-prefix {policy} ({days}d) exact projection")
        failures += not ok
    checkpoint = HORIZON_START + timedelta(days=3)
    with pre_repair_timeline():
        legacy, legacy_observer = run_policy(export, "PCD", checkpoint, legacy=True,
                                             compact=False, delay_us=30_000_000)
    optimized, optimized_observer = run_policy(export, "PCD", checkpoint, legacy=False,
                                               compact=True, delay_us=30_000_000)
    ok = projection(legacy, legacy_observer) == projection(optimized, optimized_observer)
    print(f"{'PASS' if ok else 'FAIL'} real-prefix PCD delayed-response exact projection")
    failures += not ok
    print(f"PERFORMANCE_EQUIVALENCE {'PASS' if not failures else 'FAIL'} failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
