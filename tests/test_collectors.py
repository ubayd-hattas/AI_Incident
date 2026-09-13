from __future__ import annotations

import ast
import hashlib
import sys
import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ebe import load_export  # noqa: E402
from ebe.collectors import (  # noqa: E402
    EventDerivedCollector,
    EventDerivedConfig,
    PeriodicConfig,
    PeriodicPolicy,
    periodic_sweep_times,
    run_event_derived,
    run_periodic,
)
from ebe.observer import BodyOutcome, Observer, ObserverConfig  # noqa: E402
from ebe.timeline import HORIZON_START  # noqa: E402


PINNED = ROOT / "data" / "raw" / "export"
UTC = timezone.utc
MINUTE_US = 60_000_000


def dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


class PeriodicCollectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        export = load_export(PINNED)
        cls.save_template = next(
            event for event in export.events
            if event.event_type.value == "save" and not event.relations.edges
        )
        cls.delete_template = next(
            event for event in export.events
            if event.event_type.value == "delete" and not event.relations.edges
        )
        cls.bu_template = next(event for event in export.events if event.event_type.value == "revert")
        cls.revision_template = export.revisions_by_id[cls.save_template.revision_ref]

    def revision(self, page: str, suffix: str, when: datetime, body: bytes):
        key = f"dse~{page}"
        return replace(
            self.revision_template,
            rev_id=f"{key}@{suffix}", page_key=key, page_id=f"id-{page}", name=page,
            seq=int(suffix) if suffix.isdigit() else 1,
            body=body.decode("latin-1"), source_body_bytes=body, body_len=len(body),
            body_sha256=hashlib.sha256(body).hexdigest(),
            time=replace(self.revision_template.time, raw=when.isoformat(), utc=when),
            uncertainty_seconds=1,
        )

    def save(self, revision, *, relations=None):
        return replace(
            self.save_template,
            event_id=f"save:{revision.rev_id}", page_key=revision.page_key, page=revision.name,
            revision_ref=revision.rev_id, time=revision.time,
            relations=relations or self.save_template.relations,
        )

    def delete(self, page: str, suffix: str, when: datetime):
        return replace(
            self.delete_template,
            event_id=f"delete:{page}:{suffix}", page_key=f"dse~{page}", page=page,
            time=replace(self.delete_template.time, raw=when.isoformat(), utc=when),
            uncertainty_seconds=1,
        )

    def body_unknown(self, page: str, when: datetime):
        return replace(
            self.bu_template,
            event_id=f"bu:{page}", page_key=f"dse~{page}", page=page,
            time=replace(self.bu_template.time, raw=when.isoformat(), utc=when),
            uncertainty_seconds=1,
        )

    def observer(self, events, revisions, *, delay_us=0):
        export = SimpleNamespace(
            events=tuple(events), revisions=tuple(revisions),
            revisions_by_id={revision.rev_id: revision for revision in revisions},
        )
        return Observer(export, config=ObserverConfig(get_response_delay_us=delay_us))

    def collect(
        self, policy, events, revisions, *, interval_minutes=2, phase_us=0,
        capacity=None, checkpoint="2026-05-24T00:07:00Z", delay_us=0,
    ):
        return run_periodic(
            self.observer(events, revisions, delay_us=delay_us),
            PeriodicConfig(
                policy, interval_minutes * MINUTE_US, phase_us, capacity, dt(checkpoint)
            ),
        )

    def collect_e(
        self, events, revisions, *, q=30, capacity=None,
        checkpoint="2026-05-24T00:07:00Z", delay_us=0,
    ):
        return run_event_derived(
            self.observer(events, revisions, delay_us=delay_us),
            EventDerivedConfig(q, capacity, dt(checkpoint)),
        )

    def test_global_periodic_schedule_is_t0_relative_and_end_exclusive(self) -> None:
        times = tuple(periodic_sweep_times(
            15 * MINUTE_US, checkpoint=dt("2026-05-24T00:46:00Z")
        ))
        self.assertEqual(times, tuple(dt(f"2026-05-24T00:{m:02d}:00Z") for m in (0, 15, 30, 45)))

    def test_discovery_does_not_reset_schedule(self) -> None:
        revision = self.revision("A", "1", dt("2026-05-24T00:07:00Z"), b"A")
        result = self.collect(
            PeriodicPolicy.PD, [self.save(revision)], [revision], interval_minutes=15,
            checkpoint="2026-05-24T00:16:00Z",
        )
        self.assertEqual([x.request_time for x in result.body_results], [dt("2026-05-24T00:15:00Z")])

    def test_phase_offset_uses_integer_microseconds(self) -> None:
        times = tuple(periodic_sweep_times(
            5 * MINUTE_US, 75_000_000, checkpoint=dt("2026-05-24T00:12:00Z")
        ))
        self.assertEqual(times, (
            dt("2026-05-24T00:01:15Z"), dt("2026-05-24T00:06:15Z"),
            dt("2026-05-24T00:11:15Z"),
        ))

    def test_future_title_is_not_requested_early(self) -> None:
        revision = self.revision("Future", "1", dt("2026-05-24T00:02:10Z"), b"F")
        result = self.collect(PeriodicPolicy.P, [self.save(revision)], [revision])
        self.assertEqual([x.request_time for x in result.body_results], [
            dt("2026-05-24T00:04:00Z"), dt("2026-05-24T00:06:00Z")
        ])

    def test_p_and_pd_have_identical_gets_outcomes_and_capture_packets(self) -> None:
        revision = self.revision("A", "1", dt("2026-05-24T00:00:10Z"), b"same")
        args = ([self.save(revision)], [revision])
        p = self.collect(PeriodicPolicy.P, *args)
        pd = self.collect(PeriodicPolicy.PD, *args)
        self.assertEqual(p.body_request_schedule, pd.body_request_schedule)
        self.assertEqual(p.body_results, pd.body_results)
        self.assertEqual(
            [x.capture for x in p.capture_attempts],
            [x.capture for x in pd.capture_attempts],
        )
        self.assertEqual(
            [x.packet_bytes for x in p.retained_captures],
            [x.packet_bytes for x in pd.retained_captures],
        )
        self.assertGreater(p.storage_snapshot.retained_body_bytes, pd.storage_snapshot.retained_body_bytes)
        self.assertLessEqual(pd.storage_snapshot.final_store_bytes, p.storage_snapshot.final_store_bytes)

    def test_pcd_does_not_refetch_unchanged_title(self) -> None:
        revision = self.revision("A", "1", dt("2026-05-24T00:00:10Z"), b"A")
        result = self.collect(PeriodicPolicy.PCD, [self.save(revision)], [revision])
        self.assertEqual([x.request_time for x in result.body_results], [dt("2026-05-24T00:02:00Z")])

    def test_pcd_change_becomes_eligible_and_mutations_coalesce(self) -> None:
        first = self.revision("A", "1", dt("2026-05-24T00:00:10Z"), b"one")
        second = self.revision("A", "2", dt("2026-05-24T00:02:10Z"), b"two")
        third = self.revision("A", "3", dt("2026-05-24T00:02:20Z"), b"three")
        result = self.collect(
            PeriodicPolicy.PCD,
            [self.save(first), self.save(second), self.save(third)],
            [first, second, third],
        )
        self.assertEqual([x.request_time for x in result.body_results], [
            dt("2026-05-24T00:02:00Z"), dt("2026-05-24T00:04:00Z")
        ])
        self.assertEqual([x.capture.body for x in result.capture_attempts], [b"one", b"three"])

    def test_pcd_dirty_status_comes_only_from_feed_not_body_equality(self) -> None:
        first = self.revision("A", "1", dt("2026-05-24T00:00:10Z"), b"same")
        second = self.revision("A", "2", dt("2026-05-24T00:02:10Z"), b"same")
        result = self.collect(
            PeriodicPolicy.PCD, [self.save(first), self.save(second)], [first, second]
        )
        self.assertEqual(len(result.body_results), 2)
        self.assertEqual(result.storage_snapshot.retained_body_objects, 1)
        self.assertEqual(result.storage_snapshot.retained_packets, 2)

    def test_all_periodic_policies_use_identical_feed_access(self) -> None:
        revision = self.revision("A", "1", dt("2026-05-24T00:00:10Z"), b"A")
        results = [
            self.collect(policy, [self.save(revision)], [revision])
            for policy in PeriodicPolicy
        ]
        feed_payloads = [tuple(p.response_bytes for p in result.feed_polls) for result in results]
        self.assertEqual(feed_payloads[0], feed_payloads[1])
        self.assertEqual(feed_payloads[1], feed_payloads[2])
        self.assertEqual({r.observer_costs.feed_requests for r in results}, {8})
        self.assertEqual(len({r.observer_costs.retained_shared_metadata_bytes for r in results}), 1)

    def test_clean_feed_pcd_preserves_post_change_samples_with_fewer_gets(self) -> None:
        revisions = [
            self.revision("A", "1", dt("2026-05-24T00:00:10Z"), b"one"),
            self.revision("A", "2", dt("2026-05-24T00:04:10Z"), b"two"),
        ]
        events = [self.save(item) for item in revisions]
        pd = self.collect(PeriodicPolicy.PD, events, revisions)
        pcd = self.collect(PeriodicPolicy.PCD, events, revisions)
        pd_post_change = [pd.capture_attempts[0].capture.body, pd.capture_attempts[-1].capture.body]
        self.assertEqual([x.capture.body for x in pcd.capture_attempts], pd_post_change)
        self.assertLessEqual(len(pcd.body_results), len(pd.body_results))

    def test_changed_then_overwritten_before_delayed_response_returns_current_body(self) -> None:
        old = self.revision("A", "1", dt("2026-05-24T00:00:10Z"), b"old")
        new = self.revision("A", "2", dt("2026-05-24T00:02:15Z"), b"new")
        result = self.collect(
            PeriodicPolicy.PCD, [self.save(old), self.save(new)], [old, new],
            delay_us=30_000_000,
        )
        self.assertEqual(result.capture_attempts[0].capture.body, b"new")

    def test_deleted_before_delayed_response_has_no_historical_body(self) -> None:
        saved = self.revision("A", "1", dt("2026-05-24T00:00:10Z"), b"gone")
        deleted = self.delete("A", "1", dt("2026-05-24T00:02:15Z"))
        result = self.collect(
            PeriodicPolicy.PCD, [self.save(saved), deleted], [saved], delay_us=30_000_000
        )
        self.assertEqual(result.body_results[0].outcome, BodyOutcome.MISSING)
        self.assertEqual(result.captures_attempted, 0)

    def test_body_unknown_response_remains_explicit(self) -> None:
        result = self.collect(
            PeriodicPolicy.PCD,
            [self.body_unknown("A", dt("2026-05-24T00:00:10Z"))],
            [],
        )
        self.assertEqual(result.body_results[0].outcome, BodyOutcome.BODY_UNKNOWN)
        self.assertEqual(dict(result.outcome_counts)["body_unknown"], 1)
        self.assertEqual(result.captures_attempted, 0)

    def test_delete_feed_removes_pending_changed_only_request(self) -> None:
        saved = self.revision("A", "1", dt("2026-05-24T00:00:10Z"), b"gone")
        deleted = self.delete("A", "1", dt("2026-05-24T00:01:10Z"))
        result = self.collect(PeriodicPolicy.PCD, [self.save(saved), deleted], [saved])
        self.assertEqual(result.body_results, ())

    def test_same_time_mixed_feed_is_not_treated_as_confirmed_deleted(self) -> None:
        when = dt("2026-05-24T00:00:10Z")
        saved = self.revision("A", "1", when, b"A")
        result = self.collect(
            PeriodicPolicy.PCD, [self.save(saved), self.delete("A", "1", when)], [saved]
        )
        self.assertEqual(len(result.body_results), 1)
        self.assertEqual(result.body_results[0].outcome, BodyOutcome.AMBIGUOUS)

    def test_capped_fifo_and_dedup_are_delegated_to_e08_store(self) -> None:
        revision = self.revision("A", "1", dt("2026-05-24T00:00:10Z"), b"x")
        result = self.collect(
            PeriodicPolicy.PD, [self.save(revision)], [revision], capacity=330
        )
        self.assertEqual(result.storage_snapshot.retained_body_objects, 1)
        self.assertEqual(result.storage_snapshot.retained_request_seqs, (2, 3))
        self.assertEqual(result.capture_attempts[-1].admission.evicted_request_seqs, (1,))
        self.assertLessEqual(result.storage_snapshot.final_store_bytes, 330)

    def test_oversize_rejection_is_auditable(self) -> None:
        revision = self.revision("A", "1", dt("2026-05-24T00:00:10Z"), b"x")
        result = self.collect(
            PeriodicPolicy.PD, [self.save(revision)], [revision], capacity=0
        )
        self.assertEqual(result.captures_attempted, 3)
        self.assertEqual(result.captures_admitted, 0)
        self.assertEqual(result.storage_snapshot.rejected_oversize_packets, 3)
        self.assertTrue(all(x.admission.disposition == "oversize" for x in result.capture_attempts))

    def test_storage_cap_does_not_change_request_schedule(self) -> None:
        revision = self.revision("A", "1", dt("2026-05-24T00:00:10Z"), b"x")
        uncapped = self.collect(PeriodicPolicy.PD, [self.save(revision)], [revision])
        capped = self.collect(PeriodicPolicy.PD, [self.save(revision)], [revision], capacity=0)
        self.assertEqual(uncapped.body_request_schedule, capped.body_request_schedule)
        self.assertEqual(uncapped.body_results, capped.body_results)

    def test_annotation_modules_are_not_imported(self) -> None:
        source = (ROOT / "src" / "ebe" / "collectors.py").read_text(encoding="utf-8")
        imported = set()
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                imported.add(node.module)
        self.assertFalse(any("annotation" in name for name in imported))

    def test_future_suffix_invariant(self) -> None:
        first = self.revision("A", "1", dt("2026-05-24T00:00:10Z"), b"one")
        future = self.revision("A", "2", dt("2026-05-24T00:08:10Z"), b"future")
        prefix = self.collect(PeriodicPolicy.PCD, [self.save(first)], [first])
        suffix = self.collect(
            PeriodicPolicy.PCD, [self.save(first), self.save(future)], [first, future]
        )
        self.assertEqual(prefix, suffix)

    def test_retrospective_relation_metadata_does_not_affect_scheduling(self) -> None:
        revision = self.revision("A", "1", dt("2026-05-24T00:00:10Z"), b"A")
        relation = replace(
            self.save_template.relations,
            related_event_id=replace(self.save_template.relations.related_event_id, value="secret"),
            edges=(),
        )
        plain = self.collect(PeriodicPolicy.PCD, [self.save(revision)], [revision])
        related = self.collect(
            PeriodicPolicy.PCD, [self.save(revision, relations=relation)], [revision]
        )
        self.assertEqual(plain, related)

    def test_title_order_is_stable_visible_key_order(self) -> None:
        when = dt("2026-05-24T00:00:10Z")
        a = self.revision("A", "1", when, b"A")
        z = self.revision("Z", "1", when, b"Z")
        result = self.collect(
            PeriodicPolicy.PCD, [self.save(z), self.save(a)], [z, a],
            checkpoint="2026-05-24T00:03:00Z",
        )
        self.assertEqual([x.page_key for x in result.body_results], ["dse~A", "dse~Z"])

    def test_invalid_schedule_parameters_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            tuple(periodic_sweep_times(0))
        with self.assertRaises(ValueError):
            tuple(periodic_sweep_times(MINUTE_US, MINUTE_US))


