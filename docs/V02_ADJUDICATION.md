# V02 adjudication — local-record decision

**V02: CONDITIONAL PASS (restricted model only; full ten-packet gate not passed).**
**E06: CONDITIONAL GO. R04 PARTIALLY BLOCKED ON A03.**

This is an assistant-prepared adjudication under the user's instruction, not fabricated Jaswin/Sam signatures. No engine, collector, policy outcome, network retrieval, or annotation result was used. The seven requested files exist locally and were read. All five `data/raw/export/` expanded hashes were independently rechecked against the audit and match.

## 1. Independence, coverage, and counting

Preserve the first passes unchanged:

- `audit/JASWIN_V02_RECONSTRUCTION.md`, SHA-256 `29773cc6ada6c3e38ccc0ce21327d06d537e7b9d8d8c27050f4ffe7b52b29eee`.
- `docs/V02_INDEPENDENT_RECONSTRUCTION_2026-09-12.md`, SHA-256 `ef9fa94220504dd0b924b1adcf819379155ffc2a233d3b8467816881c7ccebbb`.

The local Sam submission calls itself *pass 1*. It publishes six nonblind cases, reports reconstruction of two blind packets without detailed expectations, and explicitly leaves legacy/tie candidates unreconstructed. It does not contain independent answers for Jaswin's AI, AgentNacoPovertyTexas2015XQ, or AgentBridgeOct2142X selections. The user's completion summary cannot substitute for missing comparison records. No later Sam supplement was found locally.

**Count: 4 documented interpretive/procedural disagreements (D01–D04), 0 fully resolved by source evidence, 2 preserved as source ambiguity, 2 settled by explicit modeling/selection conventions.** There is no published opposite nominal state assignment on a mutually described mutation. This is not a 100% boundary-agreement statistic: Sam compresses ordinary saves and withholds other answers. Missing expectations are coverage blockers, not invented disagreements. Compatible confidence qualifications and unilateral annotation observations are recorded below but not double-counted as disputes.

## 2. Disagreement ledger

### D01 — archival marker versus visibility proxy

- **Jaswin:** archival clocks never independently end live intervals or establish public archive availability.
- **Sam:** §5 characterizes them as a usually reliable proxy with lag exceptions; asks for a lag tolerance or exclusion pending clarification. His adversarial notes also warn against treating them as hard boundaries.
- **Exact records:** `dse~DataUSAConstructionWageSep18Live@29/@30` (revisions lines 5132–5133), `dse~ZZZDataUSAConstructionWageLive@9/@10` (13362–13363), their final deletions `delete:dse:rclog:145609/145611`; `dse~TestFoobaAgent@5` (10217), deletion `151010`. Additional counterexample: `dse~AgentLinkma21JuneAA@19/@20` (1660–1661).
- **Why:** correlation of storage clocks with subsequent selected saves was interpreted more strongly by Sam than by Jaswin. Sam's word “trails” is directionally wrong for the two large gaps: the archival markers precede the next saves by 1,080s and 163s. That arithmetic correction does not establish visibility semantics.
- **Outcome:** `AMBIGUOUS_BY_SOURCE` for historical meaning; no timeline transition from these markers. A lag tolerance cannot turn correlation into an availability guarantee. Native archive access remains unknown.
- **Fact/model:** recorded clocks and arithmetic are facts; carry-forward past them is the released-trace assumption, not observed HTTP continuity.
- **Scoring:** potentially material if archive time ended bodies or enabled recovery. Primary excludes those uses; archive sensitivity is explicitly hypothetical. Counted as preserved ambiguity, not an evidence-resolved historical question.

### D02 — “terminal/absorbing” versus horizon-censored trace

- **Jaswin:** deleted carries forward only under no-unobserved-mutation closure, through T; history beyond coverage unknown.
- **Sam:** construction, backup and TestFooba are terminal/absorbing within export coverage, while acknowledging restoration outside coverage cannot be ruled out.
- **Exact records:** final deletions `delete:dse:rclog:145609`, `145611`, `151010` (events lines 12231, 12232, 15852); held-page descriptors for these titles cannot resolve future state.
- **Why:** “terminal” was used for the end of a finite ledger rather than a universal absorbing state.
- **Outcome:** `AGREE_AFTER_ADJUDICATION`; deletion closes a modeled live episode but is not absorbing. Any later supported save/edit can reopen it. T is observation censoring, not a mutation; queries beyond T are out of scope.
- **Fact/model:** native deletion success is observed; continuity to T and censoring are conventions.
- **Scoring:** no difference for these nominal prefixes once scope is explicit; an absorbing implementation would wrongly suppress later recreation in other histories. Resolved by convention, not proof of future absence.

