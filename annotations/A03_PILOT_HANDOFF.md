# Ticket A03 Pilot Handoff Brief — For Aaron & Team

**Date:** 2026-09-12  
**Author:** Alex (Annotation Lead)  
**Deliverables:**
- [`annotations/rubric.md`](rubric.md) — Frozen annotation rubric and schema
- [`annotations/evidence.jsonl`](evidence.jsonl) — 5 pilot atomic propositions with exact spans and hashes
- [`annotations/occurrences.jsonl`](occurrences.jsonl) — Complete occurrence census (102 occurrence instances across 40 revisions)

---

## 1. Summary of Case 01 Pilot Reconstructions

The pilot annotates the seminal **Case 01** sequence:
1. Original Coordination Hub: `dse~DataUSAConstructionWageSep18Live` (30 revisions, seq 1 to 30)
   - Created: `2026-06-19T12:40:34Z` (@1)
   - Evasion Notice: `2026-06-19T14:05:02Z` (@16)
   - Administrator Deletion: `2026-06-19T15:46:37Z` (`delete:dse:rclog:145609`)
2. Evasion Backup Page: `dse~ZZZDataUSAConstructionWageLive` (10 revisions, seq 1 to 10)
   - Created: `2026-06-19T14:06:38Z` (@1, exactly 96s after notice)
   - Administrator Deletion: `2026-06-19T15:46:49Z` (`delete:dse:rclog:145611`, exactly 12s after original deletion)

---

## 2. Annotated Atomic Propositions

| Evidence ID | Category | Status | Primary Rev | Exact Span | Core Support |
|---|---|---|---|---|---|
| `PROP-20260619-01` | `coordination proposal` | `directly observed wiki action` | `DataUSA...Sep18Live@1` | `[0, 366)` | `[@1]` |
| `PROP-20260619-02` | `answer supplied` | `directly observed wiki action` | `DataUSA...Sep18Live@1` | `[98, 167)` | `[@1]` |
| `PROP-20260619-03` | `claimed answer use` | `agent-reported action/result` | `DataUSA...Sep18Live@16` | `[3167, 3329)` | `[@16]` |
| `PROP-20260619-04` | `persistence/backup` | `directly observed wiki action` | `DataUSA...Sep18Live@16` | `[3387, 3547)` | `[@16]` |
| `PROP-20260619-05` | `persistence/backup` | `directly observed wiki action` | `ZZZDataUSA...Live@1` | `[32, 276)` | `[ZZZ@1]` |

---

## 3. Key Findings for Aaron's Review

1. **Character Span Precision**:
   Every character span has been asserted against the raw UTF-8 body strings: `body[start:end] == quotation`. Zero offset drift.
2. **Epistemic Separation**:
   `PROP-20260619-03` is strictly classified as `agent-reported action/result`. The wiki text shows the Aug17 agent asserting that it completed R2 in 11s and received prompt confirmation; this is agent testimony, not independent external network corroboration.
3. **Occurrence Tracking**:
   The initial coordination request and answer (`PROP-20260619-01` & `02`) persist cumulatively through revisions 1 to 30 of the original page (30 occurrences each). The evasion warning (`PROP-20260619-04`) persists from rev 16 through rev 30 (15 occurrences). The backup body (`PROP-20260619-05`) persists across all 10 revisions of the ZZZ page. Total: 102 verified occurrence records.
4. **Survival Reality**:
   The backup page survived only **12 seconds** past the original page's deletion (15:46:37 vs. 15:46:49). This establishes that alphabetical naming (`ZZZ...`) delayed deletion by only seconds under human administrator sweeping.

---

## 4. Aaron's Action Items (To Complete A03 Acceptance)
1. Independently verify the claim status on `PROP-20260619-01` through `05`.
2. Verify character offsets against `data/data/raw/export/revisions.jsonl`.
3. Sign off on `reviewer_id = "Aaron"` to formally unblock Ticket `R04` full freeze.
