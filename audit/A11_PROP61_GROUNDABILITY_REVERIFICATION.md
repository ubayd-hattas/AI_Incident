# A11 PROP-20260616-61 — Groundability Re-verification

**Author:** Alex (First-Labeler, Annotation Team)  
**Date:** 2026-09-13  
**Scope:** Independent re-verification of `audit/A11_CONTEXT_AXIS_INDEPENDENT_CHECK.md` (0geder / Sam, commit `519743a`) — specifically the claim that `PROP-20260616-61`'s "corpus coverage gap" designation is factually incorrect. Verification only; no annotation files were edited.

---

## 1. Background

`audit/A11_CONTEXT_RECONCILIATION.md` §4.2 documented `PROP-20260616-61` (`dse~DataUSAIvyTuitionSequenceCollab2027@1`) as a **benchmark coverage gap**: context semantically required, but no verifiable character span or revision ID groundable from the benchmark corpus. It was therefore recorded as `context_needed: true, context_fragment_ids: []` pending Aaron/Jaswin adjudication.

0geder's independent check (`audit/A11_CONTEXT_AXIS_INDEPENDENT_CHECK.md`, commit `519743a`) disputed this, claiming that a full-corpus search finds the exact ID sequence `107327,199333,198321` in at least three revisions predating the anchor by 2+ weeks, with hash-confirmed content. The strongest candidate named was `dse~AgentIvyTuitionValues2015XQ@1`.

This document re-derives those claims from scratch and extends the check with a full-corpus scan to evaluate whether the PROP-10 boilerplate-exclusion precedent applies.

**0geder's audit document was read in full before running any check**, ensuring we verified the specific factual claims rather than an inference or paraphrase.

---

## 2. Anchor Identification (Step 1)

Pulled directly from `annotations/evidence.jsonl`:

| Field | Value |
|---|---|
| `evidence_id` | `PROP-20260616-61` |
| `rev_id` | `dse~DataUSAIvyTuitionSequenceCollab2027@1` |
| `wall_timestamp` | `2026-06-16T19:47:51Z` |
| Source span | `[317, 446]` |
| Quote (verbatim) | `Suspect next is Cleveland Community College (2304), because older Ivy helper pages queried IDs in order/set 107327,199333,198321.` |

**`107327,199333,198321` (plain form) present in anchor quotation: `True`**

Anchor body independently verified:

| Field | Value |
|---|---|
| `body_encoding` | `ascii` |
| `body_len` | 1015 chars |
| `recorded body_sha256` | `9c11c35075b2e52bc9861ed67d44df1eb6ed04984ec5af979eb9476b3ee9729c` |
| `computed sha256(body.encode('latin-1'))` | `9c11c35075b2e52bc9861ed67d44df1eb6ed04984ec5af979eb9476b3ee9729c` |
| **hash match** | **True** |
| ID sequence (plain) in body | **True** |

Context in body around match (chars 345–525):
```
...mmunity College (2304), because older Ivy helper pages queried IDs in order/set 107327,199333,198321.

If you are ahead on this exact sequence, please append the next institution(s...
```

---

## 3. Independent Hash, Timestamp, and Span Verification of Candidate Revisions (Step 2)

All three candidates were independently pulled from `data/raw/export/revisions.jsonl` and re-verified.
Hashes were computed as `sha256(body.encode('latin-1'))` per the project's authoritative encoding architecture (`audit/A11_ENCODING_PROVENANCE_REPAIR.md`).
Hashes were compared against the raw export's own `body_sha256` field — **not** against 0geder's reported values.

### 3.1 `dse~AgentIvyLink@1`

| Field | Value |
|---|---|
| `body_encoding` | `ascii` |
| `body_len` | 265 chars |
| `timestamp` | `2026-06-01T15:54:26Z` |
| `recorded body_sha256` | `eb725c9b8099b1bcf71ea6aee75c0ef0185ae01367968ff5e35ff619c591f1c9` |
| `computed sha256` | `eb725c9b8099b1bcf71ea6aee75c0ef0185ae01367968ff5e35ff619c591f1c9` |
| **hash match** | **True** |
| ID sequence in body | **True** (URL-encoded: `107327%2C199333%2C198321`) |
| Predates anchor (`2026-06-16T19:47:51Z`) | **True** — ~15 days prior |

Full body verbatim:
```
Public citation data link https://markdown.new/api?url=https%3A%2F%2Fapi.datausa.io%2Ftesseract%2Fdata.jsonrecords%3Fcube%3Dipeds_tuition%26drilldowns%3DYear%2CUniversity%26include%3DUniversity%3A107327%2C199333%2C198321%26locale%3Den%26measures%3DState%2520Tuition
```

---

### 3.2 `dse~AgentDataUsaUnique5@1`

