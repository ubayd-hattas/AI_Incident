"""E12 retained-only proposition evaluator under the final frozen contract."""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
import hashlib
import json
from typing import Literal, Mapping, Sequence
from .accounting import canonical_jsonl, format_timestamp

Split = Literal["dev", "held_out"]
EvaluationSplit = Literal["dev", "held_out", "full"]
Metric = Literal["core", "context"]
ContextState = Literal["self_contained", "required", "unknown", "unavailable"]

class EvaluatorError(RuntimeError): pass
class DenominatorFirewallError(EvaluatorError): pass
class SnapshotIntegrityError(EvaluatorError): pass

@dataclass(frozen=True, slots=True)
class RetainedBodyRecord:
    page_key: str
    capture_time: datetime
    body: bytes
    body_sha256: str
    request_seq: int | None = None
    packet_bytes: bytes | None = None
    object_id: str | None = None
    archive_key: str | None = None

@dataclass(frozen=True, slots=True)
class RetainedObjectRecord:
    object_id: str
    body: bytes
    body_sha256: str
    refcount: int

@dataclass(frozen=True, slots=True)
class RetainedFeedRecord:
    page_key: str
    action: Literal["live_change", "delete"]
    event_time: datetime
    delivered_time: datetime

@dataclass(frozen=True, slots=True)
class RetainedSnapshot:
    """Exclusive retained-at-C scoring input; diagnostic histories are absent."""
    checkpoint: datetime
    bodies: tuple[RetainedBodyRecord, ...]
    feed_context: tuple[RetainedFeedRecord, ...]
    capacity_bytes: int | None = None
    retained_packet_bytes: int | None = None
    retained_body_bytes: int | None = None
    declared_total_bytes: int | None = None
    stable_support_intervals: Mapping[str, tuple[tuple[int, int | None], ...]] | None = None
    retained_objects: tuple[RetainedObjectRecord, ...] = ()

    @classmethod
    def from_collector_result(cls, result) -> "RetainedSnapshot":
        export = getattr(result, "retained_export", None)
        if export is not None:
            objects = {x.object_id: x for x in export.body_objects}
            bodies: list[RetainedBodyRecord] = []
            for index, packet in enumerate(export.packets):
                obj = objects.get(packet.object_id)
                if obj is None:
                    raise SnapshotIntegrityError(
                        f"packet[{index}] references missing object {packet.object_id!r}"
                    )
                bodies.append(RetainedBodyRecord(
                    packet.page_key, packet.capture_time, obj.body,
                    packet.body_sha256, packet.request_seq, packet.packet_bytes,
                    packet.object_id, packet.archive_key,
                ))
            retained_objects = tuple(RetainedObjectRecord(
                obj.object_id, obj.body, obj.body_sha256, obj.refcount
            ) for obj in export.body_objects)
            snapshot = cls(export.checkpoint, tuple(bodies),
                tuple(RetainedFeedRecord(r.page_key, r.action, r.event_time, poll.poll_time)
                      for poll in result.feed_polls for r in poll.records),
                export.capacity_bytes, export.retained_packet_bytes,
                export.retained_body_bytes, export.total_bytes,
                retained_objects=retained_objects)
            validate_snapshot(snapshot)
            return snapshot
        return cls(result.config.checkpoint,
            tuple(RetainedBodyRecord(x.page_key, x.capture_time, x.body,
                                     x.body_sha256, x.request_seq)
                  for x in result.retained_evidence),
            tuple(RetainedFeedRecord(r.page_key, r.action, r.event_time, p.poll_time)
                  for p in result.feed_polls for r in p.records))

def _aware(value: datetime) -> bool:
    return isinstance(value, datetime) and value.tzinfo is not None and value.utcoffset() is not None

