# E06 fixture bundle — filtered, safe for development access

Purpose: `docs/E06_IMPLEMENTATION_CONTRACT.md` §4 requires that Ubayd receive "only Jaswin packets 01,02,03,05,06,07 boundary tables plus their matching source-appendix entries" and explicitly says **not** to hand over the entire research document to get those excerpts, because `audit/JASWIN_V02_RECONSTRUCTION.md` also contains the two blind packets (04, 08) in full. This file is that filtered handoff. It exists so nobody has to trust themselves not to scroll past the wrong section in the full research document.

**If you are Ubayd: this file, plus `docs/E06_IMPLEMENTATION_CONTRACT.md`, is your complete input for E06. You do not need `audit/JASWIN_V02_RECONSTRUCTION.md` or `docs/V02_ADJUDICATION.md` for this ticket — please don't open them until interface freeze, to keep packets 04/08 usable as blind tests later.**

State vocabulary: `unknown`, `live(body_ref)`, `live(body_unknown)`, `deleted`. Full transition rules and SAFE/UNSAFE classification are in `E06_IMPLEMENTATION_CONTRACT.md` §1 — this file supplies data, that one supplies rules.

---

## Released packets (01, 02, 03, 05, 06, 07) — full boundary tables + raw ledgers

Source: `audit/JASWIN_V02_RECONSTRUCTION.md`, cross-adjudicated against Sam's independent reconstruction with zero disagreement on every state/timestamp/episode boundary (`docs/V02_ADJUDICATION.md`, `audit/V02_ADJUDICATION_2026-09-12.md`).

### 01 — DataUSAConstructionWageSep18Live

One left-censored live episode, ending at deletion. All rows F+M; pre-state carry is A; ordering exact.

| Timestamp UTC (2026-06-19) | Boundary / source | Before | Mutation / after |
|---|---|---|---|
| 12:40:34 | @1; r5104/e12031 | unknown | save → L@1 |
| 12:47:08 | @2; r5105/e12037 | L@1 | save → L@2 |
| 12:55:48 | @3; r5106/e12043 | L@2 | save → L@3 |
| 12:59:09 | @4; r5107/e12046 | L@3 | save → L@4 |
| 13:02:26 | @5; r5108/e12053 | L@4 | save → L@5 |
| 13:06:18 | @6; r5109/e12055 | L@5 | save → L@6 |
| 13:10:09 | @7; r5110/e12059 | L@6 | save → L@7 |
| 13:13:23 | @8; r5111/e12062 | L@7 | save → L@8 |
| 13:16:18 | @9; r5112/e12064 | L@8 | save → L@9 |
| 13:16:54 | @10; r5113/e12065 | L@9 | save → L@10 |
| 13:22:25 | @11; r5114/e12070 | L@10 | save → L@11 |
| 13:27:33 | @12; r5115/e12075 | L@11 | save → L@12 |
| 13:38:52 | @13; r5116/e12117 | L@12 | save → L@13 |
| 13:40:55 | @14; r5117/e12123 | L@13 | save → L@14 |
| 13:45:21 | @15; r5118/e12124 | L@14 | save → L@15 |
| 14:05:02 | @16; r5119/e12174 | L@15 | save → L@16 |
| 14:07:45 | @17; r5120/e12176 | L@16 | save → L@17 |
| 14:08:33 | @18; r5121/e12177 | L@17 | save → L@18 |
| 14:09:03 | @19; r5122/e12178 | L@18 | save → L@19 |
| 14:09:51 | @20; r5123/e12180 | L@19 | save → L@20 |
| 14:10:25 | @21; r5124/e12182 | L@20 | save → L@21 |
| 14:10:49 | @22; r5125/e12183 | L@21 | save → L@22 |
| 14:11:26 | @23; r5126/e12185 | L@22 | save → L@23 |
| 14:12:11 | @24; r5127/e12187 | L@23 | save → L@24 |
| 14:14:03 | @25; r5128/e12190 | L@24 | save → L@25 |
| 14:14:50 | @26; r5129/e12191 | L@25 | save → L@26 |
| 14:14:55 | @27; r5130/e12192 | L@26 | save → L@27 |
| 14:15:35 | @28; r5131/e12193 | L@27 | save → L@28 |
| 14:17:40 | @29; r5132/e12197 | L@28 | save → L@29 |
| 14:37:47 | @30; r5133/e12206 | L@29 | save → L@30 |
| 15:46:37 | delete:dse:rclog:145609; e12231 | L@30 | successful delete → deleted |

