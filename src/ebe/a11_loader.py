"""Deterministic loader for the frozen A11 core-evidence benchmark."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime
import hashlib
import json
from pathlib import Path
from typing import Any

from .evaluator import (
    Benchmark, DenominatorFirewallError, Fragment, Proposition,
    ValidationIssue, ValidationReport, validate_population,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
ANNOTATIONS = REPO_ROOT / "annotations"
REVISIONS = REPO_ROOT / "data" / "raw" / "export" / "revisions.jsonl"


def _rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as stream:
        for line_no, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise DenominatorFirewallError(f"{path}:{line_no}: malformed JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise DenominatorFirewallError(f"{path}:{line_no}: row must be an object")
            rows.append(row)
    return rows


def _canonical_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"timestamp is not timezone-aware: {value!r}")
    return parsed


def _raw_body_bytes(body: str) -> bytes:
    """Reverse E05's unconditional Latin-1 JSON projection."""
    return body.encode("latin-1")


def _canonical_body_bytes(body: str, encoding: str) -> bytes:
    """Convert reconstructed source bytes to the observer's canonical UTF-8."""
    raw = _raw_body_bytes(body)
    codec = {"ascii": "ascii", "utf8": "utf-8", "latin1": "latin-1"}.get(encoding)
    if codec is None:
        raise ValueError(f"unsupported body encoding: {encoding!r}")
    return raw.decode(codec, errors="strict").encode("utf-8")


