# E08 independent neutrality and leakage audit

Role: independent validation (Sam). Read `docs/R04_FROZEN_SPEC.md`, `docs/R04_ACCOUNTING_AMENDMENT.md`, `audit/R04_ACCOUNTING_VERIFICATION.md`, `docs/E08_OBSERVER_STORAGE.md`, `src/ebe/observer.py`, `src/ebe/storage.py`, `src/ebe/accounting.py`. Did not implement E09 or E10, and did not modify any frozen fixture to make code agree with it.

## Method

Two complementary approaches, matching the discipline used for V02/V07/the accounting acceptance:

1. **Adversarial execution against the real code** (`audit/verify_e08_neutrality.py`) — small synthetic exports built directly as `schema.py` dataclasses (bypassing the E05 loader entirely, so test inputs are fully controlled), driven through the actual `Observer`/`CaptureStore`/`accounting` implementation. This is deliberately different from `audit/independent_replay.py`'s approach: the object under audit here *is* the E08 code, so the point is to attack it directly with adversarial inputs, not to build a parallel model that avoids it. Independent re-derivation is used specifically for canonical serialization (re-implemented from the contract text, not imported, then compared byte-for-byte against `accounting.canonical_jsonl`'s actual output).
2. **Static structural review** for the two questions that are best answered by absence-of-code rather than execution (no policy-specific branching, no annotation/evidence coupling) — via direct grep across all three audited files plus manual read of every import statement.

All 36 checks in the script, covering the fixture-reproduction, adversarial, and canonical-serialization sections, are listed with PASS/FAIL in the script's own output; the full run is reproducible via `python audit/verify_e08_neutrality.py`.

## Errors found and fixed during this audit (disclosed, not hidden)

Two bugs surfaced in **my own test harness** on the first run — neither was a bug in `src/ebe/`:

