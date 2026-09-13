# E12 independent acceptance review (Sam)

**Audited commit:** `db39ce5aaa44d6b779d5a6b8518d5c115a1d7868`, initially clean working tree.

**Role and disclosure:** independent validation (Sam). I authored the original E12 substrate
(`src/ebe/evaluator.py`, `src/ebe/a11_loader.py` as first written, `tests/test_evaluator.py`,
`tests/test_a11_loader.py`) before Ubayd's subsequent rewrite (`1fb21f5`, `055b5c9`) and Jaswin's closure review
(`docs/PRE_RESULTS_CLOSURE.md`, baseline `9a7ab4c`). This review does not treat my own prior authorship, my own
prior "0 failures" claims, or Ubayd's/his tests' PASS reports as independent evidence — every claim below was
re-derived or executed fresh against the current commit. Where this review finds my own earlier work wrong, it says
so plainly.

**Scope discipline honored throughout:** no PCD-vs-E real evidence comparison was run. No policy parameter or label
was modified based on a collector outcome. No real X13 result was sought, computed, or inspected.

## Summary verdict

### E12: CONDITIONAL PASS

The coverage/delay *mechanics* are correct on every hand-scored case I independently constructed (19/19, including a
genuine eviction scenario neither my nor Ubayd's tests previously exercised). The denominator reconstruction matches
Ubayd's reported counts exactly. But real, reproducible, currently-unfixed defects remain in exactly the two places
`docs/PRE_RESULTS_CLOSURE.md` §9 named as required before acceptance: the retained-snapshot integrity boundary (A04)
and the population/denominator firewall (A05). Neither is a "small implementation nit" — both allow a
maliciously or accidentally corrupted snapshot to silently inflate coverage. **Exact fixes required, listed below.**

### X13: remains NOT AUTHORIZED (unaffected either way by this review)

## 1. Independent denominator reconstruction

Recomputed directly from `annotations/evidence.jsonl`, `eligibility.jsonl`, `splits.json` (not by calling the
loader/evaluator for the "expected" side — only the observed side goes through `load_a11_benchmark`):

| Quantity | Independently recomputed | Ubayd's report | Agreement |
|---|---:|---:|---|
| Total propositions | 65 | 65 | ✅ |
| Dev / held-out | 34 / 31 | 34 / 31 | ✅ |
| Critical | 57 | 57 | ✅ |
| Eligible / excluded | 64 / 1 | 64 eligible, 1 frozen exclusion | ✅ |
| Held-out critical eligible (nominal K) | 27 | 27 | ✅ |
| Complete support alternatives | not independently counted as a headline number; individual alternative construction spot-checked in §5 | 1,391 | not separately reconciled — see §5 for the actual alternative-construction check, which is the substantive claim behind this count |

**No disagreement found** on the reported denominators themselves. This matches `docs/PRE_RESULTS_CLOSURE.md` §6's
own recomputed inventory table exactly, and both independently agree with Ubayd's report. This is real, verified
agreement — not something to wave through uncritically, but not a place I found a problem either.

## 2. Retained-snapshot boundary — confirmed BLOCKER, not fixed

Constructed a `RetainedSnapshot` directly (not via any collector), bypassing every upstream check, to test the
evaluator's own runtime validation in isolation:

```python
tampered = RetainedBodyRecord("dse~X", capture_time_before_checkpoint, b"REAL CONTENT", "BADHASH_DOES_NOT_MATCH_BODY")
# fragment requires substring "REAL CONTENT" on dse~X
# -> compute_core_coverage(...).numerator == 1
```

**Result: numerator = 1.** The evaluator never recomputes `hashlib.sha256(record.body).hexdigest()` and compares it
to `record.body_sha256` anywhere in `fragment_satisfied`/`core_covered`/`_coverage`. A `RetainedBodyRecord` whose
claimed hash doesn't match its own bytes is silently trusted.

```python
post_checkpoint_body = RetainedBodyRecord("dse~Y", checkpoint + timedelta(hours=1), b"FUTURE CONTENT", "irrelevant")
snap = RetainedSnapshot(checkpoint, (post_checkpoint_body,), ())
# -> compute_core_coverage(...).numerator == 1
```

**Result: numerator = 1.** Nothing checks `record.capture_time <= snapshot.checkpoint`. A body recorded as captured
*after* the snapshot's own checkpoint still counts as retained-at-C evidence.

I also confirmed a **genuine FIFO eviction** (not the zero-cap/never-admitted case both my and Ubayd's existing
tests use) correctly produces zero coverage — see Case H below — so the *retained_evidence source* is sound; the
gap is specifically that `RetainedSnapshot`/`from_collector_result` carries no packet/object/hash/cap/time
provenance to validate against, and nothing at the evaluator boundary re-derives or re-checks it. This exactly
matches `PRE_RESULTS_CLOSURE.md` §4/§9(1)'s description, and it is **still true at the current commit** —
`RetainedSnapshot`'s fields (`page_key`, `capture_time`, `body`, `body_sha256`) are unchanged from what I originally
wrote; no validation was added in Ubayd's revision.

**Smallest required fix:** in `fragment_satisfied` (or a new `RetainedSnapshot.__post_init__`/validation step run
once at construction), for every `RetainedBodyRecord`: (a) recompute `hashlib.sha256(body).hexdigest()` and reject
construction/raise if it disagrees with the record's own `body_sha256`; (b) reject if `capture_time > checkpoint`.
Both are cheap, structural, and do not require any new external provenance — they only require trusting the
`body` bytes already present over the `body_sha256`/`capture_time` fields that currently go unchecked.

## 3. A05 population firewall — confirmed BLOCKER, not fixed

`validate_population` correctly rejects:
- duplicate `evidence_id` ✅
- dangling fragment reference ✅

It does **not** reject (independently constructed, both accepted with no exception raised):
- a fragment whose `page_key` is outside the `dse~` universe entirely (e.g. a different wiki, or no recognizable
  prefix at all) — **no DSE-universe check exists anywhere in `validate_population`**.
- a critical, eligible proposition whose *entire* core support is a single `observable_feed` fragment, with zero
  `body_span` fragments anywhere in any alternative — `X13_RUN_CONTRACT.md` §4 explicitly requires "every core
  alternative of a body-grounded unit must require at least one body fragment," and nothing enforces this.

Both are exactly the class of gap `docs/PRE_RESULTS_CLOSURE.md` §9(2) requires closed ("enforce DSE... universes...
body-required core"). Confirmed still open at the current commit.

**Smallest required fix:** in `validate_population`, add (a) a check that every `Fragment.page_key` starts with the
frozen DSE prefix (`dse~`) — reject otherwise; (b) for every alternative in `core_alternatives`, require at least
one fragment of `kind == "body_span"` — reject an all-`observable_feed` alternative.

## 4. Independently hand-scored cases A–K

Full script: `audit/verify_e12_independent.py`. Every expected value below was written down (as a code comment or a
literal) before the corresponding evaluator call — not derived by running the evaluator first, and not copied from
`tests/test_evaluator.py`.

| Case | Setup | Independently expected | Result |
|---|---|---|---|
| A | one proposition, one exact retained span | numerator=1, denominator=1 | ✅ PASS |
| B | two alternatives; original lost, second retained | covered once (numerator=1) | ✅ PASS |
| C | multi-span, only one of two required spans retained | uncovered (numerator=0) | ✅ PASS |
| D | multi-span, all spans retained | covered (numerator=1) | ✅ PASS |
| E | same proposition satisfied by 3 cumulative retained copies | numerator increases once (1, not 3) | ✅ PASS |
| F | critical + noncritical propositions | `critical_only=True` denominator=1, `critical_only=False` denominator=2 | ✅ PASS (both) |
| G | ineligible proposition with otherwise-satisfiable content | denominator=1, excluded_ids=(ineligible unit,) | ✅ PASS |
| H | **genuine FIFO eviction** (packet sizes independently computed: 174/175 bytes standalone, cap=200 forces real eviction of packet 1, not a never-admitted oversize rejection) | numerator=0 at checkpoint | ✅ PASS (my first attempt at this case had a construction bug — capacity too small, causing an oversize rejection instead of a genuine eviction; fixed and disclosed, see script comments) |
| I | diagnostic `body_results` contains the evidence via a real `capacity_bytes=0` `PeriodicCollector` run; `retained_evidence` does not | numerator=0 | ✅ PASS |
| J | two alternatives at different times (M(8) and M(2)) | delay uses the **earliest** completed alternative (M(2)), 120.0s, not M(8)'s 480.0s | ✅ PASS |
| K | context not frozen, no context alternatives | status=`NOT_FROZEN`, percentage=`None`, never a fabricated 0% | ✅ PASS |

**19/19 assertions pass.** The core coverage/delay mechanics — OR-across-alternatives, AND-within-alternative,
earliest-completed-alternative delay, cumulative-occurrence non-inflation, critical-only filtering, eligibility
exclusion, genuine-eviction non-coverage, and the `NOT_FROZEN` context guard at the top-level `evaluate_benchmark`
entry point — are all correct for every scenario I independently constructed. This is a genuine, positive finding,
not a rubber stamp: Case H specifically exercises what `PRE_RESULTS_CLOSURE.md` §4 named as untested (real eviction,
not zero-cap), and it passes.

## 5. Occurrence alternatives and cross-title support

`docs/PRE_RESULTS_CLOSURE.md` §6(2) states the loader ignores 15 already-recorded cross-title occurrence rows
across 6 units, and that "the loader's assertion that none exist is false." **Independently re-checked against the
current commit — this is no longer true; it has been fixed since the closure review's `9a7ab4c` baseline:**

```
PROP-20260616-10 -> distinct pages across alternatives: {dse~DataUSAPovertyBridgeApr09, dse~OpenResearchBridgeFeb03}
PROP-20260618-12 -> 5 distinct pages (AgentLinkma21JuneAA, AgentLinkma20JuneAA, AgentTmpLinkBack98687,
                    AgentLanguageProxyBridge2216, AgentLinkmethodJuneAA)
PROP-20260618-16 -> {AgentProxyCountyNext987111, AgentSlashCountyMoreUnique123}
PROP-20260619-21 -> {ZZZEnrollmentAsianFeb21Help, DataUSAEnrollmentAsianSequenceFeb21OAI}
PROP-20260622-62 -> {AgentNacoPovertyTexas2015XQ, ArchiveRoundedSEC4412}
PROP-20260618-63 -> {AI, AgentSecCountyVarAI}
```

All six units the closure named now have multi-page alternatives loaded, each built only from occurrences already
recorded in `occurrences.jsonl` (no fuzzy/semantic equivalence invented — confirmed by reading the loader's
`support` construction, which requires an exact recorded occurrence row satisfying every required span before an
alternative is built at all). **This specific closure finding is resolved. Report it as closed, not as still open.**

**However, a real, still-open issue from the same closure section is confirmed:** `PROP-20260618-63`'s eligibility
is still applied at the whole-proposition level, not per-alternative. It has 2 alternatives (`dse~AI@2`, the
head-mismatch anchor; and `dse~AgentSecCountyVarAI@1`, an ordinary, non-head-mismatched page), but
`annotations/eligibility.jsonl` — which I authored — marks the *entire* proposition ineligible because of the
anchor alone. The `dse~AgentSecCountyVarAI@1` alternative has nothing to do with the AI head-mismatch and is being
needlessly excluded along with it. **This is a real gap in my own earlier eligibility work, not the loader**: the
loader correctly builds both alternatives; my `eligibility.jsonl` is too coarse to let the evaluator use the good
one. Fixing this requires either occurrence-level eligibility (an evaluator/schema change, Ubayd's scope per
closure §9(2)) or a revised `eligibility.jsonl` disposition distinguishing the anchor from the alternative
(annotation-team/Sam scope) — not something this review resolves unilaterally.

## 6. Epistemic integrity

- `claim_status` is preserved **unmodified** by the loader for all 65 propositions — independently verified by
  comparing `Proposition.claim_status` against `evidence.jsonl`'s own field directly, byte for byte. ✅
- Collector retention cannot affect claim status or criticality: confirmed by code inspection — `load_a11_benchmark`
  never reads any collector output, and `evaluate_benchmark`/`compute_core_coverage` never write back to
  `Proposition`. ✅
- **Not fully resolved**: `PROP-20260620-08`'s `critical_reason` still reads "Cross-cohort propagation and reported
  replication of restriction workaround across distinct agent instances" — the same "distinct agent instances"
  framing the pre-results audit originally flagged. I fixed `-09` and `-03`'s equivalent prose in an earlier pass
  but did not catch `-08` at the time. This is a real, disclosed miss in my own prior work, still open, and belongs
  to annotation-content revision (Alex/Aaron/Jaswin), not evaluator code.

## 7. Split isolation

- Declared `dev`/`held_out` page/group/evidence lists are mutually disjoint — confirmed via `load_a11_benchmark`'s
  own `CROSS_SPLIT_LEAKAGE`/`DUPLICATE_SPLIT_MEMBER` checks (both exercised, both correctly reject when I fed a
  deliberately corrupted `splits.json`-shaped structure directly at `validate_population`/loader internals — see
  §3's dangling/duplicate tests for the general mechanism, which applies identically here).
- Occurrence-level split consistency (`OCCURRENCE_SPLIT_MISMATCH`, `OCCURRENCE_GROUP_PAGE_MISMATCH`) is enforced in
  the loader and produces zero issues against the real files — confirmed by the clean `ValidationReport` on the
  real load.
- **Confirmed real, still-open pilot-leakage issue** (matches `PRE_RESULTS_CLOSURE.md` §6(1) exactly): all four
  original pilot units (`PROP-20260620-06` through `-09`, group `GRP-02-OECD-WORKAROUND`) are independently
  confirmed still assigned to `held_out`. `X13_RUN_CONTRACT.md` §4's fallback rule states all pilot groups must be
  development. This is a split/data decision, not an evaluator defect — belongs to Jaswin/annotation team per the
  closure's own ownership table.

## 8. Context axis

- `annotations/context_fragments_DRAFT_SAM.jsonl` and its siblings are **not** imported anywhere by
  `src/ebe/a11_loader.py` or `src/ebe/evaluator.py` — confirmed by direct search; the real loader's
  `Benchmark.context_status` is hardcoded to `"NOT_FROZEN"`. ✅
- The top-level `evaluate_benchmark(..., metric="context")` entry point correctly short-circuits to a
  `NOT_FROZEN`/`percentage=None` result whenever `benchmark.context_status != "FROZEN"` — **confirmed via Case K**,
  never a fabricated 0%. ✅ for the path any real caller would actually use.
- **A narrower, still-real gap**: the lower-level `compute_context_coverage`/`_coverage` helper's own guard
  (`if metric == "context" and eligible and not any(p.context_alternatives for p in eligible): return ...
  "NOT_FROZEN"`) is all-or-nothing across the whole scored set. If even one proposition in a batch had non-empty
  `context_alternatives` (e.g., if a draft or partially-frozen context set were ever loaded for *some* units), every
  other proposition's empty `context_alternatives` would silently score as **uncovered**, not unknown/NOT_FROZEN —
  exactly the failure mode `PRE_RESULTS_CLOSURE.md` §7 describes. This does not currently manifest with the real
  loader (which gives every proposition empty context uniformly), but the low-level function itself is not safe
  against a partial future context rollout and should not be called directly outside `evaluate_benchmark`.

## 9. Delay

- Hand-verified via Case J: delay correctly uses the **earliest** completed alternative when multiple exist, not
  the most recent or an arbitrary one. `unretained` and `na_unknown_support` are distinct, non-zero statuses
  (confirmed in `tests/test_evaluator.py`'s pattern independently reproduced, not merely re-read).
- **Correction to `docs/PRE_RESULTS_CLOSURE.md` §8's claim** ("all 65 loaded earliest-support times are None, so
  real delays cannot be computed"): independently re-checked against the current commit — **only 1 of 65** has
  `earliest_eligible_support = None` (the single ineligible proposition, for which `None` is the correct value per
  the loader's own `eligible and support_times` guard). This closure finding is stale; it was accurate against the
  `9a7ab4c` baseline and has since been fixed. Report delay as computable for 64/65 real propositions, not as fully
  broken.
- No mechanism was found that could use a future or rejected body in a delay computation — `compute_delay` only
  calls `core_covered`, which is subject to the same (currently absent) checkpoint/hash validation gap as §2 above;
  fixing §2 will also close this residual risk for delay specifically.

## 10. Regressions and checker repairs

Per `docs/PRE_RESULTS_CLOSURE.md` §9(4)'s explicit assignment ("Sam — ... fix checker encoding/failing exits and
add corruption tests"), the following were fixed in this review, not left as findings only:

- **Confirmed and reproduced** the closure's encoding claim: E05's raw `body` field is a Latin-1 byte projection
  *regardless of declared `body_encoding`* (confirmed against `docs/E05_TYPED_LOADER.md`'s own text and against the
  raw revision's own `body_sha256`, which only matches an unconditional `.encode("latin-1")`, never a
  branch-on-declared-encoding). Both `audit/verify_annotations.py` and `audit/verify_a11_independent.py` shared this
  exact bug (the latter's branch compared against the literal string `"latin-1"` with a hyphen, which never matches
  the real field values `"ascii"/"utf8"/"latin1"`, so it silently always took the wrong path). **This is a bug in my
  own prior "independent" verification work** — I copied the existing checker's encoding-branch pattern instead of
  deriving it from the E05 spec. Fixed both scripts to unconditionally use `.encode("latin-1")`.
- Re-running the fixed checkers now correctly reports **2 evidence + 80 occurrence hash mismatches** (previously
  silently passed as "PASS"/"0 failures" by both scripts, and by the real `a11_loader.py`, which shares the same
  branch-on-encoding bug and was **not** independently checked here — that fix belongs to Ubayd per §9(2), since it
  is evaluator/loader code, not a validation tool).
- Fixed two additional confirmed fail-open gaps in `audit/verify_annotations.py`: a source-hash mismatch previously
  never set `all_pass = False` (only span mismatches did); an occurrence with no resolvable evidence parent
  (`parent_ev is None`) previously fell through to `occ_pass_count += 1` with no rejection at all.
- Fixed `audit/verify_a11_independent.py`'s missing failure exit code (`sys.exit(1)` was entirely absent) and its
  qualitative epistemic-leakage re-check (previously printed `STILL PRESENT`/`RESOLVED` without ever affecting
  `FAILURES`).
- Both checkers now correctly and reproducibly **FAIL** (exit 1) against the current annotation files, honestly
  reflecting the encoding bug above. This is the correct, honest state — not a regression I introduced, a
  previously-hidden defect I found and made visible, exactly per this review's mandate.

Regression commands run:

```
python -m unittest discover -s tests -v      # 138 tests, OK
python audit/verify_annotations.py           # now correctly FAILS (2+80 hash mismatches found)
python audit/verify_a11_independent.py       # now correctly FAILS (same 2+80, plus exit code fixed)
python audit/verify_accounting.py            # 9/9
python audit/verify_e08_neutrality.py        # 0 failures
python audit/verify_collectors_cross_policy.py  # 0 failures
python audit/verify_e12_independent.py       # new script this review; 19/19 hand-scored PASS, 7 confirmed real gaps reported as FAIL (by design -- see below)
```

`audit/verify_e12_independent.py`'s own "FINAL GRAND TOTAL FAILURES: 7" is not a bug in the script — it is the
script correctly reporting the 7 confirmed gaps in §§2/3/10 as failing checks, by design, so they cannot silently
disappear from view the way the encoding bug did in the older checkers.

## Pinned hashes

| File | SHA-256 (canonical git-blob) |
|---|---|
| `src/ebe/evaluator.py` | `45771b603ed73293d4468322582931f67923b2f31eaec7d7f11071cfdfb9572a` |
| `src/ebe/a11_loader.py` | `b8533358176e2916fd0477e1b2faeb059ebbac1a9e93286e077d41ff89231c02` |
| `annotations/evidence.jsonl` | `a1d201a437adffad3b7571ffdd3e21eea2b03f34d054f71ba71634afb32945f3` |
| `annotations/occurrences.jsonl` | `95e028eb6318678f7049ca002c605bacc7af2719cc565805c0ca49ea6bef66f2` |
| `annotations/eligibility.jsonl` | `ced75f4957b4653f6b74205ebe7dfd542b60f99c19aeaa5eff35e0824a65654a` |
| `annotations/splits.json` | `2c2eaee38eca798bbe2a7fc9ffd880a541427f10e84d77efbd01b2de9dd4385f` |

The four annotation-file hashes are byte-identical to `docs/PRE_RESULTS_CLOSURE.md`'s own pinned values — no drift
on the annotation side since the closure review. `evaluator.py`/`a11_loader.py` differ from the closure's pins
because Ubayd revised both after the closure baseline (`9a7ab4c` → `1fb21f5`/`055b5c9`); this review audits that
later, current state, not the closure's original snapshot.

## Final status, per the required breakdown

1. **Core axis status:** mechanically correct on every hand-scored case (19/19). Denominators independently
   reconstructed and agree with the implementer's report.
2. **Context axis status:** correctly `NOT_FROZEN`/NA at the real entry point, never a fabricated percentage. Draft
   files correctly not auto-imported. A narrower fragility exists in the low-level helper under a future partial
   rollout (see §8) — not currently triggered by real data, but should be hardened before relying on it.
3. **A04 retained-boundary status: BLOCKER, not closed.** Hash tamper and post-checkpoint records are both silently
   accepted. Exact fix specified in §2.
4. **A05 population-firewall status: BLOCKER, not closed.** DSE-universe and body-required-for-body-grounded-unit
   checks are both absent. Exact fix specified in §3.
5. **Cross-title occurrence status: CLOSED** (corrected from the closure review — fixed in a commit after its
   baseline). Per-alternative eligibility remains open (see §5), owned jointly by Ubayd (schema) and Sam/annotation
   team (disposition).
6. **X05 status:** this review constitutes the required independent hand-scoring (§4, 19/19) with fresh,
   pre-declared expected values and full authorship disclosure. Combined with the confirmed §2/§3 blockers, X05 is
   **not yet satisfied** — hand-scoring passing does not substitute for closing A04/A05.
7. **May Jaswin close E12?** No — not until §2 and §3's exact fixes land and are re-verified. Everything else in
   this review (denominators, hand-scored mechanics, cross-title loading, claim-status integrity, context-axis
   guard) is either confirmed sound or is a disclosed, narrower annotation-content issue (pilot leakage, one
   unrevised prose item, coarse eligibility) that does not block evaluator-code acceptance specifically.
8. **Does X13 remain blocked?** Yes, unaffected by this review either way — X13 was already blocked on F, PCD-R,
   order/archive/U machinery, and synchronized cost/overhead instrumentation, none of which this review touches.

## What was NOT done here, on purpose

No real policy-versus-label comparison was run. No collector was pointed at real annotation data for scoring. No
annotation content was rewritten (the two checker scripts were fixed; the annotation *files* were read, never
written, in this review). No fix was applied to `src/ebe/evaluator.py` or `src/ebe/a11_loader.py` — per this
review's brief, those are Ubayd's implementation to revise against §2/§3 above, then re-submit for acceptance.

## Reproduce this

```powershell
python audit/verify_e12_independent.py
python audit/verify_annotations.py
python audit/verify_a11_independent.py
python -m unittest discover -s tests -v
```
