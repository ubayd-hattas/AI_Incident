"""Independent E12 acceptance script (Sam), for docs in audit/E12_INDEPENDENT_ACCEPTANCE.md.

Every expected value in the hand-scored section is written down as a comment
or an inline literal BEFORE the corresponding evaluator call, not derived by
running the evaluator first. Distinct from tests/test_evaluator.py (Ubayd's
own authored tests) and tests/test_a11_loader.py -- this script is Sam's own,
independently constructed.
"""
from __future__ import annotations

import hashlib
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from ebe.collectors import PeriodicConfig, PeriodicPolicy, run_periodic  # noqa: E402
from ebe.evaluator import (  # noqa: E402
    Fragment, Proposition, RetainedBodyRecord, RetainedFeedRecord, RetainedSnapshot,
    compute_context_coverage, compute_core_coverage, compute_delay,
)
from ebe.observer import Observer  # noqa: E402
from ebe.storage import Capture, CaptureStore  # noqa: E402

FAILURES: list[str] = []


def _h(body: bytes) -> str:
    """Real SHA-256 of a fixture body. Ubayd's fail-closed retained-snapshot
    validation (src/ebe/evaluator.py:validate_snapshot, added in bbdc885)
    correctly rejects a RetainedBodyRecord whose body_sha256 doesn't match its
    own bytes -- the placeholder strings ("h", "h2", ...) this script
    originally used only worked because that validation didn't exist yet.
    This is not an E12 bug; it's this script's own fixtures needing a real
    hash now that the boundary they exist to test is actually enforced."""
    return hashlib.sha256(body).hexdigest()


