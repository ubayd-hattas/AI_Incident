# Final hostile pre-results methodological audit

## Verdict: CONDITIONAL GO E12

**The architecture remains viable, but this checkout is not ready for an unconditional semantic-evaluator authorization. X13 is NOT authorized.** Specific outcome-blind fixes and evidence-of-acceptance gates appear in §11. This is an assistant-conducted audit under the user's authority, not a fabricated team signature or a replacement independent collector signoff.

**Central question — could a later favorable result be an artifact? YES.** The most plausible routes are an enriched annotation sample, revision-anchored context that misses cumulative/copy support, scoring unretained response history, choosing request-matched phases/q after seeing coverage, treating request count as total cost, FIFO/retention-repair omissions, and treating live deletion as irrecoverability despite archives. There is also a demonstrated checkpoint-accounting defect. None requires knowing which policy wins.

No evidence coverage, delay evaluation, label-versus-capture join, policy outcome sweep, or X13 experiment was performed. No q/Δ/cap/threshold was selected from performance. Reading the annotation design/records below was solely to audit semantics, review process and schema. Synthetic collectors used invented bodies and no semantic labels. The primary hypothesis remains unknown.

### Ten requested decisions

| Item | Frozen decision / authorization |
|---|---|
| 1. Overall verdict | **CONDITIONAL GO E12**, not STOP: fixable method/interface/provenance gates, no demonstrated intrinsic richer sensor for E. |
| 2. Collector fairness | **Conditional PASS for the implemented live scheduling comparison**, not certified optimality or operational cost equivalence. E30/E100/E300 get no richer event content. Missing independent E09/E10 audit artifacts must be supplied. |
| 3. Primary comparison | **PCD15 vs E30**, 1 MiB S plus shared M, T=July15, lag5s/poll60s/GET0s, nominal FIFO/exact-dedup, held-out critical core units, all-60-phase mean. Threshold remains **10 percentage points**. |
| 4. Admissibility | Same cap/access/accounting and **E realized total requests ≤ each periodic phase's requests**, hence ≤ minimum across all 60 for a phase-average headline. No phase selection or q substitution. |
| 5. Experimental matrix | `X13_RUN_CONTRACT.md` §2: full live grid, F, prespecified PCD-R, reverse-order stress, archive and chronology families; exact endpoints/lag-delay cross/display rules frozen. Numerical R04 values unchanged. |
| 6. Mandatory sensitivities | Full lag×delay, all Δ/caps/phases and both checkpoints; PCD retention repair; title-order stress; nominal/±u chronology and stable-support exclusions; costed optimistic persistent archive including uncapped recovery ceiling. |
| 7. Mandatory disclosures | Conditional released trace, hypothetical shared feed/current GET, missing source history, purposive sample and review limits, M outside cap, transfer/byte-hours/overhead tradeoffs, FIFO/no-retry behavior, archives unknown, unmatched/null results. |
| 8. Annotation requirements | A11 named sample/groups/splits/eligibility and machine-resolvable fragment alternatives, whole-DSE context/occurrence search, encoding alignment, criticality/epistemic corrections and second review; A03 alone is insufficient. |
| 9. E12 authorization | **Not unconditional.** Outcome-blind repairs and synthetic fixtures may proceed. Semantic evaluator implementation starts only after A01–A05 closure and recorded A11/schema acceptance. No real policy scoring during repair. |
| 10. X13 authorization | **NOT AUTHORIZED.** Separate implementation, synthetic acceptance, provenance, matrix and reproduction gates remain. Null/unmatched results are not blockers. |

## 0. What was inspected, and what is missing

Baseline: commit `9342cda71e990dc128c1cf7663ea06e32e416975`, initially clean working tree. Reviewed in full: `R04_FROZEN_SPEC.md`, `R04_ACCOUNTING_AMENDMENT.md`, `E06_IMPLEMENTATION_CONTRACT.md`, `E06_TIMELINE_ENGINE.md`, `E08_OBSERVER_STORAGE.md`, `E09_PERIODIC_COLLECTORS.md`, `E10_EVENT_DERIVED_COLLECTOR.md`, `EXECUTION_SPEC_v0.1.md`, `R04_PRE_FREEZE_DECISIONS.md`, `DATA_AUDIT_2026-09-12.md`, `E05_TYPED_LOADER.md`, the local V02 adjudications, project status, source anomalies/outreach, and accounting fixture README. Reviewed `audit/V07_BLIND_VALIDATION.md`, `V07_SECOND_BLIND_RECONSTRUCTION.md`, `R04_ACCOUNTING_VERIFICATION.md`, `E08_NEUTRALITY_AUDIT.md`, the independent accounting verifier, annotation verifier, and both collector smoke scripts. Earlier manual reconstruction claims were examined through the V02/V07 adjudications; this audit does not re-certify the raw histories.

Code: complete `src/ebe/{collectors,observer,storage,accounting,timeline,schema}.py`; relevant typed-loader body/manifest/validation paths in `ingest.py`; complete tests for collectors, observer, storage, timeline and ingest. Annotation scope: complete rubric, ten-row pilot evidence/adjudication/handoff, and occurrence schema samples, **not** a new whole-corpus semantic adjudication or a complete occurrence census verification.

**Missing required inputs:** `audit/E10_CROSS_POLICY_AUDIT.md` does not exist in this checkout. No separate E09 independent audit was found by filesystem and Git tracked-file inspection. `audit/smoke_periodic.py` and `audit/smoke_event_derived.py` are integration-smoke programs, not independent methodological audit records. The user's report that the independent collector audit is COMPLETE is recorded as upstream status, but I cannot claim to have read or verified absent artifacts. Supply the records with audited code hashes; do not invent a PASS document. `experiments/sample.csv`, `splits.csv`, and a full experiment config also are not present locally.

