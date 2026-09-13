"""Throwaway Gate-2 independent audit script for the X13 runner lock, resume
behavior, and reporting math. FULLY SYNTHETIC/OFFLINE: builds an isolated
scratch copy of the repo under a temp directory (copying only the actual
audited SOURCE CODE verbatim -- src/ebe/*.py and scripts/reproduce_x13.py --
and fabricating tiny invented stand-ins for data/annotations/config/fixtures).
Never touches the real runs/FINAL_PRE_X13_DEADLINE_v1 tree, never inspects
real annotations/results, never invokes --mode real to completion (only to
confirm it is refused, or -- once correctly authorized in this sandbox --
that it fails for unrelated missing-fixture reasons rather than succeeding).

Not committed; not wired into CI. Run with:
    python audit/scratch_runner_gate2_check.py
"""
from __future__ import annotations

import csv
import json
import shutil
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

REAL_REPO = Path(__file__).resolve().parents[1]
TMP = Path(tempfile.mkdtemp(prefix="gate2_audit_"))
REPO = TMP / "repo"

RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name} :: {detail}")


def build_scratch_repo() -> None:
    REPO.mkdir(parents=True)
    for d in ("data/raw/export", "annotations", "configs",
              "tests/fixtures/accounting", "scripts"):
        (REPO / d).mkdir(parents=True, exist_ok=True)
    shutil.copytree(REAL_REPO / "src/ebe", REPO / "src/ebe")
    shutil.copy(REAL_REPO / "scripts/reproduce_x13.py", REPO / "scripts/reproduce_x13.py")

    (REPO / "data/raw/export/events.jsonl").write_text("", encoding="utf-8")
    revisions = [
        {"wiki": "dse", "rev_id": "REV-0001", "page_key": "PAGE-A", "body": "hello world",
         "body_encoding": "ascii", "time": "2026-01-01T00:00:00Z", "uncertainty_seconds": 0},
        {"wiki": "dse", "rev_id": "REV-0002", "page_key": "PAGE-A", "body": "hello world v2",
         "body_encoding": "ascii", "time": "2026-01-02T00:00:00Z", "uncertainty_seconds": 5},
    ]
    with (REPO / "data/raw/export/revisions.jsonl").open("w", encoding="utf-8") as f:
        for r in revisions:
            f.write(json.dumps(r) + "\n")

    annotation_files = {
        "evidence.jsonl": "",
        "occurrences.jsonl": json.dumps({"occurrence_id": "OCC-0001", "rev_id": "REV-0001"}) + "\n",
        "eligibility.jsonl": "", "splits.json": "{}", "adjudication.csv": "id\n",
        "context_eligibility.jsonl": "", "context_fragments.jsonl": "",
        "context_occurrences.jsonl": json.dumps({"context_fragment_id": "CTX-0001", "rev_id": "REV-0002"}) + "\n",
        "rubric.md": "# fixture rubric\n", "A11_BENCHMARK_SPEC.md": "# fixture spec\n",
    }
    for name, content in annotation_files.items():
        (REPO / "annotations" / name).write_text(content, encoding="utf-8")
    (REPO / "tests/fixtures/accounting/fixture_a.json").write_text(
        json.dumps({"fixture": "SYNTHETIC"}), encoding="utf-8")
    (REPO / "configs/x13_deadline_v1.json").write_text(
        json.dumps({"fixture": "SYNTHETIC_CONFIG_RECIPE"}), encoding="utf-8")


build_scratch_repo()
sys.path.insert(0, str(REPO / "src"))

from ebe.x13_manifest import (generate_manifest, validate_manifest, sha256_file,
                               AMENDMENT, RUN_ROOT_NAME)
from ebe.support_masks import generate_stable_mask
from ebe.x13_reporting import (create_result_scaffolding, build_synthetic_report,
                                primary_label, exact_percentage, linear_quantile,
                                phase_summary, request_admissible, primary_difference,
                                group_robustness, PRIMARY_LABELS)
from ebe import x13_runner
from ebe.x13_runner import run, AuthorizationError, ResumeMismatchError

FREEZE = REPO / "runs" / RUN_ROOT_NAME / "freeze"
MASK = FREEZE / "stable_support_intervals.jsonl"


