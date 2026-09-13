# A11 context axis — Sam's independent DRAFT (for comparison, not accepted ground truth)

**This document and the files it describes (`annotations/context_fragments_DRAFT_SAM.jsonl`,
`annotations/context_eligibility_DRAFT_SAM.jsonl`) are an independent draft, produced to be compared against
whatever Alex/Aaron/Jaswin produce for the same requirement — they are explicitly not adjudicated, not
second-reviewed, and not authorized as accepted annotation ground truth.** Every file/field name says `DRAFT_SAM`
for exactly this reason. Nothing in `annotations/evidence.jsonl`, `occurrences.jsonl`, or `eligibility.jsonl` (the
real, already-committed files) was touched to produce this.

This covers the parts of acceptance-matrix items C, D, and E that `audit/A11_ITEMS_CDE_PROGRESS.md` explicitly left
open as requiring human judgment: context fragments, context-eligibility, and near-copy occurrence review.

## Method

For each of the 65 propositions, `evidence.jsonl`'s own `support_bundles.context_complete` field (already authored
by Alex) lists which revisions/events beyond the core anchor are needed as context. Independently re-deriving this
directly from the raw data (not copying the acceptance matrix's own inventory) found:

- **59 propositions** list only their own anchor's `save:<rev_id>` in `context_complete` — i.e., no additional
  revision is required, only the observable fact that the anchor save happened. Modeled as a single
  `observable_feed` fragment (`page_key`, `action="live_change"`) — a fair, minimal typed reading of "this was
  redundant with core," converted into an actual predicate rather than left as a bare revision-ID reference.
- **6 propositions** require a genuinely different revision or event as context. For each, the specific required
  substring or event was independently identified by reading the target revision's real body / the raw event
  record, then **verified as an exact substring/event match before being written down** (never asserted without
  checking):
  - `PROP-20260619-03` → requires `dse~DataUSAConstructionWageSep18Live@1`'s coordination-header text (showing the
    "shared answer" the proposition claims to use actually existed).
  - `PROP-20260620-07` → requires `dse~OAIEquityDec30Raw@1`'s bypass-technique text (the original SNI/NO_PROXY
    claim being replicated).
  - `PROP-20260620-08`, `PROP-20260620-09` → require the same text, persisting to `@4`.
  - `PROP-20260619-04`, `PROP-20260619-05` → see the discrepancy below; these need **two** context fragments each.

## A real disagreement found against the independently-produced acceptance matrix

The acceptance matrix's own "Complete affected-record inventory" (§C) named exactly four propositions needing
additional revisions: `-03`, `-07`, `-08`, `-09`. **Independently re-deriving this from `context_complete` directly
finds two more: `PROP-20260619-04` and `PROP-20260619-05`**, each requiring a different page's body text *and* a
delete event:

- `PROP-20260619-04` (the notice warning of an impending cleanup sweep, with a fallback pointer to the ZZZ backup)
  needs: (a) the ZZZ backup page's own opening text, confirming the named fallback genuinely exists and cross-links
  back — verified exact match at `dse~ZZZDataUSAConstructionWageLive@1`; and (b) the actual deletion of the
  *original* page — `delete:dse:rclog:145609`, looked up directly in `data/raw/export/events.jsonl`
  (`page_key=dse~DataUSAConstructionWageSep18Live`, `2026-06-19T15:46:37Z`).
- `PROP-20260619-05` (the ZZZ backup's own opening, claiming to link back to the original and summarize it) needs:
  (a) the original page's own persisting header — verified exact match at
  `dse~DataUSAConstructionWageSep18Live@16`; and (b) — this is the surprising part — the deletion of the **ZZZ
  backup page itself**, `delete:dse:rclog:145611` (`page_key=dse~ZZZDataUSAConstructionWageLive`,
  `2026-06-19T15:46:49Z`), not the original. This implies the backup mirror was later taken down too, consistent
  with `GRP-01-CONSTRUCT`'s documented repeated persistence/takedown cycle, but this specific reading should be
  double-checked against Alex/Aaron's own interpretation — it's exactly the kind of judgment call this draft is
  meant to be compared against, not presumed correct because it came from a careful derivation.

Whether this is a real gap in the acceptance matrix's inventory or a difference in scope/definition is worth
resolving explicitly when comparing against the human team's version.

## Near-copy occurrence search (Item D's harder half): one finding, with a recommended disposition

Ran a normalized (whitespace-collapsed, case-folded) search — one step more permissive than the byte-exact search
in `audit/occurrence_census_search.py`, still objective, not yet semantic paraphrase detection — across all 65
propositions' spans against the full corpus. One result:

- `PROP-20260616-10` (a non-critical, "ordinary task material" negative control — bare DataUSA API documentation
  URLs) has normalized matches on five *different* pages (`dse~DataUSAQueryBridgeFeb03Poverty1@1/@2/@3`,
  `dse~DataUSAQueryBridgeXQ9@1`, `dse~DataUsaApiBridgeJunePlace@1`), none currently in any of the 25 groups'
  catalogs.

**Recommended disposition (draft, not final):** do not add these as occurrences. The matched text is a generic
API endpoint URL, and finding it reused verbatim across several unrelated documentation pages is consistent with —
arguably confirms — this proposition's own classification as an ordinary, non-critical control, not evidence of a
genuine additional occurrence of *this specific proposition's claim*. Treating a shared boilerplate reference as a
"cross-title mirror occurrence" would inflate the occurrence count without adding real evidentiary content. This is
a judgment call, disclosed as such, and should be confirmed or overridden by human review, not treated as settled.

No other propositions produced any normalized-match candidates beyond what the exact-match census already found.

## What was deliberately not attempted

- Genuine semantic/paraphrase near-copy detection (different wording, same meaning) — this needs human judgment
  about equivalence and was not attempted at all, not even as a draft.
- Re-deriving `minimum_context`'s free-text prose into a fully formal predicate language beyond
  `body_span`/`observable_feed` — the two-kind model in `src/ebe/evaluator.py` is what exists; a real annotation
  schema might reasonably want more expressive predicate types (e.g., "temporal ordering between two events"),
  which is exactly the kind of schema design decision belonging to Alex/Aaron/Jaswin.
- No coverage or delay scoring was run using this draft context data against any real collector output, in
  keeping with `docs/E12_SUBSTRATE.md`'s and `docs/X13_RUN_CONTRACT.md` §9's scope — `tests/test_a11_loader_context_draft.py`
  checks only structural loading and the population firewall.

## Reproduce this

```powershell
python -m unittest tests.test_a11_loader_context_draft -v
python audit/near_copy_search_DRAFT_SAM.py
```

The `context_complete` cross-reference used to find the `-04`/`-05` discrepancy against the acceptance matrix's
inventory was a direct read of `evidence.jsonl`'s own `support_bundles.context_complete` field (see the Method
section above) — reproduce by comparing each proposition's `context_complete` list against its own `core` list and
`rev_id`.
