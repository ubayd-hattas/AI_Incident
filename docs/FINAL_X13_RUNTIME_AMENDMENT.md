# FINAL_X13_RUNTIME_v2 — outcome-blind runtime amendment candidate

**RUNTIME AMENDMENT BLOCKED — NOT FROZEN, NOT AUTHORIZED.**

This document is the current runtime-scope handoff and supersedes instructions to
execute the historical 791-row deadline roster. It does **not** establish a
replacement executable freeze. Earlier working drafts in this session called
v2 frozen prematurely; that designation is withdrawn before any outcome access.
`configs/x13_runtime_v2.json` is an exact **130-row candidate**, not authorization.
No historical failed-run record, v1 config, manifest, status or result was changed.

## 1. Outcome-access declaration and unchanged science

No scientific X13 result exists according to the supplied preservation record.
Zero completed historical rows and zero stable re-scores were reported. This
amendment session ran no X13 collection, evidence scoring, collector/annotation
join, or real coverage/unit-retention inspection. It read the requested scientific
contracts and performance reports, not raw annotations or evidence artifacts for
selection. Structural roster tests cannot independently prove all human access;
this declaration and the recorded tool operations provide that provenance.

Unchanged: benchmark semantics, annotations, criticality, evidence definitions,
evaluator and collection algorithms, PCD15/E30, token bucket, feed interface,
exact cost accounting, 1 MiB capacity, July15 endpoint and outcome labels.
Primary remains held-out critical core K=23 and
`D=100*(E30_core(K)-mean_60(PCD15_core(K)))`, with exact rational threshold
`D >= 10pp`. E30 must satisfy `R_E30 <= min_j R_PCD15_j` over **all 60**
primary phases, with identical shared access/accounting. Stable-mask denominator
changes follow existing rules only. No q promotion, favorable phase selection,
failed-row deletion or outcome-dependent scope change is allowed.

## 2. Performance evidence and why 791 rows cannot run

Read first: `audit/X13_PERFORMANCE_DIAGNOSIS.md`,
`audit/X13_RUNTIME_SCOPE_EVIDENCE.md`,
`audit/X13_FAILED_RUN_PRESERVATION.md`, and the complete
`audit/verify_performance_equivalence.py` implementation.

Candidate: `cc37a141777608a6f766b3c81f0ca9e8518645f1`.
Reported pre-amendment code-state identity:
`78c293efe22b5d90d839e34fd6119a476db14375e709b9233426d1fd5b2aaf60`.
These identify prior evidence, not the current changed candidate or Sam approval.

Manifest custody discrepancy found by hash-only checks: the cc37a14 Git blob has
SHA256 `0db63b0bc62fdf2c84fb1b3e01eb3b04715679a40c66e936b9175afdebcef62b`,
as reported. Starting HEAD `f51502e64e59ef67b2168e8e36801a045f3ffe88` and its
unchanged working manifest instead have SHA256
`5ac8b2a7cbda11710d03c597a88ad30dc38ffa3bb9434ffa9a1656e455ea14c5`.
Both raw and LF-normalized hashes agree at HEAD, so this is not CRLF conversion.
No manifest was regenerated or overwritten here. Sam must reconcile which
candidate/manifest each historical assertion refers to; this document does not
retroactively correct the preservation record.

- Five-day P15 before optimization: 154.869s; after: 21.199s;
  7.31x speedup and 41.39x traced-memory reduction.
- Instrumented rates: 523 GET/s before; 3,825 GET/s after.
  Untraced early-prefix rate: 18,461 GET/s.
- Full ordinal-1 P15 phase0 still incomplete after approximately one hour;
  observed RSS 612,515,840 bytes. Historical timeout: over 7,200s.
- Ordinal-1: 6,387,883 body GETs + 74,881 polls = 6,462,764 attempts.
- P/PD primary/reverse: 240 rows, 1,551,038,656 attempts, >10 serial days
  even using a one-hour representative-row lower bound.
- Exact equivalence verifier reportedly passed zero mismatches. It compares
  collector/storage projections, not evidence coverage. It was read, not rerun
  on real prefixes in this session. Sam must independently assess its scope.
