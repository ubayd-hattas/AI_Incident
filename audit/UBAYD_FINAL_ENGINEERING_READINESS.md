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
