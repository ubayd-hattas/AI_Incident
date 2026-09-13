# Ubayd final engineering readiness — FINAL_PRE_X13_DEADLINE_v1

Audited 2026-09-13 (Africa/Johannesburg) against commit
`f1552717b43eec6c8d4eee1f4e7d3777988d46dc` and frozen working candidate
code-state SHA-256
`d3b7bde8bdd0ecba975a8c5aa43e572db9a6bd9ff9e28887fc9713f6b69d0fca`.
This report is Gate 1 engineering evidence, not independent authorization.

## 1. Files changed

- Observer/storage/accounting: `src/ebe/observer.py`,
  `src/ebe/storage.py`, `src/ebe/accounting.py`.
- Collectors/controls: `src/ebe/collectors.py`,
  `src/ebe/terminal_archive.py`.
- E12: `src/ebe/a11_loader.py`,
  `src/ebe/a11_loader_context_draft.py`, `src/ebe/evaluator.py`,
  `src/ebe/support_masks.py`, `docs/E12_EVALUATOR.md`.
- X13: `configs/x13_deadline_v1.json`, `src/ebe/x13_manifest.py`,
  `src/ebe/x13_runner.py`, `src/ebe/x13_reporting.py`,
  `scripts/reproduce_x13.py`, `docs/X13_REPRODUCIBILITY.md`.
- Audits/tests: the three superseded audit expectations, five existing contract
  test files, `tests/conftest.py`, all seven required final test modules, and
  `tests/fixtures/final_x13_controls.json`.
- Generated pre-score/result/synthetic artifacts under
  `runs/FINAL_PRE_X13_DEADLINE_v1/`.

## 2. Observer integrity

PASS. One monotonic operation clock governs polls, GET dispatch, delayed
completion, terminal directory, and terminal GET. Delayed GET returns an opaque
handle and exposes outcome/body only through due completion. Terminal directory
is one-shot, terminal-only, state-derived, lexicographic, and mutually exclusive
with feed use. As-of cost reconstruction filters dispatches at/after C while
retaining the special charged terminal abstraction at T; future polls,
responses, headers, and payloads cannot alter earlier totals. Zero-delay request
sequence ordering is preserved.

## 3. Final controls

- F: PASS. One charged T directory, no feed, lexicographic atomic GET, 1 MiB,
  exact dedup/FIFO, explicit outcomes. Invented hand-counted test passes.
- PCD-R15: PASS. Online last-completed hash/length repair metadata, no body
  cache, title provenance, current-cap prospective packet-width check, ordinary
  work priority, sweep-start union, no same-sweep retry, and repair after
  eviction. Roster has 60 phases.
- Ordering stress: PASS. Periodic service reverses titles; E preserves oldest
  event time and reverses only equal-time title ties. Roster has 181 rows.
- Persistent archive: PASS. Whole held-DSE enumeration at T, frozen sort,
  charged metadata/GETs, continuing prefix sequence, shared cap/dedup/FIFO,
  reconstructable exact prefix store, A-live 61 rows, and A-only capped plus
  uncapped. Repeated bodies still issue GETs; invented sequence/dedup test
  passes.

## 4. E12 final context integration

PASS. The loader accepts and pins all three accepted context files and rejects
DRAFT basenames. Diagnostic loads are non-scoreable. Body encoding follows
Latin-1 raw projection -> strict declared codec -> canonical Unicode/UTF-8.
Required context is core × extra-context DNF; self-contained context equals
core. Context can never satisfy absent core. PROP-20260616-61 expands all
eligible cores across three independently sufficient context branches. Body
context uses exact frozen page/hash/span provenance; events use exact
page/action/event-time/delivery/multiplicity. Unknown/unavailable states remain
in the denominator with exact lower/upper numerators. Delay keeps AND-latest,
OR-earliest, actual capture time, and rejects negative delay.

## 5. Stable support mask

