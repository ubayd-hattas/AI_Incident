"""E12 substrate: retained-only evaluator boundary and coverage/delay core.

Scope (see docs/E12_SUBSTRATE.md for the full account): this module implements
only the mechanics X13_RUN_CONTRACT.md SS4/SS5 describe -- the evaluator API
firewall, and coverage/delay computation over a typed fragment/proposition
representation. It does NOT implement, and must never be pointed at,
annotations/evidence.jsonl or annotations/occurrences.jsonl: the real
fragment-alternatives schema (C1/C2), whole-DSE occurrence-census completeness
(D), and machine-readable eligibility mask (E) do not exist yet, and building
those is Alex/Aaron/Jaswin's annotation-authorship work, not something this
module invents. The Fragment/Proposition types below are synthetic scaffolding
for testing the evaluator's LOGIC in isolation, not a proposal for the real
annotation schema.

Firewall (SS4): the only permitted evaluator input is RetainedSnapshot, built
exclusively from what a collector's CaptureStore genuinely retained at
checkpoint C (via CollectorResult.retained_evidence / RetainedEvidenceUnit)
plus the feed context actually delivered and charged to that collector
(CollectorResult.feed_polls). It is never built from body_results,
capture_attempts, or any other diagnostic/audit surface.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Sequence


class EvaluatorError(RuntimeError):
    """Base class for invalid evaluator inputs or configuration."""


class DenominatorFirewallError(EvaluatorError):
    """A11 population/eligibility invariants were violated (A05)."""


# ---------------------------------------------------------------------------
# SS4: the firewalled evaluator input
# ---------------------------------------------------------------------------


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
    """The ONLY type E12's coverage/delay core may consume.

    Construct via `from_collector_result` for real collector output, or build
    directly (as the synthetic tests do) for hand-scored acceptance cases.
    Never construct this from `CollectorResult.body_results` or
    `.capture_attempts` -- those include oversize/evicted/rejected bodies that
    were never actually retained, and scoring against them would silently
    defeat the entire point of a capacity cap.
    """

    checkpoint: datetime
    bodies: tuple[RetainedBodyRecord, ...]
    feed_context: tuple[RetainedFeedRecord, ...]

    @classmethod
    def from_collector_result(cls, result) -> "RetainedSnapshot":
        bodies = tuple(
            RetainedBodyRecord(unit.page_key, unit.capture_time, unit.body, unit.body_sha256)
            for unit in result.retained_evidence
        )
        feed_context = tuple(
            RetainedFeedRecord(record.page_key, record.action, record.event_time, poll.poll_time)
            for poll in result.feed_polls
            for record in poll.records
        )
        return cls(result.config.checkpoint, bodies, feed_context)


# ---------------------------------------------------------------------------
# Synthetic fragment/proposition representation (scaffolding, not the real schema)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Fragment:
    """A typed body-span or observable-feed predicate (SS4).

    `required_substring` models an exact-span requirement at the level of
    canonical body bytes (the real schema's character-span/hash mapping
    between source projection and canonical text is annotation-authorship
    work, not modeled here). `feed_action` models an observable-feed
    predicate: the retained feed context alone (no body) can satisfy it.
    """

    fragment_id: str
    page_key: str
    kind: Literal["body_span", "observable_feed"]
    required_substring: bytes | None = None
    feed_action: Literal["live_change", "delete"] | None = None

    def __post_init__(self) -> None:
        if self.kind == "body_span" and not self.required_substring:
            raise EvaluatorError(f"fragment {self.fragment_id!r}: body_span requires required_substring")
        if self.kind == "observable_feed" and self.feed_action is None:
            raise EvaluatorError(f"fragment {self.fragment_id!r}: observable_feed requires feed_action")


Alternative = tuple[str, ...]  # fragment_ids, ALL required (AND)


@dataclass(frozen=True, slots=True)
class Proposition:
    evidence_id: str
    critical: bool
    core_alternatives: tuple[Alternative, ...]
    context_alternatives: tuple[Alternative, ...] = ()
    eligible: bool = True
    eligibility_reason: str | None = None
    earliest_eligible_support: datetime | None = None

    def __post_init__(self) -> None:
        if not self.eligible and self.eligibility_reason is None:
            raise EvaluatorError(f"{self.evidence_id}: ineligible proposition must record a reason")
        for alt in self.core_alternatives:
            if not alt:
                raise EvaluatorError(f"{self.evidence_id}: empty core alternative is not permitted")
        for alt in self.context_alternatives:
            if not alt:
                raise EvaluatorError(f"{self.evidence_id}: empty context alternative is not permitted")


def validate_population(propositions: Sequence[Proposition], fragments_by_id: dict[str, Fragment]) -> None:
    """A05 denominator firewall: reject duplicate units and dangling references
    before any coverage is computed. Raises DenominatorFirewallError, never
    silently drops or de-duplicates."""

    seen: set[str] = set()
    for prop in propositions:
        if prop.evidence_id in seen:
            raise DenominatorFirewallError(f"duplicate evidence_id: {prop.evidence_id!r}")
        seen.add(prop.evidence_id)
        for alt in (*prop.core_alternatives, *prop.context_alternatives):
            for fragment_id in alt:
                if fragment_id not in fragments_by_id:
                    raise DenominatorFirewallError(
                        f"{prop.evidence_id}: dangling fragment reference {fragment_id!r}"
                    )
        if prop.critical and not prop.core_alternatives and prop.eligible:
            raise DenominatorFirewallError(
                f"{prop.evidence_id}: an eligible critical proposition must have at least one core alternative"
            )


# ---------------------------------------------------------------------------
# Fragment / alternative / proposition satisfaction
# ---------------------------------------------------------------------------


def fragment_satisfied(fragment: Fragment, snapshot: RetainedSnapshot) -> tuple[bool, datetime | None]:
    """Returns (satisfied, earliest acquisition time), never inventing a time
    for an unsatisfied fragment."""

    if fragment.kind == "body_span":
        matches = [
            record for record in snapshot.bodies
            if record.page_key == fragment.page_key and fragment.required_substring in record.body
        ]
        if not matches:
            return False, None
        return True, min(record.capture_time for record in matches)
    matches = [
        record for record in snapshot.feed_context
        if record.page_key == fragment.page_key and record.action == fragment.feed_action
    ]
    if not matches:
        return False, None
    return True, min(record.delivered_time for record in matches)


def _alternative_satisfied(
    alternative: Alternative, fragments_by_id: dict[str, Fragment], snapshot: RetainedSnapshot,
) -> tuple[bool, datetime | None]:
    times: list[datetime] = []
    for fragment_id in alternative:
        satisfied, when = fragment_satisfied(fragments_by_id[fragment_id], snapshot)
        if not satisfied:
            return False, None
        assert when is not None
        times.append(when)
    # "Multi-part acquisition time is the latest component" (SS5).
    return True, max(times)


def _best_alternative_time(
    alternatives: tuple[Alternative, ...], fragments_by_id: dict[str, Fragment], snapshot: RetainedSnapshot,
) -> tuple[bool, datetime | None]:
    candidates: list[datetime] = []
    for alt in alternatives:
        satisfied, when = _alternative_satisfied(alt, fragments_by_id, snapshot)
        if satisfied:
            assert when is not None
            candidates.append(when)
    if not candidates:
        return False, None
    # "Minimize over valid retained alternatives" (SS5).
    return True, min(candidates)


def core_covered(
    proposition: Proposition, fragments_by_id: dict[str, Fragment], snapshot: RetainedSnapshot,
) -> tuple[bool, datetime | None]:
    return _best_alternative_time(proposition.core_alternatives, fragments_by_id, snapshot)


def context_covered(
    proposition: Proposition, fragments_by_id: dict[str, Fragment], snapshot: RetainedSnapshot,
) -> tuple[bool, datetime | None]:
    if not proposition.context_alternatives:
        return False, None
    return _best_alternative_time(proposition.context_alternatives, fragments_by_id, snapshot)


# ---------------------------------------------------------------------------
# Coverage aggregation (SS5) -- micro only; group/phase/archive robustness is
# explicitly out of scope for this substrate pass.
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CoverageResult:
    numerator: int
    denominator: int
    covered_ids: tuple[str, ...]
    uncovered_ids: tuple[str, ...]
    excluded_ids: tuple[str, ...]
    percentage: float | None  # None (NA) when denominator == 0 -- never a fabricated 0/0

    @property
    def status(self) -> Literal["OK", "NA_EMPTY_DENOMINATOR"]:
        return "NA_EMPTY_DENOMINATOR" if self.denominator == 0 else "OK"


def compute_core_coverage(
    propositions: Sequence[Proposition],
    fragments_by_id: dict[str, Fragment],
    snapshot: RetainedSnapshot,
    *,
    critical_only: bool,
) -> CoverageResult:
    validate_population(propositions, fragments_by_id)
    scoped = [p for p in propositions if not critical_only or p.critical]
    excluded = tuple(p.evidence_id for p in scoped if not p.eligible)
    eligible = [p for p in scoped if p.eligible]
    covered: list[str] = []
    uncovered: list[str] = []
    for prop in eligible:
        satisfied, _ = core_covered(prop, fragments_by_id, snapshot)
        (covered if satisfied else uncovered).append(prop.evidence_id)
    denom = len(eligible)
    pct = (100.0 * len(covered) / denom) if denom else None
    return CoverageResult(len(covered), denom, tuple(covered), tuple(uncovered), excluded, pct)


def compute_context_coverage(
    propositions: Sequence[Proposition],
    fragments_by_id: dict[str, Fragment],
    snapshot: RetainedSnapshot,
    *,
    critical_only: bool,
) -> CoverageResult:
    """Uses the SAME denominator (K) as core coverage for the critical-context
    row, per SS5: "the critical context row uses the same K as critical core."
    Context coverage is reported for eligible units regardless of whether a
    context requirement was declared; a unit with no context_alternatives is
    simply uncovered on this axis, not excluded."""

    validate_population(propositions, fragments_by_id)
    scoped = [p for p in propositions if not critical_only or p.critical]
    excluded = tuple(p.evidence_id for p in scoped if not p.eligible)
    eligible = [p for p in scoped if p.eligible]
    covered: list[str] = []
    uncovered: list[str] = []
    for prop in eligible:
        satisfied, _ = context_covered(prop, fragments_by_id, snapshot)
        (covered if satisfied else uncovered).append(prop.evidence_id)
    denom = len(eligible)
    pct = (100.0 * len(covered) / denom) if denom else None
    return CoverageResult(len(covered), denom, tuple(covered), tuple(uncovered), excluded, pct)


# ---------------------------------------------------------------------------
# Delay (SS5)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class DelayResult:
    evidence_id: str
    status: Literal["retained", "unretained", "na_unknown_support"]
    delay_seconds: float | None


def compute_delay(
    proposition: Proposition, fragments_by_id: dict[str, Fragment], snapshot: RetainedSnapshot,
) -> DelayResult:
    if proposition.earliest_eligible_support is None:
        return DelayResult(proposition.evidence_id, "na_unknown_support", None)
    satisfied, acquisition_time = core_covered(proposition, fragments_by_id, snapshot)
    if not satisfied:
        return DelayResult(proposition.evidence_id, "unretained", None)
    assert acquisition_time is not None
    delay = (acquisition_time - proposition.earliest_eligible_support).total_seconds()
    return DelayResult(proposition.evidence_id, "retained", delay)


__all__ = [
    "Alternative",
    "CoverageResult",
    "DelayResult",
    "DenominatorFirewallError",
    "EvaluatorError",
    "Fragment",
    "Proposition",
    "RetainedBodyRecord",
    "RetainedFeedRecord",
    "RetainedSnapshot",
    "compute_context_coverage",
    "compute_core_coverage",
    "compute_delay",
    "context_covered",
    "core_covered",
    "fragment_satisfied",
    "validate_population",
]
