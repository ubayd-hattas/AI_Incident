from pathlib import Path
from ebe.x13_manifest import configuration_rows, stable_rescore_families, phase_us, validate_manifest

ROOT=Path(__file__).resolve().parents[1]
def test_exact_roster_arithmetic_and_blocks():
    rows=configuration_rows()
    assert len(rows)==791
    assert {r["block"] for r in rows}=={"L-primary","L-interval","L-latency","F","R","O","A-live","A-only"}
    assert len(stable_rescore_families())==61
def test_phase_formula_and_nulls():
    assert phase_us(15,59)==885_000_000
    assert next(r for r in configuration_rows() if r["config"]["policy"]=="E")["config"]["phase"] is None
def test_checked_in_manifest_validates():
    assert validate_manifest(ROOT)["collection_row_count"]==791

