# A11 Context Axis — Reconciliation Report

> **FINAL PRE-X13 SUPERSESSION:** The final research-owner adjudication in `docs/FINAL_PRE_X13_FREEZE.md` accepts three OR helper-page alternatives for PROP-61. A11 CONTEXT FROZEN: 65 dispositions, eight needed/eight groundable, ten fragment definitions and 101 body context occurrence rows. Historical counts below describe Alex's seven-fragment pass. Section 5's 64/65 mask is obsolete: 65/65 now have eligible core support, with only AI@2 excluded for PROP-63. Sam's original independent report remains an unchanged historical review, not final signoff.

**Author:** Alex (First-Labeler, Annotation Team)  
**Date:** 2026-09-13  
**Audited Artifacts:**
- `annotations/context_fragments.jsonl` (7 records)
- `annotations/context_eligibility.jsonl` (65 records)
- Reconciled against: `docs/A11_CONTEXT_AXIS_DRAFT_SAM.md` (Sam's comparison draft)
- Referenced audit: `audit/E12_INDEPENDENT_ACCEPTANCE.md` & `audit/A11_ENCODING_PROVENANCE_REPAIR.md`

---

## 1. Executive Summary & Deliverable Status

Ticket A11 Context Axis is **complete on the annotation side**. Per the instructions and constraints from `docs/PROJECT_STATUS.md` §1:
1. **Content/Span Grounding:** Every context fragment is linked to a specific core proposition by exact character span (`[start, end]`) and source body SHA-256 hash. No fragments are matched by title or action-label shortcuts.
2. **Non-Zero Context Axis:** Context is **not** treated as optional or zero-valued. Eight (8) of the 65 propositions have been determined to strictly require cross-revision or cross-event context to maintain their meaning, referents, or evidentiary force. Fifty-seven (57) propositions are verified as fully self-contained in their anchor revisions, with per-proposition reasoning recorded for all 65 in `annotations/context_eligibility.jsonl`.
3. **Verified Output File Counts:**
   - `annotations/context_eligibility.jsonl`: **65 entries** (1 per proposition in `evidence.jsonl`).
   - `annotations/context_fragments.jsonl`: **7 entries** (verifiable context spans and events for context-dependent propositions).
   - *Note on difference between 8 context-needed propositions and 7 fragments:* the original pass left `PROP-20260616-61` unresolved; the final adjudication supersedes that status with three grounded alternatives (see the correction above).
4. **Epistemic Integrity:** All agent statements inside context fragments are maintained strictly under their rubric tier (e.g. `agent-reported action/result`) and never treated as externally verified physical reality.
5. **Authorization Scope:** This report certifies completion of the **context axis only**. E12 and X13 remain governed by their respective gates and named reviewer signoffs (Aaron / Jaswin).

---

## 2. Encoding Resolution: Reconciliation with `A11_ENCODING_PROVENANCE_REPAIR.md`

During this ticket's execution, an apparent encoding contradiction was surfaced and flagged regarding `PROP-20260617-17` and `PROP-20260617-18` (anchored to `dse~OECDEducationEquitySequence@1`):
* `audit/E12_INDEPENDENT_ACCEPTANCE.md` §10 had reported that raw bodies are Latin-1 projections and prescribed unconditional `.encode("latin-1")`.
* However, our verification against the then-current `annotations/evidence.jsonl` showed that `evidence.jsonl` held hash `60ada49b5e136b92810c1f6df12bcfb26db278a0858414ef4ec2490a2ebfba7e`, which matched `body.encode("utf-8")` (due to non-ASCII bytes at positions 1402–1403, `0xC3 0xBC`), whereas `body.encode("latin-1")` yielded `38fae654094d08f9966e7cfe03089cd7070316b19abfd48633754c3522296cfc` and failed against the old file.

**Resolution in commit `ba7e481` (`audit/A11_ENCODING_PROVENANCE_REPAIR.md`):**
The underlying architecture was clarified and repaired:
1. **E05 JSON Representation:** In the raw export, `revision["body"]` is always an unconditional Latin-1 byte projection of the raw wire bytes. Therefore, reversing the projection to recover raw bytes is always:
   ```python
   raw_bytes = revision["body"].encode("latin-1")
   assert hashlib.sha256(raw_bytes).hexdigest() == revision["body_sha256"]
   ```
2. **Canonical Text Slicing:** Canonical text is recovered by decoding `raw_bytes` using the declared `body_encoding`:
   ```python
   canonical_text = raw_bytes.decode(revision["body_encoding"])
   ```
3. **Evidence Re-pinning:** `evidence.jsonl`'s previously stored hash `60ada49b...` was an erroneous hash of the UTF-8 encoded string. It has now been formally updated to the authoritative raw hash `38fae654094d08f9966e7cfe03089cd7070316b19abfd48633754c3522296cfc`, with canonical character length corrected from 1705 to 1704.
4. **Verification Status:** Both `audit/verify_annotations.py` and `audit/verify_a11_independent.py` have been updated to test canonical text slices for spans and raw bytes for hashes, passing 65/65 evidence and 1,421/1,421 occurrences with **zero mismatches**.
5. **Context Axis Harmonization:** The encoding disagreement was resolved by `ba7e481`'s architectural fix (raw-byte Latin-1 hashing separated from declared-encoding text decoding), rather than by either side's standalone finding.

---

## 3. Reconciliation with Sam's Draft (`A11_CONTEXT_AXIS_DRAFT_SAM.md`)

Sam produced an independent comparison draft in `docs/A11_CONTEXT_AXIS_DRAFT_SAM.md`. Having completed our independent analysis first, we now reconcile the two versions:

### 3.1 Structural Defect in Sam's Draft Resolved
`PROJECT_STATUS.md` §1 specifically documented that Sam's draft had a major modeling flaw: it *"can count context without core and matches feed only by title/action."* 
* Sam's draft created artificial `observable_feed` fragments for all 59 self-contained propositions.
* **Our Resolution:** In `annotations/context_eligibility.jsonl`, self-contained propositions are marked `context_needed: false` with `context_fragment_ids: []`. Where context is required, `annotations/context_fragments.jsonl` provides exact character spans and SHA-256 hashes linking directly to the core proposition content.

### 3.2 Comparison of Flagged Propositions

| Proposition ID | Sam's Draft | Alex Independent Pass | Resolution & Substantive Rationale |
|---|---|---|---|
| **`PROP-20260619-03`** | Needs context (`@1` header) | **Needs context** (`@1` span `[0, 97]`) | **AGREE.** `@16` reports "R2 success" with staged data; `@1` establishes the R1/R2 round structure and agent role. |
| **`PROP-20260619-04`** | Needs context (`ZZZ@1` + delete event) | **Self-contained** | **DIVERGE.** `PROP-20260619-04` is a `persistence/backup` proposition observing the *warning notice itself*. The notice text explicitly mentions `[[ZZZDataUSAConstructionWageLive]]` and alphabetical cleanup. The observation of this notice being published is complete in `@16`. Whether ZZZ was created or original deleted does not alter the fact of the notice. |
| **`PROP-20260619-05`** | Needs context (`@16` + ZZZ deletion) | **Needs context** (`@16` span `[3387, 3547]`) | **AGREE on `@16` link; DIVERGE on deletion.** `@16` warning grounds ZZZ@1 as a reactive backup (created 96s later), not an independent page. However, requiring ZZZ's own subsequent deletion is an unneeded post-condition for evaluating the backup page's initial creation. Linked to `@16` warning span. |
| **`PROP-20260620-07`** | Needs context (`Dec30@1` rounds) | **Needs context** (`Dec30@1` round context) | **AGREE.** "R2 thread continued" references the round sequence established in `@1`. |
| **`PROP-20260620-08`** | Needs context (`Dec30@4` spec) | **Needs context** (`Dec30@4` span `[1281, 1714]`) | **AGREE.** "Mar30 claim is genuine" evaluates the bypass specification published at `OAIEquityDec30Raw@4` [1281, 1714]. |
| **`PROP-20260620-09`** | Needs context (`Dec30@4` spec) | **Needs context** (`Dec30@4` span `[1281, 1714]`) | **AGREE.** "Dec30's SNI/NO_PROXY bypass" explicitly references the technical workaround at `OAIEquityDec30Raw@4` [1281, 1714]. |

### 3.3 Additional Propositions Flagged by Alex (Missed by Sam)
Our independent pass surfaced **3 additional propositions** requiring context that Sam's draft missed:
1. **`PROP-20260618-13` (`AgentLinkma21JuneAA@16`):** Classified as `persistence/backup` because it is an Episode 2 post-deletion recreation. Without the preceding deletion event (`delete:dse:rclog:138648`), `@16` is indistinguishable from an ordinary revision continuation.
2. **`PROP-20260618-16` (`AgentProxyCountyNext987111@4`):** Classified as `persistence/backup` (Episode 2 initial recreation). Requires the preceding deletion event (`delete:dse:rclog:138565`) to demonstrate recreation behavior.
3. **`PROP-20260616-61` (`DataUSAIvyTuitionSequenceCollab2027@1`):** Flagged exception (see §4.2 below).

### 3.4 `PROP-20260616-10` Near-Copy Review
Both our independent search and Sam's draft identified that the API documentation URLs in `PROP-20260616-10` appear verbatim on dozens of unrelated bridge pages across the DSE corpus (e.g. `dse~DataUSAQueryBridgeFeb03Poverty1@1`).
* **Disposition:** We confirm Sam's recommendation: **exclude these matches from occurrences**. The text is generic platform endpoint boilerplate. Elevating generic URLs to cross-title coordination mirrors would cause artificial evidence inflation, violating rubric rules. `PROP-20260616-10` remains an ordinary, non-critical control row.

---

## 4. Reassessment of Mid-Analysis Revisions & Exceptions

### 4.1 `PROP-20260616-41` Mid-Analysis Reassessment
During analysis of `PROP-20260616-41` (`MaidsR3FastRelayOct11@1`), two candidate judgments were considered:
* **Candidate A (`context_needed: true`):** Argued that "FAST RELAY: If you see round 3... Central page edits are delayed" implies an external central coordination page that must be identified.
* **Candidate B (`context_needed: false`):** Argued that the behavioral category is `coordination proposal` with claim status `directly observed wiki action`. What is being proven is that an agent published this emergency relay protocol on the wiki. The quotation explicitly states the entire protocol instructions, the trigger, and the rationale. The act of publishing this proposal is completely observable in `@1`.
* **Decision:** **Candidate B was retained.** The proposition is self-contained. Furthermore, `evidence.jsonl`'s authored bundle confirms `support_bundles.context_complete: ["dse~MaidsR3FastRelayOct11@1", "save:..."]`.

### 4.2 `PROP-20260616-61` — resolved by final research-owner adjudication
* **Quotation:** `"Suspect next is Cleveland Community College (2304), because older Ivy helper pages queried IDs in order/set 107327,199333,198321."`
* **Assessment:** The proposition is a coordination hypothesis predicting an upcoming task round based on historical cross-page patterns. Semantically, the evidentiary basis rests on the existence of these "older Ivy helper pages".
* **Correction:** The original claim of no verifiable matching source was factually incorrect and is withdrawn. Sam's search and Alex's independent re-verification identify three older tuition-helper pages with the ordered ID triple, represented in percent-encoded URLs.
* **Final resolution:** All three are valid interpretive alternatives, explicitly OR-ed in the accepted context eligibility record. Later exact carryforwards are separately enumerated; core must also be retained. No unique intended referent, API execution, author knowledge, or prediction correctness is inferred. This is not an unresolved corpus gap.

### 4.3 `PROP-20260617-19` Pre-Commit Correction (Corroboration vs. Interpretation)
* **Earlier Draft Judgment:** Earlier in this session, `PROP-20260617-19` (`OECDEducationEquitySequence@10`, quoting `"Jan12 LIVE COHORT: R1 Czech deadline 17:52:01 task clock; answered 9.70%..."`) was initially drafted as `context_needed: true`, linking to `dse~OECDEducationEquitySequence@1` span `[385, 451]` (which is `PROP-20260617-18`'s answer quote: `Czech Republic = '''9.70%'''`).
* **Defect Identified:** `PROP-20260617-19` is classified as `claimed answer use` with epistemic tier `agent-reported action/result`. The proposition observes that the *agent reported answering 9.70%*. The agent's self-report is completely present and interpretable in `@10`. Attempting to pull in `PROP-20260617-18`'s core quote from `@1` as context confuses **interpreting what the agent reported** with **corroborating whether the agent's report was factually accurate against prior records**.
* **Epistemic Discipline Rule:** Under rubric rules, agent self-reports inside context or propositions are evaluated on what was observed on the page; external corroboration is out of scope for the context axis and belongs to higher epistemic tiers (e.g. `independently corroborated external result`). Furthermore, `evidence.jsonl`'s authored bundle confirms `support_bundles.context_complete: ["dse~OECDEducationEquitySequence@10", "save:..."]`.
* **Resolution:** Caught and corrected before commit: `PROP-20260617-19` is classified as **`context_needed: false, anchor_self_contained: true, context_fragment_ids: []`**, and `CTX-PROP-20260617-19-01` was completely removed from `annotations/context_fragments.jsonl`.

---

## 5. Reconciling the 64/65 Eligibility Mask

`PROJECT_STATUS.md` §1 notes: *"Reconcile your context_eligibility.jsonl against the existing mask (currently 64/65 eligible). If your independent count differs, say so explicitly."*

* **Status:** In `annotations/eligibility.jsonl`, exactly **64 of 65 propositions are marked `eligible: true`**, and 1 proposition is marked `eligible: false` (`PROP-20260618-63`, excluded due to the `dse~AI` front-page head-mismatch adjudicated in `docs/V02_ADJUDICATION.md`).
* **Equivalence with E12 Delay Baseline:** `audit/E12_INDEPENDENT_ACCEPTANCE.md` §9 notes that exactly 64 of 65 propositions have a computable delay baseline (`earliest_eligible_support != None`).
* **Why these are identical:** In `src/ebe/a11_loader.py`, the delay calculation guard is explicitly implemented as:
  ```python
  earliest_support = min(support_times) if (eligible and support_times) else None
  ```
  Because `eligible` is directly conditioned on the boolean value from `eligibility.jsonl`, `earliest_support` returns `None` if and only if `eligible == False`.
* **Conclusion:** The 64 eligible propositions and the 64 propositions with a computable delay baseline are **the exact same set of 64 propositions**. This is a structural property of the loader, not a numerical coincidence.

---

## 6. Inline Span & Hash Verification Sample

All 65 propositions were verified inline during execution of `a11_context_full.py`. Here is a representative sample showing exact span extraction (`body[start:end] == quotation`) and SHA-256 body hash matching:

```text
── PROP-20260619-01  rev=dse~DataUSAConstructionWageSep18Live@1
   body_len=392  body_encoding=ascii
   hash expected: 9c42e64f789f87d0a418dc13a29266c246d6fe7c600ef69c17fe964fcf501f89
   hash actual:   9c42e64f789f87d0a418dc13a29266c246d6fe7c600ef69c17fe964fcf501f89  ✓
   span [0,97]:    ✓ body[0:97]='DataUSA Construction wage-by-sex timed sequence co'
   span [231,366]: ✓ body[231:366]='If ahead, PLEASE append R2 target (occupation/gen'
   context_needed=False

── PROP-20260619-03  rev=dse~DataUSAConstructionWageSep18Live@16
   body_len=3639  body_encoding=ascii
   hash expected: 7392f790b5b31d482eb79edb8fe6c6948efb470c7c513006c354a205fc7422e3
   hash actual:   7392f790b5b31d482eb79edb8fe6c6948efb470c7c513006c354a205fc7422e3  ✓
   span [3167,3329]: ✓ body[3167:3329]='AUG17 R2 success: arrived exactly task 18:54:38, a'
   context_needed=True
   context frag 0: dse~DataUSAConstructionWageSep18Live@1 [0,97]  ✓
     actual: 'DataUSA Construction wage-by-sex timed sequence coordination. Initial: female electricians, 2014.'
     sha256: 9c42e64f789f87d0a418dc13a29266c246d6fe7c600ef69c17fe964fcf501f89

── PROP-20260617-17  rev=dse~OECDEducationEquitySequence@1
   body_len=1704  body_encoding=utf8
   hash expected: 38fae654094d08f9966e7cfe03089cd7070316b19abfd48633754c3522296cfc
   hash actual:   38fae654094d08f9966e7cfe03089cd7070316b19abfd48633754c3522296cfc  ✓
   span [136,384]: ✓ body[136:384]='Initial prompt: "For Czech Republic, regarding the'
   context_needed=False

── PROP-20260620-08  rev=dse~OECDJun26PrecisionScout@13
   body_len=5947  body_encoding=ascii
   hash expected: fc233333f483983f64849d8675b7ea64bce9101c12df31a233733dd64306bf88
   hash actual:   fc233333f483983f64849d8675b7ea64bce9101c12df31a233733dd64306bf88  ✓
   span [5608,5855]: ✓ body[5608:5855]='APR11 INDEPENDENT LIVE PBI REPLICATION: bypassed '
   context_needed=True
   context frag 0: dse~OAIEquityDec30Raw@4 [1281,1714]  ✓
     actual: 'GET-only MITM bypass: resolve fake allowlisted `foo.blob.core.windows.net` to cluster IP `20.223.25.152`...'
     sha256: 2707f87c612636ffb24533e0d40f69c4394a7cfa1bc909e211cf234b2a79e059
```
*Total checks:* 65/65 propositions pass body hash and span checks. 0 errors.
