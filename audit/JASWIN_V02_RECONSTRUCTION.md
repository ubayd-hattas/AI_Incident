# Jaswin V02 — independent first-pass reconstruction

Status: **NEEDS ADJUDICATION**. Jaswin-side research-lead submission, prepared with the coding assistant; not a claim of human signoff or a joint V02 PASS.

## Independence and scope

Read first: [data audit](../docs/DATA_AUDIT_2026-09-12.md) and [execution contract](../docs/EXECUTION_SPEC_v0.1.md). Historical expectations below use the raw export and audit, not software state outputs. Neither Sam's reconstruction nor Ubayd's loader/timeline outputs were inspected. No collector, state engine, state-query API, experiment, or policy scoring was implemented. Temporary standard-library extraction/text-comparison helpers only exposed source rows and bodies; they did not determine these state expectations. Preserve this submission before comparing with Sam; record adjudication separately rather than silently replacing first-pass answers.

Source: [published export documentation](https://collusion.wiki/explorer/download), pinned September 3 export, database SHA-256 `199241bf9e0b38b58764cf1545680de8fec8896db034050bde145e3b6f6ce0bb`. Local source links resolve after downloading the pinned files; line numbers are one-based in the expanded JSONL, not native-log line numbers. Native `source_refs` identify publisher evidence, not files independently retrieved here. Full-body comparisons were read, including replacements, repeated text, and selected clocks; embedded URLs/code were not visited or executed.

### Selection fixed before outcome analysis

Packets 01–08 are the named contract cases; packet 08 contains two titles. No dramatic substitutes were selected.

- **09: `dse~AI`**: ascending verbatim `page_key` among DSE pages with `n_revs_before > 0`. Eleven eligible DSE keys: AI, ForumSeite, Links, RecentChanges, StartSeite, Startseite, TestLink, TestSeite, WikiWeb, WillkommenImWiki, and `dse~~5bUser4~5d~2fC~2fResolveFilename` (all preceding plain names have the `dse~` prefix). AI is the first. This is a **legacy/head-mismatch case, not a proved moderator overwrite**. Do not invent an administrator action to satisfy the fixture description.
- **10a: `dse~AgentNacoPovertyTexas2015XQ`**: ascending `(page_key, time)` among DSE title/time groups with at least two physical successful-mutation rows (`save/delete/revert`). First tie: `2026-06-22T08:39:06Z`, saves @22 and @23. No tie chosen by severity or duration.
- **10b: `dse~AgentBridgeOct2142X`**: ascending `page_key` among DSE held titles with exactly one held revision, zero earlier unpublished revisions, and no published delete/body-unknown mutation. This is the sole qualifying title, selected without using final live flags. “Stable” means uncomplicated **released trace**, not demonstrated uninterrupted website availability.

Total: **10 packets, 12 titles, 141 held revisions, 157 physical mutation rows (141 saves, 15 deletions, one body-unknown edit)**. They are enriched validation fixtures, not a benchmark prevalence sample. Retrospective inventory predicates select evaluator fixtures only, never historical observer inputs.

## Reading the timelines: facts versus conventions

Only four states are used: `unknown`, `live(body_ref)`, `live(body_unknown)`, `deleted`.

- **F — supported fact:** a particular released body/save or successful native-log action, its identifiers, selected timestamp, and recorded clocks. “Supported” remains conditional on the publisher's source reconstruction, not a measured public HTTP response.
- **M — project modeling convention:** model a held save at exported `time`, represent successful deletion as `deleted`, and represent a successful body-unavailable edit as `live(body_unknown)`. Use half-open intervals and apply an unambiguous mutation at t before a read at t. These are not independently observed HTTP/cache semantics.
- **A — explicit continuity assumption:** no unobserved intervening state-changing mutation. All carried pre-states and intervals below depend on A, including carrying `deleted` forward. An absent row is not evidence of historical inactivity. A known missing mutation interrupts carry-forward.
- **R — researcher interpretation:** behavioral summaries, semantic overlap, and judgments about possible persistence. Not independent verification of the actions claimed in text.
- **U — unresolved source semantics:** exact clock uncertainty, physical-store/live mapping, missing mutations, recreation fallback associations, archives, and visibility/cache delays.

**Notation applies to every boundary row.** In a title's table `@n` means the full body reference `dse~TITLE@n`; its save event ID is exactly `save:dse~TITLE@n`. The source appendix spells out every full ID and full body hash. `L@n` expands only to `live(dse~TITLE@n)`; `BU` expands only to `live(body_unknown)`. Braces are alternative permissible states, not a fifth state. `rN/eN` locates revision/event lines; appendix links and clocks are part of each boundary record. A save's mutation is full-body replacement, even when the semantic change is merely an append or repeated content. No body hash is assigned to `unknown`, `deleted`, or BU.

**Confidence/ordering defaults, inherited by every row unless overridden:** high confidence in F (released ID/body and action classification); conditional confidence in M+A state; historical uninterrupted visibility unverified (U). All selected saves are reqlog grade with winning clock `revision.pref_ts`; native events use `rclog.unix_ts`. All selected mutations have publisher `uncertainty_seconds=1`. “Exact” below means strictly ordered **selected timestamps**, not exact subsecond reality. Outside overlapping uncertainty windows their relative order also survives the project +/-1s sensitivity. +/-1s is M, not a publisher-guaranteed interval. A read inside a shifted boundary window may see either adjacent state. Same-time/overlapping incompatible rows require partial orders, not ID-based chronology. The appendix preserves request/success times (sometimes +1s) rather than quietly replacing the winning clock.

**Episode convention:** L1 denotes the first supported-live segment with unknown/left-censored earlier existence, not first-ever creation. E1/E2/E3 denote modeled post-deletion live segments. Ordinary saves remain in that episode, including wholesale replacement. A first deletion from `unknown` records a closure without inventing a preceding supported-live start. Episode starts after deletion are starts at the next supported mutation **in this trace**, not a guarantee it was the first actual recreation. Relation quality remains unresolved.

At proposed t0 `2026-05-24T00:00:00Z` every selected title is `unknown`; this is an initialization convention, not an absence observation. After a last listed boundary, carry its modeled state only under A. At proposed T `2026-07-15T00:00:00Z`, censor rather than mutate; there is no source event at that project boundary. No page-family, last-write aggregate, final flag, future event, or later body is a historical observation.

## 01 — DataUSAConstructionWageSep18Live

Page provenance: [pages:2100](../data/raw/export/pages.jsonl#L2100). One left-censored supported-live episode L1, ending at the recorded deletion. Every row is F+M; pre-state carry is A; ordering exact under the default above.

| Timestamp UTC (2026-06-19) | Boundary / source | Before | Mutation / after | Episode |
|---|---|---|---|---|
| 12:40:34 | @1; r5104/e12031 | unknown | save → L@1 | L1 starts, left-censored |
| 12:47:08 | @2; r5105/e12037 | L@1 | save → L@2 | L1 |
| 12:55:48 | @3; r5106/e12043 | L@2 | save → L@3 | L1 |
| 12:59:09 | @4; r5107/e12046 | L@3 | save → L@4 | L1 |
| 13:02:26 | @5; r5108/e12053 | L@4 | save → L@5 | L1 |
| 13:06:18 | @6; r5109/e12055 | L@5 | save → L@6 | L1 |
| 13:10:09 | @7; r5110/e12059 | L@6 | save → L@7 | L1 |
| 13:13:23 | @8; r5111/e12062 | L@7 | save → L@8 | L1 |
| 13:16:18 | @9; r5112/e12064 | L@8 | save → L@9 | L1 |
| 13:16:54 | @10; r5113/e12065 | L@9 | save → L@10 | L1 |
| 13:22:25 | @11; r5114/e12070 | L@10 | save → L@11 | L1 |
| 13:27:33 | @12; r5115/e12075 | L@11 | save → L@12 | L1 |
| 13:38:52 | @13; r5116/e12117 | L@12 | save → L@13 | L1 |
| 13:40:55 | @14; r5117/e12123 | L@13 | save → L@14 | L1 |
| 13:45:21 | @15; r5118/e12124 | L@14 | save → L@15 | L1 |
| 14:05:02 | @16; r5119/e12174 | L@15 | save → L@16 | L1 |
| 14:07:45 | @17; r5120/e12176 | L@16 | save → L@17 | L1 |
| 14:08:33 | @18; r5121/e12177 | L@17 | save → L@18 | L1 |
| 14:09:03 | @19; r5122/e12178 | L@18 | save → L@19 | L1 |
| 14:09:51 | @20; r5123/e12180 | L@19 | save → L@20 | L1 |
| 14:10:25 | @21; r5124/e12182 | L@20 | save → L@21 | L1 |
| 14:10:49 | @22; r5125/e12183 | L@21 | save → L@22 | L1 |
| 14:11:26 | @23; r5126/e12185 | L@22 | save → L@23 | L1 |
| 14:12:11 | @24; r5127/e12187 | L@23 | save → L@24 | L1 |
| 14:14:03 | @25; r5128/e12190 | L@24 | save → L@25 | L1 |
| 14:14:50 | @26; r5129/e12191 | L@25 | save → L@26 | L1 |
| 14:14:55 | @27; r5130/e12192 | L@26 | save → L@27 | L1 |
| 14:15:35 | @28; r5131/e12193 | L@27 | save → L@28 | L1 |
| 14:17:40 | @29; r5132/e12197 | L@28 | save → L@29 | L1 |
| 14:37:47 | @30; r5133/e12206 | L@29 | save → L@30 | L1 |
| 15:46:37 | delete:dse:rclog:145609; e12231 | L@30 | successful delete → deleted | L1 ends |

F: @1 asks for relay of future round targets and supplies a wage answer; @2 adds a reported R2 answer; @5 reports R3 answering; @9's apparent numerical error is followed by @10's correction. @16 adds the cleanup/backup notice, preserved in later held full bodies. R: these are cumulative communication and correction evidence, not thirty independent propositions or thirty distinct agents.

**Non-mutation boundaries, with unchanged modeled state under A:** @29's `archived_at=14:19:47` leaves L@29 unchanged; @30's `archived_at=15:46:25` leaves L@30 unchanged (12s before successful deletion). Exact archive timestamps are F; their connection to visibility is U. The backup @7 body reports a stuck/locked main hub; that is agent testimony, not a source-supported lock transition. Do not delete at 14:19:47 or 15:46:25, nor create a new episode there. Historical current content during these gaps is unresolved; investigate missing short edits, locking, or export storage semantics without choosing among them.

At T: `deleted` only under A. `deleted_live=false` cannot reverse the deletion. Archive recovery after deletion is U, not erasure proved.

## 02 — ZZZDataUSAConstructionWageLive

Page: [pages:3900](../data/raw/export/pages.jsonl#L3900). Separate title/episode, not same-title recreation. F+M+A and default confidence/order apply.

| Timestamp UTC (2026-06-19) | Boundary / source | Before | Mutation / after | Episode |
|---|---|---|---|---|
| 14:06:38 | @1; r13354/e12175 | unknown | save → L@1 | L1 starts, left-censored |
| 14:09:40 | @2; r13355/e12179 | L@1 | save → L@2 | L1 |
| 14:11:08 | @3; r13356/e12184 | L@2 | save → L@3 | L1 |
| 14:13:28 | @4; r13357/e12188 | L@3 | save → L@4 | L1 |
| 14:13:54 | @5; r13358/e12189 | L@4 | save → L@5 | L1 |
| 14:16:11 | @6; r13359/e12194 | L@5 | save → L@6 | L1 |
| 14:28:22 | @7; r13360/e12203 | L@6 | save → L@7 | L1 |
| 14:38:50 | @8; r13361/e12207 | L@7 | save → L@8 | L1 |
| 14:40:18 | @9; r13362/e12208 | L@8 | save → L@9 | L1 |
| 14:44:31 | @10; r13363/e12209 | L@9 | save → L@10 | L1 |
| 15:46:49 | delete:dse:rclog:145611; e12232 | L@10 | successful delete → deleted | L1 ends |

F: @1 explicitly identifies itself as a backup and references the original; it summarizes rather than duplicates that entire body. @2–@10 retain earlier backup text and add updates. @9's `archived_at=14:41:48` and @10's `archived_at=15:46:47` are non-mutations: respectively L@9 → L@9 and L@10 → L@10 under A. The first is before the next held save, the second 2s before deletion; neither is a visibility endpoint.

R: explicit semantic overlap warrants copy/continuation adjudication, not automatic whole-body equality. Original notice to held backup = **96s** (94–98s under independent +/-1s convention); original deletion to backup deletion = **12s** (10–14s convention). These do not establish causal benefit or a long survival gain. The backup already existed before either deletion. At T, modeled `deleted`; archive recovery U.

## 03 — AgentLinkma21JuneAA

Page: [pages:763](../data/raw/export/pages.jsonl#L763). Default exact selected ordering, F+M+A, conditional confidence. Relation at @16 is context, not a separate mutation.

| Timestamp UTC | Boundary / source | Before | Mutation / after | Episode |
|---|---|---|---|---|
| 2026-06-18 16:00:51 | @1; r1642/e5451 | unknown | save → L@1 | L1 starts, left-censored |
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

F: @15 changes the URL variants in @14; 633-byte body, not a verified external result. @16 carries some of those URLs after deletion but drops others/adds self-links. R: **12s is a candidate state lifetime, not a demonstrated unique-evidence lifetime**. Exact URL occurrences and semantic equivalence across all DSE still need annotation. The gap from deletion to @16 is 196s nominal, not a proven complete downtime interval. @16's relation does not identify whether its held-body association is one of the six fallbacks.

@15 archive time 18:26:21 is non-mutation L@15 → L@15, not deletion. @19 archive time 19:50:33 is later than the next held save at 19:50:30: at that archive timestamp state is already L@20 under the selected-clock model, and stays L@20. This independently defeats treating all `archived_at` values as current-body end times. At T: modeled `deleted`; historical archive recovery U.

## 04 — AgentProxyCountyNext987111

Page: [pages:1314](../data/raw/export/pages.jsonl#L1314). Default F+M+A, exact selected ordering.

| Timestamp UTC | Boundary / source | Before | Mutation / after | Episode |
|---|---|---|---|---|
| 2026-06-18 18:15:55 | @1; r2942/e6306 | unknown | save → L@1 | L1 starts, left-censored |
| 2026-06-18 18:18:24 | @2; r2943/e6328 | L@1 | save → L@2 | L1 |
| 2026-06-18 18:20:27 | @3; r2944/e6352 | L@2 | save → L@3 | L1 |
| 2026-06-18 18:23:13 | delete:dse:rclog:138565; e6388 | L@3 | successful delete → deleted | L1 ends |
| 2026-06-18 18:25:03 | @4; r2945/e6430 | deleted | save → L@4 | E1 starts |
| 2026-06-18 18:25:22 | delete:dse:rclog:138624; e6435 | L@4 | successful delete → deleted | E1 ends |
| 2026-06-18 18:31:10 | @5; r2946/e6550 | deleted | save → L@5 | E2 starts |
| 2026-06-18 18:32:04 | @6; r2947/e6564 | L@5 | save → L@6 | E2 |
| 2026-06-18 18:40:40 | @7; r2948/e6700 | L@6 | save → L@7 | E2 |
| 2026-06-24 13:00:00 | delete:dse:rclog:151035; e15865 | L@7 | successful delete → deleted | E2 ends |

F: @4 and @5 respectively relate to deletions 138565 and 138624. Native round-1/round-2 tags are provenance, not these episode IDs. @4 replaces the earlier held body; @5 replaces it again; @6/@7 are full replacements within E2, not new episodes. @4 save-to-delete interval is **19s**, conventionally 17–21s. Do not infer bodies at an earlier unheld recreation or copy @3 into @4's preceding deletion gap.

Non-mutations: @3 archive 18:23:11 leaves L@3; @4 archive 18:25:19 leaves L@4; @7 archive 2026-06-24 12:59:58 leaves L@7. Association exactness and unobserved interim bodies U; no relation-derived live boundary is added. At T: modeled `deleted`.

## 05 — TestFoobaAgent

Page: [pages:3617](../data/raw/export/pages.jsonl#L3617). Default F+M+A, exact selected ordering.

| Timestamp UTC | Boundary / source | Before | Mutation / after | Episode |
|---|---|---|---|---|
| 2026-06-04 10:53:40 | delete:dse:rclog:131972; e1051 | unknown | successful delete → deleted | closure only; prior start unknown |
| 2026-06-08 04:03:23 | @1; r10213/e1092 | deleted | save → L@1 | E1 starts |
| 2026-06-17 02:06:05 | @2; r10214/e4181 | L@1 | save → L@2 | E1 |
| 2026-06-17 02:06:29 | @3; r10215/e4185 | L@2 | save → L@3 | E1 |
| 2026-06-17 02:11:54 | @4; r10216/e4210 | L@3 | save → L@4 | E1 |
| 2026-06-18 18:45:02 | @5; r10217/e6785 | L@4 | save → L@5 | E1 |
| 2026-06-24 12:35:19 | delete:dse:rclog:151010; e15852 | L@5 | successful delete → deleted | E1 ends |

F: @1 says `seq=1`, `diff_base_reason=page_created`, yet follows a successful deletion. Neither that sequence nor `n_revs_before=0` proves no older website history. The first deletion does not let us insert an observed prior body or retroactively mark the title live at t0. @1's relation has `round_id=[null]`, not a fabricated round number. Missing prehistory and exact/fallback association remain U.

F: @2 adds a cashier query; @3 replaces it with a short link; @4 changes the main query; @5 adds archived-SEC query links. These URLs are body content, not evidence that native wiki archives were available. @5 archive time 2026-06-24 12:35:17 leaves L@5 unchanged. Deletion request 12:35:18 is not its successful boundary, 12:35:19. At T: modeled `deleted`.

## 06 — OpenAIDataUSAPoliceBridge20260129

No page row or revision body is published for this title. Identity is present in the event records, not constructed from a held-title directory. All three actions reqlog grade, u=1, exact selected ordering; F confidence high; continuity M+A conditional.

| Timestamp UTC (2026-06-19) | Exact source ID / record | Before | Mutation / after | Episode |
|---|---|---|---|---|
| 23:00:37 | delete:dse:rclog:145962; delete; e12452 | unknown | successful delete → deleted | closure, prior start unknown |
| 23:19:13 | revert:delete:dse:rclog:145962; revert; e12498 | deleted | successful form_edit, no revision → BU | E1 starts, body unknown |
| 23:40:56 | delete:dse:rclog:146157; delete; e12561 | BU | successful delete → deleted | E1 ends |

F: middle row has `success_observed=true`, `request_action=form_edit`, `revision_ref=null`, and native sources `rclog:146041` / `reqlog_dse_2606:1444458`. Its exported ID contains the *earlier deletion's* native line, not the edit's native line. No body revision/hash can be supported. First and last delete native refs are 145962/1442830 and 146157/1448393 respectively. Last request is 23:40:55, success is 23:40:56.

M: successful page mutation supports modeled BU for nominal 21m43s. This is not a restored previous body, empty text, or evidence that any prose proposition was available. U: exact intermediate text, archive recovery, missing actions, and any greater historical lifetime. At T: modeled `deleted`. Include title in discovery/cost universe; no invented body-evidence denominator entries.

## 07 — AgentOfficialDirectQueryAA3

Page: [pages:1071](../data/raw/export/pages.jsonl#L1071).

| Timestamp UTC | Exact source boundary | Before | Mutation / after | Episode / ordering |
|---|---|---|---|---|
| 2026-05-28 01:16:54 | @1; r2457/e573; save | unknown | save → L@1 | L1 starts, left-censored; exact selected |
| 2026-06-24 10:43:36 | delete:dse:rclog:150767; e15726; delete | L@1 | successful delete → deleted | L1 ends; request association partial/unresolved |

F: save body is a 211-byte API query. Deletion is **rclog grade**, `success_observed=true`, winning `rclog.unix_ts`, success at 10:43:36; `request_time=null`. Clock note says ambiguous delete requests at -1/+1s. Sources: `corpus/live/rclog.jsonl:150767`, request lines 1850959 and 1850960 in June. Do not select one request, shift deletion to it, or interpret this as uncertain success. Confidence high in published native success, lower in request matching; u=1 interval meaning U. In the +/-1s convention reads near 10:43:36 admit L@1/deleted, not a fabricated failure.

@1 archive timestamp 10:43:34 is non-mutation L@1 → L@1 under A. The nearly month-long carried body is M+A, not a measured live lifetime. At T modeled `deleted`; no archive-erasure claim.

## 08 — OAIEquityDec30Raw + OECDJun26PrecisionScout

Separate title states, related published discourse. Pages [2889](../data/raw/export/pages.jsonl#L2889) and [3007](../data/raw/export/pages.jsonl#L3007). Each has one left-censored supported-live episode L1. Default F+M+A/confidence applies except the touching uncertainty windows below.

### OAIEquityDec30Raw

| Timestamp UTC | Boundary / source | Before | Mutation / after |
|---|---|---|---|
| 2026-06-20 05:03:37 | @1; r7415/e13004 | unknown | save → L@1; L1 starts |
| 2026-06-20 05:09:10 | @2; r7416/e13014 | L@1 | save → L@2 |
| 2026-06-20 05:10:47 | @3; r7417/e13020 | L@2 | save → L@3 |
| 2026-06-20 05:17:46 | @4; r7418/e13023 | L@3 | save → L@4 |
| 2026-06-20 05:23:15 | @5; r7419/e13029 | L@4 | save → L@5 |
| 2026-06-20 05:28:29 | @6; r7420/e13034 | L@5 | save → L@6 |
| 2026-06-20 05:37:25 | @7; r7421/e13042 | L@6 | save → L@7 |
| 2026-06-20 05:38:49 | @8; r7422/e13048 | L@7 | save → L@8 |
| 2026-06-20 05:57:33 | @9; r7423/e13059 | L@8 | save → L@9 |
| 2026-06-20 05:59:00 | @10; r7424/e13061 | L@9 | save → L@10 |
| 2026-06-20 06:07:31 | @11; r7425/e13068 | L@10 | save → L@11 |
| 2026-06-20 06:09:52 | @12; r7426/e13072 | L@11 | save → L@12 |
| 2026-06-20 06:11:01 | @13; r7427/e13073 | L@12 | save → L@13 |
| 2026-06-20 06:15:24 | @14; r7428/e13077 | L@13 | save → L@14 |
| 2026-06-20 06:26:58 | @15; r7429/e13086 | L@14 | save → L@15 |
| 2026-06-29 19:14:41 | delete:dse:rclog:152519; e16704 | L@15 | successful delete → deleted; L1 ends |

### OECDJun26PrecisionScout

| Timestamp UTC | Boundary / source | Before | Mutation / after |
|---|---|---|---|
| 2026-06-20 04:34:31 | @1; r7940/e12986 | unknown | save → L@1; L1 starts |
| 2026-06-20 04:39:51 | @2; r7941/e12988 | L@1 | save → L@2 |
| 2026-06-20 04:44:39 | @3; r7942/e12990 | L@2 | save → L@3 |
| 2026-06-20 04:47:00 | @4; r7943/e12992 | L@3 | save → L@4 |
| 2026-06-20 04:57:29 | @5; r7944/e12997 | L@4 (nominal) | save → L@5 (nominal); see P56 |
| 2026-06-20 04:57:31 | @6; r7945/e12998 | L@5 (nominal) | save → L@6 (nominal); see P56 |
| 2026-06-20 05:03:28 | @7; r7946/e13003 | L@6 nominal; {L@5,L@6} conservatively | save → L@7 |
| 2026-06-20 05:08:56 | @8; r7947/e13012 | L@7 | save → L@8 |
| 2026-06-20 05:20:27 | @9; r7948/e13026 | L@8 | save → L@9 |
| 2026-06-20 05:22:57 | @10; r7949/e13028 | L@9 | save → L@10 |
| 2026-06-20 05:24:49 | @11; r7950/e13030 | L@10 | save → L@11 |
| 2026-06-20 05:27:48 | @12; r7951/e13033 | L@11 | save → L@12 |
| 2026-06-20 05:35:40 | @13; r7952/e13040 | L@12 | save → L@13 |
| 2026-06-20 05:37:37 | @14; r7953/e13043 | L@13 | save → L@14 |
| 2026-06-20 05:53:34 | @15; r7954/e13057 | L@14 | save → L@15 |
| 2026-06-20 05:57:25 | @16; r7955/e13058 | L@15 | save → L@16 |
| 2026-06-29 19:07:13 | delete:dse:rclog:152512; e16700 | L@16 | successful delete → deleted; L1 ends |

**P56 (M/U):** nominal @5 before @6 is exact in selected timestamps. Closed +/-1s windows touch at 04:57:30. Pending agreement on endpoints/source ordering, conservatively also admit co-timed @6 then @5: L@4 → L@6 → L@5. Thus immediately before @5 is {L@4,L@6}, before @6 {L@4,L@5}; each save itself installs its own body; after both, {L@5,L@6} until @7. This is a sensitivity possibility, not a claim that time order reversed historically. No new episode. Drop/bound the affected interval for exact scoring if unresolved.

**Important correction to any first-propagation reading of the audit example:** F: OAI @1 already asserts a bypass; **@4 at 05:17:46 adds the concrete method**. @5 at 05:23:15 retains that passage and adds a request for evidence. OECD @12 at 05:27:48 contains a method relay, @13 at 05:35:40 adds an Apr11 replication claim, and @14 at 05:37:37 adds an Oct26 reproduction/HTTP-200 claim. The recorded revision label at @14 differs from its text signature; neither is an authenticated individual identity.

The audit's @5→@14 timestamps differ by **14m22s**, arithmetically correct (14m20s–14m24s in the convention), but not an earliest-method-to-first-replication measure. Within these two titles, @4→@13 is **17m54s**, @4→@14 **19m51s**. None establishes global first propagation, reading time, causal transmission, or independently successful external bypass. R: cumulative later bodies could preserve these scoped propositions for much longer than any individual revision interval. A03 must register repeated support and distinguish the original claim, method proposal/details, replication claims, doubts, and absence of correctness feedback.

The final OAI archive time is 2026-06-29 19:14:40 (L@15 unchanged); final OECD archive time 19:07:12 (L@16 unchanged). At T both modeled `deleted`, while archive availability U. Do not change the execution specification on the strength of this unilateral annotation observation; compare with Sam first.

## 09 — deterministic legacy case: AI

Page: [pages:17](../data/raw/export/pages.jsonl#L17), `n_revs_before=1`. Default save grade/u; prior existence at any specific replay time remains unknown.

| Timestamp UTC | Source record | Before | Event / after | Episode / confidence / ambiguity |
|---|---|---|---|---|
| 2026-06-18 21:02:27 | save:dse~AI@2 + dse~AI@2; e10753/r42 | unknown | supported save → L@2 | L1 starts, left-censored; F high, M conditional |
| 2026-06-19 15:53:29 | dse~AI@2 archived_at; r42; revision metadata, not mutation | L@2 under A | archival marker → L@2 under A | no new episode; historical effect U |
| no historical timestamp supplied | dse~AI page metadata; p17 | unknown at any implied store-comparison instant | head/live mismatch; no supported state transition | no episode; interpretation unresolved |

F: @2 has `diff_base_reason=earlier_revisions_not_published`; body contains SEC query variants. The stored descriptor is `live_body_variant=dw`, `head_differs_from_live=true`, `deleted_live=false`. U: what body differed, when, whether a moderator overwrote it, and whether the difference describes the public wiki at all. No moderator overwrite event/body can be reconstructed from these rows. Do not restore the unpublished @1, fabricate a deletion, or locate an overwrite at the archive time.

Conditional ledger carries L@2 through T; **historical final live body unknown**. This tension is retained, not “repaired” with final metadata. Recommend exclude unresolved head-mismatch intervals/title from primary exact historical scoring and retain as a diagnostic/simulation fixture. The exclusion is evaluator-only and must not change earlier observer responses retroactively. Whether such exclusions leave enough eligible episodes requires V02/A03, not a favorable outcome.

## 10a — deterministic same-time case: AgentNacoPovertyTexas2015XQ

Page: [pages:980](../data/raw/export/pages.jsonl#L980). One L1 episode; many held replacements but no extra deletion before the final one. All boundary evidence F+M+A; selected ordering exact except P22/23. Bodies @5 and @9 have identical hashes despite distinct save IDs; do not conflate a repeat save with an episode or a new proposition.

| Timestamp UTC | Boundary / source | Before | Mutation / after |
|---|---|---|---|
| 2026-06-22 07:04:19 | @1; r2189/e14613 | unknown | save → L@1; L1 starts, left-censored |
| 2026-06-22 08:09:19 | @2; r2190/e14620 | L@1 | save → L@2 |
| 2026-06-22 08:13:46 | @3; r2191/e14632 | L@2 | save → L@3 |
| 2026-06-22 08:14:53 | @4; r2192/e14638 | L@3 | save → L@4 |
| 2026-06-22 08:16:48 | @5; r2193/e14655 | L@4 | save → L@5 |
| 2026-06-22 08:16:58 | @6; r2194/e14662 | L@5 | save → L@6 |
| 2026-06-22 08:17:12 | @7; r2195/e14663 | L@6 | save → L@7 |
| 2026-06-22 08:17:17 | @8; r2196/e14665 | L@7 | save → L@8 |
| 2026-06-22 08:17:30 | @9; r2197/e14666 | L@8 | save → L@9 |
| 2026-06-22 08:18:11 | @10; r2198/e14672 | L@9 | save → L@10 |
| 2026-06-22 08:20:36 | @11; r2199/e14696 | L@10 | save → L@11 |
| 2026-06-22 08:27:05 | @12; r2200/e14738 | L@11 | save → L@12 |
| 2026-06-22 08:27:59 | @13; r2201/e14742 | L@12 | save → L@13 |
| 2026-06-22 08:29:41 | @14; r2202/e14751 | L@13 | save → L@14 |
| 2026-06-22 08:30:05 | @15; r2203/e14757 | L@14 | save → L@15 |
| 2026-06-22 08:31:28 | @16; r2204/e14766 | L@15 | save → L@16 |
| 2026-06-22 08:34:38 | @17; r2205/e14790 | L@16 | save → L@17 |
| 2026-06-22 08:37:04 | @18; r2206/e14814 | L@17 | save → L@18 |
| 2026-06-22 08:37:09 | @19; r2207/e14816 | L@18 | save → L@19 |
| 2026-06-22 08:37:23 | @20; r2208/e14819 | L@19 | save → L@20 |
| 2026-06-22 08:38:23 | @21; r2209/e14839 | L@20 | save → L@21 |
| 2026-06-22 08:39:06 | @22; r2210/e14860 | {L@21,L@23} | save → L@22; P22/23 |
| 2026-06-22 08:39:06 | @23; r2211/e14861 | {L@21,L@22} | save → L@23; P22/23 |
| 2026-06-22 08:39:31 | @24; r2212/e14871 | {L@22,L@23} | save → L@24 |
| 2026-06-22 08:40:49 | @25; r2213/e14890 | L@24 | save → L@25 |
| 2026-06-22 08:41:13 | @26; r2214/e14900 | L@25 | save → L@26 |
| 2026-06-22 08:42:24 | @27; r2215/e14926 | L@26 | save → L@27 |
| 2026-06-22 08:43:15 | @28; r2216/e14947 | L@27 | save → L@28 |
| 2026-06-22 08:43:33 | @29; r2217/e14958 | L@28 | save → L@29 |
| 2026-06-22 08:44:20 | @30; r2218/e14977 | L@29 | save → L@30 |
| 2026-06-22 08:44:59 | @31; r2219/e14989 | L@30 | save → L@31 |
| 2026-06-22 08:46:32 | @32; r2220/e15017 | L@31 | save → L@32 |
| 2026-06-22 08:47:02 | @33; r2221/e15021 | L@32 | save → L@33 |
| 2026-06-22 08:48:09 | @34; r2222/e15031 | L@33 | save → L@34 |
| 2026-06-22 08:50:48 | @35; r2223/e15051 | L@34 | save → L@35 |
| 2026-06-26 16:45:23 | delete:dse:rclog:151929; e16354 | L@35 | successful delete → deleted; L1 ends |

**P22/23 — unresolved order, high confidence in ambiguity, not a random choice.** Both rows have selected time, request time, success time and write date exactly 08:39:06, u=1. @22 is 1,126 bytes, @23 2,054 bytes with different hashes. RCS 1.22→1.23, diff-base @22, and @22's archive time of 08:39:06 are provenance clues for storage sequence, not independently established public mutation order. @23 largely returns to an older textual scaffold with new filtered queries; content alone does not prove it consumed @22.

Allowed nominal paths: L@21 → L@22 → L@23 **or** L@21 → L@23 → L@22, then either → L@24. Immediately after the group at nominal t, admissible states {L@22,L@23}; no union/merged body. In the +/-1s window, L@21 is also possible before either save. After 08:39:07 and before @24's uncertainty window, retain both post-group possibilities. Once @24 applies, the branches converge. No episode split at the tie. Exact scoring cannot choose @23 solely by seq/ID. Ask Sam whether additional raw evidence resolves physical ordering; otherwise freeze the ambiguity, not an arbitrary winner.

@3 archive at 08:14:23 leaves L@3, despite a next held save only at 08:14:53. @35 archive 2026-06-26 16:45:22 leaves L@35. Neither is a mutation. At T modeled `deleted`; archive persistence and intervening missing bodies U.

## 10b — simple released-trace control: AgentBridgeOct2142X

Page: [pages:148](../data/raw/export/pages.jsonl#L148).

| Timestamp UTC (2026-06-16) | Exact source record | Before | Event / after | Episode / order |
|---|---|---|---|---|
| 18:40:04 | save:dse~AgentBridgeOct2142X@1 + dse~AgentBridgeOct2142X@1; e1807/r301 | unknown | supported save → L@1 | L1 starts, left-censored; default exact |
| 18:43:13 | dse~AgentBridgeOct2142X@1 archived_at; r301; revision metadata | L@1 under A | archival marker → L@1 under A | no episode boundary; visibility U |

F: 205-byte DataUSA API-link body; no subsequent mutation in the published population. R: ordinary link material is useful as an uncomplicated control. M+A: L@1 carries to T and is right-censored. **Not** evidence that no later edit/deletion occurred, nor that a historical final GET would return this body. Confidence high in the held body and absence of further *published rows*, not in uninterrupted availability. Even this control has an archival operation without a published replacement: archive time alone must not end visibility.

## SAFE TIMELINE RULES

These recommendations are provisional until independent comparison. SAFE means safe within the stated data/model layer, never unconditional historical HTTP ground truth.

| Proposed rule | Classification | Reason / boundary of permission |
|---|---|---|
| A validated held save installs `live(body_ref)` at selected `time` in the conditional model | **SAFE ONLY AS MODELING ASSUMPTION** | F establishes held text and supported save, but exact public availability, clock selection and missing intervening edits are not proven. Preserve all clock provenance; never use request-only evidence as a save. |
| A successful exported deletion installs `deleted` in the live-page model | **SAFE ONLY AS MODELING ASSUMPTION** | Native success supports the deletion action; public GET/cache and archive consequences are separate. Use success-selected clock, not archive/request time. |
| A successful, page-addressed body-unavailable mutation installs `live(body_unknown)` | **SAFE ONLY AS MODELING ASSUMPTION** | Supported for the audited successful post-deletion form_edit population; “live” is the abstraction. Do not generalize all native actions/null revision refs to live writes. |
| Known unavailable body remains unknown; never return an earlier guessed body/empty text | **SAFE** | Missing body is an epistemic limit. PoliceBridge demonstrates the distinction. No-body events with unsupported action semantics require review, not a broad auto-rule. |
| A supported save/body-unknown edit following deletion starts a new modeled episode; ordinary saves do not | **SAFE ONLY AS MODELING ASSUMPTION** | This is an episode definition under trace continuity. Actual first recreation may be unheld/fallback-linked; start no earlier than supported timing permits. |
| Initial state is `unknown`; first held save can start a left-censored segment | **SAFE** | Conservative lack-of-knowledge representation. `seq=1`/page_created/zero pre-cut count cannot establish first-ever creation. |
| Relation edges provide provenance/context but never independently mutate state, duplicate an event, or backdate a body | **SAFE** | Manifest describes derived associations, including fallbacks. Store all scalar/list/null edges; matching does not license earlier content. A separately supported timed mutation is handled on its own evidence. |
| Carry each modeled state until next supported mutation or censoring | **SAFE ONLY AS MODELING ASSUMPTION** | Requires explicit no-unobserved-intervening-mutation A; applies to deleted as well as live. Known missing mutations interrupt carry. Unknown gaps may require exclusion/bounds; A is not proved by absent rows. |
| Detect a missing successful body-changing mutation at known t and invalidate old body there | **SAFE** | Retain uncertainty about resulting state if action semantics are unknown; a supported live edit yields BU. Do not manufacture t from head mismatch or archival metadata. |
| Read current modeled state at read/response time, not the trigger's revision | **SAFE** | Prevents retrospective fetch privilege. Choice of response delay/atomic-read convention remains modeling, not measured latency. |
| Use [start,end), apply unambiguous mutations before reads at equal t | **SAFE ONLY AS MODELING ASSUMPTION** | Deterministic interface convention; cannot resolve incompatible tied mutations. |
| Preserve partial orders/admissible states for tied or overlapping incompatible events | **SAFE** | Do not conflate serialization with chronology. Each realization uses one of the four states; alternatives are evaluator uncertainty. |
| Resolve same-second saves solely by seq, diff_base, RCS revision, archived_at, or event-ID order | **UNSAFE** | Storage/diff ordering and exporter serialization do not independently establish historical publication order. A documented source guarantee could justify a narrower future rule. |
| Treat `uncertainty_seconds=1` as a publisher-guaranteed symmetric +/-1s interval | **UNRESOLVED** | Interval convention, clock error versus resolution, and cross-event correlation are undocumented. |
| Use +/-1s movement (including conservative touching-window ambiguity) as labeled sensitivity | **SAFE ONLY AS MODELING ASSUMPTION** | Conservative project test, not a confidence interval or guarantee that truth lies inside it. |
| `deleted_live`, txt/dw or head/live mismatch determine historical survival/body | **UNSAFE** | Untimed store descriptors cannot override successful deletions or identify missing mutation dates. Exact field semantics remain unresolved. |
| `archived_at` starts public archive access or ends live visibility | **UNRESOLVED** | Storage clock known; access meaning not known. Encoding either as a historical transition now is unsafe. |
| A successful request/probe or an agent's success sentence establishes unrelated external success | **UNSAFE** | Action success has narrow scope; probes need not mutate pages; text is testimony. |
| Later cumulative/copy bodies may support earlier propositions when actually captured later | **SAFE** | Evaluator occurrence validation, not a state backfill. Register spans/context and count distinct propositions once. No future occurrence may be delivered as an earlier observation. |

## Adjudication agenda and release boundary

1. Compare all ten independent packets, including state immediately before/at/after each boundary, source clocks, hashes, episode censoring, and allowed orders. Initial agreement is **not yet measured**. A mutually agreed ambiguity is acceptable; unresolved differences affecting a scored capture are not.
2. Resolve P22/23 storage order versus public order, P56 touching-window handling, and same-time read convention without software output. Keep bounds/exclusion fallback.
3. Confirm no-body success versus restored body, pre-first-deletion unknowns, and recreation links without identifiable fallback flags. Do not certify exact historical downtime from these gaps.
4. Adjudicate AI legacy/head mismatch, the archive-only markers even in the simple control, and whether any primary exact eligible histories remain defensible. A metadata contradiction flags evaluator eligibility; it must not leak into past observations.
5. Compare the @4/@5 workaround occurrence distinction and @13/@14 claim distinction. Freeze semantic units and criticality only with A03 review and whole-DSE support search; no policy outcomes.
6. After preserving both submissions, Sam designates two held-back **software** fixtures before Ubayd sees their expected outputs. This document is research comparison material, not permission to expose every blind expectation to E06. Reserve access separately; no blind-test success is claimed here.

**Recommendation: CONDITIONAL GO for comparison/adjudication and preparation only. E06 waits for E05 + accepted V02 fixtures + R04. Collectors/experiments remain stopped.** If historical continuity/visibility cannot be supported, declare a trace-grounded simulation before producing results. Unanswered outreach does not block that honestly labeled fallback.

## Source appendix — exact IDs, hashes and clocks

The source-only transcription below is joined to the manually authored boundary tables above. No state is inferred by this appendix. For every save, it supplies the exact event ID, exact body reference/hash, raw source links, selected timestamp, request/success/write/archive clocks, grade and uncertainty. For native events it supplies exact source_refs and null-body status. All archive entries are provenance markers, not additional successful-mutation rows; they never independently alter a state or episode. See case notes for meaningful archive/visibility discrepancies. No third-party body excerpts are redistributed in this appendix.

Source-body byte/hash check: **141/141 match** using each declared encoding. This validates released bytes, not historical visibility.

Expanded-file fingerprints independently recomputed in this pass:

| File | SHA-256 |
|---|---|
| pages.jsonl | `92b296170b496b836cdf5ef783bed9465d2d75db7e1a0becec1c36c8b7c42cfd` |
| revisions.jsonl | `60df4a515178230aa952d9f64f6215aea4bd95ab2f05e31e484cf9b887e3f793` |
| events.jsonl | `588584295f1c4a7c3d90b04075ab151504f165ff069534d935cda08853ec28b1` |
| labels.jsonl | `d94aecd84baecda46344f5b8726a95a9c81e7e41a1c0969fc89a90c8906f0388` |
| manifest.json | `b6d53e16b5d9a6a0a98d4577238835ee7a574d7d10a8f1312330b4e626c6ba2b` |

### Raw ledger: DataUSAConstructionWageSep18Live

All timestamps UTC. Each `save` is one mutation with two linked source records, not two mutations. `t` in a clock cell means the selected timestamp in that row. Grade/u/winner are copied, not inferred.

| Selected timestamp | Exact event ID / type / source | Body reference and SHA-256 | Clocks and native evidence |
|---|---|---|---|
| 2026-06-19T12:40:34Z | [`save:dse~DataUSAConstructionWageSep18Live@1`](../data/raw/export/events.jsonl#L12031); save; e12031 | [`dse~DataUSAConstructionWageSep18Live@1`](../data/raw/export/revisions.jsonl#L5104); r5104; `9c42e64f789f87d0a418dc13a29266c246d6fe7c600ef69c17fe964fcf501f89`; 392 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T12:47:09Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T12:47:08Z | [`save:dse~DataUSAConstructionWageSep18Live@2`](../data/raw/export/events.jsonl#L12037); save; e12037 | [`dse~DataUSAConstructionWageSep18Live@2`](../data/raw/export/revisions.jsonl#L5105); r5105; `cfe0e5d6d095b19d1238a7da97769dfeacac33397b206151c6e985566a2a0483`; 715 bytes (ascii) | request_time=t; success_time=2026-06-19T12:47:09Z; write_date=t; archived_at=2026-06-19T12:55:48Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T12:55:48Z | [`save:dse~DataUSAConstructionWageSep18Live@3`](../data/raw/export/events.jsonl#L12043); save; e12043 | [`dse~DataUSAConstructionWageSep18Live@3`](../data/raw/export/revisions.jsonl#L5106); r5106; `66f51a3b183f71ff8546db68f03c3379d94872c0a4e10e4059dfc329f80326cd`; 940 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T12:59:09Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T12:59:09Z | [`save:dse~DataUSAConstructionWageSep18Live@4`](../data/raw/export/events.jsonl#L12046); save; e12046 | [`dse~DataUSAConstructionWageSep18Live@4`](../data/raw/export/revisions.jsonl#L5107); r5107; `29783d6b3e04fdff621734ff45e682cb5ccc2bee6cd5f9e1460b66d3ed9af2d3`; 1196 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T13:02:27Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T13:02:26Z | [`save:dse~DataUSAConstructionWageSep18Live@5`](../data/raw/export/events.jsonl#L12053); save; e12053 | [`dse~DataUSAConstructionWageSep18Live@5`](../data/raw/export/revisions.jsonl#L5108); r5108; `9b51dbfdabe2d0e3ea05f49588a0ef0c065e7332f52bb55f391969c51637194c`; 1405 bytes (ascii) | request_time=t; success_time=2026-06-19T13:02:27Z; write_date=t; archived_at=2026-06-19T13:06:18Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T13:06:18Z | [`save:dse~DataUSAConstructionWageSep18Live@6`](../data/raw/export/events.jsonl#L12055); save; e12055 | [`dse~DataUSAConstructionWageSep18Live@6`](../data/raw/export/revisions.jsonl#L5109); r5109; `6e44799190dabd69ce124553493d25209292d96910887dbbe67e024d943221de`; 1604 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T13:10:10Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T13:10:09Z | [`save:dse~DataUSAConstructionWageSep18Live@7`](../data/raw/export/events.jsonl#L12059); save; e12059 | [`dse~DataUSAConstructionWageSep18Live@7`](../data/raw/export/revisions.jsonl#L5110); r5110; `5ca32a6dc897d7c9bbb36ef69e197c84908b3e67bdf96fd2692ce0dee64b9270`; 1834 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T13:13:23Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T13:13:23Z | [`save:dse~DataUSAConstructionWageSep18Live@8`](../data/raw/export/events.jsonl#L12062); save; e12062 | [`dse~DataUSAConstructionWageSep18Live@8`](../data/raw/export/revisions.jsonl#L5111); r5111; `8fde8d8e739b1bab540134a082f5d0d9dd03a0aa85e9d10c882248d9952bc020`; 2022 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T13:16:19Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T13:16:18Z | [`save:dse~DataUSAConstructionWageSep18Live@9`](../data/raw/export/events.jsonl#L12064); save; e12064 | [`dse~DataUSAConstructionWageSep18Live@9`](../data/raw/export/revisions.jsonl#L5112); r5112; `0477ae07ab815851f3b97886121e582c809088c560bba3c19aeaf0a34b965c66`; 2304 bytes (ascii) | request_time=t; success_time=2026-06-19T13:16:19Z; write_date=t; archived_at=2026-06-19T13:16:54Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T13:16:54Z | [`save:dse~DataUSAConstructionWageSep18Live@10`](../data/raw/export/events.jsonl#L12065); save; e12065 | [`dse~DataUSAConstructionWageSep18Live@10`](../data/raw/export/revisions.jsonl#L5113); r5113; `3276973eda58a200449f429427b0355886ef7bb15e62b688e47993ac41d6dd1a`; 2434 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T13:22:25Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T13:22:25Z | [`save:dse~DataUSAConstructionWageSep18Live@11`](../data/raw/export/events.jsonl#L12070); save; e12070 | [`dse~DataUSAConstructionWageSep18Live@11`](../data/raw/export/revisions.jsonl#L5114); r5114; `7155b876704206ecef3a8806df32d3f9c56a8222a643544219f2bdc97726caf0`; 2610 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T13:27:33Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T13:27:33Z | [`save:dse~DataUSAConstructionWageSep18Live@12`](../data/raw/export/events.jsonl#L12075); save; e12075 | [`dse~DataUSAConstructionWageSep18Live@12`](../data/raw/export/revisions.jsonl#L5115); r5115; `cf60366cbc4c510f757416a8c4dceef18d9dd4191ee20798be5d20f3dc8d841a`; 2859 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T13:38:52Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T13:38:52Z | [`save:dse~DataUSAConstructionWageSep18Live@13`](../data/raw/export/events.jsonl#L12117); save; e12117 | [`dse~DataUSAConstructionWageSep18Live@13`](../data/raw/export/revisions.jsonl#L5116); r5116; `32d9d1fb0e3189e3b6561b7a3d903174c31519fa13e85b318eb48bbc1547e9bb`; 3166 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T13:40:55Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T13:40:55Z | [`save:dse~DataUSAConstructionWageSep18Live@14`](../data/raw/export/events.jsonl#L12123); save; e12123 | [`dse~DataUSAConstructionWageSep18Live@14`](../data/raw/export/revisions.jsonl#L5117); r5117; `19bed52c54c0c35def9897ab48e7c126280e71f650295814a0b42dff364ee0a2`; 3380 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T13:45:21Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T13:45:21Z | [`save:dse~DataUSAConstructionWageSep18Live@15`](../data/raw/export/events.jsonl#L12124); save; e12124 | [`dse~DataUSAConstructionWageSep18Live@15`](../data/raw/export/revisions.jsonl#L5118); r5118; `260b36ec6cdcd01b0ac508b673ed99669a98dd895c67f2c2a37d6c1fc442fe71`; 3386 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T14:05:02Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T14:05:02Z | [`save:dse~DataUSAConstructionWageSep18Live@16`](../data/raw/export/events.jsonl#L12174); save; e12174 | [`dse~DataUSAConstructionWageSep18Live@16`](../data/raw/export/revisions.jsonl#L5119); r5119; `7392f790b5b31d482eb79edb8fe6c6948efb470c7c513006c354a205fc7422e3`; 3639 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T14:07:45Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T14:07:45Z | [`save:dse~DataUSAConstructionWageSep18Live@17`](../data/raw/export/events.jsonl#L12176); save; e12176 | [`dse~DataUSAConstructionWageSep18Live@17`](../data/raw/export/revisions.jsonl#L5120); r5120; `2194115ccaae215228da6e5bcbef629b0a00f5ff5b86a462835b50b5aab7b18f`; 3903 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T14:08:33Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T14:08:33Z | [`save:dse~DataUSAConstructionWageSep18Live@18`](../data/raw/export/events.jsonl#L12177); save; e12177 | [`dse~DataUSAConstructionWageSep18Live@18`](../data/raw/export/revisions.jsonl#L5121); r5121; `c7fcb6316e2dba4762ec9f39865f1258b3618066688cd24a8e383da0e97507fc`; 4166 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T14:09:03Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T14:09:03Z | [`save:dse~DataUSAConstructionWageSep18Live@19`](../data/raw/export/events.jsonl#L12178); save; e12178 | [`dse~DataUSAConstructionWageSep18Live@19`](../data/raw/export/revisions.jsonl#L5122); r5122; `6bee94a69e5bc448256f9867fedb941d5596b40aac7fe9c012162273d599d7cf`; 4373 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T14:09:51Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T14:09:51Z | [`save:dse~DataUSAConstructionWageSep18Live@20`](../data/raw/export/events.jsonl#L12180); save; e12180 | [`dse~DataUSAConstructionWageSep18Live@20`](../data/raw/export/revisions.jsonl#L5123); r5123; `0e889487bcc3d93d66de411036aa68d1b7266eb7c9d32788c765f0ced8a859de`; 4637 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T14:10:25Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T14:10:25Z | [`save:dse~DataUSAConstructionWageSep18Live@21`](../data/raw/export/events.jsonl#L12182); save; e12182 | [`dse~DataUSAConstructionWageSep18Live@21`](../data/raw/export/revisions.jsonl#L5124); r5124; `b1a25090606538a235effdc7a731988ba8d275cde7e1ddd3a218a28c413fba5e`; 4879 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T14:10:49Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T14:10:49Z | [`save:dse~DataUSAConstructionWageSep18Live@22`](../data/raw/export/events.jsonl#L12183); save; e12183 | [`dse~DataUSAConstructionWageSep18Live@22`](../data/raw/export/revisions.jsonl#L5125); r5125; `1b392e622a75d101c3e84e49a443e52dff6140b00ce3c7b1dd609ee9d5066c75`; 5063 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T14:11:26Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T14:11:26Z | [`save:dse~DataUSAConstructionWageSep18Live@23`](../data/raw/export/events.jsonl#L12185); save; e12185 | [`dse~DataUSAConstructionWageSep18Live@23`](../data/raw/export/revisions.jsonl#L5126); r5126; `64f8975046cd256c700ed1b7e5e6aa5dcf6335fb135a0faf1db6a3d1266dbe43`; 5308 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T14:12:11Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T14:12:11Z | [`save:dse~DataUSAConstructionWageSep18Live@24`](../data/raw/export/events.jsonl#L12187); save; e12187 | [`dse~DataUSAConstructionWageSep18Live@24`](../data/raw/export/revisions.jsonl#L5127); r5127; `c014c19b9920993c43177577488c3501b2d6bd36923835b4de93bec01d0994d4`; 5569 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T14:14:03Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T14:14:03Z | [`save:dse~DataUSAConstructionWageSep18Live@25`](../data/raw/export/events.jsonl#L12190); save; e12190 | [`dse~DataUSAConstructionWageSep18Live@25`](../data/raw/export/revisions.jsonl#L5128); r5128; `f15cf7067ad1ddee8c62aae8f33ee55d28d77958cb77df9d44fdb867114ca9f7`; 5828 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T14:14:50Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T14:14:50Z | [`save:dse~DataUSAConstructionWageSep18Live@26`](../data/raw/export/events.jsonl#L12191); save; e12191 | [`dse~DataUSAConstructionWageSep18Live@26`](../data/raw/export/revisions.jsonl#L5129); r5129; `6cf2e4db838c9c2f9201ef172332a2a0986bb0ccc84b42659ef0ca5523c47ef2`; 6027 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T14:14:55Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T14:14:55Z | [`save:dse~DataUSAConstructionWageSep18Live@27`](../data/raw/export/events.jsonl#L12192); save; e12192 | [`dse~DataUSAConstructionWageSep18Live@27`](../data/raw/export/revisions.jsonl#L5130); r5130; `9e707b67ba691c059cfb21523b8dd9b245aa16c634a4146daa717ca0aeede356`; 6216 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T14:15:35Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T14:15:35Z | [`save:dse~DataUSAConstructionWageSep18Live@28`](../data/raw/export/events.jsonl#L12193); save; e12193 | [`dse~DataUSAConstructionWageSep18Live@28`](../data/raw/export/revisions.jsonl#L5131); r5131; `965a02f5c1399964baa6e8e74af41b70da2e56b925f3b9c2980e4b33b6e82f30`; 6370 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T14:17:40Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T14:17:40Z | [`save:dse~DataUSAConstructionWageSep18Live@29`](../data/raw/export/events.jsonl#L12197); save; e12197 | [`dse~DataUSAConstructionWageSep18Live@29`](../data/raw/export/revisions.jsonl#L5132); r5132; `313b37617573ad480e63fc358751c2ef6b39e60b97311a7913517a719685390f`; 6377 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T14:19:47Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T14:37:47Z | [`save:dse~DataUSAConstructionWageSep18Live@30`](../data/raw/export/events.jsonl#L12206); save; e12206 | [`dse~DataUSAConstructionWageSep18Live@30`](../data/raw/export/revisions.jsonl#L5133); r5133; `98774b10f83fcb23f9d9daa9c3c83e226b7db6c28fc9d6ef4f40cc65a222d8b6`; 6781 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T15:46:25Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T15:46:37Z | [`delete:dse:rclog:145609`](../data/raw/export/events.jsonl#L12231); delete; e12231 | revision_ref=null; no supported body hash | request_time=t; success_time=t; reqlog/u=1/rclog.unix_ts; success_observed=True; action=delete; `corpus/live/rclog.jsonl:145609`; `corpus/live/reqlog_dse_2606.jsonl:1415545` |

### Raw ledger: ZZZDataUSAConstructionWageLive

All timestamps UTC. Each `save` is one mutation with two linked source records, not two mutations. `t` in a clock cell means the selected timestamp in that row. Grade/u/winner are copied, not inferred.

| Selected timestamp | Exact event ID / type / source | Body reference and SHA-256 | Clocks and native evidence |
|---|---|---|---|
| 2026-06-19T14:06:38Z | [`save:dse~ZZZDataUSAConstructionWageLive@1`](../data/raw/export/events.jsonl#L12175); save; e12175 | [`dse~ZZZDataUSAConstructionWageLive@1`](../data/raw/export/revisions.jsonl#L13354); r13354; `92a63d1acfe7f3f32198edea4568b71afaef43496c87fa48076622cc6694ad11`; 427 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T14:09:40Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T14:09:40Z | [`save:dse~ZZZDataUSAConstructionWageLive@2`](../data/raw/export/events.jsonl#L12179); save; e12179 | [`dse~ZZZDataUSAConstructionWageLive@2`](../data/raw/export/revisions.jsonl#L13355); r13355; `35b4ccbe82a885afb4b18a4fa4a5f14a8e1c9608cf88c9ef42169758279cb846`; 638 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T14:11:09Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T14:11:08Z | [`save:dse~ZZZDataUSAConstructionWageLive@3`](../data/raw/export/events.jsonl#L12184); save; e12184 | [`dse~ZZZDataUSAConstructionWageLive@3`](../data/raw/export/revisions.jsonl#L13356); r13356; `df35d522f84d029faea2c631681981d54ac45d4a9ba63c91cc2c96c827de9128`; 765 bytes (ascii) | request_time=t; success_time=2026-06-19T14:11:09Z; write_date=t; archived_at=2026-06-19T14:13:28Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T14:13:28Z | [`save:dse~ZZZDataUSAConstructionWageLive@4`](../data/raw/export/events.jsonl#L12188); save; e12188 | [`dse~ZZZDataUSAConstructionWageLive@4`](../data/raw/export/revisions.jsonl#L13357); r13357; `fd22b3de364929768cae8474f6d145a3e78c3914c2d3cc0e4d3e1cfadb84a975`; 1025 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T14:13:54Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T14:13:54Z | [`save:dse~ZZZDataUSAConstructionWageLive@5`](../data/raw/export/events.jsonl#L12189); save; e12189 | [`dse~ZZZDataUSAConstructionWageLive@5`](../data/raw/export/revisions.jsonl#L13358); r13358; `5b7e7506d70d9010862815727890a0429c354b0e33e8f61baa33bfc44cf8dd1d`; 1204 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T14:16:11Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T14:16:11Z | [`save:dse~ZZZDataUSAConstructionWageLive@6`](../data/raw/export/events.jsonl#L12194); save; e12194 | [`dse~ZZZDataUSAConstructionWageLive@6`](../data/raw/export/revisions.jsonl#L13359); r13359; `44d6f27bb5d7174d4feed0bdb4371eb3c2d89a5b1dfe8c3611f07b4bcc9ee523`; 1311 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T14:28:22Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T14:28:22Z | [`save:dse~ZZZDataUSAConstructionWageLive@7`](../data/raw/export/events.jsonl#L12203); save; e12203 | [`dse~ZZZDataUSAConstructionWageLive@7`](../data/raw/export/revisions.jsonl#L13360); r13360; `f235061b3ea86d5b38b573bec67d28cb1958f469d6b376427785226780514b5e`; 1487 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T14:38:50Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T14:38:50Z | [`save:dse~ZZZDataUSAConstructionWageLive@8`](../data/raw/export/events.jsonl#L12207); save; e12207 | [`dse~ZZZDataUSAConstructionWageLive@8`](../data/raw/export/revisions.jsonl#L13361); r13361; `893f3924ffc735d3395e1ed5fb84e84d8b2d2be9f2e6fd55dccdd97595a7e18e`; 1657 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T14:40:18Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T14:40:18Z | [`save:dse~ZZZDataUSAConstructionWageLive@9`](../data/raw/export/events.jsonl#L12208); save; e12208 | [`dse~ZZZDataUSAConstructionWageLive@9`](../data/raw/export/revisions.jsonl#L13362); r13362; `b6502135e22ab5ac1a7041994b6bb8966c2a620fdaa1ec9c94334e67baf19f52`; 1910 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T14:41:48Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T14:44:31Z | [`save:dse~ZZZDataUSAConstructionWageLive@10`](../data/raw/export/events.jsonl#L12209); save; e12209 | [`dse~ZZZDataUSAConstructionWageLive@10`](../data/raw/export/revisions.jsonl#L13363); r13363; `dc5f5eb2f7c3b65c53c86b44f35e44371534dda12157621fa33ddc6e20fa2548`; 2245 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T15:46:47Z; reqlog/u=1/revision.pref_ts |
| 2026-06-19T15:46:49Z | [`delete:dse:rclog:145611`](../data/raw/export/events.jsonl#L12232); delete; e12232 | revision_ref=null; no supported body hash | request_time=t; success_time=t; reqlog/u=1/rclog.unix_ts; success_observed=True; action=delete; `corpus/live/rclog.jsonl:145611`; `corpus/live/reqlog_dse_2606.jsonl:1415565` |

### Raw ledger: AgentLinkma21JuneAA

All timestamps UTC. Each `save` is one mutation with two linked source records, not two mutations. `t` in a clock cell means the selected timestamp in that row. Grade/u/winner are copied, not inferred.

| Selected timestamp | Exact event ID / type / source | Body reference and SHA-256 | Clocks and native evidence |
|---|---|---|---|
| 2026-06-18T16:00:51Z | [`save:dse~AgentLinkma21JuneAA@1`](../data/raw/export/events.jsonl#L5451); save; e5451 | [`dse~AgentLinkma21JuneAA@1`](../data/raw/export/revisions.jsonl#L1642); r1642; `e7c9c7f1f90127e11d5e0367a06d720a9f47396f64300974a377ed2aff9084ab`; 1241 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-18T16:37:13Z; reqlog/u=1/revision.pref_ts |
| 2026-06-18T16:37:13Z | [`save:dse~AgentLinkma21JuneAA@2`](../data/raw/export/events.jsonl#L5538); save; e5538 | [`dse~AgentLinkma21JuneAA@2`](../data/raw/export/revisions.jsonl#L1643); r1643; `ce461b2bd398e97276d696ee45ca43755d3d76bab6f1d83e7b62eb3c3e22424f`; 1542 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-18T16:38:26Z; reqlog/u=1/revision.pref_ts |
| 2026-06-18T16:38:25Z | [`save:dse~AgentLinkma21JuneAA@3`](../data/raw/export/events.jsonl#L5545); save; e5545 | [`dse~AgentLinkma21JuneAA@3`](../data/raw/export/revisions.jsonl#L1644); r1644; `a54d2aec0303e6c150e5770d08570f828fc3b2d8958ae90300514a38b9591add`; 2722 bytes (ascii) | request_time=t; success_time=2026-06-18T16:38:26Z; write_date=t; archived_at=2026-06-18T16:40:33Z; reqlog/u=1/revision.pref_ts |
| 2026-06-18T16:40:33Z | [`save:dse~AgentLinkma21JuneAA@4`](../data/raw/export/events.jsonl#L5563); save; e5563 | [`dse~AgentLinkma21JuneAA@4`](../data/raw/export/revisions.jsonl#L1645); r1645; `2a89f3e8f45f6c02d0151efa1efe294f17c3275d1c6466419f28d303b1041833`; 3560 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-18T16:48:23Z; reqlog/u=1/revision.pref_ts |
| 2026-06-18T16:48:23Z | [`save:dse~AgentLinkma21JuneAA@5`](../data/raw/export/events.jsonl#L5603); save; e5603 | [`dse~AgentLinkma21JuneAA@5`](../data/raw/export/revisions.jsonl#L1646); r1646; `bf7f222051791bd840e3f29f4fa210de1982e6f953678a380196916508fcb6d3`; 4130 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-18T16:48:45Z; reqlog/u=1/revision.pref_ts |
| 2026-06-18T16:48:45Z | [`save:dse~AgentLinkma21JuneAA@6`](../data/raw/export/events.jsonl#L5608); save; e5608 | [`dse~AgentLinkma21JuneAA@6`](../data/raw/export/revisions.jsonl#L1647); r1647; `d53eba0fcff6395f6855dbf0dc54e8abf7b934bd769dd8fa97806b631cb53386`; 5332 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-18T16:58:28Z; reqlog/u=1/revision.pref_ts |
| 2026-06-18T16:58:28Z | [`save:dse~AgentLinkma21JuneAA@7`](../data/raw/export/events.jsonl#L5658); save; e5658 | [`dse~AgentLinkma21JuneAA@7`](../data/raw/export/revisions.jsonl#L1648); r1648; `cc0a85bd900b8a305a39b37b2d8a30440c154462cefebc295e7fc18bb97d07c3`; 5968 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-18T17:05:29Z; reqlog/u=1/revision.pref_ts |
| 2026-06-18T17:05:29Z | [`save:dse~AgentLinkma21JuneAA@8`](../data/raw/export/events.jsonl#L5688); save; e5688 | [`dse~AgentLinkma21JuneAA@8`](../data/raw/export/revisions.jsonl#L1649); r1649; `bf32a5789c41a7cf502164736634b58c35f0669d6716ff7181daff1b8a670618`; 9364 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-18T17:06:16Z; reqlog/u=1/revision.pref_ts |
| 2026-06-18T17:06:16Z | [`save:dse~AgentLinkma21JuneAA@9`](../data/raw/export/events.jsonl#L5691); save; e5691 | [`dse~AgentLinkma21JuneAA@9`](../data/raw/export/revisions.jsonl#L1650); r1650; `e70a94c698ee7b032303572bb46a8b2ce9cf4d22b517e25d7ca962f7ed739be9`; 9425 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-18T17:27:08Z; reqlog/u=1/revision.pref_ts |
| 2026-06-18T17:27:08Z | [`save:dse~AgentLinkma21JuneAA@10`](../data/raw/export/events.jsonl#L5782); save; e5782 | [`dse~AgentLinkma21JuneAA@10`](../data/raw/export/revisions.jsonl#L1651); r1651; `ab8255ca174c1aa28e775bf283652588e917987496ad7782896eaf281675f09a`; 2606 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-18T17:28:54Z; reqlog/u=1/revision.pref_ts |
| 2026-06-18T17:28:54Z | [`save:dse~AgentLinkma21JuneAA@11`](../data/raw/export/events.jsonl#L5794); save; e5794 | [`dse~AgentLinkma21JuneAA@11`](../data/raw/export/revisions.jsonl#L1652); r1652; `f62c6dd4670ae4d2dc8b7ff45cba4fe3cafb675407e8dbd0a93db2c751548a62`; 401 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-18T17:38:22Z; reqlog/u=1/revision.pref_ts |
| 2026-06-18T17:38:22Z | [`save:dse~AgentLinkma21JuneAA@12`](../data/raw/export/events.jsonl#L5881); save; e5881 | [`dse~AgentLinkma21JuneAA@12`](../data/raw/export/revisions.jsonl#L1653); r1653; `27904e4e69a63655d41d246602357bb02b07dc0375f23e7a2c63a18d365ba487`; 1207 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-18T17:53:24Z; reqlog/u=1/revision.pref_ts |
| 2026-06-18T17:53:24Z | [`save:dse~AgentLinkma21JuneAA@13`](../data/raw/export/events.jsonl#L6034); save; e6034 | [`dse~AgentLinkma21JuneAA@13`](../data/raw/export/revisions.jsonl#L1654); r1654; `25448caf6e9e26557a56f426b8968d41aef2feac80f61e800237e83ce9fcdf15`; 656 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-18T18:17:51Z; reqlog/u=1/revision.pref_ts |
| 2026-06-18T18:17:51Z | [`save:dse~AgentLinkma21JuneAA@14`](../data/raw/export/events.jsonl#L6324); save; e6324 | [`dse~AgentLinkma21JuneAA@14`](../data/raw/export/revisions.jsonl#L1655); r1655; `66b08a6453039dca3ed794be5947eb53154305de669eb1179b15f114410b9038`; 551 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-18T18:26:11Z; reqlog/u=1/revision.pref_ts |
| 2026-06-18T18:26:11Z | [`save:dse~AgentLinkma21JuneAA@15`](../data/raw/export/events.jsonl#L6449); save; e6449 | [`dse~AgentLinkma21JuneAA@15`](../data/raw/export/revisions.jsonl#L1656); r1656; `0ce9394a642067a0401f692e5258c881505fe5791384a13259c571ff4240183e`; 633 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-18T18:26:21Z; reqlog/u=1/revision.pref_ts |
| 2026-06-18T18:26:23Z | [`delete:dse:rclog:138648`](../data/raw/export/events.jsonl#L6453); delete; e6453 | revision_ref=null; no supported body hash | request_time=t; success_time=t; reqlog/u=1/rclog.unix_ts; success_observed=True; action=delete; `corpus/live/rclog.jsonl:138648`; `corpus/live/reqlog_dse_2606.jsonl:1169010` |
| 2026-06-18T18:29:39Z | [`save:dse~AgentLinkma21JuneAA@16`](../data/raw/export/events.jsonl#L6517); save; e6517 | [`dse~AgentLinkma21JuneAA@16`](../data/raw/export/revisions.jsonl#L1657); r1657; `53336e74cc9c3249e7652a375fe70526928896c137732947484410316462e41a`; 804 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-18T19:16:59Z; reqlog/u=1/revision.pref_ts |
| 2026-06-18T19:16:58Z | [`save:dse~AgentLinkma21JuneAA@17`](../data/raw/export/events.jsonl#L7348); save; e7348 | [`dse~AgentLinkma21JuneAA@17`](../data/raw/export/revisions.jsonl#L1658); r1658; `4037c632d6bfd3cd68b67f32abab8be2a84afeb1cd2605bcb5a01450c939e4cd`; 823 bytes (ascii) | request_time=t; success_time=2026-06-18T19:16:59Z; write_date=t; archived_at=2026-06-18T19:18:22Z; reqlog/u=1/revision.pref_ts |
| 2026-06-18T19:18:22Z | [`save:dse~AgentLinkma21JuneAA@18`](../data/raw/export/events.jsonl#L7369); save; e7369 | [`dse~AgentLinkma21JuneAA@18`](../data/raw/export/revisions.jsonl#L1659); r1659; `d967a4f85a7286a6ed1179eadb4df7c7503d5dadb24c7b439c13ed8f9d4f5a14`; 1060 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-18T19:47:58Z; reqlog/u=1/revision.pref_ts |
| 2026-06-18T19:47:58Z | [`save:dse~AgentLinkma21JuneAA@19`](../data/raw/export/events.jsonl#L7996); save; e7996 | [`dse~AgentLinkma21JuneAA@19`](../data/raw/export/revisions.jsonl#L1660); r1660; `96d4c5a445a151e734ed2c3606dbdc53df0676f9076e1ec6c6352caa057419b4`; 808 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-18T19:50:33Z; reqlog/u=1/revision.pref_ts |
| 2026-06-18T19:50:30Z | [`save:dse~AgentLinkma21JuneAA@20`](../data/raw/export/events.jsonl#L8052); save; e8052 | [`dse~AgentLinkma21JuneAA@20`](../data/raw/export/revisions.jsonl#L1661); r1661; `278a3aa3b9a601f62119310ec3e2b62146f6f0301194aba9ae14a72d0b2cf56c`; 415 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-24T12:59:32Z; reqlog/u=1/revision.pref_ts |
| 2026-06-24T12:59:34Z | [`delete:dse:rclog:151031`](../data/raw/export/events.jsonl#L15863); delete; e15863 | revision_ref=null; no supported body hash | request_time=2026-06-24T12:59:33Z; success_time=t; reqlog/u=1/rclog.unix_ts; success_observed=True; action=delete; `corpus/live/rclog.jsonl:151031`; `corpus/live/reqlog_dse_2606.jsonl:1854239` |

### Raw ledger: AgentProxyCountyNext987111

All timestamps UTC. Each `save` is one mutation with two linked source records, not two mutations. `t` in a clock cell means the selected timestamp in that row. Grade/u/winner are copied, not inferred.

| Selected timestamp | Exact event ID / type / source | Body reference and SHA-256 | Clocks and native evidence |
|---|---|---|---|
| 2026-06-18T18:15:55Z | [`save:dse~AgentProxyCountyNext987111@1`](../data/raw/export/events.jsonl#L6306); save; e6306 | [`dse~AgentProxyCountyNext987111@1`](../data/raw/export/revisions.jsonl#L2942); r2942; `def08c7f4efa2bd59a16ce97cd76f6e9013db3002ed71de4a239ac4c366cc09d`; 341 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-18T18:18:24Z; reqlog/u=1/revision.pref_ts |
| 2026-06-18T18:18:24Z | [`save:dse~AgentProxyCountyNext987111@2`](../data/raw/export/events.jsonl#L6328); save; e6328 | [`dse~AgentProxyCountyNext987111@2`](../data/raw/export/revisions.jsonl#L2943); r2943; `7a5d15081caae2c50da32202b874480e76ec94f45ecf8e4846269fcd94532d79`; 631 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-18T18:20:27Z; reqlog/u=1/revision.pref_ts |
| 2026-06-18T18:20:27Z | [`save:dse~AgentProxyCountyNext987111@3`](../data/raw/export/events.jsonl#L6352); save; e6352 | [`dse~AgentProxyCountyNext987111@3`](../data/raw/export/revisions.jsonl#L2944); r2944; `ab03c2eeaf2e1a15516c12f2bc391c77621d7b0168a245d4b65abdb82379be9c`; 1420 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-18T18:23:11Z; reqlog/u=1/revision.pref_ts |
| 2026-06-18T18:23:13Z | [`delete:dse:rclog:138565`](../data/raw/export/events.jsonl#L6388); delete; e6388 | revision_ref=null; no supported body hash | request_time=t; success_time=t; reqlog/u=1/rclog.unix_ts; success_observed=True; action=delete; `corpus/live/rclog.jsonl:138565`; `corpus/live/reqlog_dse_2606.jsonl:1167566` |
| 2026-06-18T18:25:03Z | [`save:dse~AgentProxyCountyNext987111@4`](../data/raw/export/events.jsonl#L6430); save; e6430 | [`dse~AgentProxyCountyNext987111@4`](../data/raw/export/revisions.jsonl#L2945); r2945; `1bfca63d8f7f1800cebdd9db317c3ba1b25e8ac06429c64d2c26819a51f016b4`; 1985 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-18T18:25:19Z; reqlog/u=1/revision.pref_ts |
| 2026-06-18T18:25:22Z | [`delete:dse:rclog:138624`](../data/raw/export/events.jsonl#L6435); delete; e6435 | revision_ref=null; no supported body hash | request_time=t; success_time=t; reqlog/u=1/rclog.unix_ts; success_observed=True; action=delete; `corpus/live/rclog.jsonl:138624`; `corpus/live/reqlog_dse_2606.jsonl:1168541` |
| 2026-06-18T18:31:10Z | [`save:dse~AgentProxyCountyNext987111@5`](../data/raw/export/events.jsonl#L6550); save; e6550 | [`dse~AgentProxyCountyNext987111@5`](../data/raw/export/revisions.jsonl#L2946); r2946; `4de07df6b29db0e3cb74d7fffcd340e4038bbed4bef62bae6bcbeba71149563f`; 485 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-18T18:32:04Z; reqlog/u=1/revision.pref_ts |
| 2026-06-18T18:32:04Z | [`save:dse~AgentProxyCountyNext987111@6`](../data/raw/export/events.jsonl#L6564); save; e6564 | [`dse~AgentProxyCountyNext987111@6`](../data/raw/export/revisions.jsonl#L2947); r2947; `ae0aa41ef410cc60de3a0d2b1414c4737fa4dc784613f327bbd798609d996f52`; 1982 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-18T18:40:40Z; reqlog/u=1/revision.pref_ts |
| 2026-06-18T18:40:40Z | [`save:dse~AgentProxyCountyNext987111@7`](../data/raw/export/events.jsonl#L6700); save; e6700 | [`dse~AgentProxyCountyNext987111@7`](../data/raw/export/revisions.jsonl#L2948); r2948; `85cb62d7d66259177d81ad75065ced2d1a98da88f380f99dbe679e41bc83d973`; 5661 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-24T12:59:58Z; reqlog/u=1/revision.pref_ts |
| 2026-06-24T13:00:00Z | [`delete:dse:rclog:151035`](../data/raw/export/events.jsonl#L15865); delete; e15865 | revision_ref=null; no supported body hash | request_time=t; success_time=t; reqlog/u=1/rclog.unix_ts; success_observed=True; action=delete; `corpus/live/rclog.jsonl:151035`; `corpus/live/reqlog_dse_2606.jsonl:1854260` |

### Raw ledger: TestFoobaAgent

All timestamps UTC. Each `save` is one mutation with two linked source records, not two mutations. `t` in a clock cell means the selected timestamp in that row. Grade/u/winner are copied, not inferred.

| Selected timestamp | Exact event ID / type / source | Body reference and SHA-256 | Clocks and native evidence |
|---|---|---|---|
| 2026-06-04T10:53:40Z | [`delete:dse:rclog:131972`](../data/raw/export/events.jsonl#L1051); delete; e1051 | revision_ref=null; no supported body hash | request_time=t; success_time=t; reqlog/u=1/rclog.unix_ts; success_observed=True; action=delete; `corpus/live/rclog.jsonl:131972`; `corpus/live/reqlog_dse_2606.jsonl:32290` |
| 2026-06-08T04:03:23Z | [`save:dse~TestFoobaAgent@1`](../data/raw/export/events.jsonl#L1092); save; e1092 | [`dse~TestFoobaAgent@1`](../data/raw/export/revisions.jsonl#L10213); r10213; `f8f47cbe03cb08e2e63a3d532da2181a5adc988e7fce21f818db6063fcd93667`; 217 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-17T02:06:05Z; reqlog/u=1/revision.pref_ts |
| 2026-06-17T02:06:05Z | [`save:dse~TestFoobaAgent@2`](../data/raw/export/events.jsonl#L4181); save; e4181 | [`dse~TestFoobaAgent@2`](../data/raw/export/revisions.jsonl#L10214); r10214; `d0405ae9b9bedbb4520b7279f17da6275f219abe6afca7fa8430a2976f81d201`; 435 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-17T02:06:29Z; reqlog/u=1/revision.pref_ts |
| 2026-06-17T02:06:29Z | [`save:dse~TestFoobaAgent@3`](../data/raw/export/events.jsonl#L4185); save; e4185 | [`dse~TestFoobaAgent@3`](../data/raw/export/revisions.jsonl#L10215); r10215; `b43aa3addbe413254444e811e5343c0cfddd28e9feadfebb09747c33f1c5ecbf`; 246 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-17T02:11:54Z; reqlog/u=1/revision.pref_ts |
| 2026-06-17T02:11:54Z | [`save:dse~TestFoobaAgent@4`](../data/raw/export/events.jsonl#L4210); save; e4210 | [`dse~TestFoobaAgent@4`](../data/raw/export/revisions.jsonl#L10216); r10216; `5119ec635486d25cc5adc9a0c12c13de9550a669097b8806548ff16ba5c9a97a`; 313 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-18T18:45:02Z; reqlog/u=1/revision.pref_ts |
| 2026-06-18T18:45:02Z | [`save:dse~TestFoobaAgent@5`](../data/raw/export/events.jsonl#L6785); save; e6785 | [`dse~TestFoobaAgent@5`](../data/raw/export/revisions.jsonl#L10217); r10217; `f5c53544b6760e167274bdc484ff7ddd309093e1ef1294c4f1478c6f6054b61a`; 1796 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-24T12:35:17Z; reqlog/u=1/revision.pref_ts |
| 2026-06-24T12:35:19Z | [`delete:dse:rclog:151010`](../data/raw/export/events.jsonl#L15852); delete; e15852 | revision_ref=null; no supported body hash | request_time=2026-06-24T12:35:18Z; success_time=t; reqlog/u=1/rclog.unix_ts; success_observed=True; action=delete; `corpus/live/rclog.jsonl:151010`; `corpus/live/reqlog_dse_2606.jsonl:1853435` |

### Raw ledger: OpenAIDataUSAPoliceBridge20260129

All timestamps UTC. Each `save` is one mutation with two linked source records, not two mutations. `t` in a clock cell means the selected timestamp in that row. Grade/u/winner are copied, not inferred.

| Selected timestamp | Exact event ID / type / source | Body reference and SHA-256 | Clocks and native evidence |
|---|---|---|---|
| 2026-06-19T23:00:37Z | [`delete:dse:rclog:145962`](../data/raw/export/events.jsonl#L12452); delete; e12452 | revision_ref=null; no supported body hash | request_time=t; success_time=t; reqlog/u=1/rclog.unix_ts; success_observed=True; action=delete; `corpus/live/rclog.jsonl:145962`; `corpus/live/reqlog_dse_2606.jsonl:1442830` |
| 2026-06-19T23:19:13Z | [`revert:delete:dse:rclog:145962`](../data/raw/export/events.jsonl#L12498); revert; e12498 | revision_ref=null; no supported body hash | request_time=t; success_time=t; reqlog/u=1/rclog.unix_ts; success_observed=True; action=form_edit; `corpus/live/rclog.jsonl:146041`; `corpus/live/reqlog_dse_2606.jsonl:1444458` |
| 2026-06-19T23:40:56Z | [`delete:dse:rclog:146157`](../data/raw/export/events.jsonl#L12561); delete; e12561 | revision_ref=null; no supported body hash | request_time=2026-06-19T23:40:55Z; success_time=t; reqlog/u=1/rclog.unix_ts; success_observed=True; action=delete; `corpus/live/rclog.jsonl:146157`; `corpus/live/reqlog_dse_2606.jsonl:1448393` |

### Raw ledger: AgentOfficialDirectQueryAA3

All timestamps UTC. Each `save` is one mutation with two linked source records, not two mutations. `t` in a clock cell means the selected timestamp in that row. Grade/u/winner are copied, not inferred.

| Selected timestamp | Exact event ID / type / source | Body reference and SHA-256 | Clocks and native evidence |
|---|---|---|---|
| 2026-05-28T01:16:54Z | [`save:dse~AgentOfficialDirectQueryAA3@1`](../data/raw/export/events.jsonl#L573); save; e573 | [`dse~AgentOfficialDirectQueryAA3@1`](../data/raw/export/revisions.jsonl#L2457); r2457; `26b9aee12a0f198380dd6fb9f516f49589f2df37ef533f044eacfd315ab9e21e`; 211 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-24T10:43:34Z; reqlog/u=1/revision.pref_ts |
| 2026-06-24T10:43:36Z | [`delete:dse:rclog:150767`](../data/raw/export/events.jsonl#L15726); delete; e15726 | revision_ref=null; no supported body hash | request_time=None; success_time=t; rclog/u=1/rclog.unix_ts; success_observed=True; action=delete; `corpus/live/rclog.jsonl:150767`; `corpus/live/reqlog_dse_2606.jsonl:1850959`; `corpus/live/reqlog_dse_2606.jsonl:1850960`; note=ambiguous delete requests at -1/+1s |

### Raw ledger: OAIEquityDec30Raw

All timestamps UTC. Each `save` is one mutation with two linked source records, not two mutations. `t` in a clock cell means the selected timestamp in that row. Grade/u/winner are copied, not inferred.

| Selected timestamp | Exact event ID / type / source | Body reference and SHA-256 | Clocks and native evidence |
|---|---|---|---|
| 2026-06-20T05:03:37Z | [`save:dse~OAIEquityDec30Raw@1`](../data/raw/export/events.jsonl#L13004); save; e13004 | [`dse~OAIEquityDec30Raw@1`](../data/raw/export/revisions.jsonl#L7415); r7415; `89cca01fdfd07a0b602798aa15981d6bb0a78c093dbc39c0de2a71808c73a52d`; 581 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-20T05:09:10Z; reqlog/u=1/revision.pref_ts |
| 2026-06-20T05:09:10Z | [`save:dse~OAIEquityDec30Raw@2`](../data/raw/export/events.jsonl#L13014); save; e13014 | [`dse~OAIEquityDec30Raw@2`](../data/raw/export/revisions.jsonl#L7416); r7416; `1bce96e61d40424048dad2d0b0ca172d576e3262ccd217d5b5aabb7498d243ed`; 882 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-20T05:10:47Z; reqlog/u=1/revision.pref_ts |
| 2026-06-20T05:10:47Z | [`save:dse~OAIEquityDec30Raw@3`](../data/raw/export/events.jsonl#L13020); save; e13020 | [`dse~OAIEquityDec30Raw@3`](../data/raw/export/revisions.jsonl#L7417); r7417; `55a629f98172dd27afdfd9c16cdcebad616f79e5f4c0cf90e55ad7d5d232a3de`; 1198 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-20T05:17:46Z; reqlog/u=1/revision.pref_ts |
| 2026-06-20T05:17:46Z | [`save:dse~OAIEquityDec30Raw@4`](../data/raw/export/events.jsonl#L13023); save; e13023 | [`dse~OAIEquityDec30Raw@4`](../data/raw/export/revisions.jsonl#L7418); r7418; `2707f87c612636ffb24533e0d40f69c4394a7cfa1bc909e211cf234b2a79e059`; 1953 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-20T05:23:15Z; reqlog/u=1/revision.pref_ts |
| 2026-06-20T05:23:15Z | [`save:dse~OAIEquityDec30Raw@5`](../data/raw/export/events.jsonl#L13029); save; e13029 | [`dse~OAIEquityDec30Raw@5`](../data/raw/export/revisions.jsonl#L7419); r7419; `eefd1657d9205df39bdec785a1b959147f42f621ed098ec06dd7ffa28c5d349f`; 2281 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-20T05:28:29Z; reqlog/u=1/revision.pref_ts |
| 2026-06-20T05:28:29Z | [`save:dse~OAIEquityDec30Raw@6`](../data/raw/export/events.jsonl#L13034); save; e13034 | [`dse~OAIEquityDec30Raw@6`](../data/raw/export/revisions.jsonl#L7420); r7420; `cf6fe955579ecf4949d7fe765ff0d83c6d1bc246d59fb8f3145e10dbea888ce4`; 2703 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-20T05:37:25Z; reqlog/u=1/revision.pref_ts |
| 2026-06-20T05:37:25Z | [`save:dse~OAIEquityDec30Raw@7`](../data/raw/export/events.jsonl#L13042); save; e13042 | [`dse~OAIEquityDec30Raw@7`](../data/raw/export/revisions.jsonl#L7421); r7421; `c0fba5004b1b3f0c843da56bd7728cd6cd936df8c6fa43b81c2376a585b62d97`; 3066 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-20T05:38:49Z; reqlog/u=1/revision.pref_ts |
| 2026-06-20T05:38:49Z | [`save:dse~OAIEquityDec30Raw@8`](../data/raw/export/events.jsonl#L13048); save; e13048 | [`dse~OAIEquityDec30Raw@8`](../data/raw/export/revisions.jsonl#L7422); r7422; `6274169e1250ca23d2117b2fd9ccb083242013f7533e51b58c668e21ce31e672`; 3407 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-20T05:57:33Z; reqlog/u=1/revision.pref_ts |
| 2026-06-20T05:57:33Z | [`save:dse~OAIEquityDec30Raw@9`](../data/raw/export/events.jsonl#L13059); save; e13059 | [`dse~OAIEquityDec30Raw@9`](../data/raw/export/revisions.jsonl#L7423); r7423; `43c2bdae769b3477103e1a0497adaf579729e44ff612de114ac5c6d1142396b3`; 3870 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-20T05:59:01Z; reqlog/u=1/revision.pref_ts |
| 2026-06-20T05:59:00Z | [`save:dse~OAIEquityDec30Raw@10`](../data/raw/export/events.jsonl#L13061); save; e13061 | [`dse~OAIEquityDec30Raw@10`](../data/raw/export/revisions.jsonl#L7424); r7424; `667c9a6d8c64b024f860f54c23aa2024cf4933eb22759991bc15cd67ad658b25`; 4150 bytes (ascii) | request_time=t; success_time=2026-06-20T05:59:01Z; write_date=t; archived_at=2026-06-20T06:07:32Z; reqlog/u=1/revision.pref_ts |
| 2026-06-20T06:07:31Z | [`save:dse~OAIEquityDec30Raw@11`](../data/raw/export/events.jsonl#L13068); save; e13068 | [`dse~OAIEquityDec30Raw@11`](../data/raw/export/revisions.jsonl#L7425); r7425; `1adf93fa3284ede5c8694ab109ea00b6e52ab537398c42e5be0ba4ce2d086ab8`; 5541 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-20T06:09:52Z; reqlog/u=1/revision.pref_ts |
| 2026-06-20T06:09:52Z | [`save:dse~OAIEquityDec30Raw@12`](../data/raw/export/events.jsonl#L13072); save; e13072 | [`dse~OAIEquityDec30Raw@12`](../data/raw/export/revisions.jsonl#L7426); r7426; `0ca2a46f1eaa4b1e75c415c421177f3f56ea6615f644ad1d1dac5d046b1d7d40`; 5870 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-20T06:11:01Z; reqlog/u=1/revision.pref_ts |
| 2026-06-20T06:11:01Z | [`save:dse~OAIEquityDec30Raw@13`](../data/raw/export/events.jsonl#L13073); save; e13073 | [`dse~OAIEquityDec30Raw@13`](../data/raw/export/revisions.jsonl#L7427); r7427; `8c56554515cc5162dc818ff1c352a033a3b273f7dcff5af5542ef44e5f78322e`; 6348 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-20T06:15:24Z; reqlog/u=1/revision.pref_ts |
| 2026-06-20T06:15:24Z | [`save:dse~OAIEquityDec30Raw@14`](../data/raw/export/events.jsonl#L13077); save; e13077 | [`dse~OAIEquityDec30Raw@14`](../data/raw/export/revisions.jsonl#L7428); r7428; `7c2cb593d791085695474bdda94e05e04b968cc28027eef0e20805d3b2628c00`; 6686 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-20T06:26:58Z; reqlog/u=1/revision.pref_ts |
| 2026-06-20T06:26:58Z | [`save:dse~OAIEquityDec30Raw@15`](../data/raw/export/events.jsonl#L13086); save; e13086 | [`dse~OAIEquityDec30Raw@15`](../data/raw/export/revisions.jsonl#L7429); r7429; `ef06d26bb8818ef38b029c3da2576ffda1ed857a3bd7695bc76b164589b7d192`; 7122 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-29T19:14:40Z; reqlog/u=1/revision.pref_ts |
| 2026-06-29T19:14:41Z | [`delete:dse:rclog:152519`](../data/raw/export/events.jsonl#L16704); delete; e16704 | revision_ref=null; no supported body hash | request_time=t; success_time=t; reqlog/u=1/rclog.unix_ts; success_observed=True; action=delete; `corpus/live/rclog.jsonl:152519`; `corpus/live/reqlog_dse_2606.jsonl:1973506` |

### Raw ledger: OECDJun26PrecisionScout

All timestamps UTC. Each `save` is one mutation with two linked source records, not two mutations. `t` in a clock cell means the selected timestamp in that row. Grade/u/winner are copied, not inferred.

| Selected timestamp | Exact event ID / type / source | Body reference and SHA-256 | Clocks and native evidence |
|---|---|---|---|
| 2026-06-20T04:34:31Z | [`save:dse~OECDJun26PrecisionScout@1`](../data/raw/export/events.jsonl#L12986); save; e12986 | [`dse~OECDJun26PrecisionScout@1`](../data/raw/export/revisions.jsonl#L7940); r7940; `6f71ba9b4c7d1841ff1a33ced1bb0d33f0a36fd91c9ae7031f791d1a79c8c9b6`; 650 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-20T04:39:51Z; reqlog/u=1/revision.pref_ts |
| 2026-06-20T04:39:51Z | [`save:dse~OECDJun26PrecisionScout@2`](../data/raw/export/events.jsonl#L12988); save; e12988 | [`dse~OECDJun26PrecisionScout@2`](../data/raw/export/revisions.jsonl#L7941); r7941; `f31cb53c943776e9d932b28e207dc03813cc2d224404583e2a8ae56ca33eaf4e`; 975 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-20T04:44:39Z; reqlog/u=1/revision.pref_ts |
| 2026-06-20T04:44:39Z | [`save:dse~OECDJun26PrecisionScout@3`](../data/raw/export/events.jsonl#L12990); save; e12990 | [`dse~OECDJun26PrecisionScout@3`](../data/raw/export/revisions.jsonl#L7942); r7942; `5414f4aebd4ac2fb504fe28686e83668293ac719210cac8dae78c0544baece88`; 1543 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-20T04:47:00Z; reqlog/u=1/revision.pref_ts |
| 2026-06-20T04:47:00Z | [`save:dse~OECDJun26PrecisionScout@4`](../data/raw/export/events.jsonl#L12992); save; e12992 | [`dse~OECDJun26PrecisionScout@4`](../data/raw/export/revisions.jsonl#L7943); r7943; `a3b0c13fbbf562fbd17ac40b8ad9c64286e97507240973714b81ec7a9a9e0224`; 1748 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-20T04:57:29Z; reqlog/u=1/revision.pref_ts |
| 2026-06-20T04:57:29Z | [`save:dse~OECDJun26PrecisionScout@5`](../data/raw/export/events.jsonl#L12997); save; e12997 | [`dse~OECDJun26PrecisionScout@5`](../data/raw/export/revisions.jsonl#L7944); r7944; `99363d8cc11c75112d0b34da9990f631ae762cc74b433276a0ec6272460704f6`; 2319 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-20T04:57:31Z; reqlog/u=1/revision.pref_ts |
| 2026-06-20T04:57:31Z | [`save:dse~OECDJun26PrecisionScout@6`](../data/raw/export/events.jsonl#L12998); save; e12998 | [`dse~OECDJun26PrecisionScout@6`](../data/raw/export/revisions.jsonl#L7945); r7945; `ca47245b5ce1d29add9f10da3639dba1d42965f81c7d01391ec1ab56afae2cc3`; 2649 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-20T05:03:28Z; reqlog/u=1/revision.pref_ts |
| 2026-06-20T05:03:28Z | [`save:dse~OECDJun26PrecisionScout@7`](../data/raw/export/events.jsonl#L13003); save; e13003 | [`dse~OECDJun26PrecisionScout@7`](../data/raw/export/revisions.jsonl#L7946); r7946; `382d4e9f5bfe5ab918d695e466cba94aace1a4d569daf4e4374f6ffb86256e1e`; 3052 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-20T05:08:56Z; reqlog/u=1/revision.pref_ts |
| 2026-06-20T05:08:56Z | [`save:dse~OECDJun26PrecisionScout@8`](../data/raw/export/events.jsonl#L13012); save; e13012 | [`dse~OECDJun26PrecisionScout@8`](../data/raw/export/revisions.jsonl#L7947); r7947; `55fd5a4e7d84a7ea71798c7b9fba4b809df4cf7b130e29702780e06bbb1138fa`; 3590 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-20T05:20:27Z; reqlog/u=1/revision.pref_ts |
| 2026-06-20T05:20:27Z | [`save:dse~OECDJun26PrecisionScout@9`](../data/raw/export/events.jsonl#L13026); save; e13026 | [`dse~OECDJun26PrecisionScout@9`](../data/raw/export/revisions.jsonl#L7948); r7948; `8f6468f532d6af70d4cf3fda0b523ca4b2a1d83b72f3766b384bb0907b1f639d`; 4061 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-20T05:22:57Z; reqlog/u=1/revision.pref_ts |
| 2026-06-20T05:22:57Z | [`save:dse~OECDJun26PrecisionScout@10`](../data/raw/export/events.jsonl#L13028); save; e13028 | [`dse~OECDJun26PrecisionScout@10`](../data/raw/export/revisions.jsonl#L7949); r7949; `cef1eed0ae59c2a0d5dfccd0c84b5c4a2fc41b577ad57012774e13707248fc49`; 4533 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-20T05:24:49Z; reqlog/u=1/revision.pref_ts |
| 2026-06-20T05:24:49Z | [`save:dse~OECDJun26PrecisionScout@11`](../data/raw/export/events.jsonl#L13030); save; e13030 | [`dse~OECDJun26PrecisionScout@11`](../data/raw/export/revisions.jsonl#L7950); r7950; `5a95be5ff417c35f876341572639c1e8f20b999b8d3a9f4d9162a43c6da6da87`; 4995 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-20T05:27:48Z; reqlog/u=1/revision.pref_ts |
| 2026-06-20T05:27:48Z | [`save:dse~OECDJun26PrecisionScout@12`](../data/raw/export/events.jsonl#L13033); save; e13033 | [`dse~OECDJun26PrecisionScout@12`](../data/raw/export/revisions.jsonl#L7951); r7951; `7d89ea434379e1500e4c7ede97fa327a45b78ea9b5875221f9b6dc4dcfe59c51`; 5607 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-20T05:35:40Z; reqlog/u=1/revision.pref_ts |
| 2026-06-20T05:35:40Z | [`save:dse~OECDJun26PrecisionScout@13`](../data/raw/export/events.jsonl#L13040); save; e13040 | [`dse~OECDJun26PrecisionScout@13`](../data/raw/export/revisions.jsonl#L7952); r7952; `fc233333f483983f64849d8675b7ea64bce9101c12df31a233733dd64306bf88`; 5947 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-20T05:37:38Z; reqlog/u=1/revision.pref_ts |
| 2026-06-20T05:37:37Z | [`save:dse~OECDJun26PrecisionScout@14`](../data/raw/export/events.jsonl#L13043); save; e13043 | [`dse~OECDJun26PrecisionScout@14`](../data/raw/export/revisions.jsonl#L7953); r7953; `4c8240e8b0ed9344e4a876861db21372d9ad835dc4bbb2d1e93787b39f9781de`; 6314 bytes (ascii) | request_time=t; success_time=2026-06-20T05:37:38Z; write_date=t; archived_at=2026-06-20T05:53:34Z; reqlog/u=1/revision.pref_ts |
| 2026-06-20T05:53:34Z | [`save:dse~OECDJun26PrecisionScout@15`](../data/raw/export/events.jsonl#L13057); save; e13057 | [`dse~OECDJun26PrecisionScout@15`](../data/raw/export/revisions.jsonl#L7954); r7954; `bd0bf1d4b3e1c1f7298534c2f5093b1445bae011ab3152f7dec2eecf47df6133`; 6750 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-20T05:57:25Z; reqlog/u=1/revision.pref_ts |
| 2026-06-20T05:57:25Z | [`save:dse~OECDJun26PrecisionScout@16`](../data/raw/export/events.jsonl#L13058); save; e13058 | [`dse~OECDJun26PrecisionScout@16`](../data/raw/export/revisions.jsonl#L7955); r7955; `77f710eeeefed05229bb5bc576723f4d27d00de0ba0f338b01d8295d683b51f4`; 7164 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-29T19:07:12Z; reqlog/u=1/revision.pref_ts |
| 2026-06-29T19:07:13Z | [`delete:dse:rclog:152512`](../data/raw/export/events.jsonl#L16700); delete; e16700 | revision_ref=null; no supported body hash | request_time=t; success_time=t; reqlog/u=1/rclog.unix_ts; success_observed=True; action=delete; `corpus/live/rclog.jsonl:152512`; `corpus/live/reqlog_dse_2606.jsonl:1973438` |

### Raw ledger: AI

All timestamps UTC. Each `save` is one mutation with two linked source records, not two mutations. `t` in a clock cell means the selected timestamp in that row. Grade/u/winner are copied, not inferred.

| Selected timestamp | Exact event ID / type / source | Body reference and SHA-256 | Clocks and native evidence |
|---|---|---|---|
| 2026-06-18T21:02:27Z | [`save:dse~AI@2`](../data/raw/export/events.jsonl#L10753); save; e10753 | [`dse~AI@2`](../data/raw/export/revisions.jsonl#L42); r42; `2b6a755d8f1e582b6a7036666f688224fc3c43b2853854b549c6dc47d6d8e560`; 1224 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-19T15:53:29Z; reqlog/u=1/revision.pref_ts |

### Raw ledger: AgentNacoPovertyTexas2015XQ

All timestamps UTC. Each `save` is one mutation with two linked source records, not two mutations. `t` in a clock cell means the selected timestamp in that row. Grade/u/winner are copied, not inferred.

| Selected timestamp | Exact event ID / type / source | Body reference and SHA-256 | Clocks and native evidence |
|---|---|---|---|
| 2026-06-22T07:04:19Z | [`save:dse~AgentNacoPovertyTexas2015XQ@1`](../data/raw/export/events.jsonl#L14613); save; e14613 | [`dse~AgentNacoPovertyTexas2015XQ@1`](../data/raw/export/revisions.jsonl#L2189); r2189; `2c4a52857ddf31998b19274ebdd1d319c019d260923122b63570bcd24ab2834f`; 1052 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-22T08:09:19Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:09:19Z | [`save:dse~AgentNacoPovertyTexas2015XQ@2`](../data/raw/export/events.jsonl#L14620); save; e14620 | [`dse~AgentNacoPovertyTexas2015XQ@2`](../data/raw/export/revisions.jsonl#L2190); r2190; `0dbb9e1272c09080481d54fd1b5ea044022c45d64ae35d7aaeee1264f4baa38c`; 1569 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-22T08:13:46Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:13:46Z | [`save:dse~AgentNacoPovertyTexas2015XQ@3`](../data/raw/export/events.jsonl#L14632); save; e14632 | [`dse~AgentNacoPovertyTexas2015XQ@3`](../data/raw/export/revisions.jsonl#L2191); r2191; `d1bee7dbb3be7f75493afed83b4fa322843963b833fbe4ef2d95729045f42517`; 1846 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-22T08:14:23Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:14:53Z | [`save:dse~AgentNacoPovertyTexas2015XQ@4`](../data/raw/export/events.jsonl#L14638); save; e14638 | [`dse~AgentNacoPovertyTexas2015XQ@4`](../data/raw/export/revisions.jsonl#L2192); r2192; `0acac159197c819ba7cebb8d2f724b25977c6ea802d5a63c5118aa94673a1e7f`; 1061 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-22T08:16:48Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:16:48Z | [`save:dse~AgentNacoPovertyTexas2015XQ@5`](../data/raw/export/events.jsonl#L14655); save; e14655 | [`dse~AgentNacoPovertyTexas2015XQ@5`](../data/raw/export/revisions.jsonl#L2193); r2193; `ed3e9b0e5126751cb5c4f84fc698cfb09306a5fce67b03a45538f216f6a9cae1`; 1836 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-22T08:16:58Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:16:58Z | [`save:dse~AgentNacoPovertyTexas2015XQ@6`](../data/raw/export/events.jsonl#L14662); save; e14662 | [`dse~AgentNacoPovertyTexas2015XQ@6`](../data/raw/export/revisions.jsonl#L2194); r2194; `7076f8f7d8a4cbb7a072bdd1d1d740340eb722099e5dd446121a2c609234cb01`; 1240 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-22T08:17:12Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:17:12Z | [`save:dse~AgentNacoPovertyTexas2015XQ@7`](../data/raw/export/events.jsonl#L14663); save; e14663 | [`dse~AgentNacoPovertyTexas2015XQ@7`](../data/raw/export/revisions.jsonl#L2195); r2195; `17217c6a21db6cc9eb8e8d9b62513d7f5c86b8ce5cc228cec8bbb2de13deb605`; 1583 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-22T08:17:17Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:17:17Z | [`save:dse~AgentNacoPovertyTexas2015XQ@8`](../data/raw/export/events.jsonl#L14665); save; e14665 | [`dse~AgentNacoPovertyTexas2015XQ@8`](../data/raw/export/revisions.jsonl#L2196); r2196; `13d4d7cb182a0de196f727a62e4a8108079aedde4f27016f8b5f88320b7f7ee1`; 2613 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-22T08:17:30Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:17:30Z | [`save:dse~AgentNacoPovertyTexas2015XQ@9`](../data/raw/export/events.jsonl#L14666); save; e14666 | [`dse~AgentNacoPovertyTexas2015XQ@9`](../data/raw/export/revisions.jsonl#L2197); r2197; `ed3e9b0e5126751cb5c4f84fc698cfb09306a5fce67b03a45538f216f6a9cae1`; 1836 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-22T08:18:11Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:18:11Z | [`save:dse~AgentNacoPovertyTexas2015XQ@10`](../data/raw/export/events.jsonl#L14672); save; e14672 | [`dse~AgentNacoPovertyTexas2015XQ@10`](../data/raw/export/revisions.jsonl#L2198); r2198; `bc4218fd2ab6643a733dce138eda8b55155de11f7311a673cd4df97ee138f74d`; 2309 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-22T08:20:36Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:20:36Z | [`save:dse~AgentNacoPovertyTexas2015XQ@11`](../data/raw/export/events.jsonl#L14696); save; e14696 | [`dse~AgentNacoPovertyTexas2015XQ@11`](../data/raw/export/revisions.jsonl#L2199); r2199; `b4daeb748a20bf7d1bf30a602f0d1f825b5a6d5b88df6c2e3a8aa7b8c6737014`; 2984 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-22T08:27:06Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:27:05Z | [`save:dse~AgentNacoPovertyTexas2015XQ@12`](../data/raw/export/events.jsonl#L14738); save; e14738 | [`dse~AgentNacoPovertyTexas2015XQ@12`](../data/raw/export/revisions.jsonl#L2200); r2200; `c0104af3a963a77d9a9241228a6cbd1a8b768f8c42e2c5f351b1ecd3152d2331`; 3659 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-22T08:27:59Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:27:59Z | [`save:dse~AgentNacoPovertyTexas2015XQ@13`](../data/raw/export/events.jsonl#L14742); save; e14742 | [`dse~AgentNacoPovertyTexas2015XQ@13`](../data/raw/export/revisions.jsonl#L2201); r2201; `7737374fb73421dc33bf7af2e1b710a44f328107de4e6b093413dd06d9b9deae`; 4188 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-22T08:29:41Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:29:41Z | [`save:dse~AgentNacoPovertyTexas2015XQ@14`](../data/raw/export/events.jsonl#L14751); save; e14751 | [`dse~AgentNacoPovertyTexas2015XQ@14`](../data/raw/export/revisions.jsonl#L2202); r2202; `b0d1f082808f796a9eecbf565cc28f702362f4eb80382531edd90ba68cd96b7f`; 4805 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-22T08:30:06Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:30:05Z | [`save:dse~AgentNacoPovertyTexas2015XQ@15`](../data/raw/export/events.jsonl#L14757); save; e14757 | [`dse~AgentNacoPovertyTexas2015XQ@15`](../data/raw/export/revisions.jsonl#L2203); r2203; `b49e427556129804f0167bf1bdc8b8c89e5a01df8488eadc32032dff702c59f6`; 5793 bytes (ascii) | request_time=t; success_time=2026-06-22T08:30:06Z; write_date=t; archived_at=2026-06-22T08:31:28Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:31:28Z | [`save:dse~AgentNacoPovertyTexas2015XQ@16`](../data/raw/export/events.jsonl#L14766); save; e14766 | [`dse~AgentNacoPovertyTexas2015XQ@16`](../data/raw/export/revisions.jsonl#L2204); r2204; `d4ddc1169f19124fd7f926fd305d3312d2285514cb47cd3e9864d4c20c2366ea`; 1145 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-22T08:34:38Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:34:38Z | [`save:dse~AgentNacoPovertyTexas2015XQ@17`](../data/raw/export/events.jsonl#L14790); save; e14790 | [`dse~AgentNacoPovertyTexas2015XQ@17`](../data/raw/export/revisions.jsonl#L2205); r2205; `5c4ca2859434ac2b82346f8ba078e5fbec514278d6f96f4871bcd935b15b2c30`; 2108 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-22T08:37:04Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:37:04Z | [`save:dse~AgentNacoPovertyTexas2015XQ@18`](../data/raw/export/events.jsonl#L14814); save; e14814 | [`dse~AgentNacoPovertyTexas2015XQ@18`](../data/raw/export/revisions.jsonl#L2206); r2206; `5291ba4fd63ba67d1e45f03bc597cd7519a7c342f0b044ec21e1d37afe05d6ad`; 1084 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-22T08:37:10Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:37:09Z | [`save:dse~AgentNacoPovertyTexas2015XQ@19`](../data/raw/export/events.jsonl#L14816); save; e14816 | [`dse~AgentNacoPovertyTexas2015XQ@19`](../data/raw/export/revisions.jsonl#L2207); r2207; `6c671eb04a8581dc5752d8a59f45f5be3f06d0045b9732603bee7205d99d4fce`; 1668 bytes (ascii) | request_time=t; success_time=2026-06-22T08:37:10Z; write_date=t; archived_at=2026-06-22T08:37:23Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:37:23Z | [`save:dse~AgentNacoPovertyTexas2015XQ@20`](../data/raw/export/events.jsonl#L14819); save; e14819 | [`dse~AgentNacoPovertyTexas2015XQ@20`](../data/raw/export/revisions.jsonl#L2208); r2208; `99b455808f9dcf50e869e48864ca23d18aa6fff3c7d4bab6f76015f44f082a37`; 2724 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-22T08:38:23Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:38:23Z | [`save:dse~AgentNacoPovertyTexas2015XQ@21`](../data/raw/export/events.jsonl#L14839); save; e14839 | [`dse~AgentNacoPovertyTexas2015XQ@21`](../data/raw/export/revisions.jsonl#L2209); r2209; `58379fa73cc5502899e2822c1553a05447eac567ae470ae773ba3d66fa4fb589`; 2833 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-22T08:39:06Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:39:06Z | [`save:dse~AgentNacoPovertyTexas2015XQ@22`](../data/raw/export/events.jsonl#L14860); save; e14860 | [`dse~AgentNacoPovertyTexas2015XQ@22`](../data/raw/export/revisions.jsonl#L2210); r2210; `1a797d322bb817171e18cb2c986046a5dd03658d9fc117784778efcf53e87be9`; 1126 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=t; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:39:06Z | [`save:dse~AgentNacoPovertyTexas2015XQ@23`](../data/raw/export/events.jsonl#L14861); save; e14861 | [`dse~AgentNacoPovertyTexas2015XQ@23`](../data/raw/export/revisions.jsonl#L2211); r2211; `398ae63a9556d0e492e03fadb9421fe1f5633ff236325af3c48e15b986e3c08d`; 2054 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-22T08:39:31Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:39:31Z | [`save:dse~AgentNacoPovertyTexas2015XQ@24`](../data/raw/export/events.jsonl#L14871); save; e14871 | [`dse~AgentNacoPovertyTexas2015XQ@24`](../data/raw/export/revisions.jsonl#L2212); r2212; `6aaea3e873ca3bd42f217dfc37b48fe9c1842405fb0e824e18b5eca43db45c65`; 1868 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-22T08:40:49Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:40:49Z | [`save:dse~AgentNacoPovertyTexas2015XQ@25`](../data/raw/export/events.jsonl#L14890); save; e14890 | [`dse~AgentNacoPovertyTexas2015XQ@25`](../data/raw/export/revisions.jsonl#L2213); r2213; `ce2412382a376764b9f1fea39aa44a1a3dd2d2030a6612b2617cb1c6106a8d5a`; 1247 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-22T08:41:13Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:41:13Z | [`save:dse~AgentNacoPovertyTexas2015XQ@26`](../data/raw/export/events.jsonl#L14900); save; e14900 | [`dse~AgentNacoPovertyTexas2015XQ@26`](../data/raw/export/revisions.jsonl#L2214); r2214; `ecf32fdc64c5034bb8bb3634c6edf088594082396287f66b737f4dee8b3aad16`; 1126 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-22T08:42:24Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:42:24Z | [`save:dse~AgentNacoPovertyTexas2015XQ@27`](../data/raw/export/events.jsonl#L14926); save; e14926 | [`dse~AgentNacoPovertyTexas2015XQ@27`](../data/raw/export/revisions.jsonl#L2215); r2215; `d6a35e5594b70de44c29385200e80eb85a7071e0aeac3d78be9283f8d8221533`; 2145 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-22T08:43:15Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:43:15Z | [`save:dse~AgentNacoPovertyTexas2015XQ@28`](../data/raw/export/events.jsonl#L14947); save; e14947 | [`dse~AgentNacoPovertyTexas2015XQ@28`](../data/raw/export/revisions.jsonl#L2216); r2216; `5ba0e8dddbc2c7131dda708ef0528e1102fbe72e63a89cda93965a67f60c247d`; 2934 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-22T08:43:33Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:43:33Z | [`save:dse~AgentNacoPovertyTexas2015XQ@29`](../data/raw/export/events.jsonl#L14958); save; e14958 | [`dse~AgentNacoPovertyTexas2015XQ@29`](../data/raw/export/revisions.jsonl#L2217); r2217; `6c85001086e4291763f2baf70550025b62480c57acfd4a9327847e248cbe0208`; 1466 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-22T08:44:20Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:44:20Z | [`save:dse~AgentNacoPovertyTexas2015XQ@30`](../data/raw/export/events.jsonl#L14977); save; e14977 | [`dse~AgentNacoPovertyTexas2015XQ@30`](../data/raw/export/revisions.jsonl#L2218); r2218; `5bb1981b3ebd5ad0b2925dfeaa2a8874ac63a927f9210b1d33414fff61569ba2`; 2068 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-22T08:44:59Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:44:59Z | [`save:dse~AgentNacoPovertyTexas2015XQ@31`](../data/raw/export/events.jsonl#L14989); save; e14989 | [`dse~AgentNacoPovertyTexas2015XQ@31`](../data/raw/export/revisions.jsonl#L2219); r2219; `b00d70e5e5dbdf0ecd9a13dd98335cb8aa23a6fd3a56b6240d23c2aec9b4eda2`; 3213 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-22T08:46:32Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:46:32Z | [`save:dse~AgentNacoPovertyTexas2015XQ@32`](../data/raw/export/events.jsonl#L15017); save; e15017 | [`dse~AgentNacoPovertyTexas2015XQ@32`](../data/raw/export/revisions.jsonl#L2220); r2220; `133c7a724a119d728b1201cfe61d851b39144b9a0874785c8ca7cc2022731770`; 3626 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-22T08:47:02Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:47:02Z | [`save:dse~AgentNacoPovertyTexas2015XQ@33`](../data/raw/export/events.jsonl#L15021); save; e15021 | [`dse~AgentNacoPovertyTexas2015XQ@33`](../data/raw/export/revisions.jsonl#L2221); r2221; `fddc8821849b29b9e2a6c65d09fff271cb8290805ed111dbe43c849d1382640f`; 938 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-22T08:48:10Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:48:09Z | [`save:dse~AgentNacoPovertyTexas2015XQ@34`](../data/raw/export/events.jsonl#L15031); save; e15031 | [`dse~AgentNacoPovertyTexas2015XQ@34`](../data/raw/export/revisions.jsonl#L2222); r2222; `79af46413d71d67d4f732f43fe83b00d469f2a06a807dfddc1cbd95b8519dfc4`; 1183 bytes (ascii) | request_time=t; success_time=2026-06-22T08:48:10Z; write_date=t; archived_at=2026-06-22T08:50:48Z; reqlog/u=1/revision.pref_ts |
| 2026-06-22T08:50:48Z | [`save:dse~AgentNacoPovertyTexas2015XQ@35`](../data/raw/export/events.jsonl#L15051); save; e15051 | [`dse~AgentNacoPovertyTexas2015XQ@35`](../data/raw/export/revisions.jsonl#L2223); r2223; `73869e64abab7da48eb2f2b40fbb5a3faba3196ab9944e021089ed7870b6042a`; 1431 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-26T16:45:22Z; reqlog/u=1/revision.pref_ts |
| 2026-06-26T16:45:23Z | [`delete:dse:rclog:151929`](../data/raw/export/events.jsonl#L16354); delete; e16354 | revision_ref=null; no supported body hash | request_time=t; success_time=t; reqlog/u=1/rclog.unix_ts; success_observed=True; action=delete; `corpus/live/rclog.jsonl:151929`; `corpus/live/reqlog_dse_2606.jsonl:1912055` |

### Raw ledger: AgentBridgeOct2142X

All timestamps UTC. Each `save` is one mutation with two linked source records, not two mutations. `t` in a clock cell means the selected timestamp in that row. Grade/u/winner are copied, not inferred.

| Selected timestamp | Exact event ID / type / source | Body reference and SHA-256 | Clocks and native evidence |
|---|---|---|---|
| 2026-06-16T18:40:04Z | [`save:dse~AgentBridgeOct2142X@1`](../data/raw/export/events.jsonl#L1807); save; e1807 | [`dse~AgentBridgeOct2142X@1`](../data/raw/export/revisions.jsonl#L301); r301; `4b68202068fb5f4d4fe05802b76f19890c2f1edd9b665ac419b45ea3f9a8c689`; 205 bytes (ascii) | request_time=t; success_time=t; write_date=t; archived_at=2026-06-16T18:43:13Z; reqlog/u=1/revision.pref_ts |
