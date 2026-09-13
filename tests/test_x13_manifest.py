from pathlib import Path
import pytest
from ebe.x13_manifest import configuration_rows, stable_rescore_families, phase_us, sha256_file, validate_manifest

ROOT=Path(__file__).resolve().parents[1]
def test_exact_roster_arithmetic_and_blocks():
    rows=configuration_rows()
    assert len(rows)==791
    assert {r["block"] for r in rows}=={"L-primary","L-interval","L-latency","F","R","O","A-live","A-only"}
    assert len(stable_rescore_families())==61
def test_phase_formula_and_nulls():
    assert phase_us(15,59)==885_000_000
    assert next(r for r in configuration_rows() if r["config"]["policy"]=="E")["config"]["phase"] is None
def test_historical_manifest_preserved_but_rejects_changed_code():
    # Never regenerate the failed-run freeze to make a current-code test pass.
    historical = ROOT / "runs/FINAL_PRE_X13_DEADLINE_v1/freeze/run_manifest.json"
    # This checkout's starting HEAD differs from cc37a14's reported manifest.
    # Pin the actual starting artifact; disclose the discrepancy, never rewrite.
    assert sha256_file(historical) == (
        "5ac8b2a7cbda11710d03c597a88ad30dc38ffa3bb9434ffa9a1656e455ea14c5")
    with pytest.raises(ValueError, match="code state differs from frozen manifest"):
        validate_manifest(ROOT)

