# R04 v0.1 — partial freeze

**R04 PARTIALLY BLOCKED ON A03. CONDITIONAL GO E06 only.**

Authority/scope: local-record adjudication requested by the user; no claim of signed team ratification. Read `V02_ADJUDICATION.md` and `E06_IMPLEMENTATION_CONTRACT.md`. This freezes only the decisions below. It is not a completed TOML configuration, benchmark, split, evidence-label freeze, software acceptance or experiment result. First-pass reconstructions and earlier planning documents remain unchanged.

## 1. Frozen design and source/model decisions

| Decision | Final v0.1 value |
|---|---|
| Study description | **Trace-grounded simulation under a shared hypothetical monitoring interface**, technically a conditional released-trace replay. Not measured historical HTTP visibility, complete incident evidence, or permanent erasure. |
| Source/population | Pinned September 3 core export, DSE only: 13,403 saves/held revisions, 5,217 successful deletions, four bodyless successful form_edits. All 5,154 mutation-addressed title keys participate in background load/discovery potential, including 1,246 titles without held revisions. No preload of that universe to policies. Probes are neither live mutations nor triggers. No other-wiki/shortener/expanded-record populations. |
| Replay horizon | `2026-05-24T00:00:00Z` through terminal checkpoint `2026-07-15T00:00:00Z` (T); ordinary collection schedules run in [t0,T). Additional report checkpoint `2026-07-03T00:00:00Z`. State queries at T summarize the censored trace; T is not a deletion. |
| Horizon verification | Local raw recheck: first/last save May 24 06:02:19 / July 2 17:24:40; first/last deletion June 4 10:53:40 / July 14 13:56:54; first/last bodyless edit June 19 23:19:13 / June 21 17:26:56 (UTC, 2026). All selected boundaries and ±1s windows fit. No outcome-dependent endpoint selection. |
| State model | `unknown`, `live(body_ref)`, `live(body_unknown)`, `deleted`. Selected-time, full replacement on save; successful deletion removes live content; the four audited bodyless edits install BU. Post-delete supported live mutation starts another modeled episode. Initial existence is unknown. |
| Continuity | Explicit **no-unobserved-intervening-mutation assumption**, for deleted as well as live states, until next supported mutation or censoring. Known missing successful body-changing action invalidates old content; undocumented action semantics remain unknown/review-required. Never invent a missing mutation time from untimed metadata. |
| Ordering | Half-open state intervals; unambiguous mutation before read at equal time. Same-time incompatible mutations have all permissible orders, not an ID/seq winner. Separate nominal selected-clock model and closed ±uncertainty_seconds sensitivity, including touching endpoints. Precise API in E06 contract. |
| Provenance | Relation edges, archive clocks, final store descriptors and page-family aggregates do not mutate states. All source clocks/hashes retained privately; no fallback backdating. |
| Eligibility | Exact means exact **within the declared nominal trace model**, not historical certainty. Unknown bodies/prehistory supply no body proposition. Exclude untimed head-mismatch titles from exact body scoring; retain modeled load. Incompatible ambiguous support is excluded from exact occurrence support or evaluated through a separate admissible-trajectory analysis. No observer behavior is changed using retrospective eligibility. |

The held-title universe is 3,908; 5,154 is the union of mutation-addressed keys, **not an initial observer directory**. Raw counts do not prove adequate semantic sample size.

## 2. Frozen hypothetical interface and policy settings

These are design choices, not claims about a historical public API. E06 does not implement this observer or any collector.

