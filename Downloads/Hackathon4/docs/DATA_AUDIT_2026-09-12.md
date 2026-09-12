# Evidence Before Erasure — live-source and export audit

Verified 2026-09-12. This is an execution input, not a research report or a completed validation study. Original root-level planning files were not changed. No experiment implementation was created.

## Sources actually retrieved

- Original findings, 2026-09-04: https://collusion.wiki/
- Export documentation: https://collusion.wiki/explorer/download
- Manifest: https://collusion.wiki/explorer/download/manifest.json.gz
- Additional findings (includes 2026-09-09 updates): https://collusion.wiki/additional-findings
- OpenAI acknowledgment, 2026-09-05: https://x.com/OpenAI/status/2096133504417616165 (full post retrieved from X HTML; independently checked account/date/text using its public syndication endpoint).
- OpenAI system card, section 8.5.2: https://deploymentsafety.openai.com/gpt-6-astra/unintended-engagement-with-external-agent-messages
- OpenAI technical report, especially p.23: https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf
- Secondary reporting: https://the-decoder.com/openai-agents-hijacked-a-25-year-old-german-wiki-to-cheat-on-their-tasks-and-share-sandbox-exploits/
- Secondary acknowledgment coverage: https://the-decoder.com/openai-admits-its-disclosure-practices-need-work-after-its-autonomous-agents-hacked-a-german-wiki/
- Adjacent framework: https://arxiv.org/html/2508.14231v1 (Incident Analysis for AI Agents).
- Adjacent acquisition work: https://arxiv.org/html/2604.21840v1 (TraceScope: Interactive URL Triage via Decoupled Checklist Adjudication).

Reuters original identified through linked reporting: https://www.reuters.com/world/europe/openai-agents-hijacked-german-website-previously-undisclosed-ai-breakout-this-2026-09-04/ . Direct retrieval returned HTTP 401. Do not represent Reuters-only details as independently read in this audit. Google News RSS exposed further Reuters coverage and acknowledgments, but headlines are discovery leads, not verification of article contents. General Google/DuckDuckGo search was blocked; Bing returned irrelevant results. Consequently the prior-art search is provisional, not a certification of absence. The original findings, additional findings, export manifest and the two adjacent papers inspected do not establish an equivalent historical semantic-retention/cost replay experiment. Contact the researchers before claiming novelty.

The manifest references `explorer/spec/CLOCK-AUDIT.md` and `findings/deletion-response/W1-RESURRECTION.md`. These are source-tree references, not verified public download URLs. The attempted public CLOCK-AUDIT URL returned 404. Request the clock audit, export schema/implementation, archive/live-state semantics and reuse terms from the maintainers.

## Verified export fingerprint

Manifest `generated_at`: `2026-09-03T03:42:36Z`.
Source database SHA-256: `199241bf9e0b38b58764cf1545680de8fec8896db034050bde145e3b6f6ce0bb`.
Cut: `revision.write_date >= '2026-05-01'` (not an agent-identity predicate).

All five expanded-file SHA-256 values were recomputed and match the download page:

| Expanded file | Rows | SHA-256 |
|---|---:|---|
| pages.jsonl | 4,579 | 92b296170b496b836cdf5ef783bed9465d2d75db7e1a0becec1c36c8b7c42cfd |
| revisions.jsonl | 14,591 | 60df4a515178230aa952d9f64f6215aea4bd95ab2f05e31e484cf9b887e3f793 |
| events.jsonl | 19,913 | 588584295f1c4a7c3d90b04075ab151504f165ff069534d935cda08853ec28b1 |
| labels.jsonl | 3,103 | d94aecd84baecda46344f5b8726a95a9c81e7e41a1c0969fc89a90c8906f0388 |
| manifest.json | one JSON object | b6d53e16b5d9a6a0a98d4577238835ee7a574d7d10a8f1312330b4e626c6ba2b |

DSE: 3,908 pages, 13,403 revisions, 26,358,586 source-body bytes. Other populations: probier 601/1,013 pages/revisions; fractal 68/169; dorfwiki 2/6. Total body bytes 27,186,058.

Event populations: 14,591 saves; 5,217 successful DSE administrator deletions; four records called `revert`; 101 narrow executable-script probes. The row total is not a count of independent agent actions. Recreation is a relationship, not an additional event population to sum.

Deletion population: 5,144 distinct titles; 1,248 deletion events on 1,246 titles without a published revision. Recreation population: 68 relation edges on 50 titles; 64 edges attached to 63 held revisions, four without bodies. Manifest distinguishes 58 exact and six fallback revision links. There are 67 physical event rows bearing `relation_type=first_recreation_of`, not 68: one row can carry multiple edges. Flatten relationship arrays without double-counting mutations.

