# E09/E10 independent cross-policy neutrality and token-bucket audit

Role: independent validation (Sam). Read `docs/E09_PERIODIC_COLLECTORS.md`, `docs/E10_EVENT_DERIVED_COLLECTOR.md`,
`src/ebe/collectors.py`, `src/ebe/observer.py`, `src/ebe/storage.py`, `src/ebe/accounting.py`,
`audit/E08_NEUTRALITY_AUDIT.md`, `audit/smoke_periodic.py`, `audit/smoke_event_derived.py`. Did not implement or
modify P/PD/PCD/`E(q)`, did not implement or run semantic evidence scoring, and did not modify any frozen fixture or
contract text to make code agree with it. No prior E09-specific audit file existed before this one — this is the
first independent pass over `src/ebe/collectors.py` for either E09 or E10.

## Method

All checks are in `audit/verify_collectors_cross_policy.py`, reproducible via
`python audit/verify_collectors_cross_policy.py`. Three complementary techniques, matching the discipline used for
V02/V07/R04/E08:

1. **Adversarial execution against the real collectors** — small synthetic exports built directly as `schema.py`
   dataclasses (bypassing E05), driven through the real `PeriodicCollector`/`EventDerivedCollector` via
   `run_periodic`/`run_event_derived`, across nine named adversarial scenarios plus the sensor-access and accounting
   checks.
2. **An independent token-bucket simulator** (`independent_token_sim`), coded directly from
   `docs/E10_EVENT_DERIVED_COLLECTOR.md`'s arithmetic description, never importing or calling
   `EventDerivedCollector`'s own loop. It is run standalone at q=30/100/300 across six scenarios, then cross-validated
   against the real collector's dispatch behavior on a concrete burst export.
3. **Static structural review** of `src/ebe/collectors.py` — a regex over every `self.observer.<attr>` access in the
   file, checked against the allowed neutral Observer surface, to rule out policy-specific branching by source
   inspection rather than by trusting the by-eye read.

## Errors found and fixed during this audit (disclosed, not hidden)

All bugs found in this pass were in **my own test harness**, not in `src/ebe/collectors.py`:

1. An early "rapid overwrite" test asserted `E(q)` would only ever observe the final body in an A→B→C sequence. That
   assumption was wrong: `E(q)`'s 1-minute dispatch cadence is finer than the 60-minute periodic schedule used
   elsewhere in that scenario, so it can legitimately sample an intermediate state (B) that a slower periodic sweep
   never visits. That is a sampling-rate effect, not a leak. Fixed by adding a matched-cadence comparison (P and
   `E(30)` both run at 1-minute granularity) to isolate the real invariant: never observing an already-superseded
   body, regardless of schedule.
2. The "repeated unchanged content" test initially had P/PD's expected `retained_body_objects` backwards (asserted
   non-dedup P should share one object, when it should allocate one fresh object per capture). Fixed with the
   correct per-policy expectation and verified with a direct debug print before trusting the assertion.
3. `independent_token_sim` originally used `if` instead of `while` to dispatch at most one page per minute-tick,
   regardless of available token credit. This was a real design question, not an obvious typo: re-reading the
   contract text ("dispatch opportunities occur every minute" names tick granularity, not a per-tick dispatch cap)
   and noting the task's own "burst immediately at t0" scenario name settled it — a full bucket must be able to
   burst-drain multiple pages in one tick. Fixed the simulator to a `while credit >= HOUR` loop and updated four
   downstream consumers that assumed the old single-page-per-tick log format.
4. The body-unknown token-consumption test initially computed its expected final credit by hand and got it wrong
   (missing a trailing refill). Root cause: `independent_token_sim` stopped updating credit at the last dispatch
   tick and never advanced it to the checkpoint instant, but the contract's "final checkpoint feed poll occurs, but
   no new request is dispatched there" implies credit is a continuous function of time that keeps refilling up to
   the checkpoint even when nothing is spent there. Fixed by adding a trailing refill-only step from the last tick
   to the checkpoint, and switched the test's expected value from hand arithmetic to the (now-fixed) simulator's own
   output, since hand-deriving this exact arithmetic is exactly the kind of transcription risk this audit exists to
   catch.
5. A leftover line from before fix (3) counted dispatched pages as `1 if page is not None else 0` against the new
   `(minute, tuple_of_pages, credit)` log format, where every tuple is truthy-non-`None` — silently reporting 180
   dispatches instead of 40. Fixed to `sum(len(pages) for _, pages, _ in log)`.

## Sensor-access parity (Section 3)

`collectors.py` was grepped for every `self.observer.<attr>` access. The complete set found is `{config,
poll_feed, get_body, discovered_titles, costs}` — nothing else. P/PD/PCD share one `PeriodicCollector` class;
`EventDerivedCollector` is the only other caller of `Observer` in the file. This makes per-policy branching on
Observer access structurally absent, not merely untested, confirmed further by byte-identical feed-poll content and
identical `discovered_titles` across all four policies on the same export/config.

