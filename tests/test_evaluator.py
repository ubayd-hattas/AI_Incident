"""Hand-scored synthetic acceptance suite for the E12 substrate (src/ebe/evaluator.py).

Every expected value below is computed by hand in the test itself, not generated
by the evaluator -- per X13_RUN_CONTRACT.md SS9's "E12 independent hand-scored
synthetic acceptance" gate. No real annotation file is read or scored here.
"""
from __future__ import annotations

import hashlib
import sys
import unittest
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ebe.collectors import PeriodicConfig, PeriodicPolicy, run_periodic  # noqa: E402
from ebe.evaluator import (  # noqa: E402
    DenominatorFirewallError,
    Fragment,
    Proposition,
    RetainedBodyRecord,
    RetainedFeedRecord,
    RetainedSnapshot,
    compute_context_coverage,
    compute_core_coverage,
    compute_delay,
    core_covered,
    validate_population,
)
from ebe.observer import Observer  # noqa: E402
from ebe.schema import (  # noqa: E402
    BodyEncoding, EventRecord, ExportedEventType, ExportFingerprint,
    ManifestRecord, NormalizedExport, ObservedEventSemantics, RelationFields,
    RelationValue, RelationValueForm, RevisionRecord, SourceLocation, SourceTimestamp,
)
from ebe.timeline import HORIZON_START  # noqa: E402

UTC = timezone.utc
SRC = SourceLocation(Path("synthetic"), None, None)
_NO_RELATION = RelationFields(
    RelationValue(RelationValueForm.NULL, None),
    RelationValue(RelationValueForm.NULL, None),
    RelationValue(RelationValueForm.NULL, None),
    (),
)


def M(minutes: int) -> datetime:
    return HORIZON_START + timedelta(minutes=minutes)


def _ts(d: datetime) -> SourceTimestamp:
    return SourceTimestamp(d.isoformat(), d)


@dataclass
class Mut:
    kind: str  # "save" | "delete"
    page: str
    time: datetime
    body: str = ""
    seq: int = 1


def build_export(mutations: list[Mut]) -> NormalizedExport:
    """Minimal self-contained synthetic export builder (no pinned raw export
    dependency) -- adapted from audit/verify_collectors_cross_policy.py."""

    revisions: list[RevisionRecord] = []
    events: list[EventRecord] = []
    for i, m in enumerate(mutations):
        event_id = f"{m.kind}:{m.page}:{i}"
        t = _ts(m.time)
        if m.kind == "save":
            rev_id = f"dse~{m.page}@{m.seq}"
            body_bytes = m.body.encode("utf-8")
            revisions.append(RevisionRecord(
                source=SRC, raw={}, rev_id=rev_id, page_id=f"dse/{m.page}", page_key=f"dse~{m.page}",
                wiki="dse", name=m.page, seq=m.seq, rcs_rev="1.1", rcs_path="synthetic", body=m.body,
                source_body_bytes=body_bytes, body_len=len(body_bytes),
                body_sha256=hashlib.sha256(body_bytes).hexdigest(), body_encoding=BodyEncoding.UTF8,
                lines=1, diff_base=None, diff_base_reason="page_created" if m.seq == 1 else None, hunks=(),
                label="L", ip16="0.0", time=t, time_grade="reqlog", winning_clock="revision.pref_ts",
                uncertainty_seconds=1, request_time=t, success_time=t, recent_changes_time=None,
                write_date=t, archived_at=t, request_action="form_edit", change_summary=None,
                relations=_NO_RELATION,
            ))
            events.append(EventRecord(
                source=SRC, raw={}, present_fields=frozenset(), event_id=event_id,
                event_type=ExportedEventType.SAVE, observed_semantics=ObservedEventSemantics.HELD_BODY_SAVE,
                time=t, time_grade="reqlog", wiki="dse", page=m.page, page_key=f"dse~{m.page}",
                revision_ref=rev_id, winning_clock=None, uncertainty_seconds=None, request_time=None,
                success_time=None, write_date=None, recent_changes_time=None, rcs_date=None,
                clock_delta_seconds=None, clock_note=None, success_observed=None, request_action=None,
                change_summary=None, actor_label=None, ip16=None, page_held=None, param_family=None,
                source_refs=(), relations=_NO_RELATION,
            ))
        elif m.kind == "delete":
            events.append(EventRecord(
                source=SRC, raw={}, present_fields=frozenset(), event_id=event_id,
                event_type=ExportedEventType.DELETE, observed_semantics=ObservedEventSemantics.SUCCESSFUL_DELETION,
                time=t, time_grade="reqlog", wiki="dse", page=m.page, page_key=f"dse~{m.page}",
                revision_ref=None, winning_clock="rclog.unix_ts", uncertainty_seconds=1, request_time=t,
                success_time=t, write_date=None, recent_changes_time=None, rcs_date=None,
                clock_delta_seconds=0, clock_note=None, success_observed=True, request_action="delete",
                change_summary="deleted.", actor_label="[Admin1]", ip16="0.0", page_held=True,
                param_family=None, source_refs=(), relations=_NO_RELATION,
            ))
        else:
            raise ValueError(m.kind)
    manifest = ManifestRecord(
        source=SRC, raw={}, generated_at=_ts(HORIZON_START), db_sha256="synthetic",
        cut={}, counts={}, per_wiki={}, population_counts={}, grade_histograms={}, body_bytes={},
        body_encoding={}, page_family_coverage={}, facts={}, recreation_source={}, resources={},
        tool_versions={}, source_scan={}, request_source_note="", checks=(),
    )
    fingerprint = ExportFingerprint(sha256={}, row_counts={})
    return NormalizedExport(
        (), tuple(revisions), tuple(events), (), manifest, fingerprint,
        {}, {}, {r.rev_id: r for r in revisions}, {e.event_id: e for e in events}, {},
    )


