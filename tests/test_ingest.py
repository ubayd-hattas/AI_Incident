from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ebe.ingest import ValidationError, load_export  # noqa: E402
from ebe.schema import (  # noqa: E402
    BodyEncoding,
    ExportedEventType,
    ObservedEventSemantics,
    RelationValueForm,
)


PINNED = ROOT / "data" / "raw" / "export"


def page_row() -> dict:
    return {
        "page_id": "dse/A/B", "page_key": "opaque-key", "wiki": "dse", "name": "A/B",
        "bucket": "A", "page_family": "unknown", "page_family_cohort": None,
        "page_family_confidence": None, "page_family_method": None,
        "page_family_source": "none", "n_revs": 1, "n_revs_before": 0,
        "first_write": "2026-01-01T00:00:00Z", "last_write": "2026-01-01T00:00:06Z",
        "body_bytes": 3, "deleted_live": False, "live_body_variant": "txt",
        "head_differs_from_live": False, "n_deletions": 0, "n_recreations": 0,
        "labels": [""], "n_labels": 1, "n_ips": 1, "n_ip16": 1,
    }


def revision_row(body: str = "abc", encoding: str = "ascii") -> dict:
    body_bytes = body.encode("latin-1")
    return {
        "rev_id": "opaque-revision", "page_id": "dse/A/B", "page_key": "opaque-key",
        "wiki": "dse", "name": "A/B", "seq": 1, "rcs_rev": "1.1",
        "rcs_path": "opaque/path", "body": body, "body_len": len(body_bytes),
        "body_sha256": hashlib.sha256(body_bytes).hexdigest(), "lines": 1,
        "diff_base": None, "diff_base_reason": "page_created",
        "hunks": [{"op": "insert", "a0": 0, "a1": 0, "b0": 0, "b1": 1}],
        "label": "", "ip16": "192.0", "time": "2026-01-01T00:00:01Z",
        "time_grade": "reqlog", "winning_clock": "revision.pref_ts",
        "uncertainty_seconds": 1, "request_time": "2026-01-01T00:00:02Z",
        "success_time": "2026-01-01T00:00:03Z",
        "recent_changes_time": "2026-01-01T00:00:04Z",
        "write_date": "2026-01-01T00:00:05Z", "archived_at": "2026-01-01T00:00:06Z",
        "request_action": None, "change_summary": None, "related_event_id": None,
        "relation_type": None, "round_id": None, "body_encoding": encoding,
    }


def save_event() -> dict:
    return {
        "event_id": "save-one", "event_type": "save", "wiki": "dse", "page": "A/B",
        "page_key": "opaque-key", "time": "2026-01-01T00:00:01Z",
        "time_grade": "reqlog", "revision_ref": "opaque-revision",
        "related_event_id": None, "relation_type": None, "round_id": None,
    }


def label_row() -> dict:
    return {
        "label": "", "is_human_handle": False, "stored_revisions": 1,
        "first_write": "2026-01-01T00:00:00Z", "last_write": "2026-01-01T00:00:06Z",
        "stored_revision_ips": 1, "stored_revision_ip16": 1, "stored_revision_pages": 1,
        "pages": ["dse/A/B"], "wikis": ["dse"], "save_requests": 0,
        "save_request_ips": 0, "save_request_ip16": 0, "save_request_pages": 0,
        "save_request_source": None,
    }


def manifest_row() -> dict:
    return {
        "generated_at": "2026-01-02T00:00:00Z", "db_sha256": "0" * 64,
        "cut": {}, "counts": {}, "per_wiki": {}, "population_counts": {},
        "grade_histograms": {}, "body_bytes": {}, "body_encoding": {},
        "page_family_coverage": {}, "facts": {}, "recreation_source": {},
        "resources": {}, "tool_versions": {}, "source_scan": {},
        "request_source_note": "synthetic", "checks": [],
    }