| Capability | P | PD | PCD | E(q) |
|---|---|---|---|---|
| Content-free feed (`poll_feed`) | Y | Y | Y | Y |
| `discovered_titles` | Y | Y | Y | Y |
| Response-time body GET (`get_body`) | Y | Y | Y | Y |
| Observer config | Y | Y | Y | Y |
| Observer `costs()` | Y | Y | Y | Y |
| Trace/revision/final-directory/annotation access | N | N | N | N |

**Classification: PASS.**

## Token-bucket independent verification (Section 2)

`independent_token_sim` (coded from the contract text, never importing `EventDerivedCollector`'s loop) was run at
q=30/100/300 across: burst-at-t0, sustained queue, idle-then-burst, fractional-refill boundary, and an equally-old
tie-break case. All confirm: capacity is never exceeded; a single minute-tick can burst-drain multiple tokens' worth
of dirty work (not throttled to one dispatch per tick); refill is exact integer microseconds with no rounding;
ties break on ascending `page_key`. Cross-validated against the real `EventDerivedCollector` on a concrete 40-page
burst at q=30: the real collector also burst-drains multiple pages within a single minute-tick, and the total
eventually-served count matches the independent simulator's prediction exactly. A body-unknown mutation is
confirmed dispatched (it is dirty and request-eligible even though it can never yield `BODY`) and charged exactly
one token, not refunded, with the real collector's `final_token_credit_numerator` matching the independent
simulator's prediction once the simulator's own trailing-refill-to-checkpoint bug (item 4 above) was fixed.

**Classification: PASS.**

## PCD vs E(q) fairness (Section 5)

The "repeated unchanged content" result (PCD issues exactly 1 GET over an extended horizon) was originally measured
at a coarse 60-minute PCD sweep interval, which would be a weak comparison if the efficiency were an artifact of
that choice. Re-run at a 1-minute PCD sweep interval — matched to `E(q)`'s own dispatch granularity — on the
identical single-unchanged-page scenario: PCD still issues exactly 1 GET, and `E(30)` also issues exactly 1 GET on
the same scenario. Neither mechanism has a structural request-count advantage over the other here.

The one-extremely-hot-page scenario (30 saves, one per minute) shows PCD@1-minute-sweep issuing 30 GETs versus
`E(q=1, slow bucket)` issuing 2 GETs. This is a genuine, contract-described design difference — PCD's coalescing
window is its sweep interval, `E(q)`'s coalescing window is whatever the token bucket can absorb — not an
implementation bug or an artificial handicap. Recorded as INFO, not PASS/FAIL, since neither contract requires the
two mechanisms to coalesce identically.

**Classification: PASS** (no artificial weakening found; the one behavioral asymmetry identified is a documented
design property of the frozen contracts, not a bug).

## Accounting parity across P/PD/PCD/E(q) (Section 4)

On a mixed-outcome export (BODY, save-then-delete producing MISSING, and a body-unknown mutation), for all four
policies: every dispatched body attempt lands in exactly one `outcome_counts` bucket summing to
`observer_costs.body_requests`; `captures_attempted <= body_requests`; `captures_admitted <= captures_attempted`;
`retained_body_objects <= retained_packets`. `feed_requests` and `final_shared_metadata_bytes` are identical across
all four policies given the same `Observer` config — confirming feed-polling cost is an Observer-config property,
never a collector-policy choice. P (non-dedup) shows `retained_body_objects == retained_packets` (no sharing); PD
(dedup) shows `retained_body_objects <= retained_packets`, strictly less whenever content repeats, confirming dedup
metadata is doing real work rather than being a no-op.

**Classification: PASS.**

## Nine adversarial scenarios (Section 6)

| Scenario | Result |
|---|---|
| Rapid overwrite (A→B→C) | **PASS** — no policy ever observes a superseded body; matched-cadence check confirms this is mechanism-neutral, not schedule-dependent |
| Save then delete | **PASS** — no policy ever records a `BODY` outcome for content deleted before any request could see it |
| Repeated unchanged content | **PASS** — P/PD re-request every sweep as designed; PCD requests once and stops; P/PD retain equal packet counts, differing only in body-object sharing |
| Many hot pages | **PASS** — 50 simultaneously-dirty pages under q=30 are not all served in the first minute; `token_starved_dispatch_opportunities` correctly registers demand exceeding supply |
| One extremely hot page | **PASS** — 30 rapid saves coalesce into far fewer GET dispatches under a slow bucket; `coalesced_updates` reflects this |
| Many new titles | **PASS** — 200 simultaneously-discovered titles are all eventually served without exceeding the q/hour rate; discovery itself is feed-driven and budget-independent |
| Simultaneous mutations (mixed same-time save+delete) | **PASS** — remains request-eligible under both P and `E(q)`, never silently treated as confirmed-deleted |
| Body-unknown mutation | **PASS** — never produces a `BODY` outcome under any of the four policies |
| Capacity pressure | **PASS** — a tight 500-byte cap is respected by `final_store_bytes` under all four policies |

## Smoke-script review (Section 8, engineering check only)

`audit/smoke_periodic.py` and `audit/smoke_event_derived.py` were executed against the pinned 24-hour export prefix.
Both ran to completion with no errors and produced well-formed JSON. Per the contracts' own non-claims sections and
per this audit's explicit brief, their operational counts (GET counts, capture counts, byte totals) are reviewed
here **only** as a structural-plausibility / "does it run" check. No evidence-coverage, comparative-effectiveness,
or "which policy is better" inference was drawn from these numbers, and none should be — that comparison requires
E12/X13 semantic evidence scoring, which is explicitly out of scope for this audit and was not implemented or run.

**Classification: PASS** (execution-only check; not an evidence-quality signal).

## Request-budget comparability (Section 7)

`CollectorResult` exposes `observer_costs` (separating feed/directory/body request counts), `storage_snapshot`
(peak/final bytes and byte-hours separately), `requests_made`, `captures_attempted`, `captures_admitted`, and
`outcome_counts` — everything named in the task as needed to judge cost admissibility later, with evidence-coverage
scoring correctly absent (deferred to E12/X13, not an omission here).

**Classification: PASS.**

## Findings summary

| # | Finding | Classification |
|---|---|---|
| 1 | Sensor-access parity across P/PD/PCD/E(q) | PASS |
| 2 | Token-bucket arithmetic (capacity, refill, burst-drain, no-refund) | PASS |
| 3 | PCD vs E(q) fairness (no artificial weakening) | PASS |
| 4 | Coalescing-window asymmetry between PCD and E(q) on the one-hot-page scenario | NONBLOCKING — documented design difference, not a bug |
| 5 | Accounting parity (feed cost, outcome bookkeeping, dedup metadata) | PASS |
| 6 | Nine adversarial scenarios | PASS (all nine) |
| 7 | Smoke scripts execute cleanly on the pinned export | PASS (engineering check only) |
| 8 | Request-budget comparability fields present on `CollectorResult` | PASS |
| 9 | Bugs found in `src/ebe/collectors.py` itself | **None** |

No **BUG**, **CONTRACT_AMBIGUITY**, or **BLOCKER_BEFORE_E10** findings resulted from this pass.

## Gate: **PASS**

## Completion report

1. **E09 status:** PASS. Sensor-access parity, feed-cost parity, dirty-tracking/eligibility rules, FIFO/dedup
   accounting, and all nine adversarial scenarios confirmed for P/PD/PCD with zero bugs found in the implementation.
2. **E10 status:** PASS. Token-bucket arithmetic independently re-derived and cross-validated against the real
   `EventDerivedCollector` at q=30/100/300; burst-drain, no-refund-on-failure, and coalescing behavior all match the
   frozen contract with zero bugs found in the implementation.
3. **Sensor-access parity:** Confirmed structurally (regex over every `self.observer.<attr>` access in
   `collectors.py`) and empirically (byte-identical feed content, identical `discovered_titles`) across all four
   policies.
4. **Accounting parity:** Confirmed — feed-request counts and shared metadata bytes are identical across all four
   policies given the same Observer config; outcome/capture/admission bookkeeping is internally consistent for
   every policy under a mixed-outcome scenario.
5. **Token-bucket verification:** Confirmed independently at q=30/100/300, including burst-at-t0, sustained queue,
   idle-then-burst, fractional-refill boundary, tie-break ordering, and token consumption on a non-BODY
   (body-unknown) outcome — all match an independently-coded simulator, cross-validated against the real collector.
6. **PCD fairness assessment:** PCD is not artificially weakened relative to `E(q)`. At matched (1-minute) schedule
   granularity, PCD and `E(30)` issue identical request counts on the repeated-unchanged-content scenario. The one
   asymmetry found (coalescing window differs between the two mechanisms on a very-hot single page) is a documented
   design property of the frozen E09/E10 contracts, not an implementation bug.
7. **Policy-specific advantages found:** None beyond the contract-specified design differences (P's no-dedup, PD's
   dedup, PCD's dirty-only servicing, E(q)'s token-budget-bounded dispatch) — all four remain sensor-access-neutral
   and accounting-neutral.
8. **Bugs found:** Zero in `src/ebe/collectors.py`. Five bugs were found and fixed in my own test harness during
   this pass (listed above under "Errors found and fixed") — disclosed per the same discipline used in the V07,
   R04, and E08 audits.
9. **Is a fix required before proceeding?** No.
10. **May Jaswin begin the pre-results Astra audit?** Yes — nothing found here should block or change it.
11. **Do E12/X13 remain blocked?** Yes, unchanged — this audit explicitly did not implement or run semantic evidence
    scoring, and E12/X13 remain scoped to future work, not touched or unblocked by this pass.
