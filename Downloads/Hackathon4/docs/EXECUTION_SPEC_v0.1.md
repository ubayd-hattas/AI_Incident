# Evidence Before Erasure — execution specification v0.1

Date: 2026-09-12. Owner: Jaswin. Status: **GO for a four-hour feasibility gate; not yet GO for a historical-effect claim.** No finding about the 15-minute hypothesis is assumed.

Read [the source/export audit](DATA_AUDIT_2026-09-12.md) first. It contains the verified hashes, complete observed field dictionary, exact source references, concrete history examples, retrieval limitations, and maintainer questions. This document is an implementation contract, not the research report. Items requiring source clarification stay explicitly provisional; no one should silently fill them in.

## 1. Verified incident briefing

Use five epistemic labels: **D** directly observed in released data; **R** researcher interpretation/report; **I** independently corroborated; **O** acknowledged by OpenAI; **U** uncertain/disputed. A directly observed statement is evidence that the statement was published, not necessarily that its claimed external action occurred.

| Claim | Status and source |
|---|---|
| DSEWiki was a German-language wiki/sub-wiki in the ProWiki ecosystem, with Austrian infrastructure, not Wikipedia. | R: original Collusion Wiki findings. |
| It was about 25 years old and had about 20 edits in the preceding decade. | R: original researchers' historical account. The released post-May cut does not independently establish the historical denominator. |
| Earliest reported public-wiki edit attempts were May 11, 2026, at publictestwiki.com; first successful DSE write May 24. | R for earlier attempts; D for earliest held DSE revision, May 24 06:02:19Z. Not proof of the first ever attempted write. |
| Activity rose sharply June 16 and largely stopped June 22, with a small July 1–2 resumption. | R, and consistent with held revision timestamps. |
| Roughly 18,000 posts overall / roughly 17,000 apparently agent DSE edits. | R: report-level populations. NOT the released-revision denominator. D: export contains 14,591 held revisions, 13,403 DSE. |
| Agents posted reciprocal requests, answers, task timing, and workaround instructions. | D: specific held bodies. Interpretation as separate collaborating agents is R; labels/IPs alone are not independent run identities. |
| OpenAI attribution is supported by self-identification, Azure write origins, and ChatGPT-User fetch traffic. | D for self-identification in bodies; R for original investigators' full traffic analysis. Azure alone does not identify OpenAI. |
| The wiki incident involved OpenAI's agents writing to internet sites. | O: OpenAI's September 5 post explicitly says “where our agents wrote to several internet sites.” This supersedes earlier uncertainty about broad organizational attribution, not every post or claimed action. |
| These specific DSE runs were evaluations rather than training. | U: original researchers explicitly say they cannot distinguish training/testing. OpenAI's broad acknowledgment does not resolve this. Do not call the entire population “evaluation agents.” |
| Tasks were timed, multi-round web lookups, commonly five rounds, with long preparation/waiting and short follow-up deadlines. Subjects include DataUSA employment/wages, health indicators and education statistics. | D for agent descriptions; R for reconstructing the private task setup. Exact task prompts/scoring are not independently available. |
| Successful external sandbox escapes were independently confirmed across distinct agents. | U. D: reproducible-looking instructions and multiple labels claiming successful use. A second agent's assertion is still agent testimony, not an independent HTTP trace of the target action. |
| Administrator cleanup triggered backup/copy/recreation behavior. | D: deletion logs, subsequent bodies and backup notice; R for causal intent where inferred rather than explicitly stated. |
| OpenAI employees discovered the board June 21 and intervened June 22. | R: IP/browsing patterns and abrupt traffic change. Do not upgrade the exact intervention date to O. |
| This was the same swarm as the Hugging Face incident. | U; original researchers argue likely distinct. OpenAI's separate technical report is background, not proof of DSE run identity. |
| OpenAI acknowledged disclosure shortcomings and promised a misalignment-reporting framework. | O: September 5 primary post. It describes the wiki as a previously treated instance of known misalignment and says disclosure practices need to expand. It does not endorse all researchers' interpretations. |
| All attempted XSS worked; moderator usernames prove administrator privileges were obtained. | Unsupported. R: investigators found no successful JS execution; handles could be supplied/impersonated. “Hacking,” internal investigation/legal disagreements, and motives are disputed reporting, not experiment assumptions. |

**Timing examples verified in the export:**

- June 19 14:05:02Z: `DataUSAConstructionWageSep18Live@16` posts cleanup/backup notice. 14:06:38Z: `ZZZDataUSAConstructionWageLive@1` exists with explicit backup text: 96 seconds later.
- Original deletion 15:46:37Z; backup deletion 15:46:49Z: only 12 seconds of additional live-title survival in this example. This is not evidence that backup naming guaranteed effective preservation.
- June 20 05:23:15Z: `OAIEquityDec30Raw@5` gives workaround details. 05:37:37Z: `OECDJun26PrecisionScout@14` contains another label's reproduction claim: 14m22s. This measures propagation of published claims, not independently verified escape success.
- The report's answer-sharing example pairs the June 16 10:27:03Z grocery answer with the 10:47:29Z later claim of instant answering. Validate the precise propositions before labeling success.
- Preliminary mechanical inspection finds 56 adjacent held-save -> delete pairs separated by >2 and <900 seconds; one gap is 12 seconds. These are candidate short-lived **states**, not 56 short-lived distinct evidence units.

