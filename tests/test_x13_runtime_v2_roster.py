"""Coordinate-only tests: no source export, benchmark or evidence scoring."""
import json
from collections import Counter
from pathlib import Path

import pytest

from ebe.x13_runtime_v2 import (CONFIG_PATH, canonical_json, collection_rows,
                               load_roster, require_executable, stable_rows,
                               v1_partition)

DIAGNOSTIC = list(range(0, 60, 5))
EXPECTED = {
    "PRIMARY_PCD15": ("PCD", 15, None, list(range(60)), 5, 0, False, "forward", 1048576),
    "PRIMARY_E30": ("E", None, 30, [None], 5, 0, False, "forward", 1048576),
    "FINAL_STATE_F": ("F", None, None, [None], 5, 0, False, "forward", 1048576),
    "PCD_R15_PHASE0_DIAGNOSTIC": ("PCD-R", 15, None, [0], 5, 0, False, "forward", 1048576),
    "INTERVAL_PCD5": ("PCD", 5, None, DIAGNOSTIC, 5, 0, False, "forward", 1048576),
    "INTERVAL_PCD60": ("PCD", 60, None, DIAGNOSTIC, 5, 0, False, "forward", 1048576),
    "LATENCY_PCD15_L60_D30": ("PCD", 15, None, DIAGNOSTIC, 60, 30, False, "forward", 1048576),
    "LATENCY_E30_L60_D30": ("E", None, 30, [None], 60, 30, False, "forward", 1048576),
    "REVERSE_PCD15": ("PCD", 15, None, DIAGNOSTIC, 5, 0, False, "reverse", 1048576),
    "REVERSE_E30": ("E", None, 30, [None], 5, 0, False, "reverse_ties", 1048576),
    "ARCHIVE_PCD15": ("PCD", 15, None, DIAGNOSTIC, 5, 0, True, "forward", 1048576),
    "ARCHIVE_E30": ("E", None, 30, [None], 5, 0, True, "forward", 1048576),
    "ARCHIVE_ONLY_CAPPED": ("A-only", None, None, [None], 5, 0, True, "forward", 1048576),
    "ARCHIVE_ONLY_UNCAPPED": ("A-only", None, None, [None], 5, 0, True, "forward", None),
    "SECONDARY_E100": ("E", None, 100, [None], 5, 0, False, "forward", 1048576),
    "SECONDARY_E300": ("E", None, 300, [None], 5, 0, False, "forward", 1048576),
}


def test_exact_candidate_coordinates_no_hidden_extra_rows():
    rows = collection_rows()
    assert len(rows) == 130
    assert Counter(r["family"] for r in rows) == Counter({k: len(v[3]) for k, v in EXPECTED.items()})
    for family, settings in EXPECTED.items():
        policy, interval, q, phases, lag, delay, archive, order, cap = settings
        actual = [r["config"] for r in rows if r["family"] == family]
        assert [r["phase"] for r in actual] == phases
        for r in actual:
            assert (r["policy"], r["interval_minutes"], r["q"], r["lag_us"],
                    r["delay_us"], r["archive"], r["order"], r["cap"]) == (
                        policy, interval, q, lag*1_000_000, delay*1_000_000, archive, order, cap)
            assert r["phase_us"] == (None if r["phase"] is None else r["phase"]*interval*1_000_000)
            assert r["checkpoint"] == "2026-07-15T00:00:00Z"
            assert r["horizon_start"] == "2026-05-24T00:00:00Z"
            assert r["feed_poll_interval_us"] == 60_000_000
    assert not any(r["config"]["policy"] in {"P", "PD"} for r in rows)
    assert len({r["id"] for r in rows}) == 130
    assert len({canonical_json(r["config"]) for r in rows}) == 130
    assert rows == collection_rows()


def test_all_61_stable_sources_are_exact_primary_coordinates():
    stable = stable_rows()
    primary = {r["id"] for r in collection_rows() if r["family"] in {"PRIMARY_PCD15", "PRIMARY_E30"}}
    assert len(stable) == 61
    assert {r["source_coordinate_id"] for r in stable} == primary
    assert all(r["evaluation_only"] for r in stable)


def test_all_791_v1_rows_partition_with_distinct_historical_reasons():
    partition = v1_partition()
    assert len(partition["retained"]) == 130
    assert len(partition["omitted"]) == 661
    assert all(r["reason_code"] == "NOT_EXECUTED_RUNTIME_AMENDMENT" for r in partition["omitted"])
    assert Counter(r["block"] for r in partition["omitted"]) == {
        "L-primary": 120, "L-interval": 96, "L-latency": 170,
        "R": 59, "O": 168, "A-live": 48,
    }
    assert load_roster()["historical_omissions"]["reason_code"] == "NOT_EXECUTED_SCOPE_AMENDMENT"
    assert not any(r["config"]["policy"] == "F" for r in partition["omitted"])


def test_expansion_reads_only_config_not_annotation_or_evidence(monkeypatch):
    # Import the old coordinate generator before guarding data reads. No census,
    # collector or evaluator is called by the partition operation.
    from ebe import x13_manifest  # noqa: F401
    text = CONFIG_PATH.read_text(encoding="utf-8")
    def guarded_read(path, *args, **kwargs):
        assert path.resolve() == CONFIG_PATH.resolve(), f"forbidden data read: {path}"
        return text
    def reject(*args, **kwargs):
        raise AssertionError("candidate expansion must not read arbitrary files")
    monkeypatch.setattr(Path, "read_text", guarded_read)
    monkeypatch.setattr(Path, "read_bytes", reject)
    monkeypatch.setattr("builtins.open", reject)
    monkeypatch.setattr("io.open", reject)
    assert len(collection_rows()) == 130
    assert len(stable_rows()) == 61
    assert len(v1_partition()["omitted"]) == 661


@pytest.mark.parametrize("mutation", ["phase", "count", "authorize", "stable", "duplicate"])
def test_mutated_candidate_rejected(tmp_path, mutation):
    value = load_roster()
    if mutation == "phase": value["phase_sets"]["primary_all_60"][0] = 1
    if mutation == "count": value["expected_collection_rows"] = 131
    if mutation == "authorize": value["authorization"]["real_scoring"] = True
    if mutation == "stable": value["stable_rescore_families"][0]["source_family"] = "INTERVAL_PCD5"
    if mutation == "duplicate": value["collection_families"].append(value["collection_families"][0])
    path = tmp_path / "candidate.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError):
        stable_rows(path)


def test_draft_cannot_be_treated_as_an_executable_freeze():
    assert load_roster()["status"] == "BLOCKED_NOT_FROZEN"
    with pytest.raises(ValueError, match="RUNTIME AMENDMENT BLOCKED"):
        require_executable()
