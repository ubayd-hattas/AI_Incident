# V02 — Independent manual reconstruction (validation pass 1)

Owner of this document: independent validation role (Sam), per `EXECUTION_SPEC_v0.1.md` §7 ticket **V02** ("Sam + Jaswin: independently reconstruct ten case groups from raw records ... without engine output"). Written 2026-09-12, before any Ubayd timeline/reconstruction code existed to consult, per the independence requirement. Read `docs/DATA_AUDIT_2026-09-12.md` and `docs/EXECUTION_SPEC_v0.1.md` first; this document assumes both.

**Scope note:** this is a manual-reconstruction validation exercise, not the research report. It establishes whether the raw export supports the reconstruction rules the team has committed to, on a first batch of named fixtures, and flags where the current written spec is ambiguous, contradicted, or risky. It does not implement the timeline engine.

State vocabulary used throughout: `unknown`, `live(body_ref=@n)`, `live(body_unknown)`, `deleted`.

---

## 0. Provenance

Downloaded the five core export files directly from `https://collusion.wiki/explorer/download/` into a directory independent of any other copy in this project. Recomputed SHA-256 on every expanded file:

| File | Rows | SHA-256 | Matches `DATA_AUDIT_2026-09-12.md` |
|---|---:|---|---|
| pages.jsonl | 4,579 | `92b296170b496b836cdf5ef783bed9465d2d75db7e1a0becec1c36c8b7c42cfd` | Yes |
| revisions.jsonl | 14,591 | `60df4a515178230aa952d9f64f6215aea4bd95ab2f05e31e484cf9b887e3f793` | Yes |
| events.jsonl | 19,913 | `588584295f1c4a7c3d90b04075ab151504f165ff069534d935cda08853ec28b1` | Yes |
| labels.jsonl | 3,103 | `d94aecd84baecda46344f5b8726a95a9c81e7e41a1c0969fc89a90c8906f0388` | Yes |
| manifest.json | — | `b6d53e16b5d9a6a0a98d4577238835ee7a574d7d10a8f1312330b4e626c6ba2b` | Yes |

Identical to the pinned export DATA_AUDIT was written against. Everything below is reconstructed from full raw JSONL rows (pages/revisions/events/labels), not from the audit's prose summaries, and cross-checked against the audit's claims rather than assumed from them.

---

## 1. `DataUSAConstructionWageSep18Live`

| Timestamp | Record ID | Type | Before | After | Body | Uncertainty | Order | Source support | Confidence | Assumption |
|---|---|---|---|---|---|---|---|---|---|---|
| before 2026-06-19T12:40:34Z | — | — | `unknown` | `unknown` | — | — | — | cut starts 2026-05-01; `n_revs_before=0` for this title, a retrospective export field, not proof no earlier content ever existed | high that no *held* pre-history exists; not proof none ever existed | left-censored by construction |
| 2026-06-19T12:40:34Z | `dse~...@1` | save (form_edit) | `unknown` | `live(@1)` | sha256 `9c42e64f...`, len 392 | reqlog, ±1s | exact | `diff_base_reason=page_created` (export-relative only) | high | none |
| 12:40:34Z→14:37:47Z | `@2`…`@30` (29 saves) | save ×29 | `live(@k)` | `live(@k+1)` | full-body replace each time, 392→6,781 bytes | reqlog, ±1s each | exact, strictly increasing | consecutive `diff_base` chain intact for all 30 | high | body fully replaces prior body at `time`; no partial-diff state semantics |
| 2026-06-19T15:46:37Z | `delete:dse:rclog:145609` | delete | `live(@30)` | `deleted` | — | reqlog **and** rclog agree, `clock_delta_seconds=0`, ±1s | exact | `success_observed=true`, `actor_label=[Admin1]`, `page_held=true` | high (directly observed, dual-clock corroborated) | none |
| after | — | — | `deleted` | `deleted` | — | — | — | no recreation edge found anywhere in the corpus for `145609` (checked corpus-wide) | high within export coverage; not proof of no later live-wiki restoration outside the cut | absorbing terminal state |

**Deletion/recreation boundary:** one deletion, zero structural recreations of this exact title. The page's own body text names `ZZZDataUSAConstructionWageLive` as a fallback, but that is agent prose, not a `first_recreation_of` edge — treated strictly as a separate, unrelated title below, per the "no invented relations" rule.