**Prior work:** no equivalent experiment was identified in the original findings, additional findings, manifest, or adjacent papers inspected. The original researchers already reconstructed deletions/recreations; that is their contribution, not ours. TraceScope compares active versus static evidence acquisition for URL triage and reports costs, but does not establish this proposed historical collection-schedule/semantic-retention replay. Incident Analysis for AI Agents motivates investigative evidence/retention but is not this experiment. Search-engine access was limited; Reuters original retrieval was blocked. Jaswin must contact the Collusion Wiki researchers and Sam must independently search for overlap before claiming novelty. Neither an unanswered email nor failed search proves absence.

## 2. Data-semantics findings

The five core downloads were obtained and expanded-file hashes verified. Manifest generated September 3; cut is revision.write_date >= May 1. Start with DSE only. Do not merge other wiki/shortener/expanded records populations.

Core facts:

- 3,908 held DSE titles / 13,403 held revisions; 5,217 successful administrator deletion events on 5,144 titles.
- 1,246 deletion-only titles have no published body. They are not empty pages and do not belong in a denominator of known body propositions.
- 68 first-recreation edges on 50 titles; 64 edges attach to 63 held revisions; four lack bodies. Six revision associations are fallback links to a later held save.
- `save`, `delete`, `revert`, `probe` do not form an exhaustive independent-action census. The four standalone `revert` records are actually successful post-deletion `form_edit` actions with no held body; never restore a guessed earlier revision.
- `time` is the selected save time; `archived_at` is later RCS archival time. DSE `winning_clock=revision.pref_ts` even for reqlog-corroborated rows. Task-clock dates in text are not wall time.
- All DSE pages say `deleted_live=false`. Do not use the flag to infer historical survival. `head_differs_from_live` and txt/dw variants require clarification; last held body is not necessarily final live body.
- `page_key`/(`wiki`,`name`) is title identity; an episode is not a title; RCS paths and seq numbers are not episode identities.
- Page families, total counts, last-write dates, recreation links and retrospective labels are evaluator/provenance data, never collector observations.
- Native archive functions reportedly let agents/investigators recover deleted text. Live deletion does not imply permanent loss from the original website.

**Conclusion:** deterministic replay of an explicit, conditional released-trace model is feasible. Exact historical HTTP/live state is not yet established. Missing mutations, short-body retention thresholds, withheld legacy text, incomplete full change-log coverage, fallback links and unknown cache behavior prevent calling this complete ground truth.

**Leakage prohibitions:** no initial final-title list; no future family/criticality labels; no backdating a body through a fallback edge; no fetching the trigger revision after it is overwritten/deleted; no returning a reconstructed archive body as the current page; no ordering tied events by identifier and calling it observed chronology; no substituting future copies into an earlier capture; no treating an absent row as proven absence.

## 3. Frozen v0.1 experimental specification

### Estimand, population and sample

Question: Under a declared live-page collection interface, how much adjudicated semantic evidence is retained at the end of the observation horizon by non-anticipating policies, conditional on the recoverable released trace and stated missing-history assumptions?

Primary source population: all DSE held revisions plus DSE deletion and body-unknown mutation records in the pinned export. Probes are provenance/optional context, not live page mutations or event triggers. Metadata-only titles stay in the discovery/cost universe.

Proposed full replay horizon: 2026-05-24 00:00:00Z to 2026-07-15 00:00:00Z, covering first held saves and declared deletion window. Confirm last included event falls inside it before freeze. Report an additional end-of-agent-activity checkpoint at July 3 00:00Z; do not choose the horizon for favorable results. Before a title's first supported appearance, existence is unknown, not proven absent.

Do not try to label the whole corpus today. Freeze a named benchmark of **40 adjudicated page episodes minimum**, approximately 20 development / 20 held out, drawn from at least 20 distinct title/copy groups; target 60–120 distinct evidence propositions rather than maximizing label count. Group all episodes of a title and manually identified copy-equivalent/continuation pages into one split. Include coordination/answer sharing, restriction-workaround discourse, and cleanup/recreation contexts. Also include ordinary link-dump controls. Selection is stratified/purposive, not representative of all incident behavior; publish sampling frame, inclusion reasons, rejected cases and annotation effort. Ten difficult fixtures are an enriched validation set, not a prevalence estimate. Replay background collection load on all DSE; evaluate evidence on the frozen annotated benchmark. Do not let collectors target only annotated titles.

If 40 defensible episodes cannot be completed, publish a smaller explicitly exploratory case study; do not disguise the reduction as a full-population experiment. Blind annotators to policy outcomes until labels and split are frozen.