- **Common feed:** P/PD/PCD/E receive only title key, normalized successful action and selected event time. The feed covers the released mutation population, not a claimed exhaustive historical log. No body, revision pointer, relation, label, priority, future count or probe. Save and bodyless successful edit are live-change notifications; deletion is shared event context.
- Publication lag **5s**; common charged batch feed poll every **60s** from UTC t0. Each record becomes eligible when event time + lag ≤ poll time; deliver once. All time-based policies retain the same compact feed log, charged outside the body-store cap. Same-time batch members supply no source-resolved internal chronology.
- Body GET uses **response-time current modeled state**, never a trigger revision. Primary delay **0s**, sensitivity **5s/30s**; publication-lag sensitivities **30s/60s**. Every attempt is charged. Deleted = modeled missing response; unknown and BU = distinct unavailable/unknown responses, not empty text/404. Ambiguity stays evaluator-side alternatives, never free access to multiple bodies.
- Discovery only through delivered feed. At a common instant: apply source mutation group, process eligible feed poll/delivery, update policy knowledge, then schedule reads. This is an interface convention, not historical chronology. T finalization includes already scheduled responses due by T, not new ordinary sweeps at T; response-delay requests completing after T cannot support retention at T.
- **Final-only F:** separate low-information baseline. At T receives one assumed current-live-title directory per admissible realization, including BU titles, and attempts one GET per listed title. It has no continuous feed history. This terminal batch is an explicitly atomic, zero-delay checkpoint abstraction; charge directory and all GETs. Do not stretch replay to favorable post-T bodies. Directory is derived from modeled states, never pages.jsonl flags/last bodies. Historical directory fidelity unresolved.
- Unknown title existence yields no asserted live-directory membership; a scenario whose directory membership differs must retain that difference in bounds, not union directories into a privileged F run.
- **Roster:** F; P (full periodic snapshots, fresh body per successful response); PD (same requests, global exact-body dedup plus captures); PCD (changed-only periodic exact-dedup strong control); E(q) (bounded dirty-title collection, exact dedup). PCD15 is required, not optional. No semantic priorities.
- **Intervals:** primary 15m; secondary 1m, 5m, 60m. P/PD sweep discovered titles currently believed live. PCD services changes since its last sweep. Unknown/mixed knowledge cannot be silently treated as a confirmed deleted title; operational branch behavior must remain consistent within each admissible realization.
- **E rates:** headline candidate q=30 attempts/hour; secondaries 100,300. Token capacity q, initially q, continuous refill q/hour, minute dispatch on common epoch. Dirty updates coalesce; oldest pending visible change first, then visible title key. Deletes remove pending live reads. Consume tokens on every attempt, including unknown/missing. Visible-title scheduling tie-breaks are not historical source-event ordering.
- **Phase grid:** 60 global phases phi=j*Delta/60, j=0..59, from UTC t0; no page-relative reset. Feed epoch fixed. Publish zero-offset and phase mean/min/max/p10–p90; no n=60 independent-incident CI. Integer microsecond times.

## 3. Frozen retention and costs

- Body/capture store cap **1 MiB** primary. Secondary **64 KiB, 256 KiB, 4 MiB, 16 MiB, 32 MiB**, plus uncapped diagnostic. Binary units. Common feed-log bytes are additional and reported, not hidden in “1 MiB total”.
- FIFO **capture packets**: each successful known-body response gets capture metadata plus a body reference, even if repeated. P allocates a fresh body object; PD/PCD/E share globally exact-equal canonical bodies. No semantic/diff compression. Evict oldest packets until admission fits, free a body only at zero references. For identical admission times use policy's request sequence, then visible title key. No annotation-aware eviction.
- Before evicting, reject an intrinsically oversize standalone packet+body, log reason, keep existing store; do not truncate. Otherwise recompute incremental bytes/refcounts through FIFO eviction and admission. Repeated-body capture metadata still costs bytes. No free retained body cache.
- Byte rule: canonical UTF-8, sorted JSON keys, separators `(',', ':')`, `ensure_ascii=false`, LF for JSON records; source-body byte hash/encoding separate from canonical storage identity. No primary gzip discount. Count bodies, refs and packet metadata in the cap. Immutable source export/evaluator stores are not accessible policy caches.
- **Exact field-level storage/feed/directory serialization schema and hand-counted byte fixtures are DEFERRED to a pre-E08 accounting amendment**, not left to outcome-driven implementation. This blocks E08/storage/collector execution, not E06: budgets, FIFO, all charged components and serialization convention are frozen now; no numerical retained-byte claim is authorized until exact fields/fixtures are frozen.
- Report feed/directory requests, all body attempts, known-body successes, missing/unknown responses; downloaded modeled payload/metadata bytes (not exact HTTP wire overhead); retained body objects/capture packets; peak/final bytes, bytes evicted, byte-hours; discovery-map/queue memory; runtime/RSS and named CPU. Unknown downloaded body size is NA/bounded, not fabricated zero; response envelope bytes still count once schema is fixed.
- Cost admissibility requires **both** equal store cap/common metadata accounting **and E realized total requests ≤ periodic comparator**. Publish all preregistered q points; q30 above comparator requests is unmatched, not a reason to tune q. Include PCD15 and two-dimensional cost surface. Envelope admissibility may use cost only, never coverage to pick winners.

## 4. Frozen metric form — not evidence semantics

The following algebra is frozen conditional on a later A03/A11-approved evidence set. No proposition, criticality label, support equivalence, eligibility denominator or sample is approved by this freeze.

For each distinct unit, core retention is true iff all fragments of any one frozen core support alternative survive in actual captures/context at T. Context-complete retention uses context-complete alternatives. Validated later cumulative/copy occurrences can support a proposition when actually captured later, never earlier. Copies count once, not once per revision/signature.