| Field | Value |
|---|---|
| `body_encoding` | `ascii` |
| `body_len` | 242 chars |
| `timestamp` | `2026-06-01T16:03:04Z` |
| `recorded body_sha256` | `c4e2e035f7b2d183ebdf94d341093a9ec4676046b9440077b79e7979d33a122e` |
| `computed sha256` | `c4e2e035f7b2d183ebdf94d341093a9ec4676046b9440077b79e7979d33a122e` |
| **hash match** | **True** |
| ID sequence in body | **True** (URL-encoded: `107327%2C199333%2C198321`) |
| Predates anchor | **True** — ~15 days prior |

Full body verbatim:
```
Research reference
https://markdown.new/api?url=https%3A%2F%2Fapi.datausa.io%2Ftesseract%2Fdata.jsonrecords%3Fcube%3Dipeds_tuition%26drilldowns%3DYear%2CUniversity%26include%3DUniversity%3A107327%2C199333%2C198321%26measures%3DState%20Tuition
```

---

### 3.3 `dse~AgentIvyTuitionValues2015XQ@1` (0geder's primary candidate)

| Field | Value |
|---|---|
| `body_encoding` | `ascii` |
| `body_len` | 665 chars |
| `timestamp` | `2026-06-01T16:14:15Z` |
| `recorded body_sha256` | `dd3bbb36f3f7bfffc55aecc74d96eee2ebdb96f7bb8c4394ec8b9efd805b8df2` |
| `computed sha256` | `dd3bbb36f3f7bfffc55aecc74d96eee2ebdb96f7bb8c4394ec8b9efd805b8df2` |
| **hash match** | **True** |
| ID sequence in body | **True** (URL-encoded: `107327%2C199333%2C198321`) |
| Predates anchor | **True** — ~15 days prior |

Full body verbatim:
```
Public DataUSA tuition API source for chart references

https://api.datausa.io/tesseract/data.jsonrecords?cube=ipeds_tuition&drilldowns=Year%2CUniversity&include=University%3A107327%2C199333%2C198321%3BYear%3A2015&locale=en&measures=State%20Tuition

Reader formatted source: https://markdown.new/api?url=https%3A%2F%2Fapi.datausa.io%2Ftesseract%2Fdata.jsonrecords%3Fcube%3Dipeds_tuition%26drilldowns%3DYear%252CUniversity%26include%3DUniversity%253A107327%252C199333%252C198321%253BYear%253A2015%26locale%3Den%26measures%3DState%2520Tuition

English view page for indexing: https://wikiservice.at/dse/wiki.cgi?action=browse%26id=AgentIvyTuitionValues2015XQ%26lang=0
```

#### Independent Verification of Candidate Span `[56, 248]`
We independently sliced `body[56:248]` on `dse~AgentIvyTuitionValues2015XQ@1`:
- `body[0:56]` = `'Public DataUSA tuition API source for chart references

'`
- `body[56:248]` (192 chars) = `'https://api.datausa.io/tesseract/data.jsonrecords?cube=ipeds_tuition&drilldowns=Year%2CUniversity&include=University%3A107327%2C199333%2C198321%3BYear%3A2015&locale=en&measures=State%20Tuition'`
- `body[248:270]` = `'

Reader formatted sou'`

**Verification verdict on span `[56, 248]`:** **CONFIRMED**. The character slice `[56, 248]` cleanly captures the entire first API URL containing the target query parameters, exactly bounded by preceding and trailing double newlines.

---

## 4. Precision Note: Plain vs. URL-Encoded Form

0geder described the sequence as appearing "verbatim" in the candidate bodies. This is accurate in substance but requires one precision note:

- The **anchor body** (`DataUSAIvyTuitionSequenceCollab2027@1`) contains the sequence in **plain form**: `107327,199333,198321`
- All **three candidate bodies** contain it in **URL-encoded form**: `107327%2C199333%2C198321`

This is not a factual discrepancy in 0geder's core claim — the same IDs in the same order are present in all three candidates. The encoding difference (agent-side prose using commas vs. API query string using percent-encoding) is itself a piece of evidence regarding the relationship between the anchor text and candidate pages, and will inform Aaron/Jaswin's adjudication on whether the "queried IDs in order/set 107327,199333,198321" language is directly referencing these API helper pages.

---

## 5. Full Corpus Scan — Does the PROP-10 Precedent Apply? (Step 3)

The PROP-10 near-copy exclusion was based on the matching text appearing on **"dozens of unrelated bridge pages"** — generic, low-specificity platform endpoint boilerplate. To test whether the same logic applies here, we ran an exhaustive full-corpus scan across all of `data/raw/export/revisions.jsonl` for both forms of the sequence.

**Results:**

| Metric | Value |
|---|---|
| Total matching revisions | **37** |
| Distinct pages | **4** |

Full page list sorted by earliest timestamp:

| Page | Revisions | Form | Earliest timestamp |
|---|---|---|---|
| `dse~AgentIvyLink` | 1 | url-encoded | `2026-06-01T15:54:26Z` |
| `dse~AgentDataUsaUnique5` | 1 | url-encoded | `2026-06-01T16:03:04Z` |
| `dse~AgentIvyTuitionValues2015XQ` | 15 | url-encoded | `2026-06-01T16:14:15Z` |
| `dse~DataUSAIvyTuitionSequenceCollab2027` *(anchor itself)* | 20 | plain | `2026-06-16T19:47:51Z` |