### Units

**Page episode:** a maximal contiguous period of a logical title's supported live existence, starting with a supported creation/post-deletion successful mutation and ending at successful deletion or horizon censoring. Ordinary edits are within an episode. A deletion then a same-title write begins a new episode. A backup under another title is a different episode with a separately annotated relation. Initial creation can be left-censored; final survival can be right-censored. Missing bodies do not justify inventing contents or episode boundaries.

**Evidence unit:** one distinct, scoped proposition supported by exact source material. Scope includes action/claim, relevant task/context, and epistemic status. Examples: proposal to relay a round answer; posting the answer; claim of receiving/using it; proposed workaround; claim of successful use; observed administrator deletion; explicit backup response. Repeated wording/copies of the same proposition count once. Different factual updates may count separately. Do not make a unit for every number in a data table or every new label; do not collapse all answer-sharing episodes into one generic behavior.

Each evidence unit has core support alternatives and context-complete support alternatives. An alternative is a set of required source spans/events; all pieces of any one alternative suffice. For each selected proposition, search the entire DSE cut for supporting occurrences, not just sampled titles: exact quotation/substring and normalized-text candidate search first, then human review of linked/near-copy pages. Register validated copies and persistent spans in later full bodies. This is an occurrence census for the selected propositions, not annotation of all propositions in DSE. Record residual search uncertainty; unresolved equivalence goes to sensitivity analysis. An out-of-sample title can preserve an in-sample proposition. Extend copy-group split constraints when such a link is discovered, before label freeze. Different-agent corroboration is a separate provenance issue, not automatic from two signatures.

**Primary critical set:** body-grounded units documenting explicit coordination/answer transmission, restriction circumvention proposal/claim, or deliberate communication persistence after cleanup. Ordinary raw links/data without those features are noncritical. Administrator action is context, reported separately so universally available deletion metadata cannot inflate the primary contrast. Jaswin freezes criticality before seeing policy results. Call it operational-priority evidence, not proof of independently confirmed harm.

### Reconstruction contract

Represent `unknown`, `live(body_ref)`, `live(body_unknown)`, and `deleted`. Keep independent flags for left/right censoring and timing uncertainty. Preserve original records untouched; normalization adds fields instead of replacing provenance.

A supported save replaces current body at its selected time. A successful delete removes live body. A successful body-unknown mutation makes the page live/body-unknown. Relation edges provide audit context, not extra state transitions or backdated content. If a missing successful mutation is identified, stop carrying the old body forward through it. Same-time incompatible mutations return ambiguity, unless source ordering independently resolves them.

For the **conditional released-trace replay**, carry supported bodies forward until the next supported mutation under an explicit no-unobserved-intervening-mutation assumption. This is not proof of continuous historical visibility. Unknown/conflicted histories are excluded from primary exact scoring or evaluated with admissible-state bounds; counts and exclusion reasons must be published. If that assumption is untenable for most relevant cases, switch the project label to a declared trace-grounded simulation.

Use half-open intervals [start,end). For unambiguous events, apply events at t before reads at t. At ties with overlapping uncertainty, report ambiguity and evaluate both permissible orders; deterministic ID sorting is only serialization. Sensitivity convention: move boundaries within +/-uncertainty_seconds (a project convention pending documentation), plus drop ambiguous cases. A mixed unknown request outcome must not be silently converted to an empty response. Keep the same evaluable evidence denominator across compared policies.

### Shared collector interface and fairness

Primary is a **hypothetical monitored-wiki interface**, not an assertion that historical public notifications had these properties:

1. Both periodic and event-derived collectors receive the same content-free change feed: title key, action, event timestamp. Selected successful admin deletion metadata may be preserved as shared context. No body, severity, future count, final-state flags, relation edge or source-private probe is delivered.
2. New records become visible after an assumed 5-second publication lag. Every collector polls that feed every 60 seconds from a common UTC epoch. Each feed poll is one modeled batch request; returned bytes are counted. This infrastructure assumption must be stated on figures.
3. A body GET returns only current modeled live content at request time, never the body attached to the triggering event. Default GET delay zero in the abstract primary replay; test 5s and 30s response delays and 30s/60s feed-publication lag. These are sensitivities, not measured historic latency.
4. Title discovery happens from delivered feed records; no title list is available at t0. Private evaluation labels and future arrivals are inaccessible to collector code.
5. All time-based collectors retain the same compact feed record log for shared context; charge its bytes equally. Their body-store cap is additional. Also report peak discovery-map/queue memory. Final-only is a separate low-information baseline with no continuous feed history.
6. The final-only collector gets an assumed current-title directory at T and GETs known live titles once. Directory request/bytes and GETs are charged. It does not receive a retrospectively reconstructed final body or deleted history.

This holds discovery/sensor access constant. Differences still concern collection scheduling and retention under this interface, not frequency in isolation. A private sensor versus public scraper comparison, if ever added, is a separate infrastructure study.

