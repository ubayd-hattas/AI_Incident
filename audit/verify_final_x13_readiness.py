"""Gate 2 independent readiness verification (Sam).

Companion to audit/FINAL_PRE_X13_INDEPENDENT_READINESS.md. This script
reproduces the DECISIVE, blocking findings directly and cheaply so anyone
can re-run it against a repaired candidate without re-doing the full
multi-hour adversarial sweep (the full sweep lives in the four
audit/scratch_*_gate2_check.py scripts written during the original review
-- those are exploratory/adversarial, not meant to be maintained; this
file is the small, permanent regression check).

This script is intentionally NOT pinned to one specific commit SHA: it
records whatever HEAD currently is as "the candidate under test" and
verifies the regenerated manifest actually binds to that candidate's real
code tree, so the same script can validate today's candidate, a later
repaired candidate, or any future one, without editing a hardcoded SHA
each time.

Every expected value is written down before the call that reveals it, per
this project's established discipline. Section 6's manifest-integrity
checks are real behavioral mutation tests (they mutate a throwaway scratch
copy and confirm validate_manifest() actually rejects the tampering) --
they are not hardcoded to fail; they will start reporting PASS the moment
the underlying gap is fixed, with no changes needed to this script.
"""
from __future__ import annotations

import csv
import hashlib
import inspect
import shutil
import subprocess
import sys
import tempfile
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
tree_status = subprocess.run(["git", "status", "--short"], cwd=REPO, capture_output=True, text=True).stdout
tracked_dirty = [line for line in tree_status.splitlines() if not line.lstrip().startswith("??")]
print(f"  CANDIDATE SHA (this run): {head}")
check("tree has no uncommitted changes to TRACKED files", len(tracked_dirty) == 0, f"dirty tracked files: {tracked_dirty}")

from ebe.x13_manifest import generate_manifest, validate_manifest, _code_state_hash  # noqa: E402
from ebe.support_masks import generate_stable_mask  # noqa: E402
freeze = REPO / "runs" / "FINAL_PRE_X13_DEADLINE_v1" / "freeze"
mask_path = freeze / "stable_support_intervals.jsonl"
generate_stable_mask(REPO, mask_path)
generate_manifest(REPO, mask_path=mask_path)
try:
    manifest = validate_manifest(REPO)
    expected_code_hash = _code_state_hash(REPO)
    check("regenerated manifest's code_state_sha256 correctly binds to THIS candidate's real code tree (not a stale/hardcoded SHA)",
          manifest.get("code_state_sha256") == expected_code_hash,
          f"manifest={manifest.get('code_state_sha256')} recomputed={expected_code_hash}")
    manifest_sha256 = (freeze / "manifest.sha256").read_text(encoding="ascii").split()[0]
    print(f"  MANIFEST SHA-256 (run_manifest.json) for candidate {head}: {manifest_sha256}")
except Exception as exc:
    check("manifest regenerates and validates cleanly for this candidate", False, f"{type(exc).__name__}: {exc}")

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

print("\n=== 6. Manifest content integrity: does validate_manifest() reject real tampering? (behavioral, not hardcoded) ===")


def _build_scratch_repo() -> Path:
    """A throwaway stand-in repo so mutation tests never touch real frozen project data.

    Copies only the actual audited SOURCE CODE verbatim (src/ebe/*.py, scripts/reproduce_x13.py,
    configs/x13_deadline_v1.json) since generate_manifest/_code_state_hash hash these files' real
    bytes. Everything generate_manifest only HASHES (never semantically parses) -- annotations,
    raw source export, accounting fixtures -- is tiny invented placeholder content, which is
    sufficient because this section tests hash re-verification, not annotation/loader correctness
    (that is covered independently in sections 3-4 against the real files).
    """
    scratch = Path(tempfile.mkdtemp(prefix="x13_manifest_mutation_check_"))
    (scratch / "src" / "ebe").mkdir(parents=True)
    for f in (REPO / "src" / "ebe").glob("*.py"):
        shutil.copy2(f, scratch / "src" / "ebe" / f.name)
    (scratch / "scripts").mkdir()
    shutil.copy2(REPO / "scripts" / "reproduce_x13.py", scratch / "scripts" / "reproduce_x13.py")
    (scratch / "configs").mkdir()
    shutil.copy2(REPO / "configs" / "x13_deadline_v1.json", scratch / "configs" / "x13_deadline_v1.json")
    (scratch / "annotations").mkdir()
    for name in ("evidence.jsonl", "occurrences.jsonl", "eligibility.jsonl", "splits.json",
                 "adjudication.csv", "context_eligibility.jsonl", "context_fragments.jsonl",
                 "context_occurrences.jsonl", "rubric.md", "A11_BENCHMARK_SPEC.md"):
        (scratch / "annotations" / name).write_text(f"invented placeholder content for {name}\n", encoding="utf-8")
    (scratch / "data" / "raw" / "export").mkdir(parents=True)
    (scratch / "data" / "raw" / "export" / "events.jsonl").write_text('{"invented":"event"}\n', encoding="utf-8")
    (scratch / "data" / "raw" / "export" / "revisions.jsonl").write_text('{"invented":"revision"}\n', encoding="utf-8")
    (scratch / "tests" / "fixtures" / "accounting").mkdir(parents=True)
    (scratch / "tests" / "fixtures" / "accounting" / "fixture_a.json").write_text('{"invented":"fixture"}\n', encoding="utf-8")
    return scratch


