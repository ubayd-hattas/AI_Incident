"""Typed, provenance-preserving records for the Collusion Wiki core export.

These records describe source observations only.  They deliberately contain no
historical page state, ordering priority, body carry-forward, or survival logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Mapping


class BodyEncoding(str, Enum):
    ASCII = "ascii"
    UTF8 = "utf8"
    LATIN1 = "latin1"


class ExportedEventType(str, Enum):
    SAVE = "save"
    DELETE = "delete"
    REVERT = "revert"
    PROBE = "probe"


class ObservedEventSemantics(str, Enum):
    """Observed record shape, not a page-state transition instruction."""

    HELD_BODY_SAVE = "held_body_save"
    SUCCESSFUL_DELETION = "successful_deletion"
    BODY_UNKNOWN_FORM_EDIT = "body_unknown_form_edit"
    NON_MUTATION_PROBE = "non_mutation_probe"


class RelationValueForm(str, Enum):
    ABSENT = "absent"
    NULL = "null"
    SCALAR = "scalar"
    LIST = "list"


@dataclass(frozen=True, slots=True)
class SourceLocation:
    file: Path
    row_number: int | None = None
    identifier: str | None = None


@dataclass(frozen=True, slots=True)
class SourceTimestamp:
    """A losslessly parsed UTC timestamp and its exact source spelling."""

    raw: str
    utc: datetime


@dataclass(frozen=True, slots=True)
class RelationValue:
    """One original null/scalar/list relation field, without interpretation."""

    form: RelationValueForm
    value: None | str | tuple[str | None, ...]


@dataclass(frozen=True, slots=True)
class RelationEdge:
    relation_type: str
    related_event_id: str
    round_id: str | None


@dataclass(frozen=True, slots=True)
class RelationFields:
    related_event_id: RelationValue
    relation_type: RelationValue
    round_id: RelationValue
    edges: tuple[RelationEdge, ...]


@dataclass(frozen=True, slots=True)
class DiffHunk:
    op: str
    a0: int
    a1: int
    b0: int
    b1: int


@dataclass(frozen=True, slots=True)
class PageRecord:
    source: SourceLocation
    raw: Mapping[str, Any]
    page_id: str
    page_key: str
    wiki: str
    name: str
    bucket: str
    page_family: str
    page_family_cohort: str | None
    page_family_confidence: float | None
    page_family_method: str | None
    page_family_source: str
    n_revs: int
    n_revs_before: int
    first_write: SourceTimestamp
    last_write: SourceTimestamp
    body_bytes: int
    deleted_live: bool
    live_body_variant: str
    head_differs_from_live: bool
    n_deletions: int
    n_recreations: int
    labels: tuple[str, ...]
    n_labels: int
    n_ips: int
    n_ip16: int


@dataclass(frozen=True, slots=True)
class RevisionRecord:
    source: SourceLocation
    raw: Mapping[str, Any]
    rev_id: str
    page_id: str
    page_key: str
    wiki: str
    name: str
    seq: int
    rcs_rev: str
    rcs_path: str
    body: str
    source_body_bytes: bytes
    body_len: int
    body_sha256: str
    body_encoding: BodyEncoding
    lines: int
    diff_base: str | None
    diff_base_reason: str | None
    hunks: tuple[DiffHunk, ...]
    label: str
    ip16: str
    time: SourceTimestamp
    time_grade: str
    winning_clock: str
    uncertainty_seconds: int
    request_time: SourceTimestamp | None
    success_time: SourceTimestamp | None
    recent_changes_time: SourceTimestamp | None
    write_date: SourceTimestamp
    archived_at: SourceTimestamp
    request_action: str | None
    change_summary: str | None
    relations: RelationFields


@dataclass(frozen=True, slots=True)
class EventRecord:
    source: SourceLocation
    raw: Mapping[str, Any]
    present_fields: frozenset[str]
    event_id: str
    event_type: ExportedEventType
    observed_semantics: ObservedEventSemantics
    time: SourceTimestamp
    time_grade: str
    wiki: str | None
    page: str | None
    page_key: str | None
    revision_ref: str | None
    winning_clock: str | None
    uncertainty_seconds: int | None
    request_time: SourceTimestamp | None
    success_time: SourceTimestamp | None
    write_date: SourceTimestamp | None
    recent_changes_time: SourceTimestamp | None
    rcs_date: SourceTimestamp | None
    clock_delta_seconds: int | None
    clock_note: str | None
    success_observed: bool | None
    request_action: str | None
    change_summary: str | None
    actor_label: str | None
    ip16: str | None
    page_held: bool | None
    param_family: str | None
    source_refs: tuple[str, ...]
    relations: RelationFields


@dataclass(frozen=True, slots=True)
class LabelRecord:
    source: SourceLocation
    raw: Mapping[str, Any]
    label: str
    is_human_handle: bool
    stored_revisions: int
    first_write: SourceTimestamp
    last_write: SourceTimestamp
    stored_revision_ips: int
    stored_revision_ip16: int
    stored_revision_pages: int
    pages: tuple[str, ...]
    wikis: tuple[str, ...]
    save_requests: int
    save_request_ips: int
    save_request_ip16: int
    save_request_pages: int
    save_request_source: str | None


@dataclass(frozen=True, slots=True)
class ManifestRecord:
    source: SourceLocation
    raw: Mapping[str, Any]
    generated_at: SourceTimestamp
    db_sha256: str
    cut: Mapping[str, Any]
    counts: Mapping[str, Any]
    per_wiki: Mapping[str, Any]
    population_counts: Mapping[str, Any]
    grade_histograms: Mapping[str, Any]
    body_bytes: Mapping[str, Any]
    body_encoding: Mapping[str, Any]
    page_family_coverage: Mapping[str, Any]
    facts: Mapping[str, Any]
    recreation_source: Mapping[str, Any]
    resources: Mapping[str, Any]
    tool_versions: Mapping[str, Any]
    source_scan: Mapping[str, Any]
    request_source_note: str
    checks: tuple[Mapping[str, Any], ...]


@dataclass(frozen=True, slots=True)
class ExportFingerprint:
    sha256: Mapping[str, str]
    row_counts: Mapping[str, int]


@dataclass(frozen=True, slots=True)
class NormalizedExport:
    """Deterministic, in-file-order E05 output for a future E06 consumer."""

    pages: tuple[PageRecord, ...]
    revisions: tuple[RevisionRecord, ...]
    events: tuple[EventRecord, ...]
    labels: tuple[LabelRecord, ...]
    manifest: ManifestRecord
    fingerprint: ExportFingerprint
    pages_by_id: Mapping[str, PageRecord]
    pages_by_key: Mapping[str, PageRecord]
    revisions_by_id: Mapping[str, RevisionRecord]
    events_by_id: Mapping[str, EventRecord]
    labels_by_label: Mapping[str, LabelRecord]