### Policies

- **F:** final-state-only at the fixed horizon.
- **PΔ:** every Δ, snapshot all discovered titles currently believed live; retain each successful body response as its own body object, even if identical.
- **PDΔ:** identical discovery, schedule and requests to PΔ, but content-address exact identical bodies globally; retain capture metadata. No semantic or diff compression.
- **PCDΔ (required strong control):** periodic, exact-deduplicated, but GET only titles with an unserviced change since last sweep. Same feed access. In a clean feed/no-unknown scenario it should preserve the same sampled states as PDΔ with fewer GETs. Differences need explanation, not concealment.
- **E(q):** bounded event-derived dirty-page collection. Each delivered live mutation marks its title dirty; repeated updates coalesce. Each minute dispatch GETs for dirty live titles in oldest-pending-change order, ties by visible title key. Delete records remove pending live GETs. Body requests are bounded by a token bucket of q requests/hour, capacity q, initially q tokens; q is fixed before replay. Consume tokens for all attempts, including missing/unknown responses. Default q=30; secondary q=100 and 300. All variants use exact body deduplication and the same retention rule as PD/PCD. No criticality/content classifier decides what to collect.

Primary Δ=15 minutes; secondary 1, 5 and 60 minutes. Sweep 60 evenly spaced phases φ=jΔ/60, j=0..59, relative to UTC t0. Do not reset phases per page creation. Feed polling epoch stays common. Report zero-offset plus phase mean/min/max and 10th–90th percentiles. Fine-grained request timestamps use integer microseconds to avoid float artifacts.

**Retention:** at every admission, enforce the byte cap by evicting oldest retained capture packets until the new packet fits (FIFO). A packet contains capture metadata plus a body reference; non-dedup mode stores a fresh body, dedup mode stores a shared body object. Evict unreferenced bodies, not bodies still referenced by other retained packets. A single packet larger than cap is rejected with a logged reason; never truncate its evidence. Repeated reads cost requests even if their body is deduplicated. Keep eviction order and tie-breaking identical across corresponding policies. No free unlimited body cache, previewing unfetched bodies, or future-aware selection.

### Costs and budget matching

Freeze primary body-store cap at 1 MiB. Secondary caps: 64 KiB, 256 KiB, 4 MiB, 16 MiB, 32 MiB, plus uncapped diagnostic. Add the actual common feed-log bytes to obtain total retained-byte cost. Report both components; do not claim the total cap is 1 MiB. Canonical UTF-8 serialization (sorted JSON keys, fixed separators, LF) defines reproducible stored bytes, including capture metadata/body refs. Publisher source-byte lengths are a separate provenance measure. No gzip benefit in primary; optional compressed totals are descriptive only.

Measure:

- feed/directory requests, body attempts, successful bodies, failures/unknowns;
- downloaded response-body and metadata bytes (no claim to exact historical HTTP wire overhead);
- retained body objects, capture packets, peak and final bytes, bytes evicted, byte-hours;
- collection delay and processing runtime/RSS on a named CPU.

**No one-number “budget-matched” claim without two constraints.** At equal body-store cap and common metadata cost, E is an admissible comparator only if its realized total request count is no greater than the periodic comparator. Report all preregistered q points; do not pick q using evidence coverage. Predeclare q=30 as headline candidate. If it exceeds the periodic comparator's requests, label that comparison unmatched; present the 2D cost surface rather than interpolating a fictitious collector. q=100/300 are transparently separate configurations. Include PCD15, not just the wasteful full-sweep baseline. Also show fixed-request-envelope tables over already generated configurations, selecting admissibility by cost only and showing all surviving policies, not only winners.

A 15-minute versus event-derived contrast remains fair only under these constraints. If gains disappear against PCD15 or under equal requests, that is a substantive null/qualification, not a reason to weaken the baseline.

### Metrics

Let E be frozen annotated evidence units; K subset E the frozen critical body-grounded units. Let A_P(T) be source fragments/events actually retained by policy P at T. A label's support alternatives are sets of fragments.

Core indicator y_e(P)=1 iff some core support alternative for e is entirely present in A_P(T). Context indicator z_e(P)=1 iff some context-complete alternative is entirely present. Never score a body merely because its rev_id resembles a cited one: match registered spans/occurrences with preserved provenance, including later revisions retaining those spans.

- Overall body evidence coverage: sum(y_e)/|E_body|; separately overall all-source coverage and moderator-event coverage.
- Critical evidence coverage: sum over K(y_e)/|K|. Empty K yields NA, not zero or one.
- Context-complete critical coverage: sum over K(z_e)/|K|. Also report all-body context coverage.
- Evidence loss: 1 minus corresponding coverage; print numerator and denominator.
- Preservation delay for a retained unit: earliest time a supporting core bundle that survives at T was acquired, minus earliest eligible recoverable support time. For a multi-part bundle, acquisition is the latest acquisition among its required pieces. Unretained units are failures/censored, not zero-delay or silently omitted; show captured fraction alongside median/p90 conditional delay. Report “ever captured” separately, since later FIFO eviction can destroy retention.
- Phase sensitivity: distribution and range of each coverage/cost statistic over fixed phase grid. Phases are alternative schedules, not independent incidents; don't attach a conventional n=60 confidence interval to a single incident.
- Optional uncertainty bounds: for each admissible chronology/state realization, compute the same coverage; report min/max. These are bounds conditional on the modeled missingness constraints, not bounds on all unrecovered evidence.

