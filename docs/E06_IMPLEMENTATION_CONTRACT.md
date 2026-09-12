# E06 implementation contract — restricted v0.1

**CONDITIONAL GO E06.** Ubayd may implement a minimal offline timeline/state-query engine and its tests from E05's validated immutable records. **Do not implement feed/GET observer, collectors, storage, evidence evaluator, scoring, plots or experiments in E06.** No such code is created by this adjudication.

Dependencies actually established: E01/E05 PASS; six published V02 cases support the restricted rules; source/interface design decisions are partially frozen. **Full V02 acceptance and R04 remain incomplete; R04 PARTIALLY BLOCKED ON A03.** See `V02_ADJUDICATION.md` for missing independent answers and blind custody. Starting E06 is not declaring it complete.

## 1. Allowed model and transition rules

All timing/state installation below describes a **conditional released-trace model**, not measured public responses. Population: DSE successful saves/deletions and the four audited bodyless edits only. Work from selected exported `time`, never task dates or an undocumented alternate clock priority. Preserve original clocks separately.

| Candidate rule | Classification | Permission / limit |
|---|---|---|
| Validated held save at t: any state → live(body_ref) | `SAFE_ONLY_UNDER_RELEASED_TRACE_MODEL` | Full linked revision body replaces prior content at selected save time, even if identical or cumulative. Held text/save is supported; exact public availability is not. |
| Successful deletion: any state → deleted | `SAFE_ONLY_UNDER_RELEASED_TRACE_MODEL` | Selected successful deletion clock, not request or archive time. Removes live modeled body, says nothing about native archive recovery. Repeated delete is allowed without inventing a live episode. |
| Audited successful bodyless form_edit: any state → live(body_unknown) | `SAFE_ONLY_UNDER_RELEASED_TRACE_MODEL` | Clear any old body. Not a restored revision, blank body or generic rule for every null revision_ref. |
| Supported live save/edit after deletion starts another modeled episode | `SAFE_ONLY_UNDER_RELEASED_TRACE_MODEL` | Start at supported mutation, never relation-linked earlier time. Ordinary saves stay in the same episode. Actual first historical recreation may be unheld. |
| Carry any current state to next supported mutation/censoring | `SAFE_ONLY_UNDER_RELEASED_TRACE_MODEL` | Includes deleted. Requires no unobserved intervening mutations. A known missing successful body-changing mutation invalidates prior content; unknown action outcome must not be guessed. |
| Initial unknown; unavailable body has no body/hash | `SAFE` | Never infer absence or initial creation from seq=1, page_created, zero pre-cut count or final directory. |
| Relation/copy metadata has no state-transition effect | `SAFE` | Preserve edges privately as provenance. Relation-driven transitions/backdating/duplicating mutations are `UNSAFE`. |
| Archival clock/final flags establish live end/current body/archive start | `UNSAFE` to implement | Their historical semantics are `UNRESOLVED`. No transition even if a clock often correlates with next save. |
| Resolve incompatible ties using event ID, input order, seq, RCS, diff-base | `UNSAFE` | These are not documented public chronology guarantees. Sorting is serialization only. |
| Preserve admissible partial orders/states | `SAFE` | No merged body or arbitrary winner. |
| ±u seconds as publisher-guaranteed uncertainty interval | `UNRESOLVED` | Closed symmetric windows permitted only as labeled project sensitivity, `SAFE_ONLY_UNDER_RELEASED_TRACE_MODEL`. |
| Probe/request or text success claim becomes page mutation/external success | `UNSAFE` | Action success has narrow scope. Unsupported actions fail closed for review. |

The bodyless rule applies to these exact audited events, all with success_observed=true, action=form_edit, revision_ref=null:

