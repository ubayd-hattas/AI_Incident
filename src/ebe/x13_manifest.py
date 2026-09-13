"""Deterministic FINAL_PRE_X13_DEADLINE_v1 pre-score manifest builder.

This module only describes work.  It never imports the evaluator or runs a
collector, which makes manifest generation safe before Gate 2 authorization.
"""
from __future__ import annotations

import csv
import hashlib
import json
import platform
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

AMENDMENT = "FINAL_PRE_X13_DEADLINE_v1"
RUN_ROOT_NAME = AMENDMENT
DEFAULT_CAP = 1_048_576
DEFAULT_LAG_US = 5_000_000
DEFAULT_DELAY_US = 0
POLL_US = 60_000_000
CHECKPOINT = "2026-07-15T00:00:00Z"


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def phase_us(interval_minutes: int, phase: int) -> int:
    if type(phase) is not int or not 0 <= phase < 60:
        raise ValueError("phase must be j=0..59")
    return phase * interval_minutes * 60_000_000 // 60


def _base(*, policy: str, interval_minutes: int | None = None,
          phase: int | None = None, q: int | None = None, block: str,
          lag_us: int = DEFAULT_LAG_US, delay_us: int = DEFAULT_DELAY_US,
          order: str = "forward", archive: str = "none",
          capacity_bytes: int | None = DEFAULT_CAP) -> dict[str, Any]:
    return {
        "archive": archive, "capacity_bytes": capacity_bytes,
        "checkpoint": CHECKPOINT, "delay_us": delay_us,
        "feed_lag_us": lag_us, "feed_poll_interval_us": POLL_US,
        "interval_us": None if interval_minutes is None else interval_minutes * 60_000_000,
        "order": order, "phase": phase,
        "phase_us": None if phase is None else phase_us(interval_minutes or 0, phase),
        "policy": policy, "q": q,
    }


def _periodic(block: str, policy: str, minutes: int, **kwargs: Any) -> Iterable[dict[str, Any]]:
    for j in range(60):
        yield {"block": block, "config": _base(policy=policy, interval_minutes=minutes,
                                                 phase=j, block=block, **kwargs)}


def configuration_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for policy in ("P", "PD", "PCD"):
        rows.extend(_periodic("L-primary", policy, 15))
    for q in (30, 100, 300):
        rows.append({"block": "L-primary", "config": _base(policy="E", q=q, block="L-primary")})
    for minutes in (5, 60):
        rows.extend(_periodic("L-interval", "PCD", minutes))
    for lag, delay in ((5_000_000, 30_000_000), (60_000_000, 0),
                       (60_000_000, 30_000_000)):
        rows.extend(_periodic("L-latency", "PCD", 15, lag_us=lag, delay_us=delay))
        rows.append({"block": "L-latency", "config": _base(
            policy="E", q=30, block="L-latency", lag_us=lag, delay_us=delay)})
    rows.append({"block": "F", "config": _base(policy="F", block="F")})
    rows.extend(_periodic("R", "PCD-R", 15))
    for policy in ("P", "PD", "PCD"):
        rows.extend(_periodic("O", policy, 15, order="reverse"))
    rows.append({"block": "O", "config": _base(policy="E", q=30, block="O", order="reverse_ties")})
    rows.extend(_periodic("A-live", "PCD", 15, archive="terminal_persistent"))
    rows.append({"block": "A-live", "config": _base(policy="E", q=30, block="A-live", archive="terminal_persistent")})
    rows.append({"block": "A-only", "config": _base(policy="A-only", block="A-only", archive="terminal_persistent")})
    rows.append({"block": "A-only", "config": _base(policy="A-only", block="A-only", archive="terminal_persistent", capacity_bytes=None)})
    if len(rows) != 791:
        raise AssertionError(f"deadline roster arithmetic changed: {len(rows)} != 791")
    return rows


def stable_rescore_families() -> list[dict[str, Any]]:
    rows = list(_periodic("U-stable", "PCD", 15))
    rows.append({"block": "U-stable", "config": _base(policy="E", q=30, block="U-stable")})
    for row in rows:
        row["evaluation_only"] = True
        row["support_mask"] = "conservative_stable"
    assert len(rows) == 61
    return rows