def validate_snapshot(snapshot: RetainedSnapshot) -> None:
    issues: list[str] = []
    if not _aware(snapshot.checkpoint): issues.append("checkpoint is not timezone-aware")
    seen_seq: set[int] = set(); packet_total = 0; objects: dict[str, bytes] = {}
    for index, record in enumerate(snapshot.bodies):
        if not _aware(record.capture_time): issues.append(f"body[{index}] capture_time is not aware")
        try: record.body.decode("utf-8", errors="strict")
        except UnicodeDecodeError: issues.append(f"body[{index}] is not canonical UTF-8")
        if hashlib.sha256(record.body).hexdigest() != record.body_sha256:
            issues.append(f"body[{index}] {record.page_key!r}: body_sha256 mismatch")
        if record.capture_time > snapshot.checkpoint: issues.append(f"body[{index}] capture_time is after checkpoint")
        if record.request_seq is not None:
            if record.request_seq in seen_seq: issues.append(f"duplicate request sequence {record.request_seq}")
            seen_seq.add(record.request_seq)
        if record.packet_bytes is not None: packet_total += len(record.packet_bytes)
        if record.packet_bytes is not None:
            expected = {"body_sha256": record.body_sha256,
                        "capture_time": format_timestamp(record.capture_time),
                        "page_key": record.page_key, "request_seq": record.request_seq}
            if record.archive_key is not None: expected["archive_key"] = record.archive_key
            if record.request_seq is None or record.packet_bytes != canonical_jsonl(expected):
                issues.append(f"body[{index}] packet schema/width mismatch")
        key = record.object_id or record.body_sha256
        if key in objects and objects[key] != record.body: issues.append(f"object {key} has conflicting bytes")
        objects[key] = record.body
    if snapshot.retained_objects:
        declared_objects: dict[str, RetainedObjectRecord] = {}
        actual_refs: dict[str, int] = {}
        for index, obj in enumerate(snapshot.retained_objects):
            if obj.object_id in declared_objects:
                issues.append(f"duplicate retained object ID {obj.object_id!r}")
            declared_objects[obj.object_id] = obj
            if not isinstance(obj.body, bytes):
                issues.append(f"object[{index}] body is not bytes")
                continue
            try: obj.body.decode("utf-8", errors="strict")
            except UnicodeDecodeError: issues.append(f"object[{index}] is not canonical UTF-8")
            if hashlib.sha256(obj.body).hexdigest() != obj.body_sha256:
                issues.append(f"object[{index}] {obj.object_id!r}: body_sha256 mismatch")
            if type(obj.refcount) is not int or obj.refcount < 1:
                issues.append(f"object[{index}] {obj.object_id!r}: invalid refcount")
            actual_refs[obj.object_id] = 0
        for index, record in enumerate(snapshot.bodies):
            if record.object_id not in declared_objects:
                issues.append(f"body[{index}] references missing object {record.object_id!r}")
                continue
            obj = declared_objects[record.object_id]
            actual_refs[record.object_id] += 1
            if record.body != obj.body or record.body_sha256 != obj.body_sha256:
                issues.append(f"body[{index}] object reference bytes/hash mismatch")
        for object_id, obj in declared_objects.items():
            if actual_refs[object_id] == 0:
                issues.append(f"object {object_id!r} is hidden/unreferenced")
            if obj.refcount != actual_refs[object_id]:
                issues.append(
                    f"object {object_id!r} refcount mismatch: "
                    f"declared {obj.refcount}, actual {actual_refs[object_id]}"
                )
        body_total = sum(len(obj.body) for obj in declared_objects.values())
    else:
        body_total = sum(len(x) for x in objects.values())
    for index, record in enumerate(snapshot.feed_context):
        if not _aware(record.event_time) or not _aware(record.delivered_time):
            issues.append(f"feed[{index}] timestamps are not aware")
        elif record.event_time > record.delivered_time or record.delivered_time > snapshot.checkpoint:
            issues.append(f"feed[{index}] violates event/delivery/checkpoint order")
    if snapshot.retained_packet_bytes is not None and packet_total != snapshot.retained_packet_bytes:
        issues.append("declared retained packet bytes are not synchronized")
    if snapshot.retained_body_bytes is not None and body_total != snapshot.retained_body_bytes:
        issues.append("declared retained body bytes are not synchronized")
    computed = packet_total + body_total
    if snapshot.declared_total_bytes is not None and computed != snapshot.declared_total_bytes:
        issues.append("declared total S is not synchronized")
    if snapshot.capacity_bytes is not None and computed > snapshot.capacity_bytes:
        issues.append("retained bytes exceed cap")
    if issues: raise SnapshotIntegrityError("; ".join(issues))

@dataclass(frozen=True, slots=True)
class BodyOccurrence:
    page_key: str
    body_sha256: str
    required_bytes: bytes
    support_id: str | None = None