def _rewrite_csv_field(path: Path, fieldnames: list[str], row_index: int, field: str, new_value: str) -> None:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    rows[row_index][field] = new_value
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _mutate_config_manifest(scratch: Path) -> None:
    path = scratch / "runs" / "FINAL_PRE_X13_DEADLINE_v1" / "freeze" / "configuration_manifest.csv"
    with path.open(encoding="utf-8", newline="") as f:
        row_count = sum(1 for _ in csv.DictReader(f))
    _rewrite_csv_field(path, ["ordinal", "run_id", "block", "config_json"], row_count - 1,
                       "config_json", "TAMPERED-CONFIG-JSON")  # row count unchanged, content changed


def _mutate_omitted_scope(scratch: Path) -> None:
    path = scratch / "runs" / "FINAL_PRE_X13_DEADLINE_v1" / "freeze" / "omitted_scope.csv"
    _rewrite_csv_field(path, ["scope_id", "family", "status"], 0, "status", "TAMPERED-STATUS")


def _mutate_source_input(scratch: Path) -> None:
    path = scratch / "data" / "raw" / "export" / "revisions.jsonl"
    path.write_text(path.read_text(encoding="utf-8") + '{"tampered":true}\n', encoding="utf-8")


def _mutate_accounting_fixture(scratch: Path) -> None:
    path = scratch / "tests" / "fixtures" / "accounting" / "fixture_a.json"
    path.write_text('{"invented":"TAMPERED"}\n', encoding="utf-8")


def _assert_mutation_rejected(scratch: Path, label: str, mutate) -> None:
    generate_manifest(scratch)  # fresh, clean baseline every time -- no compounding mutations
    mutate(scratch)
    try:
        validate_manifest(scratch)
        check(label, False, "validate_manifest() did NOT raise after the mutation -- content tampering goes undetected")
    except Exception as exc:
        check(label, True, f"correctly rejected via {type(exc).__name__}: {exc}")


_scratch_repo = _build_scratch_repo()
try:
    _assert_mutation_rejected(_scratch_repo,
        "validate_manifest() rejects a configuration_manifest.csv content mutation (row count held at 791-equivalent)",
        _mutate_config_manifest)
    _assert_mutation_rejected(_scratch_repo,
        "validate_manifest() rejects an omitted_scope.csv content mutation",
        _mutate_omitted_scope)
    _assert_mutation_rejected(_scratch_repo,
        "validate_manifest() rejects a source-input (data/raw/export) mutation made after manifest generation",
        _mutate_source_input)
    _assert_mutation_rejected(_scratch_repo,
        "validate_manifest() rejects an accounting-fixture mutation made after manifest generation",
        _mutate_accounting_fixture)
finally:
    shutil.rmtree(_scratch_repo, ignore_errors=True)

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

print("\n=== 8. Manifest roster arithmetic (freshly regenerated in section 1 against THIS candidate) ===")
if (freeze / "configuration_manifest.csv").exists():
    with open(freeze / "configuration_manifest.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    from collections import Counter
    blocks = Counter(r["block"] for r in rows)
    expected_blocks = {"L-primary": 183, "L-interval": 120, "L-latency": 183, "F": 1, "R": 60, "O": 181, "A-live": 61, "A-only": 2}
    check("791 total rows, exact block breakdown", len(rows) == 791 and dict(blocks) == expected_blocks, str(dict(blocks)))
    mask_sha = hashlib.sha256((freeze / "stable_support_intervals.jsonl").read_bytes()).hexdigest()
    check("stable mask SHA-256 matches the last-known-good value (depends only on frozen annotation content, not code state, so should be stable across engineering-only repairs)",
          mask_sha == "78081b810fbcc277cdeade86f6dd61d4ca4fd25025d57c94f353329095787093", mask_sha)
    mask_rows = load_jsonl("runs/FINAL_PRE_X13_DEADLINE_v1/freeze/stable_support_intervals.jsonl")
    n_elig = sum(1 for r in mask_rows if r["eligible"])
    n_excl = sum(1 for r in mask_rows if not r["eligible"])
    check("1522 mask rows: 1516 eligible / 6 excluded", (len(mask_rows), n_elig, n_excl) == (1522, 1516, 6), str((len(mask_rows), n_elig, n_excl)))
else:
    check("freeze artifacts present (regenerated in section 1)", False, "runs/FINAL_PRE_X13_DEADLINE_v1/freeze/ not found -- section 1 must have failed before writing it")

print("\n" + "=" * 70)
print(f"FINAL GRAND TOTAL FAILURES: {len(FAILURES)}")
for f in FAILURES:
    print("  -", f)
print("=" * 70)
print("Sections 5-7 test real behavior, not a fixed expectation: each will report PASS on its own, with")
print("no changes to this script, the moment the underlying implementation gap it targets is fixed.")
print("See audit/FINAL_PRE_X13_INDEPENDENT_READINESS.md for the original full verdict and repair list.")
if FAILURES:
    sys.exit(1)
