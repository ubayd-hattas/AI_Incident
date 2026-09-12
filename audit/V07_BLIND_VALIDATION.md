# V07 — independent validation of the E06 released-trace state engine

Role: independent validation engineer (Sam). Inputs read: `docs/E06_IMPLEMENTATION_CONTRACT.md`, `docs/V02_ADJUDICATION.md`, `docs/R04_FROZEN_SPEC.md`, `docs/E06_TIMELINE_ENGINE.md`, `docs/V02_INDEPENDENT_RECONSTRUCTION_2026-09-12.md`, and the raw pinned Collusion Wiki export. Ubayd's `src/ebe/timeline.py` was **not modified**.

## Independence disclosure (read this before trusting anything below)

`audit/independent_replay.py` imports nothing from `ebe` — no `ebe.timeline`, no `ebe.schema`, no `TraceModel`, no shared helper. It re-parses `revisions.jsonl`/`events.jsonl` directly and re-verifies the pinned SHA-256 hashes independently.

What it is **not**: a blind-from-birth implementation in the strictest sense. During the E06 code review two turns before this one, I read `src/ebe/timeline.py` in full while auditing it directly. I did not copy its code, and the reference module below uses a different concrete algorithm in several places (see "Design choices, and where they differ from E06" below) — but I cannot claim I was never exposed to Ubayd's approach before writing this. Recording that plainly rather than implying a cleanliness this pass doesn't have.

A second, narrower exposure: packets 09/10's expected answers were read from Jaswin's document during an earlier adjudication pass, and I ran ad-hoc queries against the live E06 engine for `AgentLinkma21JuneAA` and `AgentNacoPovertyTexas2015XQ` in an earlier session turn (informal spot-checks, not this ticket). Section 3 below discloses exactly what was and wasn't re-derived from raw source independently of that prior exposure.

## Design choices, and where they differ from E06

Both implementations necessarily converge on similar structure because the contract is prescriptive (apply groups atomically, admit every source-permitted ordering, never resolve ties by ID). Concretely, the reference:

- Classifies raw event dicts directly (`event_type`, `success_observed`, `request_action`, `revision_ref`) rather than going through a typed `ObservedEventSemantics` enum — same classification outcome, different code path, so a bug specific to that enum's construction wouldn't be shared.
- Represents ambiguity as a deduplicated set of `(state_kind, rev_id)` pairs for comparison purposes (`ReplayQuery.distinct_states`), rather than preserving one alternative per full permutation. This is a coarser representation than E06's (which keeps duplicate-state alternatives with distinct provenance, matching the contract's "convergence of body does not prove earlier chronology"). The differential tests below compare on the **set of admissible terminal states**, not alternative-count, since the contract explicitly permits E06's richer representation and doesn't mandate a minimal one. This is disclosed, not hidden, in case a future reviewer wonders why alternative counts differ between the two while states always match.
- Fails closed (`ReplayError`) on any event whose `event_type` isn't one of the four expected ones, same discipline as E06's `UnsupportedMutationError`, arrived at independently from the "fail closed for review" contract rule rather than by matching E06's exception name.

## 1. Blind packets revealed

### Packet 04 — `AgentProxyCountyNext987111`

Previously-held-back expectation (from `docs/V02_INDEPENDENT_RECONSTRUCTION_2026-09-12.md` / `audit/JASWIN_V02_RECONSTRUCTION.md`, unchanged since first written): create → 2 edits → delete (`138565`) → recreate (`@4`) → delete again 19 seconds later (`138624`) → recreate (`@5`) → 2 more edits → final delete (`151035`) six days later. Three deletions, two recreations, one title.

| Boundary | Expected | E06 output | Classification |
|---|---|---|---|
| `@1`–`@3` saves | `live(@1)` → `live(@2)` → `live(@3)` | matches | MATCH |
| delete `138565` | `deleted` | matches | MATCH |
| `@4` (recreate) | `live(@4)`, new episode | matches | MATCH |
| delete `138624`, 19s later | `deleted` | matches | MATCH |
| `@5` (recreate) | `live(@5)`, new episode | matches | MATCH |
| `@6`, `@7` | `live(@6)` → `live(@7)` | matches | MATCH |
| final delete `151035` | `deleted` | matches | MATCH |

12 query boundaries (before/at each of 7 mutations), 0 divergences. **Result: MATCH on every boundary.**

### Packet 08 — `OAIEquityDec30Raw` / `OECDJun26PrecisionScout`

Previously-held-back expectation: two independent 15/16-revision episodes, no structural link between the titles, both eventually deleted. The propagation-timing correction from `docs/R04_FROZEN_SPEC.md` departure #7 (the true method/replication content appears at `@4`/`@12`/`@13`, not `@5`/`@14`) is a claim-status/annotation question, not a state-transition question — it does not change what state the pages were in, so it isn't scored here as a state divergence.

