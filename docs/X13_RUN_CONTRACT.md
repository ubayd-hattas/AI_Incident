# X13 run contract — pre-results freeze

## Amendment v1 — FINAL_PRE_X13_DEADLINE_v1 (outcome-blind)

**Current authority:** this amendment and `FINAL_PRE_X13_FREEZE.md` supersede the original matrix/completion gates below, not its accounting, primary estimand or result guardrails. The original text is retained as v0 provenance. Decision made before any real PCD-vs-E evidence result, without running X13 or inspecting policy coverage. Research-methodology owner acts under the user's final-consolidation mandate; this is not a fabricated Sam signature.

**Option 2 selected.** The original 100,319 rows plus uncertainty expansion are not a defensible same-day engineering commitment with required controls still unimplemented. No runtime benchmark or outcome was used to prune. Freeze 791 logical scored run rows, plus 61 evaluation-only conservative-mask families. All rows use the complete DSE background, t0=2026-05-24T00:00:00Z and T=2026-07-15T00:00:00Z. Unless specified: S=1,048,576 bytes, lag5s, delay0s, polling60s, nominal chronology, FIFO, original service order and R04 accounting. Every periodic family includes all j=0..59 with phi_us=j*Delta_us//60. E has phase NA.

| Block | Exact settings | Logical rows |
|---|---|---:|
| L-primary | P15, PD15, PCD15 all phases; E30, E100, E300 | 183 |
| L-interval | PCD5 and PCD60, all phases; compare existing E30 at same interface | 120 |
| L-latency | PCD15 all phases and E30 at (lag,GET delay) seconds = (5,30), (60,0), (60,30); with primary (5,0), a complete 2x2 factorial | 183 |
| F | Final-live-only, one terminal directory and one atomic GET per listed title, 1 MiB, no feed | 1 |
| R | PCD-R15, all phases, primary interface/cap | 60 |
| O | Reverse-title P15, PD15, PCD15 all phases and E30 (reverse title ties only, oldest-event priority unchanged) | 181 |
| A-live | Terminal persistent archive augmentation of PCD15 all phases and E30 primary prefixes, 1 MiB | 61 |
| A-only | Empty-prefix archive-only at 1 MiB and uncapped | 2 |
| U-stable | Conservative stable-support re-score of nominal PCD15 all phases and E30 primary snapshots; not additional collection runs | 61 families / 0 extra runs |
| **Total scored collection rows** | **183+120+183+1+60+181+61+2** | **791** |

No optional additions today: E100/E300 are secondary only at L-primary; shorter/longer intervals only PCD5/60. All 791 rows are required for completed-amendment status. Primary remains PCD15 vs E30, all-phase request rule, held-out critical core, unchanged 10pp practical threshold. K=23 nominal at T (see final freeze). Because validated evidence-bearing episode/sampling provenance is insufficient to certify the original design target, classify the entire study **exploratory prespecified finite-benchmark simulation**; do not claim full-design confirmatory success. Threshold labels remain descriptive conditional-benchmark decisions with this qualifier.

### Mandatory sensitivities and explicit omissions

Retain online PCD-R repair (§3), reverse-title service, the full stated 2x2 latency interaction, capped archive augmentation plus costed uncapped archive-only ceiling (§7), nominal ambiguity diagnostics and conservative stable-support exclusion (§5). These controls and their unfavorable results cannot be waived at the deadline. Archive enumeration always includes all held DSE revisions, not annotations. All-phase admissibility and full cost outputs apply to each comparable family; archive-only/F are distinct-access baselines.

**NOT_EXECUTED_SCOPE_AMENDMENT:** July3 checkpoint; all live caps except 1 MiB; Delta1; P/PD at Delta5/60; q100/q300 outside primary; lag30 and delay5; all secondary cross-products of R/O/A; P/PD archive prefixes; archives at other capped sizes; full nominal-tie and closed +/-u shared-trajectory range enumeration/certification. Generate `omitted_scope.csv` with every original v0 logical row/family absent from v1 and its reason; v1-only rows get explicit added IDs. No missing row is silently reclassified as an omission.

Stable support is a deterministic annotation-private compilation under v0 §5: accept only support identity/availability common to all closed +/-u states (or certified equal text) at acquisition, preserving background load and nominal collection; freeze mask algorithm/source pins and compiled interval mask **before scoring**. Uncertifiable support is excluded with reason, never presumed stable. Report changed denominator, numerator, removed IDs and NA; this is NOT a replay-trajectory bound. Full trajectory ranges are deliberately **NOT_EXECUTED_SCOPE_AMENDMENT**, with full-range fields NA, not an invented examined-subset range or INCOMPLETE_BOUNDS claim from zero work. Incompatible nominal states remain explicit ambiguous responses; an engine `unsupported` background response still invalidates the run.

**Forbidden if omitted:** no claims of robustness to chronology realizations, clock uncertainty's storage spillovers, July3/other endpoints, broad capacities, omitted latency/interval/rate combinations, full factorial completion, population representativeness, validated >=40 evidence-bearing episodes, or universal periodic/event superiority. No permanent erasure/historical responder loss, equal-total-cost, operational archive availability, optimal capped archive strategy, or independent-agent/external-success inference is permitted even with all v1 rows complete. Allowed claim: the prespecified, exploratory finite-benchmark all-phase contrast under the declared nominal live-only model and request/cap constraints, with observed repair/order/latency/archive and stable-mask qualifications adjacent. A partially completed required matrix is NOT_EVALUABLE as a completed study; individually valid rows may be published only as explicitly incomplete descriptive results.

### Outputs and two-gate authorization