| Event ID | Page key | Selected UTC time | Native edit evidence |
|---|---|---|---|
| revert:delete:dse:rclog:145962 | dse~OpenAIDataUSAPoliceBridge20260129 | 2026-06-19T23:19:13Z | rclog:146041; reqlog_dse_2606:1444458 |
| revert:delete:dse:rclog:146247 | dse~OpenAIResearchPoliceDataBridge194814 | 2026-06-19T23:55:26Z | rclog:146248; reqlog_dse_2606:1449939 |
| revert:delete:dse:rclog:146986 | dse~--help | 2026-06-21T06:43:21Z | rclog:147412; reqlog_dse_2606:1611310 |
| revert:delete:dse:rclog:146029 | dse~OAITestFoo | 2026-06-21T17:26:56Z | rclog:147893; reqlog_dse_2606:1670146 |

These four raw rows were inspected locally in adjudication. Only PoliceBridge is a mutually published manual history; inspection of the other three action records is not a fabricated independent reconstruction. E06 must test all four action classifications plus a synthetic old-body → BU invalidation case.

## 2. State representation and API semantics

Expected conceptual API:

`state_at(page_key, t, *, mode="nominal") -> StateQuery`

Names of implementation dataclasses may vary; semantics may not. `t` is timezone-aware UTC, integer microsecond precision. `page_key` is an opaque exact identifier, never a filesystem path. E05 tuple order is not chronology.

`StateQuery` contains:

- `mode`: nominal or uncertainty; explicit conditional-model identifier.
- Nonempty `alternatives`: each a state plus compatible trajectory/constraint reference. Each state is exactly `unknown`, `live(body_ref)`, `live(body_unknown)`, or `deleted`. A singleton is deterministic **in that mode**. Ambiguity is a wrapper/set, not a fifth physical state. Preserve distinct provenance even when state values coincide.
- Evaluator-only support IDs/source locations, timing constraints/ambiguity reasons, episode/censoring information per alternative. Stable ordering of these output records may use IDs but cannot discard alternatives.
- No hash/ref on unknown, BU or deleted. A live body_ref resolves exactly to E05's immutable rev_id, source SHA-256, source bytes/encoding and body string. Different revisions with equal hashes remain different captures/provenance; no semantic merge in E06.

### Nominal before/at/after

1. Horizon: t0=`2026-05-24T00:00:00Z`, T=`2026-07-15T00:00:00Z`. Queries t<t0 or t>T raise an explicit out-of-horizon error; do not extrapolate. An unrecognized key within horizon returns unknown, not proof of absence or an existence oracle.
2. At t0 all titles unknown; before first supported mutation unknown. Events ≤t apply, in selected-time order except ties. For an isolated mutation at b, query b−1 microsecond yields predecessor; b and b+1 microsecond yield installed state if no intervening boundary. Intervals are [start,end).
3. At tied nominal b, apply the **whole group** before reads; admit every source-permitted ordering. Reads cannot observe a handpicked mid-group body. A save/save tie with different bodies gives possible last bodies, not their union; save/delete gives possible live/deleted. Compatible identical effects may yield one state while retaining multiple provenance paths.
4. A later full replacement/delete can converge state alternatives. Preserve any still-different episode provenance; convergence of body does not prove earlier chronology.
5. At T return the carried state with observation-end marker. Ongoing live/BU episode is right-censored; a deleted episode ended at its deletion, but post-deletion observation is still limited to T. Deleted is not globally absorbing. Earlier unknown prehistory is left-censored; first supported live appearance is not first-ever creation. Initial delete closes unobserved prehistory without inventing a supported live start.
6. A later supported live mutation after deleted starts a new modeled episode; ordinary edits, copy metadata and archival markers never do. Episode IDs must be prefix-stable opaque IDs based on supported starts, not final round counts. If order changes episode boundaries, return alternatives, not a forced single episode ID.

### Uncertainty / partial orders

`mode="uncertainty"` uses a separately labeled project convention: each mutation boundary may lie anywhere in the **closed** interval [selected time−u, selected time+u]. For saves obtain u from linked revision; native events use their own u. Null/unsupported uncertainty must be explicit review-required, never silently u=0. The pinned DSE audited mutations use u=1. Do not describe these intervals as calibrated confidence bounds or independently measured clock error.