- PCD-R counts depend on online repair/store state. No full-horizon measured
  count/runtime is available. F reached `AmbiguityLimitError` during terminal
  nominal membership construction, before evaluation.

A censored one-hour run gives a runtime **lower bound**, not a throughput floor.
Neither the five-day rate nor request ratios establish a full-horizon upper
runtime. PCD-R additionally scans retained provenance, builds dummy captures and
serializes repair metadata; those costs are not represented by counting GETs.

## 3. Historical roster

Preserve `configs/x13_deadline_v1.json`, `FINAL_PRE_X13_FREEZE.md` and historical
run files. v1 rows: L-primary 183, L-interval 120, L-latency 183, F 1,
R 60, O 181, A-live 61, A-only 2 = **791**; stable **61** families.
The old required-all-791 completion condition is historical; it is not permission
to execute that infeasible roster now.

## 4. Exact candidate roster and arithmetic

All continuous rows retain full DSE background, May24 start, July15 endpoint,
60s feed polls, nominal chronology and 1 MiB. Default lag5s/delay0s and forward
FIFO/exact dedup. No feed is added to F/A-only: lag/poll fields there are inert
schema values, and their frozen terminal semantics remain unchanged.

| Family | Candidate collection rows | Settings |
|---|---:|---|
| Primary PCD15 | 60 | j=0..59 |
| Primary E30 | 1 | no phase |
| PCD-R15 | 1 | j=0, diagnostic, feasibility unresolved |
| F | 1 | original final-state definition, required but blocked |
| PCD5 / PCD60 | 12+12=24 | diagnostic phases below |
| Latency PCD15 / E30 | 12+1=13 | lag60s/delay30s, diagnostic phases |
| Reverse PCD15 / E30 | 12+1=13 | reverse sweep title / reverse title ties only |
| Archive PCD15 / E30 | 12+1=13 | terminal persistent augmentation, same store |
| Archive-only | 2 | 1 MiB and uncapped |
| E100 / E300 | 2 | primary interface, secondary only |
| **Total** | **130** | 60+1+1+1+24+13+13+13+2+2 |

Stable arithmetic: all 60 primary PCD15 snapshots + primary E30 = **61**
evaluation-only families, zero recollection, core/context re-scores using the
same frozen stable mask. No diagnostic snapshot replaces a primary snapshot.

Primary phases: exactly `[0,1,...,59]`. Diagnostic phases:
`[0,5,10,15,20,25,30,35,40,45,50,55]`, the deterministic rule
`range(0,60,5)`. Actual offsets remain `j*Delta_us//60`. PCD-R j0 is selected
for deterministic compatibility with the existing walkthrough, not coverage.

## 5. Runtime planning table — assumptions, not measured completion

For transparent comparison only, use an assumed 500 attempts/s and show **2x**
time (equivalent to 250 attempts/s). This is below the measured early-prefix
rates, but is **not a demonstrated conservative full-horizon floor**. The
following request-volume screen therefore cannot certify deadline feasibility.
No perfect linear scaling, parallelism or prefix reuse is assumed. Evaluation,
source/model setup, repair scans and reporting have no measured budget here.