PASS. The data-only compiler reads frozen source chronology and frozen
occurrence identities, not collector outcomes. It emits 1,522 records (1,421
core plus 101 context occurrences): 1,516 eligible intervals and 6 explicit
`EMPTY_UNCERTAINTY_INTERSECTION` exclusions. Equal-text continuity and closed
uncertainty separation are deterministic; capture time is checked against the
compiled interval during the 61 U-stable re-scores. U-stable is evaluated from
the same primary collection snapshots and never reruns collectors.

Mask SHA-256:
`78081b810fbcc277cdeade86f6dd61d4ca4fd25025d57c94f353329095787093`.

## 6. Benchmark and pins

PASS: 65 propositions; 38 development; 27 held-out; 57 critical; 34 development
critical; 23 held-out critical; K=23; 25 groups; 1,421 core occurrence records;
8 required-context propositions; 57 self-contained; 10 context definitions
(8 body, 2 event); 101 exact context-body occurrence rows; one excluded
`PROP-20260618-63 / dse~AI@2` support revision with its eligible alternative
retained. All ten canonical annotation hashes exactly match
`docs/FINAL_PRE_X13_FREEZE.md` and the generated benchmark manifest.

## 7. Manifest and omitted scope

PASS. `configuration_manifest.csv` contains exactly 791 logical collection
rows with block arithmetic 183+120+183+1+60+181+61+2. Exactly 61 U-stable
evaluation-only families are declared. Canonical JSON uses sorted compact UTF-8
keys, integer microseconds, and literal nulls. IDs bind amendment, block, full
config, source hash, code commit, benchmark hashes, and mask hash.

`omitted_scope.csv` contains 12 explicit removed-v0 families, each marked
`NOT_EXECUTED_SCOPE_AMENDMENT`; omissions are separate from runtime failures.

Run-manifest SHA-256:
`e5109dff54f6cffa6f4d5827f88cd0e7675d9ef8d4ab4a1a8a37e41cc46fe4ea`.

## 8. Runner, costs, reporting, reproduction

PASS. The runner is offline, deterministic, append-only, resumable, and
writes atomic per-row artifacts plus checksums. It preserves attempts/errors,
detects missing/corrupt completed artifacts, refuses scientific-identity
mismatch, marks unsupported nominal responses not evaluable, and never performs
coverage-driven stopping. Real mode checks a future independent authorization
artifact before lazily importing source, benchmark, collectors, or evaluator;
the post-authorization executor is wired but was not invoked.

The logical result schema covers request decomposition, all outcomes, transfer
lower bounds/NA payloads, S packet/body/object/refcount/eviction accounting, M,
synchronized S+M and exact byte-microseconds, runtime/RSS/disk/auxiliary
measurements, queue/pending/coalescing/starvation/drop fields, and reuse
provenance. Unknown quantities use null, never zero.

Synthetic reporting uses exact rational percentages, the fixed 10 pp decision
boundary, all required labels, strict request admissibility, all-60 phase
summaries with linear (n-1)p quantiles, equal-proposition/group summaries, and
leave-one-group-out ranges. Header-only future result schemas and six
deterministic plot generators exist; Gate 1 generated no real plots.

Offline reproduction regenerated the mask/manifest/scaffolding, completed an
invented 17-row interrupted prefix, then resumed the remaining 774 rows. Final:
791 synthetic row JSON files plus 791 matching checksum files, zero errors and
zero missing. The final status-log write interval was 47.928 s; a prior explicit
17+774 resume measured the 774-row segment at 29.484 s and 38,891,520 bytes RSS
at process end (synthetic harness only; not peak RSS and not deployment
efficiency). A no-op checksum/resume verification on the final identity used
2.645 s and ended at 38,629,376 bytes RSS.

## 9. Verification log