Admissible trajectories choose one boundary time per event within its window and an order for co-timed events, respecting any genuinely supported precedence. **No extra precedence is certified by this contract** from seq, diff-base, RCS, archival time, request-match candidate or row order. Nonoverlapping windows force chronological order; touching endpoints allow co-timing and either internal order. Event-before-read applies within each realization. Thus:

- For an isolated transition with lower endpoint l and upper endpoint h, before l only predecessor; at l through times <h either predecessor or successor; at h the transition has occurred in every realization (unless another admissible mutation changes its effect).
- Overlapping/touching groups may leave multiple possible terminal states even after every member's latest boundary; keep these until a subsequent supported overwrite/delete converges them.
- Alternatives must be **globally consistent across queries**. Retain a constraint graph/trajectory handle sufficient for later evaluator consistency. A query-wise union without temporal constraints is not adequate for full bounds or evidence scoring.
- An implementation resource limit may return an explicit incomplete/unsupported-ambiguity error; it may not prune silently, select an ID winner or claim complete bounds. Initial E06 may support nominal mode plus explicit review-required uncertainty, but E06 cannot be called complete until the released uncertainty tests and independent comparisons pass.

Primary nominal prefix invariance: appending future mutations with selected time>t cannot alter `state_at(...,t)` except same-time-group completion if t was previously an incomplete group. Treat input groups atomically; do not claim an incomplete group is final. Uncertainty-mode evaluator queries may change if an appended event's uncertainty window reaches t; expose that reason. This retrospective evaluator sensitivity must not be delivered as a live-observer oracle. Future events whose earliest admissible boundary is >t cannot change earlier state.

## 3. Exclusions and no-leakage boundary

E06 is a private state oracle, **not** a policy-visible historical directory. It may index all validated mutations internally. The future observer must expose only time-eligible sanitized events and current response content per realization; it must never hand policies `StateQuery` alternatives, source store handles or full E05 objects.

Explicitly prohibited as live observations/features:

1. Final page/title lists, aggregate first/last-write/counts, final-state descriptors (`deleted_live`, head/live/txt/dw).
2. Future revision bodies/IDs/clocks or the overwritten/deleted body attached to an earlier trigger; archived_at as a visibility or archive-availability clock.
3. Retrospective recreation/copy links, fallback associations or round metadata as real-time observations or earlier body availability.
4. Evidence annotations, criticality, support alternatives, sampling/split membership, exclusion labels or reviewer judgments.
5. Future copies, future page-family/group membership, label/IP aggregates or identities inferred from them.

Retrospective exact-scoring exclusions live in evaluator metadata, not in historical state selection. AI/head-mismatch traces still have model queries/load, marked historical interpretation unresolved privately; never use the flag to alter earlier responses. Unknown/BU is not an empty success, deleted is not archival erasure, and excluded title is not absent. Bodies cannot be executed, their embedded URLs fetched, or their path-like identifiers used as local paths.

## 4. Frozen fixture release contract

Research owner supplies a **filtered fixture bundle**: only Jaswin packets 01,02,03,05,06,07 boundary tables plus their matching source-appendix entries, with the adjudication overrides here. Exact IDs/timestamps/full hashes are pinned by the unchanged first-pass hash recorded in `V02_ADJUDICATION.md`; do not give Ubayd the entire research document to obtain those excerpts. Raw inputs may be transcribed from the pinned export; expected outputs must be transcribed from the manual tables, not produced by the engine. Review transcription against raw records before acceptance.

All 76 mutation rows in these six packets require predecessor/at/after tests, plus initial unknown, horizon censoring and listed archival no-ops. Sam's compressed ranges are not claimed as a second row-by-row hash oracle. Required named tests:

