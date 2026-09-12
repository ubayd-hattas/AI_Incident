# E09 frozen periodic collectors

## Scope and dependency boundary

E09 implements only the frozen periodic family `PΔ`, `PDΔ`, and `PCDΔ` in
`src/ebe/collectors.py`. A collector receives an already-created E08 `Observer` and
uses only `poll_feed()`, `discovered_titles`, `get_body()`, `config`, and `costs()`.
It does not receive the export or a `TraceModel` and cannot inspect revisions, future
records, final page lists, page families, relations, annotations, evidence units, or
criticality.

The neutral entry point is:

```python
result = run_periodic(
    observer,
    PeriodicConfig(
        PeriodicPolicy.PD,
        interval_us=15 * 60_000_000,
        phase_us=0,
        capacity_bytes=1024 * 1024,
    ),
)
```

`PeriodicCollector(observer, config).run()` is the equivalent object API.
`capacity_bytes=None` selects the frozen uncapped diagnostic. The optional checkpoint
supports deterministic prefix tests and the already-defined report checkpoint; the
default is T.

## Global schedule and feed order

Sweep times are `t0 + phase + kΔ`, calculated with integer microseconds and restricted
to `[t0, checkpoint)`. The phase must be in `[0, Δ)`. This is one global schedule: a
title discovered at 00:07 under a zero-phase 15-minute schedule is first eligible at
00:15, not 00:22. Discovery never starts or resets a title-relative clock.

Every policy polls the E08 common feed on its independently frozen 60-second epoch.
Polls include the final checkpoint so the shared feed log is retained and charged
through that point, but no ordinary sweep occurs at the final checkpoint. When a poll
and sweep coincide, the feed batch is delivered and policy knowledge is updated before
reads are scheduled.

Feed records alone determine operational belief. `live_change` makes a title believed
live and changed; `delete` makes it believed deleted and removes pending changed-only
work. Multiple records for the same title and selected time are treated as one group.
If that group contains both actions, the knowledge is mixed: feed serialization order
is not promoted into chronology, and the title remains request-eligible rather than
being silently treated as confirmed deleted.

Eligible titles at a sweep are ordered by visible opaque title key. E08 assigns the
body-attempt sequence in that order. Completed bodies are supplied to E08 storage in
`(response_time, request_seq, page_key)` order. GET responses carry current modeled
state at response time, not a trigger revision.

## Policy behavior

### PΔ

At every sweep, P requests every discovered title currently believed live or mixed.
Every known-body response becomes a capture attempt. Its `CaptureStore` is configured
with `deduplicate=False`, so every admitted capture has a fresh body object even when
its bytes equal an earlier body. Repeated GETs and repeated bodies are intentional.

### PDΔ

PD uses exactly the same feed processing, eligibility rule, sweep times, title order,
and GET path as P. Its only intended difference is `CaptureStore(deduplicate=True)`,
which globally shares exact byte-equal canonical body objects while retaining a packet
for every capture. Storage capacity never changes its request schedule.

### PCDΔ

PCD uses the same feed polls and exact-deduplicated store as PD. A visible live change
marks a title dirty. At a sweep, PCD requests only dirty titles then clears those it
attempted; repeated visible mutations before that sweep therefore coalesce into one
GET. A confirmed delete clears pending work and produces no historical-body request.
A later live change marks the title dirty again. GET outcomes and body equality never
drive dirty status.

PCD is required because it is the strong periodic control: it prevents a later
event-derived policy from appearing superior merely because a naive periodic baseline
repeatedly requests unchanged pages.

## Output and accounting

`CollectorResult` exposes the configuration, feed poll results, sweep times, body
responses/pending requests, capture/admission results, retained captures, final E08
storage snapshot, E08 observer costs, discovered-title state, and peak discovered/dirty
counts. Convenience properties report total modeled requests, capture attempts,
admissions, outcome counts, and the deterministic body-request schedule.

E09 never calculates body, packet, feed, eviction, or byte-hour costs itself. Known
bodies are wrapped in E08 `Capture` objects and passed to `CaptureStore`; failed,
unknown, ambiguous, unsupported, and horizon-pending outcomes remain explicit and are
not admitted. A cap may cause E08 FIFO eviction or oversize rejection, but cannot alter
collection decisions.

## Determinism and deliberate exclusions

The same observer configuration, trace, policy, interval, phase, cap, and checkpoint
produce the same poll stream, sweep stream, request order, outcomes, captures, and
storage state. Sets are never iterated to choose request order; visible keys are sorted.

E09 deliberately does not implement F, `E(q)`, token buckets, event-derived dispatch,
semantic/evidence scoring, criticality, annotation access, archive behavior, experiment
sweeps, result selection, plots, E12 evaluation, or X13 experiments.

`python audit/smoke_periodic.py` is the fixed integration smoke: it runs all three
policies against the first 24 hours of the pinned DSE export with Δ=60 minutes, phase
zero, and a 32 MiB cap. The bounded prefix keeps this an execution check rather than an
experimental sweep; its JSON output contains operational counts only.