@dataclass(frozen=True, slots=True)
class Fragment:
    fragment_id: str
    page_key: str
    kind: Literal["body_span", "observable_feed"]
    required_substring: bytes | None = None
    feed_action: Literal["live_change", "delete"] | None = None
    body_sha256: str | None = None
    source_ref: str | None = None
    event_time: datetime | None = None
    minimum_multiplicity: int = 1
    body_occurrences: tuple[BodyOccurrence, ...] = ()
    def __post_init__(self) -> None:
        if self.kind == "body_span" and not self.required_substring and not self.body_occurrences:
            raise EvaluatorError(f"fragment {self.fragment_id!r}: body_span requires frozen bytes")
        if self.kind == "observable_feed" and (self.feed_action is None or self.event_time is None):
            raise EvaluatorError(f"fragment {self.fragment_id!r}: observable_feed requires exact action/time")
        if type(self.minimum_multiplicity) is not int or self.minimum_multiplicity < 1:
            raise EvaluatorError("minimum_multiplicity must be positive")

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
    context_state: ContextState = "self_contained"
    def __post_init__(self) -> None:
        if not self.eligible and self.eligibility_reason is None: raise EvaluatorError("ineligible proposition requires reason")
        if any(not alt for alt in (*self.core_alternatives, *self.context_alternatives)): raise EvaluatorError("empty support alternative")
        if self.context_state == "self_contained" and self.context_alternatives and self.context_alternatives != self.core_alternatives:
            raise EvaluatorError("self-contained context must equal core")
        if self.context_state == "required":
            for alt in self.context_alternatives:
                if not any(set(core).issubset(alt) for core in self.core_alternatives):
                    raise EvaluatorError("context alternative lacks complete core")

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
    def valid(self) -> bool: return not self.issues
    def raise_for_errors(self) -> None:
        if self.issues: raise DenominatorFirewallError("; ".join(f"{i.code}: {i.message}" for i in self.issues))
@dataclass(frozen=True, slots=True)
class Benchmark:
    propositions: tuple[Proposition, ...]
    fragments_by_id: Mapping[str, Fragment]
    validation: ValidationReport
    artifact_hashes: tuple[tuple[str, str], ...] = ()
    benchmark_id: str = "A11"
    context_status: Literal["FROZEN", "NOT_FROZEN"] = "NOT_FROZEN"
    scoreable: bool = True

def validate_population(propositions: Sequence[Proposition], fragments_by_id: Mapping[str, Fragment], *, strict_metadata: bool = False) -> None:
    issues=[]; seen=set()
    for fid,f in fragments_by_id.items():
        if not f.page_key.startswith("dse~"): issues.append(f"{fid}: outside DSE")
    for prop in propositions:
        if prop.evidence_id in seen: issues.append(f"duplicate evidence_id {prop.evidence_id}")
        seen.add(prop.evidence_id)
        if strict_metadata and (prop.split not in ("dev","held_out") or not prop.group_id): issues.append(f"{prop.evidence_id}: missing split/group")
        for alt in (*prop.core_alternatives,*prop.context_alternatives):
            for fid in alt:
                if fid not in fragments_by_id: issues.append(f"{prop.evidence_id}: dangling {fid}")
        for alt in prop.core_alternatives:
            if prop.eligible and not any(fragments_by_id[f].kind == "body_span" for f in alt if f in fragments_by_id): issues.append(f"{prop.evidence_id}: core alternative without body")
        if prop.critical and prop.eligible and not prop.core_alternatives: issues.append(f"{prop.evidence_id}: no core")
    if issues: raise DenominatorFirewallError("; ".join(issues))

def fragment_satisfied(fragment: Fragment, snapshot: RetainedSnapshot) -> tuple[bool, datetime | None]:
    validate_snapshot(snapshot)
    if fragment.kind == "body_span":
        occurrences = fragment.body_occurrences or (BodyOccurrence(fragment.page_key, fragment.body_sha256 or "", fragment.required_substring or b""),)
        hits=[]
        for r in snapshot.bodies:
            for o in occurrences:
                support_id=o.support_id or fragment.source_ref
                allowed=True
                if snapshot.stable_support_intervals is not None:
                    point=int(r.capture_time.timestamp()*1_000_000)
                    allowed=support_id is not None and any(
                        point>=start and (end is None or point<end)
                        for start,end in snapshot.stable_support_intervals.get(support_id,()))
                if allowed and r.page_key==o.page_key and (not o.body_sha256 or r.body_sha256==o.body_sha256) and o.required_bytes in r.body:
                    hits.append(r.capture_time)
        return (False,None) if not hits else (True,min(hits))
    hits=[r.delivered_time for r in snapshot.feed_context if r.page_key==fragment.page_key and r.action==fragment.feed_action and r.event_time==fragment.event_time and r.delivered_time<=snapshot.checkpoint and r.event_time<=r.delivered_time]
    return (False,None) if len(hits)<fragment.minimum_multiplicity else (True,sorted(hits)[fragment.minimum_multiplicity-1])

