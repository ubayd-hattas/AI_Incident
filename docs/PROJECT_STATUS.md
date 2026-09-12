# Project Status & Decision Log — Evidence Before Erasure

Living document. Latest checkpoint: **final hostile pre-results audit — CONDITIONAL GO E12; X13 NOT AUTHORIZED**, now reconciled with the merged E09/E10 independent cross-policy audit. See `docs/PRE_RESULTS_AUDIT.md`, the frozen `docs/X13_RUN_CONTRACT.md`, and `audit/E10_CROSS_POLICY_AUDIT.md`. No evidence coverage or policy-versus-label evaluation has been run. Earlier dated entries are historical, not current authorization. Deadline recorded in the original plan: **2026-09-13, 23:59 AoE**.

How to use this file: section 1 and `PRE_RESULTS_AUDIT.md` §11 define current gates; section 3 tracks implementation. Sections labeled historical do not override those gates.

---

## 1. One-line status

**Track 2, "Evidence Before Erasure." E01/E05 PASS; V02/E06/V07 state-model acceptance is retained with its documented limits. E08 observer/storage is implemented and neutrality-audited, while the final pre-results audit identifies fixes and gates that must be closed before semantic results. E09 periodic P/PD/PCD and E10 bounded `E(q)` are implemented; Sam's newly merged independent cross-policy audit records PASS for the audited collector code, including sensor/accounting parity, PCD fairness, and independently re-derived token-bucket behavior. That audit does not supersede the later pre-results gates. Accounting arithmetic reproduces 9/9, but all 11 hashes in the prior accounting acceptance record disagree with the current files and require reconciliation/reacceptance. A03 pilot signoff is recorded, not an A11 benchmark/sample/schema freeze. E12 remains CONDITIONAL GO only; X13 is NOT AUTHORIZED. Neither has been run, no semantic evidence-coverage result exists, and the primary hypothesis is unknown.**

### Current pre-results authorization gate

- **Verdict: CONDITIONAL GO E12.** Outcome-blind substrate repairs and synthetic tests may proceed; semantic evaluator implementation waits for A01–A05 closure and A11/schema acceptance in `PRE_RESULTS_AUDIT.md` §11.
- Before E12: close audit issues A01–A05. The E09/E10 audit artifacts have now arrived; A01 closure requires recording their audited code hash/scope and reconciling their collector-level PASS with the later pre-results findings and any fixes. Also reconcile/reaccept accounting pins; freeze A11 sample/groups/splits/criticality/fragments/context/encoding/eligibility; and enforce retained-only snapshot and population boundaries.
- Before X13: fix earlier-checkpoint response accounting and causal observer guards; implement/validate F and required repair/order/archive/chronology controls; accept E12 on hand-scored synthetic cases; instrument full costs and clean-environment reproduction. **Separate GO X13 required.**
- Frozen primary: **PCD15 versus E30**, 1 MiB capture/body store plus shared feed metadata, July15 endpoint, lag5s/poll60s/GET0s, 60-phase mean, held-out critical core evidence, unchanged **10pp** threshold. E requests must not exceed **any** comparator phase for the phase-average headline. No q substitution if E30 is unmatched.
- Exact matrix, statistics, archive ledger, all-configuration/unfavorable-result outputs and fixed walkthrough: `X13_RUN_CONTRACT.md`. Numerical settings frozen; named annotation membership still needs A11 acceptance.
- Demonstrated synthetic defects: post-checkpoint response counted completed/downloaded; observer permits a backward GET after future discovery; rejected full bodies remain in out-of-cap result history. No current E-only richer sensor access found. Nulls, PCD wins and archive collapse are not blockers.

### Earlier E08 authorization gate (historical)

