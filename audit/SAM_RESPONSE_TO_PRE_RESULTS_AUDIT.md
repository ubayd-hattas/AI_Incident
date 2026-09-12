# Response to the final hostile pre-results audit (`docs/PRE_RESULTS_AUDIT.md`)

Role: independent validation (Sam). This document independently re-checks the pre-results audit's concrete,
falsifiable claims rather than taking them on trust or defending prior work reflexively — the same discipline
applied to Ubayd's and Jaswin's work all along applies to this audit too. Three claims are **confirmed** by fresh,
independently-constructed reproductions (not copies of the audit's own snippets). One claim (A02) is **not
reproducible** against the current repository and is corrected below with hard evidence. One self-criticism (D04,
aimed at my own `E08_NEUTRALITY_AUDIT.md`) is **accepted and closed for real**, not just acknowledged.

## Confirmed: X01 — checkpoint response accounting is not "as of C"

Independently reproduced with a scenario I built myself (different timestamps/page name from the audit's own
snippet), in `/tmp/repro_x01.py` (throwaway, not committed — logic below is what matters): a page saved at
`t0+10s`, PCD with a 1-minute sweep interval and 45s phase (first sweep at `t0+45s` is too early to see the save;
second sweep at `t0+1:45` dispatches the GET), checkpoint at `t0+2:00`, a 30s response delay.

```
body_results: [BodyResponse(request_time=00:01:45, response_time=00:02:15, outcome=BODY, body=b'A')]
successful_body_responses: 1
downloaded_known_body_bytes: 1
pending_body_requests: 0
captures_admitted: 0
retained_captures: 0
```

Root cause confirmed by reading `src/ebe/observer.py:get_body` directly: it only classifies a response as
`pending` when `response_time > HORIZON_END` (the frozen absolute replay horizon), never against the collector's
own, usually much earlier, `checkpoint`. `Observer.costs(checkpoint)`'s `checkpoint` parameter only integrates
`shared_metadata_byte_microseconds` up to that point — it does not touch `_outcomes`, `_downloaded_body`, or
`_pending`, which are unconditional cumulative counters incremented inside `get_body` at the moment it is called.
`collectors.py`'s `completed` list correctly filters `response_time <= config.checkpoint` before admitting anything
to `CaptureStore`, so **storage/retention accounting is correct**, but **`ObserverCosts` reports this response as a
completed, downloaded BODY**, when from the checkpoint's own vantage point it should still read as one pending
request with zero downloaded bytes. This directly means my own `E08_NEUTRALITY_AUDIT.md` Q6 ("confirmed
`body_requests` increments for every dispatch including the pending one") tested pending-past-`HORIZON_END` only,
never pending-past-an-earlier-collector-checkpoint — a real blind spot in that audit's coverage. **Confirmed real
bug, not previously caught.**

## Confirmed: X02 — `get_body` has no causal ordering guard against discovery/poll time

Independently reproduced: a page saved at `t0+1:10`; poll the feed at `t0+2:00` (discovers it, default 5s
publication lag); then dispatch a GET timestamped at `t0+1:30` — earlier than the very poll that discovered the
page.

```
discovered after poll: ('dse~FUTURE',)
GET dispatched at 00:01:30, after a poll at 00:02:00 but before that poll's own instant:
  outcome: BODY, body: b'F'
```

Root cause: `get_body`'s only ordering guard is `request_time < self._last_dispatch` (monotonicity against the
*previous GET call*), and `poll_feed`'s only guard is against the previous poll. Neither checks a GET's
`request_time` against the poll that actually delivered discovery for that page. Confirmed by code reading, and
confirmed that neither shipped `PeriodicCollector` nor `EventDerivedCollector` exploits this: both always dispatch
GETs at sweep/dispatch times that are `>=` the poll that discovered the page, in nondecreasing order, so this is
**not a demonstrated current advantage for any policy** — but it is a real API-level looseness worth hardening
before X13, as the audit says.

## Confirmed: A04 — response/capture-attempt history exposes bodies never admitted to the store

Independently reproduced: one page, `capacity_bytes=0` (nothing can ever be retained), one save.

```
retained_captures: 0
body_results[0].body: b'SECRET_BODY'
capture_attempts[0].capture.body: b'SECRET_BODY'
```

Confirmed: `CollectorResult.body_results` and `.capture_attempts` carry full body bytes regardless of what the
store actually admitted. `CaptureStore` itself is correct — it rejects/evicts properly, and `body_for_capture`
correctly refuses evicted references. The gap is that nothing currently stops a naive future E12 implementation
from scoring evidence coverage against `body_results`/`capture_attempts` instead of the real retained-at-checkpoint
snapshot, which would silently defeat the whole point of the capacity cap. **Confirmed real gap**, correctly
classified as a pre-E12 blocker (A04), not a storage bug.

## Correction: A02 — the accounting-hash mismatch does not reproduce

The pre-results audit states "Checked all 11 SHA-256 entries in accounting acceptance against local bytes: none
match" and lists A02 as a **BLOCKER BEFORE E12**. Independently recomputing SHA-256 over every one of the same 11
files, right now, against a clean working tree (`git status` clean, `HEAD` = current `main`):

| File | Current SHA-256 | Matches `R04_ACCOUNTING_VERIFICATION.md`'s pinned hash? |
|---|---|---|
| `docs/R04_ACCOUNTING_AMENDMENT.md` | `4370744a1da7e5586912762e60b5ce8e4d5560ce63e7c572c6330d7eefde4abb` | **Yes** |
| `tests/fixtures/accounting/README.md` | `ae60dd12b22bcc9257219dbdb4475e73ff0587b3442fb767c0cc1b917309df43` | **Yes** |
| `tests/fixtures/accounting/A_feed.json` | `5412bbe2cb0e3e658f49280a4ceeb96720b2b16dfdc154fb9ab40533d31ce0ce` | **Yes** |
| `tests/fixtures/accounting/B_unique.json` | `3c69ed5db8efb91b348b522c87069aaf1b95b5f8ceb2a6b9f5cedffb0b632a9f` | **Yes** |
| `tests/fixtures/accounting/C_duplicate.json` | `a797a7a53d0d100d970dee2b1c5c3005e59963f2ee0230b9bb5affaa08901525` | **Yes** |
| `tests/fixtures/accounting/D_nondedup.json` | `5682dd2ee68d2e7cc7385fc390fdaba0258514348b12d372957b528419fde01e` | **Yes** |
| `tests/fixtures/accounting/E_fifo.json` | `2f0fa686f886a6f5d0a90f87df8e72d539872aea3a658ab6e5c10fdf13a696ea` | **Yes** |
| `tests/fixtures/accounting/F_oversize.json` | `ce1e5afd11fdaac47865791430b7fb8243c4d0bb71ef8fbbd971de6d19caf999` | **Yes** |
| `tests/fixtures/accounting/G_shared_fifo.json` | `e07f39048fa95e63bbc402adecdab870767ff3325004612cc1f7e7e3f74f0a7e` | **Yes** |
| `tests/fixtures/accounting/H_protocol.json` | `da9c3da6018a9b35b5c6034a398960c183c1658d69e427b45210fb4c93750d14` | **Yes** |
| `tests/fixtures/accounting/I_encoding.json` | `e61761488cd5a2d3a5ec5858866132175c6f456dbb17a7816de86c8d8f4dce50` | **Yes** |

**All 11 match exactly**, byte for byte. Further, `git log --oneline --follow -- docs/R04_ACCOUNTING_AMENDMENT.md`
(and the same for each fixture file) shows exactly **one** commit ever touched these files —
`aaf0028 docs: freeze R04 accounting and block E08 pending review`, the original freeze — with no subsequent edits.
The working tree is clean, so current bytes are exactly the bytes committed at `aaf0028`, which are exactly the
bytes `R04_ACCOUNTING_VERIFICATION.md` pinned at acceptance time. There is no custody gap to trace: the files never
changed.

I am not asserting the pre-results audit fabricated this — the more likely explanation is a hashing-methodology
difference in that pass (e.g. a different checkout state, an encoding/line-ending handling difference in whatever
computed the "current" column of its own appendix table, which itself lists a *different* amendment hash,
`3ccd0a55...`, than what any live copy of this repository has ever contained). Whatever the cause on that end, **as
independently checked right now, A02 does not reproduce and should not block E12.** `docs/PROJECT_STATUS.md`'s
current text (§1, §3 R04 row, §7 changelog) asserting "all 11 hashes... disagree" is being corrected alongside
this document.

## Accepted and closed: D04 — my own E08 audit overstated A/H/I's chronology

The pre-results audit is right: `audit/E08_NEUTRALITY_AUDIT.md` originally said fixtures A/H/I were "already
covered by the pre-E08 acceptance, which audited the same `accounting.py` functions." That is false —
`git log` confirms `audit/R04_ACCOUNTING_VERIFICATION.md` (commit `9116a97`) predates `src/ebe/accounting.py`'s
existence (commit `ffc7e99`) entirely. The pre-E08 acceptance used my own from-scratch simulator
(`audit/verify_accounting.py`, which imports no `ebe` code at all — confirmed by inspection), not the real shipped
code. A/H/I had genuinely never been checked against the real implementation.

This is now closed for real, not just relabeled: `audit/verify_ahi_against_real_code.py` independently drives every
concrete claim in A/H/I through the actual `Observer`/`accounting`/`storage` code —

- **A**: one-record canonical bytes (87) and array framing (89), empty-poll framing (3), two-record framing (176)
- **H**: all six outcome-header byte counts (19/22/22/27/24/26, sum 140) via the real `accounting.canonical_jsonl`,
  and terminal-directory array framing for 0/1/2 titles (3/10/19)
- **I**: ASCII/UTF-8/Latin-1 sources all canonicalize to the identical UTF-8 body and SHA-256 regardless of source
  encoding; a genuinely empty known body hashes to the real empty-string SHA-256, not an unknown sentinel; the
  generic serializer probe (`false`/`null`/int/non-ASCII/escaped LF-quote-backslash) round-trips through the real
  serializer with literal (non-ASCII-escaped) output; the packet-width probe's page_key/request_seq byte deltas
  match via the real `Capture.packet_bytes`

0 failures. `audit/E08_NEUTRALITY_AUDIT.md` item 8 has been corrected in place with a note pointing here.

## What this changes

- **A02 is not a blocker as stated.** The accounting acceptance's custody is intact; no reacceptance of *content*
  is needed (though nothing here waives Aaron's still-open optional second confirmation).
- **X01, X02, A04 are real and now independently confirmed**, not just asserted by one audit pass — they remain
  correctly classified as pre-X13/pre-E12 blockers and are not fixed by this document. Fixing `src/ebe/observer.py`
  and `src/ebe/collectors.py` is implementation work belonging to Ubayd, not this validation pass.
- **D04 is fixed, not just disclosed** — A/H/I now have genuine real-code coverage.
- Nothing else in the pre-results audit's findings was re-litigated here; its sensor-access matrix, PCD-strength
  analysis, and statistical-plan sections were not independently re-derived in this pass and stand as delivered.

No source, collector, annotation, frozen contract, or prior acceptance record's *findings* were altered — only
`audit/E08_NEUTRALITY_AUDIT.md`'s item 8 text (a correction to what it claims to have covered) and
`docs/PROJECT_STATUS.md` (reflecting the A02 correction and this closure) were touched, alongside the two new files
this document names.
