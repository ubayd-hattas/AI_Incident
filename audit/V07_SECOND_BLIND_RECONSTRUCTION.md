# Fresh blind reconstruction — packets 04 and 08

**Provenance:** produced by a separate, freshly-spawned agent instance with no memory of this
project's conversation history and no access to any of its planning, adjudication, or
validation documents. It was given only a copy of the five raw pinned export files and
`docs/E06_IMPLEMENTATION_CONTRACT.md`, in an isolated scratch directory containing nothing
else, with explicit instructions not to search the web or look for any other file related to
this project. This is the second, genuinely independent blind reconstruction of packets 04/08
that `audit/V07_BLIND_VALIDATION.md` identified as still missing — see that file's certification
section for the comparison against the first reconstruction and against E06's own output.


Independently reconstructed from `raw_export/{pages,events,revisions}.jsonl` filtered to
`page_key` exact match and `wiki="dse"`, applying only the rules in
`E06_IMPLEMENTATION_CONTRACT.md` §1–§3. No other file, prior packet, or external source was
consulted. All times are UTC as carried in the raw records (`time` field of `events.jsonl`,
which equals the linked revision's `time`/`write_date` for saves). All observed
`uncertainty_seconds` = 1 for every event on all three pages (saves: from the linked
revision; deletes: native event field) — no null/unsupported uncertainty encountered.
Horizon: t0=2026-05-24T00:00:00Z, T=2026-07-15T00:00:00Z (all mutations below fall inside it).

Per-page `pages.jsonl` descriptor fields (`deleted_live`, `head_differs_from_live`,
`n_deletions`, `n_recreations`, `first_write`/`last_write`) were read only as a post-hoc
cross-check of row counts, never as a source for any state or transition claim below.

---

## 1. `dse~AgentProxyCountyNext987111`

10 mutating events found (7 `save`, 3 `delete`), seq 1–7 fully contiguous, no bodyless
(`revision_ref=null`) events, no `revert` events. Two `relation_type=first_recreation_of`
edges exist (rev@4 → `delete:dse:rclog:138565`; rev@5 → `delete:dse:rclog:138624`); both point
to deletions of this same page_key's own prior life, not to some other title — recorded as
provenance only, not used to move or backdate any transition.

| # | Event ID | Time (UTC) | u (s) | Before | Mutation | After | Episode | Ordering | Archival note (non-mutating) | Confidence |
|---|---|---|---|---|---|---|---|---|---|---|
| — | (horizon) | t0=2026-05-24T00:00:00Z | — | — | — | `unknown` | (pre-episode) | — | — | SAFE |
| 1 | `save:dse~AgentProxyCountyNext987111@1` | 2026-06-18T18:15:55Z | 1 | `unknown` | save rev@1 | `live(body_ref=1)` | **starts** Ep.1 | exact (no co-timed event on this page) | rev@1 `archived_at`=18:18:24Z, exactly = save@2's time; not used as a transition | SAFE_ONLY_UNDER_RELEASED_TRACE_MODEL |
| 2 | `save:dse~AgentProxyCountyNext987111@2` | 2026-06-18T18:18:24Z | 1 | `live(1)` | save rev@2 | `live(body_ref=2)` | continues Ep.1 | exact | rev@2 `archived_at`=18:20:27Z, exactly = save@3's time | SAFE_ONLY_UNDER_RELEASED_TRACE_MODEL |
| 3 | `save:dse~AgentProxyCountyNext987111@3` | 2026-06-18T18:20:27Z | 1 | `live(2)` | save rev@3 | `live(body_ref=3)` | continues Ep.1 | exact | rev@3 `archived_at`=18:23:11Z, 2s before the next delete (18:23:13) | SAFE_ONLY_UNDER_RELEASED_TRACE_MODEL |
| 4 | `delete:dse:rclog:138565` | 2026-06-18T18:23:13Z | 1 | `live(3)` | delete | `deleted` | **ends** Ep.1 | exact | — (deletes carry no `archived_at`) | SAFE_ONLY_UNDER_RELEASED_TRACE_MODEL |
| 5 | `save:dse~AgentProxyCountyNext987111@4` | 2026-06-18T18:25:03Z | 1 | `deleted` | save rev@4 | `live(body_ref=4)` | **starts** Ep.2 (post-deletion save) | exact | rev@4 `archived_at`=18:25:19Z, 3s before the next delete (18:25:22); rev@4 also carries `relation_type=first_recreation_of → delete:dse:rclog:138565` (provenance only, not used to move this boundary) | SAFE_ONLY_UNDER_RELEASED_TRACE_MODEL |
| 6 | `delete:dse:rclog:138624` | 2026-06-18T18:25:22Z | 1 | `live(4)` | delete | `deleted` | **ends** Ep.2 | exact | — | SAFE_ONLY_UNDER_RELEASED_TRACE_MODEL |
| 7 | `save:dse~AgentProxyCountyNext987111@5` | 2026-06-18T18:31:10Z | 1 | `deleted` | save rev@5 | `live(body_ref=5)` | **starts** Ep.3 | exact | rev@5 `archived_at`=18:32:04Z, exactly = save@6's time; `relation_type=first_recreation_of → delete:dse:rclog:138624` (provenance only) | SAFE_ONLY_UNDER_RELEASED_TRACE_MODEL |
| 8 | `save:dse~AgentProxyCountyNext987111@6` | 2026-06-18T18:32:04Z | 1 | `live(5)` | save rev@6 | `live(body_ref=6)` | continues Ep.3 | exact | rev@6 `archived_at`=18:40:40Z, exactly = save@7's time | SAFE_ONLY_UNDER_RELEASED_TRACE_MODEL |
| 9 | `save:dse~AgentProxyCountyNext987111@7` | 2026-06-18T18:40:40Z | 1 | `live(6)` | save rev@7 | `live(body_ref=7)` | continues Ep.3 | exact | rev@7 `archived_at`=2026-06-24T12:59:58Z, 2s before the final delete, six days later | SAFE_ONLY_UNDER_RELEASED_TRACE_MODEL |
| 10 | `delete:dse:rclog:151035` | 2026-06-24T13:00:00Z | 1 | `live(7)` | delete | `deleted` | **ends** Ep.3 | exact | — | SAFE_ONLY_UNDER_RELEASED_TRACE_MODEL |
| — | (horizon) | T=2026-07-15T00:00:00Z | — | `deleted` (carried, right-censored) | — | `deleted` | Ep.3 remains ended; no Ep.4 observed | — | no mutation observed after 2026-06-24T13:00:00Z through T | SAFE_ONLY_UNDER_RELEASED_TRACE_MODEL (carry rule) |

**Ambiguity/uncertainty:** none of this page's 10 events share an exact timestamp with another
event on this same page, so nominal ordering is exact throughout and there is no genuine tie to
preserve as a wrapper/alternatives set. The minimum gap between consecutive events is 19s
(delete@18:25:03→18:25:22 pair), well outside the ±1s uncertainty windows, so no boundary
touches or overlaps even in `mode="uncertainty"`. The only assumption made anywhere is the
released-trace-model assumption required by the contract itself for every save/delete
transition (held text/save ≠ proven public availability). Three episodes were found
(matching this page's own `n_deletions=3`/`n_recreations=2`, used here only as a passive
consistency check, not as a source of the boundaries).

---

## 2. `dse~OAIEquityDec30Raw`

16 mutating events found (15 `save`, 1 `delete`), seq 1–15 fully contiguous, no bodyless
events, no `revert` events, no `relation_type`/`related_event_id` set on any revision or event
(single unbroken episode, no recreation).

| # | Event ID | Time (UTC) | u (s) | Before | Mutation | After | Episode | Ordering | Archival note (non-mutating) |
|---|---|---|---|---|---|---|---|---|---|
| — | (horizon) | t0 | — | — | — | `unknown` | pre-episode | — | — |
| 1 | `save:dse~OAIEquityDec30Raw@1` | 2026-06-20T05:03:37Z | 1 | `unknown` | save rev@1 | `live(1)` | **starts** Ep.1 | exact | rev@1 archived 05:09:10Z (=save@2 time) |
| 2 | `…@2` | 05:09:10Z | 1 | `live(1)` | save rev@2 | `live(2)` | continues | exact | rev@2 archived 05:10:47Z (=save@3 time) |
| 3 | `…@3` | 05:10:47Z | 1 | `live(2)` | save rev@3 | `live(3)` | continues | exact | rev@3 archived 05:17:46Z (=save@4 time) |
| 4 | `…@4` | 05:17:46Z | 1 | `live(3)` | save rev@4 | `live(4)` | continues | exact | rev@4 archived 05:23:15Z (=save@5 time) |
| 5 | `…@5` | 05:23:15Z | 1 | `live(4)` | save rev@5 | `live(5)` | continues | exact | rev@5 archived 05:28:29Z (=save@6 time) |
| 6 | `…@6` | 05:28:29Z | 1 | `live(5)` | save rev@6 | `live(6)` | continues | exact | rev@6 archived 05:37:25Z (=save@7 time) |
| 7 | `…@7` | 05:37:25Z | 1 | `live(6)` | save rev@7 | `live(7)` | continues | exact | rev@7 archived 05:38:49Z (=save@8 time) |
| 8 | `…@8` | 05:38:49Z | 1 | `live(7)` | save rev@8 | `live(8)` | continues | exact | rev@8 archived 05:57:33Z (=save@9 time) |
| 9 | `…@9` | 05:57:33Z | 1 | `live(8)` | save rev@9 | `live(9)` | continues | exact | rev@9 archived 05:59:01Z (1s after save@10's time 05:59:00) |
| 10 | `…@10` | 05:59:00Z | 1 | `live(9)` | save rev@10 | `live(10)` | continues | exact | rev@10 archived 06:07:32Z (1s after save@11's time 06:07:31) |
| 11 | `…@11` | 06:07:31Z | 1 | `live(10)` | save rev@11 | `live(11)` | continues | exact | rev@11 archived 06:09:52Z (=save@12 time) |
| 12 | `…@12` | 06:09:52Z | 1 | `live(11)` | save rev@12 | `live(12)` | continues | exact | rev@12 archived 06:11:01Z (=save@13 time) |
| 13 | `…@13` | 06:11:01Z | 1 | `live(12)` | save rev@13 | `live(13)` | continues | exact | rev@13 archived 06:15:24Z (=save@14 time) |
| 14 | `…@14` | 06:15:24Z | 1 | `live(13)` | save rev@14 | `live(14)` | continues | exact | rev@14 archived 06:26:58Z (=save@15 time) |
| 15 | `…@15` | 06:26:58Z | 1 | `live(14)` | save rev@15 | `live(15)` | continues | exact | rev@15 archived 2026-06-29T19:14:40Z, 1s before the delete, nine days later |
| 16 | `delete:dse:rclog:152519` | 2026-06-29T19:14:41Z | 1 | `live(15)` | delete | `deleted` | **ends** Ep.1 | exact | — |
| — | (horizon) | T | — | `deleted` (carried, right-censored) | — | `deleted` | no further episode | — | no mutation observed after 2026-06-29T19:14:41Z through T |

**Ambiguity/uncertainty:** all 16 timestamps on this page are distinct; the smallest gap
between consecutive events is 69s (rev@11→rev@12), far outside any ±1s uncertainty window, so
there is no tie and no touching-window case even in `mode="uncertainty"`. One episode only.
All transitions are `SAFE_ONLY_UNDER_RELEASED_TRACE_MODEL` (saves/delete) or `SAFE`
(carry-to-horizon, initial unknown prehistory). No bodyless mutation, no relation edge, so no
assumption beyond the released-trace model was required anywhere in this page's history.

---

## 3. `dse~OECDJun26PrecisionScout`

17 mutating events found (16 `save`, 1 `delete`), seq 1–16 fully contiguous, no bodyless
events, no `revert` events, no `relation_type`/`related_event_id` set anywhere (single episode,
no recreation).

| # | Event ID | Time (UTC) | u (s) | Before | Mutation | After | Episode | Ordering | Archival note (non-mutating) |
|---|---|---|---|---|---|---|---|---|---|
| — | (horizon) | t0 | — | — | — | `unknown` | pre-episode | — | — |
| 1 | `save:dse~OECDJun26PrecisionScout@1` | 2026-06-20T04:34:31Z | 1 | `unknown` | save rev@1 | `live(1)` | **starts** Ep.1 | exact | rev@1 archived 04:39:51Z (=save@2 time) |
| 2 | `…@2` | 04:39:51Z | 1 | `live(1)` | save rev@2 | `live(2)` | continues | exact | rev@2 archived 04:44:39Z (=save@3 time) |
| 3 | `…@3` | 04:44:39Z | 1 | `live(2)` | save rev@3 | `live(3)` | continues | exact | rev@3 archived 04:47:00Z (=save@4 time) |
| 4 | `…@4` | 04:47:00Z | 1 | `live(3)` | save rev@4 | `live(4)` | continues | exact | rev@4 archived 04:57:29Z (=save@5 time) |
| 5 | `…@5` | 04:57:29Z | 1 | `live(4)` | save rev@5 | `live(5)` | continues | **nominal: exact** (distinct timestamp); **see note below** | rev@5 archived 04:57:31Z (=save@6 time) |
| 6 | `…@6` | 04:57:31Z | 1 | `live(5)` | save rev@6 | `live(6)` | continues | **nominal: exact**; **see note below** | rev@6 archived 05:03:28Z (=save@7 time) |
| 7 | `…@7` | 05:03:28Z | 1 | `live(6)` | save rev@7 | `live(7)` | continues | exact | rev@7 archived 05:08:56Z (=save@8 time) |
| 8 | `…@8` | 05:08:56Z | 1 | `live(7)` | save rev@8 | `live(8)` | continues | exact | rev@8 archived 05:20:27Z (=save@9 time) |
| 9 | `…@9` | 05:20:27Z | 1 | `live(8)` | save rev@9 | `live(9)` | continues | exact | rev@9 archived 05:22:57Z (=save@10 time) |
| 10 | `…@10` | 05:22:57Z | 1 | `live(9)` | save rev@10 | `live(10)` | continues | exact | rev@10 archived 05:24:49Z (=save@11 time) |
| 11 | `…@11` | 05:24:49Z | 1 | `live(10)` | save rev@11 | `live(11)` | continues | exact | rev@11 archived 05:27:48Z (=save@12 time) |
| 12 | `…@12` | 05:27:48Z | 1 | `live(11)` | save rev@12 | `live(12)` | continues | exact | rev@12 archived 05:35:40Z (=save@13 time) |
| 13 | `…@13` | 05:35:40Z | 1 | `live(12)` | save rev@13 | `live(13)` | continues | exact | rev@13 archived 05:37:38Z (1s after save@14's time 05:37:37) |
| 14 | `…@14` | 05:37:37Z | 1 | `live(13)` | save rev@14 | `live(14)` | continues | exact | rev@14 archived 05:53:34Z (=save@15 time) |
| 15 | `…@15` | 05:53:34Z | 1 | `live(14)` | save rev@15 | `live(15)` | continues | exact | rev@15 archived 05:57:25Z (=save@16 time) |
| 16 | `…@16` | 05:57:25Z | 1 | `live(15)` | save rev@16 | `live(16)` | continues | exact | rev@16 archived 2026-06-29T19:07:12Z, 1s before the delete, nine days later |
| 17 | `delete:dse:rclog:152512` | 2026-06-29T19:07:13Z | 1 | `live(16)` | delete | `deleted` | **ends** Ep.1 | exact | — |
| — | (horizon) | T | — | `deleted` (carried, right-censored) | — | `deleted` | no further episode | — | no mutation observed after 2026-06-29T19:07:13Z through T |

**Ambiguity/uncertainty — the one notable finding on this page:** save@5 (04:57:29Z) and save@6
(04:57:31Z) are only **2 seconds apart**, both carrying the standard u=1s. Their nominal
timestamps are distinct, so in `mode="nominal"` this is a plain, exactly-ordered pair — no real
tie, no alternatives needed (`live(5)` strictly precedes `live(6)`). But this is the only place
across all three pages where the gap is small enough to matter under `mode="uncertainty"`: the
closed windows are [04:57:28, 04:57:30] and [04:57:30, 04:57:32] — they **touch** at exactly
04:57:30Z. Per the contract's uncertainty semantics ("touching endpoints allow co-timing and
either internal order"), a state query at that single instant in uncertainty mode must admit
both `live(5)` and `live(6)` as alternatives rather than picking one; every other boundary on
this page (and on the other two pages) has gaps far larger than 2×u, so no other touching or
overlapping window exists anywhere in the three reconstructions. All transitions are otherwise
`SAFE_ONLY_UNDER_RELEASED_TRACE_MODEL` (saves/delete) or `SAFE` (initial unknown, carry to
horizon); no bodyless mutation and no relation edge appear anywhere in this page's records, so
no assumption beyond the released-trace model was needed.

---

## Cross-page notes

- No event on any of the three pages shares an exact nominal timestamp with another event on
  the *same* page_key — the only near-collision found anywhere is the 2-second save@5/save@6
  gap on `OECDJun26PrecisionScout`, and it only becomes a real ambiguity in uncertainty mode
  (see above), never in nominal mode.
- A very regular pattern recurs on all three pages: each revision's `archived_at` lands at, or
  within a few seconds of, the time of the *next* mutation on that page (occasionally a second
  or two *after* it instead of before). This is exactly the "archival clock ... often
  correlates with next save" situation the contract calls out by name as `UNSAFE to implement`
  and `UNRESOLVED` in historical meaning — it was recorded here only as a non-mutating
  observation for every row where it appears near a boundary, and was never allowed to
  establish, confirm, or move any live/deleted transition.
- `AgentProxyCountyNext987111` is the only one of the three with `relation_type
  =first_recreation_of` edges; both point to deletions of this same page's own prior life. They
  were preserved as provenance annotations only — the episode boundaries they happen to sit next
  to were established purely from the save/delete event timestamps, not from the edges.
- No bodyless (`revision_ref=null`, `action=form_edit`) event and no `revert` event occurs on
  any of the three pages, so no `live(body_unknown)` state and no "carried-body invalidation"
  case arises for these page keys.
- All prehistory before each page's first observed save is `unknown` (left-censored); none of
  the three first revisions carry a `relation_type` back to an earlier deletion, so none of
  them is treated as anything other than "first *supported* appearance," never as proof of
  first-ever creation.