| Released manual fixture | Minimum anchor expectations in addition to every manual boundary |
|---|---|
| 01 DataUSAConstructionWageSep18Live | First save 2026-06-19 12:40:34 installs @1; all @2–@30 replace; @29 archive at 14:19:47 does not end @29; @30 archive 15:46:25 does not delete; deletion 145609 at 15:46:37 installs deleted. |
| 02 ZZZDataUSAConstructionWageLive | First save 2026-06-19 14:06:38 installs its own @1; all @2–@10 replace; @9 archive 14:41:48 is no-op; deletion 145611 at 15:46:49 deletes this title independently. No cross-title state transfer. |
| 03 AgentLinkma21JuneAA | @15 at 2026-06-18 18:26:11, deletion 138648 at 18:26:23, @16 at 18:29:39 in new episode. @19 archive at 19:50:33 must leave @20 already installed at 19:50:30. Final deletion 151031, 2026-06-24 12:59:34. |
| 05 TestFoobaAgent | Unknown before deletion 131972 at 2026-06-04 10:53:40; deleted until supported @1 at June 8 04:03:23, not creation at t0. @2–@5 ordinary edits; final deletion 151010 June 24 12:35:19, not request at :18. |
| 06 OpenAIDataUSAPoliceBridge20260129 | June 19 unknown → deleted at 23:00:37 → BU at 23:19:13 → deleted at 23:40:56. No prior/new body hash or text. |
| 07 AgentOfficialDirectQueryAA3 | @1 May 28 01:16:54; deletion 150767 June 24 10:43:36. Archive :34 no-op, request null not failure. In ±1 sensitivity isolated deletion at :35 admits live/deleted; at :37 deleted. |

Also required public diagnostic tests (not yet jointly validated manual packets):

- 09 `AI`: unknown → supported @2; archive no-op; no inference of missing @1, moderator overwrite or final historical body. Independent review pending.
- 10a `AgentNacoPovertyTexas2015XQ`: @22/@23 at 2026-06-22 08:39:06 are different bodies. Nominal before group @21, at/after group {@22,@23}, convergence at @24 (08:39:31). Equal @5/@9 body hashes do not erase distinct mutations. Independent review pending.
- 10b `AgentBridgeOct2142X`: @1 June 16 18:40:04; archive 18:43:13 no-op, carry conditionally to T with right-censoring. Independent review pending.
- Synthetic adversarial tests: isolated save/delete/BU, delete→save with and without relation metadata, repeated deletes, save/save and save/delete ties, identical-body ties, touching windows, later convergence, suffix invariance, unsupported action/uncertainty fail-closed, opaque keys, out-of-horizon, no metadata-triggered mutation. Synthetic expected states are hand-authored, not a replacement for independent manual cases.

**Held back:** 04 `AgentProxyCountyNext987111` and 08 `OAIEquityDec30Raw` / `OECDJun26PrecisionScout`. Do not inspect their research-only detailed expectations, transcribe them into development tests, or infer Sam's missing answers. Generic uncertainty rules are public; full blind packet outcomes remain with Sam. At interface freeze, Sam submits/compares the original independent answers and runs blind/differential tests without changing expectations to match software. Record any prior access contamination; no secrecy guarantee is claimed merely because a filename says blind.

## 5. Completion gate and forbidden scope expansion

Restricted implementation may begin now. E06 **completion** requires:

1. All released before/at/after/hash/unknown/censoring tests pass, including no-op provenance markers and four bodyless action classifications.
2. Independent supplements for packets 09/10 and controlled adjudication of 04/08 supply the presently missing comparisons. All expected alternate states/trajectories pass, or disagreements are explicitly excluded/bounded with research-owner approval. No engine-led manual-answer revision.
3. No future-field leakage or arbitrary ordering; uncertainty/suffix tests pass and limitations are explicit. Independent V07 review follows before observer/collector work.
4. A03 is not needed to write the restricted state engine, but is needed to complete R04's semantic/sample freeze. E08 additionally waits for its exact response/storage-accounting contract; E09/E10 remain stopped.

**Five nonnegotiable rules:** no future information; no invented/carried body through a bodyless mutation; no ID-derived historical ordering; no archive/final/relation-derived state transition; no historical-loss/full-gate claim from a conditional model or incomplete independent fixtures.