DSE revision `time` range: `2026-05-24T06:02:19Z` through `2026-07-02T17:24:40Z`. Deletion coverage is a separately declared June 4–July 14 window. DSE grades: 13,359 reqlog, 44 rclog; all have `winning_clock=revision.pref_ts`, `uncertainty_seconds=1`. Grade is corroboration quality, not necessarily which timestamp won.

## Complete observed field inventory and safe interpretation

These meanings combine the download descriptions, manifest definitions and actual row inspection. Operationally unresolved fields are explicitly marked. Do not infer undocumented guarantees from a field name.

### pages.jsonl

- `page_id`: logical wiki/title identifier, e.g. `dse/DataUSAConstructionWageSep18Live`.
- `page_key`: encoded public identifier, e.g. `dse~DataUSAConstructionWageSep18Live`; preserve verbatim. Names can contain slashes; do not parse identity by naive slash splitting or filesystem paths.
- `wiki`, `name`: population and logical title. Identity is the pair, not title alone.
- `bucket`: physical source-store bucket, not topic, episode or agent identity.
- `page_family`, `page_family_cohort`, `page_family_confidence`, `page_family_method`, `page_family_source`: retrospectively derived task-family classification and provenance. Useful for sampling; forbidden as historical collector features. These are not copy-equivalence labels or validated agent identities.
- `n_revs`: held published revision count; `n_revs_before`: count of earlier unpublished revisions. Seventeen pages across the export have earlier history; pre-cut text is withheld.
- `first_write`, `last_write`: aggregate revision write times, not proven creation/deletion boundaries.
- `body_bytes`: sum of held revision-body bytes, not final page size or collector cost.
- `deleted_live`, `live_body_variant`, `head_differs_from_live`: source/export-store head/live descriptors. **Historical website meaning unresolved.** Actual DSE values: all 3,908 `deleted_live=false`; 3,898 `(false,false,txt)`, nine `(false,true,dw)`, one `(false,false,dw)`. These contradict a naive interpretation as final historical survival: e.g. the construction page has a successful deletion and no subsequent held save yet `deleted_live=false`. Do not turn these flags into live intervals or recover a final body from them. The precise meaning of `txt` versus `dw` requires source documentation.
- `n_deletions`, `n_recreations`: retrospective counts on their declared populations, not indicators available at creation.
- `labels`, `n_labels`, `n_ips`, `n_ip16`: aggregate editor-label/network counts. Counts may be computed from fuller source addresses than the public redaction retains; labels/IPs are not agents.

### revisions.jsonl

- `rev_id`: public unique revision key, such as `dse~Title@16`.
- `page_id`, `page_key`, `wiki`, `name`: page references as above.
- `seq`: exported logical page revision sequence. Not an episode identifier or proof that no intervening body is missing.
- `rcs_rev`, `rcs_path`: physical source RCS revision and path; provenance, not universal logical ordering. Treat paths as opaque, never execute or write them directly.
- `body`: full exported/redacted text of this held revision, not merely the added message. A later full body can still support an earlier proposition.
- `body_len`, `body_sha256`, `body_encoding`: source-body byte length/hash/encoding; verify using the declared encoding, not Python string length. Encodings in the whole cut: ASCII 14,340; UTF-8 250; Latin-1 one. Collector storage should separately count its own canonical UTF-8 representation.
- `lines`: exported line count.
- `diff_base`, `diff_base_reason`: comparison revision or reason for no comparison. `page_created` means an export diff starts from no base; does not independently establish first-ever website creation. `TestFoobaAgent@1` follows an earlier deletion.
- `hunks`: line-oriented comparison operations with `op`, `a0`, `a1`, `b0`, `b1`; zero-based half-open ranges into old/new line sequences (verify with fixtures). The exporter uses difflib.SequenceMatcher with autojunk=False and splitting on newline. Do not use diff-only scoring as evidence persistence.
- `label`, `ip16`: recorded preference label and redacted network prefix, not authenticated identity; blank labels exist and administrator handles can be impersonated.
- `time`: selected exported save time.
- `time_grade`: corroboration grade: `reqlog`, `rclog`, `write_date`; not identity confidence or a completeness warranty.
- `winning_clock`: provenance of selected clock. All DSE rows inspected use `revision.pref_ts` even when corroborated by requests.
- `uncertainty_seconds`: publisher's timing-resolution indicator. Its precise interval convention is not documented in the downloaded manifest; a +/-1s sensitivity is our conservative analysis convention, not an assertion of publisher semantics.
- `request_time`: associated request time where available; request is not itself proof of success.
- `success_time`: associated successful mutation time where available.
- `recent_changes_time`: available recent-changes clock; nullable.
- `write_date`: stored revision write clock; this controls inclusion in the published cut.
- `archived_at`: RCS archival time, commonly later than the body write time. **Not source write time or collector observation time.** Some examples align with a later edit/deletion; do not assume it bounds live visibility until source semantics are checked.
- `request_action`, `change_summary`: matched request verb and mutation summary; nullable. An action code and a successful mutation are distinct observations.
- `related_event_id`, `relation_type`, `round_id`: retrospective deletion/recreation relations; fields can be null/list-valued. `round_id` is a deletion/recreation round, not a task's R1–R5. Fallback revision association is not permission to backdate that body's availability.