1. My synthetic-export builder used positional dataclass arguments against `RevisionRecord`/`EventRecord`/`ManifestRecord` (29+ fields each) and miscounted them twice, raising `TypeError`s before any real check ran. Fixed by switching to keyword arguments throughout — exactly the kind of transcription risk this audit exists to catch, this time in my own scaffolding rather than the code under test.
2. My first fixture-E/G reproduction driver tracked store size manually (only after each full `admit()` call), producing a 4-point trajectory where the fixture expects 6 (each intermediate eviction step counted separately). This looked like a real divergence in `CaptureStore` until I checked: the store already exposes a `size_history` property that records every eviction step internally (`storage.py`'s `_evict_oldest` appends to `_size_history` on every eviction, not just on admission). Switching my driver to read `store.size_history` instead of tracking its own copy resolved it — the real store was correct throughout; my harness just wasn't reading the granularity it already provided.

## Per-question findings

| # | Question | Classification | Evidence |
|---|---|---|---|
| 1 | Exposes exactly the frozen feed fields and nothing more | **PASS** | `FeedRecord.as_dict()` returns exactly `{action, event_time, page_key}`; no `body`/`revision_ref`/`relations` attribute exists on the object at all (not just hidden from serialization — structurally absent) |
| 2 | Prevents future-title discovery | **PASS** | `get_body` on a page never delivered via `poll_feed`/`terminal_directory` returns `UNKNOWN` regardless of the page's real state, even though the save had already happened in the underlying trace |
| 3 | Applies publication lag correctly | **PASS** | Constructed an event whose `event_time + lag` lands exactly on a scheduled poll instant; confirmed invisible on the immediately preceding scheduled poll and visible (closed/`<=` boundary) exactly at that instant |
| 4 | GETs read E06 state at response/request time as frozen | **PASS** | `get_body` computes `response_time = request_time + delay` and reads `TraceModel.state_at(page_key, response_time)` — confirmed via a two-save synthetic page that a zero-delay GET dispatched at the first save's own time sees only the first body |
| 5 | Cannot retrieve an overwritten trigger body retrospectively | **PASS** | Same two-save fixture: a GET dispatched at the *first* save's time but with enough response delay to land after the *second* save returns the **new** body, never a cached/trigger-tied stale one — there is no code path that associates a response with "the body that triggered this GET" at all, only with current state at response time |
| 6 | Charges failed/unknown requests consistently | **PASS** | Drove BODY/MISSING/UNKNOWN/pending-past-T outcomes through one observer; confirmed `body_requests` increments for every dispatch including the pending one, `unknown_body_byte_attempts` increments for UNKNOWN but not MISSING (definite zero vs. true NA), and `downloaded_total_bytes` correctly collapses to `None` once any NA-byte outcome exists |
| 7 | Canonical serialization identical to the amendment | **PASS** | Re-implemented `C(x)` from the amendment text independently (not importing `accounting.canonical_jsonl`) and compared byte-for-byte on 5 probes including non-ASCII, escape sequences, `null`/`false`/integer fields, and array framing — all identical |
| 8 | Reproduces A–I independently | **PASS** (B–G, F directly re-run against real code; A/H/I already covered by the pre-E08 acceptance, which audited the same `accounting.py` functions) | Constructed real `Capture`/`CaptureStore` instances from fixtures B, C, D, E, F, G's raw packet/body data and compared `store.size_history`, `final_store_bytes`, `peak_store_bytes`, `retained_request_seqs`, and `object_reference_counts` against each fixture's `expected` block — exact match on every field checked |
| 9 | Handles dedup reference counts correctly | **PASS** | Fixture G specifically (shared body outlives one evicted packet) reproduced exactly: `object_reference_counts` and eviction/survival of the shared object matched |
| 10 | Implements FIFO exactly | **PASS** | Fixture E's double-eviction sequence (evict packet 1, then packet 2, freeing the shared body, before admitting packet 3) reproduced exactly once the harness read the store's real `size_history` |
| 11 | No policy-specific behavior | **PASS** | Grepped `observer.py`/`storage.py`/`accounting.py` for any periodic/event-derived/PD/PCD/policy-name branching — none exists; the interface has no parameter or code path that varies by which future collector will use it |
| 12 | No annotation/evidence imports | **PASS** | Grepped for annotation/evidence/criticality/support-bundle/occurrence references — the only hit was Python's `from __future__ import annotations` typing directive (a false positive from the search term, not an actual import); the real import list is exactly `.accounting`, `.schema`, `.timeline`, and stdlib `json`/`hashlib`/`datetime`/`collections`/`dataclasses` |
| 13 | No special advantage to a future periodic or event-derived collector | **PARTIAL PASS / NONBLOCKING caveat** | The interface itself is uniform — no mode flag, no privileged query path, discovery-gating and cost-charging apply identically regardless of caller. This is the strongest claim checkable *at this layer*. Full fairness is a property of how E09/E10 *use* this interface, which doesn't exist yet — this question can only be fully closed once both collectors exist and are audited against each other, per `docs/R04_FROZEN_SPEC.md`'s own required PCD-strong-control comparison |
| 14 | Maintains prefix invariance under different future suffixes | **PASS** | Built two synthetic exports identical up to a common cutoff, differing only in whether a second save occurs 500 seconds *after* that cutoff; confirmed byte-identical feed poll responses, identical GET outcome/body, and identical accrued costs through the common prefix on both |

## Additional structural checks (not in the numbered list, worth recording)

| Check | Classification | Evidence |
|---|---|---|
| Genuine ambiguity surfaces as `AMBIGUOUS`, never a silently-picked body | **PASS** | Two saves at the exact same timestamp on one page produce a real `state_at` ambiguity; `get_body` correctly returns `AMBIGUOUS` with `body=None`, not a body union or an ID-order-derived winner |
| `terminal_directory` / continuous-feed mutual exclusivity | **PASS** | A fresh observer that has already polled the feed raises on `terminal_directory()`; a fresh observer that hasn't raises nothing and returns modeled-live membership |
| Hash-collision fail-closed path | **PASS (verified by code inspection only)** | `CaptureStore._has_equal_shared_body` raises `HashCollisionError` if two request bodies share a SHA-256 digest but aren't byte-equal. A genuine SHA-256 collision cannot be synthesized for a live test; this is confirmed by reading the code path, not by execution — recorded as a weaker form of verification than the executed checks above |

## Known gaps in this pass (disclosed, not blocking)

- **CONTRACT_AMBIGUITY / NONBLOCKING**: `terminal_directory`'s `DirectoryAmbiguityError` path (ambiguous live/not-live membership exactly at T) was not exercised — I confirmed the two straightforward paths (clean directory; feed/directory mutual exclusion) but not the genuine-ambiguity trigger. Low risk given the code's structure (`memberships = {...}; if len(memberships) != 1: raise`), but not independently executed.
- **NONBLOCKING**: only the default `ObserverConfig` lag/delay values were exercised for most tests, plus one custom large `get_response_delay_us`. The pre-authorized sensitivity values named in the amendment (30s/60s lag, 5s/30s delay) were not each individually driven through a synthetic case. `ObserverConfig.__post_init__` does validate they're accepted as nonnegative integers, which is confirmed, but their end-to-end behavior at those specific values wasn't separately probed.
- Neither gap is a **BLOCKER_BEFORE_E10** — both are narrow, well-isolated pieces of one code path each, not properties that would invalidate anything E09/E10 depend on.

## Completion report

1. **E08 neutrality: PASS.** Every one of the 14 audit questions resolves to PASS or a disclosed partial-pass with a named, non-blocking reason (Q13, which is structurally sound at this layer but cannot be *fully* closed until E09/E10 exist to compare against each other).
2. **Bugs found in E08 itself: zero.** Two bugs were found and fixed in my own test harness during this pass (documented above) — disclosing them is the same discipline used in the V07 and accounting audits, not a finding against the code under audit.
3. **Accounting mismatches: zero.** All fixture reproductions (B, C, D, E, F, G against the real `CaptureStore`/`Capture`; canonical serialization against the real `accounting.canonical_jsonl`/`canonical_array`) matched exactly.
4. **Leakage findings: zero.** No path was found where a collector could discover an undiscovered title, retrieve a retrospectively-stale body, or bypass discovery-gating. The strongest test (overwritten-trigger retrieval) and the ambiguity test both confirmed the frozen behavior.
5. **Policy-specific asymmetries: zero found in E08 itself** (no branching exists at all); the deeper fairness question (Q13) is open only in the sense that it needs E09 *and* E10 to exist before it can be checked end-to-end — that is a scope limit of auditing E08 in isolation, not a finding against E08.
6. **Can E09 continue?** Yes. Nothing found here should slow down or change Ubayd's in-progress E09 work.
7. **Should E10 be blocked pending fixes?** No fixes are pending — there is nothing here to fix. E10 is unblocked from E08's side. (E10 not existing yet is simply because it hasn't been started, per the current status; it is not blocked by any finding in this audit.)
