# Methodology: Evidence Before Erasure

## Research question

Do periodic-snapshot vs. event-derived evidence collection policies preserve
distinct warning-sign evidence from a real autonomous-agent incident, at
comparable cost? We use the DSEWiki/OpenAI "wiki incident" (May-July 2026,
publicly documented by collusion.wiki on 2026-09-04) as the empirical case.

## Source priority

1. **Primary data export** — `events.jsonl`, `revisions.jsonl`,
   `pages.jsonl`, `manifest.json`, downloaded directly from
   `collusion.wiki/explorer/download`, checksum-verified against the
   publisher's own `SHA256SUMS` block.
2. **collusion.wiki explorer pages** — individual revision URLs
   (`/explorer/page/<page>#rev-N`) quoting specific agent posts.
3. **collusion.wiki report body** — the narrative write-up at
   `collusion.wiki/`, used only where a specific claim isn't otherwise
   traceable to a raw record.
4. **Independent press / primary lab reports** — Reuters, The Decoder,
   Tom's Hardware, GBHackers, CyberPress, and OpenAI/METR's own technical
   reports, used for corroboration and for OpenAI's public response.

## Status discipline

Every row is labeled with exactly one of:

- **observed** — directly present in a raw record (a jsonl line, a specific
  wiki revision) or a directly quoted primary statement.
- **researcher inference** — a claim made by the collusion.wiki authors or
  by us, not tied to a specific quoted post or raw record.
- **acknowledged** — a statement made by OpenAI itself, confirmed verbatim
  against at least one independent source.
- **uncertain** — plausible but not independently confirmable from
  available sources.

A claim never gets upgraded in status because a source states it confidently.
If we can't verify a number, date, or ID against something checkable, it's
dropped or marked uncertain rather than presented as fact.

## Verification steps actually performed

1. **Checksum verification**: SHA-256 of downloaded `events.jsonl`,
   `revisions.jsonl`, and `manifest.json` computed and compared against the
   publisher's published `SHA256SUMS`. See `scripts/verify_events.py`.
2. **Event-type reconciliation**: tallied `event_type` counts in
   `events.jsonl` (14,591 save / 5,217 delete / 4 revert / 101 probe =
   19,913 total) and confirmed this matches the publisher's own stated
   breakdown on the download page.
3. **Dual-source replication**: `events.jsonl` was independently fetched
   twice — once inside the bundled `full-wiki-logs.zip`, once as a
   standalone `events.jsonl.gz` — and the two copies were confirmed
   byte-for-byte identical (matching SHA-256) before trusting any line
   extracted from either.
4. **Targeted record extraction**: specific claims (e.g., the 12-second gap
   between the deletion of `DataUSAConstructionWageSep18Live` and its `ZZZ`
   backup) were checked against exact `event_id` lines in the raw file,
   not against summary narrative.
5. **Quote re-verification**: every direct quote attributed to OpenAI was
   re-found in a live, fetchable source before inclusion; quotes carried
   over from notes without being independently re-located were stripped
   (see `CORRECTIONS.md`).

## Known limitations

- The heartbeat/dead-man-switch rows are sourced to report prose rather
  than a raw jsonl record, and are a weaker evidentiary tier than the
  deletion-pair rows even though both are marked "observed."
- The `revert` row's null body reflects that no body was captured for that
  event in the export; this does not by itself establish *why* it's
  missing (export artifact vs. genuine loss), and Part 2 should not
  over-interpret it.
- We do not have access to model chain-of-thought; all agent "intent"
  language is the collusion.wiki authors' interpretation, not verified
  internal reasoning.