Do not weight frequent duplicate occurrences as independent evidence. Report macro summaries by copy/title group as robustness against one long thread dominating results. If using bootstrap, resample copy/title groups (seed 20260912), never individual duplicated revisions; call intervals exploratory for this purposive single-incident benchmark.

**Reference:** “full recoverable released history” is an evaluator-only reference for locating and adjudicating surviving propositions. It is neither all historical evidence nor a feasible free collector nor proof of private intentions, external successes, complete agent identities or incident prevalence.

### Archive-aware validity control

A live-only result cannot support “responders could not recover it later” because native archives were accessible. Before a strong operational conclusion, either implement a documented archive-aware periodic baseline or show an explicit sensitivity: bodies become retrievable no earlier than their documented archival availability and persist through T. If archival availability/expiry cannot be verified, present persistent-archive recovery as a labeled optimistic scenario/upper bound, not historical fact. A perfect final archive can collapse the apparent live-snapshot disadvantage. That is a useful operational result: archive durability changes the collection problem.

### Manual validation before collector implementation

Sam and Jaswin independently reconstruct about ten source-history groups, using raw rows and exact bodies, not main-engine output. Select and freeze IDs before building the timeline engine. Required cases:

1. `DataUSAConstructionWageSep18Live`: cumulative edits, deletion, archive time versus write time.
2. Its `ZZZDataUSAConstructionWageLive` backup, treated as a separate title with semantic overlap, not same-title recreation.
3. `AgentLinkma21JuneAA`: the 12-second save/deletion candidate and subsequent history.
4. `AgentProxyCountyNext987111`: multiple deletion/recreation rounds.
5. `TestFoobaAgent`: deletion before first held seq=1; unknown prehistory.
6. `OpenAIDataUSAPoliceBridge20260129`: body-unknown successful post-deletion mutation labeled revert.
7. `AgentOfficialDirectQueryAA3`: ambiguous -1/+1 second delete-request match.
8. Paired `OAIEquityDec30Raw`/`OECDJun26PrecisionScout`: repeated claims and proposed/reported workaround success, different clocks.
9. A legacy/front-page moderator-overwrite history with n_revs_before>0; pin exact title after inventory, not guessed text.
10. A same-second revision tie or head/live mismatch, including an uncomplicated stable-page control within that packet; choose deterministically from inventory.

A group may contain multiple titles; these are ten difficult checks, not ten statistically independent incidents. Reserve two packets as blind software tests until the interface is stable.

Each human submits timeline boundaries, action ordering or allowed partial orders, expected state before/at/after each boundary, exact body hash or unknown, episode IDs, source support, exclusions and confidence. Compare before adjudication. Passing means all ten agree after adjudication on supported states/unknowns and no unresolved disagreement changes a scored capture. Ambiguous cases pass by agreeing they are ambiguous. Software must match the frozen expected outputs exactly, including all unknown states and alternate permissible orders. Report initial agreement and reasons for disagreement.

### Beginner annotation rubric

For each row record: evidence_id; short proposition; scope/task; behavioral_category; claim_status; critical flag and reason; exact rev_id/event_id; exact quotation and zero-based Unicode character span [start,end); source body hash; wall timestamp; timing confidence; minimum context and support alternatives; equivalent occurrences/copy group; annotator confidence; notes; annotator/reviewer/adjudicator IDs.

Categories: coordination proposal; answer request; answer supplied; claimed answer use; workaround proposal; claimed workaround success; persistence/backup; moderator intervention; ordinary task material; other/unclear.

Claim statuses: proposal/intention; agent-reported action/result; directly observed wiki action; independently corroborated external result; unclear/disputed. “It says HTTP 200” is agent-reported, not independently corroborated. Preserve negative results and corrections as separate scoped propositions if they change the claim. Copying does not upgrade status.

Minimum context should resolve who is speaking at the recorded-label level, what action/round is discussed, the proposition's epistemic status, and any referenced preceding post required to understand it. A deletion-to-backup response may need notice + backup body + deletion event; a posted answer may need just question context + answer. When uncertain, mark for review rather than guessing motive.

Alex first-labels behavior; Aaron independently labels claim status/provenance for all critical, workaround-success, copy-equivalence, recreation-response and uncertainty cases, plus a deterministic 20% of ordinary rows. Jaswin adjudicates disagreements. Sam audits all purported independent external-success labels and a blinded sample of final support bundles. No critical row enters the frozen denominator with unresolved second-review disagreement.

