#!/usr/bin/env python3
"""Collection-only P15 profiler; deliberately imports no evaluator/annotations."""
from __future__ import annotations

import argparse
import json
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ebe.collectors import PeriodicConfig, PeriodicPolicy, run_periodic
from ebe.ingest import load_export
from ebe.observer import Observer, ObserverConfig
from ebe.timeline import HORIZON_END, HORIZON_START


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int)
    parser.add_argument("--legacy-retention", action="store_true")
    args = parser.parse_args()
    checkpoint = HORIZON_END if args.days is None else HORIZON_START + __import__(
        "datetime"
    ).timedelta(days=args.days)
    export = load_export(ROOT / "data" / "raw" / "export")
    observer = Observer(export, config=ObserverConfig(5_000_000, 60_000_000, 0),
                        retain_diagnostics=args.legacy_retention)
    cfg = PeriodicConfig(PeriodicPolicy.P, 900_000_000, 0, 1_048_576, checkpoint)
    try:
        import psutil
        process = psutil.Process()
        peak = [process.memory_info().rss]
        stop = threading.Event()

        def sample() -> None:
            while not stop.wait(0.1):
                peak[0] = max(peak[0], process.memory_info().rss)

        thread = threading.Thread(target=sample, daemon=True)
        thread.start()
    except ImportError:
        process = None; peak = [None]; stop = None; thread = None
    wall = time.perf_counter(); cpu = time.process_time()
    result = run_periodic(observer, cfg, compact=not args.legacy_retention)
    wall = time.perf_counter() - wall; cpu = time.process_time() - cpu
    if stop is not None:
        stop.set(); thread.join()
    output = {
        "scope": "P15 collection only; evaluator and annotations not imported",
        "checkpoint": checkpoint.isoformat(), "feed_polls": result.observer_costs.feed_requests,
        "sweeps": int((checkpoint - HORIZON_START).total_seconds() // 900),
        "body_gets": result.observer_costs.body_requests,
        "total_attempts": result.requests_made, "elapsed_seconds": wall,
        "cpu_seconds": cpu, "rss_peak_bytes": peak[0],
        "rss_end_bytes": None if process is None else process.memory_info().rss,
        "observer_audit_objects": len(observer.audit_records),
        "body_result_objects": len(result.body_results),
        "capture_attempt_objects": len(result.capture_attempts),
        "storage_accounting_points": len(result.retained_export.accounting_points),
        "storage_size_history_points": "not exposed in retained export",
        "retained_packets": result.storage_snapshot.retained_packets,
        "retained_objects": result.storage_snapshot.retained_body_objects,
    }
    print(json.dumps(output, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