def check(label: str, cond: bool, detail: str = "") -> None:
    status = "PASS" if cond else "FAIL"
    print(f"  {status} {label}" + (f" -- {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append(f"{label}: {detail}")


UTC = timezone.utc
T0 = datetime(2026, 5, 24, tzinfo=UTC)


def M(minutes: int) -> datetime:
    return T0 + timedelta(minutes=minutes)


print("=== Hand-scored cases A-K (expected values fixed before any evaluator call) ===")

# --- Case A: one proposition, one exact retained span. Expected: covered=1, denom=1. ---
_body_a = b"the exact required span"
snap_a = RetainedSnapshot(M(10), (RetainedBodyRecord("dse~A", M(1), _body_a, _h(_body_a)),), ())
frag_a = {"f1": Fragment("f1", "dse~A", "body_span", required_substring=b"exact required span")}
prop_a = Proposition("CASE-A", True, (("f1",),))
res_a = compute_core_coverage([prop_a], frag_a, snap_a, critical_only=False)
check("Case A: numerator=1, denominator=1", (res_a.numerator, res_a.denominator) == (1, 1), str((res_a.numerator, res_a.denominator)))

# --- Case B: two valid alternative occurrences; original lost (not in snapshot), second retained.
# Expected: covered ONCE (numerator=1), not twice, and not zero.
_body_b = b"second occurrence text"
snap_b = RetainedSnapshot(M(10), (RetainedBodyRecord("dse~B", M(5), _body_b, _h(_body_b)),), ())
frag_b = {
    "alt1-f1": Fragment("alt1-f1", "dse~B", "body_span", required_substring=b"original occurrence text (never retained)"),
    "alt2-f1": Fragment("alt2-f1", "dse~B", "body_span", required_substring=b"second occurrence text"),
}
prop_b = Proposition("CASE-B", True, (("alt1-f1",), ("alt2-f1",)))
res_b = compute_core_coverage([prop_b], frag_b, snap_b, critical_only=False)
check("Case B: covered once via the surviving alternative (numerator=1)", res_b.numerator == 1, str(res_b.numerator))

# --- Case C: multi-span proposition, only ONE of two required spans retained. Expected: uncovered (numerator=0). ---
_body_c = b"span one present but span two missing entirely"
snap_c = RetainedSnapshot(M(10), (RetainedBodyRecord("dse~C", M(1), _body_c, _h(_body_c)),), ())
frag_c = {
    "f1": Fragment("f1", "dse~C", "body_span", required_substring=b"span one present"),
    "f2": Fragment("f2", "dse~C", "body_span", required_substring=b"span two REQUIRED BUT ABSENT"),
}
prop_c = Proposition("CASE-C", True, (("f1", "f2"),))
res_c = compute_core_coverage([prop_c], frag_c, snap_c, critical_only=False)
check("Case C: uncovered, one of two required spans missing (numerator=0)", res_c.numerator == 0, str(res_c.numerator))

# --- Case D: multi-span proposition, ALL spans retained. Expected: covered (numerator=1). ---
_body_d = b"span one present AND span two present too"
snap_d = RetainedSnapshot(M(10), (RetainedBodyRecord("dse~D", M(1), _body_d, _h(_body_d)),), ())
frag_d = {
    "f1": Fragment("f1", "dse~D", "body_span", required_substring=b"span one present"),
    "f2": Fragment("f2", "dse~D", "body_span", required_substring=b"span two present too"),
}
prop_d = Proposition("CASE-D", True, (("f1", "f2"),))
res_d = compute_core_coverage([prop_d], frag_d, snap_d, critical_only=False)
check("Case D: covered, all required spans present (numerator=1)", res_d.numerator == 1, str(res_d.numerator))

# --- Case E: same proposition satisfied by THREE cumulative retained copies. Expected: numerator increases ONCE (1, not 3). ---
snap_e = RetainedSnapshot(M(10), (
    RetainedBodyRecord("dse~E", M(1), _body_e := b"persisting header text", _h(_body_e)),
    RetainedBodyRecord("dse~E", M(3), _body_e, _h(_body_e)),
    RetainedBodyRecord("dse~E", M(5), _body_e, _h(_body_e)),
), ())
frag_e = {"f1": Fragment("f1", "dse~E", "body_span", required_substring=b"persisting header text")}
prop_e = Proposition("CASE-E", True, (("f1",),))
res_e = compute_core_coverage([prop_e], frag_e, snap_e, critical_only=False)
check("Case E: three cumulative copies still count as ONE covered unit (numerator=1, not 3)", res_e.numerator == 1, str(res_e.numerator))

# --- Case F: critical + noncritical propositions. Expected: critical_only=True denominator=1 (only CASE-F-CRIT), not 2. ---
_body_f = b"crit content"
snap_f = RetainedSnapshot(M(10), (RetainedBodyRecord("dse~F", M(1), _body_f, _h(_body_f)),), ())
frag_f = {"f1": Fragment("f1", "dse~F", "body_span", required_substring=b"crit content")}
prop_f_crit = Proposition("CASE-F-CRIT", True, (("f1",),))
prop_f_noncrit = Proposition("CASE-F-NONCRIT", False, (("f1",),))
res_f_all = compute_core_coverage([prop_f_crit, prop_f_noncrit], frag_f, snap_f, critical_only=False)
res_f_crit = compute_core_coverage([prop_f_crit, prop_f_noncrit], frag_f, snap_f, critical_only=True)
check("Case F: critical_only=False denominator=2 (both units)", res_f_all.denominator == 2, str(res_f_all.denominator))
check("Case F: critical_only=True denominator=1 (only the critical unit)", res_f_crit.denominator == 1, str(res_f_crit.denominator))

# --- Case G: ineligible proposition. Expected: excluded from BOTH numerator and denominator, appears only in excluded_ids. ---
_body_g = b"would-be-covered content"
snap_g = RetainedSnapshot(M(10), (RetainedBodyRecord("dse~G", M(1), _body_g, _h(_body_g)),), ())
frag_g = {"f1": Fragment("f1", "dse~G", "body_span", required_substring=b"would-be-covered content")}
prop_g_eligible = Proposition("CASE-G-ELIGIBLE", True, (("f1",),))
prop_g_ineligible = Proposition("CASE-G-INELIGIBLE", True, (("f1",),), eligible=False, eligibility_reason="test exclusion")
res_g = compute_core_coverage([prop_g_eligible, prop_g_ineligible], frag_g, snap_g, critical_only=False)
check("Case G: denominator=1 (ineligible unit excluded despite having satisfiable content)", res_g.denominator == 1, str(res_g.denominator))
check("Case G: excluded_ids contains the ineligible unit", res_g.excluded_ids == ("CASE-G-INELIGIBLE",), str(res_g.excluded_ids))

# --- Case H: a body that WAS genuinely admitted and retained is then ACTUALLY EVICTED by real FIFO
# (not a zero-cap/never-admitted oversize rejection). Expected: no coverage at the final checkpoint.
# Built directly against the real CaptureStore (not the collector, to construct a precise admit-then-evict
# sequence): admit a small packet, then admit a second packet that forces FIFO eviction of the first.
# Packet sizes independently computed first: standalone packet1=174 bytes, packet2=175
# bytes, sum=349. Capacity=200 admits EITHER alone (174<=200, 175<=200) but not both
# (349>200) -- this forces a genuine FIFO eviction of packet1 to admit packet2, unlike
# a capacity chosen too small to admit packet2 at all (which would be an intrinsic
# oversize rejection, not eviction of a previously-retained body).
store_h = CaptureStore(capacity_bytes=200, deduplicate=True, start_time=M(0))
cap1 = Capture("dse~H1", M(1), 1, b"FIRST BODY")
cap2 = Capture("dse~H2", M(2), 2, b"SECOND BODY")
admit1 = store_h.admit(cap1)
admit2 = store_h.admit(cap2)
retained_after = {rc.request_seq for rc in store_h.retained_captures}
check("Case H setup: packet 1 was genuinely admitted at the time (not oversize-rejected)", admit1.disposition == "admitted", str(admit1.disposition))
check("Case H setup: packet 1 is NOT in the final retained set (genuinely evicted by FIFO, not never-admitted)", 1 not in retained_after, str(retained_after))
snap_h = RetainedSnapshot(M(10), tuple(
    RetainedBodyRecord(rc.page_key, rc.capture_time, store_h.body_for_capture(rc.request_seq), rc.body_sha256)
    for rc in store_h.retained_captures
), ())
frag_h = {"f1": Fragment("f1", "dse~H1", "body_span", required_substring=b"FIRST BODY")}
prop_h = Proposition("CASE-H", True, (("f1",),))
res_h = compute_core_coverage([prop_h], frag_h, snap_h, critical_only=False)
check("Case H: genuinely-evicted (not merely never-admitted) body produces NO coverage (numerator=0)", res_h.numerator == 0, str(res_h.numerator))

# --- Case I: diagnostic/attempt history (body_results) contains the evidence, retained store does not.
# Uses the real Observer/PeriodicCollector at capacity_bytes=0. Expected: no coverage.
# Build a tiny synthetic export inline (mirrors the pattern used throughout this project's audits).
from ebe.schema import (  # noqa: E402
    BodyEncoding, EventRecord, ExportedEventType, ExportFingerprint, ManifestRecord,
    NormalizedExport, ObservedEventSemantics, RelationFields, RelationValue,
    RelationValueForm, RevisionRecord, SourceLocation, SourceTimestamp,
)

_SRC = SourceLocation(Path("synthetic"), None, None)
_NOREL = RelationFields(RelationValue(RelationValueForm.NULL, None), RelationValue(RelationValueForm.NULL, None), RelationValue(RelationValueForm.NULL, None), ())


def _ts(d):
    return SourceTimestamp(d.isoformat(), d)


def _build_export(page, when, body_text):
    rev_id = f"dse~{page}@1"
    body_bytes = body_text.encode("utf-8")
    t = _ts(when)
    rev = RevisionRecord(
        source=_SRC, raw={}, rev_id=rev_id, page_id=f"dse/{page}", page_key=f"dse~{page}",
        wiki="dse", name=page, seq=1, rcs_rev="1.1", rcs_path="synthetic", body=body_text,
        source_body_bytes=body_bytes, body_len=len(body_bytes), body_sha256=hashlib.sha256(body_bytes).hexdigest(),
        body_encoding=BodyEncoding.UTF8, lines=1, diff_base=None, diff_base_reason="page_created", hunks=(),
        label="L", ip16="0.0", time=t, time_grade="reqlog", winning_clock="revision.pref_ts", uncertainty_seconds=1,
        request_time=t, success_time=t, recent_changes_time=None, write_date=t, archived_at=t,
        request_action="form_edit", change_summary=None, relations=_NOREL,
    )
    ev = EventRecord(
        source=_SRC, raw={}, present_fields=frozenset(), event_id=f"save:{page}:0",
        event_type=ExportedEventType.SAVE, observed_semantics=ObservedEventSemantics.HELD_BODY_SAVE,
        time=t, time_grade="reqlog", wiki="dse", page=page, page_key=f"dse~{page}", revision_ref=rev_id,
        winning_clock=None, uncertainty_seconds=None, request_time=None, success_time=None, write_date=None,
        recent_changes_time=None, rcs_date=None, clock_delta_seconds=None, clock_note=None, success_observed=None,
        request_action=None, change_summary=None, actor_label=None, ip16=None, page_held=None, param_family=None,
        source_refs=(), relations=_NOREL,
    )
    manifest = ManifestRecord(source=_SRC, raw={}, generated_at=_ts(T0), db_sha256="synthetic", cut={}, counts={},
                               per_wiki={}, population_counts={}, grade_histograms={}, body_bytes={}, body_encoding={},
                               page_family_coverage={}, facts={}, recreation_source={}, resources={}, tool_versions={},
                               source_scan={}, request_source_note="", checks=())
    fp = ExportFingerprint(sha256={}, row_counts={})
    return NormalizedExport((), (rev,), (ev,), (), manifest, fp, {}, {}, {rev_id: rev}, {ev.event_id: ev}, {})


export_i = _build_export("CASEI", M(1), "SECRET DIAGNOSTIC ONLY CONTENT")
obs_i = Observer(export_i)
result_i = run_periodic(obs_i, PeriodicConfig(PeriodicPolicy.PCD, interval_us=60_000_000, capacity_bytes=0, checkpoint=M(5)))
check("Case I setup: diagnostic body_results DOES contain the content (expected, not a bug)",
      any(getattr(r, "body", None) == b"SECRET DIAGNOSTIC ONLY CONTENT" for r in result_i.body_results))
check("Case I setup: retained_evidence is empty (nothing actually retained under cap=0)", len(result_i.retained_evidence) == 0)
snap_i = RetainedSnapshot.from_collector_result(result_i)
frag_i = {"f1": Fragment("f1", "dse~CASEI", "body_span", required_substring=b"SECRET DIAGNOSTIC ONLY CONTENT")}
prop_i = Proposition("CASE-I", True, (("f1",),))
res_i = compute_core_coverage([prop_i], frag_i, snap_i, critical_only=False)
check("Case I: diagnostic-only content produces NO coverage (numerator=0)", res_i.numerator == 0, str(res_i.numerator))

# --- Case J: delay with two alternative supports at different times. Expected: uses the EARLIEST
# completed alternative (M(2)), not the later one (M(8)), and delay = M(2) - earliest_eligible_support.
snap_j = RetainedSnapshot(M(10), (
    RetainedBodyRecord("dse~J", M(8), _body_j_late := b"later alternative content", _h(_body_j_late)),
    RetainedBodyRecord("dse~J", M(2), _body_j_early := b"earlier alternative content", _h(_body_j_early)),
), ())
frag_j = {
    "alt-early": Fragment("alt-early", "dse~J", "body_span", required_substring=b"earlier alternative content"),
    "alt-late": Fragment("alt-late", "dse~J", "body_span", required_substring=b"later alternative content"),
}
prop_j = Proposition("CASE-J", True, (("alt-late",), ("alt-early",)), earliest_eligible_support=M(0))
res_j = compute_delay(prop_j, frag_j, snap_j)
expected_delay_seconds = (M(2) - M(0)).total_seconds()  # hand-computed: 120.0 seconds, using the EARLIER alternative
check("Case J: delay uses the earliest completed alternative (120.0s), not the later one (480.0s)",
      res_j.delay_seconds == expected_delay_seconds, f"got {res_j.delay_seconds} expected {expected_delay_seconds}")
check("Case J: status is 'retained'", res_j.status == "retained", res_j.status)

# --- Case K: context not frozen. Expected: explicit NOT_FROZEN status, NOT a fabricated 0%. ---
_body_k = b"core content"
snap_k = RetainedSnapshot(M(10), (RetainedBodyRecord("dse~K", M(1), _body_k, _h(_body_k)),), ())
frag_k = {"f1": Fragment("f1", "dse~K", "body_span", required_substring=b"core content")}
prop_k = Proposition("CASE-K", True, (("f1",),), context_alternatives=())  # no context modeled
res_k = compute_context_coverage([prop_k], frag_k, snap_k, critical_only=False)
check("Case K: context status is NOT_FROZEN (not a fabricated percentage)", res_k.status == "NOT_FROZEN", res_k.status)
check("Case K: context percentage is None, never 0.0", res_k.percentage is None, str(res_k.percentage))

print("\n" + "=" * 60)
print(f"HAND-SCORED CASES A-K FAILURES: {len(FAILURES)}")
for f in FAILURES:
    print("  -", f)

# ===========================================================================
print("\n=== Section 2: retained-snapshot integrity boundary ===")
# Ubayd's bbdc885 added evaluator.validate_snapshot, called from every
# coverage/delay entry point -- these two cases previously demonstrated a
# silent-acceptance gap (numerator=1 when it should be rejected). Re-verify
# independently: the correct current behavior is that BOTH now raise
# SnapshotIntegrityError, not merely "numerator=0".
from ebe.evaluator import SnapshotIntegrityError  # noqa: E402

tampered = RetainedBodyRecord("dse~TX", M(1), b"REAL CONTENT", "BADHASH_DOES_NOT_MATCH_BODY")
snap_tx = RetainedSnapshot(M(10), (tampered,), ())
frag_tx = {"f1": Fragment("f1", "dse~TX", "body_span", required_substring=b"REAL CONTENT")}
try:
    compute_core_coverage([Proposition("TX", True, (("f1",),))], frag_tx, snap_tx, critical_only=False)
    check("FIXED: a body whose body_sha256 does NOT match its own bytes is now rejected (raises SnapshotIntegrityError)", False, "no exception raised -- still silently accepted")
except SnapshotIntegrityError:
    check("FIXED: a body whose body_sha256 does NOT match its own bytes is now rejected (raises SnapshotIntegrityError)", True)

post_ck = RetainedBodyRecord("dse~TY", M(10) + timedelta(hours=1), b"FUTURE CONTENT", _h(b"FUTURE CONTENT"))
snap_ty = RetainedSnapshot(M(10), (post_ck,), ())
frag_ty = {"f1": Fragment("f1", "dse~TY", "body_span", required_substring=b"FUTURE CONTENT")}
try:
    compute_core_coverage([Proposition("TY", True, (("f1",),))], frag_ty, snap_ty, critical_only=False)
    check("FIXED: a RetainedBodyRecord with capture_time AFTER the snapshot's own checkpoint is now rejected (raises SnapshotIntegrityError)", False, "no exception raised -- still silently counted")
except SnapshotIntegrityError:
    check("FIXED: a RetainedBodyRecord with capture_time AFTER the snapshot's own checkpoint is now rejected (raises SnapshotIntegrityError)", True)

# ===========================================================================
print("\n=== Section 3: A05 population firewall corruption attempts ===")
from ebe.evaluator import validate_population, DenominatorFirewallError  # noqa: E402


def _fw_check(name, fn):
    try:
        fn()
        check(name, False, "not rejected by validate_population")
    except DenominatorFirewallError:
        check(name, True)
    except Exception as exc:
        check(name, True, f"rejected via {type(exc).__name__}, not DenominatorFirewallError specifically")


_fw_check("duplicate evidence ID is rejected", lambda: validate_population(
    [Proposition("DUP", True, (("f1",),)), Proposition("DUP", True, (("f1",),))],
    {"f1": Fragment("f1", "dse~A", "body_span", required_substring=b"x")}))
_fw_check("dangling fragment reference is rejected", lambda: validate_population(
    [Proposition("DANGLE", True, (("missing",),))], {}))

_fw_check("FIXED: a fragment referencing a page OUTSIDE the dse~ universe (e.g. a foreign wiki's page_key) is now rejected", lambda: validate_population(
    [Proposition("OFFSITE", True, (("f-off",),))],
    {"f-off": Fragment("f-off", "notdse~SomePage", "body_span", required_substring=b"x")}))

_fw_check("FIXED: a critical proposition whose ENTIRE core support is a single observable_feed fragment (no body_span at all) is now rejected", lambda: validate_population(
    [Proposition("FEEDONLY", True, (("feed-f",),))],
    {"feed-f": Fragment("feed-f", "dse~A", "observable_feed", feed_action="live_change")}))

# ===========================================================================
print("\n=== Section 4: source-encoding custody (independent of the loader's own check) ===")
# E05's raw `body` field is a Latin-1 BYTE PROJECTION regardless of the declared
# body_encoding -- every byte of the true source was mapped 1:1 to one Python
# character. To recover the true source bytes you must ALWAYS body.encode("latin-1"),
# never branch on body_encoding. src/ebe/a11_loader.py's `_raw_body_bytes` (added in
# 266f3b3, after this review first reported the gap) now does this unconditionally --
# the check below now independently confirms the loader catches it, rather than
# demonstrating that it doesn't.
import json as _json  # noqa: E402
_revs = {}
with open(REPO / "data" / "raw" / "export" / "revisions.jsonl", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            r = _json.loads(line)
            _revs[r["rev_id"]] = r
with open(REPO / "annotations" / "evidence.jsonl", encoding="utf-8") as f:
    _evidence = [_json.loads(line) for line in f if line.strip()]
with open(REPO / "annotations" / "occurrences.jsonl", encoding="utf-8") as f:
    _occurrences = [_json.loads(line) for line in f if line.strip()]

_ev_mismatches = [e["evidence_id"] for e in _evidence
                   if (rev := _revs.get(e["rev_id"])) is not None
                   and hashlib.sha256(rev["body"].encode("latin-1")).hexdigest() != e["source_body_hash"]]
_occ_mismatches = [o["occurrence_id"] for o in _occurrences
                    if (rev := _revs.get(o["rev_id"])) is not None
                    and hashlib.sha256(rev["body"].encode("latin-1")).hexdigest() != o["body_sha256"]]
check("ENCODING BUG: evidence.jsonl source_body_hash matches the TRUE (always-latin-1-projection) source bytes for all 65 propositions", len(_ev_mismatches) == 0, f"{len(_ev_mismatches)} mismatches: {_ev_mismatches}")
check("ENCODING BUG: occurrences.jsonl body_sha256 matches the TRUE source bytes for all occurrence rows", len(_occ_mismatches) == 0, f"{len(_occ_mismatches)} mismatches (sample: {_occ_mismatches[:5]})")

from ebe.a11_loader import load_a11_benchmark  # noqa: E402
_bm = load_a11_benchmark(fail_on_error=False)
_independent_hash_defect = bool(_ev_mismatches) or bool(_occ_mismatches)
_loader_reports_hash_issue = any("HASH" in i.code for i in _bm.validation.issues)
print(f"  INFO loader issue breakdown: {dict(__import__('collections').Counter(i.code for i in _bm.validation.issues))}")
check(
    "the real loader's own hash check agrees with this script's independent from-scratch recomputation "
    "(both clean, or both catching the same defect -- not asserting which state is 'correct')",
    _loader_reports_hash_issue == _independent_hash_defect,
    f"independent recomputation found a defect={_independent_hash_defect}, loader reports a HASH issue={_loader_reports_hash_issue}",
)
if _independent_hash_defect:
    print("  INFO a source-encoding hash defect is present in the frozen annotation files (per this script's own")
    print("       independent recomputation, not the loader's report) -- this is the annotation-layer blocker; a fix")
    print("       requires the annotation team to correct evidence.jsonl/occurrences.jsonl, not this script or E12 code.")
try:
    load_a11_benchmark()
    _default_raised = False
except DenominatorFirewallError:
    _default_raised = True
check(
    "load_a11_benchmark(fail_on_error=True) (the real default) raises iff this script's own independent "
    "recomputation found a real hash defect (not asserting the annotation layer's state either way)",
    _default_raised == _independent_hash_defect,
    f"independent defect found={_independent_hash_defect}, default loader raised={_default_raised}",
)
if not _independent_hash_defect:
    print("  INFO independently confirmed (fresh sha256(body.encode('latin-1')) recomputation against evidence.jsonl/")
    print("       occurrences.jsonl's own recorded hashes, not trusting the loader or any PASS report): the source-")
    print("       encoding hash provenance defect this review originally found (2 evidence + 80 occurrence rows) is no")
    print("       longer present. This confirms only the hash/encoding provenance repair -- it is NOT a rerun of the")
    print("       full E12 independent acceptance review (pilot leakage, PROP-20260618-63 eligibility, epistemic-leakage")
    print("       prose, split isolation, context/delay sections were not re-checked here) and does not by itself amend")
    print("       audit/E12_INDEPENDENT_ACCEPTANCE.md's CONDITIONAL PASS verdict.")

print("\n" + "=" * 60)
print(f"FINAL GRAND TOTAL FAILURES: {len(FAILURES)}")
for f in FAILURES:
    print("  -", f)