class EventDerivedCollectorTests(unittest.TestCase):
    """E10 queue/rate/fairness tests using the same synthetic E08 boundary."""

    @classmethod
    def setUpClass(cls) -> None:
        PeriodicCollectorTests.setUpClass.__func__(cls)

    revision = PeriodicCollectorTests.revision
    save = PeriodicCollectorTests.save
    delete = PeriodicCollectorTests.delete
    body_unknown = PeriodicCollectorTests.body_unknown
    observer = PeriodicCollectorTests.observer
    collect = PeriodicCollectorTests.collect
    collect_e = PeriodicCollectorTests.collect_e

    def test_first_change_makes_one_dirty_item_and_repeated_changes_coalesce(self) -> None:
        revisions = [
            self.revision("A", str(i), dt(f"2026-05-24T00:00:{i}0Z"), str(i).encode())
            for i in (1, 2, 3)
        ]
        result = self.collect_e([self.save(x) for x in revisions], revisions)
        self.assertEqual(len(result.body_results), 1)
        self.assertEqual(result.event_stats.max_queue_depth, 1)
        self.assertEqual(result.event_stats.coalesced_updates, 2)

    def test_different_pages_are_separate_and_visible_key_breaks_ties(self) -> None:
        when = dt("2026-05-24T00:00:10Z")
        a = self.revision("A", "1", when, b"A")
        z = self.revision("Z", "1", when, b"Z")
        result = self.collect_e(
            [self.save(z), self.save(a)], [z, a], q=1,
            checkpoint="2026-05-24T00:03:00Z",
        )
        self.assertEqual(result.event_stats.max_queue_depth, 2)
        self.assertEqual([x.page_key for x in result.body_results], ["dse~A"])
        self.assertEqual(result.event_stats.pending_dirty_pages, ((when, "dse~Z"),))

    def test_oldest_pending_visible_change_orders_queue(self) -> None:
        early = self.revision("Z", "1", dt("2026-05-24T00:00:10Z"), b"early")
        late = self.revision("A", "1", dt("2026-05-24T00:00:20Z"), b"late")
        result = self.collect_e(
            [self.save(late), self.save(early)], [late, early], q=1,
            checkpoint="2026-05-24T00:03:00Z",
        )
        self.assertEqual([x.page_key for x in result.body_results], ["dse~Z"])

    def test_initial_bucket_capacity_and_backlog_are_exact(self) -> None:
        when = dt("2026-05-24T00:00:10Z")
        revisions = [self.revision(f"P{i:02d}", "1", when, b"x") for i in range(31)]
        result = self.collect_e(
            [self.save(x) for x in revisions], revisions, q=30,
            checkpoint="2026-05-24T00:02:00Z",
        )
        self.assertEqual(len(result.body_results), 30)
        self.assertEqual(len(result.event_stats.pending_dirty_pages), 1)
        self.assertEqual(result.event_stats.final_token_credit_numerator, 30 * MINUTE_US)

    def test_refill_is_continuous_exact_and_dispatches_on_minute_epoch(self) -> None:
        when = dt("2026-05-24T00:00:10Z")
        revisions = [self.revision(f"P{i:02d}", "1", when, b"x") for i in range(31)]
        result = self.collect_e(
            [self.save(x) for x in revisions], revisions, q=30,
            checkpoint="2026-05-24T00:04:00Z",
        )
        self.assertEqual(len(result.body_results), 31)
        self.assertEqual(result.body_results[-1].request_time, dt("2026-05-24T00:03:00Z"))
        self.assertGreaterEqual(result.event_stats.token_starved_dispatch_opportunities, 1)

    def test_token_bucket_bound_holds_for_every_request_prefix(self) -> None:
        when = dt("2026-05-24T00:00:10Z")
        revisions = [self.revision(f"P{i:03d}", "1", when, b"x") for i in range(80)]
        result = self.collect_e(
            [self.save(x) for x in revisions], revisions, q=30,
            checkpoint="2026-05-24T00:31:00Z",
        )
        for item in result.body_results:
            elapsed = int((item.request_time - HORIZON_START).total_seconds() * 1_000_000)
            allowed = 30 + (30 * elapsed) // (60 * MINUTE_US)
            made = sum(x.request_time <= item.request_time for x in result.body_results)
            self.assertLessEqual(made, allowed)

    def test_failed_body_unknown_attempt_consumes_a_token_without_retry(self) -> None:
        event = self.body_unknown("A", dt("2026-05-24T00:00:10Z"))
        result = self.collect_e([event], [], q=1, checkpoint="2026-05-24T00:03:00Z")
        self.assertEqual(result.body_results[0].outcome, BodyOutcome.BODY_UNKNOWN)
        self.assertEqual(result.observer_costs.body_requests, 1)
        self.assertEqual(result.event_stats.final_token_credit_numerator, 2 * MINUTE_US)

    def test_missing_response_consumes_a_token_without_retry(self) -> None:
        saved = self.revision("A", "1", dt("2026-05-24T00:00:10Z"), b"gone")
        deleted = self.delete("A", "1", dt("2026-05-24T00:01:15Z"))
        result = self.collect_e(
            [self.save(saved), deleted], [saved], q=1, delay_us=30_000_000,
            checkpoint="2026-05-24T00:03:00Z",
        )
        self.assertEqual(result.body_results[0].outcome, BodyOutcome.MISSING)
        self.assertEqual(result.observer_costs.body_requests, 1)
        self.assertEqual(result.captures_attempted, 0)

    def test_attempt_pending_past_global_horizon_is_charged(self) -> None:
        when = dt("2026-05-24T00:00:10Z")
        revision = self.revision("A", "1", when, b"A")
        result = self.collect_e(
            [self.save(revision)], [revision], q=1,
            delay_us=60 * 24 * 60 * MINUTE_US,
            checkpoint="2026-05-24T00:03:00Z",
        )
        self.assertEqual(result.observer_costs.body_requests, 1)
        self.assertEqual(result.observer_costs.pending_body_requests, 1)
        self.assertEqual(dict(result.outcome_counts)["pending"], 1)

    def test_get_time_state_only_overwrite_cannot_recover_trigger_body(self) -> None:
        old = self.revision("A", "1", dt("2026-05-24T00:00:10Z"), b"old")
        new = self.revision("A", "2", dt("2026-05-24T00:01:15Z"), b"new")
        blocker = self.revision("B", "1", dt("2026-05-24T00:00:05Z"), b"B")
        result = self.collect_e(
            [self.save(old), self.save(new), self.save(blocker)], [old, new, blocker],
            q=1, checkpoint="2026-05-24T01:02:00Z",
        )
        self.assertEqual([x.capture.body for x in result.capture_attempts], [b"B", b"new"])
        self.assertEqual(result.event_stats.coalesced_updates, 1)

    def test_delete_before_dispatch_removes_work_and_never_fetches_old_body(self) -> None:
        a = self.revision("A", "1", dt("2026-05-24T00:00:10Z"), b"gone")
        b = self.revision("B", "1", dt("2026-05-24T00:00:05Z"), b"B")
        deleted = self.delete("A", "1", dt("2026-05-24T00:01:10Z"))
        result = self.collect_e(
            [self.save(a), self.save(b), deleted], [a, b], q=1,
            checkpoint="2026-05-24T00:04:00Z",
        )
        self.assertEqual([x.page_key for x in result.body_results], ["dse~B"])
        self.assertEqual(result.event_stats.pending_dirty_pages, ())

    def test_same_time_mixed_group_remains_request_eligible(self) -> None:
        when = dt("2026-05-24T00:00:10Z")
        saved = self.revision("A", "1", when, b"A")
        result = self.collect_e([self.save(saved), self.delete("A", "1", when)], [saved])
        self.assertEqual(result.body_results[0].outcome, BodyOutcome.AMBIGUOUS)

    def test_shared_observer_feed_and_get_semantics_match_pcd(self) -> None:
        revision = self.revision("A", "1", dt("2026-05-24T00:00:10Z"), b"A")
        events = [self.save(revision)]
        periodic = self.collect(
            PeriodicPolicy.PCD, events, [revision], interval_minutes=1
        )
        event = self.collect_e(events, [revision])
        self.assertEqual(
            [x.response_bytes for x in periodic.feed_polls],
            [x.response_bytes for x in event.feed_polls],
        )
        self.assertEqual(periodic.body_results, event.body_results)
        self.assertIsInstance(EventDerivedCollector(self.observer(events, [revision]), EventDerivedConfig(30)), EventDerivedCollector)

    def test_publication_lag_and_discovery_apply_identically(self) -> None:
        revision = self.revision("A", "1", dt("2026-05-24T00:00:59Z"), b"A")
        result = self.collect_e([self.save(revision)], [revision], checkpoint="2026-05-24T00:03:00Z")
        self.assertEqual(result.body_results[0].request_time, dt("2026-05-24T00:02:00Z"))

    def test_exact_dedup_fifo_cap_and_oversize_use_shared_store(self) -> None:
        first = self.revision("A", "1", dt("2026-05-24T00:00:10Z"), b"same")
        second = self.revision("A", "2", dt("2026-05-24T00:01:10Z"), b"same")
        dedup = self.collect_e([self.save(first), self.save(second)], [first, second])
        self.assertEqual(dedup.storage_snapshot.retained_packets, 2)
        self.assertEqual(dedup.storage_snapshot.retained_body_objects, 1)
        rejected = self.collect_e([self.save(first)], [first], capacity=0)
        self.assertEqual(rejected.storage_snapshot.rejected_oversize_packets, 1)
        self.assertEqual(rejected.captures_admitted, 0)

    def test_pcd_and_event_derived_share_capture_store_accounting(self) -> None:
        revisions = [
            self.revision("A", str(i), dt(f"2026-05-24T00:0{i}:10Z"), b"same")
            for i in (0, 1, 2)
        ]
        events = [self.save(x) for x in revisions]
        periodic = self.collect(
            PeriodicPolicy.PCD, events, revisions, interval_minutes=1, capacity=330
        )
        event = self.collect_e(events, revisions, capacity=330)
        self.assertEqual(periodic.body_results, event.body_results)
        self.assertEqual(periodic.capture_attempts, event.capture_attempts)
        self.assertEqual(periodic.storage_snapshot, event.storage_snapshot)

    def test_request_costs_and_outcomes_are_observer_accounted(self) -> None:
        revision = self.revision("A", "1", dt("2026-05-24T00:00:10Z"), b"A")
        result = self.collect_e([self.save(revision)], [revision])
        self.assertEqual(result.observer_costs.body_requests, len(result.body_results))
        self.assertEqual(result.observer_costs.successful_body_responses, 1)
        self.assertEqual(result.requests_made, result.observer_costs.feed_requests + 1)

    def test_final_poll_can_leave_pending_but_never_dispatches_at_checkpoint(self) -> None:
        revision = self.revision("A", "1", dt("2026-05-24T00:01:55Z"), b"A")
        result = self.collect_e(
            [self.save(revision)], [revision], checkpoint="2026-05-24T00:02:00Z"
        )
        self.assertEqual(result.body_results, ())
        self.assertEqual(result.event_stats.pending_dirty_pages, ((revision.time.utc, "dse~A"),))
        self.assertNotIn(dt("2026-05-24T00:02:00Z"), result.event_stats.dispatch_times)

    def test_future_suffix_invariance_and_repeat_determinism(self) -> None:
        first = self.revision("A", "1", dt("2026-05-24T00:00:10Z"), b"one")
        future = self.revision("A", "2", dt("2026-05-24T00:08:10Z"), b"future")
        one = self.collect_e([self.save(first)], [first])
        two = self.collect_e([self.save(first), self.save(future)], [first, future])
        repeat = self.collect_e([self.save(first)], [first])
        self.assertEqual(one, two)
        self.assertEqual(one, repeat)

    def test_queue_order_does_not_depend_on_body_or_relation_metadata(self) -> None:
        when = dt("2026-05-24T00:00:10Z")
        a = self.revision("A", "1", when, b"semantically critical")
        z = self.revision("Z", "1", when, b"ordinary")
        plain = self.collect_e([self.save(z), self.save(a)], [z, a], q=1)
        swapped_a = replace(a, body="ordinary", source_body_bytes=b"ordinary", body_len=8, body_sha256=hashlib.sha256(b"ordinary").hexdigest())
        swapped_z = replace(z, body="semantically critical", source_body_bytes=b"semantically critical", body_len=21, body_sha256=hashlib.sha256(b"semantically critical").hexdigest())
        swapped = self.collect_e([self.save(swapped_z), self.save(swapped_a)], [swapped_z, swapped_a], q=1)
        self.assertEqual([x.page_key for x in plain.body_results], [x.page_key for x in swapped.body_results])

    def test_retrospective_relations_do_not_affect_event_queue(self) -> None:
        revision = self.revision("A", "1", dt("2026-05-24T00:00:10Z"), b"A")
        relation = replace(
            self.save_template.relations,
            related_event_id=replace(self.save_template.relations.related_event_id, value="secret"),
            edges=(),
        )
        plain = self.collect_e([self.save(revision)], [revision])
        related = self.collect_e([self.save(revision, relations=relation)], [revision])
        self.assertEqual(plain, related)

    def test_event_collector_observer_surface_has_no_privileged_fields(self) -> None:
        source = (ROOT / "src" / "ebe" / "collectors.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        event_class = next(
            node for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "EventDerivedCollector"
        )
        direct = {
            node.attr
            for node in ast.walk(event_class)
            if isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Attribute)
            and isinstance(node.value.value, ast.Name)
            and node.value.value.id == "self"
            and node.value.attr == "observer"
        }
        self.assertLessEqual(
            direct, {"config", "poll_feed", "discovered_titles", "get_body", "complete_due", "costs"}
        )

    def test_no_annotation_or_semantic_modules_are_imported_for_e10(self) -> None:
        source = (ROOT / "src" / "ebe" / "collectors.py").read_text(encoding="utf-8")
        imported = set()
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                imported.add(node.module)
        forbidden = ("annotation", "evidence", "critical", "relation", "family")
        self.assertFalse(any(any(word in name.lower() for word in forbidden) for name in imported))

    def test_invalid_event_config_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            EventDerivedConfig(0)
        with self.assertRaises(ValueError):
            EventDerivedConfig(30, -1)


if __name__ == "__main__":
    unittest.main()