- `pytest -q`: PASS — 209 tests, 5 subtests, 91.89 s.
- `python audit/verify_annotations.py`: PASS — 65/65 and 1,421/1,421.
- `python audit/verify_a11_independent.py`: PASS — 0 failures.
- `python audit/verify_final_context.py`: PASS — 65/10/101, no scoring.
- `python audit/verify_e12_independent.py`: PASS — 0 failures.
- `python audit/verify_accounting.py`: PASS — 9/9 fixtures.
- `python audit/verify_e08_neutrality.py`: PASS — 0 failures.
- `python audit/verify_collectors_cross_policy.py`: PASS — 0 failures.
- Manifest generation/validation: PASS — 791 + 61 and pinned mask hash.
- Synthetic interrupt/resume: PASS — 17 + 774 = 791.
- Synthetic reporting/reproduction: PASS.
- `git diff --check`: PASS.

The three audit changes are narrow authority updates: E12 Case K now tests
frozen self-contained context, delayed observer verification resolves its
opaque handle only at completion, and the neutral observer surface recognizes
`complete_due`. No audit was weakened around source, accounting, provenance,
retention, or scoring.

## 10. Unresolved bugs and outcome-access declaration

Known Gate 1 engineering blockers: none.

No real X13 collector/evaluator join was executed. No real policy/evidence
score, PCD-vs-E coverage, D value, favorable phase/case, or real plot was
generated or inspected. Synthetic values are explicitly marked
`SYNTHETIC_INVENTED`. X13 remains unauthorized.

### GATE 1 PASS — READY FOR SAM

Exact next owner: **Sam — comprehensive Gate 2 independent readiness audit.**

## 11. Gate 2 repair continuation handoff (Jaswin)

Ubayd completed the substantive Gate 2 repair implementation through commit
`b10596f2b7e4bd490b07479d09a7afe32bd48f01` before reaching his usage limit.
Jaswin continued from that exact state without changing annotations, K, the
791-row roster, policies, or frozen experiment parameters. The final engineering
code commit is:

`1e46f23837cd8c319f504acf01128a14a01d6967`

This section is an engineering handoff only. It does **not** claim independent
acceptance, create Gate 2 authorization, or authorize real X13.

### Snapshot integrity

PASS on synthetic/adversarial fixtures. The retained adapter and validator now
fail closed with `SnapshotIntegrityError` for missing packet object references
(no raw `KeyError`), incorrect object refcounts, hidden/unreferenced objects,
duplicate request sequences, derived retained bytes over cap even without a
declared total, and declared-total mismatches. One-reference objects,
correctly-refcounted shared bodies, and exact-cap snapshots pass.

### Delayed PCD-R

PASS. The frozen primary R rows remain delay0. Synthetic nonzero-delay PCD-R
supports opaque pending handles and completion-event replay. A pending request
suppresses repair; successful completion clears pending state and refreshes
last-known hash/length; unavailable completion disables repair until a later
known completion. Tests cover no same-sweep feedback, sweep-only retries,
unchanged ordinary dirty work, and unchanged primary delay0 request behavior.

### Runner cost/overhead wiring

All 17 fields identified by the independent Gate 2 failure are now assigned a
real measurement/derived value or an explicit contract-valid NA:

1. `synchronized_peak_s_plus_m` — derived by the existing verified
   `synchronized_accounting(...)` over merged S/M step ledgers.
2. `combined_byte_microseconds` — from that same synchronized result; no
   duplicate byte-hour arithmetic.
3. `elapsed_seconds` — `time.perf_counter()` per independently executed row.
4. `cpu_seconds` — `time.process_time()` per independently executed row.
5. `rss_bytes` — platform process RSS when available, otherwise explicit
   `NA_RSS_UNAVAILABLE_ON_PLATFORM`.
6. `artifact_disk_bytes` — fixed-point serialization records the exact persisted
   row JSON byte count.
7. `aux_collector_bytes` — measured PCD-R repair-metadata peak where exposed;
   explicit in-process non-separability NA otherwise.
8. `aux_store_bytes` — explicit in-process non-separability NA.
9. `aux_evaluator_bytes` — explicit in-process non-separability NA.
10. `pending_index_peak` — actual E event-derived pending/dirty-index peak; NA
    for non-E rows.
