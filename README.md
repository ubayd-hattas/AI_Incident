# Evidence Before Erasure

**Track 2: Apart × CeSIA AI Incident Response Research Sprint**

How well do different automated evidence-collection policies preserve evidence from a live incident before it
disappears? This project benchmarks **periodic snapshot collection** against a **budget-matched event-derived
policy** using a real trace: AI agents coordinating and sharing answers via a dormant German wiki
("Collusion Wiki") during evaluations.

The core question: does a naive time-interval snapshotter lose materially more critical evidence than a policy that
reacts to change notifications under an equal request/storage budget?

## Status

This is a research pipeline under active development, built as a sequence of frozen, independently-audited stages.
**`docs/PROJECT_STATUS.md` is the single source of truth for current status.** Check it before assuming anything
below still holds. As of writing: data ingestion, the state-reconstruction engine, the shared observer/storage
substrate, all four collection policies (P / PD / PCD / bounded event-derived), and the evaluation benchmark are
implemented and independently audited.

**X13 (the full 791-row experiment sweep) was authorized and attempted, and failed before completing its first row**
(a 7,200-second execution timeout). A subsequent performance repair and a reduced 130-row runtime candidate were
independently audited and found not yet authorizable: two of the reduced candidate's rows (PCD-R and F) remain
either unproven-feasible or blocked outright. See `docs/PROJECT_STATUS.md` and
`audit/FINAL_PRE_X13_INDEPENDENT_READINESS.md` (sections 10-13) for the full history and exact reasons.

## Current results

There is no real coverage, cost, or policy-comparison result. The submitted report states this directly rather than
filling the gap with a placeholder number.

- [Final report](report/report.tex) (PDF: `report/report.pdf`, pending a fresh recompile): the actual submission,
  an honest incomplete-execution report with independently fact-checked citations to this repository.
- [SYNTHETIC, watermarked coverage-cost placeholder](figures/coverage_cost.svg): superseded illustrative figure, not a finding, excluded from the final report.
- [SYNTHETIC, watermarked Construction/ZZZ panel](figures/case_walkthrough.svg): superseded illustrative figure, not a finding, excluded from the final report.
- [Judge walkthrough](docs/JUDGE_WALKTHROUGH.md): the one worked, inspectable development example (Construction/ZZZ, `GRP-01-CONSTRUCT`).

## Limitations

- This is a single incident family; any future findings will not establish broad generalization.
- The benchmark is purposive and enriched, not a representative sample.
- The evaluation is a live-only, trace-grounded simulation under a shared hypothetical feed, not a measurement of actual historical HTTP visibility.
- It makes no claim of permanent evidence erasure.
- It makes no claim about actual agent intent, coordination, distinct agent identities, or external task success.
- It makes no claim of general event-driven collection superiority.

## How the project is organized

Every stage is specified in a frozen contract *before* it is implemented, implemented by one person, and then
independently re-derived and checked by someone who did not write the code, never by re-running the author's own
arithmetic. Findings, corrections, and disagreements are kept, not smoothed over.

| Path | What lives here |
|---|---|
| `docs/` | Frozen specs and contracts: data audit, execution spec, per-stage implementation contracts, the pre-results methodological audit, the run contract |
| `src/ebe/` | The implementation: ingestion/typed loader, the state-at-time engine, the observer/storage substrate, and the four collection policies |
| `audit/` | Independent verification scripts and their written findings for every stage: reproducible, re-runnable, and never editing a fixture to make code agree with it |
| `annotations/` | The human-labeled evaluation benchmark: evidence propositions, occurrence census, dev/held-out splits |
| `tests/` | Unit tests for the implementation |
| `sources/` | Provenance: pinned hashes, download recipe, novelty search log, rights/outreach notes |
| `data/` | Raw export (**not tracked in git**; see below) |

## Getting started

Requires Python 3.12+ and the standard library only. No third-party dependencies.

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

This fails loudly on any hash, row-count, or schema mismatch against the pinned values in `sources/registry.json`.
It never trusts a fresh download blindly.

**3. Run the tests:**

```powershell
python -m unittest discover -s tests -v
```

**4. Run an independent audit** (repeat for any file under `audit/`):

```powershell
python audit/verify_collectors_cross_policy.py
```

**5. Regenerate the judge-facing figures** after a hash-validated local export:

```powershell
py -3 -m unittest discover -s tests -v
py -3 scripts/generate_p14_assets.py
```

These commands require no network access and no model API key. Until authorized X13 CSVs exist, the generated figures are visibly watermarked SYNTHETIC placeholders.

## Where to look next

- **Current status, open gates, ticket tracker:** `docs/PROJECT_STATUS.md`
- **What's authorized to run and what isn't, right now:** `docs/PRE_RESULTS_AUDIT.md` §11 (gate register)
- **The frozen experiment design:** `docs/X13_RUN_CONTRACT.md`
- **Execution specification:** [docs/EXECUTION_SPEC_v0.1.md](docs/EXECUTION_SPEC_v0.1.md)
- **Current methodology, benchmark, and final engineering authority:** [docs/FINAL_PRE_X13_FREEZE.md](docs/FINAL_PRE_X13_FREEZE.md)
- **The evaluation benchmark:** `annotations/A11_BENCHMARK_SPEC.md`

## License

MIT. See `LICENSE`.