### D03 — meaning of ±1 second

- **Jaswin:** publisher `uncertainty_seconds=1` has undocumented interval semantics; symmetric closed windows are a conservative project sensitivity.
- **Sam:** tables write “±1s” without consistently separating publisher semantics from a convention; lower confidence on the rclog-only deletion.
- **Exact records:** all selected revision uncertainty fields; representative `dse~DataUSAConstructionWageSep18Live@1`; `delete:dse:rclog:150767` (events 15726), native rclog 150767 and June request lines 1850959/1850960. Tie/endpoint diagnostics are identified in §3, not claimed jointly reconstructed.
- **Why:** timing-resolution metadata was used as interval shorthand.
- **Outcome:** `AMBIGUOUS_BY_SOURCE` for publisher meaning; nominal selected time plus a separately labeled closed ±u sensitivity. The rclog-only row still has successful deletion at 10:43:36; null request association is not evidence of failed deletion. Do not select either request.
- **Fact/model:** clocks, success and unresolved request match are facts; symmetric endpoints, independent boundary movement and event-before-read are modeling choices.
- **Scoring:** near-boundary captures/order can differ. Preserve admissible trajectories and use common exclusions/bounds, never a policy-specific denominator. Counted as preserved ambiguity.

### D04 — legacy/tie/control packet selection and comparison coverage

- **Jaswin:** deterministic AI legacy/head-mismatch, AgentNacoPovertyTexas2015XQ tie, AgentBridgeOct2142X control.
- **Sam:** recommends StartSeite for legacy plus ties, alternatively OAIResearchBridgeMay3X; explicitly not reconstructed. No stable-control answer published.
- **Exact records:** `dse~AI` pages line 17 and `dse~AI@2` revision 42; `dse~AgentNacoPovertyTexas2015XQ@22/@23` revisions 2210–2211; `dse~AgentBridgeOct2142X@1` revision 301. Sam's alternative is exact page key `dse~StartSeite` (456 held revisions, 216 earlier), and `dse~OAIResearchBridgeMay3X`.
- **Why:** different inventory-selection procedures and incomplete comparison coverage, not conflicting reconstructed bodies.
- **Outcome:** selection `AGREE_AFTER_ADJUDICATION` by retaining Jaswin's preregistered deterministic packets 09/10, not opportunistically substituting cases. **BLOCKER for full V02 signoff** until independent raw expectations are supplied. This selection decision is not Sam's endorsement.
- **Fact/model:** page inventory is observed; fixture selection is a procedural convention. No moderator overwrite is inferred for AI.
- **Scoring:** these are validation packets, not a frozen evidence sample. AI is excluded from exact body scoring; tie intervals bounded/excluded. No result can depend on unresolved independent acceptance.

## 3. Case-by-case boundary disposition

Packet numbering follows Jaswin, not Sam's section order. `@a–@b` denotes **every** integer revision in that range with exact prefix `dse~TITLE`; each mutation ID is `save:dse~TITLE@n`. Exact UTC times, full hashes, before/after states and one-based raw lines in Jaswin's boundary tables and source appendix are incorporated by reference for **released packets only**. They are manual expectations, not generated engine output. An ordinary save replaces the entire body; deletion uses its selected successful clock. All initial states are unknown. Boundary classification below applies individually to every row in the specified range, including the carried pre-state under the convention. Compressed Sam ranges support rule-level comparison, not an independent per-hash transcription claim.

