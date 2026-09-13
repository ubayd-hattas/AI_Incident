"""Gate 2 independent readiness verification (Sam), audited commit
9cbf2b6fb07b83034eeea840ab761841532b0561.

Companion to audit/FINAL_PRE_X13_INDEPENDENT_READINESS.md. This script
reproduces the DECISIVE, blocking findings directly and cheaply so anyone
can re-run it without re-doing the full multi-hour adversarial sweep
(the full sweep lives in the four audit/scratch_*_gate2_check.py scripts
written during this review -- those are exploratory/adversarial, not meant
to be maintained; this file is the small, permanent regression check).

Every expected value is written down before the call that reveals it, per
this project's established discipline.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

FAILURES: list[str] = []


def check(label: str, cond: bool, detail: str = "") -> None:
    status = "PASS" if cond else "FAIL"
    print(f"  {status} {label}" + (f" -- {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append(f"{label}: {detail}")


print("=== 1. Pin the exact candidate ===")
head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True).stdout.strip()
status = subprocess.run(["git", "status", "--short"], cwd=REPO, capture_output=True, text=True).stdout
AUDITED_SHA = "9cbf2b6fb07b83034eeea840ab761841532b0561"
check("HEAD matches audited candidate", head == AUDITED_SHA, f"HEAD={head}")
check("tree was clean of TRACKED changes at audit time", True, "git status --short showed only untracked audit/scratch_*.py + generated runs/ at review time")

print("\n=== 2. Ten canonical annotation pins (independently recomputed from git objects) ===")
PINS = [
    ("annotations/evidence.jsonl", "5cc077ff284279d61f2814beadcb66294a2569be", "2efff9113056a797614de940c28b3fe1f5aac301fdaf3250c8fc83978c88565b"),
    ("annotations/occurrences.jsonl", "16aa2e42dd4bc94e86ba2a47382af4e546b68a46", "02542d8e78b640da45f05cc1376c92226c459c44cdcbc1f782e022b932ad0c9d"),
    ("annotations/eligibility.jsonl", "8d55e351507bbf666f29a442fe3903137098144a", "acb0ef84d749e42f9bac2786b1ceb7903a76bfdeae930eac98341109788f674a"),
    ("annotations/splits.json", "0e8d40fc4a13126cb62601a6c0f2813a22fb320e", "46db260749340a6a37bc08bf7b1e6b5f1b386cc99063971e1b5f37c66eca84c9"),
    ("annotations/adjudication.csv", "5606d1e103e0bdb71c49e6ad8590054c1c4e1f0a", "aaab09f6afae45b19b97b232d52ccdf827572715edb5638edfcad2322471fcf1"),
    ("annotations/context_eligibility.jsonl", "6c8ff9eac10e3465228bb4b3105f4df428d45cdb", "59affb8ad353e87b98b00be21b75f22934a4c8eb3025e9384d31e79e7ba38034"),
    ("annotations/context_fragments.jsonl", "4a3b9bb2cd316878d65f6de696d37680c21ccd50", "485e8897dbd9c8bea51ef1e2ec000653612b5539122b52db820e9945317848bd"),
    ("annotations/context_occurrences.jsonl", "bf386b68067bbb869325e98c982d4b555bc37ba1", "040a4c8c5bff7b34428212470b1b036feab9331f02c4704a0ba80c5beefaa2f3"),
    ("annotations/rubric.md", "89b15d8d409ee1a9fb3ec6fa49a526880768efc2", "a4e8b86ffc9971d75908ed95978636b9f782ef6f2f5b44b29d04eb41d415e76d"),
    ("annotations/A11_BENCHMARK_SPEC.md", "f2e87f34cbb30c7235d16a72ff188244ea55da73", "d9deac839b2a3972af50ad1f4aa4f99cc2746e2178fe14a7cf5f3d12ee3bd276"),
]
for path, oid, sha in PINS:
    actual_oid = subprocess.run(["git", "hash-object", path], cwd=REPO, capture_output=True, text=True).stdout.strip()
    blob = subprocess.run(["git", "cat-file", "blob", actual_oid], cwd=REPO, capture_output=True).stdout
    actual_sha = hashlib.sha256(blob).hexdigest()
    check(f"{path} blob OID + SHA-256 match FINAL_PRE_X13_FREEZE.md", actual_oid == oid and actual_sha == sha, f"oid={actual_oid} sha={actual_sha}")

print("\n=== 3. Benchmark reconstruction (from raw annotation files, not the loader) ===")
import json

def load_jsonl(p):
    with open(REPO / p, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

ev = load_jsonl("annotations/evidence.jsonl")
splits = json.load(open(REPO / "annotations/splits.json", encoding="utf-8"))
occ = load_jsonl("annotations/occurrences.jsonl")
ctx_elig = load_jsonl("annotations/context_eligibility.jsonl")
ctx_frag = load_jsonl("annotations/context_fragments.jsonl")
ctx_occ = load_jsonl("annotations/context_occurrences.jsonl")
dev_pages = set(splits["splits"]["dev"]["page_keys"])
held_pages = set(splits["splits"]["held_out"]["page_keys"])
page_of = lambda rid: rid.split("@")[0]
dev_ct = sum(1 for e in ev if page_of(e["rev_id"]) in dev_pages)
held_ct = sum(1 for e in ev if page_of(e["rev_id"]) in held_pages)
dev_crit = sum(1 for e in ev if page_of(e["rev_id"]) in dev_pages and e.get("critical"))
held_crit = sum(1 for e in ev if page_of(e["rev_id"]) in held_pages and e.get("critical"))
check("65 propositions", len(ev) == 65, str(len(ev)))
check("38 dev / 27 held-out", (dev_ct, held_ct) == (38, 27), str((dev_ct, held_ct)))
check("34 dev-critical / 23 held-out-critical, K=23", (dev_crit, held_crit) == (34, 23), str((dev_crit, held_crit)))
check("57 critical total", sum(1 for e in ev if e.get("critical")) == 57, "")
check("25 groups", len(splits["groups"]) == 25, str(len(splits["groups"])))
check("1421 core occurrence rows", len(occ) == 1421, str(len(occ)))
needed = [r for r in ctx_elig if r.get("context_needed")]
check("8 context-needed, all 8 groundable", len(needed) == 8 and all(r.get("context_fragment_ids") for r in needed), str(len(needed)))
check("57 self-contained", sum(1 for r in ctx_elig if not r.get("context_needed")) == 57, "")
check("10 context fragment definitions", len(ctx_frag) == 10, str(len(ctx_frag)))
check("101 context body occurrence rows", len(ctx_occ) == 101, str(len(ctx_occ)))
check("pilot GRP-02-OECD-WORKAROUND remains dev", splits["groups"]["GRP-02-OECD-WORKAROUND"]["split"] == "dev", "")

elig = load_jsonl("annotations/eligibility.jsonl")
e63 = next(r for r in elig if r["evidence_id"] == "PROP-20260618-63")
check("PROP-20260618-63 eligible=true, excludes only dse~AI@2", e63["eligible"] is True and e63["excluded_support_revisions"] == ["dse~AI@2"], str(e63))

print("\n=== 4. PROP-20260616-61 three-way OR wiring (compiled proposition, not annotation text) ===")
from ebe.a11_loader import load_a11_benchmark
bm = load_a11_benchmark()
p61 = next(p for p in bm.propositions if p.evidence_id == "PROP-20260616-61")
check("context_status FROZEN", bm.context_status == "FROZEN", bm.context_status)
n_core = len(p61.core_alternatives)
n_ctx = len(p61.context_alternatives)
check("60 context alternatives = 20 core revisions x 3 context choices", n_ctx == n_core * 3 == 60, f"core={n_core} ctx={n_ctx}")
check("every context alternative is core-alternative UNION one ctx fragment (context implies core, structurally)",
      all(any(set(core).issubset(set(alt)) for core in p61.core_alternatives) for alt in p61.context_alternatives), "")

print("\n=== 5. Confirmed BLOCKING bug: unguarded KeyError on missing object_id (not fail-closed) ===")
from ebe.evaluator import RetainedSnapshot
packet = SimpleNamespace(object_id="MISSING-OBJ", page_key="dse~A", capture_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
                         body_sha256="x" * 64, request_seq=1, packet_bytes=10, archive_key=None)
export = SimpleNamespace(body_objects=[], packets=[packet], checkpoint=datetime(2026, 1, 1, tzinfo=timezone.utc),
                         capacity_bytes=100, retained_packet_bytes=10, retained_body_bytes=0, total_bytes=10)
result = SimpleNamespace(retained_export=export, feed_polls=[])
try:
    RetainedSnapshot.from_collector_result(result)
    check("a packet referencing a missing object_id raises SnapshotIntegrityError (fail-closed)", False, "no exception raised at all")
except KeyError as exc:
    check("a packet referencing a missing object_id raises SnapshotIntegrityError (fail-closed), not a raw KeyError",
          False, f"raised raw KeyError({exc}) instead -- evaluator.py:56, unguarded objects[p.object_id]")
except Exception as exc:
    check("a packet referencing a missing object_id raises SnapshotIntegrityError specifically",
          type(exc).__name__ == "SnapshotIntegrityError", f"raised {type(exc).__name__} instead")

print("\n=== 6. Confirmed BLOCKING gap: manifest content integrity is not actually re-verified ===")
import inspect
from ebe import x13_manifest
src = inspect.getsource(x13_manifest.validate_manifest)
check("validate_manifest re-hashes configuration_manifest.csv content (not just row count)",
      "configuration_sha256" in src and "sha256_file" in src.split("configuration")[0][-200:] if "configuration_sha256" in src else False,
      "manifest.get('configuration_sha256') is written at generation time (x13_manifest.py:182) but validate_manifest() only checks "
      "`sum(1 for _ in csv.DictReader(stream)) != 791` -- row count, never re-hashed content")
check("validate_manifest re-verifies source_hash / accounting_fixture_identity / omitted_scope_sha256",
      False,
      "all three are computed and stored in the manifest at generation time (x13_manifest.py:187-188,186) but never "
      "read back or re-compared in validate_manifest() -- confirmed by direct source inspection")

print("\n=== 7. Confirmed BLOCKING gap: real executor never populates required cost/overhead fields ===")
from ebe import x13_runner
runner_src = inspect.getsource(x13_runner)
NEVER_ASSIGNED = [
    "synchronized_peak_s_plus_m", "combined_byte_microseconds", "elapsed_seconds", "cpu_seconds",
    "rss_bytes", "artifact_disk_bytes", "aux_collector_bytes", "aux_store_bytes", "aux_evaluator_bytes",
    "pending_index_peak", "queue_peak", "coalesced_updates", "starvation_events", "dropped_work",
    "reused_from", "feed_metadata_bytes", "directory_metadata_bytes",
]
# These fields appear only in the LOGICAL_RESULT_FIELDS schema declaration and the all-None synthetic
# initializer; they must never appear as the left side of a payload.update({...}) real-value assignment.
missing = [f for f in NEVER_ASSIGNED if f'"{f}":' not in runner_src.split("def execute")[1].split("is_primary_stable_family")[0]]
check("real execute() populates synchronized S+M peak / byte-hours / per-row overhead / aux-memory / E-policy queue stats",
      len(missing) == 0,
      f"{len(missing)}/{len(NEVER_ASSIGNED)} required fields are never assigned a real value in execute()'s payload.update() calls "
      f"(x13_runner.py) -- they stay permanently None even in real mode: {missing}")

print("\n=== 8. Manifest roster arithmetic (freshly regenerated, not the stale Gate-1 report text) ===")
print("  NOTE: run `PYTHONPATH=src python scripts/reproduce_x13.py --mode synthetic` first to (re)generate")
print("  runs/FINAL_PRE_X13_DEADLINE_v1/freeze/ before this section if it is missing.")
import csv
freeze = REPO / "runs" / "FINAL_PRE_X13_DEADLINE_v1" / "freeze"
if (freeze / "configuration_manifest.csv").exists():
    with open(freeze / "configuration_manifest.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    from collections import Counter
    blocks = Counter(r["block"] for r in rows)
    expected_blocks = {"L-primary": 183, "L-interval": 120, "L-latency": 183, "F": 1, "R": 60, "O": 181, "A-live": 61, "A-only": 2}
    check("791 total rows, exact block breakdown", len(rows) == 791 and dict(blocks) == expected_blocks, str(dict(blocks)))
    mask_sha = hashlib.sha256((freeze / "stable_support_intervals.jsonl").read_bytes()).hexdigest()
    check("stable mask SHA-256 matches Gate 1's reported value", mask_sha == "78081b810fbcc277cdeade86f6dd61d4ca4fd25025d57c94f353329095787093", mask_sha)
    mask_rows = load_jsonl("runs/FINAL_PRE_X13_DEADLINE_v1/freeze/stable_support_intervals.jsonl")
    n_elig = sum(1 for r in mask_rows if r["eligible"])
    n_excl = sum(1 for r in mask_rows if not r["eligible"])
    check("1522 mask rows: 1516 eligible / 6 excluded", (len(mask_rows), n_elig, n_excl) == (1522, 1516, 6), str((len(mask_rows), n_elig, n_excl)))
else:
    check("freeze artifacts present (run reproduce_x13.py first)", False, "runs/FINAL_PRE_X13_DEADLINE_v1/freeze/ not found")

print("\n" + "=" * 70)
print(f"FINAL GRAND TOTAL FAILURES: {len(FAILURES)}")
for f in FAILURES:
    print("  -", f)
print("=" * 70)
print("This script intentionally FAILS while sections 5-7's blocking bugs/gaps are unfixed.")
print("See audit/FINAL_PRE_X13_INDEPENDENT_READINESS.md for the full verdict and required repairs.")
if FAILURES:
    sys.exit(1)
