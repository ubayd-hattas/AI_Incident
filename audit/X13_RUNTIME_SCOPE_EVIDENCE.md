# X13 runtime scope evidence (outcome-blind)

This document contains runtime/request facts only. It contains no benchmark
coverage, evidence retention, policy winner, or PCD-vs-E result.

## Exact schedule arithmetic

The full horizon has 74,881 frozen feed polls. Ordinal-1 P15 phase 0 adds
6,387,883 body GETs, for 6,462,764 total modeled attempts. Across phase variants,
each P/PD row has 6,462,476 to 6,462,865 total attempts.

| Frozen family | Rows | Total attempts per row | Aggregate attempts |
|---|---:|---:|---:|
| L-primary P15 | 60 | 6,462,476–6,462,865 | 387,759,664 |
| L-primary PD15 | 60 | 6,462,476–6,462,865 | 387,759,664 |
| O reverse P15 | 60 | 6,462,476–6,462,865 | 387,759,664 |
| O reverse PD15 | 60 | 6,462,476–6,462,865 | 387,759,664 |
| L-primary/O/A-live PCD15 | 180 | 82,196–82,262 before archive | 14,802,756 before archive |
| L-interval PCD5 | 60 | 83,621–83,648 | 5,017,956 |
| L-interval PCD60 | 60 | 80,635–80,737 | 4,841,146 |
| L-latency PCD15 | 180 | 82,195–82,262 | 14,802,756 |
| E(q), all listed q/lag/order rows | 8 | 80,047–84,074 | under 0.7 million total |
| A-only | 2 | 13,404 | 26,808 |

The four P/PD families alone require 1,551,038,656 attempts. A-live rows add one
archive enumeration and 13,403 archive body attempts per row. PCD-R request
counts are outcome/storage-dependent because repair requests depend on retained
known bodies; they were not inferred by the schedule-only census.

The F control was collection-only attempted and reached the frozen
`AmbiguityLimitError` while constructing terminal nominal directory membership,
before evidence evaluation. It therefore has no measured completed request
count in this diagnosis.

## Measured work and throughput

- Pre-repair five-day P15: 81,081 GETs in 154.869 seconds with profiling and
  allocation tracing; 523 GET/s including instrumentation.
- Post-repair five-day P15: the same 81,081 GETs in 21.199 seconds under the same
  allocation tracer (3,825 GET/s), or 4.392 seconds without tracing (18,461
  GET/s).
- Post-repair full ordinal 1: still incomplete at the bounded one-hour stop,
  with 612,515,840 bytes observed RSS and no row artifact.

The early-prefix rate is not representative of the late trace: title population,
mutation churn, canonical bodies, and FIFO work grow sharply after day five.
The full-row censored measurement is the conservative planning datum.

## Feasibility classification

Computationally dominant/prohibitive blocks are the 240 P/PD phase/order rows:
even a one-hour lower bound per representative row implies more than ten serial
days for those rows alone, before the remaining 551 rows, evaluator work, or
stable re-scores. F also has a separate terminal ambiguity-limit blocker.

The primary/essential low-request work that is computationally feasible consists
of PCD, E, A-only, and archive augmentation request volumes; their rows are two
orders of magnitude smaller than P/PD. PCD-R requires separate measured repair
counts but does not justify altering its frozen semantics here.

No scope cut is proposed in this document. The runtime-only evidence supports:

## PERFORMANCE REPAIR INSUFFICIENT

**EXACT NEXT OWNER: Jaswin/Astra — outcome-blind runtime-only X13 scope amendment.**