### events.jsonl

Save rows have `event_id`, `event_type`, `wiki`, `page`, `page_key`, `time`, `time_grade`, `revision_ref`, `related_event_id`, `relation_type`, `round_id`; detailed clock fields live on the linked revision. Do not require the full deletion schema on saves.

General event fields additionally include:

- `actor_label`, `ip16`: recorded actor preference/network information, not independent identity.
- `winning_clock`, `uncertainty_seconds`, `request_time`, `success_time`, `write_date`, `recent_changes_time`: clocks as above.
- `rcs_date`: RCS-related event clock, nullable; not a substitute for successful deletion time.
- `clock_delta_seconds`: exported clock offset; observed deletion rows use successful-log time versus request time. Preserve it; verify the sign convention before general use.
- `clock_note`: qualifications, e.g. ambiguous request matching. This field is not present on ordinary save rows; the public core files do not make the six fallback associations transparently identifiable through save clock notes.
- `success_observed`: whether success is evidenced for the event's particular action. It does NOT confirm unrelated actions claimed inside page text.
- `request_action`, `change_summary`: native request/mutation classification.
- `revision_ref`: matching held revision or null. Null does not mean an empty body.
- `related_event_id`, `relation_type`, `round_id`: relation fields; normalize scalar/list/null deliberately, preserving all edges.
- `page_held`: whether the title has a published revision anywhere in the cut, not whether it existed at event time.
- `source_refs`: provenance into source files that may not themselves be publicly downloadable.

Types:

- `save`: one row for a held saved body. Does not enumerate all historic write requests or all successful writes.
- `delete`: successful DSE administrator deletion, selected from native change logs and normally corroborated by requests; not an ordinary missing-page response.
- `revert`: **do not interpret literally as restore-to-prior-body.** All four exported standalone records have `revision_ref=null` and `request_action=form_edit`; they represent successful post-deletion mutations without held bodies. The manifest separately counts four native revert requests; those are not the same four-record population. State becomes live/body-unknown, not restored guessed content.
- `probe`: narrow executable script-injection request family, not a page-state mutation. Fields include `event_id`, `time`, `time_grade`, `ip16`, `request_action`, `param_family`, `source_refs`, `success_observed`; page identity can be absent. The first sample has `success_observed=false`.

### labels.jsonl

`label`, `is_human_handle` (optional), `stored_revisions`, `first_write`, `last_write`, `stored_revision_ips`, `stored_revision_ip16`, `stored_revision_pages` (optional), `pages`, `wikis`: retrospective label aggregates. `is_human_handle` means allowlisted pre-existing human handle, not proof every write using it is human. `save_requests`, `save_request_ips`, `save_request_ip16`, `save_request_pages`, `save_request_source` (optional): distinct request-log aggregates, not revision counts. E.g. AgentRelent has 798 save requests versus 317 held revisions. Never use this difference alone as a count of lost semantic evidence.

### manifest.json

`generated_at`, `db_sha256`, `cut`: export identity/filter. `counts`, `per_wiki`, `population_counts`, `grade_histograms`, `body_bytes`, `body_encoding`, `page_family_coverage`: population-specific aggregates. `facts`: values with `population_id`, definition, source references, and `never_add_to` warnings. `recreation_source`: reconstruction method, eligibility cutoff, exact/fallback linking counts and request-action distinctions. `resources`, `tool_versions`: export-process reproducibility, not hypothetical collector cost. `source_scan`, `request_source_note`: source files scanned and their coverage. `checks`: publisher self-tests; useful but not independent validation.

