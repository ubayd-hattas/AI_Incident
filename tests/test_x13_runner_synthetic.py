from pathlib import Path
import pytest
import json
from ebe.x13_runner import (LOGICAL_RESULT_FIELDS, _serialize_with_artifact_size,
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
def test_real_mode_requires_authorization():
    with pytest.raises(AuthorizationError): run(ROOT,mode="real",max_rows=0)