- Frozen definitions: metadata JSON serialization, feed/directory/response/packet schemas, canonical body bytes, dedup/FIFO and charged/excluded components.
- Fixtures: `tests/fixtures/accounting/README.md` plus A_feed, B_unique, C_duplicate, D_nondedup, E_fifo, F_oversize, G_shared_fifo, H_protocol and I_encoding JSON files.
- Author-side local checks: 9/9 PASS (not independent signoff on their own).
- **Independent acceptance was recorded at that checkpoint.** `audit/R04_ACCOUNTING_VERIFICATION.md` states that Sam rebuilt the canonical serializer, packet/feed/header schemas, and FIFO/dedup/byte-hours logic from the contract text alone and obtained 9/9 matches. The final pre-results audit later found that every pinned hash in that record differs from the current corresponding file, so the acceptance's applicability to current bytes is unresolved until traced and reaccepted.
- **E08 implementation was authorized and completed on that historical basis.** This does not waive the current accounting-custody reconciliation or the separate pre-results fixes before E12/X13. Aaron's optional second confirmation was not recorded as completed.

---

## 2. Decisions that have changed (don't assume the old answer still holds)

| # | Decision | Was | Now | Why it changed |
|---|---|---|---|---|
| 1 | Project | Candidate among 8–12 generated by the selection memo | **Evidence Before Erasure**, Track 2 | Scored highest (~82/100) on the selection rubric; least prior-art collision |
| 2 | Falsifiable hypothesis | Numeric threshold drifted to a descriptive estimand in the execution spec | **Resolved before outcomes:** PCD15 phase-average vs E30, held-out critical core, primary cap/interface/T, ≥10pp; all-phase request admissibility; no q promotion | `PRE_RESULTS_AUDIT.md` / `X13_RUN_CONTRACT.md` restore the unchanged practical threshold within a conditional simulation claim, not historical-loss inference. |
| 3 | Repo layout | Duplicate docs existed in both `docs/` and `Downloads/Hackathon4/` | Cleaned up in commit `1fffb7a` — `Downloads/Hackathon4/` gone, everything under `docs/`/`sources/`/`src/` | Ubayd's cleanup alongside E01 |
| 4 | "Does implementation exist?" | As of the first audit pass (before `1fffb7a`): no, repo was docs-only despite being described as having "V3... scoring, validation, pipelines" | As of `1fffb7a`: yes, real — `src/ebe/ingest.py`, independently re-run and byte-identical on a clean download | Ubayd shipped E01 |
| 5 | Novelty status | "Provisional, not certified absent" (searches blocked, no confirmed maintainer contact) | **Certified Novel** for Track 2 scope | Aaron & Jaswin completed formal prior-art audit (`sources/search_log.md`), differentiating EBE's collection policy benchmark from Boyd Kane's forensic tracing talk, collusion.wiki disclosures, and arXiv agent taxonomy literature. |
| 6 | Headline "14m22s propagation" example | Cited at face value in `DATA_AUDIT`/`EXECUTION_SPEC` as the propagation gap between `OAIEquityDec30Raw@5`→`OECDJun26PrecisionScout@14` | Jaswin's V02 pass read the full bodies and found the actual method/replication content appears earlier (`@4`, `@12`/`@13`); the true interval is 17–20 minutes, anchored on different revisions | Closer content reading during independent reconstruction — recorded as departure #7 in `docs/R04_FROZEN_SPEC.md` |
| 7 | Item 9/10 fixture picks | Sam proposed `StartSeite`/`OAIResearchBridgeMay3X` (chosen because they looked like strong examples) | Superseded by Jaswin's pre-declared deterministic rule: `AI`, `AgentNacoPovertyTexas2015XQ`, `AgentBridgeOct2142X` | Outcome-blind selection rules beat "pick the most interesting-looking case" — both independent adjudications agree on this |
| 8 | "Does E01 gate the rest?" | E05/E06 explicitly said to depend on V02 sign-off | E05 shipped anyway; R04 is now an explicit **partial** freeze ("CONDITIONAL GO E06 only... R04 PARTIALLY BLOCKED ON A03") rather than a full freeze | Team chose to proceed on the 6/10 titles with full agreement rather than wait for all 10 |

---

## 3. Are we getting there? — ticket tracker

Ticket IDs match `EXECUTION_SPEC_v0.1.md` §7. This is the real gauge — check this section, not your memory of the plan.

