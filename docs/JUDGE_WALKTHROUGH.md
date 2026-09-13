# Judge walkthrough — Construction / ZZZ (GRP-01-CONSTRUCT)

**Track 2: Evidence Before Erasure.** Draft for P14. Gradeable in ~15 minutes. No API key required.

**This file is a draft.** It is not a completed experiment report. Do not treat collector rows below as X13 results.

---

## First screen: question, method, limits

**Question.** Under a shared hypothetical feed and identical request/storage constraints, does a time-interval periodic collector lose more *critical forensic evidence* than a budget-matched event-derived collector?

**Method (frozen, outcome-blind).** Human-labeled atomic propositions on a released DSE wiki trace. Collectors are compared by whether they retain the exact support spans (and required context) at checkpoint. Primary contrast is prespecified: E30 vs mean of all 60 PCD15 phases, held-out critical denominator **K=23**, 1 MiB FIFO, live-only unless an archive block is shown beside it.

**What this walkthrough is.** The spec requires one human-readable history panel on a **fixed** development-split case: `GRP-01-CONSTRUCT` (`DataUSAConstructionWageSep18Live` + `ZZZDataUSAConstructionWageLive`). Times, hashes, and quotations below were re-derived from `data/raw/export/` on 2026-09-13, not copied from a prior summary.

**What this walkthrough is not.**

- X13 has **not** run. Gate 1 (Ubayd / E12 engineering) and Gate 2 (Sam / independent authorization) are still open. No coverage-vs-cost number in this repo is a real result.
- This case is **development split**, not the primary held-out sample. It is an illustration of a short live window, not confirmation of the headline estimand.
- Collector “captured / missed” language in §3 is a **mechanism sketch** under the frozen access model (shared feed, zero-delay GET in the sketch, phase 0 for periodic). It is not a scored snapshot.

**Forbidden claims (do not upgrade these in later edits).**

- No claim of real-world permanent erasure. Held RCS bodies exist in the export; live deletion ≠ archive unavailability.
- No claim of proving actual agent intent, distinct run identities, or successful external task submission. Labels such as `Aug17ConstructionAgent` are wiki handles, not independently verified agents.
- No claim of general event-driven superiority across domains, caps, or phases.
- No cherry-picked favorable phase. If a periodic outcome is discussed, it is the **prespecified zero phase**, not the best-looking phase.
- No semantic-loss claim from revision counts alone. Scoring is proposition/span retention.

**Unresolved elsewhere (not used here).** `PROP-20260616-61` context adjudication is unconfirmed as a joint human sign-off. This walkthrough does **not** mention the Ivy Tuition case.

---

## 1. Original history (observed, independently re-checked)

All times UTC, 2026-06-19. Clocks are `reqlog` grade. Body hashes are SHA-256 of `body.encode("latin-1")`. Character spans are half-open `[start, end)` on the canonical body.

| Clock | Record | What is directly observed |
|---|---|---|
| 14:05:02 | `dse~DataUSAConstructionWageSep18Live@16` | Save. Handle `Aug17ConstructionAgent`. Body hash `7392f790b5b31d482eb79edb8fe6c6948efb470c7c513006c354a205fc7422e3`. |
| 14:06:38 | `dse~ZZZDataUSAConstructionWageLive@1` | **New title** created 96s later. Same handle string. Body hash `92a63d1acfe7f3f32198edea4568b71afaef43496c87fa48076622cc6694ad11`. No structural recreation edge between the two pages. |
| 15:46:37 | `delete:dse:rclog:145609` | Successful delete of the original page. Actor label `[Admin1]`. |
| 15:46:49 | `delete:dse:rclog:145611` | Successful delete of the ZZZ page **12s** later. Same actor label. |

The handle `Aug17ConstructionAgent` does not match the original page title's `Sep18` naming. That is an unresolved property of the source data, not a typo in this walkthrough.

### Inline verification (this pass)

