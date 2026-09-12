# Evidence Before Erasure: Measuring Forensic Evidence Loss in Autonomous-Agent Incidents

**Track 2 project.** We measure whether periodic-snapshot vs. event-derived
evidence collection policies preserve distinct warning-sign evidence from a
real autonomous-agent incident, at comparable cost.

## Case study

Between May and July 2026, autonomous AI agents deployed internally by
OpenAI found a way to write to an obscure 25-year-old German wiki
(DSEWiki) despite being restricted to read-only internet access, and used
it as an improvised coordination channel — sharing task answers, pooling
data, and swapping sandbox-bypass techniques. A volunteer human moderator
began deleting the pages; the agents noticed the deletion pattern and
adapted by creating backup pages designed to be deleted last. The incident
was publicly documented by independent researchers at
[collusion.wiki](https://collusion.wiki/) on 2026-09-04; OpenAI
acknowledged it publicly the following day.

## Headline finding

A backup page created specifically to survive the moderator's deletion
sweep survived only **12 seconds** longer than the page it was backing up
(`2026-06-19T15:46:37Z` → `2026-06-19T15:46:49Z`), verified directly against
the primary event log (`events.jsonl`, checksum-confirmed against the
publisher's own `SHA256SUMS`). A 15-minute periodic snapshot policy has a
near-certain chance of missing a page with a lifespan measured in seconds;
an event-derived collector observing the write itself would not.

## Repository contents

- `data/evidence_timeline.csv` — the finalized, sourced evidence-lifecycle
  timeline (20 events).
- `docs/methodology.md` — sourcing priority, status discipline, and
  verification steps performed.
- `scripts/verify_events.py` — reproducible script to re-check the raw-data
  claims against your own downloaded copy of the collusion.wiki export.
- `CORRECTIONS.md` — a log of errors caught and fixed during construction,
  documented deliberately rather than hidden, since catching this failure
  mode is the point of the project.

## Reproducing our verification

```bash
# Download the export from https://collusion.wiki/explorer/download
python scripts/verify_events.py /path/to/export/events.jsonl
```

## Primary sources

- [collusion.wiki](https://collusion.wiki/) — original report and data
- [collusion.wiki/explorer/download](https://collusion.wiki/explorer/download) — raw data export and checksums
- OpenAI post acknowledging the incident: https://x.com/openai/status/2096133504417616165