| Family | Candidate rows | Attempts estimate / bound | 2x request-time screen | Purpose / tier | Decision / reason |
|---|---:|---:|---:|---|---|
| Primary PCD15 | 60 | <=4,935,720 | 5.48h | primary mean / 1 | retain all; highest priority |
| Primary E30 | 1 | <=84,074 | 0.094h | primary contrast / 1 | retain once |
| U-stable | 61 re-scores | 0 new collection | unmeasured evaluator time | support robustness / 1 | retain all primary snapshots |
| PCD-R15 j0 | 1 | <=6,462,865 proposed attempt ceiling | 7.18h, **not a repair runtime bound** | repair mechanism / 1 | retain diagnostic pending feasibility |
| F | 1 | unknown completed count; <=5,155 requests if membership can be constructed | request-only <=0.006h; membership blocked | terminal live baseline / 1 | retain; do not disguise engine failure as scope omission |
| PCD5/PCD60 | 24 | <=1,972,620 | 2.192h | interval diagnosis / 2 | retain sampled, omit 96 phases |
| Latency | 13 | <=1,071,218 | 1.190h | strongest declared joint degradation / 2 | retain sampled, omit 170 rows |
| Reverse | 13 | <=1,071,218 | 1.190h | FIFO/service-order diagnosis / 2 | retain sampled |
| Archive augmentation + only | 15 | <=1,272,278 | 1.414h | recoverability sensitivity / 1 | retain sampled plus capped/uncapped ceilings |
| E100/E300 | 2 | <=168,148 | 0.187h | secondary q / 2 | retain; never promote |
| P/PD primary/reverse | 0 of 240 | 1,551,038,656 omitted | >10 days empirical screen, >20 days with 2x | exhaustive baselines / 3 | omit dominant workload |
| Other PCD-R phases | 0 of 59 | counts unmeasured; 59*6,462,865 coarse ceiling | request-only screen up to 423.7h | broad repair diagnosis / 1 | omit broad grid provisionally; j0 unverified |
| Omitted interval phases | 0 of 96 | <=7,890,480 | 8.77h | exhaustive interval phases / 3 | omit |
| Omitted latency rows | 0 of 170 | <=13,988,164 | 15.54h | exhaustive factorial / 3 | omit |
| Omitted reverse PCD phases | 0 of 48 | <=3,948,576 | 4.39h | exhaustive order grid / 3 | omit |
| Omitted archive PCD phases | 0 of 48 | <=4,591,968 | 5.10h | exhaustive archive grid / 3 | omit |

PCD-R attempt ceiling reasoning for Sam to check: at a nominal zero-delay sweep,
its dirty/repair union is visited once and is a subset of P's believed-live/mixed
sweep candidates, using the same feed and phase. This does not bound CPU per
attempt or pre-sweep work and must not be represented as a measured R count.
F's 5,155 ceiling is one directory plus at most 5,154 mutation-addressed titles;
it does not solve directory ambiguity or justify preloading any title.

Low-request families total <=10,575,276 attempts. Adding the proposed R ceiling
and F membership-success ceiling gives **<=17,043,296 attempts**, conditional on
those bounds. The linear screen is 9.47h base, **18.94h with 2x**. A genuine
conservative total execution estimate remains **UNESTABLISHED**, not 18.94h.
There is no supplied numerical deadline/remaining wall-clock allocation, and no
measured setup/scoring/reporting allowance. Consequently this draft cannot claim
that substantial audit/report/QA time remains. That is a blocking requirement,
not permission to silently use a smaller safety factor or drop R/F.

## 6. Decisions and exact omissions

- P/PD: omit all 240 v1 primary/reverse rows. This does not redefine the primary.
- PCD15: retain all60; no evidence supports sacrificing its primary phase mean.
- PCD-R: propose j0, not all60. Broad coverage is not known cheap. Even j0 is
  not demonstrated feasible; lack of measurement is not proof it is infeasible.
- F: retain required. `AmbiguityLimitError` is an implementation/nominal-model
  blocker, not a scientific zero or a runtime-amendment omission.
- Archive: propose 12 fixed primary PCD prefixes + E30 and both archive-only
  rows. All held revisions remain enumerated/charged, no annotation selection.
  Use the corresponding same-phase live prefixes for pre/post comparison.
- Reverse: PCD diagnostic phases/E30 only; no P/PD recollection.
- Latency: retain (60,30), the strongest previously specified joint degradation.
  Compare the same 12 nominal primary phases; no factorial interaction claim.
- Intervals: both shorter5 and longer60 on12 evenly spaced phases.
- Stable: retain61, no recollection.

Candidate v1-to-v2 partition: 130 retained + **661 omitted** = 791.
Disjoint runtime omissions: P/PD240 + R59 + latency170 + intervals96 +
reverse PCD48 + archive PCD48 =661. These use
`NOT_EXECUTED_RUNTIME_AMENDMENT`. Phase complements are relative to j0..59,
never a coverage-selected set. PCD-R/secondary cuts are provisional workload
prioritization within this blocked candidate, not empirical feasibility findings.

All pre-existing v0-to-v1 omissions keep **NOT_EXECUTED_SCOPE_AMENDMENT**:
July3, other live caps, Delta1, P/PD5/60, q100/300 outside primary, lag30,
delay5, secondary R/O/A cross-products, P/PD archive prefixes, other capped
archive-live rows and both trajectory-enumeration families. Their reasons must
not be retroactively rewritten as runtime measurements. The config preserves
these separately in `historical_omissions`.

