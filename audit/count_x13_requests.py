#!/usr/bin/env python3
"""Outcome-blind exact request-schedule arithmetic for frozen X13 rows."""
from __future__ import annotations

import csv
import json
import math
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ebe.ingest import load_export
from ebe.schema import ObservedEventSemantics
from ebe.timeline import HORIZON_START

POLL_US = 60_000_000
HOUR_US = 3_600_000_000


def us(when: datetime) -> int:
    delta = when - HORIZON_START
    return delta.days * 86_400_000_000 + delta.seconds * 1_000_000 + delta.microseconds


def feed_batches(export, lag_us: int, checkpoint_us: int):
    buckets = defaultdict(list)
    for index, event in enumerate(export.events):
        if event.wiki != "dse" or event.page_key is None:
            continue
        if event.observed_semantics is ObservedEventSemantics.NON_MUTATION_PROBE:
            continue
        action = ("delete" if event.observed_semantics is
                  ObservedEventSemantics.SUCCESSFUL_DELETION else "live_change")
        publication = us(event.time.utc) + lag_us
        poll = math.ceil(publication / POLL_US) * POLL_US
        if poll <= checkpoint_us:
            buckets[poll].append((us(event.time.utc), event.page_key, action, index))
    return {when: sorted(records, key=lambda x: (x[0], x[1], x[2], x[3]))
            for when, records in buckets.items()}


def apply_batch(records, beliefs, dirty_set=None, dirty_times=None):
    live_delta = 0
    index = 0
    while index < len(records):
        event_time, page, _, _ = records[index]
        end = index + 1
        while end < len(records) and records[end][:2] == (event_time, page):
            end += 1
        actions = {item[2] for item in records[index:end]}
        was_live = beliefs.get(page) in {"live", "mixed"}
        if actions == {"delete"}:
            beliefs[page] = "deleted"
            if dirty_set is not None: dirty_set.discard(page)
            if dirty_times is not None: dirty_times.pop(page, None)
        else:
            beliefs[page] = "live" if actions == {"live_change"} else "mixed"
            if dirty_set is not None: dirty_set.add(page)
            if dirty_times is not None and page not in dirty_times:
                dirty_times[page] = event_time
        is_live = beliefs.get(page) in {"live", "mixed"}
        live_delta += int(is_live) - int(was_live)
        index = end
    return live_delta


def periodic_count(export, cfg):
    checkpoint = datetime.fromisoformat(cfg["checkpoint"].replace("Z", "+00:00"))
    end = us(checkpoint)
    batches = feed_batches(export, cfg["feed_lag_us"], end)
    beliefs = {}; dirty = set(); count = 0; live_count = 0
    interval = cfg["interval_us"]; sweep = cfg["phase_us"]
    poll_times = iter(sorted(batches)); next_poll = next(poll_times, None)
    while sweep < end:
        while next_poll is not None and next_poll <= sweep:
            live_count += apply_batch(batches[next_poll], beliefs, dirty_set=dirty)
            next_poll = next(poll_times, None)
        if cfg["policy"] == "PCD":
            count += len(dirty)
            dirty.clear()
        else:
            count += live_count
        sweep += interval
    polls = end // cfg["feed_poll_interval_us"] + 1
    return polls, count


def event_count(export, cfg):
    checkpoint = datetime.fromisoformat(cfg["checkpoint"].replace("Z", "+00:00"))
    end = us(checkpoint); batches = feed_batches(export, cfg["feed_lag_us"], end)
    dirty = {}; beliefs = {}; requests = 0
    q = cfg["q"]; capacity = q * HOUR_US; credit = capacity; last = 0
    for dispatch in range(0, end, POLL_US):
        if dispatch in batches:
            apply_batch(batches[dispatch], beliefs, dirty_times=dirty)
        credit = min(capacity, credit + q * (dispatch - last)); last = dispatch
        while dirty and credit >= HOUR_US:
            oldest = min(dirty.values())
            tied = [key for key, value in dirty.items() if value == oldest]
            page = max(tied) if cfg["order"] == "reverse_ties" else min(tied)
            del dirty[page]; requests += 1; credit -= HOUR_US
    polls = end // cfg["feed_poll_interval_us"] + 1
    return polls, requests


def main() -> int:
    export = load_export(ROOT / "data" / "raw" / "export")
    archive_requests = 1 + sum(r.wiki == "dse" and r.time.utc <=
                               datetime(2026, 7, 15, tzinfo=timezone.utc)
                               for r in export.revisions)
    manifest = ROOT / "runs" / "FINAL_PRE_X13_DEADLINE_v1" / "freeze" / "configuration_manifest.csv"
    rows = list(csv.DictReader(manifest.open(encoding="utf-8", newline="")))
    grouped = defaultdict(list)
    cache = {}
    for row in rows:
        cfg = json.loads(row["config_json"]); policy = cfg["policy"]
        if policy in {"P", "PD", "PCD"}:
            schedule_policy = "P" if policy in {"P", "PD"} else policy
            cache_key = (schedule_policy, cfg["interval_us"], cfg["phase_us"],
                         cfg["feed_lag_us"], cfg["feed_poll_interval_us"], cfg["checkpoint"])
            if cache_key not in cache:
                cache[cache_key] = periodic_count(export, cfg)
            polls, bodies = cache[cache_key]
        elif policy == "E":
            cache_key = (policy, cfg["q"], cfg["feed_lag_us"],
                         cfg["feed_poll_interval_us"], cfg["checkpoint"], cfg["order"])
            if cache_key not in cache:
                cache[cache_key] = event_count(export, cfg)
            polls, bodies = cache[cache_key]
        elif policy == "F":
            # One terminal directory plus one GET for every uniquely live title.
            # The exact live-title count is obtained by the terminal collection
            # audit; this schedule-only census records the known upper bound.
            polls, bodies = 0, 1 + 5_154
        elif policy == "A-only":
            polls, bodies = 0, archive_requests
        else:
            continue
        if cfg["archive"] == "terminal_persistent" and policy != "A-only":
            bodies += archive_requests
        key = (row["block"], policy, cfg.get("interval_us"), cfg.get("q"),
               cfg["feed_lag_us"], cfg["delay_us"], cfg["order"], cfg["archive"])
        grouped[key].append(polls + bodies)
    for key, values in sorted(grouped.items(), key=lambda item: repr(item[0])):
        print(json.dumps({
            "family": key, "rows": len(values), "min_total_requests": min(values),
            "median_total_requests": statistics.median(values),
            "max_total_requests": max(values), "sum_total_requests": sum(values),
        }, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