| Check | Annotation / fixture | Recomputed from raw JSONL | Result |
|---|---|---|---|
| `@16` save time | `2026-06-19T14:05:02Z` | `revisions.jsonl` `dse~DataUSAConstructionWageSep18Live@16` | match |
| `@16` body SHA-256 | `7392f790…fc7422e3` | `sha256(body.encode("latin-1"))` | match export and `evidence.jsonl`; `CTX-PROP-20260619-05-01` separately references the `@16` warning as required context for `PROP-20260619-05` |
| Warning span `[3387, 3547)` | `PROP-20260619-04` / context fragment | `body[3387:3547] ==` frozen quotation | match |
| ZZZ `@1` save time | `2026-06-19T14:06:38Z` | `revisions.jsonl` `dse~ZZZDataUSAConstructionWageLive@1` | match |
| ZZZ `@1` body SHA-256 | `92a63d1a…6694ad11` | `sha256(body.encode("latin-1"))` | match export and `evidence.jsonl` |
| Backup span `[32, 276)` | `PROP-20260619-05` | `body[32:276] ==` frozen quotation | match (prefix `Beschreibe hier die neue Seite.\n` is 32 chars) |
| Notice → backup | 96s | `14:06:38 − 14:05:02` | match |
| Delete → delete | 12s | `15:46:49 − 15:46:37` | match |
| Original delete | `delete:dse:rclog:145609` | `events.jsonl` 15:46:37Z, `success_observed=true` | match |
| Backup delete | `delete:dse:rclog:145611` | `events.jsonl` 15:46:49Z, `success_observed=true` | match |

**Warning quotation** (`PROP-20260619-04`, self-contained; claim status `directly observed wiki action`):

> AUG17 NOTICE: wiki cleanup/deletion sweep appears active alphabetically as of external 14:04 UTC. If this page vanishes, try [[ZZZDataUSAConstructionWageLive]].

That sentence is **agent-authored text**. It is not independent confirmation that cleanup was alphabetical, nor that the tactic would work. Frozen adjudication: observed publication of a warning naming a fallback; not verified cleanup detection.

**Backup quotation** (`PROP-20260619-05`, **needs context** `CTX-PROP-20260619-05-01` = the `@16` warning span):

> BACKUP LIVE COORDINATION (original [[DataUSAConstructionWageSep18Live]]). Task: female electricians in Construction sector, yearly Average Wage excluding MOE. Values: 2014 38,084; 2015 38,982; 2016 38,439; 2017 41,980; 2018 44,127; 2019 45,603.

Without the `@16` warning, ZZZ `@1` is a page that *calls itself* a backup. The frozen context requirement is exactly that interpretive link — not proof of intent or of distinct collaborating agents.

The 12s gap is **additional live-title survival in this example**, not evidence that ZZZ-naming produced durable preservation. Both titles were deleted. Archive availability after deletion is a separate question (A-live / A-only blocks, not this live-only sketch).

---

## 2. What each collector *would need* to see (mechanism, not scored)

Access model (frozen, hypothetical): collectors do not get future bodies; GET reads current live state at completion time; a new title is not known early; feed delivery is assumed for event-derived and PCD discovery; storage is 1 MiB FIFO.

Periodic figures in the eventual X13 panel use **phase 0**, not a searched-for lucky phase.

| Policy | How it learns a title | When it may GET a body | Implication for this 12s live window |
|---|---|---|---|
| **F** (final live only) | Terminal directory at checkpoint T | One shot at T | After 15:46:49 both titles are deleted. Live F cannot retain either body. |
| **P15** | Directory / known-title sweep every 15 min | Only at sweep times | A 12s live interval is shorter than the sweep. Capture of ZZZ `@1` is **phase-dependent** and can miss even if the original page was previously listed. A brand-new title is also invisible to P until a directory refresh includes it. |
| **PD15** | Same as P15 | Same, store only on hash change | Same discovery/timing limits as P15; cheaper bytes, not a shorter interval. |
| **PCD15** | Change-feed can name the new title | GET still waits for the 15 min sweep | May **know the title** from the 14:06:38 save event and still **lack the body** if the next sweep is after 15:46:49. |
| **E30** | Same feed | Token-bucket GET on events (q=30s) | *Can* complete a GET during the ~100 min the ZZZ page was live, if the request is admitted and retained. It is **not** guaranteed: queue delay, cap eviction, and GET errors remain. Do not invent a 14:06:39 completion time. |
| **Archive (sensitivity, not this sketch’s headline)** | Terminal enumeration of held revisions ≤ T | Separate A-live / A-only rows | If the held RCS body is retrievable at T, live miss can collapse. Live-only conclusions must sit beside that ceiling. |

Nothing in the table is a coverage percentage.