All v0 §6 cost dimensions and §8 tabular outputs remain mandatory for the executed roster, including context, delays, groups, phase distributions, exclusions, archive comparison, overhead and failed rows. Plot domains are restricted to v1; no lines suggesting an omitted cap sweep. `latency_checkpoint` becomes the T-only 2x2 panel, chronology reports stable-mask values and explicit NA trajectory fields. The fixed construction/ZZZ walkthrough stays development-only and uses existing zero-phase P/PD/PCD15, E30/100/300, PCD-R and PCD15/E30 archive rows; do not invent missing per-policy archive runs. Standalone graphics for cost envelopes, group robustness and omitted trajectory ranges may be omitted; their CSV/NA disclosures cannot. Source/annotation snapshots and exact manifest hash precede scoring.

Only two readiness gates now exist: Ubayd's consolidated engineering acceptance, then Sam's comprehensive independent PASS on the pinned candidate, as specified in `FINAL_PRE_X13_FREEZE.md`. Sam PASS records automatic X13 authorization for that exact candidate/manifest without another broad Astra review. Genuine implementation bugs or a methodological contradiction fail the applicable gate; null, reversal, unmatched, below-threshold and archive-collapse outcomes do not. X13 has not run and is not authorized by this amendment alone.

---

# Original v0 contract (historical where amended above)

**Status: frozen by this audit as a pre-outcome methodological supplement; execution NOT authorized.** Read `PRE_RESULTS_AUDIT.md` for the gates. This is not team signatures, an A11 label acceptance, implemented configuration software, or a result. Baseline repository: `9342cda71e990dc128c1cf7663ea06e32e416975`. No evidence coverage was calculated in making this contract.

Authority: retain R04's source/model, numeric settings and accounting definitions. This supplement resolves its remaining comparison/reporting discretion and prespecifies additional hostile controls. Earlier status headings are historical. Deviations require a versioned amendment recording rationale and who has seen which outputs; after outcome access, additions are exploratory and cannot replace the frozen primary. Do not alter old results or accepted fixtures to conceal a correction.

## 1. Primary estimand and decision rule

Study description, including on the first figure:

> **Trace-grounded, live-only simulation under a shared hypothetical change-feed interface, conditional on the released DSE history. Evidence not retained by a simulated collector is not evidence permanently erased from the website.**

Primary comparator: **PCD, Δ=15 minutes**, not P, PD, or F. Primary event configuration: **E(30)**, capacity/refill/initial tokens all as R04; no alternative dispatch phase. Primary endpoint: **2026-07-15T00:00:00Z**. Primary capped capture/body store S: **1,048,576 bytes (1 MiB)**, shared feed M additional. Nominal selected-clock interface, lag 5s, polling 60s, GET delay 0s, FIFO and exact dedup.

Primary evidence set K: A11-frozen, held-out, distinct, critical **body-grounded** units having eligible exact core support. K is common to every configuration. Sections 4–5 define split, support and NA rules. No aggregate manifest count or moderator-event unit enters K.

For phase j, let c_j be PCD15 critical core retention at T and e be E(30)'s retention on K. Primary contrast in percentage points is

`D = 100 * (e - sum(c_j for j=0..59)/60)`.

This is the uniform-grid schedule-average contrast on one frozen benchmark, not an average of independent incidents. Positive favors E. The preregistered practical hypothesis is **D ≥ 10 percentage points**, conditional on admissibility. Exactly 10 qualifies; compare unrounded rational values, not rounded printed numbers. It is defensible as a falsifiable finite-benchmark hypothesis, not a promised effect or a calibrated population significance test.

### Request/storage admissibility

For a run, `R = feed polls + live-directory requests + all body attempts dispatched before its checkpoint`; include failed, unknown, rejected, and still-pending attempts. F/archives have separately permitted atomic terminal requests. No retries/refunds/hidden requests. The common terminal feed poll is included.

For each E(q)/periodic phase pair at the **same cap, checkpoint, feed/latency settings, trajectory and retention convention**:

`matched_j = (R_E <= R_periodic_j) AND identical shared metadata accounting/access`.

For a full 60-phase summary to be called request-admissible, require **all 60** pairwise checks: equivalently `R_E <= min_j R_periodic_j`. Do not match to mean/max periodic requests, average only passing phases, select a favorable phase, or interpolate a collector. Publish the 60 flags, admissible fraction, request gaps and mean/min/max requests. A partially matched family has a descriptive all-phase difference but **no budget-matched primary decision**. Secondary pairwise matched points may be labeled individually, never presented as the preregistered all-phase test.

Equal cap is equal *allowed* S, not equal realized final occupancy or equal total cost. M must be identical for continuous policies at identical interface settings; mismatched M/feed streams are an invariant failure, not another treatment. Requests and caps are the frozen admissibility dimensions, not a scalar utility. Section 6 requires the remaining cost dimensions beside any headline.

### Exhaustive result labels (no q selection)

| Condition | Required primary statement |
|---|---|
| E30 all-phase admissible, K nonempty, D ≥ 10 | `THRESHOLD_MET_IN_CONDITIONAL_BENCHMARK`; report D, counts, all phases and robustness qualifications. Not historical loss or population significance. |
| E30 admissible, 0 < D < 10 | `POSITIVE_BUT_BELOW_PREREGISTERED_THRESHOLD`; hypothesis not supported. |
| E30 admissible, D = 0 | `TIE`; hypothesis not supported. |
| E30 admissible, D < 0 | `PCD_BETTER_ON_PRIMARY_ESTIMAND`; hypothesis not supported. |
| E30 fails any phase request check | `PRIMARY_UNMATCHED`; hypothesis not tested at its preregistered budget rule. Show D only as unmatched descriptive contrast. **Do not promote E100/E300.** |
| Multiple q values admissible | E30 remains primary. Show **every** q and their flags/contrasts; no winner selection by coverage or maximum gain. |
| E30 unmatched but another q admissible | Primary remains unmatched; other q is explicitly secondary. Do not presume request monotonicity in q. |
| No q admissible | `NO_PREREGISTERED_EVENT_CONFIGURATION_MATCHED`; publish full cost surface, no budget-matched superiority claim. |
| K empty, invalid labels, incomplete required run, or a gate failure | `NA_EMPTY_DENOMINATOR` or `NOT_EVALUABLE` with reason; never a zero, tie, or primary success. |

