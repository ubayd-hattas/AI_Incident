# Fixes for X01 (checkpoint accounting), X02 (causal ordering), and A04 (retained-only boundary)

Role: independent validation (Sam), with explicit authorization to implement these fixes directly given the
deadline. `audit/SAM_RESPONSE_TO_PRE_RESULTS_AUDIT.md` independently confirmed all three as real bugs/gaps with
fresh reproductions. This document records the fixes applied to `src/ebe/observer.py` and `src/ebe/collectors.py`,
and the re-verification evidence that they work and introduce no regression.

## X01 — checkpoint response accounting

**Bug:** `Observer.get_body` only ever classified a response as `pending` when `response_time > HORIZON_END` (the
frozen absolute replay horizon). A collector's own `checkpoint` is usually much earlier than `HORIZON_END`, so a GET
dispatched before that checkpoint but resolving after it (via `get_response_delay_us`) was fully processed and
counted as a completed BODY response — even though, from the checkpoint's own vantage point, the outcome was not
yet knowable. `Observer.costs(checkpoint)`'s `checkpoint` parameter only integrated shared-metadata byte-hours; it
never touched the outcome/pending/downloaded-byte counters, which were populated unconditionally inside `get_body`
at dispatch/resolution time.

**Fix:** `Observer` now keeps a separate `_non_body_metadata` counter (feed-poll and terminal-directory bytes only,
excluding GET response headers), and `costs(checkpoint)` recomputes every checkpoint-sensitive field
(`successful_body_responses`, `missing_responses`, `unknown_responses`, `body_unknown_responses`,
`ambiguous_responses`, `unsupported_responses`, `pending_body_requests`, `downloaded_metadata_bytes`,
`downloaded_known_body_bytes`, `unknown_body_byte_attempts`) directly from the per-request `_audit` trail: any
record whose `response_time` is `None` (permanently pending past `HORIZON_END`, as before) or `> checkpoint` is
counted as pending, contributing zero outcome/byte weight; everything else is counted exactly as before. Calling
`costs()` with no checkpoint is completely unchanged (uses the original eager counters, matching every existing
caller/test that doesn't pass a checkpoint).

`CollectorResult.outcome_counts` (in `collectors.py`) had the identical blind spot — it derived counts straight from
`body_results` with no checkpoint awareness — and is fixed the same way: a `BodyResponse` whose `response_time >
self.config.checkpoint` is now bucketed as `"pending"` instead of its nominal outcome.

**Verification:**
- Independent reproduction (`/tmp/repro_x01.py`, a scenario built from scratch, not the pre-results audit's own
  snippet): PCD, 1-minute sweep, 45s phase, checkpoint at `t0+2:00`, 30s response delay, one save at `t0+10s`. Before
  the fix: `successful_body_responses=1, downloaded_known_body_bytes=1, pending_body_requests=0`. After the fix:
  `successful_body_responses=0, downloaded_known_body_bytes=0, pending_body_requests=1` — correct.
- Full test suite (103 tests) passes unchanged.
- All prior independent audit scripts re-run clean: `verify_collectors_cross_policy.py` (0 failures),
  `verify_e08_neutrality.py` (0 failures, after two of its own test cases were fixed — see X02 below),
  `verify_ahi_against_real_code.py` (0 failures), `verify_accounting.py` (9/9).

## X02 — causal ordering guard

**Bug:** `Observer.get_body`'s only ordering guard was against the *previous GET call's* `request_time`
(nondecreasing dispatch order). Nothing checked a GET's `request_time` against the most recent `poll_feed` call, so
a caller could poll at a later time (discovering a page), then dispatch a GET timestamped *before* that poll —
using knowledge that, causally, hadn't been delivered yet at that earlier instant. Symmetrically, `poll_feed` had no
guard against being called after `terminal_directory` (only the reverse direction was enforced).

**Fix:** `get_body` now raises `ObserverTimeError` if `request_time < self._last_poll` (when any poll has occurred).
`poll_feed` now raises `ObserverError` if `self._directory_requests` is nonzero, making the feed/directory mutual
exclusion two-directional.

**Verification:**
- Independent reproduction (`/tmp/repro_x02.py`): save at `t0+1:10`; poll at `t0+2:00` (discovers it); GET
  timestamped at `t0+1:30` (before that poll). Before the fix: returns `BODY`, `b'F'` — the loophole. After the fix:
  raises `ObserverTimeError`.
- No shipped collector was ever affected (`PeriodicCollector`/`EventDerivedCollector` always dispatch causally), so
  this is a pure hardening with zero behavioral change to P/PD/PCD/E(q) — confirmed by the full test suite and
  `verify_collectors_cross_policy.py` both passing unchanged.
- **My own `audit/verify_e08_neutrality.py` had two synthetic test cases that exercised exactly this loophole**
  (dispatching a GET at an original trigger's timestamp *after* a much-later poll, to test "no retrospective replay
  of an overwritten body"). Both were rewritten to dispatch causally (poll and GET at the same, earlier instant,
  using response *delay* alone — not backdated dispatch — to land the response after the overwrite), which tests
  the identical property without relying on the now-forbidden ordering. Confirmed still PASS after the rewrite.

## A04 — retained-only evidence boundary

**Gap:** `CollectorResult.body_results` and `.capture_attempts` carry every dispatched response and every attempted
capture, including ones `CaptureStore` rejected as oversize or later evicted. Nothing in the public interface
distinguished "genuinely retained at the final checkpoint" from "attempted, possibly not retained" — a future E12
implementation could accidentally score against `body_results`/`capture_attempts` and silently defeat the entire
point of the capacity cap.

**Fix:** Added `RetainedEvidenceUnit` (`page_key`, `capture_time`, `request_seq`, `body_sha256`, `body`) and a new
`CollectorResult.retained_evidence` field, populated in both `PeriodicCollector.run()` and
`EventDerivedCollector.run()` *exclusively* from `store.retained_captures` plus `store.body_for_capture(request_seq)`
— the latter already refuses (raises `KeyError`) for anything not currently retained, so this surface cannot
structurally leak an evicted or oversize body. `body_results`/`capture_attempts` are unchanged and still exist (removing
them would break the existing, already-passing test suite and other audits that legitimately use them as
diagnostic/audit history) — they are now explicitly documented as diagnostic-only via the new dataclass's docstring,
and `retained_evidence` is the field a future E12 must use for anything claiming to be "retained state."

**Verification:**
- Independent reproduction: one save, `capacity_bytes=0` (nothing retained). Before and after the fix,
  `body_results[0].body` still (correctly, by design) shows the diagnostic raw response — but `retained_evidence`
  is now `()`, an empty tuple, giving E12 a safe, structurally-guaranteed-correct surface to use instead.
- Full test suite passes unchanged (additive field, default `()`, no existing caller broken).

## What this means for the gates

- **X01 and X02 are fixed in `src/ebe/observer.py`/`src/ebe/collectors.py`**, not just reported. Both were on the
  gate register as `BLOCKER BEFORE X13`.
- **A04 is fixed** (`RetainedEvidenceUnit`/`retained_evidence`), closing the `BLOCKER BEFORE E12` item of the same
  name.
- Combined with A01 (E09/E10 audit reconciliation, already merged), A02 (accounting-hash mismatch, corrected — see
  `audit/SAM_RESPONSE_TO_PRE_RESULTS_AUDIT.md`), and A03/A11 (now independently verified 14/14, see
  `audit/A11_INDEPENDENT_VERIFICATION.md`), **A01–A04 are all now closed**. A05 (typed evidence/body/event universes,
  denominator firewall) is a design constraint on E12's *own* implementation rather than a precondition that can be
  satisfied in the abstract before E12 exists — it should be enforced and tested as part of building E12 itself.
- **X13 remains NOT AUTHORIZED.** X01/X02 closing removes two of its five blockers, but F (the low-information
  comparator collector, X03) is still unimplemented, and X04 (full cost/overhead instrumentation) and X05 (E12
  hand-scored synthetic acceptance — which needs E12 to exist first) are untouched. S01–S05 (PCD-R repair, ordering
  stress, latency/phase sensitivities, ambiguity bounds, archive ledger) are also untouched.

## Reproduce this

```powershell
python -m unittest discover -s tests
python audit/verify_collectors_cross_policy.py
python audit/verify_e08_neutrality.py
python audit/verify_ahi_against_real_code.py
python audit/verify_accounting.py
```