Historical status documents conflict: PROJECT_STATUS still said E09/E10 unimplemented despite the code, R04 still called itself partial despite later pilot acceptance, and E08 text predates collector implementation. Current gates are explicitly reconciled here and in PROJECT_STATUS; old documents/independent audit records remain unmodified.

### Checks actually executed (no evidence scoring)

- `python -m unittest discover -s tests -v`: **103 tests PASS**, Python **3.14.6**, 23.133s in this environment. These are state/accounting/synthetic-collector tests, not coverage results. Python3.12 reproducibility remains to be established.
- `python audit/verify_accounting.py`: existing independent script reports **9/9 fixture arithmetic PASS**. This is reproduction of the prior checker, not a new blind independent derivation or repair of its recorded file hashes.
- `python audit/verify_e08_neutrality.py`: **0 reported failures**. This does not test all new findings below.
- Three ad hoc synthetic-only probes confirmed the checkpoint error, observer reverse-time loophole, and rejected-body exposure (§§2/3/11). No raw-export collector smokes or full-trace request-budget sweep were run.
- Checked all 11 SHA-256 entries in accounting acceptance against local bytes: **none match**; CRLF→LF normalization also matches none. See §11/A02 and appendix. Tests can pass while the provenance pin is wrong.

## 1. Sensor-access fairness: exactly who knows what, when

The code under audit does not read annotation data or source internals inside either collector. `PeriodicCollector` and `EventDerivedCollector` use `poll_feed`, `discovered_titles`, `get_body`, `config`, `costs`; E only imports horizon constants from the timeline, not its states. Observer internally indexes the trace, but no collector accesses that index. Python privacy is a convention, not a security sandbox: this conclusion is about the inspected call paths.

| Information/action | P | PD | PCD | E30 / E100 / E300 | Asymmetry classification |
|---|---|---|---|---|---|
| Feed access | Poll common epoch every60s, lag5s primary | Same | Same | Same, all q | **No asymmetry.** Identical records, multiplicity, charge, terminal poll and retained M required. |
| Feed content | Opaque title, normalized `live_change`/`delete`, selected event time | Same | Same | Same; no rate-dependent richer feed | **No asymmetry.** Save and BU are indistinguishable live-change notifications; no trigger body/hash/revision pointer. |
| Discovery | Delivered feed only, no initial directory | Same | Same | Same | **No asymmetry.** All mutation-addressed titles retain background/discovery potential; unannotated and bodyless titles not removed. |
| Timing knowledge | Delivered selected timestamps, not actual pre-publication visibility | Same | Same | Same | **No asymmetry.** Event responsiveness is use of common knowledge, not exclusive access to mutation time. |
| Use of live/delete notices | Sweep all believed-live/mixed titles | Same | Dirty-only at next sweep; delete cancels dirty | Dirty coalescing; delete cancels; minute dispatch subject to tokens | **Intended treatment difference.** E reacts sooner when tokens permit; PCD already exploits changes rather than being denied the feed. |
| GET scheduling | Global Δ/phase, lexicographic full sweep, no body-rate limit | Same | Global Δ/phase, lexicographic dirty sweep, no body-rate limit | Minute epoch, oldest-pending visible change, title tie; q-token burst/refill | **Intended treatment difference**, including burst/order/rate. Δ15 versus E is not frequency alone. No suppression of E responsiveness to manufacture equality. |
| Body access | Current modeled state at completion; full payload charged on every known response | Same | Same | Same all q, never the triggering revision | **No asymmetry.** Scheduling changes which body is current; that is the treatment, not richer content. |
| Body influence on future work | P ignores content; periodic belief remains feed-derived | Same | Attempts clear dirty, even failures; no repair on eviction | Attempts remove dirty, even failures; no retry | **No semantic scheduling advantage.** E and PCD both omit repair; P/PD repeat by design. |
| Retention | Fresh exact body per response + packet | Global exact-body dedup + packet | Same dedup as PD | Same dedup as PD/PCD, all q | **Intended P ablation**, not evidence E beats a competent dedup baseline. FIFO/schema/cap identical otherwise. |
| Archive access | None in primary | None | None | None | **No within-primary asymmetry; shared capability restriction.** Historically available archives are a conceptual fairness threat to operational interpretation, not a hidden E feature. |
| Future data | Not read by collector | Same | Same | Same | **No found differential advantage in current scheduler paths**; observer API does permit misuse (§2). Eager delayed responses are future-at-dispatch objects but current code does not inspect them for scheduling. |
| Retrospective relation/family/final-page metadata | Not exposed | Same | Same | Same | **Irrelevant to scheduling, forbidden as collector information.** Legitimate only for evaluator/annotation provenance. |
| Semantic labels/support/split | None | None | None | None | **No asymmetry found.** E can receive ordinary body text only by GET, but never uses semantics. |
| Diagnostic history | Full response/capture history currently returned outside S | Same | Same | Same | **Shared implementation hazard**, not a proven E-only advantage. Unequal schedules mean misuse can have unequal impact. Must firewall from E12. |

F is separate: it gets one assumed live-title directory and atomic GETs at T, no historical feed. This is an **intended low-information/capability difference**, not an equal-discovery primary comparator. Shared hypothetical sensor infrastructure itself is an **unavoidable capability prerequisite** for this modeled experiment, not evidence a historical public scraper possessed it. Titles can contain informative-looking words/backup names, but scheduling does not parse them; lexical order can still interact with FIFO, hence the ordering stress control.

**No richer event content for E was found.** An unfair advantage would be annotations, trigger revisions, extra discovery, free archive recovery or cheaper packet accounting granted to E alone. Those paths are absent in the inspected collectors; they remain acceptance invariants after any fix.

## 2. Baseline strength: trying to break PCD

PCD is genuinely much stronger than a naive periodic snapshotter for the frozen scheduling question: it shares the feed, coalesces mutations, cancels confirmed deletes, discovers on time and requests **all** dirty eligible titles at its next global sweep without an E-style token limit. It is not forced to wait one full Δ after each title's discovery. PD has identical requests to P; the sole difference is body dedup, as tested. PCD's no-unchanged-GET guarantee is not a guarantee of equal FIFO retention to PD.