A gain against P/PD does not establish the primary hypothesis if PCD ties/wins. A primary gain that disappears against the stronger retention-repair control must be described as conditional on the preregistered changed-only implementation, not general event-driven superiority. A durable-archive collapse must appear beside the live-only claim. No prespecified unfavorable result is a project kill criterion.

## 2. Exact logical experiment matrix

One logical configuration is a row even when identical schedules are safely reused. No label-dependent dispatch, early stopping, downsampling, or tuning. Generate the complete row manifest **before** any scoring and hash it. Use integer microseconds throughout.

### Fixed values

| Dimension | Frozen values / interpretation |
|---|---|
| Source | Pinned September 3 core export; DSE only. All 13,403 held saves, 5,217 successful deletions and four BU edits in background replay; 5,154 mutation-addressed keys are NOT preloaded to collectors. Probes and relation edges are not additional mutations. |
| t0 | `2026-05-24T00:00:00Z`; initial state/discovery unknown/empty. |
| Checkpoints C | `2026-07-03T00:00:00Z` (secondary) and `2026-07-15T00:00:00Z` (primary). Each evaluated as its own prefix, with requests in [t0,C), completions through C and terminal feed poll at C. No new periodic sweep/E dispatch at C. |
| Periodic policies | P, PD, PCD; Δ in **1, 5, 15, 60 minutes**. P intentionally fresh-body; PD/PCD exact dedup. |
| Periodic phases | j=0…59, `phi_us=j*Delta_us//60`; these intervals divide exactly. Schedule t0+phi+kΔ in [t0,C). Feed epoch never shifts. |
| E settings | q=**30,100,300** body attempts/hour; q token capacity, initially q, continuous exact refill; dispatch each minute from t0 in [t0,C); oldest pending visible event time then opaque title. No E phase sweep or 60 replicated E runs. |
| Caps B | **65,536; 262,144; 1,048,576; 4,194,304; 16,777,216; 33,554,432 bytes; null (uncapped)**. Null is a diagnostic, not infinity encoded as a number or a substitute primary. |
| Publication lag L | **5,30,60 seconds**. |
| GET response delay Dg | **0,5,30 seconds**. |
| Poll interval | **60 seconds**, fixed epoch t0. Polls at t0 through C inclusive. One charged batch request even when empty. |
| Feed/response | R04 accounting schema, no content/revision/hash/label in feed; selected-time eligibility plus lag; current body at response completion. |
| Storage | R04 FIFO capture packets, exact canonical UTF-8, no gzip/diff/semantic compression; standalone oversize rejection before eviction; refcounts and exact byte equality; no zero-reference cache. |
| Retry/service | None in PCD/E primary; attempt services dirty work regardless of outcome; new delivered live change can mark dirty again. P/PD repeat on sweeps as specified. |
| Unknowns | Explicit BU/unknown/ambiguous/unsupported; never an empty body. Post-C responses are pending at C, not completed transfers. |
| Source-time uncertainty | Nominal main matrix. Separate closed ±u convention in block U, not calibrated historical clock error. |

### Required blocks

1. **L — live-only full grid:** cross all B × C × L × Dg. At each cell: P/PD/PCD × four Δ × 60 phases, plus the three E rates. This is **91,098 logical rows**: `7*2*3*3*(3*4*60+3)`. Full 3×3 lag/delay factorial, not selectively displayed one-factor changes. Reuse of a label-independent request stream across caps is allowed only after schedule/cap invariance tests; store replay must still be correct per cap. Never replay an annotation-only background.
2. **F — final-live-only:** seven caps, **T only**, one state-derived directory and one GET per listed live/BU title, lexicographic title order, exact dedup, atomic zero-delay checkpoint. No feed. Seven rows. No latency/phase copies of this abstraction; secondary-checkpoint F is outside v0.1 rather than silently extrapolated from the current T-only API.
3. **R — stronger periodic repair control:** `PCD-R15` (§3), all 60 phases × seven caps × both checkpoints × all nine lag/delay pairs: **7,560 rows**. Compare to the corresponding existing E rows with the same per-phase/all-phase admissibility rules. Supplemental, not a replacement primary comparator.
4. **O — ordering stress:** P15/PD15/PCD15 and all three E rates at 1 MiB, both checkpoints, lag5/delay0; **366 rows**. Reverse title service order at periodic sweeps; for E retain oldest-pending priority but reverse the title tie-break only. Admission still follows actual request sequence; no reversal of source chronology. This tests alphabetic-title/FIFO interactions, not an optimized alternative ordering.
5. **A — optimistic terminal persistent archive:** at T only, lag5/delay0 live prefixes, seven caps: P15/PD15/PCD15 (all 60 phases) and E30/100/300, each with the identical terminal archive augmentation in §7. **1,281 rows**, plus seven archive-only A rows (empty starting S/M, same enumeration and GETs). Uncapped archive-only is the costed recovery ceiling. P retains its non-dedup mode, all other rows exact-dedup. No F+archive is needed; it has no additional archive affordance beyond A and would only add a different live prefix.
6. **U — chronology/eligibility robustness:** primary interface and 1 MiB, both checkpoints, P15/PD15/PCD15 all 60 phases and three E rates. For each of these **366 configuration families**, report (a) shared consistent nominal-tie trajectory range, (b) closed ±u trajectory range, and (c) conservative stable-support re-scoring defined below. These are families of realizations, not 366 invented single trajectories. Identical realizations must drive compared policies' feeds, reads, queues and FIFO; range request admissibility too. Archive/repair/latency cross-products with U are not required v0.1.

