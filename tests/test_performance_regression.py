from __future__ import annotations

from datetime import timedelta
from pathlib import Path

from ebe.accounting import synchronized_accounting
from ebe.collectors import PeriodicConfig, PeriodicPolicy, run_periodic
from ebe.ingest import load_export
from ebe.observer import Observer, ObserverConfig
from ebe.storage import Capture, CaptureStore
from ebe.timeline import HORIZON_START


ROOT = Path(__file__).resolve().parents[1]


def test_nominal_interval_and_observer_outcome_are_cached() -> None:
    export = load_export(ROOT / "data" / "raw" / "export")
    observer = Observer(export)
    page = next(item.record.page_key for item in observer._feed)
    timeline = observer._trace.timeline(page)
    when = timeline._mutations[0].timing.selected_time
    observer._discovered.add(page)
    observer._observe_state(page, when)
    cache_sizes = (len(timeline._nominal_cache), len(observer._nominal_outcome_cache))
    for seconds in (1, 2, 3):
        observer._observe_state(page, when + timedelta(seconds=seconds))
    assert (len(timeline._nominal_cache), len(observer._nominal_outcome_cache)) == cache_sizes


def test_compact_periodic_retains_no_per_request_diagnostics() -> None:
    export = load_export(ROOT / "data" / "raw" / "export")
    observer = Observer(export, config=ObserverConfig(), retain_diagnostics=False)
    checkpoint = HORIZON_START + timedelta(days=1)
    result = run_periodic(observer, PeriodicConfig(
        PeriodicPolicy.P, 900_000_000, 0, 1_048_576, checkpoint
    ), compact=True)
    assert result.observer_costs.body_requests > 0
    assert result.body_results == ()
    assert result.capture_attempts == ()
    assert observer.audit_records == ()
    assert result.captures_attempted == result.observer_costs.successful_body_responses


def test_compact_accounting_keeps_instantaneous_peak_and_final_state() -> None:
    when = HORIZON_START
    legacy = CaptureStore(330, deduplicate=True, start_time=when)
    compact = CaptureStore(330, deduplicate=True, start_time=when, retain_history=False)
    captures = [Capture("dse~A", when, 1, b"same"),
                Capture("dse~A", when, 2, b"same"),
                Capture("dse~B", when, 3, b"different")]
    assert [legacy.admit(c) for c in captures] == [compact.admit(c) for c in captures]
    assert legacy.snapshot(when) == compact.snapshot(when)
    left = synchronized_accounting([(t, s, 23) for t, s in legacy.accounting_points], when)
    right = synchronized_accounting([(t, s, 23) for t, s in compact.accounting_points], when)
    assert left == right
    assert len(compact.accounting_points) <= 2
