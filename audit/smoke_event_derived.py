"""Deterministic E10 pinned-export smoke run; operational quantities only."""

from __future__ import annotations

import json
import sys
from datetime import timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ebe import HORIZON_START, load_export  # noqa: E402
from ebe.collectors import EventDerivedConfig, run_event_derived  # noqa: E402
from ebe.observer import Observer  # noqa: E402


def main() -> int:
    export = load_export(ROOT / "data" / "raw" / "export")
    checkpoint = HORIZON_START + timedelta(hours=24)
    result = run_event_derived(
        Observer(export),
        EventDerivedConfig(
            q=30,
            capacity_bytes=1024 * 1024,
            checkpoint=checkpoint,
        ),
    )
    assert result.event_stats is not None
    print(json.dumps({
        "policy": "E(q)",
        "q_attempts_per_hour": 30,
        "capacity_bytes": 1024 * 1024,
        "checkpoint": checkpoint.isoformat(),
        "feed_polls": result.observer_costs.feed_requests,
        "body_get_attempts": result.observer_costs.body_requests,
        "outcomes": dict(result.outcome_counts),
        "capture_attempts": result.captures_attempted,
        "captures_admitted": result.captures_admitted,
        "retained_captures": len(result.retained_captures),
        "max_queue_depth": result.event_stats.max_queue_depth,
        "coalesced_updates": result.event_stats.coalesced_updates,
        "token_starved_dispatch_opportunities": (
            result.event_stats.token_starved_dispatch_opportunities
        ),
        "final_store_bytes": result.storage_snapshot.final_store_bytes,
        "pending_dirty_pages": len(result.event_stats.pending_dirty_pages),
    }, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
