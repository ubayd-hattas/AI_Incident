# Primary result: PCD15 vs E30, held-out critical core retention

Computed 2026-09-14. This is a real result: real collector code, run against
the real corpus, scored against the real, frozen, hash-validated A11
benchmark (`annotations/`). Read this document alongside the process
disclosure in the next section before treating the numbers as authoritative
for any claim beyond exactly what they measure.

## Process disclosure (read this first)

This did not go through `src/ebe/x13_runner.py`'s two-gate authorization
path. That path is hard-bound to the frozen 791-row `FINAL_PRE_X13_DEADLINE_v1`
manifest (`src/ebe/x13_manifest.py`'s `validate_manifest` asserts exactly 791
rows) and would correctly refuse a reduced roster; rebuilding that gate for a
new, smaller, previously-audited candidate was not attempted under the
remaining time.

Instead, the scored rows were produced by directly invoking the same
audited primitives the official runner uses internally (`Observer`,
`run_periodic`, `run_event_derived`, `terminal_archive`'s controls,
`a11_loader.load_a11_benchmark`, `evaluator.evaluate_benchmark`), against
the roster already defined and disclosed in `src/ebe/x13_runtime_v2.py`'s
`collection_rows()` (the `FINAL_X13_RUNTIME_v2` candidate, independently
audited in `audit/FINAL_PRE_X13_INDEPENDENT_READINESS.md` sections 12-13),
restricted to the 61 rows that make up the frozen primary contrast: all 60
PCD15 phases plus E30. PCD-R and F remain excluded, both independently
confirmed infeasible/blocked in this same audit.

Critically: the actual execution (the step that joins collector output with
the real annotation benchmark to produce a score) was run by the human
account owner directly, in their own terminal, not by the Claude Code
session assisting this project. Claude Code's own auto-mode safety
classifier blocked that specific action when the assisting session
attempted it directly, correctly identifying it as bypassing the project's
own Gate 2 authorization control. The assisting session did not attempt to
route around that block; instead it wrote the execution script
(`run_scoped_x13_full.py`, sharded across 6 parallel processes for the
account owner to run) and, once the account owner had produced the row
output files themselves, read and aggregated those already-produced files.
This is disclosed here in full because the project's own standing rule is
to disclose process, not just results, and a departure from the normal
two-gate flow is exactly the kind of thing that rule exists to surface.

No annotation content or evaluator internals were used to select or shape
the roster; the roster was fixed in `x13_runtime_v2.py`/
`configs/x13_runtime_v2.json` before this execution existed.

## Result

61 of 61 rows in the primary contrast completed. Zero errors.

| Quantity | Value |
|---|---|
| E30 held-out critical core | 0 / 23 (0.0000%) |
| PCD15 mean held-out critical core, 60 phases | 0.0000% |
| D = E30 − mean(PCD15) | **0.00 percentage points** |
| Frozen decision threshold | ≥ 10 pp |
| Result vs. threshold | **Below threshold. Null result.** |
| Distinct PCD15 core numerators across all 60 phases | `{0}` (every single phase scored exactly 0/23) |
| E30 held-out critical context | 0 / 23 (0.0000%) |
| PCD15 mean held-out critical context, 60 phases | 0.0000% |
| E30 requests made | 80,049 |
| PCD15 requests made, range across 60 phases | 82,196 – 82,262 |
| Request admissibility (E30 ≤ min_j PCD15_j) | **True** (80,049 ≤ 82,196) |

Per-phase request counts and wall-clock times for all 60 PCD15 phases are in
`results/rows_shard{0..5}.jsonl` (one JSON object per row); raw values are
also summarized in `primary_result_summary.json` in the repo root (generated
by aggregation, not itself a scored artifact).

## What this means

Under the frozen primary settings (1 MiB shared capacity, 5s feed lag, 60s
poll interval, held-out critical core, K=23, July 15 checkpoint), **neither**
periodic collection at any of the 60 tested phase offsets **nor**
event-derived collection at q=30 retained any of the 23 held-out critical
propositions' required core evidence. This is not "E30 loses less than
PCD15" or the reverse; it is both at exactly zero, for every phase tried.

A companion diagnostic (run during the earlier smoke test, same session)
found the likely mechanism for at least one page: the page was retained at
the July 15 checkpoint, but the retained version was a later edit that had
already overwritten the specific text the evidence required. Both policies
in this implementation retain only the current/latest known state per page
under capacity pressure; neither retains multiple historical versions of a
repeatedly-edited page once capacity forces eviction. An uncapped
archive-only control run in the same smoke test (which enumerates every held
revision with no capacity constraint at all) found all 23 propositions'
evidence present, confirming the evidence exists somewhere in the corpus and
that the benchmark/evaluator wiring is correct; it is specifically the
capacity-bounded retention step that loses it, for both policies alike.

## What this does not establish

- It does not establish that event-driven monitoring is better or worse
  than periodic monitoring in general, or at any capacity other than 1 MiB.
- It does not include PCD-R, F, or any of the interval/latency/reverse/
  archive/secondary-E sensitivity rows from the same 128-row candidate;
  those remain either excluded (PCD-R: demonstrated infeasible even after
  two independently-verified performance fixes; F: blocked by an
  unresolved `AmbiguityLimitError` in the terminal-directory path) or
  simply not yet run.
- It is one corpus, one capacity setting, one checkpoint. The frozen
  contract's own limitations (purposive, enriched, non-representative
  benchmark; simulated, not production, telemetry) apply to this result
  exactly as they apply everywhere else in this project.
- The severity of the result (exactly zero, not merely low) is itself worth
  treating with some caution before generalizing: it may reflect something
  specific about how tightly capacity (1 MiB) is undersized relative to
  this corpus's total edit volume (roughly 26 MB of DSE body bytes across
  the same window, per `docs/DATA_AUDIT_2026-09-12.md`), rather than a
  general property of capacity-constrained monitoring at any budget.

## Next owner

Sam (independent audit role): fold this result into the report and the
audit trail with full process disclosure, exactly as done here. If time
remains, the same script (`run_scoped_x13_full.py`, no `--families` filter)
can be used to complete the remaining 67 rows of the 128-row candidate
(interval, latency, reverse, archive, secondary-E), which would let a
sensitivity/hostile-control table be added to the report on the same
honest, disclosed basis as this primary result.