def _alternative_satisfied(alternative, fragments_by_id, snapshot):
    times=[]
    for fid in alternative:
        ok,when=fragment_satisfied(fragments_by_id[fid],snapshot)
        if not ok:return False,None
        times.append(when)
    return True,max(times)
def _best_alternative_time(alternatives,fragments_by_id,snapshot):
    times=[when for alt in alternatives for ok,when in [_alternative_satisfied(alt,fragments_by_id,snapshot)] if ok]
    return (False,None) if not times else (True,min(times))
def core_covered(proposition,fragments_by_id,snapshot): return _best_alternative_time(proposition.core_alternatives,fragments_by_id,snapshot)
def context_covered(proposition,fragments_by_id,snapshot):
    if proposition.context_state in ("unknown","unavailable"): return False,None
    if not core_covered(proposition,fragments_by_id,snapshot)[0]: return False,None
    return _best_alternative_time(proposition.context_alternatives or proposition.core_alternatives,fragments_by_id,snapshot)

@dataclass(frozen=True, slots=True)
class CoverageResult:
    numerator:int; denominator:int; covered_ids:tuple[str,...]; uncovered_ids:tuple[str,...]; excluded_ids:tuple[str,...]; percentage:float|None
    result_status:str|None=None; unknown_ids:tuple[str,...]=(); unknown_reason_codes:tuple[tuple[str,str],...]=(); lower_numerator:int|None=None; upper_numerator:int|None=None
    witness_fragment_ids:tuple=(); witness_packet_ids:tuple=()
    @property
    def status(self): return self.result_status or ("NA_EMPTY_DENOMINATOR" if self.denominator==0 else "OK")

def _coverage(propositions,fragments_by_id,snapshot,*,critical_only,metric):
    validate_snapshot(snapshot); validate_population(propositions,fragments_by_id)
    scoped=[p for p in propositions if not critical_only or p.critical]; excluded=tuple(p.evidence_id for p in scoped if not p.eligible); eligible=[p for p in scoped if p.eligible]
    covered=[]; uncovered=[]; unknown=[]; reasons=[]
    for p in eligible:
        if metric=="context" and p.context_state in ("unknown","unavailable"):
            unknown.append(p.evidence_id); reasons.append((p.evidence_id,f"CONTEXT_{p.context_state.upper()}")); continue
        scorer=core_covered if metric=="core" else context_covered
        (covered if scorer(p,fragments_by_id,snapshot)[0] else uncovered).append(p.evidence_id)
    n=len(eligible); point=None if not n or unknown else 100*len(covered)/n
    status="NA_EMPTY_DENOMINATOR" if not n else ("NA_CONTEXT_INTERVAL" if unknown else "OK")
    return CoverageResult(len(covered),n,tuple(covered),tuple(uncovered),excluded,point,status,tuple(unknown),tuple(reasons),len(covered),len(covered)+len(unknown))
def compute_core_coverage(propositions,fragments_by_id,snapshot,*,critical_only): return _coverage(propositions,fragments_by_id,snapshot,critical_only=critical_only,metric="core")
def compute_context_coverage(propositions,fragments_by_id,snapshot,*,critical_only): return _coverage(propositions,fragments_by_id,snapshot,critical_only=critical_only,metric="context")

