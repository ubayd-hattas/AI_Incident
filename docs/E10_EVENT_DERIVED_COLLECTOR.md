# E10 bounded event-derived collector

## Scope and interface

E10 implements only bounded event-derived collection `E(q)` in
`src/ebe/collectors.py`. Its public entry points are
`EventDerivedCollector(observer, config).run()` and `run_event_derived(observer,
config)`. `EventDerivedConfig.q` is a positive integer number of body attempts per
hour; `capacity_bytes=None` retains the frozen uncapped diagnostic behavior.

The collector receives an existing E08 `Observer`, exactly as E09 does. It uses only
the content-free feed, discovered opaque title keys, response-time body GETs, observer
configuration, and observer costs. It has no trace, revision, final-directory,
annotation, evidence, criticality, page-family, semantic-duplicate, relation, or
future-mutation input. Event-derived collection therefore requires access to the same
modeled change feed and represents an infrastructure capability, not a free external
observer.

## Dirty work and deletion

A delivered visible live change creates one dirty item keyed by page. Its priority is
the earliest still-pending visible event time. Further live changes coalesce into that
item and do not replace its timestamp or create more requests. Queue selection is
strictly `(oldest pending event_time, visible page_key)`; body content and all semantic
attributes are absent from the ordering.

A delivered confirmed deletion removes un-dispatched dirty work. It does not cause a
GET and cannot retrieve the prior body. A later live change creates new work. A
same-page, same-event-time group containing both live and delete notifications remains
mixed and request-eligible, matching E09: feed serialization is not treated as source
chronology.

GETs read E06 state at response time through E08. They never read the revision that
triggered the queue item. Thus coalesced overwrites can only yield the current body,
and deletion before a delayed response yields the shared missing outcome. Unknown,
body-unknown, ambiguous, unsupported, missing, and horizon-pending outcomes remain
explicit and are never admitted as content.

## Exact token bucket and schedule

The bucket has capacity `q` tokens and starts with `q` tokens. It refills continuously
at `q` tokens/hour. Dispatch opportunities occur every minute on the common `t0`
epoch, in `[t0, checkpoint)`. At a common instant, the feed poll and queue update occur
before dispatch. The final checkpoint feed poll occurs, but no new request is
dispatched there.

Arithmetic is exact: credit is stored as an integer numerator over
`3,600,000,000` microseconds per hour. Capacity is
`q * 3,600,000,000`, elapsed refill adds `q * elapsed_microseconds`, and every body
attempt subtracts `3,600,000,000`. Every dispatched attempt consumes one token,
including missing, unknown, body-unknown, ambiguous, unsupported, or a response pending
past T. There are no retries. If fewer than one token remains, work stays queued for a
later minute; no future work is pulled backward.

## Storage and accounting equality

Every known-body response is wrapped in the same E08 `Capture` and admitted through
`CaptureStore(deduplicate=True)`, the identical exact-deduplicated mode used by PD/PCD.
E10 does not calculate serialization, hashes, packet sizes, FIFO eviction, refcounts,
caps, oversize rejection, byte-hours, downloads, or request costs. E08
`CaptureStore`, `Observer`, and frozen accounting functions remain authoritative.

`CollectorResult` is shared with E09. E10 adds neutral `EventDerivedStats`: minute
dispatch times, maximum queue depth, coalesced-update count, token-starved dispatch
opportunities, ordered pending dirty work at the horizon, and final exact token credit.
Pending dirty pages at the checkpoint remain visible and unserved.

## Audit smoke and non-claims

`python audit/smoke_event_derived.py` is preregistered at `q=30`, the first 24-hour
prefix, and a 1 MiB cap. It reports operational counts only. E10 makes no evidence
coverage, semantic priority, comparative effectiveness, experiment, parameter-tuning,
archive, or historical public-interface claim. It does not implement E12, X13, plots,
or results.
