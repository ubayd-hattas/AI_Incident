# V02 adjudication — Sam vs. Jaswin independent reconstructions

Closes the outstanding item both `docs/R04_PRE_FREEZE_DECISIONS.md` ("Sam comparison has not occurred") and `audit/JASWIN_V02_RECONSTRUCTION.md` (adjudication agenda, item 1) call for. This document compares two independently produced reconstructions against each other and against the raw export, and states what can now be declared agreed versus what still needs a human decision.

**Independence preserved:** `docs/V02_INDEPENDENT_RECONSTRUCTION_2026-09-12.md` (Sam's pass) was written from the raw export, `DATA_AUDIT_2026-09-12.md`, and `EXECUTION_SPEC_v0.1.md` only, before `audit/JASWIN_V02_RECONSTRUCTION.md` existed in the repo and before Ubayd's E05 loader (`src/ebe/schema.py`) was read. This document is the first point at which the two are compared.

---

## 1. Per-title agreement table

| Title / packet | Agreement | Notes |
|---|---|---|
| `DataUSAConstructionWageSep18Live` | **Full agreement** | Identical state sequence, identical deletion timing (15:46:37Z), identical `archived_at` anomalies at @29 (1,080s lag) and @30 (12s lag before deletion) — independently found by both passes |
| `ZZZDataUSAConstructionWageLive` | **Full agreement** | Identical states; both independently reproduce 96s (notice→backup) and 12s (original deletion→backup deletion); both flag @9/@10 `archived_at` as non-mutations |
| `TestFoobaAgent` | **Full agreement** | Identical treatment of the pre-`@1` deletion (`131972`), identical refusal to backdate a body, same 8-day-22-hour dormancy noted as a single episode |
| `AgentLinkma21JuneAA` | **Full agreement, Jaswin's pass adds a stronger finding** | Same states/episodes, same 12s save→delete gap. Jaswin additionally found `@19`'s `archived_at` (19:50:33) is *later* than the next held save `@20` (19:50:30) — an "overshoot" case, distinct from and stronger than the lag cases found elsewhere. Both findings should be merged (see §3) |
| `AgentProxyCountyNext987111` | **Full agreement** | Same 3-deletion/2-recreation structure, same 19s recreation→second-deletion gap. **Process note:** this was one of Sam's two designated blind fixtures — see §5 |
| `OpenAIDataUSAPoliceBridge20260129` | **Full agreement, Jaswin's pass is more precise** | Same `deleted → live(body_unknown) → deleted` structure. Jaswin computed the exact BU duration (21m43s) and traced the exported revert ID to the *earlier* deletion's native log line, not the edit's — a level of source-tracing Sam's pass didn't reach |
| `AgentOfficialDirectQueryAA3` | **Full agreement** | Same single-revision-then-ambiguous-deletion structure, same `rclog`-only grade flagged as lower-confidence |
| `OAIEquityDec30Raw` / `OECDJun26PrecisionScout` | **Agreement on raw timeline; substantive correction to claim-status reading** | Both independently reproduce the arithmetic 14m22s (`@5`→`@14`) gap. Jaswin's closer content read shows this is **not** the right interval to call "propagation" — see §3, this is the most important finding in this adjudication |
| Item 9 (legacy/`n_revs_before>0`) | **Sam's candidate superseded** | Sam proposed `StartSeite` on qualitative grounds ("richest legacy history"). Jaswin used a pre-declared deterministic rule (ascending `page_key` among the 11 DSE titles with `n_revs_before>0`) and got `AI`. Jaswin's selection is more defensible — see §4 |
| Item 10 (same-second tie / stable control) | **Sam's candidates superseded** | Sam proposed `OAIResearchBridgeMay3X` (richest tie) with no pre-declared rule. Jaswin used deterministic rules and got `AgentNacoPovertyTexas2015XQ` (tie) and `AgentBridgeOct2142X` (stable control) — see §4 |

**Bottom line on agreement:** on every title reconstructed by both passes, there is **zero disagreement on any scored state, timestamp, or episode boundary**. Both passes independently derived the same states, the same two `DataUSAConstructionWageSep18Live` timing anomalies, and the same refusal-to-invent rules. This is the strongest form of validation available before any code exists: two people, blind to each other, produced identical timelines from the same raw rows.

---

## 2. What this resolves from R04's open items

From `docs/R04_PRE_FREEZE_DECISIONS.md` §3, "Joint V02 expectations and two blind software fixtures":

> Sam comparison has not occurred; no accepted boundaries/hash/order/episode output contract exists.

**That comparison has now occurred**, and the result is agreement on every directly comparable title. This does not by itself constitute the "accepted" sign-off R04 requires (that's a human decision — see §6), but it removes the technical blocker: there is nothing left to reconcile on the shared titles, only the two refinements below.

---

## 3. The one substantive correction: OAI/OECD "propagation" timing

Both passes verified the audit's arithmetic — `OAIEquityDec30Raw@5` (05:23:15Z) to `OECDJun26PrecisionScout@14` (05:37:37Z) is exactly 862 seconds (14m22s). Sam's pass stopped there and reported the arithmetic as confirmation of the audit's framing.

**Jaswin's pass went further and reads the actual body content of the surrounding revisions**, and this changes what the number means:

- `OAIEquityDec30Raw@1` already asserts a bypass exists.
- `OAIEquityDec30Raw@4` (05:17:46Z) — **not** `@5` — is where the concrete method first appears. `@5` merely retains that passage and adds a request for evidence.
- `OECDJun26PrecisionScout@12` (05:27:48Z) already contains a method relay, **before** `@13` (05:35:40Z, an Apr11 replication claim) and `@14` (05:37:37Z, the audit's cited revision, an Oct26 reproduction/HTTP-200 claim).

So the defensible candidate intervals are `@4→@13` = 17m54s and `@4→@14` = 19m51s — both larger than, and anchored on different revisions than, the audit's headline 14m22s. The audit's number is arithmetically correct but measures the gap between two arbitrarily-cited revisions, not "earliest method published → earliest replication claim."

**Disposition:** Sam's pass should adopt Jaswin's reading. This is exactly the kind of overclaiming the project's own "claim status" discipline (agent-reported vs. corroborated, EXECUTION_SPEC's claim-status categories) exists to catch — and it caught it in the team's own working documents, not just in the incident data. Recommend `DATA_AUDIT_2026-09-12.md` and `EXECUTION_SPEC_v0.1.md`'s citations of this example be corrected to reference `@4`/`@12`/`@13` rather than treating `@5`/`@14` as "the" propagation boundary, before this example is used in the report or in A03's annotation pilot.

---

## 4. Selection-rule concession: item 9/10 fixtures

Sam's V02 pass identified `StartSeite` and `OAIResearchBridgeMay3X` as candidates for the legacy-history and same-second-tie fixtures, chosen because they looked like strong examples (most pre-cut history; richest tie cluster). That is a **researcher-discretion pick made after seeing what the candidates looked like** — exactly the kind of selection R04's own hostile-review item 6 ("handpicked dramatic benchmark") warns against.

Jaswin's pass instead fixed a selection rule *before* looking at outcomes (e.g., "ascending `page_key` among DSE titles with `n_revs_before>0`") and took whatever it returned — `AI`, `AgentNacoPovertyTexas2015XQ`, `AgentBridgeOct2142X`. That is the right way to pick a fixture meant to stand for a category rather than to showcase the most interesting example.

**Disposition:** adopt Jaswin's three as the official item 9/10 fixtures. Sam's `StartSeite`/`OAIResearchBridgeMay3X` can be kept as *supplementary* exploratory examples (they're real, and `StartSeite`'s 456-revision depth is useful for a future stress test) but should not be presented as the frozen fixture-list entries for items 9/10.

---

## 5. Process finding: the blind-fixture plan is already compromised

Sam's V02 pass deliberately withheld full expected-output detail for two fixtures — `AgentProxyCountyNext987111` and the `OAIEquityDec30Raw`/`OECDJun26PrecisionScout` pair — specifically so they could later be used as blind differential tests against Ubayd's engine.

**Jaswin's independently-committed document publishes full expected states, timestamps, and hashes for both of those same fixtures**, in a file (`audit/JASWIN_V02_RECONSTRUCTION.md`) sitting in the same repository Ubayd works in. Whatever the intent, both of Sam's designated blind fixtures are now fully exposed in plain text to anyone who reads that file — including, potentially, Ubayd, before E06 exists.

**This needs a decision, not a workaround:**
- The two fixtures Sam held back no longer function as blind tests. Either designate two *different* fixtures as the actual holdback (drawn from titles neither published document covers in full), or accept that no blind differential fixture currently exists and plan to construct fresh ones once E06 nears.
- Going forward, anything intended to stay blind from an implementer needs to live outside the shared repository (or in an access-restricted location) rather than in a markdown file committed to `main` — committing it and then asking people not to read it doesn't hold up.

---

## 6. Can V02 be declared passed?

Per this adjudication: **yes, on the substance — no**, not yet, on process.

- **Substance:** every state, episode boundary, and timestamp on every title reconstructed by both Sam and Jaswin agrees. The two open items (§3, §4) are refinements that improve the spec, not contradictions that block it. No finding here contradicts EXECUTION_SPEC's four-hour-gate "Continue" criteria (`docs/EXECUTION_SPEC_v0.1.md` §6).
- **Process:** R04 §5 explicitly requires a *human* meeting to adjudicate, ratify the corrections above, and record "who had seen results" before E06 starts — this document is an input to that meeting, not a substitute for it. The blind-fixture compromise in §5 also needs a human call before E06 begins, since it affects what Sam can actually test once code exists.

**Recommendation:** treat V02 as substantively resolved for the purpose of unblocking R04's remaining freeze decisions, conditional on: (a) the team formally accepting the §3 correction and §4 fixture swap, (b) designating replacement blind fixtures per §5 before E06 starts, (c) the usual human sign-off R04 §5 requires — this document doesn't grant that on its own.

---

## 7. E05 loader — quick re-check (carried over finding)

Re-verified against the newly committed `src/ebe/schema.py` and extended `src/ebe/ingest.py`: `revert` events are correctly typed as body-unknown `form_edit` observations, never restoration — matches `docs/E05_TYPED_LOADER.md`'s own claim and the SAFE rule both reconstructions independently arrived at. One gap flagged in the earlier E01 review is **still open**: the manifest's `facts`/`never_add_to`/`population_id` structure (the explicit list of non-additive population groups) is loaded only as an opaque object field (`object_field("facts")` in `ingest.py`) — nothing in `schema.py` or `ingest.py` encodes or enforces the `never_add_to` adjacency constraints. Not a blocker for E05 itself, but worth closing before E12 (the evaluator) starts combining counts across populations.