def fresh_pipeline():
    if (REPO / "runs").exists():
        shutil.rmtree(REPO / "runs")
    generate_stable_mask(REPO, MASK)
    manifest = generate_manifest(REPO, mask_path=MASK)
    validate_manifest(REPO)
    create_result_scaffolding(REPO)
    build_synthetic_report(REPO)
    return manifest


def make_valid_artifact(manifest_sha, **overrides):
    value = {"amendment": AMENDMENT, "manifest_sha256": manifest_sha,
              "disposition": "GATE_2_PASS", "real_scoring_authorized": True,
              "independent_reviewer": "Sam (Gate 2 Independent Auditor)"}
    value.update(overrides)
    return value


# =========================== RUNNER LOCK ===================================
manifest = fresh_pipeline()
manifest_sha = manifest["manifest_sha256"]
counts = run(REPO, mode="synthetic")
check("baseline clean synthetic run: 791 COMPLETE / 0 ERROR", counts["COMPLETE"] == 791 and counts["ERROR"] == 0, str(counts))

fresh_pipeline()
try:
    run(REPO, mode="real", authorization_artifact=None)
    check("(a) real mode, no artifact -> rejected", False, "did NOT raise")
except AuthorizationError as e:
    check("(a) real mode, no artifact -> rejected", True, str(e))

garbage = TMP / "garbage.json"
garbage.write_text("not json {{{", encoding="utf-8")
try:
    run(REPO, mode="real", authorization_artifact=garbage)
    check("(b) garbage artifact -> rejected", False, "did NOT raise")
except Exception as e:
    check("(b) garbage artifact -> rejected", True, f"{type(e).__name__}: {e}")

bad_sha = TMP / "bad_manifest_sha.json"
bad_sha.write_text(json.dumps(make_valid_artifact("0" * 64)), encoding="utf-8")
try:
    run(REPO, mode="real", authorization_artifact=bad_sha)
    check("(d) wrong manifest_sha256 -> rejected", False, "did NOT raise")
except AuthorizationError as e:
    check("(d) wrong manifest_sha256 -> rejected", True, str(e))

wrong_amendment = TMP / "wrong_amendment.json"
wrong_amendment.write_text(json.dumps(make_valid_artifact(manifest_sha, amendment="OTHER")), encoding="utf-8")
try:
    run(REPO, mode="real", authorization_artifact=wrong_amendment)
    check("(c) wrong amendment/code-identity -> rejected", False, "did NOT raise")
except AuthorizationError as e:
    check("(c) wrong amendment/code-identity -> rejected", True, str(e))

fresh_pipeline()
manifest_sha_e = sha256_file(FREEZE / "run_manifest.json")
valid_for_e = TMP / "valid_e.json"
valid_for_e.write_text(json.dumps(make_valid_artifact(manifest_sha_e)), encoding="utf-8")
(REPO / "annotations" / "evidence.jsonl").write_text('{"tamper":true}\n', encoding="utf-8")
try:
    run(REPO, mode="real", authorization_artifact=valid_for_e)
    check("(e) tampered benchmark/annotation hash -> rejected", False, "did NOT raise")
except ValueError as e:
    check("(e) tampered benchmark/annotation hash -> rejected", "benchmark hash mismatch" in str(e), str(e))
(REPO / "annotations" / "evidence.jsonl").write_text("", encoding="utf-8")

fresh_pipeline()
manifest_sha_f = sha256_file(FREEZE / "run_manifest.json")
valid_for_f = TMP / "valid_f.json"
valid_for_f.write_text(json.dumps(make_valid_artifact(manifest_sha_f)), encoding="utf-8")
MASK.write_bytes(MASK.read_bytes() + b'{"support_id":"X","page_key":"y","body_sha256":null,"start_us":null,"end_us":null,"eligible":false,"reason":"TAMPER"}\n')
try:
    run(REPO, mode="real", authorization_artifact=valid_for_f)
    check("(f) tampered stable-mask hash -> rejected", False, "did NOT raise")
except ValueError as e:
    check("(f) tampered stable-mask hash -> rejected", "mask" in str(e).lower(), str(e))