OMITTED_FAMILIES = (
    "July 3 checkpoint", "all live caps except 1 MiB", "Delta1",
    "P/PD at Delta5/60", "q100/q300 outside L-primary", "lag30",
    "delay5", "secondary R/O/A cross-products", "P/PD archive prefixes",
    "archive live rows at other caps", "full nominal-tie trajectory enumeration",
    "full closed +/-u trajectory enumeration/certification",
)


def logical_run_id(row: dict[str, Any], *, source_hash: str, code_commit: str,
                   benchmark_hashes: dict[str, str], mask_hash: str) -> str:
    identity = {"amendment": AMENDMENT, "block": row["block"],
                "config": row["config"], "source_hash": source_hash,
                "code_commit": code_commit, "benchmark_hashes": benchmark_hashes,
                "mask_hash": mask_hash}
    return hashlib.sha256(canonical_json(identity)).hexdigest()


def _git_commit(repo: Path) -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo,
                            capture_output=True, text=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else "UNAVAILABLE"


def _code_state_hash(repo: Path) -> str:
    paths = sorted((repo / "src/ebe").glob("*.py"))
    paths += [repo / "scripts/reproduce_x13.py", repo / "configs/x13_deadline_v1.json"]
    return hashlib.sha256(canonical_json({
        str(path.relative_to(repo)).replace("\\", "/"): sha256_file(path)
        for path in paths if path.exists()})).hexdigest()


def _write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def _hashed_files(repo: Path, paths: Iterable[Path]) -> dict[str, str]:
    return {
        str(path.relative_to(repo)).replace("\\", "/"): sha256_file(path)
        for path in paths
    }


def _aggregate_identity(values: dict[str, str]) -> str:
    return hashlib.sha256(canonical_json(values)).hexdigest()


def generate_manifest(repo: Path, *, mask_path: Path | None = None) -> dict[str, Any]:
    repo = repo.resolve()
    freeze = repo / "runs" / RUN_ROOT_NAME / "freeze"
    freeze.mkdir(parents=True, exist_ok=True)
    annotation_names = ("evidence.jsonl", "occurrences.jsonl", "eligibility.jsonl",
        "splits.json", "adjudication.csv", "context_eligibility.jsonl",
        "context_fragments.jsonl", "context_occurrences.jsonl", "rubric.md",
        "A11_BENCHMARK_SPEC.md")
    benchmark_hashes = {name: sha256_file(repo / "annotations" / name) for name in annotation_names}
    source_files = [repo / "data/raw/export/events.jsonl", repo / "data/raw/export/revisions.jsonl"]
    source_hashes = _hashed_files(repo, source_files)
    source_hash = _aggregate_identity(source_hashes)
    accounting_files = sorted((repo / "tests/fixtures/accounting").glob("*.json"))
    accounting_identity = _aggregate_identity(_hashed_files(repo, accounting_files))
    if mask_path is None:
        mask_path = freeze / "stable_support_intervals.jsonl"
    if not mask_path.exists():
        mask_path.write_bytes(b"")
    mask_hash = sha256_file(mask_path)
    commit = _git_commit(repo)
    rows = configuration_rows()
    csv_rows = []
    for ordinal, row in enumerate(rows, 1):
        run_id = logical_run_id(row, source_hash=source_hash, code_commit=commit,
                                benchmark_hashes=benchmark_hashes, mask_hash=mask_hash)
        csv_rows.append({"ordinal": ordinal, "run_id": run_id, "block": row["block"],
                         "config_json": canonical_json(row["config"]).decode("utf-8")})
    _write_csv(freeze / "configuration_manifest.csv",
               ["ordinal", "run_id", "block", "config_json"], csv_rows)
    omitted = [{"scope_id": f"OMIT-{i:03d}", "family": name,
                "status": "NOT_EXECUTED_SCOPE_AMENDMENT"}
               for i, name in enumerate(OMITTED_FAMILIES, 1)]
    _write_csv(freeze / "omitted_scope.csv", ["scope_id", "family", "status"], omitted)
    bench = {"benchmark_id": "A11", "counts": {"propositions": 65, "critical": 57,
             "held_out": 27, "held_out_critical": 23, "groups": 25,
             "core_occurrences": 1421, "context_definitions": 10,
             "context_body_occurrences": 101}, "hashes": benchmark_hashes}
    (freeze / "benchmark_manifest.json").write_bytes(canonical_json(bench) + b"\n")
    manifest = {"amendment": AMENDMENT, "authorization": "GATE_1_ONLY",
        "benchmark_hashes": benchmark_hashes, "code_commit": commit,
        "code_state_sha256": _code_state_hash(repo),
        "collection_row_count": len(rows), "configuration_sha256": sha256_file(freeze / "configuration_manifest.csv"),
        "environment": {"implementation": platform.python_implementation(), "python": platform.python_version(),
                        "platform": platform.platform()},
        "mask_sha256": mask_hash, "omitted_scope_count": len(omitted),
        "omitted_scope_sha256": sha256_file(freeze / "omitted_scope.csv"),
        "source_hash": source_hash, "source_hashes": source_hashes,
        "accounting_fixture_identity": accounting_identity,
        "configuration_recipe_sha256": sha256_file(repo / "configs/x13_deadline_v1.json"),
        "stable_rescore_family_count": len(stable_rescore_families())}
    run_manifest = freeze / "run_manifest.json"
    run_manifest.write_bytes(canonical_json(manifest) + b"\n")
    digest = sha256_file(run_manifest)
    (freeze / "manifest.sha256").write_text(f"{digest}  run_manifest.json\n", encoding="ascii", newline="\n")
    return {**manifest, "manifest_sha256": digest}