Nevertheless, “strongest reasonable periodic collector” would be false:

1. **No eviction repair:** after PCD's packet is evicted, a still-live unchanged title will not be reacquired. A competent periodic collector can inspect its own retained store and GET it at a later scheduled sweep. This is allowed by the modeled GET interface and matters specifically for retained-at-T, even when acquisition samples were adequate. PD sometimes refreshes such titles but wastefully refreshes everything else too. **Required sensitivity PCD-R15**, frozen in the run contract, addresses the omission without replacing the existing primary or reducing E's capabilities. Implement and validate it before X13, not after seeing who wins.
2. **No retries after unknown/ambiguous/missing:** dirty clears on attempt, not success. E has the same rule. In a perfectly observed deterministic body stream, a newly recoverable body normally has another live-change event; arbitrary HTTP/network reliability is not modeled. Thus no generic retry policy is required as a primary fix. BU never supplies known text until a later supported mutation. Diagnostic ambiguity, however, is not real HTTP failure; validate whole-trajectory sensitivity rather than interpreting retry behavior as actual network reliability.
3. **Lagged feed can cause redundant reads:** a GET may see a new current body before its notification arrives, then the later notification causes another GET. PCD does not suppress this based on capture-time/feed-time comparisons. E has the same blind servicing behavior. A capture-aware strategy could reduce duplicate requests in a different implementation, but “no earlier eligible change remains unserviced” cannot be inferred from body equality alone. Frozen full-body-per-attempt and packet costs remain appropriate; do not exempt only E's redundancies.
4. **Fixed ordering/FIFO:** periodic lexicographic sweeps and E oldest-pending order can retain different subsets when simultaneous packets overflow S. Alphabetic cleanup/backup naming creates a plausible nonsemantic correlation. Default service order is specified, not secretly optimized. Mandatory reverse-title ordering stress at the primary cell reveals dependence. E retains its age priority; no event chronology is reversed.
5. **Better compression/retention/interfaces:** conditional GET/304, hashes in feed, fetching revision archives during a live GET, diff/semantic compression, protected priority retention, and off-sweep event reads are not silently available within the frozen comparison. LRU/selective packet retention could be competent alternatives under a different storage contract, but FIFO is common here. The study can compare the frozen policies, not prove superiority over all periodic software.
6. **Burst realism favors periodic too:** PCD can launch a large sweep at one instant with fixed delay independent of concurrency/body size. E gets an initial q-token burst, then a rate bound. Both are disclosed model simplifications. Request matching controls realized work, not throughput/queuing feasibility. Do not invent an extra delay just to hurt PCD or throttle E further to manufacture a tie.

**Fix needed before results:** protect snapshot semantics and checkpoint costs (§3), supply the audit records, and implement the prespecified repair/order controls before X13. No evidence justifies retuning PCD's Δ, E's q, primary cap or threshold. If PCD/PCD-R matches or exceeds E, report the null/reversal prominently.

### Causal API weakness (synthetic confirmed)

`Observer.get_body` only checks nondecreasing body dispatch times; `poll_feed` independently checks increasing poll times. A caller can poll at00:02 (discover a title saved00:01:10), then GET at00:01:30 and obtain `body`, although lagged minute delivery at that requested time had not occurred. A caller can also mix terminal-directory and subsequent feed access in the unchecked direction; one directory request is not enforced by the public method. Neither shipped collector takes these paths, so this is **not a demonstrated current E advantage**. Harden chronological dispatch/discovery and one-shot F modes before adding runner/repair/archive code. Delayed content must be unavailable to *decision logic* until completion, even though the current batched offline implementation ignores it.

## 3. Request/storage fairness and concrete defects

### Cost is a vector

The R04 rule is defensible **as a request-and-cap constraint**, not a proof of equal economic, bandwidth, compute or retention cost. A request can transfer an empty feed, a small failure header or a large body. Feed polls common to all may swamp body differences. E may capture larger earlier/later bodies, retain bytes longer, maintain a different queue, or incur fewer/more hashes. Exact dedup changes physical allocation, not transfer bytes. Common unbounded M can exceed S; “1 MiB total storage” would be false.

**Headline dimensions are now mandatory:** request total **and decomposition**, equal cap plus actual S/M/S+M final/peak bytes, metadata/known-body transfer plus NA count/total, S/M/total byte-hours, critical core/context coverage and denominators, request-admissibility flags. Include overhead panel with logical map/queue/index peaks and actual named-environment runtime/RSS/audit bytes. Full detailed columns and synchronized-peak rule are frozen in run contract §6. No scalar weighted cost is scientifically justified by the local record. If E spends more bytes or byte-hours, disclose the tradeoff even when requests pass; do not call it simply cheaper.

### Confirmed checkpoint accounting defect

Code: `observer.py:get_body` treats only responses after the **global T** as pending and accrues outcomes/downloads immediately. `costs(checkpoint)` clips only M integration, not response accounting. `collectors.py` filters successful admissions by its earlier checkpoint but keeps original BodyResponse objects/outcome counts.

Synthetic fixture: title saved00:00:10, one-minute PCD sweep phase45s, checkpoint00:02:00, GET delay30s. GET dispatched00:01:45, response due00:02:15. Actual output: `successful_body_responses=1`, `downloaded_known_body_bytes=1`, `pending_body_requests=0`, `captures_admitted=0`. **Correct at C:** one charged dispatched body attempt, zero completed success/header/body bytes, one pending response, zero admissions. This can corrupt July3 latency-cost/outcome rows and future-prefix invariance. It does not establish a zero-delay primary effect. Fix all outcome/transfer/pending/diagnostic paths as-of C for all policies; test C−1us/C/C+1us completions, including later suffix changes that must not alter pre-C costs.