Primary reporting: body-grounded overall core coverage; critical body core coverage; critical context-complete coverage. Separately report all-body context, all-source and moderator-event coverage, loss=1-coverage, numerator/denominator and ever-captured versus retained-at-T. Moderator metadata cannot inflate primary body contrast. Empty denominators are NA.

Delay: earliest acquisition of a core bundle that survives at T minus earliest eligible recoverable support. Multi-fragment bundle acquisition is its latest component acquisition. Unretained units are failures/censored; unknown earliest support is NA/bounded, never zero. Show retained fraction with conditional median/p90. Title/copy-group macro robustness; optional exploratory group bootstrap seed 20260912, not revision bootstrap.

### Exact versus ambiguous scoring

Use one pre-outcome evidence denominator and occurrence eligibility mask for all policies/configurations. An excluded occurrence does not erase a unit that has other validated eligible support. If a unit has no eligible exact support, exclude it from the common exact denominator with reason and retain it for an explicitly separate bounds/unknown report. Do not drop a unit only for the policy that queried during ambiguity.

For bounds, use whole consistent admissible trajectories with the **same trajectory for compared policies**; propagate differences into feed/directory/GETs, queues, retention and support times. Report min/max over those trajectories with a fixed denominator. Do not independently choose a favorable state at each query or count a union of alternative bodies as a capture. Bounds are conditional on declared clock/closure assumptions, not bounds on all missing historical evidence. Full-run bound computation is later evaluator work; E06 must expose uncertainty without pretending to compute coverage.

## 5. Archive-aware requirement

A live-only contrast is insufficient for operational irrecoverability claims. Required before such claims: either a documented, costed archive-aware baseline with verified availability/discovery/expiry, or the preregistered **optimistic persistent-archive sensitivity**: all eligible held bodies discoverable and retrievable by T, persistent through T. Give compared policies equal archive affordance and charge enumeration/GET/storage costs under a separately frozen archive ledger. This is not historical fact and does not set availability to archived_at. A perfect, uncapped final archive may be shown as evaluator-only recovery ceiling, never a free collector. No public archival-start time or lag tolerance is frozen; maintainer questions remain unanswered/unsent in the local register.

## 6. Deferred/blocking register and departures from the earlier spec

| Item | Disposition / reopening requirement |
|---|---|
| A03 pilot and evidence-label semantics | **BLOCKER** for full R04/A11/scoring. Need Alex/Aaron artifacts satisfying all six criteria, actual second review and adjudication. No fabrication from narrative timeline. |
| Named population sample/splits | **DEFERRED/BLOCKED on A03**. Retain design target ≥40 episodes, ~20 development/~20 held-out, ≥20 title/copy groups, 60–120 propositions; not a claim of achieved feasibility or a frozen named benchmark. Keep episodes/copies together; whole-DSE occurrence search; smaller explicitly exploratory study only by documented pre-outcome amendment. |
| Full V02/V07 | **BLOCKER for full E06 completion**, not restricted development: blind packets 04/08 need controlled comparison; 09/10 need independent raw expectations. No joint signoff inferred. |
| Historical source semantics | **UNRESOLVED**, bounded by trace-only scope: clock interval/correlation, same-second guarantees, short/missing mutations, exact/fallback links, head/live fields, cache/archive semantics. No reply is not a STOP for simulation. |
| Missingness rate | **DEFERRED**. No probability inferred from request-minus-revision counts. Future stress scenarios preregister parameters before outcomes. |
| Precise cost schema, retries/unknown-service behavior and accounting tests | **DEFERRED to pre-E08 amendment**. No collector implementation/runs until pinned; no E06 dependency on evidence or storage layout. |
| Rights/novelty | **UNRESOLVED release/claim gates**. No blanket redistribution permission or novelty guarantee inferred from local download or silence. No new raw excerpts redistributed here. |

Numeric grids, source scope and horizon do not differ from `EXECUTION_SPEC_v0.1.md`. Clarifications/departures are explicit: (1) the “Frozen” heading there did not complete gates; this is only a partial freeze; (2) simulation wording is mandatory now, not postponed until results; (3) AI/Naco/control remain selected but not jointly reconstructed; (4) full A03/full-V02 prerequisites are waived **only for restricted E06 development**, not acceptance or downstream tickets; (5) archival proxy use is disallowed absent semantics; (6) endpoint/trajectory conventions and atomic F checkpoint are declared modeling choices; (7) 14m22s is the cited pair's timestamp difference, not first propagation or independent external success. Earliest-support/criticality claims still await A03. These decisions are source/feasibility-driven; there are no policy results to tune against.
