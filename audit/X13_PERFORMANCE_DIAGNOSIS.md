# X13 performance diagnosis (outcome-blind)

Date: 2026-09-13 (Africa/Johannesburg)

Scope: collection-only profiling of frozen P15 phase 0. No benchmark loader,
annotation file, evaluator, evidence metric, PCD-vs-E result, or retained-evidence
coverage result was accessed.

## Preserved failed attempt

The supplied execution handoff records ordinal 1 (`L-primary`, `P15`, phase 0)
as `RUNNING` followed by `ExecutionTimeout` after 7,200 seconds, with no row
artifact, zero completed rows, and zero stable re-scores. The checked-in frozen
manifest remains byte-for-byte untouched at SHA-256
`0db63b0bc62fdf2c84fb1b3e01eb3b04715679a40c66e936b9175afdebcef62b`.
No real authorization artifact or real status log is present in this checkout,
so its identity was not guessed or recreated.

## Bounded pre-edit profile

The first six hours contain no discoverable title and therefore only established
the empty-feed baseline: 361 polls, 24 sweeps, zero GETs, 0.098 seconds, and
113,015 peak traced bytes. A representative five-day prefix includes the first
large mutation burst and produced 7,201 feed polls, 480 sweeps, 81,081 GETs,
81,081 successful capture attempts, and 79,639 FIFO evictions.

The five-day pre-edit run used `cProfile` plus `tracemalloc`: 154.869 seconds
wall time, 139.250 profiled CPU seconds, 134,726,566 peak traced bytes, 81,081
observer audit records, 81,081 response objects, 81,081 capture-attempt objects,
and 160,721 storage accounting points.

| Rank | Hot path | Cumulative seconds | Calls | Finding |
|---:|---|---:|---:|---|
| 1 | `CaptureStore.admit` | 70.584 | 81,081 | packet/hash work plus per-operation history |
| 2 | `Observer.get_body` | 67.490 | 81,081 | response/header/audit materialization |
| 3 | `Observer._observe_state` | 42.387 | 81,081 | repeated nominal reconstruction |
| 4 | `TraceModel/PageTimeline.state_at` | 38.842/37.731 | 81,081 | unchanged prefixes replayed |
| 5 | `Capture.packet_bytes` | 32.643 | 81,081 | packet JSON repeatedly reconstructed |
| 6 | `PageTimeline._nominal` | 21.874 | 81,081 | branch/provenance replay |
| 7 | canonical JSON | 39.418 | 170,709 | validation/encoding dominated headers/packets |
| 8 | FIFO eviction | 2.753 | 79,639 | not the principal bottleneck |

## Root cause

Ordinal 1 combines 6,387,883 body GETs with 74,881 feed polls and 4,992
sweeps. The implementation rebuilt nominal title history for unchanged reads,
re-encoded fixed response headers and immutable bodies, rebuilt each capture
packet more than once, and retained several Python objects per request. Storage
also appended accounting points for zero-duration eviction/admission changes at
a common sweep timestamp.

## Performance-only changes

- Nominal mutation-prefix lookup uses a binary-search interval index and exact
  immutable prefix cache. Observer outcomes are cached only by opaque title and
  nominal mutation-prefix index; same-time ambiguity is still resolved by the
  unchanged timeline engine.
- Canonical bodies and fixed outcome headers are content/source cached. Capture
  hashes, timestamps, quoted keys, and exact packet bytes avoid redundant work
  while preserving decimal `request_seq` width.
- The real X13 periodic runner explicitly selects compact mode. It invokes and
  accounts for every GET/admission but omits empty poll objects, response and
  capture-attempt history, observer/storage audits, and size history.
- Compact storage retains, per timestamp, maximum instantaneous S and final S.
  This preserves peak S, synchronized peak S+M, S byte-microseconds, and combined
  byte-microseconds while removing zero-duration ledger growth.
- Default/debug collection remains non-compact. PCD-R and E retain their current
  histories because their request counts are small relative to P/PD.

No benchmark, annotation, K, timeline rule, request schedule, GET outcome,
request sequence, storage rule, FIFO rule, dedup rule, byte rule, policy, phase,
interval, cap, archive rule, roster row, or evaluator rule was changed.

## Post-repair measurements

On the same five-day prefix under `tracemalloc`, compact mode took 21.199 seconds
and 3,255,239 peak traced bytes: a 7.31x runtime improvement and 41.39x peak
traced-memory reduction. It made the same 81,081 GETs. Nominal `state_at` work
fell from 81,081 calls to 616 exact interval cache misses (99.24% fewer); compact
retention held zero response/audit/capture-attempt objects and 684 accounting
points. Without allocation tracing it took 4.392 seconds.

The full ordinal-1 collection-only benchmark was bounded at approximately one
hour. It remained CPU-active and responsive at 612,515,840 bytes RSS, but had
not completed, so it was manually stopped without writing any row/result
artifact. Its post-repair runtime is conservatively `> 1 hour (censored)`, versus
the historical `> 2 hours / ExecutionTimeout`. This is not a completed X13 row
and no evaluator was imported.

## Equivalence and decision

`python audit/verify_performance_equivalence.py` reports exact PASS for P, PD,
PCD, PCD-R, and E on bounded real prefixes. Compared fields include every GET
and poll schedule, request/outcome/cost totals, retained packets/bodies/hashes,
request sequences, packet bytes, final/peak S, evicted bytes, oversize count,
feed M, synchronized S+M, and exact byte-microseconds. Synthetic fixtures cover
repeated/shared bodies, dedup/non-dedup, FIFO, oversize, non-ASCII, empty body,
same-time storage, and request sequence width 9 to 10. Existing tests cover
deletion/recreation, same-time mutation ambiguity, BU/unknown, and delays.

Exact equivalence passes, but roster-wide feasibility is insufficient. See
`X13_RUNTIME_SCOPE_EVIDENCE.md`.
