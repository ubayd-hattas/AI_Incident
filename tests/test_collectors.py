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
    PeriodicConfig,
    PeriodicPolicy,
    periodic_sweep_times,
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


if __name__ == "__main__":
    unittest.main()
