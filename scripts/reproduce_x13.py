#!/usr/bin/env python3
"""Offline Gate 1 reproduction entry point; real mode remains Gate-2 locked."""
from __future__ import annotations
import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ebe.x13_manifest import generate_manifest, validate_manifest
from ebe.x13_reporting import build_synthetic_report, create_result_scaffolding
from ebe.x13_runner import run
from ebe.support_masks import generate_stable_mask

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("synthetic", "real"), default="synthetic")
    parser.add_argument("--authorization-artifact", type=Path)
    parser.add_argument("--max-rows", type=int)
    args = parser.parse_args()
    mask = ROOT / "runs" / "FINAL_PRE_X13_DEADLINE_v1" / "freeze" / "stable_support_intervals.jsonl"
    generate_stable_mask(ROOT, mask)
    generate_manifest(ROOT, mask_path=mask)
    validate_manifest(ROOT)
    create_result_scaffolding(ROOT)
    if args.mode == "synthetic":
        build_synthetic_report(ROOT)
    started = time.perf_counter()
    counts = run(ROOT, mode=args.mode, authorization_artifact=args.authorization_artifact,
                 max_rows=args.max_rows)
    measurement = {"counts": counts, "elapsed_seconds": time.perf_counter() - started,
                   "measurement_scope": "SYNTHETIC harness only" if args.mode == "synthetic" else "authorized harness"}
    try:
        import psutil
        measurement["rss_bytes_end"] = psutil.Process().memory_info().rss
    except ImportError:
        measurement["rss_bytes_end"] = None
    print(json.dumps(measurement, sort_keys=True))
    return 0

if __name__ == "__main__": raise SystemExit(main())
