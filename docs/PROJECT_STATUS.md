# Project status — Evidence Before Erasure

## Current authority

**GATE 2 FAIL (Sam, `audit/FINAL_PRE_X13_INDEPENDENT_READINESS.md`, audited `9cbf2b6`). X13 remains NOT AUTHORIZED. X13 HAS NOT RUN. No real PCD-vs-E evidence result has been computed or inspected.**

Independent Gate 2 audit found the A11 benchmark, PROP-61 three-way-OR wiring, observer causal clock (X01/X02), storage/accounting, and all four hostile collector controls (F, PCD-R15, reverse-order, terminal archive) mechanically sound under adversarial hand-scored testing (see the report for the full breakdown). Four concrete, ordinary implementation gaps against `FINAL_PRE_X13_FREEZE.md`'s own explicit requirements block PASS: (1) an unguarded `KeyError` instead of fail-closed rejection when a retained-snapshot packet references a missing object; (2) no refcount/hidden-unreferenced-body validation and a cap-overflow check that silently no-ops without a supplied `declared_total_bytes`; (3) `validate_manifest()` checks `configuration_manifest.csv` by row count only, never re-hashing its content (or the source/accounting-fixture hashes also recorded in the manifest) against what's on disk; (4) the real executor never populates 17 required cost/overhead fields (synchronized byte-hours, per-row elapsed/CPU/RSS, auxiliary memory, E-policy queue stats) despite the underlying accounting function existing and being independently confirmed correct. All are Ubayd's Gate 1 engineering scope; none require reopening an annotation/methodology decision. No authorization artifact was created.

`docs/FINAL_PRE_X13_FREEZE.md` is the final methodology/benchmark/evaluator/checklist authority. `docs/X13_RUN_CONTRACT.md` amendment **FINAL_PRE_X13_DEADLINE_v1** is the current experiment scope; original v0 text remains historical where amended. Older `PRE_RESULTS_AUDIT.md`, `PRE_RESULTS_CLOSURE.md` and dated acceptance/status reports are evidence history, not additional gates or permission to override this freeze.

## Final benchmark disposition

**A11 CONTEXT FROZEN. A11 semantic inventory frozen before results.**

- 65 propositions: **38 development / 27 held-out**; critical **34 / 23**, total57. All65 have eligible nominal exact core support; primary held-out critical denominator **K=23**.
- 1,421 core occurrence rows (808 dev / 613 held-out); one excluded AI@2 support row, with PROP-63's valid AgentSecCountyVarAI@1 alternative retained. No whole-proposition exclusion.
- 25 groups (14 dev / 11 held-out). 52 catalog pages including context dependencies (30 / 22); no split overlap. Original pilot GRP-02 remains development.
- Eight context-needed propositions, **all eight groundable**; 57 self-contained. Ten context fragment definitions (eight body, two exact observable event predicates), 101 exact body-context occurrence rows. No unknown/unavailable context proposition in the frozen inventory; evaluator must nevertheless preserve NA semantics.
- PROP-20260616-61 is resolved as **three valid OR alternatives**: the older AgentIvyTuitionValues2015XQ, AgentDataUsaUnique5 and AgentIvyLink tuition queries. No unique intended referent, actual query execution or author knowledge is inferred. The claim that no matching source exists is withdrawn. Two context-only pages join existing held-out GRP-19 without new propositions/episodes.
- The 71 episode IDs (39 / 32) are **declared catalog entries only**, not validated evidence-bearing episodes. Original >=40 adjudicated-episode target and complete sampling/rejection provenance are not certified. The final study is explicitly **exploratory, prespecified finite-benchmark simulation**, not full-design confirmatory completion.
- Corrected raw-body Latin-1 projection and PROP-08 identity language retained. Directly inconsistent -04/-09 adjudication notes now describe observed warning/self-report rather than actual cleanup detection or independent agent identity. No core labels/quotations/critical flags changed in consolidation.

Canonical git-blob OIDs and SHA-256 hashes for all ten frozen benchmark artifacts are pinned in `FINAL_PRE_X13_FREEZE.md`. No semantic edits after outcome access except disclosed versioned post-outcome corrections retaining originals.

## Implementation state and remaining owners

| Component | Current status |
|---|---|
| E01 / E05 | Raw export validation and typed loading accepted with documented source limits |
| V02 / E06 / V07 | Trace/state reconstruction accepted with uncertainty/unknown conventions |
| R04 / E08 | Accounting contract and observer/storage implemented; full causal/as-of and export validation still part of final engineering |
| E09 / E10 | P/PD/PCD and bounded E(q) implemented; independent narrow cross-policy collector audit accepted |
| A11 | Final semantic/context freeze complete; exact current counts/pins above |
| E12 | Core candidate with independent19/19 mechanics; final independent PASS **pending** accepted-context integration and consolidated integrity tests |
| X13 | **NOT RUN, NOT AUTHORIZED YET**; Ubayd implements final checklist, Sam audits once |
| P14 | Must use the narrower claims and complete adverse-result disclosures in the final freeze |