| Packet / title | Jaswin versus local Sam | Every meaningful boundary classification / fixture disposition |
|---|---|---|
| 01 DataUSAConstructionWageSep18Live | Both: @1–@30 full replacements, then deletion 145609; no later held mutation. Sam groups @2–@30. | Saves and deletion: `AGREE` nominally; final carry: `AGREE_AFTER_ADJUDICATION` D02. Archive markers, particularly @29/@30: historical effect `AMBIGUOUS_BY_SOURCE` D01, modeled no-op. Exact deterministic released-trace fixture. |
| 02 ZZZDataUSAConstructionWageLive | Both: @1–@10 on a separate title, then deletion 145611. Both verify 96s notice-to-save and 12s deletion-to-deletion. | All saves/deletion: `AGREE`; terminal carry D02. Archive markers @9/@10: `AMBIGUOUS_BY_SOURCE`, modeled no-op. Exact deterministic fixture. Sam's “unrelated” means no structural recreation edge, not absence of textual backup context. Copy-equivalence remains A03 work. |
| 03 AgentLinkma21JuneAA | Both: @1–@15; deletion 138648; @16–@20; deletion 151031. Sam gives episode/endpoints, not each intervening row/hash. | Listed episode endpoints: `AGREE`; ordinary-save replacement rule: `AGREE` at Sam's compressed level. Exact manual row expectations adopted from Jaswin, explicitly not a second full hash ledger. @15 archive and @19 archive after @20: `AMBIGUOUS_BY_SOURCE` as visibility clues, no-op in model. Exact deterministic fixture; 12s is state duration, not unique-evidence duration. |
| 04 AgentProxyCountyNext987111 | Jaswin detailed; Sam reports complete blind reconstruction and matching aggregate rounds/short interval only. | Published aggregate: `AGREE`. Every unreleased detailed boundary comparison: `BLOCKER` for full certification, not a source contradiction. **BLIND**: no detailed expected outputs released here; retain for V07. |
| 05 TestFoobaAgent | Both: deletion 131972 before @1, @1–@5 in one modeled episode, deletion 151010. | Each mutation: `AGREE`; no first-ever creation inference. Final carry D02; archive marker no-op with unknown historical effect. Exact deterministic fixture with unknown prehistory. Earlier deletion, not a relation-edge inference, supplies action evidence. Criticality deferred to A03; not a disagreement because neither freezes a label. |
| 06 OpenAIDataUSAPoliceBridge20260129 | Both: deletion 145962, bodyless successful edit `revert:delete:dse:rclog:145962`, deletion 146157. | All three mutations: `AGREE`. Exact deterministic fixture including BU, **EXCLUDE_FROM_EXACT_SCORING** for body propositions throughout (no held body); still discovery/cost and event context. Unknown before first deletion, not guessed prior live text. |
| 07 AgentOfficialDirectQueryAA3 | Both: @1 then deletion 150767. Sam's lower exact-second confidence is compatible with Jaswin's high confidence in successful native action but lower request-match confidence. | Both mutation types/selected times: `AGREE`. Request association and actual timing: `AMBIGUOUS_BY_SOURCE` D03. Nominal deterministic fixture plus ambiguity/bounds queries near deletion. Archive clock cannot move deletion two seconds earlier. |
| 08 OAIEquityDec30Raw / OECDJun26PrecisionScout | Jaswin detailed; Sam publishes only 862s arithmetic and withholds full claim annotation/expectations. | Published pair arithmetic: `AGREE`; all other detailed comparison boundaries: `BLOCKER` pending blind review. **BLIND** ambiguity/bounds packet. No full agreement on touching-window handling or earliest semantic support can be asserted. |
| 09 AI | Jaswin: @2 from unknown, archive no-op, untimed head mismatch; Sam has no reconstruction of this title. | Save/archival/final-descriptor comparison: `BLOCKER` for independent validation. Source interpretation of mismatch: `AMBIGUOUS_BY_SOURCE`; entire title **EXCLUDE_FROM_EXACT_SCORING** for body evidence, retain diagnostic trace queries/cost. No invented overwrite. |
| 10a AgentNacoPovertyTexas2015XQ | Jaswin: @1–@35 and deletion 151929; @22/@23 tied, no source-resolved order. Sam warns against ID ordering corpus-wide but gives no answer on this title. | All row comparisons: `BLOCKER` for full validation. Tie: `AMBIGUOUS_BY_SOURCE`; diagnostic bounds fixture, not a jointly accepted deterministic one. Non-tied manual rows may be development diagnostics only until independent review. |
| 10b AgentBridgeOct2142X | Jaswin: @1 from unknown, archive no-op, live to T only conditionally. No Sam answer. | Both markers and censoring comparison: `BLOCKER` for full validation. Unilateral deterministic diagnostic/control; not an independently validated stable historical page. |

