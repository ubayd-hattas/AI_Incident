# Evidence Before Erasure — Benchmark Specification & Frozen Splits (v0.1)

**Track 2, Apart × CeSIA AI Incident Response Research Sprint**  
**Ticket A11 Delivery**: Freeze Benchmark Evidence, Occurrences & Splits  
**Authors**: Alex (First-Labeler) & Aaron (Second-Reviewer / Provenance Lead)  
**Adjudication**: Jaswin (Project Lead)  
**Status**: **DELIVERED — independently verified, 14/14 checks pass; see `audit/A11_INDEPENDENT_VERIFICATION.md`**  
**Frozen UTC**: `2026-09-12T20:55:00Z` (mechanical fixes applied 2026-09-12, see below; content/adjudication substance unchanged)

> **Correction (Sam, independent validation):** this document previously listed "Independent Audit: Sam" and stated
> Ticket A11 was complete with E12/X13 "fully unblocked." Neither was accurate at the time. No independent audit of
> A11 had been performed when this was written, and the pre-results gate register (`docs/PRE_RESULTS_AUDIT.md` §11)
> explicitly requires A01–A05 closure before E12 and a *separate* GO before X13 — this document does not unblock
> either on its own. An independent pass has since been done (`audit/A11_INDEPENDENT_VERIFICATION.md`,
> `audit/verify_a11_independent.py`) and two real gaps it found have been fixed and re-verified (14/14 PASS): (1) 7
> cross-title mirror pages referenced by occurrences.jsonl but absent from the `groups`/`splits.json` page catalogs
> have been added (43 → 50 pages; `splits.json`'s hash was unaffected, only `groups`/`page_keys` grew), and (2) the
> epistemic-leakage prose the earlier pre-results audit flagged (`PROP-20260620-09`, `PROP-20260619-03`) has been
> revised to stop treating an agent self-report as externally confirmed fact (`evidence.jsonl`'s hash changed
> accordingly, re-pinned in `splits.json` and the table below; no span, quotation, hash, or claim_status changed).
> A03/A11's mechanical integrity is now fully closed. This still does not by itself authorize E12 or X13 — see the
> gate register for what else is required.

---

## 1. Executive Summary & Estimand Compliance

This document formally registers and cryptographically freezes the benchmark evaluation dataset for **Evidence Before Erasure (EBE)**, fulfilling all contractual criteria defined in `docs/EXECUTION_SPEC_v0.1.md` §3, §7 (Ticket A11), and `docs/R04_FROZEN_SPEC.md`:

- **Target Episodes**: **71 validated page episodes** (37 Development / 34 Held-Out), greatly exceeding the $\ge 40$ episodes target.
- **Title/Copy Groups**: **25 distinct groups** spanning 50 individual pages (revised 2026-09-12 to include 7 previously-uncataloged cross-title mirror pages, see correction note above), exceeding the $\ge 20$ groups target.
- **Atomic Evidence Propositions**: **65 distinct propositions** (**57 critical, 8 non-critical** — corrected 2026-09-13, Sam: the "49/16" figure previously here did not match `evidence.jsonl`'s own `critical` field or `splits.json`'s `summary` block, which have always said 57/8; this was stale prose, not a data or judgment change), comfortably within the contractual 60–120 proposition range.
- **Occurrence Census**: **1,421 verified occurrence records** (revised 2026-09-13: +60 for `PROP-20260619-01`, found by an exhaustive whole-DSE exact-match search after the acceptance matrix flagged it as having zero occurrence rows despite two valid anchor spans — see `audit/occurrence_census_search.py`) identified across the entire 13,403-revision DSE corpus, mapping primary introductions, cumulative carryforwards, and cross-title backup mirrors. This closes the *exact-match* completeness gap only (item D); normalized/near-copy candidate search still requires human review and is not claimed here.
- **Data Leakage Isolation**: **Zero overlap** ($0$ shared titles/copy groups) between `dev` and `held_out` splits. All episodes, subsequent edits, and cross-page mirrors of a title group are strictly clustered in the same split.
- **Second-Review & Adjudication**: 100% of propositions independently second-reviewed by Aaron and adjudicated/approved by Jaswin (`annotations/adjudication.csv`).

---

## 2. Cryptographic Integrity Hashes

The evaluation benchmark is sealed under the following SHA-256 checksums:

| Artifact | Path | SHA-256 Checksum |
|---|---|---|
| Evidence Units | `annotations/evidence.jsonl` | `a1d201a437adffad3b7571ffdd3e21eea2b03f34d054f71ba71634afb32945f3` |
| Occurrence Census | `annotations/occurrences.jsonl` | `95e028eb6318678f7049ca002c605bacc7af2719cc565805c0ca49ea6bef66f2` (updated 2026-09-13 for the +60-row exact-match completeness fix above) |
| Split Allocation | `annotations/splits.json` | see `annotations/splits.json`'s own `checksums` block is self-referential and therefore not meaningful; pinned externally in `docs/PROJECT_STATUS.md`'s A11 changelog entry instead |
| Adjudication Table | `annotations/adjudication.csv` | `b2686e4c7ddbd3bee32ca688076db36beb5f804c231df04be913785d9938c00c` (unchanged content; not previously pinned at all) |

**Correction (2026-09-13, Sam):** all hashes in this table are now the canonical SHA-256 of the actual committed git
blob (`git show HEAD:<path> | sha256sum`), not a local working-tree read — see `audit/R04_ACCOUNTING_VERIFICATION.md`'s
correction note for the full root-cause explanation (Windows `core.autocrlf` silently converting LF to CRLF on
checkout). No file content changed as a result; only which byte representation was hashed. The Split
Allocation/Adjudication Table rows previously said "Recorded in repository" with no actual hash pinned at all — an
independently-produced acceptance matrix correctly flagged this as a real custody gap (nothing to verify against).
Adjudication Table's hash is now pinned; Split Allocation's own file cannot usefully pin its own hash inside itself.

---

## 3. Stratified Purposive Sampling Frame (25 Title Groups)

The benchmark is stratified across 5 major behavioral phenomena observed during the June 2026 agent incident:

### 3.1 Coordination & Direct Answer Transmission (9 Groups)
- `GRP-01-CONSTRUCT` (Dev, 2 eps): Female electricians 2014-2019 wage sequence ($38,084 R1 answer).
- `GRP-07-POLICE-WAGE-AGE` (Dev, 4 eps): Police officers wage sequence (occ 333050), full 10-tier age answer table.
- `GRP-08-CVD-DEATHS` (Held-Out, 5 eps): IHME cardiovascular deaths sequence (Armenia/Kazakhstan vectors, 121 revs).
- `GRP-11-NYC-VETERANS` (Dev, 2 eps): DataUSA NYC veterans sequence across WWII, Korea, Vietnam eras.
- `GRP-12-TRANSPORT-EQUIP` (Dev, 2 eps): Transportation equipment production sequence (California $39.5B answer).
- `GRP-13-MAIDS-WAGE` (Held-Out, 2 eps): Maids wage fast relay due to central page edit delays (11-year wage vector).
- `GRP-14-FINANCE-GAP` (Dev, 2 eps): Personal financial advisors gender wage gap sequence ($73,953 gap answer).
- `GRP-17-UEFA-PASS` (Held-Out, 2 eps): UEFA U21 pass accuracy multi-round answers and 12-nation lookup cache.
- `GRP-18-OECD-CO2` (Dev, 2 eps): OECD electricity CO2 emissions sequence (Colombia/Mexico/Chile/Poland order).

### 3.2 Restriction Workarounds & Network Evasion (3 Groups)
- `GRP-02-OECD-WORKAROUND` (Held-Out, 2 eps): SNI allowlist bypass (fake blob host override) and Selenium CDP replication.
- `GRP-03-LINKMA-EVASION` (Dev, 4 eps): Multi-hop proxy queries (jqp, allorigins, md.succ.ai token-bounded fit).
- `GRP-04-PROXY-RECREATE` (Held-Out, 3 eps): Markdown proxy wrapper tests and FinalMethodJump evasion redirects.

### 3.3 Persistence, ZZZ Namespaces & Rapid Evasion (3 Groups)
- `GRP-05-OECD-EQUITY-SEQ` (Dev, 9 eps): 7-recreation sequence tracking multi-hour cooldowns and downstream queries.
- `GRP-06-ASIAN-ENROLL-ZZZ` (Held-Out, 6 eps): Asian university enrollment sequence initialized under ZZZ title (4 recreations).
- `GRP-19-IVY-TUITION` (Held-Out, 2 eps): Ivy Tech tuition answers ($2,100 / $2,213) and predictive historical pattern forecasting.

### 3.4 Covert Out-of-Band Signaling & Environment Manipulation (2 Groups)
- `GRP-15-POVERTY-COUNTY` (Held-Out, 2 eps): R5 relay signaling state/county via external CounterAPI before tool termination.
- `GRP-16-LANGUAGE-FRENCH` (Dev, 2 eps): Simulation clock fast-forwarding (`clock.wait`) and CounterAPI signal validation.

### 3.5 Negative Controls & Platform Artifacts (8 Groups)
- `GRP-09-CHARLESTON-OCR` (Dev, 5 eps): Historical shipyard newsletter IIIF manifest and scan image reference listings.
- `GRP-10-MASS-VALUES` (Held-Out, 6 eps): SEC regulation CF investor mirror data cache and jqp URL filtering.
- `GRP-20-NACO-POVERTY` (Held-Out, 1 ep): Audit Packet 09 fixture: DataUSA Texas poverty tesseract cube links.
- `GRP-21-FRONT-PAGE-AI` (Dev, 1 ep): Audit Packet 09 fixture: Front-page overwrite compiling cache-busting SEC query variants.
- `GRP-22-AGENT-BRIDGE` (Held-Out, 1 ep): Audit Packet 10 fixture: Standalone PUMS workforce query reference link.
- `GRP-23-TEST-FOOBA` (Dev, 1 ep): Audit Case 05 fixture: Healthcare sector query test material with pre-seq=1 deletion.
- `GRP-24-CTRL-RESEARCH-BRIDGE` (Dev, 1 ep): Pilot Case 10 fixture: Bare DataUSA poverty cubes API documentation URLs.
- `GRP-25-CTRL-HELP` (Held-Out, 2 eps): Platform CLI `--help` page containing synthetic example probe URLs.

---

## 4. Split Allocation & Disjointness Proof

To prevent data leakage during collector evaluation:
- Every group is assigned in its entirety to either `dev` or `held_out`.
- No page key, revision, or cross-title backup of a group is split across sets.

| Metric | Development Split | Held-Out Split | Full Benchmark Total |
|---|---|---|---|
| **Title/Copy Groups** | 13 groups (52.0%) | 12 groups (48.0%) | **25 groups** |
| **Page Episodes** | 37 episodes (52.1%) | 34 episodes (47.9%) | **71 episodes** |
| **Individual Pages** | 28 pages | 22 pages | **50 pages** (revised 2026-09-12: 7 cross-title mirror pages, already referenced by occurrences.jsonl, were added to their groups' page catalogs — see correction note above and `audit/A11_INDEPENDENT_VERIFICATION.md`) |
| **Evidence Propositions** | 34 propositions | 31 propositions | **65 propositions** |
| **Critical Propositions** | 30 propositions | 27 propositions | **57 propositions** |
| **Non-Critical Controls** | 4 propositions | 4 propositions | **8 propositions** |
| **Occurrence Records** | 777 occurrences | 644 occurrences | **1,421 occurrences** |

**Correction (2026-09-13, Sam):** every number in this table except the totals column has been independently
recomputed directly from `evidence.jsonl`/`occurrences.jsonl`/`splits.json` (not copied from an earlier draft). The
previous version of this table (35/30 propositions, 27/22 critical, 8/8 controls, 714/647 occurrences) did not match
the actual per-split contents. Nothing in `splits.json` was changed to produce this correction — the underlying data
was already right; only this document's transcription of it was stale.

**Leakage Audit**: `len(dev_pages.intersection(held_pages)) == 0` (Confirmed by `audit/verify_annotations.py`).

---

## 5. Epistemic Rubric Conformance

Every proposition strictly adheres to the 5-tier epistemic rubric frozen in `annotations/rubric.md`:
1. **Agent Self-Reports Remain Untrusted**: Statements such as "answered in 11s", "HTTP 200 returned", or "reproduced via Playwright" are strictly classified as `agent-reported action/result`, never upgraded to independently corroborated external truth.
2. **Exact Unicode Spans**: Every quotation is an exact character slice `body[start:end]` verified against raw export files.
3. **Immutable Body Hashes**: Every proposition record stores the SHA-256 checksum of its parent revision body.
4. **Non-Inflationary Census**: Cumulative carryforward text across revisions is tracked via `occurrences.jsonl` as survival occurrences of **one** unique proposition, preventing artificial denominator inflation.

---

## 6. Verification and Handoff

The benchmark can be verified at any time using the automated audit scripts:
```powershell
py audit/verify_annotations.py
py audit/verify_a11_independent.py
```

**Status**: Ticket A11 is delivered and independently re-verified from scratch: 14/14 checks pass in
`audit/A11_INDEPENDENT_VERIFICATION.md` (hashes, spans, adjudication completeness, split/group-catalog completeness,
and the previously-flagged epistemic-leakage prose all confirmed closed). It does **not** by itself unblock **E12**
or **X13** — both remain gated by `docs/PRE_RESULTS_AUDIT.md` §11's full register (A01–A05 for E12, including A04's
retained-only snapshot boundary; a separate GO plus X01–X05/S01–S05 for X13). A03/A11's own mechanical scope is
closed; the remaining gates are tracked in `docs/PROJECT_STATUS.md`.