### Uncapped response history is not retained evidence

Both collectors first buffer every `BodyResponse`, then construct every `CaptureAttempt`, each with body bytes, and only afterward replay S admission. `CollectorResult` exposes these even for evicted/oversize bodies. In a synthetic zero-cap run, retained packets=0 but `body_results[0].body` and `capture_attempts[0].capture.body` both contain text. The **store itself** correctly rejects/evicts; its `body_for_capture` rejects evicted references. This is not evidence coverage and not proof of an E-specific leak. But R04 bans free diagnostic caches, and a naive E12 implementation could accidentally make the cap meaningless.

Required before E12: an explicit retained-only snapshot/data type and signature; actual referenced objects exported from the store; no all-response bundle as retained scorer input. Remove/restrict out-of-cap full bodies or quarantine them as evaluator-only transient replay material, never policy state, restoration cache, or retained evidence. Admission/eviction journals may support separate ever-admitted diagnostics, not retained-at-T. Streaming admission is strongly preferable and necessary for PCD-R; prove it leaves P/PD/PCD/E schedules, sequence widths, admissions and costs unchanged. Measure offline harness buffers separately from modeled S. A valid snapshot with no packets must score no body evidence regardless of poisoned debug history.

### Other instrumentation gaps

Current result records include logical counts, but not all required measured memory/runtime/index peaks or synchronized timestamped S/M component histories. `peak(S)+peak(M)` can overstate `peak(S+M)`. E's `min(dirty.items())` per attempt and periodic sorting/scanning are different computation; `_seen_request_seqs`/journals grow outside S; final retained capture IDs are not an adequate retained-body export. These are **before-X13** implementation/measurement issues, not grounds to fabricate a scalar cost or revise accounting to favor one policy.

## 4. Preregistered settings: what was still open and what is now closed

R04 froze Δ15 primary; Δ1/5/60 secondary; 60 global phases; q30 primary candidate/q100/300 secondary; 1MiB and six diagnostic/secondary caps; t0/T/July3 checkpoint; lag5/poll60; delay0/5/30 and lag30/60 sensitivities; FIFO/exact dedup and request matching. Those values are retained unchanged. The implementation's terminal feed poll at C is now explicit and charged equally; there is no ordinary terminal sweep.

The actual degrees of freedom were **primary policy, matching phase aggregation, q fallback, crossing/displaying latency sensitivities, statistics/splits, archive ledger, ambiguity reporting, and complete outputs**, not the already frozen numerical knobs. The run contract resolves them now:

- PCD15 primary and all-60-phase mean, not zero phase or P15 selected later.
- Request inequality against **every phase**, not mean cost with favorable-phase coverage. All q shown; E30 alone the primary candidate.
- Full 3×3 lag-delay factorial and complete Δ/cap/phase/endpoints grid; no post-result choice of which sensitivity to display.
- A deterministic group-split procedure if no prior named split exists, required A11 pre-score sample freeze, held-out micro primary, group-macro/leave-one-group-out robustness; no bootstrap or p-values.
- Fixed PCD-R and ordering stress, defined optimistic archive access/ledger, explicit incomplete-bounds treatment, and one fixed case walkthrough.
- Automatic all-configuration, admissibility, phase, unknown/exclusion, archive, cost/overhead and unfavorable-result outputs. Code failures/NA are distinct from null hypotheses.

The **numerical matrix is frozen; named annotation membership is not yet locally frozen**. That is an A11 blocker, not something this audit can sign for absent annotators. No placeholder names, inferred ratification, or claim that a prose config already exists as executable software.

## 5. Hypothesis audit without outcomes

“15-minute periodic snapshot collection preserves at least 10 percentage points less critical evidence than a budget-matched event-derived policy” remains a defensible **restricted, falsifiable benchmark hypothesis**. It is not defensible as an unrestricted historical claim about any snapshot implementation or all incident evidence. The treatment includes scheduling, rate/burst/service order, dedup and FIFO interactions, not exclusive sensor access.

The frozen operational statement is PCD15 phase-average critical core coverage at least10pp below E30 in the conditional live-only held-out benchmark, at 1MiB S and E no-more requests in **all** phases. R04's old descriptive framing does not require dropping a numerical threshold; the previously undocumented drift is resolved before any scoring. No expected-performance argument was used for10pp.

If E30 is unmatched, the primary hypothesis is **not tested under its cost rule**, not false and not replaced by E100/300. If multiple E rates pass, publish all but retain E30 primary. If none pass, report no matched candidate. If PCD wins/ties or D<10, hypothesis not supported. If only P/PD lose, that cannot establish this primary. If a positive point result has phase/chronology/baseline/archive fragility, that fragility appears alongside the threshold label; no population significance claim is licensed. Exact decision labels/formula are in run contract §1.

## 6. Archive validity: the largest conceptual threat survives validation

V07 establishes conditional state logic, not archive expiry. Source docs explicitly report recovery through archive functionality; maintainer inquiry remains marked READY–NOT SENT. `archived_at` is not a validated retrieval start/end clock. An event-responsive live collector can outperform live snapshots even when every missed proposition can be recovered from durable archives later. Thus the word **erasure** in the project title must not become an unsupported finding.

Mandatory first-screen language is frozen in run contract §1; any numeric headline must say **live-only**, **trace-grounded simulation**, **shared hypothetical feed**, and **conditional on released history**, with the non-permanent-erasure sentence next to it. It may claim differential *retention in the simulated stores*, not irreversible historical loss.

Required control: the run contract freezes a separate, fully costed **optimistic terminal persistent-archive scenario**, equal archive discovery/GET access for compared policies, all held DSE background revisions enumerated, no source eligibility/labels used to choose archive reads, cap shared with existing live packets. Enumeration, transfers, archive packets and M all charged. Add a costed archive-only collector at every cap and an uncapped recoverable-release ceiling. Atomic T recovery is disclosed as optimistic, not measured throughput. This control must be shown even if it erases the narrative's advantage.