Current E12 includes body-hash/post-checkpoint validation, DSE namespace/body-required core firewall, corrected export decoding, cross-title alternatives and per-alternative exclusion. Do not report those repairs as absent. Remaining integration must ensure context implies core, frozen OR-of-AND and exact-time event predicates, NA/unknown handling, canonical coordinate mapping, full packet/object/cap/feed integrity and DRAFT rejection. Prior CONDITIONAL PASS is not final acceptance of these new paths.

Ubayd's **one exact implementation checklist and file list** is `FINAL_PRE_X13_FREEZE.md` §4: common operation clock/as-of accounting, one-shot terminal directory/no backdating/delayed payload availability; F; online PCD-R15; reverse-title stress; terminal persistent archive; nominal/conservative masks; finalized E12; hashed deterministic/resumable runner; synchronized costs/overhead; all required tables/plots/NA/failed rows.

## Deadline scope (frozen outcome-blind)

**Option2 adopted: 791 logical collection/scoring rows + 61 evaluation-only conservative-mask families.** Full DSE background, May24 start, July15 endpoint, primary1MiB and all60 periodic phases retained.

- Primary P15/PD15/PCD15 and E30/100/300:183 rows.
- PCD5/60 intervals:120.
- PCD15/E30 latency cells (5,30),(60,0),(60,30) seconds:183, forming2x2 with primary(5,0).
- F:1; PCD-R15:60; reverse-title P/PD/PCD15 + E30:181.
- PCD15/E30 terminal archive augmentation:61; archive-only1MiB/uncapped:2.
- Stable-support re-score primaryPCD15/E30:61 families, no new collection runs.

Full v0 matrix, July3, broader cap grid, omitted rate/interval/latency cross-products and full chronology trajectory bounds are explicitly NOT_EXECUTED_SCOPE_AMENDMENT, not silently absent. Exact omissions and narrower permitted/forbidden claims are in the amendment. Essential repair/order/latency/archive/stable-mask outputs cannot be dropped because of time or unfavorable results. Full trajectory bounds remain NA; stable-mask results are not chronology-storage robustness bounds.

Primary unchanged: E30 versus PCD15 uniform60-phase mean, K23 critical core, practical threshold>=10pp, E30 requests<=**every** comparator phase and identical shared metadata access/accounting. No q promotion, favorable phase selection, label-dependent reruns or silent failed-row deletion. Null, reversal, below-threshold, unmatched and archive-collapse results remain valid. Incomplete essential matrix permits incomplete descriptive reporting only, not a completed-study primary claim.

## TWO gates only

1. **Engineering readiness — Ubayd:** complete final freeze §4, synthetic/data-only tests and offline reproduction, exact frozen manifest/mask hashes before scoring, report `audit/UBAYD_FINAL_ENGINEERING_READINESS.md` with candidate commit. No real capture/label join.
2. **Independent readiness — Sam:** one comprehensive independent audit against the pinned candidate, with fresh hand-scored synthetic expectations, authorship disclosure and data/hash/schema verification. Record `audit/FINAL_PRE_X13_INDEPENDENT_READINESS.md`. **Sam PASS simultaneously closes E12 and authorizes X13 on that exact code/manifest, without another broad Astra methodology review.** A genuine contradiction stops; implementation bugs are repaired within these same gates.

## Verification in this consolidation (not independent readiness)

Complete source review for all37 ordered-ID matches and both frozen deletion events. Data-only checks: `verify_annotations.py`65/65 evidence and1421/1421 occurrences PASS; `verify_a11_independent.py`0 failures; `verify_final_context.py`10 fragment definitions/101 occurrences PASS. Structural loader-only check valid,65 propositions/1420 core span fragments/K23/65 earliest support timestamps. No retained snapshot, policy coverage, delay result or X13 was computed/inspected. No full engineering test-suite PASS is claimed here.

## Historical custody

Prior status detail is preserved in git through baseline `ade1f4c` and the dated audit reports. Sam's original19/19 independent acceptance is `audit/E12_INDEPENDENT_ACCEPTANCE.md`; subsequent repairs do not manufacture a new signature. Alex's original context pass and Sam's checks are preserved, with the accepted reconciliation explicitly corrected for PROP-61 and stale64/65 eligibility. Final consolidation replaces the old chain of individual methodology prompts with the two gates above.

### READY FOR FINAL ENGINEERING PASS