def validate_manifest(repo: Path) -> dict[str, Any]:
    repo = repo.resolve()
    freeze = repo / "runs" / RUN_ROOT_NAME / "freeze"
    manifest = json.loads((freeze / "run_manifest.json").read_text(encoding="utf-8"))
    if manifest["collection_row_count"] != 791 or manifest["stable_rescore_family_count"] != 61:
        raise ValueError("manifest row arithmetic is not frozen 791 + 61")
    expected = (freeze / "manifest.sha256").read_text(encoding="ascii").split()[0]
    actual = sha256_file(freeze / "run_manifest.json")
    if expected != actual:
        raise ValueError("run manifest hash mismatch")
    if manifest.get("code_state_sha256") != _code_state_hash(repo):
        raise ValueError("code state differs from frozen manifest")
    if manifest.get("mask_sha256") != sha256_file(freeze / "stable_support_intervals.jsonl"):
        raise ValueError("stable support mask hash mismatch")
    if manifest.get("configuration_sha256") != sha256_file(freeze / "configuration_manifest.csv"):
        raise ValueError("configuration manifest content hash mismatch")
    if manifest.get("omitted_scope_sha256") != sha256_file(freeze / "omitted_scope.csv"):
        raise ValueError("omitted scope content hash mismatch")
    for name, expected_hash in manifest.get("benchmark_hashes", {}).items():
        if sha256_file(repo / "annotations" / name) != expected_hash:
            raise ValueError(f"benchmark hash mismatch: {name}")
    source_hashes = manifest.get("source_hashes")
    if not isinstance(source_hashes, dict) or not source_hashes:
        raise ValueError("manifest lacks frozen source hashes")
    current_source_hashes: dict[str, str] = {}
    for relative, expected_hash in source_hashes.items():
        path = repo / relative
        actual_hash = sha256_file(path)
        if actual_hash != expected_hash:
            raise ValueError(f"source hash mismatch: {relative}")
        current_source_hashes[relative] = actual_hash
    if manifest.get("source_hash") != _aggregate_identity(current_source_hashes):
        raise ValueError("aggregate source identity mismatch")
    accounting_files = sorted((repo / "tests/fixtures/accounting").glob("*.json"))
    accounting_identity = _aggregate_identity(_hashed_files(repo, accounting_files))
    if manifest.get("accounting_fixture_identity") != accounting_identity:
        raise ValueError("accounting fixture identity mismatch")
    if manifest.get("configuration_recipe_sha256") != sha256_file(repo / "configs/x13_deadline_v1.json"):
        raise ValueError("configuration recipe hash mismatch")
    with (freeze / "configuration_manifest.csv").open(encoding="utf-8", newline="") as stream:
        if sum(1 for _ in csv.DictReader(stream)) != 791:
            raise ValueError("configuration manifest does not contain 791 rows")
    return manifest


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    print(json.dumps(generate_manifest(root), indent=2, sort_keys=True))