## 7. Mandatory report claim restrictions if this candidate is frozen

1. The reduced deadline study compares event-derived monitoring primarily with
   changed-only periodic collection; it does not comprehensively compare every
   periodic baseline.
2. PCD-R is a prespecified phase0 diagnostic, not a phase-averaged repair
   estimand. No general repair-robustness or general event-driven superiority
   claim is supported by that single phase. Publish its costs and adverse
   findings beside the primary contrast.
3. Latency sensitivity is diagnostic rather than factorial; notification lag
   and GET delay effects/interactions cannot be separately identified.
4. Interval comparisons use prespecified diagnostic phases and are not
   phase-averaged estimands equivalent to the primary analysis. Do not claim
   15 minutes optimal or interval-wide robustness.
5. Archive sensitivity tests vulnerability on prespecified configurations, not
   every phase. Persistent terminal recovery is hypothetical, atomic and costed;
   it is not evidence of historical archive availability or permanent erasure.
6. Reverse-order sensitivity applies to the tested PCD/E configurations only;
   no all-phase order-invariance or exhaustive baseline claim.
7. E100/E300 are secondary, never replacements for E30. Old restrictions on
   endpoints/caps, trajectories, representative incidents, optimal collection,
   equal total costs and historical responder loss remain binding.
8. F failure must remain explicit; it cannot be plotted as zero or omitted to
   declare study completion. Required-row failure yields incomplete descriptive
   reporting, not a completed-amendment headline.

All executed costs/unknowns/context/delay/groups/phase tables remain mandatory.
Keep the fixed construction/ZZZ development walkthrough with retained j0 rows;
mark P/PD absent and do not choose a replacement case. Diagnostic summaries must
name their actual phase lists; only the primary uses mean_60. Full chronology
ranges remain NA and stable re-scores are not shared-world trajectory bounds.

## 8. Mechanical work and validation boundary

`src/ebe/x13_runtime_v2.py` is a pure candidate roster expander. Its deterministic
IDs describe roster coordinates only, **not execution IDs** (no source/code/mask
pins). It rejects execution use while config status is blocked. It validates
exact phase sets, row arithmetic, uniqueness, stable source mapping and the full
v1 retained/omitted partition without loading annotations, evidence or collectors.

**Production manifest/runner plumbing was not changed.** Exploratory partial
edits were reverted rather than leaving v2 generation wired to v1 authorization,
stable-rescore detection or paths. Existing v1 generation remains reproducible
when explicitly selected, but old manifests cannot authorize changed code.
No manifest, stable mask, authorization or X13 output was generated here.

Ubayd must, inside the combined gate's engineering repair loop:
- thread explicit amendment/config selection through manifest, runner and CLI;
  no globals or silent fallback to791, no new hard-coded cross-products;
- read config from the selected repository, validate exact coordinates/counts,
  bind source/code/annotations/mask/config plus amendment into execution IDs;
- persist explicit61 stable source links and disjoint661 runtime omissions,
  retaining historical scope omissions and v1 reproduction separately;
- validate manifest row contents/IDs, not merely self-reported counts/hashes;
- use fresh v2 paths only; real mode validates rather than regenerates an
  authorized manifest, and must reject missing/stale/v1 authorization;
- route stable detection and diagnostic-phase reporting through the config;
- test wrong amendment, hidden/duplicate rows, mutated config, stale auth,
  synthetic resume and both version paths. Never weaken old integrity tests to
  make a stale historical manifest appear current.

## 9. One combined independent gate and exact next owner

**Sam — one combined independent audit of the performance-equivalent code
changes and FINAL_X13_RUNTIME_v2 amendment, followed by fresh authorization if
PASS.** No further broad Astra review follows Sam.

Sam must independently audit (1) the performance changes reachable from cc37a14,
(2) exact equivalence evidence and its bounded-prefix limitations, (3) this
outcome-blind basis, (4) final v2 config/roster and claim restrictions, and (5)
any final mechanical plumbing. This draft is **not eligible for PASS yet**:

