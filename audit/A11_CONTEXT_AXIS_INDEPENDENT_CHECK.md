# A11 Context Axis — Sam's Independent Check of Alex's Reconciliation

**Author:** Sam (independent validation)
**Date:** 2026-09-13
**Audited artifacts:** `annotations/context_eligibility.jsonl` (65 rows), `annotations/context_fragments.jsonl` (7 rows), `audit/A11_CONTEXT_RECONCILIATION.md` (Alex), commit `06c3e75` (merge of `298fcc6`).

Role reminder: this is an independent re-check of Alex's own report, not a restatement of it. Alex's "PASS"/"AGREE"/"confirmed" language is treated as a claim to verify, not as evidence, exactly as Ubayd's and my own prior claims have been treated elsewhere in this project.

## 1. Structural checks (all independently recomputed from scratch)

- `context_eligibility.jsonl` has exactly 65 rows, one per `evidence.jsonl` evidence_id, no duplicates, no extras — set equality confirmed by direct comparison, not by trusting the row count in the report.
- `context_needed: true` count is exactly 8, matching the report's executive summary: `PROP-20260619-03/-05`, `PROP-20260620-07/-08/-09`, `PROP-20260618-13/-16`, `PROP-20260616-61`.
- `context_fragments.jsonl` has exactly 7 rows; every `context_fragment_ids` reference in `context_eligibility.jsonl` resolves to a real fragment and every fragment is referenced by exactly one proposition (no dangling references either direction).
- **All 5 body-grounded fragments independently re-verified against the raw export** (`data/raw/export/revisions.jsonl`), using `sha256(body.encode("latin-1"))` for the hash and `body.encode("latin-1").decode(body_encoding)` for the span slice — the same reversal this review required in `E12_INDEPENDENT_ACCEPTANCE.md` §10, now correctly applied here too. 0 mismatches on hash or span text for `CTX-PROP-20260619-03-01`, `-05-01`, `PROP-20260620-07-01`, `-08-01`, `-09-01`.
- **Both event-based fragments (`PROP-20260618-13`, `-16`) independently re-verified against the raw `events.jsonl`**, not just accepted on the strength of the event ID cited: both named `delete:...` events exist, both have `event_type: delete` on the exact page named, and both fall strictly between the two named revisions' own `time` fields (`@15`/`@16` for -13, `@3`/`@4` for -16). This is a real, checkable temporal claim and it holds.

## 2. Spot-checks of substantive judgment calls

- **`PROP-20260619-04`** (the one place Alex's pass diverges from Sam's own `DRAFT_SAM`, ruling it self-contained where the draft required ZZZ@1 + a delete event): re-read the proposition's own quotation directly. It is exactly the `@16` "AUG17 NOTICE... try [[ZZZ...]]" text — i.e. the proposition is about the announcement itself, not about whether the backup was subsequently created or used. Alex's reasoning holds; this looks like a genuine improvement over Sam's earlier, overly conservative draft judgment, not a new gap.
- **`PROP-20260617-19`** pre-commit correction (corroboration vs. interpretation): re-read against the actual epistemic-tier rubric distinction described — the proposition is about what the agent reported, not whether the report was accurate. Sound.

## 3. Finding: the `PROP-20260616-61` "corpus coverage gap" claim does not hold up

Section 4.2 of `audit/A11_CONTEXT_RECONCILIATION.md` states, for `PROP-20260616-61` ("Suspect next is Cleveland Community College (2304), because older Ivy helper pages queried IDs in order/set 107327,199333,198321"):

> "These older pages are referenced generically by the agent and are neither identified nor pinned in `evidence.jsonl` or the benchmark catalog. No verifiable character span or revision ID can be grounded from the benchmark corpus."