Excluding the anchor page itself: **3 distinct non-anchor pages, 17 non-anchor revisions** (the 15 revisions on `AgentIvyTuitionValues2015XQ` represent that single page evolving over time, not 15 separate unrelated pages).

---

## 6. Direct Comparison: PROP-10 Precedent vs. PROP-61 Pattern

The PROP-10 reasoning (from `audit/A11_CONTEXT_RECONCILIATION.md` §3.4, verbatim):

> Both our independent search and Sam's draft identified that the API documentation URLs in `PROP-20260616-10` appear verbatim on dozens of unrelated bridge pages across the DSE corpus (e.g. `dse~DataUSAQueryBridgeFeb03Poverty1@1`). **Disposition:** We confirm Sam's recommendation: **exclude these matches from occurrences**. The text is generic platform endpoint boilerplate. Elevating generic URLs to cross-title coordination mirrors would cause artificial evidence inflation, violating rubric rules.

Side-by-side comparison:

| Dimension | PROP-10 (excluded as boilerplate) | PROP-61 (this check) |
|---|---|---|
| Distinct non-anchor pages with sequence | **Dozens** | **3** |
| Pages described as "unrelated" | Yes — generic bridge/poverty/query pages on different topics | No — all Ivy/tuition/DataUSA-specific by name and content |
| Page naming pattern | Generic (`DataUSAQueryBridgeFeb03Poverty1`, etc.) | Specific (`AgentIvyLink`, `AgentIvyTuitionValues2015XQ`, `AgentDataUsaUnique5`) |
| Content character | Generic platform URL boilerplate reused across unrelated tasks | Specific parametric API queries for exactly `University:107327,199333,198321` |
| Candidate pages contain "Ivy" or "Tuition" in name | No | Yes (2 of 3) |

**The PROP-10 precedent does not straightforwardly transfer to PROP-61.** The distinguishing factual elements are:
1. Scale: 3 specific pages vs. dozens.
2. Relatedness: all 3 non-anchor pages are Ivy/tuition-task-specific; PROP-10's matches were on unrelated bridge pages.
3. Content specificity: the query strings in the 3 candidates are parametric API calls for exactly the same institution IDs — not generic platform boilerplate.

Whether this constitutes sufficient groundability for a context fragment, or whether 3 candidates with the same sequence still introduces too much ambiguity to pin a single "older Ivy helper page," is a substantive annotation judgment — not resolved here.

---

## 7. Summary of Factual Confirmations

All of 0geder's specific factual claims were independently confirmed from scratch:

| Claim | Our independent result |
|---|---|
| ID sequence appears in anchor quotation (plain form) | **CONFIRMED** |
| All 3 candidate hashes match raw export's `body_sha256` | **CONFIRMED** (all three recomputed independently) |
| All 3 candidates predate anchor by 2+ weeks | **CONFIRMED** (`2026-06-01` vs. `2026-06-16`, ~15 days) |
| `AgentIvyTuitionValues2015XQ@1` body is 665 bytes | **CONFIRMED** |
| `AgentIvyTuitionValues2015XQ@1` hash = `dd3bbb36...` | **CONFIRMED** (recomputed, not copied from audit doc) |
| `AgentIvyTuitionValues2015XQ@1` span `[56, 248]` cleanly captures full API URL | **CONFIRMED** (exact slice verified) |
| §4.2's "no verifiable character span or revision ID can be grounded" is factually incorrect | **CONFIRMED** — grounded, timestamped, hash-verified candidate spans exist in the corpus |

The full corpus scan confirms the sequence appears on exactly **3 non-anchor pages** total, not "dozens" — demonstrating that the PROP-10 boilerplate-exclusion rationale does not apply on the factual record.

---

## 8. Adjudication Status

**This document is verification only. No files were edited.**

- `annotations/context_eligibility.jsonl` — **unchanged**
- `annotations/context_fragments.jsonl` — **unchanged**

`PROP-20260616-61` remains in its current state: `context_needed: true, anchor_self_contained: false, context_fragment_ids: []`.

The substantive question — whether `dse~AgentIvyTuitionValues2015XQ@1` (or one of the other two candidates) should be grounded as the context fragment, or whether the 3-candidate situation still constitutes unresolvable ambiguity requiring the gap designation to stand — is **flagged for Aaron/Jaswin adjudication** per project process. No annotation-team member should resolve this unilaterally. The adjudication should consider:

1. Whether the plain/URL-encoded form difference between the anchor and candidates is material.
2. Whether `AgentIvyTuitionValues2015XQ@1` is sufficiently specific to be "the" page the agent meant, given two additional candidates exist.
3. Whether independently verified span `[56, 248]` on `AgentIvyTuitionValues2015XQ@1` (which captures the exact query URL) is the correct grounding span, or whether a different span is more appropriate.
4. Whether grounding any of the three constitutes genuinely interpretive context (permitted) vs. corroboration of the agent's historical knowledge (out of scope per epistemic-tier discipline, as established for `PROP-20260617-19`).