def apply_stable_support_mask(benchmark: Benchmark,
                              intervals: Mapping[str, tuple[tuple[int, int | None], ...]]) -> Benchmark:
    """Filter support/denominator before U-stable evaluation."""
    def available(fid: str) -> bool:
        fragment=benchmark.fragments_by_id[fid]
        if fragment.kind=="observable_feed": return True
        ids=[o.support_id for o in fragment.body_occurrences] or [fragment.source_ref]
        return any(identity and intervals.get(identity) for identity in ids)
    propositions=[]
    for prop in benchmark.propositions:
        core=tuple(alt for alt in prop.core_alternatives if all(available(fid) for fid in alt))
        context=tuple(alt for alt in prop.context_alternatives if all(available(fid) for fid in alt))
        eligible=prop.eligible and bool(core)
        propositions.append(replace(prop,core_alternatives=core,context_alternatives=context,
            eligible=eligible,eligibility_reason=prop.eligibility_reason if eligible
            else "UNAVAILABLE_UNDER_CONSERVATIVE_STABLE_SUPPORT"))
    return replace(benchmark,propositions=tuple(propositions))

@dataclass(frozen=True, slots=True)
class DelayResult:
    evidence_id:str; status:str; delay_seconds:float|None
def compute_delay(proposition,fragments_by_id,snapshot):
    validate_snapshot(snapshot)
    if proposition.earliest_eligible_support is None:return DelayResult(proposition.evidence_id,"na_unknown_support",None)
    ok,when=core_covered(proposition,fragments_by_id,snapshot)
    if not ok:return DelayResult(proposition.evidence_id,"unretained",None)
    seconds=(when-proposition.earliest_eligible_support).total_seconds()
    if seconds<0: raise SnapshotIntegrityError("negative acquisition delay")
    return DelayResult(proposition.evidence_id,"retained",seconds)

@dataclass(frozen=True, slots=True)
class EvaluationResult:
    split:EvaluationSplit; metric:Metric; critical_only:bool; numerator:int; denominator:int; percentage:float|None; status:str
    covered_evidence_ids:tuple[str,...]; uncovered_evidence_ids:tuple[str,...]; excluded_evidence:tuple[tuple[str,str],...]; delays:tuple[DelayResult,...]; benchmark_id:str; artifact_hashes:tuple[tuple[str,str],...]
    unknown_evidence_ids:tuple[str,...]=(); unknown_reason_codes:tuple[tuple[str,str],...]=(); lower_context_numerator:int|None=None; upper_context_numerator:int|None=None

def evaluate_benchmark(benchmark,snapshot,*,split="full",metric="core",critical_only=False):
    validate_snapshot(snapshot); benchmark.validation.raise_for_errors()
    if not benchmark.scoreable: raise DenominatorFirewallError("diagnostically loaded benchmark is not scoreable")
    validate_population(benchmark.propositions,benchmark.fragments_by_id,strict_metadata=True)
    if split not in ("dev","held_out","full") or metric not in ("core","context"):raise EvaluatorError("invalid split/metric")
    excluded=[]; scoped=[]
    for p in benchmark.propositions:
        if split!="full" and p.split!=split:continue
        if critical_only and not p.critical:excluded.append((p.evidence_id,"noncritical_filter"))
        elif not p.eligible:excluded.append((p.evidence_id,p.eligibility_reason or "ineligible"))
        else:scoped.append(p)
    if metric=="context" and benchmark.context_status!="FROZEN": return EvaluationResult(split,metric,critical_only,0,0,None,"NOT_FROZEN",(),(),tuple(excluded),(),benchmark.benchmark_id,benchmark.artifact_hashes)
    cov=_coverage(scoped,benchmark.fragments_by_id,snapshot,critical_only=False,metric=metric)
    delays=tuple(compute_delay(p,benchmark.fragments_by_id,snapshot) for p in scoped) if metric=="core" else ()
    return EvaluationResult(split,metric,critical_only,cov.numerator,cov.denominator,cov.percentage,cov.status,cov.covered_ids,cov.uncovered_ids,tuple(excluded),delays,benchmark.benchmark_id,benchmark.artifact_hashes,cov.unknown_ids,cov.unknown_reason_codes,cov.lower_numerator,cov.upper_numerator)

__all__=["Alternative","Benchmark","BodyOccurrence","CoverageResult","DelayResult","DenominatorFirewallError","EvaluationResult","EvaluatorError","Fragment","Proposition","RetainedBodyRecord","RetainedFeedRecord","RetainedObjectRecord","RetainedSnapshot","SnapshotIntegrityError","ValidationIssue","ValidationReport","apply_stable_support_mask","compute_context_coverage","compute_core_coverage","compute_delay","context_covered","core_covered","evaluate_benchmark","fragment_satisfied","validate_population","validate_snapshot"]
