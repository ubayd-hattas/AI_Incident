from __future__ import annotations

import json
import sys
import unittest
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ebe.accounting import MICROSECONDS_PER_HOUR, canonical_array, canonical_jsonl  # noqa: E402
from ebe.storage import Capture, CaptureStore  # noqa: E402


FIXTURES = ROOT / "tests" / "fixtures" / "accounting"


def dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def capture_from_packet(packet_text: str, body_hex: str) -> Capture:
    packet = json.loads(packet_text)
    return Capture(
        packet["page_key"], dt(packet["capture_time"]), packet["request_seq"], bytes.fromhex(body_hex)
    )


class AccountingFixtureTests(unittest.TestCase):
    def test_A_feed_serialization(self) -> None:
        fixture = load("A_feed.json")
        record = fixture["record"]
        encoded = canonical_jsonl(record)
        self.assertEqual(encoded, fixture["canonical_record"].encode())
        self.assertEqual(len(encoded), fixture["expected"]["record_bytes"])
        response = canonical_array([record])
        self.assertEqual(response, fixture["canonical_response"].encode())
        self.assertEqual(len(response), fixture["expected"]["downloaded_metadata_bytes"])
        self.assertEqual(len(canonical_array([])), 3)
        self.assertEqual(
            len(canonical_array([record, record])),
            fixture["expected"]["two_identical_records_response_bytes"],
        )

    def test_B_unique_exact_cap_and_byte_hours(self) -> None:
        fixture = load("B_unique.json")
        capture = Capture(
            fixture["packet"]["page_key"], dt(fixture["packet"]["capture_time"]),
            fixture["packet"]["request_seq"], bytes.fromhex(fixture["body_utf8_hex"]),
        )
        self.assertEqual(capture.packet_bytes, fixture["canonical_packet"].encode())
        store = CaptureStore(fixture["capacity_bytes"], deduplicate=True, start_time=capture.capture_time)
        result = store.admit(capture)
        snap = store.snapshot(dt(fixture["checkpoint"]))
        self.assertEqual(result.disposition, "admitted")
        self.assertEqual(store.size_history, tuple(fixture["expected"]["store_bytes_after_operations"]))
        self.assertEqual(snap.final_store_bytes, fixture["expected"]["final_store_bytes"])
        self.assertEqual(snap.peak_store_bytes, fixture["expected"]["peak_store_bytes"])
        self.assertEqual(snap.store_byte_hours, fixture["expected"]["store_byte_hours"])

    def _run_sequence(self, fixture_name: str) -> tuple[dict, CaptureStore, list]:
        fixture = load(fixture_name)
        packets = fixture["canonical_packets"]
        body_hexes = fixture.get("body_utf8_hex_in_request_order")
        if body_hexes is None:
            body_hexes = [fixture["body_utf8_hex"]] * len(packets)
        captures = [capture_from_packet(packet, body) for packet, body in zip(packets, body_hexes)]
        store = CaptureStore(
            fixture["capacity_bytes"], deduplicate=fixture["deduplicate"],
            start_time=captures[0].capture_time,
        )
        results = [store.admit(capture) for capture in captures]
        return fixture, store, results

    def test_C_exact_deduplication(self) -> None:
        fixture, store, results = self._run_sequence("C_duplicate.json")
        snap = store.snapshot(dt(fixture["checkpoint"]))
        self.assertEqual([item.marginal_bytes for item in results], fixture["expected"]["marginal_admission_bytes"])
        self.assertEqual(snap.retained_body_objects, 1)
        self.assertEqual(snap.object_reference_counts, (2,))
        self.assertEqual(snap.final_store_bytes, 328)
        self.assertEqual(snap.store_byte_hours, 493)

    def test_D_non_deduplicated_repeated_body(self) -> None:
        fixture, store, results = self._run_sequence("D_nondedup.json")
        snap = store.snapshot(dt(fixture["checkpoint"]))
        self.assertEqual([item.marginal_bytes for item in results], fixture["expected"]["marginal_admission_bytes"])
        self.assertEqual(snap.retained_body_objects, 2)
        self.assertEqual(snap.object_reference_counts, (1, 1))
        self.assertEqual(snap.retained_body_bytes, 4)
        self.assertEqual(snap.final_store_bytes, 330)

    def test_E_fifo_final_reference_and_no_hidden_cache(self) -> None:
        fixture, store, results = self._run_sequence("E_fifo.json")
        snap = store.snapshot(dt(fixture["checkpoint"]))
        self.assertEqual(store.size_history, tuple(fixture["expected"]["store_bytes_after_operations"]))
        self.assertEqual(results[-1].evicted_request_seqs, (1, 2))
        self.assertEqual(snap.evicted_packet_bytes, 326)
        self.assertEqual(snap.evicted_body_bytes, 2)
        self.assertEqual(snap.retained_request_seqs, (3,))
        self.assertEqual(snap.peak_store_bytes, 328)
        self.assertEqual(snap.final_store_bytes, 165)
        self.assertEqual(snap.store_byte_hours, 658)
        with self.assertRaises(KeyError):
            store.body_for_capture(1)

    def test_F_oversize_rejected_before_eviction(self) -> None:
        fixture, store, results = self._run_sequence("F_oversize.json")
        snap = store.snapshot(dt(fixture["checkpoint"]))
        self.assertEqual([item.disposition for item in results], fixture["expected"]["admission_results"])
        self.assertEqual(results[-1].evicted_request_seqs, ())
        self.assertEqual(snap.retained_request_seqs, (1,))
        self.assertEqual(snap.rejected_oversize_packets, 1)
        self.assertEqual(snap.bytes_evicted, 0)
        self.assertEqual(snap.final_store_bytes, 165)

    def test_G_shared_body_survives_until_last_reference(self) -> None:
        fixture, store, results = self._run_sequence("G_shared_fifo.json")
        snap = store.snapshot(dt(fixture["checkpoint"]))
        self.assertEqual(results[-1].evicted_request_seqs, (1,))
        self.assertEqual(snap.evicted_body_bytes, 0)
        self.assertEqual(snap.retained_request_seqs, (2, 3))
        self.assertEqual(snap.object_reference_counts, (2,))
        self.assertEqual(store.body_for_capture(2), store.body_for_capture(3))
        self.assertEqual(snap.store_byte_hours, 821)

    def test_H_protocol_headers_and_directory_arrays(self) -> None:
        fixture = load("H_protocol.json")
        header_total = 0
        unknown = 0
        for row in fixture["body_responses"]:
            header = canonical_jsonl({"outcome": row["outcome"]})
            self.assertEqual(header, row["canonical_header"].encode())
            self.assertEqual(len(header), row["header_bytes"])
            header_total += len(header)
            unknown += row["body_bytes"] is None
        self.assertEqual(header_total, fixture["expected_response_totals"]["downloaded_metadata_bytes"])
        self.assertEqual(unknown, fixture["expected_response_totals"]["unknown_body_byte_attempts"])
        for case in fixture["directory_cases_independent_of_each_other"]:
            response = canonical_array(case["page_keys"])
            self.assertEqual(response, case["canonical_response"].encode())
            self.assertEqual(len(response), case["downloaded_metadata_bytes"])

    def test_I_encoding_non_ascii_empty_and_escaping(self) -> None:
        fixture = load("I_encoding.json")
        for case in fixture["source_cases"]:
            source = bytes.fromhex(case["source_hex"])
            codec = "latin-1" if case["encoding"] == "latin-1" else case["encoding"]
            canonical = source.decode(codec).encode("utf-8")
            self.assertEqual(canonical.hex(), case["canonical_utf8_hex"])
            self.assertEqual(len(canonical), case["canonical_body_bytes"])
            self.assertEqual(sha256(canonical).hexdigest(), case["canonical_sha256"])
        metadata = canonical_jsonl(fixture["generic_metadata_value_not_a_feed_or_packet"])
        self.assertEqual(metadata, fixture["canonical_generic_metadata"].encode())
        self.assertEqual(len(metadata), fixture["expected_generic_metadata_bytes"])
        packet = json.loads(fixture["canonical_packet_width_probe"])
        self.assertEqual(len(canonical_jsonl(packet)), fixture["expected_packet_width_probe_bytes"])

    def test_cap_never_exceeded_at_any_committed_operation(self) -> None:
        fixture, store, _ = self._run_sequence("E_fifo.json")
        self.assertTrue(all(size <= fixture["capacity_bytes"] for size in store.size_history))

    def test_zero_capacity_rejects_without_truncation(self) -> None:
        when = dt("2026-05-24T00:00:00Z")
        store = CaptureStore(0, deduplicate=True, start_time=when)
        result = store.admit(Capture("dse~A", when, 1, b""))
        self.assertEqual(result.disposition, "oversize")
        self.assertEqual(store.snapshot().final_store_bytes, 0)

    def test_same_time_order_is_request_sequence_then_key(self) -> None:
        when = dt("2026-05-24T00:00:00Z")
        store = CaptureStore(None, deduplicate=True, start_time=when)
        store.admit(Capture("dse~Z", when, 1, b"one"))
        store.admit(Capture("dse~A", when, 2, b"two"))
        self.assertEqual(store.snapshot().retained_request_seqs, (1, 2))

    def test_byte_microseconds_are_exact_integer_arithmetic(self) -> None:
        fixture = load("B_unique.json")
        packet = fixture["packet"]
        capture = Capture(
            packet["page_key"], dt(packet["capture_time"]), packet["request_seq"],
            bytes.fromhex(fixture["body_utf8_hex"]),
        )
        store = CaptureStore(
            fixture["capacity_bytes"], deduplicate=True, start_time=capture.capture_time
        )
        store.admit(capture)
        snap = store.snapshot(dt(fixture["checkpoint"]))
        self.assertEqual(snap.store_byte_microseconds, 165 * MICROSECONDS_PER_HOUR)


if __name__ == "__main__":
    unittest.main()