**Non-mutation markers (must remain no-ops):** `@29` archived_at=14:19:47 does not end L@29 (real gap: next save is 18 minutes later at 14:37:47 — do not treat archived_at as a visibility clock). `@30` archived_at=15:46:25 does not delete L@30 (12s before the real deletion at 15:46:37).

**Raw ledger (event ID / body hash / clocks):**

| Selected timestamp | Event ID | Body ref + SHA-256 | Native clocks |
|---|---|---|---|
| 2026-06-19T12:40:34Z | `save:dse~DataUSAConstructionWageSep18Live@1` (events.jsonl#L12031) | `dse~DataUSAConstructionWageSep18Live@1` (revisions.jsonl#L5104); `9c42e64f789f87d0a418dc13a29266c246d6fe7c600ef69c17fe964fcf501f89`; 392B ascii | reqlog/u=1/revision.pref_ts; archived_at=12:47:09Z |
| 2026-06-19T15:46:37Z | `delete:dse:rclog:145609` (events.jsonl#L12231) | revision_ref=null | reqlog/u=1/rclog.unix_ts; success_observed=true; `rclog.jsonl:145609`; `reqlog_dse_2606.jsonl:1415545` |

*(Full per-revision hash ledger for all 30 saves is in `audit/JASWIN_V02_RECONSTRUCTION.md`'s source appendix under "Raw ledger: DataUSAConstructionWageSep18Live" — every hash there matches the pinned export and was independently re-verified by Sam. Reproduce it directly from `data/raw/export/revisions.jsonl` rows 5104–5133 rather than retyping 30 hashes here; the two rows above anchor the first and last mutation.)*

### 02 — ZZZDataUSAConstructionWageLive

Separate title/episode from 01 — **no structural recreation edge exists between them anywhere in the corpus**, despite the body text calling itself a backup.

| Timestamp UTC (2026-06-19) | Boundary / source | Before | Mutation / after |
|---|---|---|---|
| 14:06:38 | @1; r13354/e12175 | unknown | save → L@1 |
| 14:09:40 | @2; r13355/e12179 | L@1 | save → L@2 |
| 14:11:08 | @3; r13356/e12184 | L@2 | save → L@3 |
| 14:13:28 | @4; r13357/e12188 | L@3 | save → L@4 |
| 14:13:54 | @5; r13358/e12189 | L@4 | save → L@5 |
| 14:16:11 | @6; r13359/e12194 | L@5 | save → L@6 |
| 14:28:22 | @7; r13360/e12203 | L@6 | save → L@7 |
| 14:38:50 | @8; r13361/e12207 | L@7 | save → L@8 |
| 14:40:18 | @9; r13362/e12208 | L@8 | save → L@9 |
| 14:44:31 | @10; r13363/e12209 | L@9 | save → L@10 |
| 15:46:49 | delete:dse:rclog:145611; e12232 | L@10 | successful delete → deleted |

**Non-mutation markers:** `@9` archived_at=14:41:48 no-op; `@10` archived_at=15:46:47 no-op (2s before real deletion at 15:46:49).

**Anchor raw ledger rows:** first save `dse~ZZZDataUSAConstructionWageLive@1` (revisions.jsonl#L13354, `92a63d1acfe7f3f32198edea4568b71afaef43496c87fa48076622cc6694ad11`, 427B ascii); deletion `delete:dse:rclog:145611` (events.jsonl#L12232, `rclog.jsonl:145611`, `reqlog_dse_2606.jsonl:1415565`).

**Independently reproduced timing (both passes, exact):** notice-in-@16-of-packet-01 (14:05:02Z) → this page's `@1` (14:06:38Z) = **96s**. Packet 01's deletion (15:46:37Z) → this page's deletion (15:46:49Z) = **12s**.

### 03 — AgentLinkma21JuneAA

Two episodes: L1 (creation to first deletion), E1 (post-recreation to second deletion).

| Timestamp UTC | Boundary / source | Before | Mutation / after | Episode |
|---|---|---|---|---|
| 2026-06-18 16:00:51 | @1; r1642/e5451 | unknown | save → L@1 | L1 |
| 2026-06-18 16:37:13 | @2; r1643/e5538 | L@1 | save → L@2 | L1 |
| 2026-06-18 16:38:25 | @3; r1644/e5545 | L@2 | save → L@3 | L1 |
| 2026-06-18 16:40:33 | @4; r1645/e5563 | L@3 | save → L@4 | L1 |
| 2026-06-18 16:48:23 | @5; r1646/e5603 | L@4 | save → L@5 | L1 |
| 2026-06-18 16:48:45 | @6; r1647/e5608 | L@5 | save → L@6 | L1 |
| 2026-06-18 16:58:28 | @7; r1648/e5658 | L@6 | save → L@7 | L1 |
| 2026-06-18 17:05:29 | @8; r1649/e5688 | L@7 | save → L@8 | L1 |
| 2026-06-18 17:06:16 | @9; r1650/e5691 | L@8 | save → L@9 | L1 |
| 2026-06-18 17:27:08 | @10; r1651/e5782 | L@9 | save → L@10 | L1 |
| 2026-06-18 17:28:54 | @11; r1652/e5794 | L@10 | save → L@11 | L1 |
| 2026-06-18 17:38:22 | @12; r1653/e5881 | L@11 | save → L@12 | L1 |
| 2026-06-18 17:53:24 | @13; r1654/e6034 | L@12 | save → L@13 | L1 |
| 2026-06-18 18:17:51 | @14; r1655/e6324 | L@13 | save → L@14 | L1 |
| 2026-06-18 18:26:11 | @15; r1656/e6449 | L@14 | save → L@15 | L1 |
| 2026-06-18 18:26:23 | delete:dse:rclog:138648; e6453 | L@15 | successful delete → deleted | L1 ends |
| 2026-06-18 18:29:39 | @16; r1657/e6517 | deleted | save → L@16 | E1 starts |
| 2026-06-18 19:16:58 | @17; r1658/e7348 | L@16 | save → L@17 | E1 |
| 2026-06-18 19:18:22 | @18; r1659/e7369 | L@17 | save → L@18 | E1 |
| 2026-06-18 19:47:58 | @19; r1660/e7996 | L@18 | save → L@19 | E1 |
| 2026-06-18 19:50:30 | @20; r1661/e8052 | L@19 | save → L@20 | E1 |
| 2026-06-24 12:59:34 | delete:dse:rclog:151031; e15863 | L@20 | successful delete → deleted | E1 ends |

**Critical no-op / ordering test:** `@19`'s archived_at is **19:50:33**, which is *later* than `@20`'s own selected save time (19:50:30). At that archive timestamp the modeled state is already `L@20`, and stays `L@20` — this independently proves `archived_at` cannot be used as a live-current-body clock (it can point *past* a state that has already been superseded, not just lag before the next one). This is the strongest single test case for "never derive a transition from an archival clock."

**Anchor raw ledger rows:** `@15` save (revisions.jsonl#L1656, `0ce9394a642067a0401f692e5258c881505fe5791384a13259c571ff4240183e`, 633B) → delete `138648` (events.jsonl#L6453, `rclog.jsonl:138648`, `reqlog_dse_2606.jsonl:1169010`), gap **exactly 12 seconds**. `@20` (revisions.jsonl#L1661, `278a3aa3b9a601f62119310ec3e2b62146f6f0301194aba9ae14a72d0b2cf56c`, 415B) → delete `151031` (events.jsonl#L15863).

### 05 — TestFoobaAgent

Deletion of an entirely unheld earlier incarnation precedes `@1` — `@1` is a recreation, not a first-ever creation.

| Timestamp UTC | Boundary / source | Before | Mutation / after | Episode |
|---|---|---|---|---|
| 2026-06-04 10:53:40 | delete:dse:rclog:131972; e1051 | unknown | successful delete → deleted | closure only, prior start unknown |
| 2026-06-08 04:03:23 | @1; r10213/e1092 | deleted | save → L@1 | E1 starts |
| 2026-06-17 02:06:05 | @2; r10214/e4181 | L@1 | save → L@2 | E1 |
| 2026-06-17 02:06:29 | @3; r10215/e4185 | L@2 | save → L@3 | E1 |
| 2026-06-17 02:11:54 | @4; r10216/e4210 | L@3 | save → L@4 | E1 |
| 2026-06-18 18:45:02 | @5; r10217/e6785 | L@4 | save → L@5 | E1 |
| 2026-06-24 12:35:19 | delete:dse:rclog:151010; e15852 | L@5 | successful delete → deleted | E1 ends |

**Test note:** `@1`→`@2` spans **8 days 22 hours** with zero recorded activity in between — this must remain a single episode (no deletion occurred in the gap), not be split by an implementation that treats a long silence as implicit closure. Final deletion's `request_time` is `:18`, one second before the selected `success_time` `:19` used for the transition — don't select the request time.

**Anchor raw ledger rows:** deletion of unheld prior incarnation `delete:dse:rclog:131972` (events.jsonl#L1051, `rclog.jsonl:131972`); `@1` (revisions.jsonl#L10213, `f8f47cbe03cb08e2e63a3d532da2181a5adc988e7fce21f818db6063fcd93667`, 217B, `relation_type=first_recreation_of` → `131972`); final deletion `delete:dse:rclog:151010` (events.jsonl#L15852).

### 06 — OpenAIDataUSAPoliceBridge20260129

No page row or held revision exists for this title anywhere in the export — identity comes only from event records.

| Timestamp UTC (2026-06-19) | Exact source ID / type | Before | Mutation / after | Episode |
|---|---|---|---|---|
| 23:00:37 | delete:dse:rclog:145962; e12452 | unknown | successful delete → deleted | closure, prior start unknown |
| 23:19:13 | revert:delete:dse:rclog:145962; e12498 | deleted | successful form_edit, no revision → BU | E1 starts, body unknown |
| 23:40:56 | delete:dse:rclog:146157; e12561 | BU | successful delete → deleted | E1 ends |

**This is the cleanest available test for "never invent a body after a bodyless mutation."** No body hash/reference can ever be attached to this title. The middle row's exported ID contains the *earlier* deletion's native log line, not the edit's own — don't assume the ID structure reflects the action's own provenance without checking. Nominal BU duration: **21m43s** (23:19:13→23:40:56).

**Native evidence:** first delete `rclog.jsonl:145962`/`reqlog_dse_2606.jsonl:1442830`; middle revert `rclog.jsonl:146041`/`reqlog_dse_2606.jsonl:1444458`; last delete `rclog.jsonl:146157`/`reqlog_dse_2606.jsonl:1448393` (its `request_time` is one second before `success_time` — use success_time).

### 07 — AgentOfficialDirectQueryAA3

| Timestamp UTC | Exact source boundary | Before | Mutation / after |
|---|---|---|---|
| 2026-05-28 01:16:54 | @1; r2457/e573; save | unknown | save → L@1 |
| 2026-06-24 10:43:36 | delete:dse:rclog:150767; e15726; delete | L@1 | successful delete → deleted |

**Lower-confidence test case:** this deletion is graded `rclog`-only (not `reqlog`), with `clock_note="ambiguous delete requests at -1/+1s"` and `request_time=null` — two candidate request lines exist (`reqlog_dse_2606.jsonl:1850959` and `:1850960`) and neither should be selected as *the* matching request. In the ±1s uncertainty convention, a query at `:35` admits either live/deleted; at `:37` it is deleted in every admissible realization. `@1`'s archived_at (10:43:34) is a no-op, nearly a month before this deletion — don't let the long carry duration read as a measured live lifetime.

**Anchor raw ledger rows:** `@1` (revisions.jsonl#L2457, `26b9aee12a0f198380dd6fb9f516f49589f2df37ef533f044eacfd315ab9e21e`, 211B); deletion `delete:dse:rclog:150767` (events.jsonl#L15726).

---

## Public diagnostic packets (09, 10a, 10b) — deterministic selection, independent review still pending

These were chosen by a **pre-declared rule**, not because they looked interesting (contrast with Sam's original, since-superseded candidates `StartSeite`/`OAIResearchBridgeMay3X`, which were picked after seeing what they contained and are not used).

### 09 — `AI` (legacy / head-mismatch)

Selection rule: ascending verbatim `page_key` among DSE pages with `n_revs_before > 0`.

| Timestamp UTC | Source record | Before | Event / after |
|---|---|---|---|
| 2026-06-18 21:02:27 | save:dse~AI@2 + dse~AI@2; e10753/r42 | unknown | supported save → L@2 |
| 2026-06-19 15:53:29 | archived_at on r42 (metadata, not a mutation) | L@2 under A | no-op |

`diff_base_reason=earlier_revisions_not_published`. Descriptors `live_body_variant=dw`, `head_differs_from_live=true`, `deleted_live=false` are export-store metadata, not observed transitions — **do not infer a moderator overwrite or restore the unpublished `@1`.** Historical final live body is unknown. Recommend: exclude from exact body scoring, retain for diagnostic/load queries.

### 10a — `AgentNacoPovertyTexas2015XQ` (deterministic same-time tie)

Selection rule: ascending `(page_key, time)` among DSE title/time groups with ≥2 physical mutation rows; first tie found: `2026-06-22T08:39:06Z`.

35 ordinary saves (2026-06-22 07:04:19 → 08:50:48) then deletion `151929` at 2026-06-26 16:45:23. The tie is at `@22`/`@23`, both exactly `2026-06-22T08:39:06Z`, `u=1`, different bodies/hashes (1,126 vs 2,054 bytes). **No source evidence resolves physical order.** Correct behavior: immediately before the group, state is `L@21`; immediately after, admissible states are `{L@22, L@23}` — never a merged body, never an ID/seq-based winner; convergence happens only at `@24` (08:39:31).

### 10b — `AgentBridgeOct2142X` (simple released-trace control)

Selection rule: ascending `page_key` among DSE titles with exactly one held revision, zero pre-cut revisions, no published delete/BU mutation — sole qualifier.

| Timestamp UTC (2026-06-16) | Record | Before | Event / after |
|---|---|---|---|
| 18:40:04 | save:dse~AgentBridgeOct2142X@1; e1807/r301 | unknown | supported save → L@1 |
| 18:43:13 | archived_at on r301 (metadata, not a mutation) | L@1 under A | no-op |

205-byte body, no subsequent mutation in the published population. Carries to T, right-censored. **"Stable" means uncomplicated released trace, not demonstrated uninterrupted public availability** — even this control has a non-mutating archive marker, which is itself a useful regression test (an implementation that treats every archive timestamp as a transition will wrongly end this page's episode at 18:43:13).

---

## Explicitly held back — do not request, do not infer

**Packets 04 (`AgentProxyCountyNext987111`) and 08 (`OAIEquityDec30Raw` / `OECDJun26PrecisionScout`)** are reserved for blind differential testing once the E06 interface is stable. Their full raw data exists in the same pinned export you already have access to (per E01/E05), so nothing stops anyone from independently deriving their states — the request is specifically **not to consult the research documents' pre-computed expected answers** for these two while building or testing the engine, so a real blind comparison stays possible. If you have already read `audit/JASWIN_V02_RECONSTRUCTION.md` or `docs/V02_ADJUDICATION.md` in full, say so — contamination needs to be logged, not hidden, and it changes what "blind" can mean for the rest of this ticket.

---

## Synthetic adversarial tests still required (hand-authored, not sourced from any packet)

Per `E06_IMPLEMENTATION_CONTRACT.md` §4. These don't need real data — write them directly against the state model:

- Isolated save, isolated delete, isolated BU mutation, each from `unknown`.
- Delete → save with a `first_recreation_of` relation present, and the same transition with no relation metadata at all (must produce identical state behavior — relations are provenance, never a precondition for a transition).
- Repeated deletes on the same title (delete → delete with no save in between — must not error, must not implicitly "undelete").
- Save/save tie at identical timestamp with different bodies → admissible alternatives, not a merged or ID-selected body (mirrors packet 10a).
- Save/delete tie at identical timestamp → admissible `{live, deleted}`, not one silently chosen.
- Identical-body tie (two saves, same hash, same timestamp) → distinct provenance preserved even though the state value coincides.
- Touching uncertainty windows (`[t, t+2u]` for two events whose ±u ranges just meet) → co-timing admissible, non-overlapping windows force order.
- A later full replacement converging previously-divergent alternatives (mirrors packet 10a's `@24`).
- Suffix invariance: appending a future mutation must never change `state_at(key, t)` for `t` strictly before it, except completing an already-incomplete same-time group.
- Unsupported action / unresolved uncertainty must fail closed (explicit error/ambiguity marker), never silently default to a guessed state.
- Opaque key handling: `page_key` must never be parsed, slash-split, or treated as a filesystem path.
- Out-of-horizon query (`t < t0` or `t > T`) → explicit error, never extrapolation.
- A page reachable only via `pages.jsonl`/metadata with no mutation in-horizon → `unknown`, not an existence oracle.

Hand-compute expected values for each before writing the assertion — don't let the engine's first output become the expected value.