No archival marker, diff-base, relation, final descriptor, or horizon endpoint is a new mutation in any packet. Every physical save remains one mutation even with multiple relation edges. For every unambiguous mutation the predecessor is its preceding modeled state, at/after is the installed state until another supported mutation. Every before/at/after query in the uncertainty mode additionally inherits D03 rather than claiming exact history.

### Blind custody and diagnostics

Keep packets **04 and 08** out of Ubayd's development fixture inputs and expected-output bundle until interface freeze. This document deliberately does not reproduce their detailed answers. Sam must provide his already-held expectations to the adjudicator before differential testing, not derive them from E06. The repository already contains Jaswin's detailed answers in the research-only first pass: repository presence is **not technical secrecy**. Supply Ubayd a filtered workspace/brief containing only released fixtures and this contract; record access. If Ubayd has already read the blind answers, report contamination and require new independently prepared blind tests before claiming blindness. Do not rewrite or delete either independent submission to hide that risk.

The generic partial-order requirements are public; packet 08's specific expected trajectory stays withheld. Packet 10a may be a public *unilateral diagnostic*: nominally immediately before its tied group the state is @21; after both tied saves possible states are {@22,@23}, never a merged body; @24 converges the branches. This is frozen as the conservative contract, not retrospectively attributed to Sam. Independent acceptance still required.

## 4. A03 repository inspection

No `annotations/` pilot evidence/occurrence rows, Alex first labels, Aaron second labels, or A03 adjudication artifacts were found. Inspection included all local non-Git files, `audit/`, `docs/`, `sources/`, and `evidence_timeline/`; the duplicate raw export is data, not annotation output. `docs/PROJECT_STATUS.md` also lists A03 as not started.

`evidence_timeline/evidence_timeline.csv` is a 20-row narrative chronology with four fields (date, event, source, status), not a qualifying pilot. It lacks atomic scoped proposition IDs, exact character spans/body hashes, support bundles, duplicate equivalence decisions, criticality reviews, annotator/reviewer records, and preserved adjudication alternatives. Its README's unsupported polling-loss headline is not an experimental result or an input to this decision. Neither these files nor research prose can stand in for Alex/Aaron's work. They are not rewritten here.

**A03 not demonstrated; R04 PARTIALLY BLOCKED ON A03.** All six pilot criteria remain unverified: atomicity, resolvable spans, testimony/action distinction, consistent duplicate identification, critical second review, and preserved ambiguity. No evidence denominator, critical labels, occurrence census or benchmark split is frozen.

## 5. Gate decision and exclusions

- Six published nonblind packets (01,02,03,05,06,07) support a coherent restricted four-state model and released nominal tests, including successful no-body mutation and save after deletion. They contain 76 mutation rows (66 held saves and 10 native events) and seven modeled live episodes, one body-unknown. This is sufficient for minimal engine work, **not proof of enough annotated histories for the experiment**.
- Two blind packets remain reserved, not certified as matched; packets 09/10 need independent supplementary reconstruction. Full ten-packet V02 acceptance and E06 completion wait for those comparisons.
- No source disagreement requires inventing a deterministic body. Ambiguous timing/order is representable; primary exact scoring must omit unresolved support or use a separately reported common-denominator bound. No policy runs are authorized.
- Whole-title exact-body exclusions in this manual set: **AI** (untimed head mismatch) and **PoliceBridge** (no held bodies). Unknown prehistory, all body-unknown intervals and incompatible timing intervals are excluded support occurrences, not removed from discovery/load. Other audited head-mismatch titles follow the same evaluator-only rule; the final population mask is not yet an A03-approved denominator.
- No entire history is dropped from the DSE load. Unreconstructed StartSeite/OAIResearchBridgeMay3X are unselected alternatives, not secretly substituted fixtures. The full semantic feasibility gate remains open.

**CONDITIONAL GO E06** means implement only the contract in `E06_IMPLEMENTATION_CONTRACT.md`; it does not mean V02 full PASS, R04 full freeze, A03 PASS, permission for collectors, historical loss claims, or human signoff. Missing maintainer replies do not prevent this explicitly conditional model. Missing independent fixtures prevent full validation claims until supplied.
