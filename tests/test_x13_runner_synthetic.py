from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest
import json
from ebe.accounting import synchronized_accounting
from ebe.x13_runner import (LOGICAL_RESULT_FIELDS, _collector_aux_bytes,
                            _combined_points, _serialize_with_artifact_size,
                            synthetic_executor, AuthorizationError, run)
from ebe.x13_manifest import configuration_rows
ROOT=Path(__file__).resolve().parents[1]
def test_synthetic_payload_is_explicitly_invented():
    row={"run_id":"0"*64,"block":"F","config":configuration_rows()[0]["config"]}
    assert synthetic_executor(row).payload["fixture"]=="SYNTHETIC_INVENTED"
def test_all_required_overhead_fields_are_explicit_before_materialization():
    row={"run_id":"0"*64,"block":"F","config":configuration_rows()[0]["config"]}
    payload=synthetic_executor(row).payload
    required={"synchronized_peak_s_plus_m","combined_byte_microseconds","elapsed_seconds",
        "cpu_seconds","rss_bytes","artifact_disk_bytes","aux_collector_bytes","aux_store_bytes",
        "aux_evaluator_bytes","pending_index_peak","queue_peak","coalesced_updates",
        "starvation_events","dropped_work","reused_from","feed_metadata_bytes",
        "directory_metadata_bytes"}
    assert required <= set(LOGICAL_RESULT_FIELDS)
    assert all(payload[name] is not None for name in required)
def test_artifact_disk_bytes_matches_materialized_json_size():
    result={"result":{"artifact_disk_bytes":"NA_PENDING_ARTIFACT_MATERIALIZATION"},"run_id":"x"}
    encoded=_serialize_with_artifact_size(result)
    decoded=json.loads(encoded)
    assert decoded["result"]["artifact_disk_bytes"] == len(encoded)
def test_runner_merges_real_ledgers_through_verified_synchronized_accounting():
    start=datetime(2026,5,24,tzinfo=timezone.utc)
    points=_combined_points(
        [(start,0),(start+timedelta(seconds=1),100),(start+timedelta(seconds=3),20)],
        [(start,0),(start+timedelta(seconds=2),50)],
    )
    combined=synchronized_accounting(points,start+timedelta(seconds=4))
    assert combined.synchronized_peak_s_plus_m == 150
    assert combined.s_byte_microseconds == 220_000_000
    assert combined.m_byte_microseconds == 100_000_000
    assert combined.combined_byte_microseconds == 320_000_000
def test_measured_pcdr_repair_metadata_populates_collector_aux_memory():
    assert _collector_aux_bytes(SimpleNamespace(repair_metadata_peak_bytes=123)) == 123
    assert isinstance(_collector_aux_bytes(SimpleNamespace(repair_metadata_peak_bytes=None)),str)
def test_real_mode_requires_authorization(monkeypatch, tmp_path):
    # Isolate the authorization gate from the deliberately stale historical
    # manifest. Do not generate source/annotation freezes or an auth artifact.
    from ebe import x13_runner
    monkeypatch.setattr(x13_runner, "validate_manifest", lambda repo: {"source_hash": "invented"})
    monkeypatch.setattr(x13_runner, "sha256_file", lambda path: "0" * 64)
    def forbidden(*args, **kwargs):
        raise AssertionError("real executor must not be constructed before authorization")
    monkeypatch.setattr(x13_runner, "_make_real_executor", forbidden)
    with pytest.raises(AuthorizationError): run(tmp_path,mode="real",max_rows=0)
    assert not list(tmp_path.iterdir())