class FragmentSatisfactionTests(unittest.TestCase):
    def test_body_span_fragment_satisfied_by_matching_retained_body(self) -> None:
        snapshot = RetainedSnapshot(
            checkpoint=M(10),
            bodies=(RetainedBodyRecord("dse~A", M(1), b"hello world", "x"),),
            feed_context=(),
        )
        fragment = Fragment("f1", "dse~A", "body_span", required_substring=b"hello")
        satisfied, when = core_covered(
            Proposition("P1", True, ((("f1",)),)), {"f1": fragment}, snapshot,
        )
        self.assertTrue(satisfied)
        self.assertEqual(when, M(1))

    def test_observable_feed_fragment_satisfied_without_any_body(self) -> None:
        snapshot = RetainedSnapshot(
            checkpoint=M(10),
            bodies=(),
            feed_context=(RetainedFeedRecord("dse~A", "delete", M(2), M(3)),),
        )
        fragment = Fragment("f1", "dse~A", "observable_feed", feed_action="delete")
        prop = Proposition("P1", True, (("f1",),))
        satisfied, when = core_covered(prop, {"f1": fragment}, snapshot)
        self.assertTrue(satisfied)
        self.assertEqual(when, M(3))  # delivered_time, not event_time


class HandScoredAcceptanceTests(unittest.TestCase):
    """Each case's expected coverage/delay value is computed by hand in the
    test body, never by calling the evaluator and trusting its own output."""

    def test_duplicate_support_two_retained_copies_count_once_using_earliest(self) -> None:
        # Two retained copies of the same page both contain the required text.
        # By hand: covered=True, acquisition_time = the EARLIER of the two capture times.
        snapshot = RetainedSnapshot(
            checkpoint=M(10),
            bodies=(
                RetainedBodyRecord("dse~A", M(5), b"the answer is 42", "h1"),
                RetainedBodyRecord("dse~A", M(2), b"the answer is 42", "h1"),
            ),
            feed_context=(),
        )
        fragments = {"f1": Fragment("f1", "dse~A", "body_span", required_substring=b"answer is 42")}
        prop = Proposition("P1", True, (("f1",),))
        result = compute_core_coverage([prop], fragments, snapshot, critical_only=False)
        self.assertEqual(result.numerator, 1)
        self.assertEqual(result.denominator, 1)
        satisfied, when = core_covered(prop, fragments, snapshot)
        self.assertTrue(satisfied)
        self.assertEqual(when, M(2))  # hand-computed: min(M(5), M(2)) == M(2)

    def test_cumulative_body_later_revision_satisfies_earlier_scoped_claim(self) -> None:
        # Only a LATER cumulative revision is retained; by hand it still satisfies
        # the claim (the fragment's substring is present in that later body).
        snapshot = RetainedSnapshot(
            checkpoint=M(20),
            bodies=(RetainedBodyRecord("dse~B", M(15), b"prefix text ... the original claim ... suffix", "h2"),),
            feed_context=(),
        )
        fragments = {"f1": Fragment("f1", "dse~B", "body_span", required_substring=b"the original claim")}
        prop = Proposition("P1", True, (("f1",),))
        result = compute_core_coverage([prop], fragments, snapshot, critical_only=False)
        self.assertEqual((result.numerator, result.denominator), (1, 1))

    def test_context_only_requirement_independent_of_core(self) -> None:
        # Core is satisfied by a body fragment; context requires an observed
        # delete that is NOT present. By hand: core covered, context NOT covered.
        snapshot = RetainedSnapshot(
            checkpoint=M(10),
            bodies=(RetainedBodyRecord("dse~C", M(1), b"the core claim text", "h3"),),
            feed_context=(),  # no delete observed
        )
        fragments = {
            "core1": Fragment("core1", "dse~C", "body_span", required_substring=b"core claim"),
            "ctx1": Fragment("ctx1", "dse~C", "observable_feed", feed_action="delete"),
        }
        prop = Proposition("P1", True, (("core1",),), context_alternatives=(("ctx1",),))
        core_result = compute_core_coverage([prop], fragments, snapshot, critical_only=False)
        ctx_result = compute_context_coverage([prop], fragments, snapshot, critical_only=False)
        self.assertEqual(core_result.numerator, 1)  # by hand: core satisfied
        self.assertEqual(ctx_result.numerator, 0)  # by hand: context NOT satisfied (no delete observed)
        # Now add the observed delete -- by hand, context should flip to covered.
        snapshot2 = RetainedSnapshot(
            checkpoint=M(10),
            bodies=snapshot.bodies,
            feed_context=(RetainedFeedRecord("dse~C", "delete", M(5), M(6)),),
        )
        ctx_result2 = compute_context_coverage([prop], fragments, snapshot2, critical_only=False)
        self.assertEqual(ctx_result2.numerator, 1)

    def test_encoding_alignment_non_ascii_substring_matches_at_byte_level(self) -> None:
        # By hand: "café" appears in the retained canonical UTF-8 body; the
        # fragment's required_substring is also UTF-8-encoded, so byte-level
        # containment must succeed regardless of the original source encoding
        # (the real annotation schema's source-projection-vs-canonical-offset
        # mapping is NOT modeled here -- this only checks byte-level matching
        # is encoding-consistent, which is the minimal thing this substrate
        # can promise).
        body = "the café serves the workaround answer".encode("utf-8")
        snapshot = RetainedSnapshot(checkpoint=M(5), bodies=(RetainedBodyRecord("dse~D", M(1), body, "h4"),), feed_context=())
        fragments = {"f1": Fragment("f1", "dse~D", "body_span", required_substring="café".encode("utf-8"))}
        prop = Proposition("P1", True, (("f1",),))
        result = compute_core_coverage([prop], fragments, snapshot, critical_only=False)
        self.assertEqual(result.numerator, 1)

    def test_eviction_poisoning_real_collector_evicted_body_never_counts_as_retained(self) -> None:
        # By hand: with capacity_bytes=0, NOTHING can ever be retained. A
        # fragment requiring the saved page's content must be UNCOVERED, even
        # though the real Observer/PeriodicCollector genuinely dispatched a GET
        # and saw the body (diagnostically, in body_results) -- proving the
        # firewall holds against REAL collector output, not just a hand-built
        # synthetic snapshot.
        export = build_export([Mut("save", "POISON", M(1), "SECRET_ANSWER_42", 1)])
        obs = Observer(export)
        result = run_periodic(obs, PeriodicConfig(
            PeriodicPolicy.PCD, interval_us=60_000_000, capacity_bytes=0, checkpoint=M(5),
        ))
        # Sanity: the diagnostic surface DOES see the body (this is expected,
        # documented behavior of body_results -- not itself a bug).
        self.assertTrue(any(
            getattr(r, "body", None) == b"SECRET_ANSWER_42" for r in result.body_results
        ))
        self.assertEqual(len(result.retained_evidence), 0)  # nothing retained under cap=0

        snapshot = RetainedSnapshot.from_collector_result(result)
        self.assertEqual(snapshot.bodies, ())  # firewall: no bodies reach the evaluator at all
        fragments = {"f1": Fragment("f1", "dse~POISON", "body_span", required_substring=b"SECRET_ANSWER_42")}
        prop = Proposition("P1", True, (("f1",),))
        result_cov = compute_core_coverage([prop], fragments, snapshot, critical_only=False)
        self.assertEqual(result_cov.numerator, 0)  # by hand: must NOT be inflated by the evicted/never-admitted body

    def test_na_unresolved_eligibility_excluded_from_numerator_and_denominator(self) -> None:
        snapshot = RetainedSnapshot(
            checkpoint=M(5),
            bodies=(RetainedBodyRecord("dse~F", M(1), b"the satisfied claim", "h6"),),
            feed_context=(),
        )
        fragments = {"f1": Fragment("f1", "dse~F", "body_span", required_substring=b"satisfied claim")}
        eligible_prop = Proposition("P1", True, (("f1",),))
        ineligible_prop = Proposition(
            "P2", True, (("f1",),), eligible=False, eligibility_reason="unresolved core semantics",
        )
        result = compute_core_coverage([eligible_prop, ineligible_prop], fragments, snapshot, critical_only=False)
        # By hand: P2 must not appear in numerator OR denominator, only in excluded_ids.
        self.assertEqual(result.denominator, 1)
        self.assertEqual(result.excluded_ids, ("P2",))
        self.assertNotIn("P2", result.covered_ids)
        self.assertNotIn("P2", result.uncovered_ids)

    def test_empty_denominator_reports_na_not_zero(self) -> None:
        snapshot = RetainedSnapshot(checkpoint=M(5), bodies=(), feed_context=())
        result = compute_core_coverage([], {}, snapshot, critical_only=False)
        self.assertEqual(result.denominator, 0)
        self.assertIsNone(result.percentage)  # NA, never a fabricated 0.0
        self.assertEqual(result.status, "NA_EMPTY_DENOMINATOR")

    def test_population_firewall_rejects_duplicate_evidence_id(self) -> None:
        # Both propositions have a valid, non-empty, resolvable core alternative,
        # so the ONLY thing that can trip the firewall here is the duplicate ID
        # itself -- isolating this rule from the separate empty-alternative rule.
        fragment = Fragment("f1", "dse~A", "body_span", required_substring=b"x")
        p1 = Proposition("P1", True, (("f1",),))
        p1_dup = Proposition("P1", False, (("f1",),))
        with self.assertRaises(DenominatorFirewallError):
            validate_population([p1, p1_dup], {"f1": fragment})

    def test_population_firewall_rejects_dangling_fragment_reference(self) -> None:
        prop = Proposition("P1", True, (("nonexistent_fragment",),))
        with self.assertRaises(DenominatorFirewallError):
            validate_population([prop], {})

    def test_delay_retained_unretained_and_na_are_distinct_statuses(self) -> None:
        snapshot = RetainedSnapshot(
            checkpoint=M(10),
            bodies=(RetainedBodyRecord("dse~E", M(6), b"the retained claim", "h5"),),
            feed_context=(),
        )
        fragments = {"f1": Fragment("f1", "dse~E", "body_span", required_substring=b"retained claim")}
        retained_prop = Proposition("P1", True, (("f1",),), earliest_eligible_support=M(1))
        unretained_prop = Proposition(
            "P2", True, (("f1",),), earliest_eligible_support=M(1),
        )
        na_prop = Proposition("P3", True, (("f1",),), earliest_eligible_support=None)

        retained_result = compute_delay(retained_prop, fragments, snapshot)
        self.assertEqual(retained_result.status, "retained")
        self.assertEqual(retained_result.delay_seconds, (M(6) - M(1)).total_seconds())  # hand: 5 minutes = 300s

        empty_snapshot = RetainedSnapshot(checkpoint=M(10), bodies=(), feed_context=())
        unretained_result = compute_delay(unretained_prop, fragments, empty_snapshot)
        self.assertEqual(unretained_result.status, "unretained")
        self.assertIsNone(unretained_result.delay_seconds)

        na_result = compute_delay(na_prop, fragments, snapshot)
        self.assertEqual(na_result.status, "na_unknown_support")
        self.assertIsNone(na_result.delay_seconds)


if __name__ == "__main__":
    unittest.main()