**A full-corpus search over all of `data/raw/export/revisions.jsonl` for the literal substring `107327,199333,198321` (URL-encoded as `107327%2C199333%2C198321`) finds it verbatim, in exactly that order, on at least three pages that all predate `PROP-20260616-61`'s own revision (`dse~DataUSAIvyTuitionSequenceCollab2027@1`, saved `2026-06-16T19:47:51Z`) by more than two weeks:**

| Page | Earliest revision | Time |
|---|---|---|
| `dse~AgentIvyTuitionValues2015XQ@1` | body contains `University%3A107327%2C199333%2C198321` | `2026-06-01T16:14:15Z` |
| `dse~AgentDataUsaUnique5@1` | same ID triple, same order | `2026-06-01T16:03:04Z` |
| `dse~AgentIvyLink@1` | same ID triple, same order | `2026-06-01T15:54:26Z` |

`dse~AgentIvyTuitionValues2015XQ@1`'s full 665-byte body is a DataUSA tuition API query URL for exactly `University:107327,199333,198321;Year:2015` — its own page name literally contains "Ivy" and "Tuition", making it a strong reading of "an older Ivy helper page" that "queried IDs in order/set 107327,199333,198321." Independently recomputed: `sha256(body.encode("latin-1"))` = `dd3bbb36f3f7bfffc55aecc74d96eee2ebdb96f7bb8c4394ec8b9efd805b8df2`, matching the raw export's own recorded `body_sha256` exactly. A candidate groundable span exists at `[56, 248]` (the full query-string line).

A fourth near-match, `dse~AgentTuitionEvidenceK@1`, contains a superset of IDs in a *different* order (`150987,174756,101514,199333,198321,107327`) and is a weaker match — worth noting because it suggests the annotation team's search may have surfaced this kind of near-duplicate boilerplate (the project already has one precedent for exactly this shape of ambiguity: `PROP-20260616-10`'s reused API-documentation URLs, explicitly reasoned about and excluded in §3.4 of the same report) and either mis-set the disposition here, or ran a narrower search than the one that caught it for `PROP-20260616-10`.

**This does not mean `PROP-20260616-61` should definitely be re-marked context-groundable** — that is a substantive annotation call for Alex/Aaron/Jaswin (is `AgentIvyTuitionValues2015XQ` *the* page the agent meant, given at least 3 near-identical candidates exist, or is this the same kind of generic-boilerplate situation already adjudicated for `PROP-20260616-10`?). What this finding does establish is that **the report's specific claim — "no verifiable character span or revision ID can be grounded from the benchmark corpus" — is factually incorrect**: verifiable, hash-confirmed, correctly-ordered, pre-dating spans do exist in the raw corpus. The "benchmark coverage gap" framing in §4.2 should be corrected to either ground the reference or explicitly document the multi-candidate ambiguity (as was done for `PROP-20260616-10`), not describe it as ungroundable.

## 4. Not checked in this pass

- Whether `context_eligibility.jsonl`/`context_fragments.jsonl` are actually wired into any evaluator/loader path yet (Alex's own report says this ticket is annotation-side only; no E12/coverage scoring was run here either).
- The other AGREE rows in §3.2 (`-03`, `-05`, `-07`, `-08`, `-09`) were checked for hash/span correctness (§1 above) but not re-litigated on substance beyond `-04` and `-19`, since Alex's own stated rationale for those reads as consistent with the quoted text on direct re-reading.
- Full regression: 152/152 tests pass on the merged commit (`06c3e75`); this is not a substitute for the substantive check above.

## 5. Verdict

**Mechanically sound: hash/span/event grounding for all 7 fragments and referential integrity across all 65 propositions independently confirmed, 0 discrepancies.** **One substantive finding stands**: §4.2's "corpus coverage gap" claim for `PROP-20260616-61` is not supported — real candidate grounding exists and should be resolved (grounded or explicitly flagged as ambiguous) rather than recorded as a gap. Not a blocker fabricated to look serious — it's a specific, reproducible, three-line search anyone can rerun. Does not itself change any E12 verdict; this is annotation-content feedback for Alex/Aaron/Jaswin.
