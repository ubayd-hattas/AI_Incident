# Response to the final hostile pre-results audit (`docs/PRE_RESULTS_AUDIT.md`)

> **Update:** X01, X02, and A04 (confirmed real below) have since been fixed in `src/ebe/observer.py` and
> `src/ebe/collectors.py`, with full re-verification against the existing test suite and every audit script in this
> directory. See `audit/X01_X02_A04_FIXES.md` for exactly what changed and why. The findings below describe the
> bugs as originally confirmed; they are not stale, just superseded by that follow-up.
>
> **Retraction (2026-09-13, Sam): the "Correction: A02" section below was wrong. Jaswin's pre-results audit was
> right and I was wrong.** I computed all 11 "current" hashes using `sha256sum`/`open(path,'rb')` against my local
> Windows working-tree files. This machine has `core.autocrlf=true`, which silently converts every checked-out
> text file's LF line endings to CRLF — bytes that differ from what git actually stores (LF) and from what any
> other clone produces. I re-verified: `git show HEAD:<path> | sha256sum` (the canonical, checkout-independent
> content) for all 11 files reproduces **exactly** the hashes `docs/PRE_RESULTS_AUDIT.md`'s own appendix reported —
> the ones I dismissed as unreproducible. The file *contents* were never wrong or tampered with; only my hashing
> method was. Corrected in `audit/R04_ACCOUNTING_VERIFICATION.md`, `annotations/splits.json`,
> `annotations/A11_BENCHMARK_SPEC.md` (which had the same bug, independently discovered while investigating this),
> and a new root `.gitattributes` (`* text=auto eol=lf`) so it can't recur silently. This is exactly the kind of
> error this whole validation exercise exists to catch — including in myself.

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

## Retracted and fixed: A02 — the accounting-hash mismatch was real, and has now been repinned correctly

**This section originally claimed A02 didn't reproduce. That claim was wrong; see the retraction note at the top
of this document.** The pre-results audit stated "Checked all 11 SHA-256 entries in accounting acceptance against
local bytes: none match." That was correct. My original rebuttal computed all 11 "current" hashes via
`sha256sum path` / `open(path, "rb")` on my local Windows checkout, which has `core.autocrlf=true` — git's clean/
smudge filter converts the repository's LF-stored content to CRLF on checkout, silently. Every one of those 11
"current" hashes was therefore the hash of CRLF bytes that exist only on my machine's working tree, not the LF
bytes actually stored in the git blob (what a fresh clone, CI, or any teammate without that exact local setting
would get).

Re-verified properly, using the canonical committed content (`git show HEAD:<path> | sha256sum`) instead of a raw
working-tree read:

| File | Canonical (git-blob) SHA-256 | Matches `PRE_RESULTS_AUDIT.md`'s appendix? | Matches original `R04_ACCOUNTING_VERIFICATION.md` pin (CRLF)? |
|---|---|---|---|
| `docs/R04_ACCOUNTING_AMENDMENT.md` | `3ccd0a5566cb31546455bc1a98b56bcc4369ea1d4e78f3f9f95f8e1adf573fbb` | **Yes** | No |
| `tests/fixtures/accounting/README.md` | `3f604a6beb31a5ce0962a7041d37f5b72540ccf804469450328ab1918a78f586` | **Yes** | No |
| `tests/fixtures/accounting/A_feed.json` | `f16c9066c5f30cc48e4c226510da24368cb4079012fee67ea76a54945b6a80bb` | **Yes** | No |
| `tests/fixtures/accounting/B_unique.json` | `926df392e3a1c2682cae612aa51ef17a2f7857d163b4020ff130d95d0efe8320` | **Yes** | No |
| `tests/fixtures/accounting/C_duplicate.json` | `5427dc744ff5fcf1c2219799b6840bfb0e15c95d47b547c6a4fddb627268e26b` | **Yes** | No |
| `tests/fixtures/accounting/D_nondedup.json` | `101dcf53e881af1641173670abc0ceb3fd0bccd17eba3c590d7eaa4f67666ea8` | **Yes** | No |
| `tests/fixtures/accounting/E_fifo.json` | `6d99644641b028bda6f33d4238562249c3bfe9839d5bb81e5e0f7aaed4c2e107` | **Yes** | No |
| `tests/fixtures/accounting/F_oversize.json` | `8e5e289e5721b9ab1e2addf002cf34a5eb731a45aef3c8a60fed54cdacb3409c` | **Yes** | No |
| `tests/fixtures/accounting/G_shared_fifo.json` | `6704dbf87693cfa67e01912c22bcc6c2a79dbaa69022d587d5cc46e8013cf89d` | **Yes** | No |
| `tests/fixtures/accounting/H_protocol.json` | `178ae931e9469c360517ee0edfb6131e21b5da920f4ed2d6724168020f4290da` | **Yes** | No |
| `tests/fixtures/accounting/I_encoding.json` | `f2013997173c8ca01b236052222fe1127c687d1608de1d8eef457375bf12e3a4` | **Yes** | No |

**All 11 canonical hashes exactly match `PRE_RESULTS_AUDIT.md`'s own appendix table.** `git log --oneline --follow`
still confirms exactly one commit (`aaf0028`) ever touched these files — the content genuinely never changed, only
the byte representation used to hash it did. `audit/R04_ACCOUNTING_VERIFICATION.md`'s pinned hashes have been
corrected to these canonical values. A02 is real, was real, and is now fixed by re-pinning correctly rather than by
declaring it a non-issue. `docs/PROJECT_STATUS.md` is corrected alongside this document.

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

- **A02 was real and is now fixed.** All 11 accounting-fixture hashes are re-pinned to their canonical (git-blob)
  values, matching `PRE_RESULTS_AUDIT.md`'s own appendix exactly. No fixture *content* changed or needs
  re-acceptance — only the hash-computation method was wrong (nothing here waives Aaron's still-open optional
  second confirmation).
- **X01, X02, A04 are real and now independently confirmed**, not just asserted by one audit pass — and, given the
  deadline, have since been fixed directly in `src/ebe/observer.py`/`src/ebe/collectors.py` (see
  `audit/X01_X02_A04_FIXES.md`) rather than left as a handoff, with full test-suite and audit-script re-verification.
- **D04 is fixed, not just disclosed** — A/H/I now have genuine real-code coverage.
- Nothing else in the pre-results audit's findings was re-litigated here; its sensor-access matrix, PCD-strength
  analysis, and statistical-plan sections were not independently re-derived in this pass and stand as delivered.

No fixture, evidence, or occurrence *content* was altered by the A02 retraction — only the hash values pinned in
`audit/R04_ACCOUNTING_VERIFICATION.md`, `annotations/splits.json`, and `annotations/A11_BENCHMARK_SPEC.md` (all of
which had the same CRLF-vs-canonical hashing bug, independently discovered while investigating this), plus a new
root `.gitattributes` and `docs/PROJECT_STATUS.md`. `audit/E08_NEUTRALITY_AUDIT.md`'s item 8 text was separately
corrected for the unrelated D04 finding above.
