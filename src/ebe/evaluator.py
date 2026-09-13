"""E12 retained-only, proposition-level evidence evaluator."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Mapping, Sequence

Split = Literal["dev", "held_out"]
EvaluationSplit = Literal["dev", "held_out", "full"]
Metric = Literal["core", "context"]


class EvaluatorError(RuntimeError):
    """Base class for invalid evaluator inputs or configuration."""


class DenominatorFirewallError(EvaluatorError):
    """The frozen benchmark population invariants were violated."""


@dataclass(frozen=True, slots=True)
class RetainedBodyRecord:
    page_key: str
    capture_time: datetime
    body: bytes
    body_sha256: str


@dataclass(frozen=True, slots=True)
class RetainedFeedRecord:
    page_key: str
    action: Literal["live_change", "delete"]
    event_time: datetime
    delivered_time: datetime


@dataclass(frozen=True, slots=True)
class RetainedSnapshot:
    """The exclusive body-bearing evaluator input.

    The collector adapter reads only retained evidence and delivered feed
    polls; it has no path from body_results or capture_attempts.
    """

    checkpoint: datetime
    bodies: tuple[RetainedBodyRecord, ...]
    feed_context: tuple[RetainedFeedRecord, ...]

    @classmethod
    def from_collector_result(cls, result) -> "RetainedSnapshot":
        return cls(
            result.config.checkpoint,
            tuple(RetainedBodyRecord(x.page_key, x.capture_time, x.body, x.body_sha256)
                  for x in result.retained_evidence),
            tuple(RetainedFeedRecord(r.page_key, r.action, r.event_time, p.poll_time)
                  for p in result.feed_polls for r in p.records),
        )


@dataclass(frozen=True, slots=True)
class Fragment:
    fragment_id: str
    page_key: str
    kind: Literal["body_span", "observable_feed"]
    required_substring: bytes | None = None
    feed_action: Literal["live_change", "delete"] | None = None
    body_sha256: str | None = None
    source_ref: str | None = None

    def __post_init__(self) -> None:
        if self.kind == "body_span" and not self.required_substring:
            raise EvaluatorError(f"fragment {self.fragment_id!r}: body_span requires required_substring")
        if self.kind == "observable_feed" and self.feed_action is None:
            raise EvaluatorError(f"fragment {self.fragment_id!r}: observable_feed requires feed_action")


Alternative = tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Proposition:
    evidence_id: str
    critical: bool
    core_alternatives: tuple[Alternative, ...]
    context_alternatives: tuple[Alternative, ...] = ()
    eligible: bool = True
    eligibility_reason: str | None = None
    earliest_eligible_support: datetime | None = None
    split: Split | None = None
    group_id: str | None = None
    claim_status: str | None = None

    def __post_init__(self) -> None:
        if not self.eligible and self.eligibility_reason is None:
            raise EvaluatorError(f"{self.evidence_id}: ineligible proposition must record a reason")
        if any(not alt for alt in (*self.core_alternatives, *self.context_alternatives)):
            raise EvaluatorError(f"{self.evidence_id}: empty support alternative is not permitted")


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class ValidationReport:
    proposition_count: int
    fragment_count: int
    occurrence_count: int
    issues: tuple[ValidationIssue, ...]

    @property
    def valid(self) -> bool:
        return not self.issues

    def raise_for_errors(self) -> None:
        if self.issues:
            detail = "; ".join(f"{i.code}: {i.message}" for i in self.issues)
            raise DenominatorFirewallError(detail)


@dataclass(frozen=True, slots=True)
class Benchmark:
    propositions: tuple[Proposition, ...]
    fragments_by_id: Mapping[str, Fragment]
    validation: ValidationReport
    artifact_hashes: tuple[tuple[str, str], ...] = ()
    benchmark_id: str = "A11"
    context_status: Literal["FROZEN", "NOT_FROZEN"] = "NOT_FROZEN"


def validate_population(propositions: Sequence[Proposition], fragments_by_id: Mapping[str, Fragment], *, strict_metadata: bool = False) -> None:
    issues: list[str] = []
    seen: set[str] = set()
    for prop in propositions:
        if prop.evidence_id in seen:
            issues.append(f"duplicate evidence_id: {prop.evidence_id!r}")
        seen.add(prop.evidence_id)
        if strict_metadata and prop.split not in ("dev", "held_out"):
            issues.append(f"{prop.evidence_id}: missing split assignment")
        if strict_metadata and not prop.group_id:
            issues.append(f"{prop.evidence_id}: missing group assignment")
        for alt in (*prop.core_alternatives, *prop.context_alternatives):
            for fragment_id in alt:
                if fragment_id not in fragments_by_id:
                    issues.append(f"{prop.evidence_id}: dangling fragment reference {fragment_id!r}")
        if prop.critical and prop.eligible and not prop.core_alternatives:
            issues.append(f"{prop.evidence_id}: eligible critical proposition has no core support")
    if issues:
        raise DenominatorFirewallError("; ".join(issues))


def fragment_satisfied(fragment: Fragment, snapshot: RetainedSnapshot) -> tuple[bool, datetime | None]:
    if fragment.kind == "body_span":
        hits = [r for r in snapshot.bodies if r.page_key == fragment.page_key
                and (fragment.body_sha256 is None or r.body_sha256 == fragment.body_sha256)
                and fragment.required_substring in r.body]
        return (False, None) if not hits else (True, min(r.capture_time for r in hits))
    hits = [r for r in snapshot.feed_context if r.page_key == fragment.page_key and r.action == fragment.feed_action]
    return (False, None) if not hits else (True, min(r.delivered_time for r in hits))


def _alternative_satisfied(alternative: Alternative, fragments_by_id: Mapping[str, Fragment], snapshot: RetainedSnapshot) -> tuple[bool, datetime | None]:
    times: list[datetime] = []
    for fragment_id in alternative:
        satisfied, when = fragment_satisfied(fragments_by_id[fragment_id], snapshot)
        if not satisfied:
            return False, None
        assert when is not None
        times.append(when)
    return True, max(times)


def _best_alternative_time(alternatives: tuple[Alternative, ...], fragments_by_id: Mapping[str, Fragment], snapshot: RetainedSnapshot) -> tuple[bool, datetime | None]:
    times: list[datetime] = []
    for alt in alternatives:
        satisfied, when = _alternative_satisfied(alt, fragments_by_id, snapshot)
        if satisfied:
            assert when is not None
            times.append(when)
    return (False, None) if not times else (True, min(times))


def core_covered(proposition: Proposition, fragments_by_id: Mapping[str, Fragment], snapshot: RetainedSnapshot):
    return _best_alternative_time(proposition.core_alternatives, fragments_by_id, snapshot)


def context_covered(proposition: Proposition, fragments_by_id: Mapping[str, Fragment], snapshot: RetainedSnapshot):
    return _best_alternative_time(proposition.context_alternatives, fragments_by_id, snapshot)


@dataclass(frozen=True, slots=True)
class CoverageResult:
    numerator: int
    denominator: int
    covered_ids: tuple[str, ...]
    uncovered_ids: tuple[str, ...]
    excluded_ids: tuple[str, ...]
    percentage: float | None
    result_status: Literal["OK", "NA_EMPTY_DENOMINATOR", "NOT_FROZEN"] | None = None

    @property
    def status(self):
        return self.result_status or ("NA_EMPTY_DENOMINATOR" if self.denominator == 0 else "OK")


def _coverage(propositions, fragments_by_id, snapshot, *, critical_only: bool, metric: Metric) -> CoverageResult:
    validate_population(propositions, fragments_by_id)
    scoped = [p for p in propositions if not critical_only or p.critical]
    excluded = tuple(p.evidence_id for p in scoped if not p.eligible)
    eligible = [p for p in scoped if p.eligible]
    if metric == "context" and eligible and not any(p.context_alternatives for p in eligible):
        return CoverageResult(0, 0, (), (), excluded, None, "NOT_FROZEN")
    scorer = core_covered if metric == "core" else context_covered
    covered, uncovered = [], []
    for prop in eligible:
        (covered if scorer(prop, fragments_by_id, snapshot)[0] else uncovered).append(prop.evidence_id)
    denominator = len(eligible)
    return CoverageResult(len(covered), denominator, tuple(covered), tuple(uncovered), excluded,
                          100.0 * len(covered) / denominator if denominator else None)


def compute_core_coverage(propositions, fragments_by_id, snapshot, *, critical_only: bool) -> CoverageResult:
    return _coverage(propositions, fragments_by_id, snapshot, critical_only=critical_only, metric="core")


def compute_context_coverage(propositions, fragments_by_id, snapshot, *, critical_only: bool) -> CoverageResult:
    return _coverage(propositions, fragments_by_id, snapshot, critical_only=critical_only, metric="context")


@dataclass(frozen=True, slots=True)
class DelayResult:
    evidence_id: str
    status: Literal["retained", "unretained", "na_unknown_support"]
    delay_seconds: float | None


def compute_delay(proposition: Proposition, fragments_by_id: Mapping[str, Fragment], snapshot: RetainedSnapshot) -> DelayResult:
    if proposition.earliest_eligible_support is None:
        return DelayResult(proposition.evidence_id, "na_unknown_support", None)
    satisfied, acquisition_time = core_covered(proposition, fragments_by_id, snapshot)
    if not satisfied:
        return DelayResult(proposition.evidence_id, "unretained", None)
    assert acquisition_time is not None
    return DelayResult(proposition.evidence_id, "retained", (acquisition_time - proposition.earliest_eligible_support).total_seconds())


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    split: EvaluationSplit
    metric: Metric
    critical_only: bool
    numerator: int
    denominator: int
    percentage: float | None
    status: Literal["OK", "NA_EMPTY_DENOMINATOR", "NOT_FROZEN"]
    covered_evidence_ids: tuple[str, ...]
    uncovered_evidence_ids: tuple[str, ...]
    excluded_evidence: tuple[tuple[str, str], ...]
    delays: tuple[DelayResult, ...]
    benchmark_id: str
    artifact_hashes: tuple[tuple[str, str], ...]


def evaluate_benchmark(benchmark: Benchmark, snapshot: RetainedSnapshot, *, split: EvaluationSplit = "full", metric: Metric = "core", critical_only: bool = False) -> EvaluationResult:
    benchmark.validation.raise_for_errors()
    validate_population(benchmark.propositions, benchmark.fragments_by_id, strict_metadata=True)
    if split not in ("dev", "held_out", "full") or metric not in ("core", "context"):
        raise EvaluatorError(f"invalid split/metric: {split!r}/{metric!r}")
    excluded, scoped = [], []
    for prop in benchmark.propositions:
        if split != "full" and prop.split != split:
            continue
        if critical_only and not prop.critical:
            excluded.append((prop.evidence_id, "noncritical_filter"))
        elif not prop.eligible:
            excluded.append((prop.evidence_id, prop.eligibility_reason or "ineligible"))
        else:
            scoped.append(prop)
    if metric == "context" and benchmark.context_status != "FROZEN":
        excluded.extend((p.evidence_id, "context_axis_not_frozen") for p in scoped)
        return EvaluationResult(split, metric, critical_only, 0, 0, None, "NOT_FROZEN", (), (), tuple(excluded), (), benchmark.benchmark_id, benchmark.artifact_hashes)
    coverage = _coverage(scoped, benchmark.fragments_by_id, snapshot, critical_only=False, metric=metric)
    delays = tuple(compute_delay(p, benchmark.fragments_by_id, snapshot) for p in scoped) if metric == "core" else ()
    return EvaluationResult(split, metric, critical_only, coverage.numerator, coverage.denominator, coverage.percentage,
                            coverage.status, coverage.covered_ids, coverage.uncovered_ids, tuple(excluded), delays,
                            benchmark.benchmark_id, benchmark.artifact_hashes)


__all__ = ["Alternative", "Benchmark", "CoverageResult", "DelayResult", "DenominatorFirewallError",
           "EvaluationResult", "EvaluatorError", "Fragment", "Proposition", "RetainedBodyRecord",
           "RetainedFeedRecord", "RetainedSnapshot", "ValidationIssue", "ValidationReport",
           "compute_context_coverage", "compute_core_coverage", "compute_delay", "context_covered",
           "core_covered", "evaluate_benchmark", "fragment_satisfied", "validate_population"]