def write_fixture(directory: Path, *, pages=None, revisions=None, events=None, labels=None, manifest=None) -> None:
    values = {
        "pages.jsonl": pages if pages is not None else [page_row()],
        "revisions.jsonl": revisions if revisions is not None else [revision_row()],
        "events.jsonl": events if events is not None else [save_event()],
        "labels.jsonl": labels if labels is not None else [label_row()],
    }
    for filename, rows in values.items():
        (directory / filename).write_text(
            "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in rows),
            encoding="utf-8",
        )
    (directory / "manifest.json").write_text(
        json.dumps(manifest if manifest is not None else manifest_row()), encoding="utf-8"
    )


class PinnedExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.export = load_export(PINNED)

    def test_01_pinned_counts_load(self) -> None:
        self.assertEqual(
            (len(self.export.pages), len(self.export.revisions), len(self.export.events), len(self.export.labels)),
            (4579, 14591, 19913, 3103),
        )

    def test_02_body_hashes_lengths_and_encodings(self) -> None:
        counts = {encoding: 0 for encoding in BodyEncoding}
        for revision in self.export.revisions:
            self.assertEqual(len(revision.source_body_bytes), revision.body_len)
            self.assertEqual(hashlib.sha256(revision.source_body_bytes).hexdigest(), revision.body_sha256)
            counts[revision.body_encoding] += 1
        self.assertEqual(
            counts,
            {BodyEncoding.ASCII: 14340, BodyEncoding.UTF8: 250, BodyEncoding.LATIN1: 1},
        )

    def test_03_unique_ids_and_one_to_one_save_links(self) -> None:
        self.assertEqual(len(self.export.pages_by_id), len(self.export.pages))
        self.assertEqual(len(self.export.pages_by_key), len(self.export.pages))
        self.assertEqual(len(self.export.revisions_by_id), len(self.export.revisions))
        self.assertEqual(len(self.export.events_by_id), len(self.export.events))
        saves = [event for event in self.export.events if event.event_type is ExportedEventType.SAVE]
        self.assertEqual(len(saves), len(self.export.revisions))
        self.assertEqual({event.revision_ref for event in saves}, set(self.export.revisions_by_id))

    def test_04_relation_normalization_preserves_rows_and_edges(self) -> None:
        rows = [event for event in self.export.events if event.relations.edges]
        self.assertEqual(len(rows), 67)
        self.assertEqual(sum(len(event.relations.edges) for event in rows), 68)
        self.assertTrue(any(event.relations.related_event_id.form is RelationValueForm.LIST for event in rows))
        array_row = next(event for event in rows if event.relations.related_event_id.form is RelationValueForm.LIST)
        self.assertIsInstance(array_row.raw["related_event_id"], list)

    def test_05_round_only_deletions_remain_relationless(self) -> None:
        rows = [
            event for event in self.export.events
            if event.event_type is ExportedEventType.DELETE
            and event.relations.round_id.form is RelationValueForm.SCALAR
            and event.relations.relation_type.form is RelationValueForm.NULL
            and event.relations.related_event_id.form is RelationValueForm.NULL
        ]
        self.assertEqual(len(rows), 29)
        self.assertTrue(all(not event.relations.edges for event in rows))

    def test_06_exported_reverts_are_body_unknown_form_edits(self) -> None:
        rows = [event for event in self.export.events if event.event_type is ExportedEventType.REVERT]
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(event.revision_ref is None for event in rows))
        self.assertTrue(all(event.observed_semantics is ObservedEventSemantics.BODY_UNKNOWN_FORM_EDIT for event in rows))

    def test_07_blank_labels_and_slash_names_are_opaque(self) -> None:
        self.assertIn("", self.export.labels_by_label)
        slash_pages = [page for page in self.export.pages if "/" in page.name]
        self.assertEqual(len(slash_pages), 77)
        self.assertTrue(all(page.name == page.raw["name"] for page in slash_pages))

    def test_08_nulls_and_distinct_clock_fields_survive(self) -> None:
        revision = next(item for item in self.export.revisions if item.request_time is None)
        self.assertIsNone(revision.request_time)
        self.assertIsNone(revision.raw["request_time"])
        clocked = next(item for item in self.export.revisions if item.request_time is not None)
        self.assertEqual(clocked.time.raw, clocked.raw["time"])
        self.assertEqual(clocked.request_time.raw, clocked.raw["request_time"])
        self.assertEqual(clocked.archived_at.raw, clocked.raw["archived_at"])
        self.assertIsNot(clocked.time, clocked.request_time)