11. `queue_peak` — actual E maximum queue depth; NA for non-E rows.
12. `coalesced_updates` — actual E coalescing count; NA for non-E rows.
13. `starvation_events` — actual E token-starved dispatch opportunities; NA for
    non-E rows.
14. `dropped_work` — zero only for E's actual no-drop implementation; NA for
    non-E rows.
15. `reused_from` — explicit `NA_NOT_REUSED`; this runner performs every logical
    row independently and therefore does not fake reused runtime/RSS.
16. `feed_metadata_bytes` — actual observer feed-response metadata bytes (zero
    only on terminal controls that do not use a feed).
17. `directory_metadata_bytes` — actual observer/terminal directory metadata
    bytes, with zero only where no directory is used.

Synthetic rows continue to use visibly synthetic, reason-bearing NA markers;
unknown and non-applicable values are not silently converted to zero.

### Observer/storage regression status

PASS. The complete regression retained X01 as-of accounting, X02's monotone
operation clock, delayed-response opacity, one-shot terminal directory and
feed/directory mutual exclusion, FIFO ordering, exact deduplication/refcounts,
oversize-before-eviction, and synchronized S/M accounting. No observer/storage
methodology or frozen policy behavior was redesigned.

### Final regression and freeze

Against engineering commit `1e46f23837cd8c319f504acf01128a14a01d6967`:

- `pytest -q`: **240 passed, 5 subtests passed**.
- `verify_annotations.py`: PASS (65/65 propositions; 1,421/1,421 occurrences).
- `verify_a11_independent.py`: PASS (0 failures).
- `verify_final_context.py`: PASS (65 dispositions, 10 fragments, 101 context
  body occurrences; no scoring).
- `verify_e12_independent.py`: PASS (0 failures).
- `verify_accounting.py`: PASS (9/9 fixtures).
- `verify_e08_neutrality.py`: PASS (0 failures).
- `verify_collectors_cross_policy.py`: PASS (0 failures).
- `verify_final_x13_readiness.py`: PASS (`FINAL GRAND TOTAL FAILURES: 0`).
- `git diff --check`: PASS.

The synthetic/pre-score freeze was regenerated only after the engineering commit
and validated. It contains exactly 791 collection rows with block arithmetic
183+120+183+1+60+181+61+2, 61 U-stable evaluation-only families, and 1,522
stable-mask rows (1,516 eligible / 6 excluded). Its identities are:

- run-manifest SHA-256:
  `0db63b0bc62fdf2c84fb1b3e01eb3b04715679a40c66e936b9175afdebcef62b`
- code-state SHA-256:
  `cf8ea748b833021846103a5d3957c6842ff44003ba13019b204080fd5b341aaa`
- configuration SHA-256:
  `eee7daf08974174911b8c136d4f37de395b49dba965fd1061ca1e915c3288ee4`
- omitted-scope SHA-256:
  `a6e3574468639e663dee87e4ad5b3dc871fbe66a7bbbc58a294d39b68f0bf8b2`
- source identity:
  `d11cc37ecf2d4f7bb0581b3dd480540d7f198a14b47861f3632a773c4892b943`
- accounting-fixture identity:
  `396bd57ac61115390307d5bf91e2199c98aed3dadf2cbb165f7755d3f34f16ed`
- stable-mask SHA-256:
  `78081b810fbcc277cdeade86f6dd61d4ca4fd25025d57c94f353329095787093`

Unresolved engineering blockers: **none known**. Independent acceptance remains
unresolved by design and belongs to Sam. No real collector/evidence join,
coverage result, D calculation, unit-retention result, phase comparison, real
X13 plot, or favorable parameter selection was generated.

### GATE 2 REPAIR PASS — READY FOR SAM RE-AUDIT

**Exact next owner: Sam — final comprehensive Gate 2 re-audit and authorization
decision.**
