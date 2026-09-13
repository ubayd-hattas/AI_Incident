# A11 final benchmark specification — FINAL_PRE_X13_v1

**A11 CONTEXT FROZEN. A11 semantic inventory frozen before outcomes.**
Authority, canonical git-blob pins, evaluator compilation and run authorization: `docs/FINAL_PRE_X13_FREEZE.md`. This supersedes earlier stale counts/hashes and does not assert independent final E12 PASS.

| Inventory | Development | Held-out | Total |
|---|---:|---:|---:|
| Propositions | 38 | 27 | 65 |
| Critical | 34 | 23 | 57 |
| Noncritical | 4 | 4 | 8 |
| Core-eligible at July 15 | 38 | 27 | 65 |
| Groups | 14 | 11 | 25 |
| Catalog pages including context dependencies | 30 | 22 | 52 |
| Core occurrence rows (span records, not units) | 808 | 613 | 1,421 |
| Context-needed / groundable propositions | 6 / 6 | 2 / 2 | 8 / 8 |
| Declared episode IDs, NOT validated evidence-bearing episodes | 39 | 32 | 71 |

Primary nominal K is **23 held-out critical body-grounded propositions**. The one-unit granularity is 100/23 percentage points. All 65 have exact core alternatives; no proposition-level core exclusions or unresolved core labels. `PROP-20260618-63` excludes only `dse~AI@2`; its already-recorded `dse~AgentSecCountyVarAI@1` support remains eligible. One excluded core occurrence row remains in the 1,421-row census. Trace-wide head-mismatch/BU/unknown rules still apply; the runtime stable-support mask is a separate deterministic derived artifact, not new annotation judgment.

The complete existing 65-unit purposive named sample is retained. No count-balancing, new units, resampling or stopping based on capture likelihood. The original pilot GRP-02 remains wholly development. Accepted core copy relations and all context dependencies are grouped together: the two newly grounded helper titles AgentDataUsaUnique5 and AgentIvyLink join held-out GRP-19, without moving a proposition or inventing episodes. No shared page across splits.

The 71 episode IDs are a historical catalog, not a validated evidence-bearing episode census. We do **not** certify the >=40 adjudicated-episode design target, complete candidate rejection log, representative sampling frame, or exhaustive semantic/paraphrase recall. The study is therefore explicitly **exploratory, prespecified finite-benchmark evaluation**, not completion of the original full-design confirmatory study. The unchanged practical hypothesis remains falsifiable on this inventory. Review fields exist for all 65; they do not retrospectively prove blinded independent semantic review of every axis.

## Accepted support semantics

`evidence.jsonl`, `occurrences.jsonl`, `eligibility.jsonl`, `splits.json`, and `adjudication.csv` freeze core labels, exact OR-of-AND support, per-alternative exclusions, grouping and epistemic tiers. No external truth or distinct-agent identity is inferred from signatures or self-reported success. Final ledger prose corrects the directly inconsistent identity/cleanup language on -09/-04 without changing labels.

`context_eligibility.jsonl` freezes 57 self-contained and eight context-needed units. `context_fragments.jsonl` has ten definitions: eight body fragments and two exact observable event predicates. `context_occurrences.jsonl` enumerates 101 exact body context occurrences across the whole DSE body population; no normalized matching enters scoring. Three definitions are interchangeable helper contexts for PROP-61. Body hashes refer to raw source bytes; context census separately records canonical UTF-8 hashes and both coordinate domains.

For required context, the extra-context alternatives are the explicit `context_alternatives` when present; otherwise one AND-list containing the nonempty `context_fragment_ids`. A self-contained unit's context-complete alternatives equal its core alternatives. Compile required-context alternatives by Cartesian product with eligible core alternatives. Context can never count without core. No DRAFT file is accepted.

## Final PROP-20260616-61 disposition

**Multiple valid alternative context fragments (option 2).** Any one of the three June 1 tuition-query pages interprets the exact ordered ID pattern; this does not identify which page the author read or prove the query executed. Later exact same-page carryforwards are eligible context at actual acquisition time, never backdated. The anchor's twenty repeated assertions are core support, not independent helper-page context. The former claim of no matching source is withdrawn. See the final freeze for the full adjudication.

## Verification

Data-only checks (no collector join):

```
python audit/verify_annotations.py
python audit/verify_a11_independent.py
python audit/verify_final_context.py
```

Final consolidation observed 65/65 evidence, 1,421/1,421 core occurrences, all ten context references and 101 context body occurrences valid; zero source hash/span mismatches. Re-running an independent author's script is not a new independent Sam signoff. All post-outcome semantic corrections require public versioning, retained original results and disclosure.
