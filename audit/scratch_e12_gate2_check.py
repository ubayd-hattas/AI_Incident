"""Gate 2 independent adversarial verification (Sam), NEW cases only.

Companion to audit/verify_e12_independent.py (19 hand-scored cases A-K +
snapshot-integrity/firewall/encoding sections). This script does NOT repeat
those cases. Same discipline: every expected value is a literal/comment
written BEFORE the call that produces it. No X13 semantic scoring, no real
PCD-vs-E policy comparison -- pure mechanical/adversarial evaluator testing
on synthetic fixtures. Investigation only: not committed, not edited into
existing files.
"""
from __future__ import annotations

import hashlib
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from ebe.evaluator import (  # noqa: E402
    EvaluatorError, Fragment, Proposition, RetainedBodyRecord, RetainedFeedRecord,
    RetainedSnapshot, SnapshotIntegrityError, compute_context_coverage, compute_core_coverage,
    compute_delay, context_covered, core_covered, fragment_satisfied, validate_snapshot,
)
from ebe.a11_loader import _canonical_body_bytes, _raw_body_bytes  # noqa: E402

FAILURES: list[str] = []
GAPS: list[str] = []


def _h(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def check(label: str, cond: bool, detail: str = "") -> None:
    status = "PASS" if cond else "FAIL"
    print(f"  {status} {label}" + (f" -- {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append(f"{label}: {detail}")


def gap(label: str, detail: str = "") -> None:
    print(f"  GAP {label}" + (f" -- {detail}" if detail else ""))
    GAPS.append(f"{label}: {detail}")


UTC = timezone.utc
T0 = datetime(2026, 5, 24, tzinfo=UTC)


def M(minutes: int) -> datetime:
    return T0 + timedelta(minutes=minutes)


print("=== CORE/CONTEXT ===")

# --- N1: core absent, context retained -> incomplete (context alone never counts). ---
_body_n1 = b"context only text present"
snap_n1 = RetainedSnapshot(M(10), (RetainedBodyRecord("dse~N1", M(1), _body_n1, _h(_body_n1)),), ())
frag_n1 = {
    "core": Fragment("core", "dse~N1", "body_span", required_substring=b"core text NEVER RETAINED"),
    "ctx": Fragment("ctx", "dse~N1", "body_span", required_substring=b"context only text present"),
}
prop_n1 = Proposition("N1", True, (("core",),), context_alternatives=(("core", "ctx"),), context_state="required")
res_n1 = compute_context_coverage([prop_n1], frag_n1, snap_n1, critical_only=False)
# Expected: numerator=0 (context-only retained material never counts as coverage without core).
check("N1: core absent + context retained => uncovered (numerator=0)", res_n1.numerator == 0, str(res_n1.numerator))

# --- N2: core retained, required context absent -> incomplete. ---
_body_n2 = b"core text present here"
snap_n2 = RetainedSnapshot(M(10), (RetainedBodyRecord("dse~N2", M(1), _body_n2, _h(_body_n2)),), ())
frag_n2 = {
    "core": Fragment("core", "dse~N2", "body_span", required_substring=b"core text present here"),
    "ctx": Fragment("ctx", "dse~N2", "body_span", required_substring=b"context text NEVER RETAINED"),
}
prop_n2 = Proposition("N2", True, (("core",),), context_alternatives=(("core", "ctx"),), context_state="required")
res_n2_core = compute_core_coverage([prop_n2], frag_n2, snap_n2, critical_only=False)
res_n2_ctx = compute_context_coverage([prop_n2], frag_n2, snap_n2, critical_only=False)
# Expected: core numerator=1 (core alone satisfied), context numerator=0 (required ctx missing).
check("N2: core covered (numerator=1)", res_n2_core.numerator == 1, str(res_n2_core.numerator))
check("N2: required context absent => context uncovered (numerator=0)", res_n2_ctx.numerator == 0, str(res_n2_ctx.numerator))

# --- N3: self-contained context == core coverage exactly, across BOTH a covered and an uncovered unit. ---
_body_n3a = b"self contained covered content"
snap_n3 = RetainedSnapshot(M(10), (RetainedBodyRecord("dse~N3A", M(1), _body_n3a, _h(_body_n3a)),), ())
frag_n3 = {
    "f-covered": Fragment("f-covered", "dse~N3A", "body_span", required_substring=b"self contained covered content"),
    "f-missing": Fragment("f-missing", "dse~N3B", "body_span", required_substring=b"NEVER RETAINED"),
}
prop_n3_cov = Proposition("N3-COV", True, (("f-covered",),), context_alternatives=(("f-covered",),))
prop_n3_unc = Proposition("N3-UNC", True, (("f-missing",),), context_alternatives=(("f-missing",),))
res_n3_core = compute_core_coverage([prop_n3_cov, prop_n3_unc], frag_n3, snap_n3, critical_only=False)
res_n3_ctx = compute_context_coverage([prop_n3_cov, prop_n3_unc], frag_n3, snap_n3, critical_only=False)
# Expected: core covered_ids == context covered_ids == ("N3-COV",); both numerator=1, denominator=2.
check("N3: self-contained context exactly mirrors core coverage set (covered+uncovered)",
      (res_n3_core.covered_ids, res_n3_core.numerator, res_n3_core.denominator) ==
      (res_n3_ctx.covered_ids, res_n3_ctx.numerator, res_n3_ctx.denominator),
      f"core={res_n3_core.covered_ids,res_n3_core.numerator,res_n3_core.denominator} ctx={res_n3_ctx.covered_ids,res_n3_ctx.numerator,res_n3_ctx.denominator}")

# --- N4: OR-of-3-context-alternatives modeled on PROP-20260616-61 (core AND (ctx1 OR ctx2 OR ctx3)). ---
_body_n4_core = b"core fragment content"
_body_n4_ctx2 = b"ctx alternative TWO content"
snap_n4 = RetainedSnapshot(M(10), (
    RetainedBodyRecord("dse~N4", M(1), _body_n4_core, _h(_body_n4_core)),
    RetainedBodyRecord("dse~N4", M(2), _body_n4_ctx2, _h(_body_n4_ctx2)),
), ())
frag_n4 = {
    "core": Fragment("core", "dse~N4", "body_span", required_substring=b"core fragment content"),
    "ctx1": Fragment("ctx1", "dse~N4", "body_span", required_substring=b"ctx alternative ONE NEVER RETAINED"),
    "ctx2": Fragment("ctx2", "dse~N4", "body_span", required_substring=b"ctx alternative TWO content"),
    "ctx3": Fragment("ctx3", "dse~N4", "body_span", required_substring=b"ctx alternative THREE NEVER RETAINED"),
}
prop_n4 = Proposition(
    "N4", True, (("core",),),
    context_alternatives=(("core", "ctx1"), ("core", "ctx2"), ("core", "ctx3")),
    context_state="required",
)
# Expected: only branch 2 (core+ctx2) is satisfiable (ctx1/ctx3 never retained) => context covered True via that ONE alternative.
ok_n4, _ = context_covered(prop_n4, frag_n4, snap_n4)
check("N4: any single satisfied context alternative (branch 2 of 3) suffices", ok_n4 is True, str(ok_n4))

# N4b: remove core from the snapshot entirely (only ctx2 body retained) -> whole proposition fails,
# because context_covered() gates on core_covered() AND every context alternative structurally
# embeds a complete core alternative (enforced by Proposition.__post_init__, evaluator.py:162-165).
snap_n4b = RetainedSnapshot(M(10), (RetainedBodyRecord("dse~N4", M(2), _body_n4_ctx2, _h(_body_n4_ctx2)),), ())
ok_n4b, _ = context_covered(prop_n4, frag_n4, snap_n4b)
ok_n4b_core, _ = core_covered(prop_n4, frag_n4, snap_n4b)
# Expected: core NOT covered (core fragment absent) => context also NOT covered, even though ctx2's own
# text is present, because ctx2's own alternative also includes "core" (missing) as a required fragment.
check("N4b: context alone (without core) never counts -- context_covered False", ok_n4b is False, str(ok_n4b))
check("N4b: core_covered is False (confirms context failure isn't an unrelated bug)", ok_n4b_core is False, str(ok_n4b_core))

# N4c: prove the invariant structurally -- constructing a "required" context alternative that does NOT
# contain a complete core alternative as a subset must be REJECTED at construction time (EvaluatorError),
# i.e. "context satisfied without core" is unreachable by design, not merely untested.
try:
    Proposition("N4-BAD", True, (("core",),), context_alternatives=(("ctx-only-no-core",),), context_state="required")
    _n4c_raised = False
except EvaluatorError:
    _n4c_raised = True
check("N4c: a 'required' context alternative lacking a complete core subset is REJECTED at construction (EvaluatorError)",
      _n4c_raised, "no exception -- invariant not enforced")

# --- N5: multi-fragment AND within one context alternative -- missing one fragment fails the whole alternative. ---
_body_n5_core = b"n5 core content"
_body_n5_a = b"n5 ctx fragment A"
snap_n5_partial = RetainedSnapshot(M(10), (
    RetainedBodyRecord("dse~N5", M(1), _body_n5_core, _h(_body_n5_core)),
    RetainedBodyRecord("dse~N5", M(2), _body_n5_a, _h(_body_n5_a)),
), ())
frag_n5 = {
    "core": Fragment("core", "dse~N5", "body_span", required_substring=b"n5 core content"),
    "ctx-a": Fragment("ctx-a", "dse~N5", "body_span", required_substring=b"n5 ctx fragment A"),
    "ctx-b": Fragment("ctx-b", "dse~N5", "body_span", required_substring=b"n5 ctx fragment B NEVER RETAINED"),
}
prop_n5 = Proposition("N5", True, (("core",),), context_alternatives=(("core", "ctx-a", "ctx-b"),), context_state="required")
ok_n5_partial, _ = context_covered(prop_n5, frag_n5, snap_n5_partial)
# Expected: ctx-b missing => the whole (single) AND-alternative fails => context uncovered.
check("N5: missing ONE fragment (ctx-b) within a multi-fragment AND alternative fails the whole alternative",
      ok_n5_partial is False, str(ok_n5_partial))
_body_n5_b = b"n5 ctx fragment B NEVER RETAINED"  # now actually retained
snap_n5_full = RetainedSnapshot(M(10), snap_n5_partial.bodies + (RetainedBodyRecord("dse~N5", M(3), _body_n5_b, _h(_body_n5_b)),), ())
ok_n5_full, _ = context_covered(prop_n5, frag_n5, snap_n5_full)
check("N5: with BOTH ctx-a and ctx-b retained, the alternative succeeds", ok_n5_full is True, str(ok_n5_full))

# --- N6/N7/N8 combined: unknown vs unavailable stay in denominator as NA; shared denominator across
# metrics; lower/upper numerator bounds. Four propositions, all core-eligible/core-covered: P1 context
# required+satisfied, P2 context required+unsatisfied, P3 context unknown, P4 context unavailable. ---
def _mk(page, text):
    b = text.encode()
    return RetainedBodyRecord(page, M(1), b, _h(b)), b

rec_c1, body_c1 = _mk("dse~P1", "p1 core")
rec_x1, body_x1 = _mk("dse~P1", "p1 ctx")
rec_c2, body_c2 = _mk("dse~P2", "p2 core")
rec_c3, body_c3 = _mk("dse~P3", "p3 core")
rec_c4, body_c4 = _mk("dse~P4", "p4 core")
snap_n678 = RetainedSnapshot(M(10), (rec_c1, rec_x1, rec_c2, rec_c3, rec_c4), ())
frag_n678 = {
    "c1": Fragment("c1", "dse~P1", "body_span", required_substring=body_c1),
    "x1": Fragment("x1", "dse~P1", "body_span", required_substring=body_x1),
    "c2": Fragment("c2", "dse~P2", "body_span", required_substring=body_c2),
    "x2": Fragment("x2", "dse~P2", "body_span", required_substring=b"NEVER RETAINED x2"),
    "c3": Fragment("c3", "dse~P3", "body_span", required_substring=body_c3),
    "c4": Fragment("c4", "dse~P4", "body_span", required_substring=body_c4),
}
props_n678 = [
    Proposition("P1", True, (("c1",),), context_alternatives=(("c1", "x1"),), context_state="required"),
    Proposition("P2", True, (("c2",),), context_alternatives=(("c2", "x2"),), context_state="required"),
    Proposition("P3", True, (("c3",),), context_state="unknown"),
    Proposition("P4", True, (("c4",),), context_state="unavailable"),
]
# Expected BEFORE running (per evaluator.py:251-262):
#  core: numerator=4 (all four core fragments retained), denominator=4
#  context: covered=("P1",) numerator=1; uncovered=("P2",); unknown=("P3","P4") both still in denominator;
#           denominator=4 (== core denominator, same "eligible" scoping, evaluator.py:260 n=len(eligible));
#           percentage=None (unknown non-empty, evaluator.py:260); status="NA_CONTEXT_INTERVAL" (evaluator.py:261)
#           lower_numerator=1 (==numerator), upper_numerator=1+2=3 (covered+unknown, evaluator.py:262)
res_core_678 = compute_core_coverage(props_n678, frag_n678, snap_n678, critical_only=False)
res_ctx_678 = compute_context_coverage(props_n678, frag_n678, snap_n678, critical_only=False)
check("N6/7/8 core numerator=4, denominator=4", (res_core_678.numerator, res_core_678.denominator) == (4, 4), str((res_core_678.numerator, res_core_678.denominator)))
check("N6/7/8 context numerator=1 (only P1)", res_ctx_678.numerator == 1, str(res_ctx_678.numerator))
check("N6/7/8 context uncovered=('P2',)", res_ctx_678.uncovered_ids == ("P2",), str(res_ctx_678.uncovered_ids))
check("N6: unknown+unavailable BOTH remain in denominator as NA (unknown_ids=('P3','P4'))", res_ctx_678.unknown_ids == ("P3", "P4"), str(res_ctx_678.unknown_ids))
check("N7: context denominator == core denominator (same scoped eligible population)", res_ctx_678.denominator == res_core_678.denominator == 4, str((res_ctx_678.denominator, res_core_678.denominator)))
check("N6: context percentage is None (NA), not a deflated point score", res_ctx_678.percentage is None, str(res_ctx_678.percentage))
check("N6: context status is NA_CONTEXT_INTERVAL", res_ctx_678.status == "NA_CONTEXT_INTERVAL", res_ctx_678.status)
check("N8: lower_numerator == numerator == 1", res_ctx_678.lower_numerator == 1, str(res_ctx_678.lower_numerator))
check("N8: upper_numerator == covered+unknown == 3", res_ctx_678.upper_numerator == 3, str(res_ctx_678.upper_numerator))

print("\n=== EVENTS ===")

# --- N9: exact event time match. ---
frag_evt = Fragment("evt", "dse~E1", "observable_feed", feed_action="live_change", event_time=M(5))
snap_evt_exact = RetainedSnapshot(M(10), (), (RetainedFeedRecord("dse~E1", "live_change", M(5), M(6)),))
ok_evt, _ = fragment_satisfied(frag_evt, snap_evt_exact)
check("N9: exact event_time match satisfies the fragment", ok_evt is True, str(ok_evt))

# --- N10: wrong-time same-title delete event is REJECTED, not close-enough. ---
frag_del = Fragment("del", "dse~E2", "observable_feed", feed_action="delete", event_time=M(5))
snap_del_wrong = RetainedSnapshot(M(10), (), (RetainedFeedRecord("dse~E2", "delete", M(6), M(7)),))  # 1 minute off
ok_del, _ = fragment_satisfied(frag_del, snap_del_wrong)
check("N10: a delete event at the WRONG time (1 minute off, same page/action) is rejected, not close-enough", ok_del is False, str(ok_del))

# --- N11: minimum_multiplicity requirement. ---
frag_mult = Fragment("mult", "dse~E3", "observable_feed", feed_action="live_change", event_time=M(5), minimum_multiplicity=2)
snap_mult_one = RetainedSnapshot(M(10), (), (RetainedFeedRecord("dse~E3", "live_change", M(5), M(6)),))
ok_mult_one, _ = fragment_satisfied(frag_mult, snap_mult_one)
check("N11: minimum_multiplicity=2 with only 1 matching delivered record => unsatisfied", ok_mult_one is False, str(ok_mult_one))
snap_mult_two = RetainedSnapshot(M(10), (), (
    RetainedFeedRecord("dse~E3", "live_change", M(5), M(6)),
    RetainedFeedRecord("dse~E3", "live_change", M(5), M(7)),
))
ok_mult_two, _ = fragment_satisfied(frag_mult, snap_mult_two)
check("N11: minimum_multiplicity=2 with 2 matching delivered records => satisfied", ok_mult_two is True, str(ok_mult_two))

# --- N12: event delivered AFTER the checkpoint must not count. Actual mechanism: validate_snapshot
# (evaluator.py:99-103) rejects the ENTIRE snapshot (raises SnapshotIntegrityError) for ANY feed record
# with delivered_time > checkpoint -- it is not merely excluded from that one fragment's match set.
frag_late = Fragment("late", "dse~E4", "observable_feed", feed_action="live_change", event_time=M(5))
snap_late = RetainedSnapshot(M(10), (), (RetainedFeedRecord("dse~E4", "live_change", M(5), M(11)),))  # delivered after checkpoint M(10)
try:
    validate_snapshot(snap_late)
    _n12_raised = False
except SnapshotIntegrityError:
    _n12_raised = True
check("N12: a feed record delivered AFTER the checkpoint invalidates the WHOLE snapshot (SnapshotIntegrityError), it does not merely fail to count", _n12_raised, "no exception raised")

# --- N13: an event whose event_time is AFTER its own delivered_time (impossible ordering) must not count.
# Same validate_snapshot check (evaluator.py:102, first disjunct) covers this, again at whole-snapshot scope.
frag_imp = Fragment("imp", "dse~E5", "observable_feed", feed_action="live_change", event_time=M(6))
snap_imp = RetainedSnapshot(M(10), (), (RetainedFeedRecord("dse~E5", "live_change", M(6), M(5)),))  # event_time > delivered_time
try:
    validate_snapshot(snap_imp)
    _n13_raised = False
except SnapshotIntegrityError:
    _n13_raised = True
check("N13: event_time AFTER delivered_time (impossible ordering) invalidates the whole snapshot", _n13_raised, "no exception raised")

# --- N14: private/internal event IDs cannot disambiguate otherwise-indistinguishable feed notifications.
# RetainedFeedRecord (evaluator.py:31-36) carries NO id field at all -- only page_key/action/event_time/
# delivered_time. fragment_satisfied's feed branch (evaluator.py:224) matches on page_key/action/event_time/
# multiplicity ONLY; Fragment.source_ref is never read for observable_feed matching. Two fragments with
# different (private) source_ref but the identical observable tuple are therefore BOTH satisfied by one
# single feed record.
frag_priv_a = Fragment("priv-a", "dse~E6", "observable_feed", feed_action="live_change", event_time=M(5), source_ref="PRIVATE-EVENT-ID-AAA")
frag_priv_b = Fragment("priv-b", "dse~E6", "observable_feed", feed_action="live_change", event_time=M(5), source_ref="PRIVATE-EVENT-ID-BBB")
snap_priv = RetainedSnapshot(M(10), (), (RetainedFeedRecord("dse~E6", "live_change", M(5), M(6)),))
ok_priv_a, _ = fragment_satisfied(frag_priv_a, snap_priv)
ok_priv_b, _ = fragment_satisfied(frag_priv_b, snap_priv)
check("N14: a single feed record satisfies BOTH fragments regardless of distinct private source_ref (confirms private IDs are not used, and are not available, to disambiguate)",
      ok_priv_a is True and ok_priv_b is True, str((ok_priv_a, ok_priv_b)))

print("\n=== SNAPSHOT INTEGRITY (validate_snapshot) ===")

# --- N15: duplicate request_seq is rejected (not covered by the existing 19 cases). ---
_b15a, _b15b = b"body one content", b"body two content"
rec15a = RetainedBodyRecord("dse~S1", M(1), _b15a, _h(_b15a), request_seq=7)
rec15b = RetainedBodyRecord("dse~S2", M(2), _b15b, _h(_b15b), request_seq=7)  # duplicate seq
snap15 = RetainedSnapshot(M(10), (rec15a, rec15b), ())
try:
    validate_snapshot(snap15)
    _n15_raised = False
except SnapshotIntegrityError:
    _n15_raised = True
check("N15: duplicate request_seq across two distinct bodies is rejected", _n15_raised, "no exception raised")

# --- N16: incorrect accounting totals (declared retained_body_bytes disagrees with actual sum). ---
_b16 = b"sixteen byte body!!"  # len==20
rec16 = RetainedBodyRecord("dse~S3", M(1), _b16, _h(_b16))
snap16_bad = RetainedSnapshot(M(10), (rec16,), (), retained_body_bytes=len(_b16) + 1)  # deliberately wrong
try:
    validate_snapshot(snap16_bad)
    _n16_raised = False
except SnapshotIntegrityError:
    _n16_raised = True
check("N16: a declared retained_body_bytes that disagrees with the actual computed total is rejected", _n16_raised, "no exception raised")

# --- N17: cap overflow IS enforced when declared_total_bytes is supplied and exceeds capacity_bytes. ---
_b17 = b"x" * 50
rec17 = RetainedBodyRecord("dse~S4", M(1), _b17, _h(_b17))
snap17_over = RetainedSnapshot(M(10), (rec17,), (), capacity_bytes=10, declared_total_bytes=50)
try:
    validate_snapshot(snap17_over)
    _n17_raised = False
except SnapshotIntegrityError:
    _n17_raised = True
check("N17: declared_total_bytes(50) > capacity_bytes(10) is rejected when declared_total_bytes IS supplied", _n17_raised, "no exception raised")

# --- N17b: GAP -- if declared_total_bytes is omitted (None), actual computed bytes exceeding capacity_bytes
# is NEVER checked (evaluator.py:111 requires BOTH capacity_bytes and declared_total_bytes to be non-None).
snap17_gap = RetainedSnapshot(M(10), (rec17,), (), capacity_bytes=10, declared_total_bytes=None)  # actual body=50 bytes > cap=10
try:
    validate_snapshot(snap17_gap)
    _n17b_raised = False
except SnapshotIntegrityError:
    _n17b_raised = True
if _n17b_raised:
    check("N17b GAP-check: expected the gap to reproduce (no exception) -- gap may have been fixed", False, "exception WAS raised; re-examine evaluator.py:108-112")
else:
    gap("Cap-overflow enforcement is contingent on declared_total_bytes being supplied",
        "evaluator.py:111 -- 'if snapshot.capacity_bytes is not None and snapshot.declared_total_bytes is not None and ...' "
        "A snapshot with capacity_bytes=10 and an actual 50-byte retained body, but declared_total_bytes=None, "
        "passes validate_snapshot with NO integrity issue. The 'computed' total (evaluator.py:108) is only ever "
        "compared against declared_total_bytes (a sync check), never directly against capacity_bytes.")

# --- N18: missing/wrong object reference in from_collector_result -- does it fail closed or crash raw? ---
fake_body_obj = SimpleNamespace(object_id="OBJ-REAL", body=b"real body bytes")
fake_packet = SimpleNamespace(page_key="dse~S5", capture_time=M(1), object_id="OBJ-DOES-NOT-EXIST",
                               body_sha256=_h(b"real body bytes"), request_seq=1, packet_bytes=None, archive_key=None)
fake_export = SimpleNamespace(checkpoint=M(10), body_objects=[fake_body_obj], packets=[fake_packet],
                               capacity_bytes=None, retained_packet_bytes=None, retained_body_bytes=None, total_bytes=None)
fake_result = SimpleNamespace(retained_export=fake_export, feed_polls=[])
try:
    RetainedSnapshot.from_collector_result(fake_result)
    _n18_status = "no exception"
except KeyError as exc:
    _n18_status = f"raw KeyError({exc})"
except SnapshotIntegrityError:
    _n18_status = "clean SnapshotIntegrityError"
except Exception as exc:  # noqa: BLE001
    _n18_status = f"other: {type(exc).__name__}: {exc}"
if _n18_status == "clean SnapshotIntegrityError":
    check("N18: a packet referencing a missing object_id fails closed with SnapshotIntegrityError", True)
else:
    check("N18 BUG: a packet referencing a missing/wrong object_id does NOT fail closed with a clean evaluator error", False, _n18_status)

# --- N19/N20: bad refcount / hidden unreferenced body -- explicitly not modeled. ---
gap("bad refcount enforcement", "RetainedBodyRecord/RetainedSnapshot (evaluator.py:21-48) carry no refcount field anywhere; nothing to validate.")
gap("hidden unreferenced body enforcement", "RetainedSnapshot.bodies (evaluator.py:42) IS the retained set by construction (from_collector_result only emits records for export.packets, evaluator.py:55-57); the data model has no way to represent a body object that exists in storage but is unreferenced by any packet, so there is nothing for validate_snapshot to check.")

print("\n=== ENCODING ===")

# --- N21: ascii/utf8/latin1 all reconstruct raw bytes via sha256(body.encode('latin-1')) then decode per codec. ---
for label, source_text, codec in (
    ("ascii", "plain ascii text", "ascii"),
    ("utf8", "café naïve → arrow", "utf8"),   # multi-byte UTF-8 source
    ("latin1", "café straße", "latin1"),           # Latin-1-representable source (<=0xFF codepoints)
):
    source_bytes = source_text.encode({"ascii": "ascii", "utf8": "utf-8", "latin1": "latin-1"}[codec])
    projected_json_string = source_bytes.decode("latin-1")  # simulate E05's storage
    raw = _raw_body_bytes(projected_json_string)
    canonical = _canonical_body_bytes(projected_json_string, codec)
    # Expected: raw == original source bytes; canonical == UTF-8 re-encoding of the original text.
    check(f"N21 [{label}]: _raw_body_bytes reconstructs exact source bytes", raw == source_bytes, f"{raw!r} != {source_bytes!r}")
    check(f"N21 [{label}]: _canonical_body_bytes yields canonical UTF-8 of the true source text", canonical == source_text.encode("utf-8"), f"{canonical!r} != {source_text.encode('utf-8')!r}")

# --- N22: a required span located AFTER a non-ASCII multi-byte char -- canonical offsets vs raw-byte offsets.
# Source text (what a human/editor perceives): "café DELTA required-span-here"
#   "é" (e-acute) = 1 Unicode codepoint but 2 UTF-8 bytes (0xC3 0xA9) when body_encoding="utf8".
# canonical char offset of "required-span-here": count codepoints in "café DELTA " = 11
# raw byte offset of "required-span-here": count UTF-8 BYTES in "café DELTA " = 12 (extra byte from é)
_n22_text = "café DELTA required-span-here"
_n22_source_bytes = _n22_text.encode("utf-8")
_n22_projected = _n22_source_bytes.decode("latin-1")
_n22_raw = _raw_body_bytes(_n22_projected)
assert _n22_raw == _n22_source_bytes
_n22_canonical_offset = _n22_text.index("required-span-here")  # 11 (codepoints)
_n22_raw_offset = _n22_source_bytes.index(b"required-span-here")  # 12 (bytes)
check("N22 setup: canonical (codepoint) offset (11) and raw-byte offset (12) genuinely differ after the multi-byte char", _n22_canonical_offset != _n22_raw_offset, f"{_n22_canonical_offset} vs {_n22_raw_offset}")

# Replicating the CORE occurrence path exactly (a11_loader.py:280-291): span is sliced out of `raw`
# (byte buffer) then decoded -- i.e. char_span MUST be authored as raw-byte offsets, despite the field's
# name suggesting character offsets.
_span_as_raw = (_n22_raw_offset, _n22_raw_offset + len(b"required-span-here"))
_quote_using_raw_offset = _n22_raw[_span_as_raw[0]:_span_as_raw[1]].decode("utf-8", errors="strict")
check("N22a: RAW-byte char_span (as the loader expects, a11_loader.py:280-291) extracts the correct quote", _quote_using_raw_offset == "required-span-here", repr(_quote_using_raw_offset))

# If instead an annotator authored char_span using CANONICAL (codepoint) offsets -- the natural reading
# of the field name "char_span" -- reproduce what the loader's own logic does with that (wrong) input:
_span_as_canonical = (_n22_canonical_offset, _n22_canonical_offset + len(b"required-span-here"))
try:
    _quote_using_canonical_offset = _n22_raw[_span_as_canonical[0]:_span_as_canonical[1]].decode("utf-8", errors="strict")
    _n22b_status = ("decoded", _quote_using_canonical_offset)
except UnicodeDecodeError as exc:
    _n22b_status = ("decode_error", str(exc))
if _n22b_status[0] == "decode_error":
    check("N22b: a canonical-offset char_span (off-by-one-byte after the multi-byte char) fails CLOSED (UnicodeDecodeError -> OCCURRENCE_COORDINATE_MAPPING, a11_loader.py:289-291), not a silent wrong match", True)
else:
    _wrong_quote = _n22b_status[1]
    check("N22b: a canonical-offset char_span produces a DIFFERENT, WRONG quote rather than raising (still likely caught by the quote-equality check at a11_loader.py:292-295, but NOT via a decode error)",
          _wrong_quote != "required-span-here", f"quote={_wrong_quote!r}")
    gap("char_span silently shifts by one byte without a decode-level error",
        f"a11_loader.py:280-291 has no independent canonical-vs-raw cross-check for the CORE occurrence path (unlike the "
        f"context-occurrence path at a11_loader.py:320-339, which stores and cross-validates BOTH source_projection_span "
        f"and canonical_char_span, lines 326-335). The core path relies solely on downstream quote-equality "
        f"(a11_loader.py:292-295) to fail closed if char_span was mis-authored as a codepoint offset instead of a byte "
        f"offset; got wrong quote {_wrong_quote!r} instead of a decode-level signal.")

# --- N23: an empty KNOWN body is distinct from an unknown/BU (absent) state -- both fail a nonempty
# requirement identically at the coverage boolean, but the empty-body record is independently present,
# hash-validated, and byte-accounted by validate_snapshot, whereas an absent page contributes nothing.
_empty_body = b""
snap_n23_empty = RetainedSnapshot(M(10), (RetainedBodyRecord("dse~N23", M(1), _empty_body, _h(_empty_body)),), ())
snap_n23_absent = RetainedSnapshot(M(10), (), ())  # page never captured at all
frag_n23 = Fragment("f", "dse~N23", "body_span", required_substring=b"anything nonempty")
ok_empty, _ = fragment_satisfied(frag_n23, snap_n23_empty)
ok_absent, _ = fragment_satisfied(frag_n23, snap_n23_absent)
check("N23: an empty-but-known body fails a nonempty requirement (same boolean outcome as absence, as expected)", ok_empty is False, str(ok_empty))
check("N23: a wholly-absent page also fails (same boolean outcome)", ok_absent is False, str(ok_absent))
# But they are NOT conflated at the validation/accounting layer: validate_snapshot accepts the empty
# body as a real retained object (hash of b"" is well-defined) and accounts 0 bytes for it, distinctly
# from it simply not existing in `bodies` at all.
try:
    validate_snapshot(snap_n23_empty)
    _n23_empty_valid = True
except SnapshotIntegrityError:
    _n23_empty_valid = False
check("N23: validate_snapshot accepts the empty-but-known body as a legitimately retained (zero-byte) record, distinct from non-existence", _n23_empty_valid, "empty known body was rejected by validate_snapshot")
check("N23: the empty body is present in snapshot.bodies (len=1) vs the absent snapshot (len=0) -- not conflated in the data model", len(snap_n23_empty.bodies) == 1 and len(snap_n23_absent.bodies) == 0, str((len(snap_n23_empty.bodies), len(snap_n23_absent.bodies))))

print("\n=== DELAY ===")

# --- N24: AND-within-alternative uses the LATEST (max) completion time among required fragments. ---
_b24a, _b24b = b"n24 fragment alpha", b"n24 fragment beta"
snap_n24 = RetainedSnapshot(M(10), (
    RetainedBodyRecord("dse~N24", M(2), _b24a, _h(_b24a)),
    RetainedBodyRecord("dse~N24", M(7), _b24b, _h(_b24b)),
), ())
frag_n24 = {
    "a": Fragment("a", "dse~N24", "body_span", required_substring=b"n24 fragment alpha"),
    "b": Fragment("b", "dse~N24", "body_span", required_substring=b"n24 fragment beta"),
}
prop_n24 = Proposition("N24", True, (("a", "b"),), earliest_eligible_support=M(0))
res_n24 = compute_delay(prop_n24, frag_n24, snap_n24)
# Expected: completion time = max(M(2), M(7)) = M(7); delay = (M(7)-M(0)).total_seconds() = 420.0
expected_n24 = (M(7) - M(0)).total_seconds()
check("N24: AND-within-alternative delay uses the LATEST fragment time (420.0s), not the earliest (120.0s)", res_n24.delay_seconds == expected_n24, f"got {res_n24.delay_seconds} expected {expected_n24}")

# --- N25: unretained/never-covered proposition is censored (status='unretained', delay_seconds is None), not zero delay. ---
frag_n25 = {"f": Fragment("f", "dse~N25", "body_span", required_substring=b"NEVER RETAINED AT ALL")}
snap_n25 = RetainedSnapshot(M(10), (), ())
prop_n25 = Proposition("N25", True, (("f",),), earliest_eligible_support=M(0))
res_n25 = compute_delay(prop_n25, frag_n25, snap_n25)
check("N25: unretained proposition has status 'unretained'", res_n25.status == "unretained", res_n25.status)
check("N25: unretained proposition has delay_seconds=None, NOT 0.0 (censored, not zero)", res_n25.delay_seconds is None, str(res_n25.delay_seconds))

# --- N26: unknown earliest-support baseline is NA (status='na_unknown_support', delay_seconds None), not zero. ---
_b26 = b"n26 content retained"
snap_n26 = RetainedSnapshot(M(10), (RetainedBodyRecord("dse~N26", M(1), _b26, _h(_b26)),), ())
frag_n26 = {"f": Fragment("f", "dse~N26", "body_span", required_substring=b"n26 content retained")}
prop_n26 = Proposition("N26", True, (("f",),), earliest_eligible_support=None)  # unknown baseline
res_n26 = compute_delay(prop_n26, frag_n26, snap_n26)
check("N26: unknown earliest_eligible_support => status 'na_unknown_support'", res_n26.status == "na_unknown_support", res_n26.status)
check("N26: unknown baseline => delay_seconds is None, NOT 0.0", res_n26.delay_seconds is None, str(res_n26.delay_seconds))

# --- N27: negative delay (completion BEFORE its own earliest eligible support) is an integrity error,
# not silently clamped to zero. ---
_b27 = b"n27 content retained early"
snap_n27 = RetainedSnapshot(M(10), (RetainedBodyRecord("dse~N27", M(2), _b27, _h(_b27)),), ())
frag_n27 = {"f": Fragment("f", "dse~N27", "body_span", required_substring=b"n27 content retained early")}
prop_n27 = Proposition("N27", True, (("f",),), earliest_eligible_support=M(9))  # support declared AFTER the retained completion time M(2)
try:
    compute_delay(prop_n27, frag_n27, snap_n27)
    _n27_raised = False
except SnapshotIntegrityError:
    _n27_raised = True
check("N27: negative delay raises SnapshotIntegrityError (evaluator.py:293), not clamped to 0.0", _n27_raised, "no exception raised -- check whether delay was silently clamped")

print("\n=== LOADER SEMANTIC-INVENTION CHECK ===")
print("""
  a11_loader.py: does it invent/infer semantic judgments? Answer: NO, based on
  reading the whole file. Every disposition-affecting decision reads a specific
  annotation field and applies a FIXED mechanical rule; ambiguity/malformed
  input fails closed (defaults False + flags a ValidationIssue) rather than
  guessing a "best" interpretation:
    - eligible / eligibility_reason: read directly from eligibility.jsonl's
      'eligible'/'reason' fields (a11_loader.py:396-404); malformed => eligible
      forced False + MISSING_ELIGIBILITY_DISPOSITION/REASON issue (fail-closed
      default, not a judgment about the evidence itself).
    - critical: read directly from evidence.jsonl's 'critical' field
      (a11_loader.py:409-412); malformed => False + MALFORMED_CRITICAL_FLAG.
    - context_state: a direct 4-way dispatch on context_eligibility.jsonl's
      declared fields ('context_state' in unknown/unavailable; else
      anchor_self_contained+context_needed==False => self_contained; else
      context_needed==True => required) -- a11_loader.py:415-451. No case
      picks a state the annotation didn't already assert; the final else
      defaults to 'unknown' + MISSING_CONTEXT_DISPOSITION (fail-closed).
    - context_alternatives for 'required': a fixed Cartesian-product/DNF
      expansion of (every core alternative) x (every declared extra-context
      branch) -- a11_loader.py:442-445, matching docs/E12_EVALUATOR.md's own
      description of the rule (lines 65-68). This enumerates ALL combinations
      rather than choosing "the" alternative -- it is a deterministic
      compilation formula, not a selection between candidates.
    - span-to-declared-quote resolution (a11_loader.py:292-295): decoded
      occurrence text is matched against the evidence's declared span quotes
      by EXACT string equality; if this yields zero or more than one match,
      it is rejected (OCCURRENCE_NOT_ALLOWED_SUPPORT) rather than guessing
      which declared span was intended. This is disambiguation via exact
      match with fail-closed-on-ambiguity, not an invented judgment call.
  Conclusion: no line found where the loader decides "context is/isn't
  needed" or "this is the intended alternative" from anything other than an
  explicit annotation field or a fixed combinatorial rule; all fallback paths
  for missing/malformed data are conservative (False/unknown) defaults with a
  recorded ValidationIssue, not silent semantic invention.
""")

print("\n" + "=" * 60)
print(f"NEW CASES FAILURES: {len(FAILURES)}")
for f in FAILURES:
    print("  -", f)
print(f"NEW CASES GENUINE GAPS FOUND: {len(GAPS)}")
for g in GAPS:
    print("  -", g)