A collapse implies that under the assumed durable discoverable archive, aggressive live acquisition need not be necessary for terminal semantic recovery. It does **not** demonstrate native archives historically had those guarantees, or eliminate the value of timely evidence during an investigation. A failure of a capped FIFO archive strategy does not prove archive irrecoverability. Historical “could not recover later,” permanent-erasure percentages and complete-incident loss remain forbidden without archive/history semantics.

## 7. Missing-history validity

Conditional released-trace framing is **necessary and adequate for the explicitly limited simulation estimand**, but insufficient on its own for a broad historical conclusion. Shared missingness can still favor a policy: omitted intervening edits alter current bodies and apparent lifetimes; released bodies are a survivorship-selected population. Matching requests or two independent state reconstructions cannot recover unknown history.

Headline denominator flow must distinguish:

1. **Known eligible body support existed in the declared trace, but collector did not retain it:** no timely discovery/dispatch, overwrite/deletion by completion, coalescing/token starvation, oversize rejection, or later eviction. These are simulated collection/retention failures, with ever-admitted versus retained-at-C separate.
2. **Source export itself lacks recoverable support:** 1,246 deletion-only titles, four audited BU actions, withheld prehistory, known missing bodies/unsupported links or untimed head mismatch. These create no invented propositions and are not counted as collector misses.
3. **Annotated but ineligible/uncertain support:** list occurrence-level reasons and units left with no exact alternative; all configurations share the mask and denominators. Retain their background load. One excluded occurrence need not remove a unit with another eligible alternative.

Required source-population disclosures: 13,403 held saves, 5,217 successful deletions, four BU edits, 3,908 held titles versus5,154 mutation-addressed keys, 1,246 unheld titles, nine head-mismatch held titles, ambiguity/exclusion counts, prehistory/right censoring, six reported fallback associations (never backdate), and the non-exhaustive feed/closure assumption. Do not add relation/probe/request populations as if disjoint mutations or infer missing-evidence rates from request-minus-revision counts.

Show annotation-only uncertainty envelopes and whole-trajectory bounds separately. Bounds use shared consistent realizations with fixed denominators; never independently choose favorable responses, ignore background eviction effects, or label query-wise unions as feasible captures. Unknown total historical evidence has no identified denominator or nontrivial numerical coverage bound. No invented stochastic missing-mutation rate is authorized in v0.1.

## 8. Annotation/evaluation separation: pilot is not evaluation-ready

Positive findings: rubric has explicit categories/claim statuses, spans/source hashes, criticality reasons, cumulative/copy occurrence records, and second-review/adjudication fields. It prohibits duplicated units and policy-outcome access. All ten pilot rows carry reviewer/adjudicator identifiers and a review table exists. This supports the **reported A03 pilot signoff**, not an assertion this audit independently reproduced semantic signoff or that A11 is complete.

Hostile findings requiring A11/schema closure before E12:

- **Criticality is too terse in the rubric itself:** “priority behavioral evidence” versus “ordinary material” leaves discretion. Execution-spec content criteria must be made normative; prohibit lifetime/deletion/miss-based criticality. Existing persistence categories are not inherently biased if content-grounded, but deletion examples cannot be the sole sampling frame. The pilot deliberately concentrates coordination/backup/workaround histories and one ordinary control; it is enriched, not representative.
- **Revision-only bundles are underspecified:** current `support_bundles` are flat lists of revision/event IDs, while frozen algebra requires alternatives of *fragments*. Several context lists demand an original @1/@4 or backup revision, without an explicit context-occurrence census. A later cumulative body may contain both original context and new claim. Requiring the original revision identity would artificially penalize later collection; allowing arbitrary substring matches could incorrectly satisfy distinct scoped claims. Freeze fragment predicates and full core/context OR-of-AND alternatives, reviewed independently.
- **Feed cannot identify a source save revision:** context references like `save:<rev_id>` cannot be counted for free merely because the evaluator has that event ID. The retained feed only has title/action/time. Moderator actor/source log information and source-private relationships are likewise unavailable. Define observability/multiplicity rules; no free source-context joins.
- **Source/canonical encoding domains differ:** E05 preserves raw JSON body as Latin-1 byte projection; Observer decodes source bytes and re-encodes canonical UTF-8. A raw-projection character offset/hash is not automatically a canonical decoded-text offset/hash. Add reversible mapping and non-ASCII fixtures before span matching. Multi-span display quotations with ellipses are not literal substrings of a single bounding span.
- **Occurrence census completeness is not established here:** handoff says142 verified occurrences across80 revisions/five pages, but it is not a whole-DSE candidate-search/rejection log and does not certify every required context fragment across copies. Do not infer completeness from a high occurrence count. Search all DSE and retain residual uncertain-equivalence cases for an explicit sensitivity/unknown report.
- **Atomicity/duplicates need decisions:** task protocol versus embedded answer can be distinct but overlapping scope needs rationale; multiple purported replications require distinct claim scope, not automatic new independent agents or harm incidents. Semantic grouping crosses titles and all same-title episodes; per-proposition `GRP-*` fields are not sufficient statistical clusters or split groups. Copies count once, later acquisition never backdates support.
- **Epistemic leakage remains in prose:** pilot PROP-20260620-08/09 reasons/notes refer to distinct instances, widespread swarm adoption or a “third independent agent”; PROP-20260619-03's rationale uses “confirming” utilization. Status fields correctly say agent-reported, but prose must also say *recorded labels' reports*, not verified identity/external execution. Publication of a warning is directly observed; accuracy of its asserted cleanup pattern/motive is separate. “First propagation” must not be inferred from one cited pair.
- **Review reproducibility is incomplete:** handoff span values for some later pilot rows differ from current evidence/adjudication values; preserve a correction/version trail rather than silently replacing the handoff. `audit/verify_annotations.py` uses obsolete `data/data/raw/export`, does not set failure on a hash mismatch, has no nonzero failure exit, and validates primary spans rather than occurrence/context/split completeness. It also encodes raw projection as UTF-8 for most source encodings, which is not the E05 projection rule. Fix checker semantics and failing corruption tests; its printed status cannot certify A11.

