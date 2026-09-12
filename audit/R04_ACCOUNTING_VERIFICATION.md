# R04 accounting verification — independent acceptance

**Result: 9/9 fixtures independently confirmed. E08 is AUTHORIZED for observer/storage implementation on the accounting-schema dependency.**

Reviewer: Sam (independent validation role, same role that produced V02/V07). Method: full from-scratch recomputation, not a check of the author's (Jaswin's) worked arithmetic in `tests/fixtures/accounting/README.md`. Read `docs/R04_ACCOUNTING_AMENDMENT.md` in full and implemented its rules independently in a throwaway script with zero imports from `ebe`, zero reuse of any author-side counting helper, and zero reference to the README's prose derivations while writing the recomputation logic. The README's worked numbers were consulted only afterward, to compare against my independently-produced results — the same discipline used for V02/V07.

## What was independently rebuilt from the contract text

1. **Canonical serialization `C(x)`** (§2): implemented as `json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",",":"), allow_nan=False).encode("utf-8") + b"\n"` — the exact stdlib spelling the amendment itself gives, applied to each fixture's raw field *values* (not its pre-supplied `canonical_*` strings), then compared byte-for-byte against those strings.
2. **Feed array framing** (§3): rebuilt the array-wrapping rule (per-record LF stripped inside the array, one LF after the closing bracket) from the prose description alone, applied it to fixture A's raw record, and confirmed it reproduces `canonical_response` and `downloaded_metadata_bytes=89` independently.
3. **Body/header schemas** (§4, §5): rebuilt the six outcome headers and the four-field packet schema from field lists in the contract, not from the README's byte tables.
4. **FIFO admission algorithm** (§6): re-implemented from the prose rules (intrinsic oversize test before eviction, oldest-first eviction, recompute marginal size after each eviction, dedup shares by exact-byte-equal SHA-256 while non-dedup never shares an object by hash) as an independent simulator, then ran it against fixtures C–G's raw capacities and body sequences.
5. **Byte-hours** (§6): re-derived the half-open-interval integration rule and implemented it as a separate integrator, driven by each fixture's own operation timestamps.

## Result table

| Fixture | What it tests | Independently confirmed |
|---|---|---|
| A | Feed record + array framing, empty poll, duplicate-record non-dedup | All 7 checks pass (record bytes, response bytes, empty-poll bytes, two-identical-records bytes) |
| B | Minimal packet + body admission, exact-capacity fit | All 9 checks pass, including independently recomputed SHA-256 of `é` |
| C | Two captures, dedup enabled | All 11 checks pass, including independently re-simulated FIFO admission and byte-hours |
| D | Two captures, dedup disabled | All 10 checks pass — this is where the harness itself first went wrong (see below) and was fixed before being trusted |
| E | Forced double eviction, final-reference deletion | All 14 checks pass, including the two intermediate candidate totals (493, then 330) before each eviction |
| F | Oversize rejection without destroying existing evidence | All 9 checks pass |
| G | Duplicate admission where the shared body outlives one of its packets | All 13 checks pass, including the exact eviction/re-admission sequence |
| H | Response headers, NA-vs-zero handling, directory array framing | All 10 checks pass |
| I | Source-encoding transcoding (ASCII/UTF-8/Latin-1), empty body, escape sequences, integer/id width | All 14 checks pass |

**Total: 9/9 fixtures, zero unresolved discrepancies.**

## Errors found and fixed during this verification (disclosed, not hidden)

Two bugs surfaced in my own verification script on the first run — neither was a fixture or contract error:

1. **Non-dedup object-sharing bug.** My first FIFO simulator keyed retained body objects by content hash regardless of the `deduplicate` flag, so fixture D (dedup disabled) was incorrectly treated as if two identical-content captures shared one object — producing `retained_body_objects: got 1 expected 2` and three other related failures. The contract is explicit that "non-dedup allocates a fresh B copy for every admitted packet, even if hashes match globally" (§6); my first implementation silently violated this. Fixed by keying non-dedup objects on `(request_seq)` instead of content hash, and re-ran — D then matched on all 10 checks.
2. **Byte-hours off-by-one.** My integrator looped `range(len(store_path) - 1)`, which integrates one interval short of what's needed (it silently drops the final interval running from the last state change to the checkpoint) — this made every fixture with more than one retained state (C, D, E, F, G) undershoot the expected `store_byte_hours` by exactly that missing interval's contribution. Fixed the loop bound to `range(len(store_path))` with a corresponding assertion that the timestamp list always has exactly one more entry than the store-size list, and re-ran — all five previously-affected fixtures then matched exactly.