| Ticket | Owner | What it is | Status | Evidence |
|---|---|---|---|---|
| R00 | Jaswin + Aaron | Pin sources, rights, novelty search, maintainer email | ✅ **Done** | Hashes/sources independently verified by Aaron (`audit/reconstruction_checks.csv`). Novelty search log completed and certified (`sources/search_log.md`). Data rights resolved to clean-room download recipe (`sources/registry.json`). Maintainer questions prepared (`sources/maintainer_questions.md`). |
| E01 | Ubayd | Raw export inventory, no timeline assumptions | ✅ **Done** | `sources/{registry.json,SHA256SUMS,E01_ANOMALIES.md,schema_inventory.json}`, `src/ebe/ingest.py`. Independently re-run on a separately-downloaded copy of the export — byte-identical. |
| V02 | Sam + Jaswin | Manual state reconstruction/adjudication | ✅ **State-model comparisons accepted through V07, including a fresh blind re-derivation** | `audit/V07_BLIND_VALIDATION.md` reports revealed packets 04/08 matched. A second, structurally independent blind reconstruction (a freshly-spawned agent with zero access to any prior document, given only the raw export + `E06_IMPLEMENTATION_CONTRACT.md`) was obtained afterward — `audit/V07_SECOND_BLIND_RECONSTRUCTION.md` — and matched every boundary exactly, including independently re-finding the `OECDJun26PrecisionScout` touching-uncertainty-window case. |
| A03 | Alex + Aaron | Rubric pilot: atomic propositions, spans/hashes, support bundles, second review | ✅ **Pilot signoff recorded** | Ten-proposition pilot and Aaron/Jaswin review fields/adjudication are present. Reported primary span/hash checks do not certify whole-DSE context occurrences or A11; pre-results audit identified checker/schema and epistemic-prose issues to resolve before E12. |
| R04 | Jaswin, Sam review | Freeze experiment contract and accounting | 🟡 **Design/run supplement frozen; custody and A11 gates open** | `docs/X13_RUN_CONTRACT.md` fixes primary, admissibility, matrix, statistics and outputs. Prior accounting acceptance exists and arithmetic passes9/9, but all11 pinned hashes mismatch local files: renewed acceptance required. Pilot signoff is not the named A11 freeze. |
| E05 | Ubayd | Typed validated loader | ✅ **Done** | `src/ebe/schema.py` + extended `ingest.py`, `docs/E05_TYPED_LOADER.md`, `tests/test_ingest.py`. Correctly types `revert` as body-unknown, never restoration. One gap from the E01 review still open: manifest `never_add_to`/`population_id` constraints are loaded as an opaque field, not enforced anywhere. |
| E06 | Ubayd | Timeline/state-at-time engine | ✅ **Implemented; state dependency sufficient for next ticket** | `src/ebe/timeline.py`, `docs/E06_TIMELINE_ENGINE.md`; V07 records no found state divergences with disclosed limitations. |
| V07 | Sam | Independent state reference/checks | ✅ **FULL PASS** (revised from CONDITIONAL) | `audit/V07_BLIND_VALIDATION.md` §6, `audit/independent_replay.py`, `audit/reconstruction_checks.csv`, `audit/V07_SECOND_BLIND_RECONSTRUCTION.md`. The two gaps that held this at CONDITIONAL are both closed: the `data/data/raw/export` path bug is fixed (`b1c822e`), and a second, zero-prior-exposure blind reconstruction now confirms every boundary. Does not verify accounting bytes — that's the separate, still-open E08 accounting-fixture acceptance below. |
| E08 | Ubayd | Shared observer/storage | 🟡 **Implemented/neutrality-audited; pre-result fixes required** | `src/ebe/{accounting,observer,storage}.py`, tests and `docs/E08_OBSERVER_STORAGE.md` exist. Shared schemas/FIFO tests pass, but the later pre-results audit found earlier-checkpoint response accounting, causal API guard and retained-only evaluation-boundary gaps. See PRE_RESULTS audit A04/X01/X02. Implementation completion does not close those gates. |
| E09–E10 | Ubayd | Periodic/event-derived collectors | 🟡 **Implemented; independently cross-policy audited PASS; pre-result gates remain** | `src/ebe/collectors.py` implements P/PD/PCD and bounded `E(q)`. `audit/E10_CROSS_POLICY_AUDIT.md` and `audit/verify_collectors_cross_policy.py` record Sam's independent PASS: sensor/access and accounting parity, q=30/100/300 token-bucket re-derivation, nine adversarial scenarios, and no collector-code bug found. A01 still requires hash/scope reconciliation with current bytes and later fixes. F remains unimplemented and required before X13. No semantic results. |
| A11 | Alex/Aaron/Jaswin | Freeze benchmark evidence, blind to policy outputs | 🟡 **Independent annotation work proceeding; local final freeze absent** | A03 signed pilot exists. Need named sample/group graph/splits, full core/context occurrences, eligibility/encoding contracts and accepted hashes; gaps in PRE_RESULTS audit §8. A03 completion alone does not constitute A11 acceptance. |
| E12 | Ubayd, Sam review | Evidence-coverage/delay evaluator | ⬜ **Not implemented/run; CONDITIONAL GO only** | Semantic implementation waits for audit A01–A05 closure and A11/schema acceptance. Substrate fixes/synthetic preparation are permitted; no real policy scoring. E08/E09/E10 completion does not automatically authorize E12. |
| X13 | Ubayd + Sam | Pinned sweep, clean-environment reproduction | ⬜ **Not run; NOT AUTHORIZED** | Run contract frozen; implementation fixes, independent acceptance, mandatory sensitivities and reproduction gates remain open. |
| P14 | Jaswin + Alex | Judge-facing artifact (figure + one history panel + README) | ⬜ Not started |