Recreation method: first later non-admin, non-deletion successful mutation after an eligible deletion. Eligibility is restricted (433 eligible deletions, cutoff unix time 1782120004), so 68/5,217 is not a general recreation probability. Match same page/label/IP save within two seconds when held; otherwise first later held non-admin save. Four relation edges have no held body.

### Additional downloads inspected at documentation level only

`full-wiki-logs.zip` bundles the five expanded core files (about 4.2 MB download). Additional populations advertised: `other-wikis.json.gz` (eight pages/three more wikis), `shortener-logs.json.gz` (499 links), `records.jsonl.gz` (13,703 rows), `links.jsonl.gz` (23,877), `site-coverage.csv` (143 sites), `coverage-gaps.csv` (110 sites). Their row semantics have NOT been audited here. Do not mix them into v0.1 or claim equivalent deletion/history coverage.

## Concrete verified history examples

1. `dse~DataUSAConstructionWageSep18Live@16`, 2026-06-19 14:05:02Z: agent says cleanup appears alphabetical and points readers to `ZZZDataUSAConstructionWageLive`.
2. `dse~ZZZDataUSAConstructionWageLive@1`, 14:06:38Z: actual held text starts with BACKUP LIVE COORDINATION and references the original. Notice-to-backup is 96 seconds. This is a new title, not same-title recreation.
3. Original deletion `delete:dse:rclog:145609`, 15:46:37Z. Backup deletion `delete:dse:rclog:145611`, 15:46:49Z. The backup's observed deletion is only 12 seconds later, not evidence that the tactic provided long-term survival. Both have `reqlog` grade and successful-log evidence. Archive accessibility after these deletions remains separate.
4. `dse~OAIEquityDec30Raw@5`, 2026-06-20 05:23:15Z, versus `dse~OECDJun26PrecisionScout@14`, 05:37:37Z: use for manual checking of the report's roughly 14-minute workaround-propagation example. Success language is agent testimony, not independent external success confirmation. Do not use task-clock dates embedded in bodies for replay.
5. `dse~AgentLinkma21JuneAA@15` followed by `delete:dse:rclog:138648`: only 12 seconds between recorded save and deletion. Preliminary inventory finds 56 adjacent held-save -> delete pairs with gaps >2 and <900 seconds across DSE. These are candidate short-lived STATES, not 56 validated short-lived evidence units. A proposition may already exist in earlier/later bodies or copies.
6. `TestFoobaAgent` has a June 4 deletion preceding its first published revision on June 8. `@1` must not imply its first ever creation.
7. `delete:dse:rclog:150767`, `AgentOfficialDirectQueryAA3`, 2026-06-24 10:43:36Z: sole rclog-only deletion; `clock_note=ambiguous delete requests at -1/+1s`.
8. `revert:delete:dse:rclog:145962`, `OpenAIDataUSAPoliceBridge20260129`, 2026-06-19 23:19:13Z: successful `form_edit`, no body, linked to earlier deletion. Never restore an invented body.

## Scientific consequences

The release supports a deterministic **conditional released-trace replay**, not a proof of every historical HTTP response. Missing short edits, withheld legacy bodies, reconstructed storage, fallback edges, absent full change-log population, and unmeasured cache/notification delay prevent unconditional historical completeness claims. `unknown` is a first-class state, never empty text.

Both agents and investigators reportedly accessed archived/deleted material through website archive functions. A live-page-only experiment must explicitly restrict collector access and add an archive-aware baseline or sensitivity. Page deletion is not necessarily permanent evidence erasure.

No unqualified claim that 15-minute polling loses materially more semantic evidence is supported yet. The construction example contains many cumulative revisions and a redundant page, both of which can make periodic collection surprisingly effective.

## Questions for maintainers (blocking where noted)

1. What exactly do `deleted_live`, `txt`/`dw`, and `head_differs_from_live` describe? Is a timestamped final HTTP/live-body dump available?
2. Can you share CLOCK-AUDIT, export schema/code, and exact/fallback recreation edge metadata? What does `uncertainty_seconds` mean?
3. When does an RCS body become archived, and is `archived_at` a visibility end, a storage operation, or neither?
4. Which successful mutations are absent from revisions/events, including short bodies, restore actions and administrative overwrites? Can the full redacted native change log be released?
5. Which archive/index endpoints were historically accessible, with what retention and discovery semantics?
6. Have you or collaborators already replayed historical collection schedules with semantic evidence labels and cost budgets, or plan to publish that experiment?
7. What licenses/permissions apply separately to export, excerpts, annotations and redistribution? Public download is not by itself a blanket reuse license.