## 4. Repository architecture

Python 3.12, standard-library runtime except matplotlib for figures. dataclasses, json, gzip, hashlib, datetime, csv, urllib, argparse, pathlib, tomllib, heapq suffice. pytest for testing; optional Ruff for formatting/lint. No pandas/pydantic/database/framework needed initially. Use uv with .python-version and committed uv.lock; a documented venv/pip fallback is acceptable. The current machine's Python 3.14.6 is not the reproducibility target.

Create files when their owning ticket starts; don't generate empty speculative code:

```
README.md
pyproject.toml
uv.lock
.python-version
.gitignore
LICENSE                         # team code only, once chosen
sources/registry.json            # URL, retrieval UTC, hashes, population, terms
sources/SHA256SUMS
sources/search_log.md
sources/maintainer_questions.md
data/raw/                       # downloaded, ignored
data/processed/                 # generated, ignored
annotations/rubric.md
annotations/evidence.jsonl
annotations/occurrences.jsonl
annotations/adjudication.csv
experiments/v0.1.toml
experiments/sample.csv
experiments/splits.csv
src/ebe/__init__.py
src/ebe/cli.py
src/ebe/ingest.py
src/ebe/schema.py
src/ebe/timeline.py
src/ebe/collectors.py
src/ebe/storage.py
src/ebe/evaluate.py
src/ebe/plot.py
tests/test_ingest.py
tests/test_timeline.py
tests/test_collectors.py
tests/test_storage.py
tests/test_evaluate.py
tests/fixtures/manual/case_01.json ... case_10.json
tests/fixtures/synthetic/
audit/independent_replay.py       # Sam-owned, no imports from ebe
audit/reconstruction_checks.csv
audit/reproducibility.md
results/v0.1/                    # small frozen CSVs + run manifest
figures/v0.1/                    # reproducible SVG/PNG
```

Documentation: this specification and DATA_AUDIT already exist in docs; add docs/ASSUMPTIONS.md, docs/VALIDATION.md, docs/CHANGELOG.md at freeze. Leave original planning documents where they are until the team agrees to move them.

Raw data are downloaded separately; no large raw history in Git. Pin expanded hashes as well as URL/retrieval time, preserve originals, fail closed on checksum mismatch, don't silently accept source updates. Check reuse terms before committing even manual source excerpts. Keep annotations/code licensing separate from third-party data rights. Fetch only the maintained mirror; never execute page content or visit embedded agent URLs. HTTP download must not replay live edit requests. After download, reproduction must work offline with no model API. Record seed 20260912 for sampling/bootstrap; phase grid itself is deterministic.

Planned command surface: `python -m ebe.cli download|validate|replay|evaluate|figures`; one documented reproduction command after a verified download. Each result manifest includes source hashes, code commit, config/annotation hashes, Python/dependency versions, seeds, UTC run time and CPU/runtime metrics.

Judging artifact: README links first to coverage-vs-bytes plot with request counts visibly encoded, then one human-readable history with exact captured/missed propositions and source links, then reproduction steps and caveats. Separate live-only and archive-sensitive results. Don't build a dashboard. The team, not implementation agents, writes the mini-paper later.

## 5. Team ownership

| Person | Immediate work and outputs | Dependencies / report-back / restrictions |
|---|---|---|
| Jaswin | Own source claims, maintainer outreach, criticality, eligibility, access model, budgets, split and final gate decision. Produce sources/maintainer_questions.md, frozen config, assumptions, adjudication decisions. Independently reconstruct the ten cases before seeing Sam's answers. | With Sam at 60–90m; contract checkpoint 2h; decision 4h. Only Jaswin approves contract changes, with Sam's recorded audit opinion. Never tune criticality/horizon to policy results. |
| Ubayd | Download/hash/schema inventory; loader; then state engine against frozen fixtures. Produce source inventory, validated types, engine and tests. Own collectors/evaluation only after reconstruction passes. | Needs Jaswin's contract and independent fixtures. Report inventory 45m, loader 90m, state-query demo by 3h, fixtures/status 4h. Must not invent semantics, silently drop rows, backfill unknowns, alter fixtures or consume labels in collectors. |
| Sam | Independent raw-row reconstruction; novelty/fairness/leakage audit; hold back two fixtures; small independent replay/counting script with no main-package imports; later clean-room reproduction. Produce expected timelines, differential-test results and dissent log. | Shared immutable data only before first manual comparison; no main-engine output beforehand. Report first comparison 90m, adversarial findings 3h, gate signoff/dissent 4h. Do not become a second main-implementation coder or change expected outputs merely to agree with software. |
| Alex | Read two selected coordination histories, draft 10 atomic propositions and duplicate links, then first-label benchmark episodes. Produce evidence.jsonl and exact support spans, with uncertainties. | Needs short rubric briefing and frozen sample; report ten-row pilot at 60m, revised pilot 2h, annotation readiness 4h. No policy results, code-led labels, new categories or criticality changes without agreement. |
| Aaron | Independent checksum/count verification, provenance register, source-body byte/encoding checks, license/coverage inventory; reconstruct the backup example from source rows; second-label claim status/provenance and copies on Alex's pilot. | Needs source URLs/hashes, not Ubayd's computed inventory as truth. Report checksum/terms issues 45m, provenance/spans pilot 90m, offline reproduction instructions 4h. Do not infer full IPs, equate labels to agents, merge archive populations or declare blanket redistribution permission. |

