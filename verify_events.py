#!/usr/bin/env python3
"""
Reproducibility script for "Evidence Before Erasure".

Run this against your own downloaded copy of the collusion.wiki export
to independently confirm the claims used in data/evidence_timeline.csv.

Usage:
    python verify_events.py /path/to/export/events.jsonl

Expects a directory containing events.jsonl, revisions.jsonl, and
manifest.json downloaded from https://collusion.wiki/explorer/download
"""
import sys
import json
import hashlib
import collections
from pathlib import Path

# Published checksums from https://collusion.wiki/explorer/download
KNOWN_HASHES = {
    "manifest.json": "b6d53e16b5d9a6a0a98d4577238835ee7a574d7d10a8f1312330b4e626c6ba2b",
    "events.jsonl": "588584295f1c4a7c3d90b04075ab151504f165ff069534d935cda08853ec28b1",
    "revisions.jsonl": "60df4a515178230aa952d9f64f6215aea4bd95ab2f05e31e484cf9b887e3f793",
}

# The specific record IDs the headline "12-second survival" claim depends on
TARGET_EVENT_IDS = {
    "delete:dse:rclog:145609",  # original page deleted
    "delete:dse:rclog:145611",  # ZZZ backup deleted, 12s later
    "delete:dse:rclog:145962",  # separate page deleted
    "revert:delete:dse:rclog:145962",  # ...then reverted with no body
}


def verify_checksum(path: Path) -> bool:
    name = path.name
    expected = KNOWN_HASHES.get(name)
    if not expected:
        print(f"  [skip] no known checksum for {name}")
        return True
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    ok = actual == expected
    print(f"  {name}: {'OK' if ok else 'MISMATCH'}")
    print(f"    expected: {expected}")
    print(f"    actual:   {actual}")
    return ok


def tally_event_types(events_path: Path):
    counts = collections.Counter()
    total = 0
    with events_path.open(encoding="utf-8") as f:
        for line in f:
            total += 1
            counts[json.loads(line).get("event_type")] += 1
    print(f"\nEvent type tally (total={total}):")
    for k, v in sorted(counts.items()):
        print(f"  {k}: {v}")
    expected = {"save": 14591, "delete": 5217, "revert": 4, "probe": 101}
    matches = counts == collections.Counter(expected)
    print(f"Matches published breakdown: {matches}")
    return matches


def extract_target_events(events_path: Path):
    print("\nTarget event records:")
    found = {}
    with events_path.open(encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            if d.get("event_id") in TARGET_EVENT_IDS:
                found[d["event_id"]] = d
                print(f"  {d['event_id']}: {d['page']} @ {d['time']}")
    missing = TARGET_EVENT_IDS - found.keys()
    if missing:
        print(f"  WARNING - not found: {missing}")

    if "delete:dse:rclog:145609" in found and "delete:dse:rclog:145611" in found:
        from datetime import datetime
        t1 = datetime.fromisoformat(found["delete:dse:rclog:145609"]["time"].replace("Z", "+00:00"))
        t2 = datetime.fromisoformat(found["delete:dse:rclog:145611"]["time"].replace("Z", "+00:00"))
        gap = (t2 - t1).total_seconds()
        print(f"\n  Survival gap (backup vs original deletion): {gap:.0f} seconds")
    return found


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    events_path = Path(sys.argv[1])
    export_dir = events_path.parent

    print("=== Checksum verification ===")
    for name in KNOWN_HASHES:
        p = export_dir / name
        if p.exists():
            verify_checksum(p)
        else:
            print(f"  [missing] {name} not found in {export_dir}")

    print("\n=== Event type reconciliation ===")
    tally_event_types(events_path)

    print("\n=== Targeted record extraction ===")
    extract_target_events(events_path)


if __name__ == "__main__":
    main()