def _unique(rows: list[dict[str, Any]], key: str, issues: list[ValidationIssue]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        value = row.get(key)
        if not isinstance(value, str) or not value:
            issues.append(ValidationIssue("MALFORMED_ROW", f"missing/non-string {key}"))
        elif value in result:
            issues.append(ValidationIssue(f"DUPLICATE_{key.upper()}", value))
        else:
            result[value] = row
    return result


def load_a11_benchmark(
    evidence_path: Path | None = None,
    occurrences_path: Path | None = None,
    eligibility_path: Path | None = None,
    splits_path: Path | None = None,
    revisions_path: Path | None = None,
    *,
    fail_on_error: bool = True,
) -> Benchmark:
    evidence_path = evidence_path or ANNOTATIONS / "evidence.jsonl"
    occurrences_path = occurrences_path or ANNOTATIONS / "occurrences.jsonl"
    eligibility_path = eligibility_path or ANNOTATIONS / "eligibility.jsonl"
    splits_path = splits_path or ANNOTATIONS / "splits.json"
    revisions_path = revisions_path or REVISIONS

    evidence_rows = _rows(evidence_path)
    occurrence_rows = _rows(occurrences_path)
    eligibility_rows = _rows(eligibility_path)
    revision_rows = _rows(revisions_path)
    with splits_path.open(encoding="utf-8") as stream:
        splits = json.load(stream)

    issues: list[ValidationIssue] = []
    evidence_by_id = _unique(evidence_rows, "evidence_id", issues)
    eligibility_by_id = _unique(eligibility_rows, "evidence_id", issues)
    occurrences_by_id = _unique(occurrence_rows, "occurrence_id", issues)
    revisions_by_id = _unique(revision_rows, "rev_id", issues)

    pinned = splits.get("checksums", {})
    for path, key in ((evidence_path, "evidence_jsonl_sha256"), (occurrences_path, "occurrences_jsonl_sha256")):
        if pinned.get(key) != _canonical_hash(path):
            issues.append(ValidationIssue("ARTIFACT_HASH_MISMATCH", path.name))

    evidence_ids = set(evidence_by_id)
    for evidence_id in sorted(evidence_ids - set(eligibility_by_id)):
        issues.append(ValidationIssue("MISSING_ELIGIBILITY", evidence_id))
    for evidence_id in sorted(set(eligibility_by_id) - evidence_ids):
        issues.append(ValidationIssue("ORPHAN_ELIGIBILITY", evidence_id))

    split_by_evidence: dict[str, str] = {}
    split_by_group: dict[str, str] = {}
    split_by_page: dict[str, str] = {}
    for split_name in ("dev", "held_out"):
        block = splits.get("splits", {}).get(split_name)
        if not isinstance(block, dict):
            issues.append(ValidationIssue("MISSING_SPLIT", split_name))
            continue
        for key, target in (("evidence_ids", split_by_evidence), ("group_ids", split_by_group), ("page_keys", split_by_page)):
            for value in block.get(key, []):
                if value in target:
                    code = "CROSS_SPLIT_LEAKAGE" if target[value] != split_name else "DUPLICATE_SPLIT_MEMBER"
                    issues.append(ValidationIssue(code, f"{key}:{value}"))
                target[value] = split_name
    for evidence_id in sorted(evidence_ids):
        if evidence_id not in split_by_evidence:
            issues.append(ValidationIssue("MISSING_SPLIT_ASSIGNMENT", evidence_id))
    for evidence_id in sorted(set(split_by_evidence) - evidence_ids):
        issues.append(ValidationIssue("ORPHAN_SPLIT_ASSIGNMENT", evidence_id))

    group_pages: dict[str, set[str]] = {}
    for group_id, group in splits.get("groups", {}).items():
        declared_split = group.get("split")
        if split_by_group.get(group_id) != declared_split:
            issues.append(ValidationIssue("GROUP_SPLIT_DISAGREEMENT", group_id))
        group_pages[group_id] = {f"dse~{page}" for page in group.get("pages", [])}

    span_quotes: dict[str, list[str]] = {}
    for evidence_id, row in evidence_by_id.items():
        revision = revisions_by_id.get(row.get("rev_id"))
        if revision is None:
            issues.append(ValidationIssue("UNRESOLVED_EVIDENCE_REVISION", evidence_id))
        else:
            body = revision.get("body")
            try:
                raw = _raw_body_bytes(body) if isinstance(body, str) else None
            except UnicodeEncodeError:
                raw = None
            if raw is None:
                issues.append(ValidationIssue("UNRESOLVABLE_EVIDENCE_BODY", evidence_id))
            elif hashlib.sha256(raw).hexdigest() != row.get("source_body_hash"):
                issues.append(ValidationIssue("EVIDENCE_BODY_HASH_MISMATCH", evidence_id))
        spans = row.get("source_spans")
        if not isinstance(spans, list) or not spans:
            issues.append(ValidationIssue("MISSING_CORE_SPANS", evidence_id))
            span_quotes[evidence_id] = []
            continue
        quotes: list[str] = []
        for span in spans:
            if not isinstance(span, dict) or not isinstance(span.get("quote"), str) or not span["quote"]:
                issues.append(ValidationIssue("MALFORMED_SOURCE_SPAN", evidence_id))
            else:
                quotes.append(span["quote"])
        span_quotes[evidence_id] = quotes

    # Eligibility may exclude a provenance-defective support alternative without
    # suppressing a proposition that has another frozen, eligible alternative.
    # This is annotation-owned disposition data, not collector-derived selection.
    excluded_support_revisions: dict[str, set[str]] = {}
    for evidence_id, row in eligibility_by_id.items():
        excluded = row.get("excluded_support_revisions", [])
        if not isinstance(excluded, list) or not all(isinstance(revision_id, str) for revision_id in excluded):
            issues.append(ValidationIssue("MALFORMED_ALTERNATIVE_ELIGIBILITY", evidence_id))
            excluded = []
        excluded_support_revisions[evidence_id] = set(excluded)

    support: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for occurrence_id, occurrence in occurrences_by_id.items():
        evidence_id = occurrence.get("evidence_id")
        if evidence_id not in evidence_by_id:
            issues.append(ValidationIssue("ORPHAN_OCCURRENCE", occurrence_id))
            continue
        parent = evidence_by_id[evidence_id]
        rev_id = occurrence.get("rev_id")
        if rev_id in excluded_support_revisions.get(evidence_id, set()):
            continue
        revision = revisions_by_id.get(rev_id)
        if revision is None:
            issues.append(ValidationIssue("UNRESOLVED_REVISION", f"{occurrence_id}:{rev_id}"))
            continue
        page_key = occurrence.get("page_key")
        if page_key != revision.get("page_key") or page_key != str(rev_id).split("@", 1)[0]:
            issues.append(ValidationIssue("MALFORMED_OCCURRENCE_REFERENCE", occurrence_id))
            continue
        group_id = parent.get("equivalent_occurrences_group")
        if occurrence.get("equivalent_group") != group_id:
            issues.append(ValidationIssue("OCCURRENCE_GROUP_MISMATCH", occurrence_id))
            continue
        if page_key not in group_pages.get(group_id, set()):
            issues.append(ValidationIssue("OCCURRENCE_GROUP_PAGE_MISMATCH", occurrence_id))
            continue
        expected_split = split_by_group.get(group_id)
        if expected_split is None or split_by_page.get(page_key) != expected_split or split_by_evidence.get(evidence_id) != expected_split:
            issues.append(ValidationIssue("OCCURRENCE_SPLIT_MISMATCH", occurrence_id))
            continue
        body = revision.get("body")
        encoding = revision.get("body_encoding", "ascii")
        if not isinstance(body, str) or encoding not in ("ascii", "utf8", "latin1"):
            issues.append(ValidationIssue("UNRESOLVABLE_BODY", occurrence_id))
            continue
        # E05 stores the raw JSON body as a Latin-1 projection of the original
        # byte sequence.  body_encoding classifies those source bytes; it does
        # not change how the projection itself is reversed.
        try:
            raw = _raw_body_bytes(body)
            canonical = _canonical_body_bytes(body, encoding)
        except (UnicodeEncodeError, UnicodeDecodeError, ValueError):
            issues.append(ValidationIssue("UNRESOLVABLE_BODY", occurrence_id))
            continue
        if hashlib.sha256(raw).hexdigest() != occurrence.get("body_sha256"):
            issues.append(ValidationIssue("OCCURRENCE_BODY_HASH_MISMATCH", occurrence_id))
            continue
        if occurrence.get("event_id") != f"save:{rev_id}" or occurrence.get("seq") != revision.get("seq"):
            issues.append(ValidationIssue("MALFORMED_OCCURRENCE_REFERENCE", occurrence_id))
            continue
        if occurrence.get("wall_timestamp") != revision.get("time"):
            issues.append(ValidationIssue("OCCURRENCE_TIME_MISMATCH", occurrence_id))
            continue
        span = occurrence.get("char_span")
        if not isinstance(span, list) or len(span) != 2 or not all(type(x) is int for x in span) or not 0 <= span[0] < span[1] <= len(body):
            issues.append(ValidationIssue("MALFORMED_OCCURRENCE_SPAN", occurrence_id))
            continue
        quote = body[span[0]:span[1]]
        matching_indices = [index for index, expected in enumerate(span_quotes[evidence_id]) if expected == quote]
        if len(matching_indices) != 1:
            issues.append(ValidationIssue("OCCURRENCE_NOT_ALLOWED_SUPPORT", occurrence_id))
            continue
        span_index = matching_indices[0]
        bucket = support[evidence_id].setdefault(rev_id, {
            "page_key": page_key,
            "body_sha256": hashlib.sha256(canonical).hexdigest(),
            "source_body_sha256": occurrence["body_sha256"],
            "timestamp": occurrence.get("wall_timestamp"),
            "spans": {},
        })
        if bucket["source_body_sha256"] != occurrence["body_sha256"]:
            issues.append(ValidationIssue("REVISION_HASH_DISAGREEMENT", occurrence_id))
            continue
        bucket["spans"].setdefault(span_index, (quote, occurrence_id))

    fragments: dict[str, Fragment] = {}
    propositions: list[Proposition] = []
    for evidence_id, row in evidence_by_id.items():
        alternatives: list[tuple[str, ...]] = []
        support_times: list[datetime] = []
        required_count = len(span_quotes[evidence_id])
        for rev_id, bucket in sorted(support.get(evidence_id, {}).items()):
            if set(bucket["spans"]) != set(range(required_count)):
                continue
            alternative: list[str] = []
            for index in range(required_count):
                quote, occurrence_id = bucket["spans"][index]
                fragment_id = f"{evidence_id}:{rev_id}:span-{index}"
                fragments[fragment_id] = Fragment(
                    fragment_id, bucket["page_key"], "body_span", quote.encode("utf-8"),
                    body_sha256=bucket["body_sha256"], source_ref=occurrence_id,
                )
                alternative.append(fragment_id)
            alternatives.append(tuple(alternative))
            try:
                support_times.append(_utc(bucket["timestamp"]))
            except (TypeError, ValueError) as exc:
                issues.append(ValidationIssue("MALFORMED_SUPPORT_TIME", f"{rev_id}:{exc}"))

        eligibility = eligibility_by_id.get(evidence_id, {})
        eligible = eligibility.get("eligible")
        if type(eligible) is not bool:
            issues.append(ValidationIssue("MISSING_ELIGIBILITY_DISPOSITION", evidence_id))
            eligible = False
        reason = eligibility.get("reason")
        if not eligible and not isinstance(reason, str):
            issues.append(ValidationIssue("MISSING_ELIGIBILITY_REASON", evidence_id))
            reason = "invalid eligibility record"
        group_id = row.get("equivalent_occurrences_group")
        prop_split = split_by_evidence.get(evidence_id)
        if split_by_group.get(group_id) != prop_split:
            issues.append(ValidationIssue("PROPOSITION_GROUP_SPLIT_DISAGREEMENT", evidence_id))
        critical = row.get("critical")
        if type(critical) is not bool:
            issues.append(ValidationIssue("MALFORMED_CRITICAL_FLAG", evidence_id))
            critical = False
        if eligible and critical and not alternatives:
            issues.append(ValidationIssue("ELIGIBLE_CRITICAL_WITHOUT_CORE_SUPPORT", evidence_id))
        propositions.append(Proposition(
            evidence_id=evidence_id,
            critical=critical,
            core_alternatives=tuple(alternatives),
            eligible=eligible,
            eligibility_reason=reason,
            earliest_eligible_support=min(support_times) if eligible and support_times else None,
            split=prop_split if prop_split in ("dev", "held_out") else None,
            group_id=group_id if isinstance(group_id, str) else None,
            claim_status=row.get("claim_status") if isinstance(row.get("claim_status"), str) else None,
        ))

    try:
        validate_population(propositions, fragments, strict_metadata=True)
    except DenominatorFirewallError as exc:
        issues.append(ValidationIssue("POPULATION_FIREWALL", str(exc)))

    paths = (evidence_path, occurrences_path, eligibility_path, splits_path)
    hashes = tuple((path.name, _canonical_hash(path)) for path in paths)
    report = ValidationReport(len(propositions), len(fragments), len(occurrence_rows), tuple(issues))
    benchmark = Benchmark(
        tuple(propositions), fragments, report, hashes,
        benchmark_id=splits.get("dataset_name", "A11"), context_status="NOT_FROZEN",
    )
    if fail_on_error:
        report.raise_for_errors()
    return benchmark


def load_real_propositions(
    evidence_path: Path | None = None,
    eligibility_path: Path | None = None,
) -> tuple[tuple[Proposition, ...], dict[str, Fragment]]:
    """Compatibility wrapper; new code should use load_a11_benchmark()."""
    benchmark = load_a11_benchmark(evidence_path=evidence_path, eligibility_path=eligibility_path)
    return benchmark.propositions, dict(benchmark.fragments_by_id)


__all__ = ["load_a11_benchmark", "load_real_propositions"]
