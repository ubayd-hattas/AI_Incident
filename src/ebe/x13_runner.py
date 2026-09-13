"""Offline, resumable X13 runner shell with a hard Gate 2 scoring lock."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable, Literal

from .x13_manifest import AMENDMENT, RUN_ROOT_NAME, canonical_json, sha256_file, validate_manifest

RunStatus = Literal["PLANNED", "RUNNING", "COMPLETE", "ERROR", "MISSING", "NOT_EVALUABLE"]
LOGICAL_RESULT_FIELDS = (
    "feed_polls", "directories", "live_body_attempts", "archive_enumerations",
    "archive_request_attempts", "total_attempts", "body", "missing", "unknown",
    "body_unknown", "ambiguous", "unsupported", "pending", "response_header_bytes",
    "feed_metadata_bytes", "directory_metadata_bytes", "archive_metadata_bytes",
    "known_body_downloaded_bytes", "known_lower_bound_bytes", "na_payload_count",
    "final_packet_bytes", "final_body_bytes", "final_s_bytes", "peak_s_bytes",
    "object_count", "packet_count", "refcounts", "evicted_packet_bytes",
    "evicted_object_bytes", "oversize_rejections", "final_m_bytes", "peak_m_bytes",
    "synchronized_peak_s_plus_m", "s_byte_microseconds", "m_byte_microseconds",
    "combined_byte_microseconds", "elapsed_seconds", "cpu_seconds", "rss_bytes",
    "artifact_disk_bytes", "aux_collector_bytes", "aux_store_bytes",
    "aux_evaluator_bytes", "pending_index_peak", "queue_peak", "coalesced_updates",
    "starvation_events", "dropped_work", "reused_from",
    "stable_core_numerator", "stable_core_denominator",
    "stable_context_numerator", "stable_context_denominator",
)


class RunnerError(RuntimeError): pass
class AuthorizationError(RunnerError): pass
class ResumeMismatchError(RunnerError): pass


@dataclass(frozen=True, slots=True)
class RunOutcome:
    status: RunStatus
    payload: dict[str, Any]


def _append(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("ab") as stream:
        stream.write(canonical_json(value) + b"\n")
        stream.flush(); os.fsync(stream.fileno())


def _atomic(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def _authorization(repo: Path, manifest_sha: str, artifact: Path | None) -> None:
    if artifact is None or not artifact.exists():
        raise AuthorizationError("real scoring requires the future independent Gate 2 authorization artifact")
    value = json.loads(artifact.read_text(encoding="utf-8"))
    required = {"amendment": AMENDMENT, "manifest_sha256": manifest_sha,
                "disposition": "GATE_2_PASS", "real_scoring_authorized": True}
    if any(value.get(key) != expected for key, expected in required.items()):
        raise AuthorizationError("Gate 2 artifact does not pin this exact candidate/manifest")
    if not isinstance(value.get("independent_reviewer"), str) or not value["independent_reviewer"]:
        raise AuthorizationError("Gate 2 artifact lacks independent reviewer identity")


def synthetic_executor(row: dict[str, Any]) -> RunOutcome:
    """Invented, label-free fixture output; it never loads source or annotations."""
    seed = int(row["run_id"][:12], 16)
    payload = {name: None for name in LOGICAL_RESULT_FIELDS}
    payload.update({"fixture": "SYNTHETIC_INVENTED", "requests": 1 + seed % 100,
               "retained_bytes": seed % 1_048_577, "coverage_numerator": seed % 24,
               "coverage_denominator": 23, "elapsed_seconds": None, "rss_bytes": None,
               "total_attempts": 1 + seed % 100, "unsupported": 0})
    return RunOutcome("COMPLETE", payload)


def _make_real_executor(repo: Path) -> Callable[[dict[str, Any]], RunOutcome]:
    """Construct the real engine only *after* independent authorization.

    Imports joining collectors to A11 deliberately live behind this function;
    manifest/synthetic operation cannot accidentally score evidence.
    """
    from datetime import datetime
    from .a11_loader import load_a11_benchmark
    from .collectors import (EventDerivedConfig, PeriodicConfig, PeriodicPolicy,
                             run_event_derived, run_periodic)
    from .evaluator import (RetainedBodyRecord, RetainedFeedRecord, RetainedSnapshot,
                            apply_stable_support_mask, evaluate_benchmark)
    from .ingest import load_export
    from .observer import Observer, ObserverConfig
    from .terminal_archive import (augment_collector_result, run_archive_only,
                                   run_final_state_only)
    from .support_masks import load_stable_mask

    export = load_export(repo / "data/raw/export")
    benchmark = load_a11_benchmark(freeze_manifest_path=repo / "runs" / RUN_ROOT_NAME /
                                   "freeze" / "run_manifest.json", fail_on_error=True)
    stable_intervals = load_stable_mask(repo / "runs" / RUN_ROOT_NAME / "freeze" /
                                        "stable_support_intervals.jsonl")
    stable_benchmark = apply_stable_support_mask(benchmark, stable_intervals)

    def snapshot_from_terminal(collection, live_result=None):
        retained = collection.retained
        objects = {x.object_id: x.body for x in retained.body_objects}
        bodies = tuple(RetainedBodyRecord(
            p.page_key, p.capture_time, objects[p.object_id], p.body_sha256,
            p.request_seq, p.packet_bytes, p.object_id, p.archive_key)
            for p in retained.packets)
        feed = () if live_result is None else tuple(
            RetainedFeedRecord(r.page_key, r.action, r.event_time, poll.poll_time)
            for poll in live_result.feed_polls for r in poll.records)
        return RetainedSnapshot(retained.checkpoint, bodies, feed, retained.capacity_bytes,
                                retained.retained_packet_bytes, retained.retained_body_bytes,
                                retained.total_bytes)

    def execute(row: dict[str, Any]) -> RunOutcome:
        cfg = row["config"]
        checkpoint = datetime.fromisoformat(cfg["checkpoint"].replace("Z", "+00:00"))
        observer_cfg = ObserverConfig(cfg["feed_lag_us"], cfg["feed_poll_interval_us"],
                                      cfg["delay_us"])
        policy = cfg["policy"]
        result = None; terminal = None
        if policy in {"P", "PD", "PCD", "PCD-R"}:
            result = run_periodic(Observer(export, config=observer_cfg), PeriodicConfig(
                PeriodicPolicy(policy), cfg["interval_us"], cfg["phase_us"],
                cfg["capacity_bytes"], checkpoint,
                "reverse" if cfg["order"] == "reverse" else "forward"))
        elif policy == "E":
            result = run_event_derived(Observer(export, config=observer_cfg),
                EventDerivedConfig(cfg["q"], cfg["capacity_bytes"], checkpoint,
                                   cfg["order"] == "reverse_ties"))
        elif policy == "F":
            terminal = run_final_state_only(Observer(export, config=observer_cfg),
                                            capacity_bytes=cfg["capacity_bytes"],
                                            checkpoint=checkpoint)
        elif policy == "A-only":
            terminal = run_archive_only(export, capacity_bytes=cfg["capacity_bytes"],
                                        checkpoint=checkpoint)
        else:
            raise RunnerError(f"unsupported frozen policy {policy!r}")
        if cfg["archive"] == "terminal_persistent" and policy not in {"A-only"}:
            if result is None: raise RunnerError("archive augmentation requires live prefix")
            terminal = augment_collector_result(export, result)
        snapshot = (snapshot_from_terminal(terminal, result)
                    if terminal is not None else RetainedSnapshot.from_collector_result(result))
        core = evaluate_benchmark(benchmark, snapshot, split="held_out",
                                  metric="core", critical_only=True)
        context = evaluate_benchmark(benchmark, snapshot, split="held_out",
                                     metric="context", critical_only=True)
        payload = {name: None for name in LOGICAL_RESULT_FIELDS}
        if result is not None:
            oc=result.observer_costs; ss=result.storage_snapshot
            payload.update({"feed_polls":oc.feed_requests,"directories":oc.directory_requests,
                "live_body_attempts":oc.body_requests,"total_attempts":result.requests_made,
                "body":oc.successful_body_responses,"missing":oc.missing_responses,
                "unknown":oc.unknown_responses,"body_unknown":oc.body_unknown_responses,
                "ambiguous":oc.ambiguous_responses,"unsupported":oc.unsupported_responses,
                "pending":oc.pending_body_requests,"response_header_bytes":oc.downloaded_metadata_bytes,
                "known_body_downloaded_bytes":oc.downloaded_known_body_bytes,
                "known_lower_bound_bytes":oc.known_downloaded_byte_lower_bound,
                "na_payload_count":oc.unknown_body_byte_attempts,
                "final_packet_bytes":ss.retained_packet_bytes,"final_body_bytes":ss.retained_body_bytes,
                "final_s_bytes":ss.final_store_bytes,"peak_s_bytes":ss.peak_store_bytes,
                "object_count":ss.retained_body_objects,"packet_count":ss.retained_packets,
                "refcounts":list(ss.object_reference_counts),
                "evicted_packet_bytes":ss.evicted_packet_bytes,
                "evicted_object_bytes":ss.evicted_body_bytes,
                "oversize_rejections":ss.rejected_oversize_packets,
                "final_m_bytes":oc.final_shared_metadata_bytes,"peak_m_bytes":oc.peak_shared_metadata_bytes,
                "s_byte_microseconds":ss.store_byte_microseconds,
                "m_byte_microseconds":oc.shared_metadata_byte_microseconds})
        if terminal is not None:
            payload.update({"archive_enumerations":terminal.archive_enumerations,
                "archive_request_attempts":len(terminal.attempts),
                "archive_metadata_bytes":terminal.metadata_bytes,
                "known_body_downloaded_bytes":terminal.known_body_bytes,
                "final_packet_bytes":terminal.retained.retained_packet_bytes,
                "final_body_bytes":terminal.retained.retained_body_bytes,
                "final_s_bytes":terminal.retained.total_bytes,
                "peak_s_bytes":terminal.retained.peak_bytes})
        payload.update({"core_numerator":core.numerator,"core_denominator":core.denominator,
                        "context_numerator":context.numerator,
                        "context_denominator":context.denominator,
                        "context_lower_numerator":context.lower_context_numerator,
                        "context_upper_numerator":context.upper_context_numerator})
        is_primary_stable_family = (
            row["block"] == "L-primary"
            and ((policy == "PCD" and cfg["interval_us"] == 900_000_000)
                 or (policy == "E" and cfg["q"] == 30))
        )
        if is_primary_stable_family:
            stable_snapshot = replace(snapshot, stable_support_intervals=stable_intervals)
            stable_core = evaluate_benchmark(stable_benchmark, stable_snapshot,
                split="held_out", metric="core", critical_only=True)
            stable_context = evaluate_benchmark(stable_benchmark, stable_snapshot,
                split="held_out", metric="context", critical_only=True)
            payload.update({"stable_core_numerator":stable_core.numerator,
                "stable_core_denominator":stable_core.denominator,
                "stable_context_numerator":stable_context.numerator,
                "stable_context_denominator":stable_context.denominator})
        return RunOutcome("NOT_EVALUABLE" if payload.get("unsupported") else "COMPLETE", payload)
    return execute


def run(repo: Path, *, mode: Literal["synthetic", "real"] = "synthetic",
        authorization_artifact: Path | None = None, max_rows: int | None = None,
        executor: Callable[[dict[str, Any]], RunOutcome] | None = None) -> dict[str, int]:
    repo = repo.resolve()
    manifest = validate_manifest(repo)
    freeze = repo / "runs" / RUN_ROOT_NAME / "freeze"
    run_root = repo / "runs" / RUN_ROOT_NAME
    manifest_sha = sha256_file(freeze / "run_manifest.json")
    if mode == "real":
        _authorization(repo, manifest_sha, authorization_artifact)
        if executor is None:
            executor = _make_real_executor(repo)
    elif mode != "synthetic":
        raise RunnerError(f"unknown mode {mode!r}")
    executor = executor or synthetic_executor
    status_log = run_root / "status" / f"{mode}.jsonl"
    state_file = run_root / "status" / f"{mode}_identity.json"
    identity = {"amendment": AMENDMENT, "manifest_sha256": manifest_sha,
                "source_hash": manifest["source_hash"], "mode": mode}
    if state_file.exists() and json.loads(state_file.read_text(encoding="utf-8")) != identity:
        raise ResumeMismatchError("resume refused: scientific identity differs")
    if not state_file.exists(): _atomic(state_file, canonical_json(identity) + b"\n")
    completed: set[str] = set()
    if status_log.exists():
        for line in status_log.read_text(encoding="utf-8").splitlines():
            item = json.loads(line)
            if item.get("status") == "COMPLETE":
                run_id = item["run_id"]
                target = run_root / ("synthetic_rows" if mode == "synthetic" else "rows") / f"{run_id}.json"
                checksum_path = target.with_suffix(".sha256")
                valid = target.exists() and checksum_path.exists()
                if valid:
                    declared = checksum_path.read_text(encoding="ascii").split()[0]
                    valid = declared == hashlib.sha256(target.read_bytes()).hexdigest() == item.get("checksum")
                if valid:
                    completed.add(run_id)
                else:
                    _append(status_log, {"run_id": run_id, "status": "MISSING",
                                         "reason": "RESULT_OR_CHECKSUM_MISSING_OR_CORRUPT",
                                         "attempt": time.time_ns()})
    with (freeze / "configuration_manifest.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    processed = 0
    counts = {name: 0 for name in ("PLANNED", "RUNNING", "COMPLETE", "ERROR", "MISSING", "NOT_EVALUABLE")}
    for row in rows:
        if row["run_id"] in completed: continue
        if max_rows is not None and processed >= max_rows: break
        row["config"] = json.loads(row.pop("config_json"))
        _append(status_log, {"run_id": row["run_id"], "status": "RUNNING", "attempt": time.time_ns()})
        try:
            outcome = executor(row)
            if outcome.status not in counts: raise RunnerError("executor returned invalid status")
            if outcome.payload.get("unsupported", 0):
                outcome = RunOutcome("NOT_EVALUABLE", {**outcome.payload, "reason": "UNSUPPORTED_NOMINAL_RESPONSE"})
            result = {"amendment": AMENDMENT, "manifest_sha256": manifest_sha,
                      "mode": mode, "run_id": row["run_id"], "status": outcome.status,
                      "block": row["block"], "config": row["config"], "result": outcome.payload}
            payload = canonical_json(result) + b"\n"
            target = run_root / ("synthetic_rows" if mode == "synthetic" else "rows") / f"{row['run_id']}.json"
            _atomic(target, payload)
            checksum = hashlib.sha256(payload).hexdigest()
            _atomic(target.with_suffix(".sha256"), f"{checksum}  {target.name}\n".encode("ascii"))
            _append(status_log, {"run_id": row["run_id"], "status": outcome.status,
                                 "checksum": checksum, "attempt": time.time_ns()})
            counts[outcome.status] += 1
        except Exception as exc:
            _append(status_log, {"run_id": row["run_id"], "status": "ERROR",
                                 "error_type": type(exc).__name__, "error": str(exc),
                                 "attempt": time.time_ns()})
            counts["ERROR"] += 1
        processed += 1
    counts["MISSING"] = len(rows) - len(completed) - processed
    _atomic(run_root / "status" / f"{mode}_index.json", canonical_json({
        "identity": identity, "counts_this_attempt": counts, "row_count": len(rows)}) + b"\n")
    return counts


__all__ = ["AuthorizationError", "LOGICAL_RESULT_FIELDS", "ResumeMismatchError", "RunOutcome", "RunnerError",
           "run", "synthetic_executor"]
