from pathlib import Path
import pytest
from ebe.x13_runner import synthetic_executor, AuthorizationError, run
from ebe.x13_manifest import configuration_rows
ROOT=Path(__file__).resolve().parents[1]
def test_synthetic_payload_is_explicitly_invented():
    row={"run_id":"0"*64,"block":"F","config":configuration_rows()[0]["config"]}
    assert synthetic_executor(row).payload["fixture"]=="SYNTHETIC_INVENTED"
def test_real_mode_requires_authorization():
    with pytest.raises(AuthorizationError): run(ROOT,mode="real",max_rows=0)