class SyntheticFixtureTests(unittest.TestCase):
    def load(self, **changes):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name)
        write_fixture(directory, **changes)
        return load_export(directory, verify_pinned=False)

    def test_09_all_source_encodings_reconstruct_bytes(self) -> None:
        cases = [("abc", "ascii", b"abc"), ("\u00c3\u00a9", "utf8", b"\xc3\xa9"), ("\u00e9", "latin1", b"\xe9")]
        for body, encoding, expected in cases:
            with self.subTest(encoding=encoding):
                export = self.load(revisions=[revision_row(body, encoding)])
                self.assertEqual(export.revisions[0].source_body_bytes, expected)

    def test_10_all_timestamp_fields_stay_distinct(self) -> None:
        revision = self.load().revisions[0]
        self.assertEqual(
            [revision.time.raw, revision.request_time.raw, revision.success_time.raw,
             revision.recent_changes_time.raw, revision.write_date.raw, revision.archived_at.raw],
            [f"2026-01-01T00:00:0{n}Z" for n in range(1, 7)],
        )

    def test_11_checksum_mismatch_fails_before_loading(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name)
        write_fixture(directory)
        with self.assertRaisesRegex(ValidationError, r"pages\.jsonl: SHA-256 mismatch; expected .* observed"):
            load_export(directory)

    def test_12_malformed_json_fails_with_file_and_row(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name)
        write_fixture(directory)
        (directory / "events.jsonl").write_text("{bad json}\n", encoding="utf-8")
        with self.assertRaisesRegex(ValidationError, r"events\.jsonl:1: invalid JSON"):
            load_export(directory, verify_pinned=False)

    def test_13_unexpected_schema_and_types_fail(self) -> None:
        bad_page = page_row()
        bad_page["invented"] = None
        with self.assertRaisesRegex(ValidationError, r"extra=\['invented'\]"):
            self.load(pages=[bad_page])
        wrong_type = page_row()
        wrong_type["n_revs"] = True
        with self.assertRaisesRegex(ValidationError, r"n_revs: expected int, observed bool/boolean"):
            self.load(pages=[wrong_type])

    def test_14_body_corruption_fails_loudly(self) -> None:
        bad_len = revision_row()
        bad_len["body_len"] = 99
        with self.assertRaisesRegex(ValidationError, r"body_len: expected 99, reconstructed 3"):
            self.load(revisions=[bad_len])
        bad_hash = revision_row()
        bad_hash["body_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValidationError, r"body_sha256: expected"):
            self.load(revisions=[bad_hash])

    def test_15_duplicate_and_broken_linkage_fail(self) -> None:
        duplicate = deepcopy(page_row())
        with self.assertRaisesRegex(ValidationError, r"duplicate page_id"):
            self.load(pages=[page_row(), duplicate], revisions=[] , events=[])
        broken = save_event()
        broken["revision_ref"] = "missing"
        with self.assertRaisesRegex(ValidationError, r"revision_ref 'missing' does not resolve"):
            self.load(events=[broken])

    def test_16_unresolved_and_misaligned_relations_fail(self) -> None:
        revision = revision_row()
        event = save_event()
        revision["relation_type"] = "first_recreation_of"
        revision["related_event_id"] = ["missing-a", "missing-b"]
        revision["round_id"] = [None]
        event["relation_type"] = "first_recreation_of"
        event["related_event_id"] = ["missing-a", "missing-b"]
        event["round_id"] = [None]
        with self.assertRaisesRegex(ValidationError, r"round_id: expected 2 aligned values, observed 1"):
            self.load(revisions=[revision], events=[event])


if __name__ == "__main__":
    unittest.main()
