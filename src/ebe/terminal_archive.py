"""Frozen terminal persistent-archive and final-state-only controls."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from .accounting import canonical_array, canonical_jsonl, require_utc
from .observer import BodyOutcome, BodyResponse, Observer, PendingBodyRequest
from .schema import NormalizedExport, RevisionRecord
from .storage import AdmissionResult, Capture, CaptureStore, RetainedStoreExport
from .timeline import HORIZON_END


@dataclass(frozen=True, slots=True)
class TerminalAttempt:
    request_seq: int
    page_key: str
    archive_key: str | None
    outcome: str
    header_bytes: int
    body_bytes: int | None
    admission: AdmissionResult | None


@dataclass(frozen=True, slots=True)
class TerminalCollection:
    mode: str
    checkpoint: datetime
    directory_requests: int
    archive_enumerations: int
    metadata_bytes: int
    attempts: tuple[TerminalAttempt, ...]
    retained: RetainedStoreExport

    @property
    def request_attempts(self) -> int:
        return self.directory_requests + self.archive_enumerations + len(self.attempts)

    @property
    def known_body_bytes(self) -> int:
        return sum(x.body_bytes or 0 for x in self.attempts if x.outcome == "body")


def _canonical_body(revision: RevisionRecord) -> bytes:
    codec = {"ascii": "ascii", "utf8": "utf-8", "latin1": "latin-1"}[revision.body_encoding.value]
    return revision.source_body_bytes.decode(codec, errors="strict").encode("utf-8")


def run_final_state_only(observer: Observer, *, capacity_bytes: int = 1_048_576,
                         checkpoint: datetime = HORIZON_END) -> TerminalCollection:
    """F: one terminal directory, lexicographic atomic GET, exact FIFO/dedup."""
    checkpoint = require_utc(checkpoint)
    if checkpoint != HORIZON_END:
        raise ValueError("F is defined only at terminal T")
    if observer.config.get_response_delay_us != 0:
        raise ValueError("F requires atomic zero-delay GET")
    directory = observer.terminal_directory(checkpoint)
    store = CaptureStore(capacity_bytes, deduplicate=True, start_time=checkpoint)
    attempts: list[TerminalAttempt] = []
    for page_key in directory.page_keys:
        response = observer.get_body(page_key, checkpoint)
        if isinstance(response, PendingBodyRequest):
            raise RuntimeError("atomic F response unexpectedly pending")
        admission = None
        if response.outcome is BodyOutcome.BODY:
            admission = store.admit(Capture(page_key, checkpoint, response.request_seq, response.body or b""))
        attempts.append(TerminalAttempt(response.request_seq, page_key, None,
            response.outcome.value, len(response.header_bytes),
            len(response.body) if response.body is not None else None, admission))
    return TerminalCollection("F", checkpoint, 1, 0, len(directory.response_bytes),
                              tuple(attempts), store.export_retained(checkpoint))


def archive_entries(export: NormalizedExport, checkpoint: datetime = HORIZON_END) -> tuple[RevisionRecord, ...]:
    checkpoint = require_utc(checkpoint)
    return tuple(sorted(
        (r for r in export.revisions if r.wiki == "dse" and r.time.utc <= checkpoint),
        key=lambda r: (r.time.utc, r.page_key, r.rev_id),
    ))


def append_terminal_archive(export: NormalizedExport, store: CaptureStore, *,
                            request_seq_start: int, checkpoint: datetime = HORIZON_END) -> TerminalCollection:
    """Append every held DSE revision, continuing exact sequence/store state."""
    checkpoint = require_utc(checkpoint)
    entries = archive_entries(export, checkpoint)
    metadata = canonical_array([{"archive_key": r.rev_id, "event_time": r.time.raw,
                                 "page_key": r.page_key} for r in entries])
    attempts: list[TerminalAttempt] = []
    seq = request_seq_start
    for revision in entries:
        seq += 1
        body = _canonical_body(revision)
        header = canonical_jsonl({"outcome": "body"})
        capture = Capture(revision.page_key, checkpoint, seq, body, revision.rev_id)
        admission = store.admit(capture)
        attempts.append(TerminalAttempt(seq, revision.page_key, revision.rev_id,
                                        "body", len(header), len(body), admission))
    return TerminalCollection("A", checkpoint, 0, 1, len(metadata), tuple(attempts),
                              store.export_retained(checkpoint))


def run_archive_only(export: NormalizedExport, *, capacity_bytes: int | None,
                     checkpoint: datetime = HORIZON_END) -> TerminalCollection:
    store = CaptureStore(capacity_bytes, deduplicate=True, start_time=checkpoint)
    return append_terminal_archive(export, store, request_seq_start=0, checkpoint=checkpoint)


def augment_collector_result(export: NormalizedExport, result) -> TerminalCollection:
    """A-live: continue an exact completed live prefix at terminal T."""
    retained = getattr(result, "retained_export", None)
    if retained is None:
        raise ValueError("collector result lacks immutable retained export")
    if retained.checkpoint != HORIZON_END:
        raise ValueError("persistent augmentation is terminal-only")
    store = CaptureStore.from_retained_export(retained)
    prefix_seq = max((item.request_seq for item in result.body_results), default=0)
    return append_terminal_archive(export, store, request_seq_start=prefix_seq,
                                   checkpoint=retained.checkpoint)


__all__ = ["TerminalAttempt", "TerminalCollection", "append_terminal_archive",
           "augment_collector_result",
           "archive_entries", "run_archive_only", "run_final_state_only"]
