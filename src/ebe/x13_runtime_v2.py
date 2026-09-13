"""Data-only expansion of the BLOCKED runtime-scope candidate, not a runner.

Coordinate IDs here are not authorized execution IDs. No collector, evaluator,
source export or annotation is loaded to choose or partition roster coordinates.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

AMENDMENT = "FINAL_X13_RUNTIME_v2"
CONFIG_PATH = Path(__file__).resolve().parents[2] / "configs/x13_runtime_v2.json"
PRIMARY_PHASES = list(range(60))
DIAGNOSTIC_PHASES = list(range(0, 60, 5))


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def load_roster(path: Path = CONFIG_PATH) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("amendment") != AMENDMENT:
        raise ValueError("not the FINAL_X13_RUNTIME_v2 candidate")
    if value.get("status") != "BLOCKED_NOT_FROZEN":
        raise ValueError("this draft reader cannot certify an executable freeze")
    if value.get("authorization", {}).get("real_scoring") is not False:
        raise ValueError("draft cannot authorize scoring")
    if value["phase_sets"] != {"primary_all_60": PRIMARY_PHASES,
                                "diagnostic_spaced_12": DIAGNOSTIC_PHASES}:
        raise ValueError("candidate phase sets changed")
    if (value["expected_collection_rows"], value["expected_stable_rescore_families"],
            value["expected_omitted_v1_rows"]) != (130, 61, 661):
        raise ValueError("candidate arithmetic changed")
    if sum(item["v1_rows"] for item in value["omissions"]) != 661:
        raise ValueError("omission arithmetic changed")
    if any(item["reason_code"] != "NOT_EXECUTED_RUNTIME_AMENDMENT"
           for item in value["omissions"]):
        raise ValueError("runtime omissions need distinct reasons")
    if value["historical_omissions"]["reason_code"] != "NOT_EXECUTED_SCOPE_AMENDMENT":
        raise ValueError("historical reasons must not be rewritten")
    return value


def require_executable(path: Path = CONFIG_PATH) -> None:
    load_roster(path)
    raise ValueError("RUNTIME AMENDMENT BLOCKED: no executable v2 freeze or authorization")


def _phases(family: dict[str, Any], roster: dict[str, Any]) -> list[int | None]:
    selection = family["phases"]
    phases = ([None] if selection is None else selection if isinstance(selection, list)
              else roster["phase_sets"][selection])
    if family["rows"] != len(phases) or len(set(phases)) != len(phases):
        raise ValueError("family phase arithmetic or uniqueness mismatch")
    if any(p is not None and (type(p) is not int or not 0 <= p < 60) for p in phases):
        raise ValueError("phase must be an integer j=0..59")
    return phases


def collection_rows(path: Path = CONFIG_PATH) -> list[dict[str, Any]]:
    roster = load_roster(path)
    rows = []
    family_ids = [f["id"] for f in roster["collection_families"]]
    if len(set(family_ids)) != len(family_ids):
        raise ValueError("duplicate family ID")
    for family in roster["collection_families"]:
        for phase in _phases(family, roster):
            config = {key: family[key] for key in (
                "policy", "interval_minutes", "q", "lag_us", "delay_us", "cap",
                "archive", "order", "checkpoint")}
            config["phase"] = phase
            config["phase_us"] = (None if phase is None else
                                  phase * family["interval_minutes"] * 60_000_000 // 60)
            config["feed_poll_interval_us"] = roster["feed_poll_interval_us"]
            config["horizon_start"] = roster["horizon_start"]
            identity = {"amendment": AMENDMENT, "family": family["id"], "config": config}
            rows.append({"id": hashlib.sha256(canonical_json(identity)).hexdigest(),
                         "family": family["id"], "reason_code": family["reason_code"],
                         "config": config})
    if len(rows) != 130:
        raise ValueError("collection roster count differs from candidate")
    if len({canonical_json(r["config"]) for r in rows}) != len(rows):
        raise ValueError("duplicate scientific coordinates")
    return rows


def stable_rows(path: Path = CONFIG_PATH) -> list[dict[str, Any]]:
    roster = load_roster(path)
    available = {(r["family"], r["config"]["phase"]): r for r in collection_rows(path)}
    rows = []
    for family in roster["stable_rescore_families"]:
        for phase in _phases(family, roster):
            key = family["source_family"], phase
            if key not in available:
                raise ValueError("stable family has no collection source")
            rows.append({"family": family["id"], "source_family": key[0],
                         "phase": phase, "source_coordinate_id": available[key]["id"],
                         "reason_code": family["reason_code"], "evaluation_only": True})
    expected = {("PRIMARY_PCD15", j) for j in range(60)} | {("PRIMARY_E30", None)}
    if len(rows) != 61 or {(r["source_family"], r["phase"]) for r in rows} != expected:
        raise ValueError("stable roster must cover every primary snapshot exactly once")
    return rows


def v1_partition(path: Path = CONFIG_PATH) -> dict[str, Any]:
    """Partition all791 old coordinates; never read a historical run artifact."""
    from .x13_manifest import OMITTED_FAMILIES, configuration_rows

    roster = load_roster(path)
    if tuple(roster["historical_omissions"]["families"]) != OMITTED_FAMILIES:
        raise ValueError("historical scope omissions changed")
    selected = {}
    for row in collection_rows(path):
        value = row["config"]
        old_config = {
            "archive": "terminal_persistent" if value["archive"] else "none",
            "capacity_bytes": value["cap"], "checkpoint": value["checkpoint"],
            "delay_us": value["delay_us"], "feed_lag_us": value["lag_us"],
            "feed_poll_interval_us": value["feed_poll_interval_us"],
            "interval_us": (None if value["interval_minutes"] is None else
                            value["interval_minutes"] * 60_000_000),
            "order": value["order"], "phase": value["phase"],
            "phase_us": value["phase_us"], "policy": value["policy"], "q": value["q"],
        }
        selected[canonical_json(old_config)] = row["id"]
    retained, omitted = [], []
    for row in configuration_rows():
        key = canonical_json(row["config"])
        if key in selected:
            retained.append({**row, "v2_coordinate_id": selected.pop(key)})
        else:
            cfg = row["config"]
            index = (0 if cfg["policy"] in {"P", "PD"} else
                     {"R": 1, "L-latency": 2, "L-interval": 3, "O": 4, "A-live": 5}[row["block"]])
            disposition = roster["omissions"][index]
            omitted.append({**row, "omission_family": disposition["family"],
                            "reason_code": disposition["reason_code"]})
    if selected or len(retained) != 130 or len(omitted) != 661:
        raise ValueError("candidate is not an exact130/661 partition of v1")
    for item in roster["omissions"]:
        if sum(r["omission_family"] == item["family"] for r in omitted) != item["v1_rows"]:
            raise ValueError("omission family arithmetic differs from actual coordinates")
    return {"retained": retained, "omitted": omitted}