**Plain read:** E08/E09/E10 implementation exists and the merged E09/E10 cross-policy audit records a collector-level PASS. No semantic outcome exists. The final pre-results audit remains authoritative: A01–A05 and A11/schema acceptance must close before semantic evaluation, and a separate authorization is required before X13. All null, reversal and unmatched outcomes remain publishable.

---

## 4. Earlier verification summary (historical)

Preserved from earlier checkpoints. In particular, timing arithmetic is not first semantic propagation, archival-clock correlation is not visibility, and prior novelty prose is not a methodological gate closure. Current audit findings are in section 1 and `PRE_RESULTS_AUDIT.md`.

| Claim | Verified how | Status |
|---|---|---|
| Export hashes/row counts match what `DATA_AUDIT` recorded | Re-downloaded independently, re-hashed, re-ran `ingest.py` | ✅ Confirmed, twice, from two separate downloads |
| E01's specific edge-case numbers (5,217 deletions, 1,246 deletion-only titles, 67 rows/68 edges, 4 bodyless `revert`s) | Recomputed from raw JSONL independently of `ingest.py` | ✅ Confirmed |
| DATA_AUDIT's quoted timing examples (96s notice→backup, 12s original→backup deletion, 14m22s cross-page propagation) | Recomputed from raw timestamps, not copied | ✅ Confirmed, exact to the second, on 3 separate examples |
| `archived_at` reliably reflects "next mutation time" | Tested programmatically across 50 consecutive pairs | 🟡 Mostly (48/50 within ±1s), but **two real multi-minute exceptions found** — flagged as a live risk, not yet resolved |
| Novelty (no one else has done this exact experiment) | Search engines blocked/unreliable per `DATA_AUDIT`; no confirmed maintainer reply | 🔴 Still unverified |
| Four-hour gate passed | EXECUTION_SPEC's own criteria (10 cases reconstructed & agreed, no future-info leakage, etc.) | 🟡 Substantially satisfied by informal work, **but never formally declared passed by the team** |

---

## 5. Earlier open-decision register (historical)