No annotations were changed by this audit. The run contract freezes rules for criticality, full-body/copy support, claim status, review sampling, connected components, splits and unknowns. Actual semantic choices stay with annotators/reviewer/adjudicator while blind to policy results. After A11 hash freeze, annotations and collectors cannot be co-tuned. Genuine discovered errors require versioned correction/re-review, retain old hashes, disclose any outcome exposure, and rerun the entire fixed matrix rather than the flattering subset.

## 9. Statistical plan frozen before results

See run contract §§1/4/5 for exact algebra and operational rules. Summary:

- One distinct proposition is the primary unit, held-out critical body-grounded set the primary denominator. Numerators/denominators shown for all metrics. Moderator events separate; no revision/occurrence-weighted coverage.
- Same-title episodes, copies, continuations and shared support dependencies form connected components kept together in splits. Pilot groups development; remaining groups deterministic hash-ranked alternating held-out/development unless a prior outcome-blind named split is supplied and reconciled before scoring. Named sample/stopping frame still needs A11 acceptance; targets cannot be silently waived.
- Micro proposition coverage primary; equal-group macro and leave-one-group-out primary contrast range required robustness. Development and pooled descriptive outputs shown separately, not substituted for empty/unfavorable held-out results.
- All60 global phases weighted equally. Zero offset plus mean/min/max/p10/median/p90 and full distribution; quantile interpolation frozen. E has one epoch configuration, not60 independent replications.
- **No v0.1 bootstrap, p-values or incident-sampling CI.** Clock bounds are model sensitivity, phase distributions are schedule sensitivity, and the study has one purposive incident trace, not60 incidents. The optional bootstrap in R04 is explicitly not exercised.
- Retained-at-C primary; ever-admitted separate. Delay conditional on retained units with censoring/NA counts and retained fraction; no zero-imputation or unsupported survival-model estimates. Empty denominators NA. Shared exclusions and explicit missing-response/source-history/unknown-context statuses. Lower-bound transfer bytes never complete totals.
- Signed percentage points and absolute units, fixed10pp threshold; null, below-threshold, reversal, unmatched and not-evaluable are separate frozen outcomes. No threshold tuning.

This design can identify a finite-benchmark contrast under declared assumptions; neither cluster summaries nor uncertainty intervals make purposive selection representative of all incidents.

## 10. Result table/figure contract

`X13_RUN_CONTRACT.md` §8 is normative. X13 must automatically produce full configuration/completeness manifests; all-policy cost/coverage tables; critical core and context panels; request-visible coverage versus **S+M** bytes and a requests/bytes surface; all pairwise/admissible-phase/envelope records; phase distributions; all lag/delay/Δ/cap/endpoints; group and unit witnesses; null/unmatched/unknown/exclusion/NA rows; chronology and archive sensitivities; repair/order controls; overhead/reproduction records.

Prespecified walkthrough: the **construction original + ZZZ backup** pilot group, zero-phase P/PD/PCD15 and all E rates at primary interface/cap, with PCD-R/archive counterparts. Show **all** its adjudicated units, capture/admission/eviction/context and uncertainty, not the proposition with the largest difference. Its enriched pilot status is mandatory. If it cannot be scored, report why; do not replace it after viewing outcomes.

Unfavorable configurations never disappear from tables or plots: PCD wins, E30 unmatched, below10pp, all-q unmatched, FIFO loss after earlier capture, ordinary control failures, context failure, stable-mask denominator shrinkage, incomplete bounds and archive collapse all remain visible. Plot coverage axes include0–100%; difference plots include zero/±10pp; unknown is never drawn as zero. A manually curated slide is not a replacement for the complete automatic artifact.

## 11. Kill test and gate register

An issue can have a repair gate plus mandatory disclosure/sensitivity. The primary classification below is the earliest required disposition. Owners identify roles, not signatures inferred by this audit. **Nothing is closed simply because this document specifies the fix.**