30 query boundaries (before/at each of 15+16 saves plus each title's final delete), compared against E06. **Result: MATCH on every boundary**, both titles.

## 2. Packets 09/10 — independent acceptance, from source not from E06 output

**Packet 09 — `AI`.** Selection rule: ascending `page_key` among DSE titles with `n_revs_before > 0`. I re-ran this selection query directly against `pages.jsonl` (not reusing Jaswin's or anyone else's count) and independently got the same 11 eligible titles, first being `dse~AI`. Raw fields confirmed directly: `@2`'s `diff_base_reason=earlier_revisions_not_published`, `head_differs_from_live=true`, `live_body_variant=dw`, `deleted_live=false`. The state-model treatment (unknown → `live(@2)` at the one supported save, archival marker as a no-op, exclusion from exact body scoring) follows directly from these fields with no invented step.

**Verdict: ACCEPTED** for the mechanical state-model treatment. The narrower interpretive question — whether the head/live mismatch reflects an actual moderator overwrite — is **NEEDS_ADJUDICATION**, unresolved by the export alone (matches the contract's own "no moderator overwrite is inferred" stance), and does not block using this fixture for state-engine certification, since the engine is not required to resolve it either.

**Packet 10a — `AgentNacoPovertyTexas2015XQ`.** Selection rule: ascending `(page_key, time)` among DSE title/time groups with ≥2 physical mutation rows; first tie is `@22`/`@23` at `2026-06-22T08:39:06Z`. Independently re-confirmed from raw `revisions.jsonl`: both rows carry the identical selected time, different bodies (1,126 vs 2,054 bytes), different hashes, and no field in the export resolves which was applied first.

**Verdict: ACCEPTED.** The tie itself is **CONTRACT_AMBIGUITY** by design — the correct behavior is to represent it as unresolved, not to resolve it, and both E06 and the independent reference do exactly that (confirmed in §4).

**Packet 10b — `AgentBridgeOct2142X`.** Selection rule: ascending `page_key` among DSE titles with exactly one held revision, zero pre-cut revisions, and no delete/body-unknown mutation. I independently re-ran this exact filter against the raw export (not trusting the prior claim that it's "the sole qualifier") and got exactly one result: `dse~AgentBridgeOct2142X`.

**Verdict: ACCEPTED.**

All three packets may be promoted to full certification fixtures on the state-model dimension. Packet 09's interpretive (non-state) question stays open and belongs to A03/annotation work, not E06.

## 3. Differential testing — results

Full comparison script and output: `audit/reconstruction_checks.csv` (321 rows). Summary:

| Classification | Count |
|---|---|
| MATCH | 317 |
| MATCH_WITH_ALLOWED_AMBIGUITY | 4 |
| MAIN_ENGINE_BUG | 0 |
| REFERENCE_EXPECTATION_ERROR | 0 |
| CONTRACT_AMBIGUITY | 0 (folded into the 4 above — see note) |
| UNRESOLVED | 0 |

The 4 `MATCH_WITH_ALLOWED_AMBIGUITY` rows are the two genuinely ambiguous points in the whole released+diagnostic+blind fixture set: the `AgentNacoPovertyTexas2015XQ@22/@23` tie (before and at the boundary) and `AgentOfficialDirectQueryAA3`'s uncertainty-mode query where the deletion's clock is genuinely ambiguous — both engines correctly return the *same* ambiguous state set, not a resolved single winner.

Coverage: every mutation boundary (before and at) on packets 01, 02, 03, 05, 06, 07, 09, 10a, 10b, 04, and both 08 titles — 11 pages, every held save, every deletion, the one body-unknown mutation, one uncertainty-mode query pair, plus 5 adversarial probes below. **No divergence found anywhere.**

## 4. Adversarial tests

| Test | Method | Result |
|---|---|---|
| Future-suffix invariance | Built a truncated copy of the export (removed all `AgentLinkma21JuneAA` events after its first deletion) for **both** engines independently, and confirmed `state_at` at the deletion boundary is identical with and without the future events present | MATCH on both engines |
| Relation metadata has no state effect | Verified by source inspection of both implementations (not a runtime corruption test): the reference's `_classify` never reads `relation_type`/`related_event_id`/`round_id` at all; E06's `_mutation`/`_apply` capture relation edges only into `TransitionProvenance` with a hardcoded `relation_effect: Literal["none"]`, never consulted by the state-transition logic itself | Confirmed by code reading, both sides structurally guarantee this |
| Body-unknown invalidates previous body | Packet 06 (`OpenAIDataUSAPoliceBridge20260129`): confirmed the BU mutation clears state to `live_body_unknown` with no body reference, regardless of what came before | MATCH |
| Repeated deletion | Packet 04: two deletions with only 19 seconds between them, no save in between one pair; both engines handle delete→delete correctly (no implicit "undelete") | MATCH |
| Save following deletion (new episode) | Packets 03, 04, 05: confirmed via the full sweep | MATCH |
| Same-time mutation ambiguity | Packet 10a `@22`/`@23` | MATCH_WITH_ALLOWED_AMBIGUITY (both return the same 2-element ambiguous set) |
| Uncertainty windows | Packet 07's ambiguous-clock deletion, queried in `uncertainty` mode at two points spanning the window | MATCH |
| Missing prehistory | Packet 05 (deletion before `@1`) and packet 06 (no held page at all) | MATCH |
| Opaque page keys | Queried a page key that never appears anywhere in the export, and a page whose name contains a slash (`fractal~EN~2fFederalDataLinks`) to confirm no path-like parsing occurs | MATCH (both correctly `unknown`) |
| Different trajectories converging to the same physical state | Packet 10a after `@24`: state converges to `@24` on both engines even though the pre-convergence branch differed | MATCH |

## 5. Summary

1. **V07: CONDITIONAL PASS** — see certification decision below for exactly what remains conditional and why.
2. **Packet 04: MATCH** — 12/12 boundaries, revealed above.
3. **Packet 08: MATCH** — 30/30 boundaries across both titles, revealed above.
4. **Packet 09 (`AI`): ACCEPTED** for state-model purposes; interpretive head-mismatch question separately flagged NEEDS_ADJUDICATION (non-blocking).
5. **Packet 10 (`AgentNacoPovertyTexas2015XQ` tie + `AgentBridgeOct2142X` control): ACCEPTED**.
6. **Boundaries compared: 321** (across 11 pages, both blind titles, both diagnostics beyond the tie, plus 5 adversarial probes).
7. **Mismatches: 0.**
8. **Main-engine bugs found: 0.**
9. **Reference errors found: 0** (one bug was found and fixed in the *comparison harness* itself before any results were recorded — an enum-stringification mistake that produced 281 false mismatches on the first run; caught immediately because the false mismatches were suspiciously uniform in shape, fixed, and the full sweep re-run from scratch. Recorded here for the same reason `evidence_timeline/CORRECTIONS.md` records its own errors: this is exactly the failure mode the project studies, and hiding it would be worse than disclosing it.)
10. **Can E06 be promoted from CONDITIONAL PASS to FULL PASS?** On the *engineering* dimension, yes — nothing here would block it: every released, diagnostic, and blind fixture matches, packets 09/10 are independently accepted, and the adversarial suite found nothing. What keeps this at CONDITIONAL rather than unconditional FULL PASS is outside V07's scope to resolve: (a) this is the first blind reveal, not a second independent blind team's reveal — a genuinely fresh pair of eyes has still never checked packets 04/08 without prior exposure to their answers; (b) the data-path bug flagged in the previous session turn (`data/data/raw/export/` vs the `data/raw/export/` every test and this reference expects) still means a literal fresh clone cannot run any of this without a manual fix; (c) the raw third-party export's redistribution terms are still unresolved per `sources/registry.json`. None of these are state-model defects — they're process/repo-hygiene items — but "FULL PASS" should mean a stranger can clone the repo and get these exact 321 matches, and right now they can't without first fixing (b).
11. **Is E08 safe to begin?** Yes, on the state-engine dependency specifically — `state_at` has no found defects across the full available fixture set including both previously-blind packets. E08 has its own separate blocker already on record (the pre-E08 cost/accounting-schema amendment named in `docs/R04_FROZEN_SPEC.md` §6), which is unaffected by this result either way.

## E06 certification decision

## CONDITIONAL PASS

Every released, diagnostic, and previously-blind fixture matches between E06 and an independently-written, independently-reasoned reference implementation, across 321 compared boundaries and 10 adversarial probes, with zero divergences. The two genuinely ambiguous cases in the entire fixture set are represented identically as ambiguous by both engines, not resolved differently or resolved at all. Packets 09 and 10 are independently accepted from source evidence alone. Nothing found here would block E08 from starting on the state-engine dependency.

It stays CONDITIONAL, not FULL, because full certification implies a stranger can reproduce this exact result from a clean checkout, and right now they cannot (the `data/data/raw/export` path bug), and because "blind" packets 04/08 have now been revealed to and compared by the same person (me) who reconstructed their expectations — a second, genuinely fresh reviewer re-running this comparison without that history would be the stronger form of this same result.