This list predates V07 and the accounting amendment; it is preserved as historical context, not current authorization. V07 discloses and accepts state-model checks despite prior exposure; A03 pilot signoff is now recorded. The **current** gate register is `PRE_RESULTS_AUDIT.md` §11 and section1 above, including audit/hash custody, A11 and retained-evidence boundaries. The hypothesis decision below is resolved by the pre-results run contract; source/annotation/release limitations remain separate.

1. **The blind-fixture plan is compromised.** Packets 04 (`AgentProxyCountyNext987111`) and 08 (`OAIEquityDec30Raw`/`OECDJun26PrecisionScout`) were meant to be withheld from Ubayd, but their full expected states are published in plain text in `audit/JASWIN_V02_RECONSTRUCTION.md`, which is committed to the same repo Ubayd works in. `docs/E06_IMPLEMENTATION_CONTRACT.md` already flags this ("If Ubayd has already read the blind answers, report contamination"). **Someone needs to actually check whether Ubayd has opened that file, and either accept the loss or select fresh holdback fixtures from titles neither reconstruction has published.**
2. **Sam's independent reconstruction of packets 09/10 is now contaminated.** Full validation of `AI`, `AgentNacoPovertyTexas2015XQ`, and `AgentBridgeOct2142X` still needs a genuinely blind second reconstruction, but reviewing Jaswin's document for adjudication purposes means Sam has now read the expected answers for those three specific titles. A truly independent recheck of just those three would need a different person, or an explicit acknowledgment that this is verification-against-a-published-answer rather than blind reconstruction.
3. **A03 real pilot still doesn't exist.** Alex's `evidence_timeline/` is good, fact-checked prose, but it isn't the atomic-proposition/span/hash/support-bundle/second-review pilot A03 requires. This is the actual thing blocking R04's full freeze and everything downstream of E06.
4. **Maintainer email still not sent.** It's fully drafted (`sources/maintainer_questions.md`) — send it now regardless of reply odds.
5. **`never_add_to` guard** — flagged after E01, still not implemented after E05. Needs to land before E12, or it becomes a much more expensive fix later.
6. **Hypothesis framing** — still unresolved; the descriptive (non-falsifiable-threshold) framing has now been implicitly reinforced by `R04_FROZEN_SPEC.md`'s explicit ban on "historical-loss claims," which is consistent with dropping the ≥10pp threshold — but nobody has written down *that this is the final decision and why*.

---

## 6. Earlier time reality check (historical, not a current estimate)

The following planning assessment predates E06/V07 and is not used to authorize implementation.

