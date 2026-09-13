# A11 acceptance-matrix items C/D/E — what was mechanically closeable, and what wasn't

Role: implementer (Sam), explicitly authorized to proceed on items C (typed fragment/context alternatives), D
(occurrence-census completeness), and E (eligibility mask) after flagging that these are normally
annotation-authorship work. This document is honest about the boundary: everything below is either (a) a direct,
lossless reshaping of data Alex/Aaron already authored, (b) an exhaustive but purely mechanical exact-match search,
or (c) rule application against already-documented, already-adjudicated exclusions (`docs/V02_ADJUDICATION.md`).
Nothing here invents new semantic judgment about what counts as evidence, and nowhere does this pass run real
evidence-coverage scoring.

## Item D — occurrence-census completeness (exact-match portion closed)

**Found:** `PROP-20260619-01` had zero occurrence rows despite two valid, already-recorded `source_spans` — not just
missing cumulative/copy occurrences elsewhere, but missing its own anchor revision's occurrences, which every other
proposition on the same page already had. This exactly matches the acceptance matrix's own example.

**Fixed:**
1. Added the 2 missing anchor occurrences using Alex's own already-recorded `source_spans` (zero new judgment —
   this was a data-entry gap, not a missing decision).
2. Built `audit/occurrence_census_search.py`: an exhaustive whole-DSE search (all 14,591 revisions) for byte-exact
   substring matches of every proposition's recorded span text. Found 29 additional same-page revisions
   (`dse~DataUSAConstructionWageSep18Live@2` through `@30`) where the same coordination-header text persists
   unchanged — added as `cumulative_carryforward` occurrences (58 rows for the 2 spans × 29 revisions), using each
   revision's own real `body_sha256`/`seq`/`wall_timestamp` from `data/raw/export/revisions.jsonl`.
3. Re-ran the search after the fix: **0 remaining exact-match candidates across all 65 propositions.**

**Not done, and not fabricated:** normalized/near-copy/paraphrase search (the contract's second search phase,
requiring human review of ambiguous equivalence). No cross-title (different page) exact matches were found for any
proposition, so this pass found nothing requiring that harder judgment call — but the possibility of a near-copy on
a different page, worded differently, was not searched for and would need human review if attempted.

Total occurrences: 1,361 → **1,421**. `annotations/A11_BENCHMARK_SPEC.md`, `annotations/splits.json`'s
`summary.total_occurrences` and checksums, and `audit/verify_a11_independent.py`'s expected count are all updated.
A pre-existing bug in both `audit/verify_annotations.py` and `audit/verify_a11_independent.py` (comparing a
multi-span occurrence's slice against the proposition's combined, ellipsis-joined `quotation` field instead of its
own individual `source_span`) was found and fixed while validating this change — every prior single-span
proposition happened to have `quotation == source_spans[0].quote`, so the bug was latent until this fix.

## Item E — eligibility mask (core-eligibility portion closed; context-eligibility deferred)

**Found and applied**, using only already-documented, already-adjudicated exclusions and independently-run
mechanical checks — no new eligibility judgment:

- `PROP-20260618-63` is anchored on `dse~AI@2`. `docs/V02_ADJUDICATION.md` already documents "AI (untimed head
  mismatch)... entire title EXCLUDE_FROM_EXACT_SCORING for body evidence, retain diagnostic trace queries/cost" —
  an adjudicated exclusion from before this pass, not one made here. Marked `eligible: false` with that reason.
  (It is a non-critical negative control, so this has zero effect on critical coverage either way.)
- The other documented exclusion, "PoliceBridge (no held bodies)," does not correspond to any of the 65 current
  evidence anchors — checked directly, not applicable.
- All 65 anchors independently confirmed to resolve to a genuine, known (non-BU) revision (structurally guaranteed
  by `evidence.jsonl` requiring `source_body_hash`/`body_len` at all) and to a single, unambiguous `LIVE_BODY` state
  via the real `TraceModel.state_at(mode="nominal")` at the revision's own save time — zero unsupported, zero
  ambiguous, across all 65.
- Result: 64 eligible, 1 ineligible (`PROP-20260618-63`), written to `annotations/eligibility.jsonl`, each row
  recording its method and reason explicitly.

**Not done, and not fabricated:** context-eligibility (whether a proposition's *context* requirement is available,
versus necessarily unknown/unavailable) is a separate axis from core eligibility and depends on the context
fragments this pass did not define (see Item C below). `eligibility.jsonl` says so explicitly in every row's
`method` field, so nobody downstream mistakes "core eligible" for "fully eligible on every axis."

## Item C — typed fragment/context alternatives (core/body-span portion mechanically closed; context deferred)

**Built:** `src/ebe/a11_loader.py`, converting `evidence.jsonl`'s already-authored `source_spans` directly into
`src/ebe/evaluator.py`'s `Fragment`/`Proposition` OR-of-AND representation — one `body_span` fragment per recorded
span, all of a proposition's fragments required together in a single core alternative (multi-span requires every
span, per SS4). This is a lossless reshaping of already-authored data, not a new fragment-identification decision.
Wired in the real `eligibility.jsonl` from Item E. 5 structural tests confirm it loads all 65 propositions, passes
the A05 population firewall, and wires eligibility correctly.

**Not done, and not fabricated:**
- **Context fragments.** No context requirement has been typed for any proposition — `context_alternatives` is
  empty for all 65. Declaring what context is actually *required* (per SS4: "required speaker/task/epistemic/
  temporal context") is a judgment call belonging to Alex/Aaron, not something inferred from the existing flat
  `support_bundles`/`minimum_context` prose fields.
- **Cross-title/alternative fragments.** The occurrence census (Item D) found no cross-page exact matches for any
  of the 65 propositions, so no additional cross-title fragment was needed for now — this is a fact about the
  current search result, not a claim that no such alternative could ever exist (a near-copy on a different page,
  found only by human-reviewed normalized search, could still warrant one).
- **`src/ebe/a11_loader.py`'s output was NOT run through `compute_core_coverage`/`compute_delay` against any real
  collector output.** Doing so would be semantic evidence-coverage scoring against real captures, which
  `docs/X13_RUN_CONTRACT.md` §9 does not authorize until the acceptance-matrix items are actually closed (context
  fragments still aren't). `tests/test_a11_loader.py` checks only structural loading and the population firewall —
  never scoring.

## What this changes for the gates

- **Item D: closed for exact-match completeness.** Near-copy/paraphrase search remains open, annotation-authorship
  work.
- **Item E: closed for core eligibility.** Context-eligibility remains open, blocked on Item C's context half.
- **Item C: closed for the body-span/core-alternative mechanics.** Context alternatives remain open, annotation
  authorship.
- **E12 still cannot score real data end-to-end** — the context axis is unmodeled on both the fragment side (item
  C) and the eligibility side (item E), and near-copy occurrence review (item D) is still open. What changed is
  that the *core* axis (the primary D estimand's dominant term, critical core coverage) now has a real, tested,
  non-fabricated path from `evidence.jsonl` through to the evaluator's `Proposition`/`Fragment` types — the missing
  piece is specifically the context axis, not the whole pipeline.
- Given the deadline, whether to push further on context fragments/eligibility today, or document the context axis
  as an explicit limitation and proceed with core-only reporting, is a call for Jaswin — not something this pass
  decided unilaterally.

## Reproduce this

```powershell
python audit/occurrence_census_search.py
python audit/verify_a11_independent.py
python -m unittest tests.test_a11_loader -v
```