Both are recorded here for the same reason the project's own `evidence_timeline/CORRECTIONS.md` records its errors: an accounting-verification pass that never finds anything wrong with its own first draft is less trustworthy than one that does and shows its work.

## Neutrality / policy-fairness review (§7 of the amendment)

The amendment's own red-team table asserts no policy gets a hidden accounting advantage except the two explicitly preregistered exceptions (P's non-dedup storage, F's distinct terminal-directory access model). This verification pass supports that: the same canonical-serialization function, the same packet schema, and the same FIFO simulator — with no fixture-specific branches beyond the `deduplicate` flag the contract itself calls for — reproduced every fixture's expected totals without needing any additional special case. No fixture required a different byte-counting rule to reach its expected answer, which is the concrete form that "no hidden policy-specific exception" needs to take to be checkable at all.

## File hashes at time of acceptance

| File | SHA-256 |
|---|---|
| `docs/R04_ACCOUNTING_AMENDMENT.md` | `4370744a1da7e5586912762e60b5ce8e4d5560ce63e7c572c6330d7eefde4abb` |
| `tests/fixtures/accounting/README.md` | `ae60dd12b22bcc9257219dbdb4475e73ff0587b3442fb767c0cc1b917309df43` |
| `tests/fixtures/accounting/A_feed.json` | `5412bbe2cb0e3e658f49280a4ceeb96720b2b16dfdc154fb9ab40533d31ce0ce` |
| `tests/fixtures/accounting/B_unique.json` | `3c69ed5db8efb91b348b522c87069aaf1b95b5f8ceb2a6b9f5cedffb0b632a9f` |
| `tests/fixtures/accounting/C_duplicate.json` | `a797a7a53d0d100d970dee2b1c5c3005e59963f2ee0230b9bb5affaa08901525` |
| `tests/fixtures/accounting/D_nondedup.json` | `5682dd2ee68d2e7cc7385fc390fdaba0258514348b12d372957b528419fde01e` |
| `tests/fixtures/accounting/E_fifo.json` | `2f0fa686f886a6f5d0a90f87df8e72d539872aea3a658ab6e5c10fdf13a696ea` |
| `tests/fixtures/accounting/F_oversize.json` | `ce1e5afd11fdaac47865791430b7fb8243c4d0bb71ef8fbbd971de6d19caf999` |
| `tests/fixtures/accounting/G_shared_fifo.json` | `e07f39048fa95e63bbc402adecdab870767ff3325004612cc1f7e7e3f74f0a7e` |
| `tests/fixtures/accounting/H_protocol.json` | `da9c3da6018a9b35b5c6034a398960c183c1658d69e427b45210fb4c93750d14` |
| `tests/fixtures/accounting/I_encoding.json` | `e61761488cd5a2d3a5ec5858866132175c6f456dbb17a7816de86c8d8f4dce50` |

If any of these files change, this acceptance no longer applies to the new version and must be redone against the new hashes.

## Scope and limits of this acceptance

This accepts the **accounting schema and its nine hand-authored fixtures** — canonical serialization, packet/feed/directory schemas, FIFO admission, dedup semantics, and byte-hours arithmetic. It does **not**:
- Certify V02/A03/evidence-label work (separate gates, tracked elsewhere).
- Constitute a second independent reviewer beyond Sam — Aaron's independent acceptance, if the team wants a second confirmation, remains open and would only strengthen this, not gate it (the amendment requires "Sam **or** Aaron").
- Authorize anything beyond E08's observer/storage layer — collectors, evidence scoring, policy simulation, and the archive-aware baseline all keep their own separate ticket gates per `docs/R04_FROZEN_SPEC.md`.

## Verdict

**E08 AUTHORIZED for observer/storage implementation.** Per `docs/R04_ACCOUNTING_AMENDMENT.md` §8: "Once that acceptance records all nine cases as matched and no policy-advantaging ambiguity remains, update `PROJECT_STATUS.md` explicitly to E08 AUTHORIZED for observer/storage only." That condition is met.