Deadline: 2026-09-13 23:59 AoE. As of this update, roughly **one day** of runway remains, not the "48 hours" the original schedule in `EXECUTION_SPEC_v0.1.md` §16 assumed (that schedule was written assuming a start point that, based on repo evidence, didn't actually happen until partway through day one). With 1 of 14 tickets done:

- If the team wants the **ideal** submission (160 episodes, full sweep, P14 judge artifact) — not realistic on remaining time at current velocity.
- The spec's own **minimum viable submission** (§16: one wiki population, 40–60 adjudicated episodes, 3 policies, 2 intervals, one retention figure, reproducible tables, honest limits) is still reachable **only if E05 unblocks in the next few hours.**
- The spec's own kill/pivot ladder (§17) is the honest fallback if it doesn't: narrow scope, declare it a trace-grounded simulation rather than historical reconstruction, or pivot to Witness Budget. None of those conditions have been triggered yet — this is a "watch the clock," not a "pivot now," situation.

---

## 7. Change log (append here as things move)

- **Final pre-results methodological audit, baseline `9342cda`:** created `docs/PRE_RESULTS_AUDIT.md` and `docs/X13_RUN_CONTRACT.md`; verdict **CONDITIONAL GO E12**, X13 **NOT AUTHORIZED**. Frozen PCD15/E30 primary, unchanged 10pp threshold, all-phase request admissibility, full matrix/statistics/outputs and mandatory archive/repair/order/chronology sensitivities without policy outcomes. Reproduced 103 tests and 9/9 accounting arithmetic; synthetic probes demonstrated checkpoint-accounting, causal API and unretained-body exposure issues. At that local baseline the E09/E10 independent report was absent; it has now arrived through this merge and must be reconciled under A01 rather than described as missing. The audit also found 11/11 accounting acceptance hash mismatches. A03 pilot is not A11 acceptance. No collector/scorer/annotation code changed; no coverage or experiment run.
- **2026-09-12, E09/E10 audit (arrived from remote in current merge):** Ubayd shipped E09 (`fdcd5b1`) and E10 (`9342cda`). `audit/verify_collectors_cross_policy.py` and `audit/E10_CROSS_POLICY_AUDIT.md` record Sam's independent cross-policy audit: sensor-access parity over the allowed Observer surface; an independently coded token-bucket simulator matching q=30/100/300 behavior including burst drain and body-unknown charging; nine adversarial scenarios PASS; and no artificial PCD weakening found at matched schedule granularity. The audit records zero bugs in `src/ebe/collectors.py` and five corrected bugs in its own harness. This collector-level PASS is retained, but it did not implement/run semantic scoring and does not authorize E12 or X13.

- **Pre-E08 accounting recovery checkpoint:** Preserved the existing amendment and A/B work; completed nine data-only accounting fixtures and README. Author-side direct arithmetic plus local standard-library serialization/UTF-8/hash checks passed all nine. No Sam/Aaron acceptance exists, so **E08 STILL BLOCKED**. Updated stale E06/V07 status from their local documents; no source semantics/policy parameters changed, no implementation code created, no commit/push.

- **2026-09-12, early:** Selection memo produced (`Astra_Project_Selection_Analysis.md`), Evidence Before Erasure chosen.
- **2026-09-12:** `DATA_AUDIT_2026-09-12.md` + `EXECUTION_SPEC_v0.1.md` produced — data-semantics audit and frozen v0.1 spec. Falsifiable hypothesis quietly dropped in this pass.
- **2026-09-12:** First scientific audit performed (repository found to be docs-only at that point, despite being described otherwise).
- **2026-09-12:** Independent validation pass — 7 of ~10 fixture cases reconstructed directly from raw export, cross-verified several DATA_AUDIT claims, found the `archived_at` lag pattern.
- **2026-09-12, commit `1fffb7a`:** E01 shipped by Ubayd. Independently re-verified — byte-identical clean-room reproduction. Repo cleaned up (duplicate docs removed).
- **2026-09-12, commit `0de69b0`:** E05 typed loader shipped by Ubayd (`schema.py` + extended `ingest.py` + tests). `never_add_to` gap from E01 review confirmed still open.
- **2026-09-12, commit `bf58327`:** Jaswin's independent V02 reconstruction (`audit/JASWIN_V02_RECONSTRUCTION.md`) + R04 pre-freeze decisions + maintainer email drafted (not sent).
- **2026-09-12, commits `e8fa731`/`519f045`:** Alex added `evidence_timeline/` — a sourced narrative CSV. Independently spot-checked here against raw JSONL, including the most dramatic claim (heartbeat-key dead-man switch, `hb001`–`hb353`) — holds up factually, but does not satisfy A03's pilot criteria.
- **2026-09-12, commit `13bb0c5`:** Jaswin froze `R04_FROZEN_SPEC.md` (partial — CONDITIONAL GO E06 only, blocked on A03), an independent `docs/V02_ADJUDICATION.md`, and `E06_IMPLEMENTATION_CONTRACT.md`. Independently confirmed: zero disagreement between the two V02 reconstructions on any shared, non-blind title. Two process problems surfaced: blind fixtures 04/08 are exposed in-repo, and packets 09/10 now need a genuinely fresh independent reconstruction since Sam has read Jaswin's answers during adjudication.
- **2026-09-12:** Alex delivered the real A03 pilot package (`annotations/rubric.md`, `annotations/evidence.jsonl`, `annotations/occurrences.jsonl`, `annotations/A03_PILOT_HANDOFF.md`) satisfying all six criteria: 5 atomic propositions with exact Unicode spans [start, end), SHA-256 hashes, support bundles, and 102 verified occurrences across Case 01/02. Handed off to Aaron for second review.