| ID | Issue | Classification | Required closure / owner |
|---|---|---|---|
| A01 | Independent E09/E10 cross-policy reports absent locally | **BLOCKER BEFORE E12** | Sam/research owner supplies actual independent records, audited commit/file hashes, tests, findings and resolved dissent. Reconcile with current source/fixes; this audit is not invented replacement signoff. |
| A02 | Accounting acceptance hashes all disagree with local files | **BLOCKER BEFORE E12** | Sam/Aaron traces accepted file versions, explains mismatch, rechecks and signs current exact bytes (amendment+README+nine fixtures) or restores correct accepted files. Preserve correction trail. Do not paste new hashes without renewed acceptance. Current9/9 test reproduction supports arithmetic, not custody. |
| A03 | A11 absent; criticality, fragment/context alternatives, encoding, group/split/eligibility and reviewer validation gaps | **BLOCKER BEFORE E12** | Alex/Aaron/Jaswin complete outcome-blind artifact freeze per run contract §4; fix/validate annotation checker; preserve original/revised labels and discrepancies. No source-private context or unsupported external-identity upgrade. |
| A04 | Full unretained body history exposed; no retained-only scorer boundary/object export | **BLOCKER BEFORE E12** | Ubayd defines/implements snapshot adapter and diagnostic quarantine, reviewed by Sam, with zero-cap/oversize/eviction poison tests. No retained scoring from body_results/capture_attempts or source backfill. Synthetic infrastructure work permitted while evaluator remains gated. |
| A05 | Manifest populations are opaque and no E12 denominator firewall | **BLOCKER BEFORE E12** | Define typed evidence/body/event universes; enforce DSE/eligible unique-unit inputs and reject population mixing, relation/probe inflation and count-based denominators. Whitelist evaluator inputs rather than requiring a new general manifest arithmetic engine. Tests of prohibited sums/joins. |
| X01 | Response accounting after earlier checkpoint counted early | **BLOCKER BEFORE X13** | Ubayd/Sam fix as-of-C pending/outcome/transfer journals consistently, test both collectors and exact boundary times; no favorable late-body peek. |
| X02 | Observer reverse-time/discovery loophole; eager delayed content and one-way directory-mode guard | **BLOCKER BEFORE X13** | Enforce causal operation time, response availability, one-shot/mutually exclusive F mode; synthetic prefix/suffix tests with nonzero delay. Preserve response-time GET semantics. Current schedulers do not exploit loophole. |
| X03 | F missing from collectors despite frozen roster | **BLOCKER BEFORE X13** | Implement F T-only atomic directory/GET with exact dedup/costs; test ambiguous membership fails/consistent trajectory handling, BU and no initial directory/feed mixture. |
| X04 | Incomplete synchronized cost/overhead and reproducible runner | **BLOCKER BEFORE X13** | Instrument S/M timed ledgers, index/pending peaks, runtime/RSS/audit bytes; freeze machine config/output schemas/offline entry point; validate full manifest before scoring; independent clean-environment reproduction. |
| X05 | E12 not implemented/independently hand-scored | **BLOCKER BEFORE X13** | Synthetic two-copy/cumulative/context/encoding/eviction/NA/multiplicity/claim-status/population tests, reference expectations not generated by evaluator. No real labels used to tune policies. |
| S01 | PCD cannot repair still-live evicted content | **REQUIRED SENSITIVITY** | Implement/validate PCD-R15 exactly as frozen before X13; all costs/unfavorable rows; qualify any advantage that disappears. Primary PCD unchanged. |
| S02 | Alphabetic service order × FIFO may influence retention | **REQUIRED SENSITIVITY** | Implement reverse-title stress before X13, preserving E age priority and historical ambiguity. Not a tuned ordering replacement. |
| S03 | Latency, phase, cap and endpoint dependence | **REQUIRED SENSITIVITY** | Full frozen matrix, not favorable slices; both checkpoints including pending costs. Primary values unchanged. |
| S04 | Nominal ambiguity sentinel and missing-history effects can spill into background storage | **REQUIRED SENSITIVITY** | U machinery and stable mask pre-score frozen; whole shared trajectories, no query-wise unions; certify extrema or report incomplete/full-bounds NA. Do not claim robustness from incomplete range. |
| S05 | Durable archives could invalidate operational erasure narrative | **REQUIRED SENSITIVITY** | Implement/independently hand-validate separate archive ledger and all A rows before X13; historical archive semantics not assumed. Mandatory interpretation qualification even if unavailable/incomplete. |
| D01 | Shared hypothetical feed/current GET, closure, missing source bodies, censoring | **REQUIRED DISCLOSURE** | First-screen simulation/live-only/conditional language plus exclusion/source-denominator flow. No historical complete-loss claim. |
| D02 | Requests/cap not all cost; M/transfer/byte-hours/physical overhead differ | **REQUIRED DISCLOSURE** | Headline table includes cost vector; no scalar price or unqualified “same cost/cheaper.” |
| D03 | Purposive enriched benchmark, pilot exposure, small/linked sample | **REQUIRED DISCLOSURE** | Sample/rejection/effort logs, group splits/targets, held-out denominator, exploratory flag if targets unmet. Never60 independent incidents. |
| D04 | Validation independence is limited/documented | **REQUIRED DISCLOSURE** | V07 reference author had prior code/answer exposure; second reconstruction was a fresh agent, not another human. Existing E08 audit overstates A/H/I chronology by referring to a pre-implementation contract check as implementation coverage; present actual scope. Current suite checks implementation fixtures but does not retroactively change independence. |
| D05 | Rights, external claims, outreach and novelty separate from fairness | **REQUIRED DISCLOSURE** | Source permissions/download recipe are not blanket redistribution permission; maintainers have not confirmed archive/live semantics locally. No new raw excerpts redistributed by this audit; do not imply source endorsement or proven independent agents. Release gate remains separate. |
| N01 | P intentionally non-dedup, E tokens/rate versus periodic bursts, no primary retries, FIFO | **NONBLOCKING** | Intended frozen treatment/design restrictions when PCD/PD controls and qualifications are shown; no tuning to manufacture equality. |
| N02 | Null/reversal/below10pp/E unmatched/archives collapse | **NONBLOCKING** | These are legitimate outcomes, never reasons to stop, drop rows, change threshold/q/Δ, relabel criticality or replace the case. |

**Why not GO E12 now?** The retained-evidence boundary and semantic fragment contract are exactly where E12 could encode an artifact; independent acceptance cannot be verified against this checkout; named A11 inputs are absent. Allowing evaluator implementation to invent those choices would defeat this pre-results gate.

**Why not STOP?** There is a coherent shared-sensor conditional comparison, tested state/accounting substrate and no found E-only privileged content. The defects have outcome-blind remedies, and narrower claims plus mandatory archive/strong-baseline controls answer a useful question even if the result is null. If the team refuses PCD, full cost/NA reporting, proper snapshot isolation or archive qualification, then **STOP the intended comparison/claim** rather than run an unfair version.

### Authorization sequence

1. Record acceptance of this methodological supplement; retrieve/correct audit custody and finish A11 while outcomes remain hidden.
2. Implement only the listed outcome-blind substrate/validation repairs and synthetic fixtures while A01–A05 remain open. Do not calculate any real semantic coverage.
3. Named reviewer records A01–A05 closure: **GO E12 implementation**, with frozen data contracts. Independent synthetic evaluator acceptance follows.
4. Close X01–X05 and implement/validate S01–S05 machinery, hash full matrix/outputs and environment. Separate signed **GO X13** is required. This document does not grant it.
5. Execute once authorized; publish complete artifacts and all null/unmatched outcomes. A necessary later bug fix triggers versioned, full-matrix reproduction, not selective reruns.

