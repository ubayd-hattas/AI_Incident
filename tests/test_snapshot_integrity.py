from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

import pytest

from ebe.evaluator import RetainedSnapshot, SnapshotIntegrityError, validate_snapshot
from ebe.storage import Capture, CaptureStore, RetainedBodyObject
from ebe.timeline import HORIZON_START


def _export(*, shared: bool = False):
    store = CaptureStore(None, deduplicate=True, start_time=HORIZON_START)
    store.admit(Capture("dse~A", HORIZON_START + timedelta(seconds=1), 1, b"same"))
    if shared:
        store.admit(Capture("dse~B", HORIZON_START + timedelta(seconds=2), 2, b"same"))
    return store.export_retained(HORIZON_START + timedelta(seconds=3))


def _snapshot(export):
    return RetainedSnapshot.from_collector_result(
        SimpleNamespace(retained_export=export, feed_polls=())
    )


def test_one_packet_declares_and_validates_refcount_one():
    snap = _snapshot(_export())
    assert snap.retained_objects[0].refcount == 1
    validate_snapshot(snap)


def test_shared_body_declares_refcount_two_and_charges_body_once():
    export = _export(shared=True)
    snap = _snapshot(export)
    assert snap.retained_objects[0].refcount == 2
    assert snap.retained_body_bytes == len(b"same")
    assert snap.declared_total_bytes == sum(len(p.packet_bytes) for p in export.packets) + len(b"same")


@pytest.mark.parametrize("declared", [1, 3])
def test_declared_refcount_too_low_or_high_invalidates_snapshot(declared):
    export = _export(shared=True)
    bad_object = replace(export.body_objects[0], refcount=declared)
    with pytest.raises(SnapshotIntegrityError, match="refcount mismatch"):
        _snapshot(replace(export, body_objects=(bad_object,)))


def test_removed_packet_with_stale_refcount_invalidates_snapshot():
    export = _export(shared=True)
    with pytest.raises(SnapshotIntegrityError, match="refcount mismatch"):
        _snapshot(replace(
            export,
            packets=export.packets[:1],
            retained_packet_bytes=len(export.packets[0].packet_bytes),
            total_bytes=len(export.packets[0].packet_bytes) + export.retained_body_bytes,
        ))


def test_hidden_unreferenced_object_invalidates_entire_snapshot():
    export = _export()
    hidden = RetainedBodyObject("hidden", b"secret", "2bb80d537b1da3e38bd30361aa855686bde0ba3a"
        "c8f55f8aa9f9e9c6d491bf", 1)
    with pytest.raises(SnapshotIntegrityError, match="hidden/unreferenced"):
        _snapshot(replace(export, body_objects=export.body_objects + (hidden,),
                          retained_body_bytes=export.retained_body_bytes + len(hidden.body),
                          total_bytes=export.total_bytes + len(hidden.body)))


def test_missing_or_wrong_object_id_is_typed_and_invalidates_all_packets():
    export = _export(shared=True)
    bad = replace(export.packets[1], object_id="wrong-object")
    with pytest.raises(SnapshotIntegrityError, match="missing object"):
        _snapshot(replace(export, packets=(export.packets[0], bad)))


def test_duplicate_request_sequence_is_typed_and_invalidates_snapshot():
    export = _export(shared=True)
    duplicate = replace(export.packets[1], request_seq=export.packets[0].request_seq)
    with pytest.raises(SnapshotIntegrityError, match="duplicate request sequence"):
        _snapshot(replace(export, packets=(export.packets[0], duplicate)))


def test_exact_cap_passes_and_cap_plus_one_fails_without_declared_total():
    snap = _snapshot(_export(shared=True))
    actual = snap.retained_packet_bytes + snap.retained_body_bytes
    validate_snapshot(replace(snap, capacity_bytes=actual, declared_total_bytes=None))
    with pytest.raises(SnapshotIntegrityError, match="exceed cap"):
        validate_snapshot(replace(snap, capacity_bytes=actual - 1, declared_total_bytes=None))


def test_incorrect_declared_total_fails_independently_of_cap():
    snap = _snapshot(_export())
    with pytest.raises(SnapshotIntegrityError, match="declared total"):
        validate_snapshot(replace(snap, declared_total_bytes=snap.declared_total_bytes + 1))

