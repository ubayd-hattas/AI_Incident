from __future__ import annotations

import sys
import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ebe import load_export  # noqa: E402
from ebe.observer import (  # noqa: E402
    BodyOutcome,
    Observer,
    ObserverConfig,
    PendingBodyRequest,
    PollScheduleError,
)


PINNED = ROOT / "data" / "raw" / "export"
UTC = timezone.utc


def dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


class SyntheticObserverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        export = load_export(PINNED)
        cls.save_template = next(
            event for event in export.events if event.event_type.value == "save" and not event.relations.edges
        )
        cls.delete_template = next(
            event for event in export.events if event.event_type.value == "delete" and not event.relations.edges
        )
        cls.bu_template = next(event for event in export.events if event.event_type.value == "revert")
        cls.revision_template = export.revisions_by_id[cls.save_template.revision_ref]

    def revision(self, page: str, suffix: str, when: datetime, body: bytes):
        import hashlib

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

    def test_future_title_and_event_are_invisible_before_delivery(self) -> None:
        early = dt("2026-05-24T00:00:10Z")
        later = dt("2026-05-24T00:01:10Z")
        a = self.revision("A", "1", early, b"A")
        b = self.revision("B", "1", later, b"B")
        observer = self.observer([self.save(a), self.save(b)], [a, b])
        first = observer.poll_feed(dt("2026-05-24T00:01:00Z"))
        self.assertEqual([record.page_key for record in first.records], ["dse~A"])
        self.assertEqual(observer.discovered_titles, ("dse~A",))
        unknown = observer.get_body("dse~B", dt("2026-05-24T00:01:00Z"))
        self.assertEqual(unknown.outcome, BodyOutcome.UNKNOWN)
        self.assertNotIn("dse~B", observer.discovered_titles)

    def test_feed_publication_lag_applies_at_common_poll(self) -> None:
        event_time = dt("2026-05-24T00:00:56Z")
        revision = self.revision("A", "1", event_time, b"A")
        observer = self.observer([self.save(revision)], [revision])
        self.assertEqual(observer.poll_feed(dt("2026-05-24T00:01:00Z")).records, ())
        delivered = observer.poll_feed(dt("2026-05-24T00:02:00Z"))
        self.assertEqual(len(delivered.records), 1)
        self.assertEqual(delivered.records[0].event_time, event_time)

    def test_feed_schema_has_only_frozen_content_free_fields(self) -> None:
        when = dt("2026-05-24T00:00:10Z")
        revision = self.revision("A", "1", when, b"secret body")
        observer = self.observer([self.save(revision)], [revision])
        record = observer.poll_feed(dt("2026-05-24T00:01:00Z")).records[0]
        self.assertEqual(set(record.as_dict()), {"action", "event_time", "page_key"})
        serialized = record.canonical_bytes
        for forbidden in (b"secret body", b"body_sha", b"revision", b"critical", b"relation"):
            self.assertNotIn(forbidden, serialized)

    def test_body_get_reads_response_time_and_not_trigger_revision(self) -> None:
        first_time = dt("2026-05-24T00:00:10Z")
        second_time = dt("2026-05-24T00:01:15Z")
        a = self.revision("A", "1", first_time, b"old")
        b = self.revision("A", "2", second_time, b"new")
        observer = self.observer([self.save(a), self.save(b)], [a, b], delay_us=30_000_000)
        observer.poll_feed(dt("2026-05-24T00:01:00Z"))
        response = observer.get_body("dse~A", dt("2026-05-24T00:01:00Z"))
        self.assertEqual(response.response_time, dt("2026-05-24T00:01:30Z"))
        self.assertEqual(response.outcome, BodyOutcome.BODY)
        self.assertEqual(response.body, b"new")
        self.assertNotEqual(response.body, b"old")

    def test_deleted_body_does_not_reappear(self) -> None:
        saved = dt("2026-05-24T00:00:10Z")
        deleted = dt("2026-05-24T00:01:15Z")
        revision = self.revision("A", "1", saved, b"gone")
        observer = self.observer([self.save(revision), self.delete("A", "1", deleted)], [revision], delay_us=30_000_000)
        observer.poll_feed(dt("2026-05-24T00:01:00Z"))
        response = observer.get_body("dse~A", dt("2026-05-24T00:01:00Z"))
        self.assertEqual(response.outcome, BodyOutcome.MISSING)
        self.assertIsNone(response.body)
        self.assertEqual(observer.costs().downloaded_known_body_bytes, 0)

    def test_body_unknown_remains_explicit(self) -> None:
        when = dt("2026-05-24T00:00:10Z")
        observer = self.observer([self.body_unknown("A", when)], [])
        observer.poll_feed(dt("2026-05-24T00:01:00Z"))
        response = observer.get_body("dse~A", dt("2026-05-24T00:01:00Z"))
        self.assertEqual(response.outcome, BodyOutcome.BODY_UNKNOWN)
        self.assertIsNone(response.body)
        self.assertIsNone(observer.costs().downloaded_total_bytes)

    def test_same_time_incompatible_states_return_ambiguous_not_a_union(self) -> None:
        when = dt("2026-05-24T00:00:10Z")
        a = self.revision("A", "1", when, b"one")
        b = self.revision("A", "2", when, b"two")
        observer = self.observer([self.save(a), self.save(b)], [a, b])
        observer.poll_feed(dt("2026-05-24T00:01:00Z"))
        response = observer.get_body("dse~A", dt("2026-05-24T00:01:00Z"))
        self.assertEqual(response.outcome, BodyOutcome.AMBIGUOUS)
        self.assertIsNone(response.body)

    def test_relation_and_annotation_fields_never_enter_observations(self) -> None:
        when = dt("2026-05-24T00:00:10Z")
        revision = self.revision("A", "1", when, b"A")
        relation = replace(
            self.save_template.relations,
            related_event_id=replace(self.save_template.relations.related_event_id, value="future-secret"),
            edges=(),
        )
        observer = self.observer([self.save(revision, relations=relation)], [revision])
        result = observer.poll_feed(dt("2026-05-24T00:01:00Z"))
        visible = result.response_bytes
        for forbidden in (b"future-secret", b"criticality", b"annotation", b"page_family"):
            self.assertNotIn(forbidden, visible)

    def test_polling_and_request_accounting_are_deterministic(self) -> None:
        when = dt("2026-05-24T00:00:10Z")
        revision = self.revision("A", "1", when, b"A")
        observers = [self.observer([self.save(revision)], [revision]) for _ in range(2)]
        outputs = []
        for observer in observers:
            polls = [
                observer.poll_feed(dt("2026-05-24T00:00:00Z")),
                observer.poll_feed(dt("2026-05-24T00:01:00Z")),
            ]
            response = observer.get_body("dse~A", dt("2026-05-24T00:01:00Z"))
            outputs.append(([poll.response_bytes for poll in polls], response, observer.costs()))
        self.assertEqual(outputs[0], outputs[1])
        costs = outputs[0][2]
        self.assertEqual(costs.feed_requests, 2)
        self.assertEqual(costs.body_requests, 1)
        self.assertEqual(costs.successful_body_responses, 1)
        self.assertEqual(costs.downloaded_metadata_bytes, 3 + 89 + 19)
        self.assertEqual(costs.downloaded_known_body_bytes, 1)

    def test_identical_prefixes_have_identical_observations_and_costs(self) -> None:
        prefix_time = dt("2026-05-24T00:00:10Z")
        future_time = dt("2026-05-24T00:02:10Z")
        a = self.revision("A", "1", prefix_time, b"A")
        future = self.revision("A", "2", future_time, b"future")
        prefix = self.observer([self.save(a)], [a])
        suffix = self.observer([self.save(a), self.save(future)], [a, future])
        observed = []
        for observer in (prefix, suffix):
            poll = observer.poll_feed(dt("2026-05-24T00:01:00Z"))
            get = observer.get_body("dse~A", dt("2026-05-24T00:01:00Z"))
            observed.append((poll, get, observer.discovered_titles, observer.costs()))
        self.assertEqual(observed[0], observed[1])

    def test_feed_poll_requires_frozen_epoch_schedule(self) -> None:
        observer = self.observer([], [])
        with self.assertRaises(PollScheduleError):
            observer.poll_feed(dt("2026-05-24T00:00:01Z"))

    def test_feed_metadata_retention_byte_hours(self) -> None:
        when = dt("2026-05-24T00:00:00Z")
        revision = self.revision("A", "1", when, b"A")
        observer = self.observer([self.save(revision)], [revision])
        poll = observer.poll_feed(dt("2026-05-24T00:01:00Z"))
        costs = observer.costs(dt("2026-05-24T01:01:00Z"))
        self.assertEqual(costs.retained_shared_metadata_bytes, len(poll.records[0].canonical_bytes))
        self.assertEqual(costs.shared_metadata_byte_hours, len(poll.records[0].canonical_bytes))

    def test_terminal_directory_is_state_derived_and_charged_at_T(self) -> None:
        when = dt("2026-05-24T00:00:10Z")
        live = self.revision("A", "1", when, b"A")
        deleted = self.revision("B", "1", when, b"B")
        events = [
            self.save(live), self.save(deleted),
            self.delete("B", "1", when + timedelta(seconds=1)),
            self.body_unknown("C", when + timedelta(seconds=2)),
        ]
        observer = self.observer(events, [live, deleted])
        directory = observer.terminal_directory()
        self.assertEqual(directory.page_keys, ("dse~A", "dse~C"))
        self.assertEqual(directory.response_bytes, b'["dse~A","dse~C"]\n')
        costs = observer.costs(dt("2026-07-15T00:00:00Z"))
        self.assertEqual(costs.directory_requests, 1)
        self.assertEqual(costs.downloaded_metadata_bytes, len(directory.response_bytes))
        self.assertEqual(costs.retained_shared_metadata_bytes, len(directory.response_bytes))
        self.assertEqual(costs.shared_metadata_byte_hours, 0)

    def test_response_after_T_is_pending_without_download(self) -> None:
        when = dt("2026-07-14T23:58:10Z")
        revision = self.revision("A", "1", when, b"A")
        observer = self.observer([self.save(revision)], [revision], delay_us=30_000_000)
        observer.poll_feed(dt("2026-07-14T23:59:00Z"))
        before = observer.costs().downloaded_metadata_bytes
        result = observer.get_body("dse~A", dt("2026-07-14T23:59:45Z"))
        self.assertIsInstance(result, PendingBodyRequest)
        costs = observer.costs()
        self.assertEqual(costs.body_requests, 1)
        self.assertEqual(costs.pending_body_requests, 1)
        self.assertEqual(costs.downloaded_metadata_bytes, before)


if __name__ == "__main__":
    unittest.main()