Blocks L/F/R/O/A contain **100,319 logical run rows**, before U trajectory expansion and evaluation-only split/metric summaries. This is a completeness check, not a feasibility measurement or a results count. Output separate block IDs even where two rows happen to coincide. The matrix is not reduced based on observed speed or outcomes. A resource failure yields an explicit missing row and an incomplete-run status; an outcome-blind scope amendment is needed before beginning a smaller study.

Implementation optimizations may stream bodies, reuse immutable source parsing or deduplicate identical run computations with a `reused_from` key. They must preserve all logical rows, outcomes, costs, sequence numbers and packet widths. Record actual execution/reuse; do not report a cached-row runtime as a separately measured policy runtime.

## 3. PCD strength and prespecified PCD-R15

PCD is the strong **change-aware, schedule-only** periodic control, not the optimal periodic collector. It processes all observed live changes at each sweep and has no event-rate limit. Removing unchanged repeats avoids a deliberately wasteful comparator. Do not give it archive bodies through the live GET path or add immediate off-sweep reads.

An allowed periodic strategy omitted by PCD is reacquisition of still-live text after FIFO evicts its last relevant packet. Freeze this parameter-free hostile control before any outcomes:

- Same observer, Δ15/phases, dedup, feed, FIFO and lexicographic sweep order as PCD. Storage is serviced online in completion order before each sweep eligibility decision; process due completions after source mutations/feed updates and before new reads at a common instant.
- Maintain, per title, the most recent **completed** GET outcome and, for a known body, its locally computed canonical hash and byte length. No retained text outside S. These maps/indexes are measured implementation overhead under the same R04 boundary, not free semantic evidence. Hash collisions fail closed.
- At a sweep, form the ordinary PCD dirty candidates. Additionally include a believed-live/mixed title whose most recent completed GET was a known body, whose last-known standalone packet/body would fit the current cap (using the prospective sequence's packet width), and for which **no currently retained packet for that title references that last-known body**. Uncapped has no repair candidates absent another eviction mechanism. A title with a pending request is not repaired.
- Determine ordinary dirty plus repair candidates at sweep start, visit their union once in title order. Ordinary dirty work is always attempted even if last-known size was oversize. For repair-only candidates, evaluate the size check using the actual prospective request sequence when visited. No same-sweep retry or feedback-induced additional candidate. Every attempt costs the same. Update the last-completed metadata only at response completion; any unavailable result prevents repairs until a subsequent known-body completion. A new feed change remains ordinary dirty work.
- Do not attempt never-fetched titles through repair or fetch a prior revision. Current GET can return a replacement/missing body. Shared content retained under another title is not a free provenance packet for this one.
- Clearing dirty on attempt, deletion invalidation and later re-dirtying remain PCD rules. No semantic selection, body cache, size-based skipping of ordinary changes, future liveness, or off-sweep request.

PCD-R is a distinct supplemental collection/retention strategy, not an assertion it always dominates PCD. Repair can add costs and evictions. Show all of it even when worse. It tests baseline competence without weakening E or changing the primary. Other strategies (LRU, selective retention, conditional requests, semantic compression) are not part of v0.1; several require different interfaces/storage contracts. Do not claim universal optimality from this finite roster.

## 4. A11 freeze and evaluation boundary — BEFORE E12

A03 is a pilot, not the full benchmark. Before implementing semantic evaluation, research owner and second reviewer must pin the following data-only artifacts and hashes: sampling frame/inclusion-rejection log, named sample/episodes, group graph and splits, evidence units, fragment definitions, occurrences, core/context alternatives, exact eligibility mask with reasons, uncertain alternatives, review/adjudication ledger, and rubric supplement. Any already-existing outcome-blind named sample/split must be preserved and reconciled, not overwritten with a new favorable one.

If no split exists (none located at audit), use this exact rule: a group is the connected component of same-title episodes, validated copy/continuation relationships, shared semantic units and cross-title support dependencies. Canonical group key is its smallest opaque page key. All pilot groups are development. Sort remaining components by `SHA256(UTF8("20260912:" + group_key))`, tie by group key; assign indices 0,2,4,… to held-out, indices 1,3,5,… to development. Resolve all occurrence-search links before assigning; recompute once at A11, never after policy outcomes. Do not break a group to balance counts. Report achieved balance.

Retain the ≥40 adjudicated-episode / ≥20 title-copy-group design target and approximately half held-out aspiration. The 60–120 proposition count is a feasibility target, **not permission to truncate valid units**. Freeze the named candidate frame and annotation stopping rule/effort budget before scoring; every candidate has disposition and every completed eligible unit enters its assigned set. Include ordinary material and non-deletion contexts; never select by estimated lifetime, number of transient revisions, likelihood E captures, or dramatic deletion. If targets are unmet, pre-score a recorded **exploratory-only** scope decision; do not pretend the ten pilot propositions instantiate the full design. A smaller study may retain the same contrast descriptively but cannot inherit the full-design headline status.

Freeze these semantic rules:

- Critical means explicit coordination/answer transmission, restriction-workaround proposal/report, or deliberate communication persistence, as in the execution spec. **Lifetime, subsequent deletion, rarity of capture, collector identity, and expected policy advantage cannot define criticality.** Persistence discourse can be critical on its content, not merely because moderators later deleted it. Ordinary isolated data/links are noncritical. Critical is operational priority, not severity or proven harm.
- Atomic scope separates a posted proposal, a self-reported result, observed publication/deletion, and independently corroborated external outcome. Do not create separate external incidents merely from signatures. Keep negative claims, uncertainty and corrections. Repeated testimony does not prove external execution or independent agents.
- Semantic units count once across duplicates/cumulative bodies/copies. Distinct new scoped claims can be separate with written rationale. The per-proposition occurrence-equivalence ID is **not** the statistical group ID.
- Search the **whole DSE held-body population** for each unit and each required context fragment: exact/multi-span and normalized candidate search, then human review of near copies/continuations. A later cumulative or copied body can satisfy support at its actual acquisition time; an out-of-sample title can preserve an in-sample proposition. No backdating and no automatic equivalence from text normalization or page-family fields.
- Support format must resolve to explicit OR-of-AND alternatives: `core_alternatives=[[fragment_id,...],...]`, likewise context. Each fragment has a typed body-span or observable-feed predicate and validated occurrences. Reject empty alternatives, dangling references and duplicate unit IDs. Every core alternative of a body-grounded unit must require at least one body fragment. No implicit expansion of a list of revision IDs and no free original revision/context requirement if the needed fragment survives later. Each context alternative includes all fragments of at least one core alternative plus any required context; declare required speaker/task/epistemic/temporal context rather than just naming whole original revisions.
- Multi-span fragments require all disjoint spans; a display quotation with ellipses is not a literal match. Declare and validate both source-projection offsets and canonical decoded-text offsets. E05 raw `body` is a Latin-1 byte projection; reconstruct source bytes, verify source SHA, decode its declared codec, then map spans to canonical UTF-8/text. Never compare source hashes to canonical hashes or silently shift offsets. Non-ASCII, multi-span and empty-known-body fixtures are mandatory.
- A feed record preserves only `(page_key, action, selected event_time)` with multiplicity. Private `event_id`, revision ID, actor identity, relationship or corroboration is not retained feed evidence. Link a frozen event fragment only when its observable predicate is satisfied; do not infer a particular member of indistinguishable notifications. A source-private context requirement is unavailable under this interface, not free via evaluator access. Annotators must decide whether it is actually necessary, blind to outcomes.
- Known empty bodies can support only what their text/context really establishes; unknown/BU never becomes empty. Unresolved criticality/core semantics are excluded with pre-score reason; units lacking any exact support are absent from the exact denominator, not policy-specific misses. Unresolved context is NA/unknown, not a declared complete bundle.
- Review 100% of critical, workaround-success, copy-equivalence, recreation-response and uncertainty cases; noncritical ordinary review sample is first `ceil(0.20*n)` IDs sorted by `SHA256(UTF8("20260912:"+evidence_id))`, tie by ID, including all n when n=1. Independently validate all machine-resolvable spans/hashes/references. Research owner adjudicates conflicts; reviewer labels and reasons persist separately. Sam audits all independent-external-success assertions and a frozen support-bundle sample chosen with the same hash rule.

**Evaluator API firewall:** E12 retained-at-C accepts only an immutable retained snapshot: charged packet bytes, body objects still referenced by those packets, and charged delivered feed/directory/archive context. It must not accept `CollectorResult.body_results`, `capture_attempts`, source-store handles or unrestricted audit logs as retention evidence. Export actual retained objects through `CaptureStore` before discarding it; verify references, bytes, cap and hashes. A separate evaluator-private provenance matcher may validate retained bytes against source annotations but cannot supply missing content/context. Capture packet title/time matters even when a body is globally shared.

Ever-captured means **ever admitted to S by C**, not merely downloaded and oversize-rejected. Report ever-downloaded-known-body as a third, explicitly separate diagnostic if desired; it never counts as preserved. Ever-admitted evaluation uses a separate write-only admission/provenance journal, inaccessible to policy decisions and retained-at-C scoring. A poisoned evicted/rejected-body test must fail to increase retained coverage. Missing snapshot objects, bad references or broken hashes abort validation; they are not imputed as misses.

## 5. Statistics, eligibility and unknowns

### Denominators and grouping

Primary unit: one distinct scoped body-grounded proposition; primary population: held-out K. Report all-body core, critical-body core, critical-body context, all-body context, all-source core/context, moderator-event core separately. Each row prints numerator, denominator and percentage; the critical context row uses the **same K** as critical core, with explicit unknown context counts. Do not drop context-difficult critical units to inflate context coverage. At A11, unresolvable context either receives a frozen unavailable requirement (not retained) or is marked unknown and reported with lower/upper coverage; it is never silently counted complete. A primary core decision cannot rely on unresolved core labels.

Produce development, held-out, and pooled summaries for every configuration. Only held-out is primary; pooled is not a fallback primary if held-out is empty. Episodes/revisions/occurrences are descriptive counts, never the coverage denominator. Whole-DSE background load does not make the selected benchmark representative of all DSE evidence.

At July 3, use the same frozen unit inventory, restricting the denominator **only** to units with some exact eligible core support by that checkpoint, independent of any collector. Report units not yet eligible. Do not require that support was feed-deliverable or capturable by a particular policy: feed lag/queue losses are part of the experiment. Both checkpoints are after the last selected held DSE save, but this rule must still be explicit for context and synthetic tests.

One common occurrence eligibility mask: exclude unknown prehistory/BU bodies, unsupported source linkages, all untimed head-mismatch title occurrences (nine flagged held DSE titles, retaining their load), and support confined to incompatible nominal states. Do not exclude an entire proposition if another validated exact alternative remains. Exact eligibility refers to the declared trace, never proven historical continuity. No source archive absence is added to an evidence denominator with invented propositions.

### Aggregation and uncertainty

- Equal weight to each proposition in micro coverage; equal weight to each of the 60 periodic schedules in phase means. Publish j=0, mean, min, max, p10, median, p90, and every phase value for costs and coverage. Quantiles: sorted observations, linear interpolation at index `(n-1)*p`. E appears once with phase=`NA`, not 60 independent samples.
- Group macro robustness: compute each nonempty group's coverage, then average groups equally; for critical coverage omit groups with zero critical denominator and show how many. Also publish per-group numerators/denominators and leave-one-group-out primary D range (groups with K>0); if fewer than two such groups, leave-one-out is NA. Never average per-title duplicates or weight by occurrence counts.
- **No bootstrap, significance p-value, or sampling confidence interval in v0.1.** This freezes the formerly optional bootstrap as not used. Phase ranges are schedule sensitivity; groups are a purposive within-incident robustness analysis, not independent incidents. Report exact conditional effects without population inference.
- Practical reporting: signed percentage-point differences, absolute retained-unit counts, denominators, phase ranges and the fixed 10-point line. Print the one-unit granularity `100/|K|` percentage points when K is nonempty; small-denominator discreteness is not statistical confidence. Relative percent improvements are not headline metrics; zero denominators/baseline zeros cannot yield infinite gains.
- Delay: per retained unit, earliest acquisition time of a complete core bundle whose required captures remain at C, minus earliest eligible recoverable support. Multi-part acquisition time is the latest component; minimize over valid retained alternatives. Delay unknown if earliest support is unknown. Unretained units are failures/right-censored, never zero or omitted without a retained-fraction label. Report conditional median/p90 and counts of retained, ever-admitted, unretained, NA earliest support. No Kaplan–Meier or imputed missing-history times.

### U block: no query-wise favorable worlds

Nominal ambiguity diagnostics are an explicit missing-response convention, not a physical realization. Sensitivity must account for their possible **background-storage spillovers**, not merely delete uncertain labels. For trajectory families choose one time/order for each event, apply that same whole consistent history across policies, and propagate feed publication/delivery, directory membership, body responses, queue/token scheduling, requests and FIFO. Nominal-tie runs hold selected times fixed and vary all source-permitted tied orders; ±u runs admit integer-microsecond times in the full closed windows with supported precedence only. In that counterfactual, the realized mutation time replaces the nominal timestamp in the modeled feed record and publication rule (realized time+lag); the original exported selected clock remains evaluator provenance. Thus uncertainty is a shared-world perturbation, not an E-only clock oracle. At co-timed incompatible events retain the mixed sanitized batch even when the private realization resolves their internal order; reads observe that realization's final group state. No event-ID chronology; no union of alternate bodies.

Freeze solver limit at **10,000 complete realizations/equivalence classes per family**, with deterministic, documented canonical serialization for enumeration (not evidence-based search). An exact symbolic method may certify the complete range without enumerating all time choices. Both min/max must have consistent witness trajectories or a formal range certificate. A limit, unsupported chronology or unproven extrema produces `INCOMPLETE_BOUNDS`, an explicit examined-subset range **not labeled a bound**, and true full-range fields NA. Do not promote an incomplete sampled range to robust evidence. The nominal diagnostic result remains a conditional-model result with that qualification, not a hidden selection of the favorable realization.

Stable-support re-scoring: freeze a second mask before policy scoring that accepts only body-support intervals whose identity/availability is common to all ±u states at that time (or explicitly certified equivalent body text), excluding head mismatches as above. Preserve background load and nominal observation rules. Report its changed denominator and units removed. It is an exclusion robustness check, **not** a substitute for trajectory effects on storage or bounds on all missing historical evidence.

Missing-source bounds: print exact-support coverage plus count of annotated units without any exact support; at fixed full annotated denominator N, if k retained exact units and u unresolved units, show the deliberately loose envelope `[k/N,(k+u)/N]` as **annotation/eligibility-only**, not a whole-replay trajectory bound. Unknown unannotated/withheld historical propositions have no known N; their coverage and historical total-loss fraction are **not identifiable**. This envelope must not be used to bypass FIFO/trajectory uncertainty.

## 6. Cost contract and headline table

Requests and storage cap are sufficient for the named two-constraint comparison, **insufficient for an unqualified “same total cost,” “cheaper,” or operational Pareto claim**. No weighted scalar cost or assumed dollar/HTTP-overhead multiplier.

Headline comparison table MUST include:

- policy/q/Δ; cap B; checkpoint/interface assumptions; denominator/split;
- critical core and critical context coverage, numerators/denominators, primary D/status;
- total requests **and feed/directory/body decomposition**, phase min/mean/max for periodic; unknown/missing/pending counts and admissible phases out of 60;
- downloaded metadata, known-body bytes, NA body-payload count, downloaded total (NA if any completed unknown payload) and explicit known-byte lower bound;
- final and peak **S, M, S+M**, body versus packet bytes, and **S/M/(S+M) byte-hours**;
- peak auxiliary title/dirty/pending/index counts and an adjacent measured overhead/runtime panel (CPU, elapsed/process CPU time, RSS, audit artifact bytes), with measurement scope.

Plot annotations may use compact summaries, but the adjacent linked headline table cannot omit transfer or byte-hours. Equal feed count can dominate total requests and conceal body-attempt differences; always show both. No body-only storage axis mislabeled total retained bytes. S+M peak must be the peak of the synchronized sum, **not the sum of independently timed peaks**. Store temporal component ledgers are required; `StorageSnapshot` alone cannot reconstruct this reliably.

Full costs additionally include successful known responses, per-outcome counts, objects/packets/refcounts, evicted packet/body bytes, oversize rejections, dropped/pending dirty work, starvation/coalescing, and actual outstanding requests. NA transfer bytes are not zero and defeat any exact-transfer matching assertion; dispatched pending requests have no invented pre-C payload. F/archive operations at T have zero pre-T byte-hours by abstraction, not free retrieval or proof of practical instantaneous feasibility.

Report logical auxiliary memory separately from physical process RSS; isolate source parsing/model, collector, store and evaluator/audit overhead where measurable. E's minimum-over-dirty-items loop, periodic scans/sorts, hash/refcount indexes, `_seen_request_seqs`, buffered responses and audit logs have policy-dependent computational costs even though logical payload accounting is neutral. Runtime/RSS on this simulator is not a measured deployment implementation advantage. Missing overhead instrumentation blocks X13 acceptance, not permission to invent zero overhead.

Cost envelopes: for each interface/cap/checkpoint, list all finite realized periodic request counts as reference envelopes, and **all** already generated configurations under each envelope, not just the highest coverage. Mark all nondominated configurations when showing a requests/retained-bytes surface, but do not delete dominated or unmatched points from the master table. No interpolation or post-hoc q optimization.

## 7. Required archive-aware sensitivity and separate ledger

Historical archive access remains unverified. Use this frozen **optimistic persistent-archive counterfactual**, not `archived_at` as a public clock. Every held DSE revision with selected save ≤T is assumed persistently accessible and globally enumerable at T, including deleted titles. Enumerate the **entire held DSE background**, not only eligible/scored/critical revisions. Eligibility cannot leak into collection. Source-private missing bodies remain missing; no invented prehistory. Richer archive IDs are available to **all** archive-aware rows only at T, not to any live collector earlier.

After each live prefix (including allowed live completions and terminal feed poll) perform an identical atomic zero-delay archive phase:

1. One charged global archive enumeration request. Response is C(array) of objects with exactly `archive_key` (opaque released `rev_id` string), `page_key`, and `event_time` (selected save time in fixed six-digit UTC format). Sort by `(event_time,page_key,archive_key)` ascending, retaining every held revision. This is service/enumeration order, not inferred ordering of incompatible historical mutations. No body/hash/label/eligibility/severity/relations. Retain each record as C(record) in additional M through T; response array framing is transfer only. No page-relative discovery restrictions in this deliberately optimistic archive interface.
2. Attempt one archive GET for **every enumeration entry in that order**, even if the body is already in S or an earlier body was oversize. No annotation-aware selection or free hash-based download skipping. No q rate limit in this separately declared terminal recovery phase; charge all requests. This expands both policies' capabilities equally and is not the original live-only budget experiment.
3. Known response header is the same C({"outcome":"body"}) and exact canonical UTF-8 payload. Archive capture packet has exactly the original four packet fields **plus `archive_key`**; charge all five fields using C. `capture_time=T`, title from requested archive entry, and request_seq continues the live body-attempt counter. The extra field is necessary retained archive provenance, not a hidden evaluator join. Archive-only starts sequence 1. A/R fixtures must hand-count this extension before implementation acceptance.
4. Append to the existing capped store with the same FIFO, standalone oversize test, refcounts and dedup mode as that row; do not give archive phase a second cap, protected live partition or free restoration cache. Existing live packets remain four-field packets. Archive metadata adds to M, outside S but fully reported. Enumeration and archive storage at T add peak/final bytes, zero pre-T byte-hours. S+M peak still requires synchronized accounting.
5. Report pre-archive and post-archive results/costs side by side. Match total live+archive requests at equal cap/common archive access using §1, not archive requests alone. Also show archive-only A under each cap, including uncapped with all actual enumeration/GET/transfer/storage charges.

These are modeled terminal recovery scenarios, **not historical archive availability, finite-bandwidth feasibility, or maximum possible capped archive performance**. Fixed chronological FIFO enumeration is just one neutral recovery strategy; a poor capped archive result cannot prove live evidence irrecoverable. Uncapped archive-only is the optimistic recoverable-release ceiling and must be shown even if it collapses all differences. A later verified archival-availability model requires a separate documented amendment, never substitution selected by its policy result.

Forbidden without historical archive semantics: “responders could not recover this evidence later,” “deletion permanently erased X%,” “15-minute historical responders lost X%,” or extrapolation to all incident evidence. If archive durability collapses differences, say **the live-only scheduling contrast is not an operational irrecoverability result; persistent discoverable archives can remove it under this scenario**. Do not say native archives did so historically without evidence, or that timing never matters for earlier investigation.

## 8. Automatic outputs — no favorable subset

All data tables in UTF-8 CSV plus machine-readable JSON manifest with explicit nulls/reason codes. Figures SVG and PNG generated only from frozen CSVs, no hand edits. Sort configuration IDs deterministically by block, checkpoint, lag, delay, policy order F/P/PD/PCD/PCD-R/E/A, Δ, q, cap (uncapped last), phase. Store exact integers/rational numerators; presentation rounding never determines admissibility or threshold status.

| Output | Required content |
|---|---|
| `run_manifest.json`, `configuration_manifest.csv`, `completeness.csv` | All expected logical IDs/statuses/reuse links; source/code/config/annotation/split/rubric/audit hashes; environment, interpreter/lock, seeds, UTC start, CPU/memory instrumentation; separate nondeterministic runtime metadata. Missing/failed rows explicit. |
| `all_configurations.csv` | Every L/F/R/O/A run, all costs and outcomes from §6, retained/ever-admitted counts, all metric numerators/denominators/unknowns for each split. No silent blank rows. U has its own complete family index. |
| `headline.csv` | T, primary interface, 1 MiB; F, P15/PD15/PCD15 summaries, all q, PCD-R15, archive-only and archive-augmented comparison summaries, including all unfavorable or unmatched rows. Exact primary D and decision status. |
| `admissibility.csv`, `cost_envelopes.csv` | Every E-versus-periodic phase pair for same settings and cap, R gaps/flags, all-phase flag/count; request-envelope memberships for all existing eligible points, no winner-only filtering. |
| `coverage_cost.svg/png` | Primary-interface T, all seven caps, P15/PD15/PCD15 and all E(q), F shown as distinct-access baseline. Overall body core, critical core and critical context panels. X=final S+M bytes, cap labels and S/M decomposition available; request count visibly encoded and explicitly labeled, unmatched points hollow. Periodic phase means with p10–p90 and min/max, zero-phase markers. Companion requests-vs-retained-bytes panel; uncapped distinct markers. Do not connect phases as independent incidents or imply interpolation creates feasible configurations. |
| `phase_values.csv`, `phase_distribution.svg/png` | Every phase j and periodic policy/Δ; critical/core/context and cost distributions, signed paired differences for every q at primary cell; all 60 points, zero marker, fixed 10pp line. No trimmed outliers or n=60 CI. |
| `latency_checkpoint.csv`, `latency_checkpoint.svg/png` | Full 3×3 lag/delay factorial, both checkpoints, all Δ/q/caps in table; primary-cap facet plot includes all periodic Δ and q. Identical axes/scales, no best-latency-only presentation. |
| `baseline_robustness.csv`, `baseline_robustness.svg/png` | PCD vs PCD-R at Δ15 (all required R settings); order stress O; signed differences, extra requests/bytes and admissibility, including reversals/nulls. Main-figure caption points here. |
| `group_metrics.csv`, `group_robustness.csv` | Every frozen group, per-split numerator/denominator, micro/macro, leave-one-group-out range and zero-critical groups. Development and pooled not silently mixed into held-out. |
| `unit_retention.csv`, `delay.csv` | Frozen evidence ID × config: retained core/context, ever-admitted, unknown reason, witness retained packet/fragment IDs (no forbidden raw redistribution), delays and censoring. This artifact is created **only after authorization**, never fed back to collectors/annotators. |
| `eligibility_missingness.csv`, `unknowns.csv` | Source-population counts separately, all occurrence/unit exclusions with reasons, head mismatches/BU/prehistory/ties/unmatched spans/context, unresolved equivalence, denominator flow, annotation-only envelopes. Explicit distinction between collector miss/eviction/oversize and unheld source history. |
| `chronology_sensitivity.csv`, `chronology_sensitivity.svg/png` | Every U family, complete/incomplete status, witness/certificate IDs, coverage and request/admissibility ranges, stable-mask denominators. NA full bounds if incomplete; no cherry-picked witnesses. |
| `archive_sensitivity.csv`, `archive_sensitivity.svg/png` | All A rows, pre/post-archive contrast, archive-only at each cap and costed uncapped ceiling; archive enumeration/GET/packet/M costs, explicit optimistic/atomic labels. Always next to live-only interpretation, including a complete collapse. |
| `case_walkthrough.csv`, `case_walkthrough.svg/png` | Prespecified **DataUSAConstructionWageSep18Live + ZZZDataUSAConstructionWageLive** group, full t0–T context with a June19 detailed panel; all its A11 units, not a chosen successful proposition. P15/PD15/PCD15 zero phase, E30/E100/E300, 1MiB primary interface, plus PCD-R and archive recovery. Show eligible occurrence lifetimes, deliveries, GET completions, retained/evicted/rejected states and bundle context; distinguish claims from actions. Zero phase chosen now, not best separation. If excluded or absent from A11, show that reason and source-only history; **no replacement case**. This is an enriched pilot illustration, not the primary held-out sample. |
| `overhead.csv`, `reproducibility.md` | Per-run measured/logical overhead, source/model/evaluator separation, actual versus reused runs, CPU/RSS/disk limitations; independent clean-environment reproduction, determinism and all failed checks. |

Use shared 0–100% coverage axes and signed difference axes that include zero and ±10pp. Report NA, unmatched, unscored, failed, and incomplete as distinct statuses. Never draw missing metrics at zero. All secondary Δ/caps/lag/delay/q values remain in tables even when plot space requires fixed facets. No favorable-only plots replacing these mandatory artifacts.

## 9. Execution authorization checklist

Before E12: close audit issues A01–A05 in `PRE_RESULTS_AUDIT.md` (audit provenance, accepted hashes, annotation/evaluation contracts, retained-only boundary, population firewall); A11 data/semantic acceptance must exist. Repair work and synthetic fixtures may proceed while blocked; semantic scoring against real captures may not.

Before X13: E12 independent hand-scored synthetic acceptance; checkpoint/causal-time fixes; F, PCD-R, order stress, archive ledger and U machinery implemented/validated; synchronized cost/overhead instrumentation; complete hashed matrix/output schemas and offline reproducibility entry point. Named reviewer records authorization. All source/annotation data immutable at launch. No network/model calls or embedded-URL execution during reproduction.

A configuration validation error aborts the affected scientific result, rather than silently falling back. Any nominal `unsupported` outcome caused by engine limits/implementation inability makes that run `NOT_EVALUABLE`, including when it concerns an unannotated background title: missing its body can change FIFO for scored evidence. It is not a valid collector miss or a policy-specific label exclusion. Unsupported rigorous bounds may produce the declared incomplete U report, never a robust range claim. A missing required implementation or absent mandatory output blocks **X13 acceptance/publication of a completed experiment**. A null, below-10pp effect, PCD win, unmatched E or archive collapse does not.