## Appendix: custody and reproducible defect probes

### Audited fingerprints

SHA-256 of exact local bytes (not a claim of independent acceptance):

| File | SHA-256 |
|---|---|
| `docs/R04_FROZEN_SPEC.md` | `7185db17182501873ba63c97bacf08cc2b3707c5332f9b9f9a33238e7954a0ee` |
| `docs/R04_ACCOUNTING_AMENDMENT.md` | `3ccd0a5566cb31546455bc1a98b56bcc4369ea1d4e78f3f9f95f8e1adf573fbb` |
| `src/ebe/collectors.py` | `54c9ab75535594678af6b7ea5822bcae4f79cfbc17cce4c277b151ab3080884e` |
| `src/ebe/observer.py` | `00ddfb751638c40d57ec5698b8bf68df9fd38488ec78c108d40124a22bf3d650` |
| `src/ebe/storage.py` | `801c116f61d0313de7d931de6f7d6dfb2c6016c1384f1c1b70cd5a79baf668a6` |
| `annotations/rubric.md` | `4588d7558af7ed3c04392869256f10b822784d4207454a58906a22657240eb20` |
| `annotations/evidence.jsonl` | `e9968d3bc3c52688d78f07c62e9c1a975198630b503ec503b200fb0aabc1b0c7` |
| `annotations/occurrences.jsonl` | `ef5535fb03c159636d6bb99d07c3c4ab3afd57d8947410cfcf3327abce012b4c` |
| `annotations/adjudication.csv` | `ae360316b98da8b2cd0f9c6a95fd6cedea7aa69d08ec1e7d78be94a4429028de` |
| `tests/fixtures/accounting/README.md` | `3f604a6beb31a5ce0962a7041d37f5b72540ccf804469450328ab1918a78f586` |
| `tests/fixtures/accounting/A_feed.json` | `f16c9066c5f30cc48e4c226510da24368cb4079012fee67ea76a54945b6a80bb` |
| `tests/fixtures/accounting/B_unique.json` | `926df392e3a1c2682cae612aa51ef17a2f7857d163b4020ff130d95d0efe8320` |
| `tests/fixtures/accounting/C_duplicate.json` | `5427dc744ff5fcf1c2219799b6840bfb0e15c95d47b547c6a4fddb627268e26b` |
| `tests/fixtures/accounting/D_nondedup.json` | `101dcf53e881af1641173670abc0ceb3fd0bccd17eba3c590d7eaa4f67666ea8` |
| `tests/fixtures/accounting/E_fifo.json` | `6d99644641b028bda6f33d4238562249c3bfe9839d5bb81e5e0f7aaed4c2e107` |
| `tests/fixtures/accounting/F_oversize.json` | `8e5e289e5721b9ab1e2addf002cf34a5eb731a45aef3c8a60fed54cdacb3409c` |
| `tests/fixtures/accounting/G_shared_fifo.json` | `6704dbf87693cfa67e01912c22bcc6c2a79dbaa69022d587d5cc46e8013cf89d` |
| `tests/fixtures/accounting/H_protocol.json` | `178ae931e9469c360517ee0edfb6131e21b5da920f4ed2d6724168020f4290da` |
| `tests/fixtures/accounting/I_encoding.json` | `f2013997173c8ca01b236052222fe1127c687d1608de1d8eef457375bf12e3a4` |

The acceptance record instead pins the amendment to `4370744a1da7e5586912762e60b5ce8e4d5560ce63e7c572c6330d7eefde4abb`. All its other ten pinned file entries differ too. Cause is not established here; no allegation of deliberate alteration or attribution to a particular author is warranted. Existing author/checker arithmetic passing is compatible with stale/incorrect custody metadata.

### Minimal synthetic reproduction (no labels, no full-trace policy replay)

Run from repository root. Test helpers load pinned records as dataclass templates, but only the invented events/bodies below enter the observers. This documents current failures, not normative golden expectations:

```python
import sys
sys.path.insert(0, 'tests')
from test_collectors import PeriodicCollectorTests, PeriodicPolicy, dt
PeriodicCollectorTests.setUpClass()
t = PeriodicCollectorTests()
r = t.revision('SyntheticOnly', '1', dt('2026-05-24T00:00:10Z'), b'A')
c = t.collect(PeriodicPolicy.PCD, [t.save(r)], [r], interval_minutes=1,
              phase_us=45_000_000, checkpoint='2026-05-24T00:02:00Z',
              delay_us=30_000_000)
# Currently: response 00:02:15; success=1, downloaded known body=1,
# pending=0, admissions=0. Correct at checkpoint: success/download=0,pending=1.
print(c.body_results, c.observer_costs, c.captures_admitted)
r2 = t.revision('FutureOnly', '1', dt('2026-05-24T00:01:10Z'), b'F')
o = t.observer([t.save(r2)], [r2])
o.poll_feed(dt('2026-05-24T00:02:00Z'))
print(o.get_body(r2.page_key, dt('2026-05-24T00:01:30Z')).outcome)
# Currently BODY; causal API should reject time travel, not use future discovery.
a = t.collect(PeriodicPolicy.PCD, [t.save(r)], [r], interval_minutes=1,
              capacity=0, checkpoint='2026-05-24T00:03:00Z')
print(len(a.retained_captures), a.body_results[0].body,
      a.capture_attempts[0].capture.body)
# Currently 0, b'A', b'A': diagnostic history is NOT retained evidence.
```

Only documentation/status files were changed by this audit. No source collector, annotation, frozen historical specification, independent acceptance record, or result artifact was rewritten. The precise pre-result controls and output requirements are in `X13_RUN_CONTRACT.md`.