fresh_pipeline()
manifest_sha_g = sha256_file(FREEZE / "run_manifest.json")
valid_for_g = TMP / "valid_g.json"
valid_for_g.write_text(json.dumps(make_valid_artifact(manifest_sha_g)), encoding="utf-8")
try:
    run(REPO, mode="real", authorization_artifact=valid_for_g, max_rows=0)
    check("valid artifact passes authorization (fails later for unrelated missing-fixture reason, not AuthorizationError)", True, "reached executor construction")
except AuthorizationError as e:
    check("valid artifact passes authorization", False, str(e))
except Exception as e:
    check("valid artifact passes authorization (fails later for unrelated missing-fixture reason, not AuthorizationError)", True, f"{type(e).__name__}: {e}")

# --- GAP: validate_manifest does not re-verify configuration_manifest.csv CONTENT,
# source_hash, omitted_scope_sha256, or accounting_fixture_identity ---
fresh_pipeline()
rows = list(csv.DictReader((FREEZE / "configuration_manifest.csv").open(encoding="utf-8", newline="")))
cfg = json.loads(rows[5]["config_json"]); cfg["capacity_bytes"] = 999999999
rows[5]["config_json"] = json.dumps(cfg)
with (FREEZE / "configuration_manifest.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["ordinal", "run_id", "block", "config_json"], lineterminator="\n")
    w.writeheader(); w.writerows(rows)
try:
    validate_manifest(REPO)
    check("[GAP] content-level tamper of configuration_manifest.csv (row count preserved) is caught", False,
          "validate_manifest did NOT catch a per-row config_json tamper -- only row COUNT is checked, not configuration_sha256 content")
except ValueError as e:
    check("content-level tamper of configuration_manifest.csv is caught", True, str(e))

fresh_pipeline()
rev_path = REPO / "data/raw/export/revisions.jsonl"
original = rev_path.read_bytes()
rev_path.write_bytes(original + b'{"wiki":"dse","rev_id":"INJECTED","page_key":"X","body":"x","body_encoding":"ascii","time":"2026-01-03T00:00:00Z","uncertainty_seconds":0}\n')
try:
    validate_manifest(REPO)
    check("[GAP] tampered source data (revisions.jsonl) is caught by validate_manifest", False,
          "source_hash is never recomputed/re-verified in validate_manifest")
except ValueError as e:
    check("tampered source data is caught", True, str(e))
rev_path.write_bytes(original)

fresh_pipeline()
acct_path = REPO / "tests/fixtures/accounting/fixture_a.json"
original_acct = acct_path.read_bytes()
acct_path.write_bytes(b'{"fixture":"TAMPERED"}')
try:
    validate_manifest(REPO)
    check("[GAP] tampered accounting fixture is caught by validate_manifest", False,
          "accounting_fixture_identity is never recomputed/re-verified in validate_manifest")
except ValueError as e:
    check("tampered accounting fixture is caught", True, str(e))
acct_path.write_bytes(original_acct)

# =========================== RESUME / INTERRUPT =============================
fresh_pipeline()
c_partial = run(REPO, mode="synthetic", max_rows=200)
status_log = FREEZE.parent / "status" / "synthetic.jsonl"
lines_partial = status_log.read_text(encoding="utf-8").splitlines()
check("partial run (max_rows=200) processes exactly 200", c_partial["COMPLETE"] == 200, str(c_partial))
c_resume = run(REPO, mode="synthetic")
lines_resume = status_log.read_text(encoding="utf-8").splitlines()
check("resume completes remaining 591 rows, 0 errors", c_resume["COMPLETE"] == 591 and c_resume["ERROR"] == 0, str(c_resume))
check("status log is append-only (old lines preserved as exact prefix)", lines_resume[:len(lines_partial)] == lines_partial, "")
row_files = sorted((FREEZE.parent / "synthetic_rows").glob("*.json"))
check("no duplicate/missing rows after resume (791 unique)", len(row_files) == 791 == len({p.name for p in row_files}), str(len(row_files)))

fresh_pipeline()
class FlakyExecutor:
    def __init__(self): self.n = 0
    def __call__(self, row):
        self.n += 1
        if self.n == 3:
            raise RuntimeError("SIMULATED_TRANSIENT_FAILURE")
        return x13_runner.synthetic_executor(row)
c1 = run(REPO, mode="synthetic", executor=FlakyExecutor())
sl_before = [json.loads(l) for l in status_log.read_text(encoding="utf-8").splitlines() if json.loads(l).get("status") == "ERROR"]
check("exactly one ERROR recorded", len(sl_before) == 1, str(len(sl_before)))
c2 = run(REPO, mode="synthetic")
sl_after = [json.loads(l) for l in status_log.read_text(encoding="utf-8").splitlines() if json.loads(l).get("status") == "ERROR"]
check("prior ERROR line preserved (append-only), not deleted on resume", sl_after == sl_before, f"before={len(sl_before)} after={len(sl_after)}")
check("errored row retried and eventually COMPLETE", c2["COMPLETE"] == 791 - c1["COMPLETE"], f"c1={c1['COMPLETE']} c2={c2['COMPLETE']}")

fresh_pipeline()
run(REPO, mode="synthetic", max_rows=100)
MASK.write_bytes(MASK.read_bytes() + b'{"support_id":"NEW","page_key":"z","body_sha256":null,"start_us":null,"end_us":null,"eligible":false,"reason":"TAMPER"}\n')
generate_manifest(REPO, mask_path=MASK)
try:
    run(REPO, mode="synthetic")
    check("resume refused after swapped scientific identity (mask/manifest changed)", False, "did NOT raise")
except ResumeMismatchError as e:
    check("resume refused after swapped scientific identity (mask/manifest changed)", True, str(e))

# =========================== REPORTING (invented values only) ==============
check("exactly 10pp -> THRESHOLD_MET", primary_label(Fraction(10), admissible=True) == "THRESHOLD_MET_IN_CONDITIONAL_BENCHMARK")
check("just above 10pp -> THRESHOLD_MET", primary_label(Fraction(100001, 10000), admissible=True) == "THRESHOLD_MET_IN_CONDITIONAL_BENCHMARK")
check("just below 10pp -> POSITIVE_BUT_BELOW", primary_label(Fraction(99999, 10000), admissible=True) == "POSITIVE_BUT_BELOW_PREREGISTERED_THRESHOLD")
check("PRIMARY_UNMATCHED reachable", primary_label(Fraction(5), admissible=False) == "PRIMARY_UNMATCHED")
check("NA_EMPTY_DENOMINATOR reachable", primary_label(None, admissible=True, empty_denominator=True) == "NA_EMPTY_DENOMINATOR")
check("NOT_EVALUABLE reachable", primary_label(Fraction(5), admissible=True, evaluable=False) == "NOT_EVALUABLE")
check("TIE reachable", primary_label(Fraction(0), admissible=True) == "TIE")
check("PCD-reversal (PCD_BETTER_ON_PRIMARY_ESTIMAND) reachable", primary_label(Fraction(-3), admissible=True) == "PCD_BETTER_ON_PRIMARY_ESTIMAND")
check("all 8 PRIMARY_LABELS distinct", len(set(PRIMARY_LABELS)) == 8)
check("exact_percentage(n,0) is None not 0", exact_percentage(5, 0) is None)
check("primary_difference(denominator=0) is None not 0", primary_difference(3, 0, [1] * 60) is None)
try:
    phase_summary(list(range(61)))
    check("phase_summary rejects 61 values (E not silently merged into 60-grid)", False)
except ValueError:
    check("phase_summary rejects 61 values (E not silently merged into 60-grid)", True)
try:
    phase_summary(list(range(59)))
    check("phase_summary rejects 59 values (no silently dropped phase)", False)
except ValueError:
    check("phase_summary rejects 59 values (no silently dropped phase)", True)
q = linear_quantile([10, 20, 30, 40], Fraction(1, 4))
check("(n-1)*p quantile formula (17.5, not n*p's 20)", q == Fraction(35, 2), str(q))
for n in (1, 2, 3, 7):
    gr = group_robustness([(f"g{i}", i + 1, (i + 1) * 10) for i in range(n)])
    check(f"group_robustness works for {n} group(s), no hardcoded count", gr["group_count"] == n, str(gr))

# =========================== SUMMARY ========================================
print("\n=== SUMMARY ===")
n_ok = sum(1 for _, ok, _ in RESULTS if ok)
print(f"TOTAL: {n_ok}/{len(RESULTS)} passed")
for name, ok, _ in RESULTS:
    if not ok:
        print(f"FAILED/GAP: {name}")

shutil.rmtree(TMP, ignore_errors=True)