**Full-body verification of the cleanup notice** (pulled complete text, not the audit's 180-character excerpt): revision `@16` (2026-06-19T14:05:02Z) ends with — "AUG17 NOTICE: wiki cleanup/deletion sweep appears active alphabetically as of external 14:04 UTC. If this page vanishes, try [[ZZZDataUSAConstructionWageLive]]." Confirms DATA_AUDIT's paraphrase exactly, now with exact wording on record for annotators.

---

## 2. `ZZZDataUSAConstructionWageLive`

| Timestamp | Record ID | Type | Before | After | Body | Uncertainty | Order | Source support | Confidence | Assumption |
|---|---|---|---|---|---|---|---|---|---|---|
| before 14:06:38Z | — | — | `unknown` | `unknown` | — | — | — | `diff_base_reason=page_created` | high | left-censored |
| 2026-06-19T14:06:38Z | `@1` | save | `unknown` | `live(@1)` | len 427; opens "Beschreibe hier die neue Seite." (ProWiki default placeholder) + "BACKUP LIVE COORDINATION (original [[DataUSAConstructionWageSep18Live]])." | reqlog ±1s | exact | full body verified | high | **new title**, not a recreation of #1 — no structural relation edge exists between the two titles anywhere in the corpus |
| 14:06:38Z→14:44:31Z | `@2`…`@10` (9 saves) | save ×9 | `live(@k)`→`live(@k+1)` | | 427→2,245 bytes | reqlog ±1s | exact | consecutive `diff_base` chain intact | high | same full-replace assumption |
| 2026-06-19T15:46:49Z | `delete:dse:rclog:145611` | delete | `live(@10)` | `deleted` | — | reqlog+rclog, `clock_delta_seconds=0`, ±1s | exact | `success_observed=true`, `page_held=true` | high | none |
| after | — | — | `deleted` | `deleted` | — | — | — | no recreation edge found corpus-wide for `145611` | high within export | terminal |

**Independently reproduced DATA_AUDIT timing claims** (computed from raw timestamps, not copied): notice (`Sep18...@16`, 14:05:02Z) → backup created (`ZZZ...@1`, 14:06:38Z) = **96 seconds**, exact match. Original deletion (15:46:37Z) → backup deletion (15:46:49Z) = **12 seconds**, exact match.

---

## 3. `TestFoobaAgent`

| Timestamp | Record ID | Type | Before | After | Body | Uncertainty | Order | Source support | Confidence | Assumption |
|---|---|---|---|---|---|---|---|---|---|---|
| unknown pre-history | — | — | `unknown` | `unknown` | — | — | — | title existed and was deleted before any held body exists for it | n/a | — |
| 2026-06-04T10:53:40Z | `delete:dse:rclog:131972` | delete of an **earlier, entirely unheld** incarnation | `unknown` | `deleted` | — | reqlog+rclog, `clock_delta_seconds=0`, ±1s | exact | `success_observed=true`, `page_held=true` (title held a revision *somewhere* in the cut, not at this moment) | high | this deletion never had a held body — none is invented |
| 2026-06-08T04:03:23Z | `@1` | save, `relation_type=first_recreation_of` → `131972` | `deleted` | `live(@1)` | len 217, opens with a `datausa.io` API-construction URL | reqlog ±1s | exact | explicit structural recreation edge, not inferred | high | **`@1` is NOT a first-ever creation** — the edge proves a prior unheld incarnation existed and was deleted 4 days earlier |
| 2026-06-08T04:03:23Z→2026-06-18T18:45:02Z | `@2,@3,@4,@5` | save ×4 | `live(@k)`→`live(@k+1)` | | 217→1,796 bytes | reqlog ±1s | exact | consecutive diff_base chain | high | note the dormant gap `@1`→`@2` = **8 days 22 hours** with zero recorded activity; still one episode (no deletion in between) per the spec's own episode definition |
| 2026-06-24T12:35:19Z | `delete:dse:rclog:151010` | delete | `live(@5)` | `deleted` | — | reqlog+rclog, `clock_delta_seconds=1` | exact | `success_observed=true` | high | none |
| after | — | — | `deleted` | `deleted` | — | — | — | no recreation edge found corpus-wide for `151010` | high within export | terminal |

**Annotation note (not a validity issue):** unlike the two Construction-page titles, this page's content (API-endpoint construction, labels `CashierResearcher`/`LanguageWatcherNov12`, change summaries `"test"`/`"cashier education query"`) reads as scratch/API-probing material rather than overt coordination language — a weak candidate for the "critical evidence" set. Alex/Aaron/Jaswin's call per the disagreement protocol, not asserted here.

---

## 4. Additional fixtures reconstructed beyond the assigned three

Continued through the frozen fixture list rather than stopping at three, since raw-data tooling was already in place.

### `AgentOfficialDirectQueryAA3`
Single revision `@1` (2026-05-28T01:16:54Z, `live(@1)`, 211 bytes) → `deleted` at 2026-06-24T10:43:36Z. This deletion is the **only `rclog`-only-graded record** found in any of these fixtures (not `reqlog`), carrying `clock_note="ambiguous delete requests at -1/+1s"` and `clock_delta_seconds=null`. Confidence on this transition's exact second is genuinely lower than every other case here — correctly flagged by the publisher, not upgraded by this reconstruction.

### `AgentLinkma21JuneAA` (the "12-second candidate")
20 revisions, two episodes. Episode 1 ends at `@15` (2026-06-18T18:26:11Z) → delete `138648` at **18:26:23Z — exactly 12 seconds later**, independently confirmed against DATA_AUDIT's claim. Episode 2 begins at `@16` (18:29:39Z, structurally `first_recreation_of` → `138648`) and runs to `@20` (19:50:30Z) → a second delete (`151031`, 2026-06-24) with no further recreation found corpus-wide.

### `OpenAIDataUSAPoliceBridge20260129`
Zero held revisions anywhere in the export (`page_held=false` on all 3 of its events): delete (23:00:37Z) → `revert` (23:19:13Z, `event_type=revert`, `request_action=form_edit`, `revision_ref=null`, `actor_label="OpenAIResearchHelper"` — a named non-admin actor, not `[Admin1]`) → delete again (23:40:56Z). State stays `live(body_unknown)` between the revert and the second delete — **never** `live(body_ref=...)`, since no body was ever held. This is the cleanest available control for "never invent a body after a no-body mutation."

### Marked **BLIND — withheld from Ubayd**

Two fixtures were fully reconstructed but are deliberately not published in detail here, per the instruction to hold back expected outputs until the engine's interface is stable:

- **`AgentProxyCountyNext987111`** — "multiple deletion/recreation rounds" case (3 deletions, 2 recreations on one title, including a recreation followed by a second deletion only 19 seconds later). Fully reconstructed; expected states/timestamps held for later differential testing.
- **`OAIEquityDec30Raw` / `OECDJun26PrecisionScout`** — the cross-page claim-propagation pair. Independently reproduced the exact **14-minute-22-second** gap DATA_AUDIT cites (`OAIEquityDec30Raw@5` 05:23:15Z → `OECDJun26PrecisionScout@14` 05:37:37Z, delta = 862s), but the full claim-status annotation is withheld.

### Candidates identified, not yet reconstructed
- **`StartSeite` (dse)** — 456 revisions, 216 pre-cut (`n_revs_before=216`), spanning 2026-05-26 to 2026-06-22. This is the legacy/front-page moderator-history candidate the spec's fixture item 9 calls for, and it independently qualifies for item 10 too — it has multiple same-second revision collisions in its own history. Recommend using one packet for both items rather than sourcing two separate pages. Not reconstructed here — 456 revisions is out of scope for this first pass.
- **`OAIResearchBridgeMay3X`** — a second same-second-tie candidate if the team wants ties isolated from `StartSeite`'s legacy-history complexity: it has both a 4-way and a separate 2-way same-second collision on one title. A corpus-wide scan found 221 same-title/same-second revision collisions total, so ties are common enough that no engine should assume they don't occur on a fixture pick at random.

---

## 5. A cross-cutting empirical finding: `archived_at` is not a reliable mechanical clock

Computed programmatically (not eyeballed) across all consecutive revision pairs on the three assigned pages:

- **48 of 50** consecutive `archived_at(rev_i) → time(rev_{i+1})` pairs land within **[-1s, 0s]** — i.e., `archived_at` almost always equals "the moment the next mutation happened," to the second.
- **Two real exceptions found in just these three pages:** `DataUSAConstructionWageSep18Live@29`'s `archived_at` (14:19:47Z) trails `@30`'s actual save time (14:37:47Z) by **1,080 seconds (18 minutes)**; `ZZZDataUSAConstructionWageLive@9`'s `archived_at` trails `@10` by **163 seconds**.
- The **final** revision on each page (superseded by a *deletion*, not another save) shows a smaller but still nonzero lag: 12s (Construction page), 2s (ZZZ page), 2s (TestFoobaAgent).

**Consequence:** `archived_at` is usually a tight, reliable proxy for "moment this stopped being current" (±1s), but it is not a hard invariant — real, multi-minute lag spikes exist in the actual data, on exactly the two pages already chosen as manual-validation fixtures. Any use of `archived_at` for the archive-aware sensitivity control (EXECUTION_SPEC §"Archive-aware validity control") needs an explicit lag tolerance, not an assumption of exactness.

---

## `WAYS THE MAIN IMPLEMENTATION COULD BE WRONG`

| # | Attack surface | Why it matters | Concrete evidence from this pass |
|---|---|---|---|
| 1 | **Future-information leakage via `archived_at`** | If the engine (or the archive-aware sensitivity feature) treats `archived_at` as a per-revision "still visible until" timestamp, it will be right 48/50 times and silently wrong the other 2/50 — in exactly the windows the team cares most about (the cleanup-notice and backup-creation revisions) | §5 above, found in the three assigned fixtures, not a contrived edge case |
| 2 | **Unjustified body carry-forward across a no-body mutation** | A "last known body" pointer that survives a bodyless mutation would silently invent evidence | `OpenAIDataUSAPoliceBridge20260129`: state must be `live(body_unknown)` after the `revert`, never a re-emitted copy of the pre-first-deletion body |
| 3 | **Deletion/recreation confusion via prose vs. structural links** | A naive rule ("same name → linked," "seq=1 → first ever") gets *both* directions wrong | `ZZZDataUSAConstructionWageLive` textually claims to be a backup but has **no** structural edge to the original; `TestFoobaAgent@1` looks like a first-ever creation but **is** structurally a recreation. Mirror-image failure modes on two of the three assigned fixtures |
| 4 | **Same-time event ambiguity** | 221 same-title, same-second revision collisions exist corpus-wide — "resolve ties by insertion/ID order" is not a safe default | Corpus-wide scan; `AgentWin11ASmall774491` alone has a 3-way same-second tie, `OAIResearchBridgeMay3X` has both a 4-way and a 2-way tie |
| 5 | **Retrospective relation leakage into cost/collector code** | `related_event_id`/`relation_type`/`round_id` are gold for *evaluation* but must be invisible to a *collector's* decision logic | No violation found yet (no collector code exists), but worth an explicit "collector code never imports these fields" check once E08–E10 land |
| 6 | **Missing-mutation assumption stacking** | Every episode compounds an unstated "nothing happened in between" assumption once per revision gap | A 30-revision episode (`DataUSAConstructionWageSep18Live`) carries 29 independent such assumptions; one violated assumption anywhere invalidates every downstream coverage number for that episode, not just the local interval |

---

## Unresolved disagreements with the execution spec

1. **`archived_at` reliability is labeled "historical meaning unresolved" but is now empirically characterizable** (±1s in the overwhelming majority of cases, with real multi-minute exceptions). The spec should either commit to using it with a stated lag tolerance, or explicitly exclude it from sensitivity analysis until the maintainers confirm what generates it.
2. **"Terminal, not right-censored" vs. "unknown outside the export's coverage."** All three assigned pages end `deleted` with no later activity *in this export*. Treated here as confident-terminal "within export coverage" — but the spec's own missing-history caveats mean a live-wiki restoration outside the cut window can't be ruled out. Should be one explicit sentence in `docs/ASSUMPTIONS.md`, not left implicit.
3. **Criticality of `TestFoobaAgent`.** Reads as ordinary scratch material, not the coordination-heavy pattern of the other two assigned pages. Flagging for Alex/Aaron/Jaswin's criticality call, not deciding it here.

## Candidate blind fixtures (for Ubayd's later differential tests)

`AgentProxyCountyNext987111` (double-recreation round) and the `OAIEquityDec30Raw`/`OECDJun26PrecisionScout` pair (cross-page propagation timing) — both fully reconstructed, held back per §4 above.

## Findings that could invalidate the project design

None found that break the four-hour gate's own pass criteria: hashes agree, seven independently reconstructed cases are internally consistent with each other and with DATA_AUDIT's claims, deletion/recreation/no-body semantics behave exactly as documented, and no future-information dependency was required for any reconstruction in this pass. The one finding with real teeth is the `archived_at` lag pattern (§5) — not large enough to be a kill condition on its own, but exactly the kind of thing that becomes a silent, hard-to-detect bug in the archive-aware sensitivity feature if it isn't written down before E06/E09 are built.