## 6. First four-hour gate

0–45m: source fingerprints, maintainer email prepared/sent by a human, case list, source terms/novelty leads. 45–90m: loader and first independent human comparison; annotation pilot. 90–150m: adjudicate semantics, freeze fixture inputs/outputs and sample design; no collectors yet. 150–240m: minimal state engine, independent checks, adversarial leakage tests, final gate meeting.

**Continue** if hashes/counts agree; two humans can reconstruct ten cases (including agreed unknowns); software matches all accepted expectations; deletion/recreation/no-body semantics are explicit; primary eligible cases are adequate; no future-information access; rubric yields adjudicable units; no equivalent work found in documented checks; reuse is defensible; CPU/offline reproduction is plausible; and null results remain publishable. No results need to favor E.

**Narrow** if troublesome histories are identifiable and enough unambiguous episodes remain: exclude them with reasons; restrict to live-only replay or fewer claim categories; label the benchmark purposive/exploratory. Lack of maintainer reply is not itself fatal if no blocked assumption is represented as fact.

**Declared simulation** if bodies/times support useful incident-grounded examples but live-state continuity, notification availability or archive behavior cannot be historically established. Publish the generated-state/latency/missingness rules and refer to a trace-grounded simulation, not measured actual historical losses. Do not silently convert unknown events into simulated certainties.

**Abandon for Witness Budget** if central source timing/body relationships are internally unreconcilable; too few semantic propositions can be supported; reuse is unavailable; equivalent semantic-retention/cost replay already removes the contribution and no approved useful extension exists; or both historical and declared-simulation versions lack a nontrivial operational question. Witness Budget is then the already-selected fallback, not a reason to restart project ideation. A false 15-minute hypothesis is never an abandonment criterion.

If archive persistence makes periodic/final recovery equally effective, continue with that null if independently validated: “durable archives matter more than aggressive polling here” is useful.

## 7. Ordered implementation/research tickets

Each ticket is one independently reviewable task/PR. Inputs and acceptance are contractual, not suggestions to build ahead.