A. Establish outcome-blind full-horizon cost evidence for low-request and repair
paths, including setup/scan overhead, or a justified non-linear conservative
bound. Do not score evidence or print retained units to obtain performance data.
Use at least2x safety plus explicit setup/evaluation/reporting allowances.

B. Resolve F's terminal ambiguity-limit blocker without changing nominal
semantics, selecting membership or redefining failure as missing evidence.
An actual methodological contradiction must be disclosed, not hidden by scope.

C. Record actual remaining wall-clock budget with substantial Sam audit,
execution, scoring/report writing and QA reserves. The user supplied no numeric
budget, so this session cannot invent one or assert that18.94h fits it.

D. Complete and independently test the mechanical steps in §8. All scope
choices must be frozen before outcome access; the final code and config must
be the ones Sam checks. Ordinary engineering defects return to Ubayd within
this same gate, not a new broad review sequence.

E. Reconcile the starting-HEAD versus cc37a14 manifest identity discrepancy in
§2 without rewriting historical failed-run records or importing old authorization.

When all blockers are closed outcome-blind, Sam checks the final candidate,
regenerates/verifies a **fresh v2 manifest**, and pins its exact hashes in the
combined PASS and fresh authorization. Only then execute immediately. No real
mode may run on this blocked draft, the old791 roster, or an old authorization.

## 10. Validation actually completed in this session

Command:
`python -m pytest tests/test_x13_runtime_v2_roster.py tests/test_x13_manifest.py tests/test_x13_runner_synthetic.py tests/test_x13_reporting_synthetic.py tests/test_final_controls.py tests/test_collectors.py -q`

Final result: **113 passed in40.09s**. `git diff --check` passed.
Tests cover exact130/61 arithmetic, all60 primary phases, every diagnostic
coordinate, deterministic IDs, no duplicate/hidden rows, F and Rj0 present,
all661 omitted v1 coordinates and their reasons, preserved historical omission
reasons, stable-source links, mutated candidate rejection and blocked execution.
A file-read guard permits only the candidate config during expansion/partition;
no annotation/evidence files are used for roster selection. Existing synthetic
collector/control/accounting/reporting tests ran without real evidence scoring.

Earlier failures were not suppressed: historical validation correctly rejected
changed code; its test now verifies the unchanged starting manifest digest and
that rejection. The authorization test uses an invented validated-manifest stub
in a temporary directory so it tests the independent lock rather than first
failing on a stale manifest. No production integrity check was weakened.
The initially assumed historical hash mismatch was investigated and disclosed
in §2, not repaired by regenerating a historical artifact.

Files changed/added: this document; `docs/X13_RUN_CONTRACT.md`;
`docs/PROJECT_STATUS.md`; `configs/x13_runtime_v2.json`;
`src/ebe/x13_runtime_v2.py`; `tests/test_x13_runtime_v2_roster.py`;
`tests/test_x13_manifest.py`; `tests/test_x13_runner_synthetic.py`.
Production collector/evaluator/manifest/runner/reporting/CLI files are unchanged.

## 11. Final disposition: blockers did not all close, no authorization issued

Sam's combined audit (`audit/FINAL_PRE_X13_INDEPENDENT_READINESS.md` sections
12-13) closed blockers D and E outright (mechanical plumbing confirmed inert
against real execution; the manifest-hash discrepancy in section 2 above was
benign, the two hashes describe two different things, a stale checked-in
freeze artifact versus a fresh regeneration at a later commit) and made real
progress on A (empirically timed the low-request tier at roughly 12 hours
serial), but blockers A, B, and C did not fully close. PCD-R specifically was
given two independent, equivalence-verified bug fixes and still did not
complete a full-horizon run in any tested window, so it should be treated as
comparable in cost to the infeasible P/PD rows, not to plain PCD. F's
`AmbiguityLimitError` was root-caused to one specific page and one specific
missing exception handler, and was deliberately left unfixed because the
correct behavior requires a real decision about F's frozen contract
semantics, not a same-semantics performance fix. No numeric deadline/reserve
budget was ever supplied for blocker C.

**No fresh v2 manifest was regenerated, no combined PASS was issued, and no
real execution was authorized on this candidate.** The project's actual final
submission is an honest incomplete-execution report (`report/report.tex`),
not a completed run under this amendment.