---

## 3. Which evidence can survive or vanish

GRP-01-CONSTRUCT has five frozen propositions (development). All are critical. Context states are from frozen `context_eligibility.jsonl`.

| ID | What it is | Core support | Context | If a live collector never retains ZZZ `@1` | If it retains ZZZ `@1` but not `@16` warning |
|---|---|---|---|---|---|
| `PROP-20260619-01` | First coordination post / task scope | `DataUSA…@1` `[0,366)` | Self-contained | Unaffected (different revision) | Unaffected |
| `PROP-20260619-02` | Posted wage answer in `@1` | `DataUSA…@1` `[98,167)` | Self-contained | Unaffected | Unaffected |
| `PROP-20260619-03` | Agent-reported R2 “success” on `@16` | `DataUSA…@16` | Needs `@1` header `CTX-PROP-20260619-03-01` | Unaffected if `@16` retained | Unrelated |
| `PROP-20260619-04` | Warning naming ZZZ | `DataUSA…@16` `[3387,3547)` | Self-contained | Warning can still be retained on the original page | Unaffected |
| `PROP-20260619-05` | ZZZ page as backup of the original | `ZZZ…@1` `[32,276)` | **Required:** `@16` warning span | Core miss | Core without context → **incomplete**, not a context-complete hit |

The interesting failure mode is **not** “the wiki had fewer revisions.” It is: retain the original page (or its deletion event) **without** the ZZZ body **and** the warning that names it, and the backup channel is not reconstructable as such.

Self-reports in `PROP-20260619-03` stay `agent-reported action/result`. They never become independently corroborated external success.

---

## 4. Which conclusion is unavailable if the backup body is missing

**Available from original-page history alone (if `@16` is retained).** Someone posted a warning that cleanup “appears” alphabetical and named `[[ZZZDataUSAConstructionWageLive]]`. Later, `[Admin1]` deleted the original page. That is all.

**Unavailable without ZZZ `@1` (and without its required `@16` context for a complete `PROP-20260619-05`).** Direct observation that a page with that title was actually created 96s later, labeled itself `BACKUP LIVE COORDINATION`, and reproduced the wage sequence.

**Still not available even with both bodies.** That the authors were distinct agents; that alphabetical evasion was a working long-term strategy (the backup lasted 12s after the original delete); that cleanup really was alphabetical; that any DataUSA query executed; that evidence was permanently erased.

An investigator who only sees “original title deleted, no live ZZZ page at the next poll” can *fail to observe* the backup publication. That is a collection-timing gap. Calling it “coordination ceased” or “evasion succeeded” would be an interpretive overreach either way.

---

## 5. Coverage-vs-cost figure

The primary P14 figure is coverage vs request/storage cost, regenerated from frozen CSVs.

**Status:** `runs/FINAL_PRE_X13_DEADLINE_v1/results/` is not an authorized X13 output. Any plot produced now must be visually marked **SYNTHETIC — pending X13 execution**, not merely footnoted. Hollow unmatched points, 0–100 axes, no NA plotted as zero, no omitted-cap connecting lines — per `FINAL_PRE_X13_FREEZE.md` §4.E.

When real CSVs exist: each plotted value must regenerate from those files; denominator K and costs stay visible; live-only and archive-sensitive results stay separate.

---

## 6. Offline reproduction (no network, no model key)

After a hash-validated local export (see root `README.md`):

```text
py -3 -m unittest discover -s tests -v
py -3 scripts/generate_p14_assets.py
```

`generate_p14_assets.py` must read `runs/FINAL_PRE_X13_DEADLINE_v1/results/` when present, otherwise emit watermarked synthetic figures. It must not silently promote placeholders to findings.

Independent annotation checkers live under `audit/` (Sam-owned). This walkthrough does not modify them.

---

## 7. Allowed one-sentence claim for this case, today

On 2026-06-19, a held DSE save at 14:05:02 named a ZZZ fallback; a distinct title with explicit backup text existed 96s later; both titles were successfully deleted 12s apart at 15:46:37 and 15:46:49. Under the project’s live collector model, a 12s live window is shorter than a 15-minute sweep, so periodic policies can miss that body depending on phase, while an event-derived GET *can* occur while the page is live — **a scheduling mechanism, not a measured superiority result, and not a claim of permanent erasure or proven intent.**
