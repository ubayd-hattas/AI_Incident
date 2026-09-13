# E12 core-evidence evaluator candidate

Status: implementation candidate for structural acceptance and future single-collector evaluation. This work does not authorize or run X13.

## Real A11 loader

`src/ebe/a11_loader.py::load_a11_benchmark()` mechanically loads the frozen `evidence.jsonl`, `occurrences.jsonl`, `eligibility.jsonl`, and `splits.json` artifacts. It also resolves every occurrence span against the released revision universe solely to verify the recorded revision, body hash, character span, and exact text. It returns a typed `Benchmark` with an explicit `ValidationReport` and canonical-LF SHA-256 provenance for all four annotation artifacts.

The loader freezes each proposition's evidence ID, annotation-provided `critical` and `claim_status` fields, group, split, core eligibility/reason, exact core alternatives, and earliest eligible support time. It does not derive criticality or reinterpret epistemic status.

## Retained-only firewall

`RetainedSnapshot` is the exclusive evaluator-facing collector representation. `RetainedSnapshot.from_collector_result()` reads bodies only from `CollectorResult.retained_evidence` and context only from delivered `feed_polls`. No scoring API accepts `body_results`, `capture_attempts`, raw trace bodies, rejected/oversize bodies, evicted bodies, or diagnostic history.

Synthetic poison tests confirm that bodies visible in diagnostic results but rejected or absent from the final capped store cannot satisfy evidence.

## Proposition and support semantics

One proposition is one denominator unit. Occurrence rows are a provenance/support census and never create additional evidence units.

Each real body fragment is pinned to the occurrence's page, exact UTF-8 text, and canonical retained-body SHA-256. This prevents an unadjudicated same-page or future body from satisfying a frozen occurrence accidentally.

For a single-span proposition, each complete adjudicated occurrence is an alternative. For a multi-span proposition, rows are grouped by revision and become one AND-alternative only if that revision contains every frozen source span. Alternatives are ORed. Repeated occurrences therefore provide alternate preservation routes for one proposition and cannot inflate the numerator.

No fuzzy, normalized, near-copy, or new paraphrase matching is performed.

## A05 denominator firewall

Loading fails closed on duplicate IDs, missing eligibility dispositions, missing split assignments, proposition/group split disagreement, cross-split page/group leakage, malformed or orphan occurrence references, unresolved revision/body references, body-hash/span mismatch, support outside the frozen source spans, dangling fragments, and eligible critical propositions without complete core support. Errors are exposed as structured `ValidationIssue` records in `ValidationReport`; normal loading raises on any issue rather than dropping rows.

## Split, eligibility, and critical filtering

`evaluate_benchmark()` accepts `split="dev"`, `split="held_out"`, or `split="full"` and an independent `critical_only` flag. Both are annotation-derived before any retained snapshot is inspected; collector outcomes cannot affect membership. Ineligible propositions are excluded with their frozen reason. Non-critical filtering uses only the frozen boolean field.

The current structural benchmark properties are 65 propositions: 34 dev and 31 held-out; 57 critical; 64 core-eligible and one excluded. The future primary held-out/critical core denominator is 27 as a benchmark property only.

## Coverage and delay

Core coverage is true exactly when at least one complete frozen alternative is satisfied by retained material. Coverage results include numerator, denominator, percentage or NA, covered/uncovered IDs, exclusions with reasons, split, metric, critical filter, per-proposition delay, and artifact provenance.

Delay is the earliest completed retained alternative time minus the earliest frozen eligible support time. A multi-fragment completion time is its latest fragment acquisition; the earliest completed valid alternative wins. Results distinguish `retained`, `unretained`, and `na_unknown_support`; an unretained proposition never receives zero delay.

## Context axis

The repository's `context_fragments_DRAFT_SAM.jsonl`, `context_eligibility_DRAFT_SAM.jsonl`, and `A11_CONTEXT_AXIS_DRAFT_SAM.md` remain drafts and are not loaded by the accepted core loader. The benchmark records `context_status="NOT_FROZEN"`. Context evaluation returns `NOT_FROZEN`, with percentage NA and denominator zero, rather than a misleading 0% failure. A future accepted artifact can set a frozen context schema explicitly.

## Explicitly not scored or implemented here

- No PCD-versus-E comparison, policy sweep, or X13 result.
- No real collector result was joined to A11 during implementation or verification.
- No draft context ground truth.
- No policy conclusion, threshold decision, group robustness, archive sensitivity, PCD-R, F collector, or X13 output suite.

The evaluator handles one retained collector snapshot at a time and produces no comparative conclusion.
