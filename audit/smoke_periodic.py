"""Deterministic E09 pinned-export smoke run; reports operational counts only."""

from __future__ import annotations

import gc
import json
import sys
from datetime import timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ebe import HORIZON_START, load_export  # noqa: E402
from ebe.collectors import PeriodicConfig, PeriodicPolicy, run_periodic  # noqa: E402
from ebe.observer import Observer  # noqa: E402


def main() -> int:
    export = load_export(ROOT / "data" / "raw" / "export")
    checkpoint = HORIZON_START + timedelta(hours=24)
    rows: list[dict[str, object]] = []
    for policy in PeriodicPolicy:
        result = run_periodic(
            Observer(export),
            PeriodicConfig(
                policy,
                interval_us=60 * 60_000_000,
                phase_us=0,
                capacity_bytes=32 * 1024 * 1024,
                checkpoint=checkpoint,
            ),
        )
        rows.append({
            "policy": policy.value,
            "feed_requests": result.observer_costs.feed_requests,
            "sweeps": len(result.sweep_times),
            "body_requests": result.observer_costs.body_requests,
            "outcomes": dict(result.outcome_counts),
            "capture_attempts": result.captures_attempted,
            "captures_admitted": result.captures_admitted,
            "retained_captures": len(result.retained_captures),
            "retained_body_objects": result.storage_snapshot.retained_body_objects,
            "final_store_bytes": result.storage_snapshot.final_store_bytes,
            "evicted_bytes": result.storage_snapshot.bytes_evicted,
            "oversize_rejections": result.storage_snapshot.rejected_oversize_packets,
            "shared_metadata_bytes": result.observer_costs.final_shared_metadata_bytes,
        })
        del result
        gc.collect()
    print(json.dumps({
        "interval_minutes": 60,
        "phase_us": 0,
        "capacity_bytes": 32 * 1024 * 1024,
        "checkpoint": checkpoint.isoformat(),
        "policies": rows,
    }, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
