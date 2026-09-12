# Evidence Before Erasure

**Track 2 — Apart × CeSIA AI Incident Response Research Sprint**

How well do different automated evidence-collection policies preserve evidence from a live incident before it
disappears? This project benchmarks **periodic snapshot collection** against a **budget-matched event-derived
policy** using a real trace: AI agents coordinating and sharing answers via a dormant German wiki
("Collusion Wiki") during evaluations.

The core question: does a naive time-interval snapshotter lose materially more critical evidence than a policy that
reacts to change notifications under an equal request/storage budget?

## Status

This is a research pipeline under active development, built as a sequence of frozen, independently-audited stages.
**`docs/PROJECT_STATUS.md` is the single source of truth for current status** — check it before assuming anything
below still holds. As of writing: data ingestion, the state-reconstruction engine, the shared observer/storage
substrate, all four collection policies (P / PD / PCD / bounded event-derived), and the evaluation benchmark are
implemented and independently audited. The semantic evidence-coverage evaluator and the full experiment sweep have
not been run yet.

## How the project is organized

Every stage is specified in a frozen contract *before* it is implemented, implemented by one person, and then
independently re-derived and checked by someone who did not write the code — never by re-running the author's own
arithmetic. Findings, corrections, and disagreements are kept, not smoothed over.

| Path | What lives here |
|---|---|
| `docs/` | Frozen specs and contracts — data audit, execution spec, per-stage implementation contracts, the pre-results methodological audit, the run contract |
| `src/ebe/` | The implementation: ingestion/typed loader, the state-at-time engine, the observer/storage substrate, and the four collection policies |
| `audit/` | Independent verification scripts and their written findings for every stage — reproducible, re-runnable, and never editing a fixture to make code agree with it |
| `annotations/` | The human-labeled evaluation benchmark: evidence propositions, occurrence census, dev/held-out splits |
| `tests/` | Unit tests for the implementation |
| `sources/` | Provenance: pinned hashes, download recipe, novelty search log, rights/outreach notes |
| `data/` | Raw export — **not tracked in git**; see below |

## Getting started

Requires Python 3.12+ and the standard library only — no third-party dependencies.

**1. Fetch the raw data** (not redistributed; downloaded fresh per the pinned recipe in `sources/registry.json`):

```powershell
New-Item -ItemType Directory -Path data/raw -ErrorAction Stop
Invoke-WebRequest -Uri 'https://collusion.wiki/explorer/download/full-wiki-logs.zip' -OutFile 'data/raw/full-wiki-logs.zip'
New-Item -ItemType Directory -Path data/raw/export -ErrorAction Stop
Expand-Archive -LiteralPath data/raw/full-wiki-logs.zip -DestinationPath data/raw/export
```

**2. Validate the download and rebuild the inventory:**

```powershell
python src/ebe/ingest.py data/raw/export --inventory sources/schema_inventory.json --notes sources/E01_ANOMALIES.md
```

This fails loudly on any hash, row-count, or schema mismatch against the pinned values in `sources/registry.json` —
it never trusts a fresh download blindly.

**3. Run the tests:**

```powershell
python -m unittest discover -s tests -v
```

**4. Run an independent audit** (repeat for any file under `audit/`):

```powershell
python audit/verify_collectors_cross_policy.py
```

## Where to look next

- **Current status, open gates, ticket tracker:** `docs/PROJECT_STATUS.md`
- **What's authorized to run and what isn't, right now:** `docs/PRE_RESULTS_AUDIT.md` §11 (gate register)
- **The frozen experiment design:** `docs/X13_RUN_CONTRACT.md`
- **The evaluation benchmark:** `annotations/A11_BENCHMARK_SPEC.md`

## License

MIT — see `LICENSE`.