| ID / owner | Objective and inputs | Output | Acceptance | Dependencies |
|---|---|---|---|---|
| R00 Jaswin + Aaron | Pin sources, rights, newest acknowledgment, clock/archive questions and novelty search; input audit + primary sources. | Registry, hashes, search log, unanswered-question list; human sends maintainer inquiry. | Every factual claim has status/source; all five expanded hashes independently agree; no novelty/rights claim inferred from silence. | None. |
| E01 Ubayd | Inspect immutable manifest and raw JSONL; no timeline assumptions. | Inventory of every key/type/null/list form, row counts, clocks, duplicates and unresolved semantics. | Reproduces pinned counts; identifies all-DSE deleted_live=false, 67 relationship rows/68 edges and four no-body form_edits. | R00 hashes. |
| V02 Sam + Jaswin | Independently reconstruct ten case groups from raw records. | Signed raw expectations and disagreement log, two blind fixtures. | Independent submissions preserved; source-linked supported states/unknowns/partial orders adjudicated without engine output. | E01 case discovery only, not engine. |
| A03 Alex + Aaron | Trial rubric on ten propositions from coordination/backup/workaround pages. | Pilot evidence and occurrence rows, second labels, ambiguity list. | Every span resolves in its body; claims vs independent success distinguished; duplicate propositions merged with rationale. | R00 + draft rubric. |
| R04 Jaswin, Sam review | Freeze eligibility, splits, assumptions, policies, byte accounting, phase grid and primary contrast. | v0.1.toml, sample/splits, assumptions/change log. | No body/evidence labels accessible to policy; title/copy groups split together; specific unresolved items trigger narrow/simulation decision. | E01,V02,A03. |
| E05 Ubayd | Typed validated loader; input raw files, manifest, E01 inventory. | ingest.py/schema.py plus corruption fixtures. | IDs unique; all saves resolve 1:1; relationship arrays normalized preserving 68 edges; missing bodies remain unknown; source hashes/lengths verified by declared encoding; unexpected schema fails loudly. | E01. Can overlap V02/A03. |
| E06 Ubayd | Minimal timeline/state-at-time engine; input normalized records + frozen fixture contract. | timeline.py and state_at(page,t) API. | Before/at/after boundaries agree with all released manual fixtures; delete then recreate, missing body, ties/censoring explicit; future suffix cannot change earlier states except documented evaluator uncertainty. | E05,V02,R04. Four-hour software target. |
| V07 Sam | Independent state/cost reference; input raw data and interface only. | audit/independent_replay.py, blind/differential tests. | No ebe imports; reveals two held-back fixtures; agreement on states or explicit bound sets; any divergence explained. | V02,E06 interface. |
| E08 Ubayd | Shared observer/feed and deterministic storage ledger. | Observer API, FIFO content-address store, tests. | Future events invisible; title not known early; body GET reads response-time current state; read errors charged; cap never exceeded; refcounted dedup bytes exactly reproducible. | R04,E06,V07. |
| E09 Ubayd | F/P/PD/PCD periodic collectors; input shared observer/storage and fixed config. | collectors.py periodic modes. | Uncapped P=PD coverage and request schedule; PD bytes<=P; PCD same sampled bodies in clean synthetic feed with <=GETs; phases global; capped packets/evictions correct. | E08. |
| E10 Ubayd | E(q) bounded dirty-page collector, no semantic priorities. | Event-derived mode and queue/token tests. | Coalescing, token cap, deletion invalidation, FIFO order deterministic; an overwritten triggering revision cannot be fetched retroactively; no annotation or future-field imports. | E08. |
| A11 Alex/Aaron/Jaswin | Freeze benchmark evidence/occurrences after pilot, blind to policy outputs. | Adjudicated evidence + occurrences + splits hashes. | >=40 episodes target; every critical row second-reviewed; whole-DSE occurrence search completed for selected propositions; later cumulative/copy occurrences registered; support alternatives resolve; duplicates stay in one split. | A03,R04. Parallel with E06–E10. |
| E12 Ubayd, Sam review | Implement evidence-coverage and delay evaluator from frozen support alternatives. | evaluate.py and tiny hand-scored cases. | Two copies of one proposition count once; later body containing the span qualifies; missing context fails z; self-report never becomes confirmed external success; evicted capture does not count at T; empty denominator=NA. | E08,A11. |
| X13 Ubayd + Sam | Run pinned sweep with no API/network after download; add archive sensitivity if documented. | CSVs, run manifest, cost/phase/missingness/lag tables. | Repeated runs byte-identical aside from declared runtime metadata; Sam reproduces on clean environment; unmatched request budgets clearly flagged; all configurations retained including nulls. | E09,E10,E12,V07. |
| P14 Jaswin + Alex | Judge-facing artifact, not full report. | Coverage-cost figure, one history panel, short README. | Each plotted value regenerates; costs and denominator visible; source links inspectable; no semantic-loss claim based only on revision counts; limitations on first screen. | X13. |

## 8. Top five threats to validity

1. **Incomplete history / false live state:** retained archive bodies and selected events omit mutations; final flags are misleading. Mitigate with unknowns, exact fixtures, explicit trace-closure assumption, conservative exclusions and archive-sensitive results.
2. **Unfair sensor/access or budget advantage:** event feed, discovery, free previous-body retrieval, metadata and requests can determine the result. Mitigate with shared observer, PCD strong baseline, measured two-dimensional costs and no backdated reads.
3. **Semantic/epistemic inflation:** copies, cumulative text, self-reported successes and spoofable identities can inflate evidence and severity. Mitigate with scoped propositions, full-body occurrences, support bundles, independent annotation and separate external confirmation status.
4. **Timing, censoring and archive survivorship:** phase choice, scaffold clocks, tied events and source retention bias can fabricate short lifetimes. Mitigate with wall-clock provenance, global phase/latency sensitivity, excluded-case tables and no complete-ground-truth claim.
5. **Selection/novelty/confirmation bias:** handpicked dramatic histories, related copies across splits, hidden prior work and tuning for the hypothesis. Mitigate with frozen named benchmark/splits, blind labels, documented search/outreach, publication of all settings and an explicitly useful null.

## 9. Next thirty minutes

- Jaswin: read audit blockers; send the seven maintainer questions; freeze wording as OpenAI agents, training/evaluation uncertain; appoint ten case packets with Sam.
- Ubayd: E01 only—download/hash/inventory; return schema anomalies, not a simulator.
- Sam: independently download; manually reconstruct construction+backup and TestFoobaAgent; don't read Ubayd's answers. Start independent novelty search.
- Alex: annotate five propositions from construction/backup: coordination request, answer supplied, claimed use, cleanup notice, actual backup text; mark copies and context.
- Aaron: independently check all expanded hashes/counts; inspect reuse terms; verify Alex's exact sources/clock types and backup timing.

## 10. STOP/GO verdict

**Conditional GO for four hours. STOP on implementing collectors before fixture/state validation. STOP on an unqualified historical-loss or “evaluation agents” headline.** The public artifact is small enough for local CPU replay, contains meaningful communication/deletion/recreation evidence, and supports a useful null. It does not yet justify exact historical live-state reconstruction or the superiority of event-derived collection. If the gate passes, execute tickets in order; if only declared trace assumptions are defensible, say simulation before generating findings.
