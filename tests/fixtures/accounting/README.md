# Hand-counted accounting fixtures — v0.1

**Nine data-only fixtures; E08 STILL BLOCKED pending Sam/Aaron acceptance.** Contract: [`R04_ACCOUNTING_AMENDMENT.md`](../../../docs/R04_ACCOUNTING_AMENDMENT.md). No engine generated these expected values. Counts below are direct arithmetic on literal representations; author-side local JSON/UTF-8/hash checks are not independent reviewer signoff.

## Reading the files

The pretty-printed fixture **manifest file size is not a cost**. Parse the JSON first. A `canonical_*` string's decoded value is the exact modeled serialization: encode that value as UTF-8, without adding another newline. The final `\n` in its JSON notation decodes to **one LF byte**. Canonical metadata has sorted keys, compact comma/colon separators, literal non-ASCII, JSON escapes for controls/quotes/backslashes, and one final LF. Every brace/quote/bracket/comma/colon and that LF is charged. Bodies are raw UTF-8, **no JSON wrapping and no extra LF**; hex is the authoritative body byte spelling. No implementation-generated golden files.

All examples are synthetic; keys dse~A/B/C/é are opaque test keys, not historical fixture selections. B–G isolate storage and body GET costs (shared feed M=0), not full collector runs. Their dispatch time equals capture time, with local checkpoints as specified. H/I are isolated protocol/serialization tests, not capture-admission invocations. The checkpoints test integration arithmetic, not changes to the experiment's frozen T. Standalone body GET request counts include every attempt, not a second request for its response or admission. Reference/hash fields are inside packet bytes, never added twice. Uncharged diagnostic/manifest bytes are inaccessible to policies.

## Reusable hand arithmetic

A JSON field's size = key length + **3** (two quotes and colon) + serialized value length. Add commas between fields, outer braces, then LF. ASCII characters are one byte; **é is c3 a9 = two UTF-8 bytes**. Fixed UTC timestamp `2026-05-24T00:00:00.000000Z` has 27 characters/bytes, **29 with quotes**. Any timestamp used here has the same width. Digests have 64 ASCII hex digits, **66 with quotes**.

### Feed record (A)

Exact decoded canonical bytes, with `<LF>` denoting the single byte 0a, not six literal characters:

```text
{"action":"live_change","event_time":"2026-05-24T00:00:00.000000Z","page_key":"dse~A"}<LF>
```

| Component | Calculation | Bytes |
|---|---|---:|
| action field | 6+3 + (11+2) | 22 |
| event_time field | 10+3 + (27+2) | 42 |
| page_key field | 8+3 + (5+2) | 18 |
| Two commas, braces, LF | 2+2+1 | 5 |
| **Record** | 22+42+18+5 | **87** |

### Standard packet (B–G)

```text
{"body_sha256":"4a99557e4033c3539de2eb65472017cad5f9557f7a0625a09f1c3f6e2ba69c4c","capture_time":"2026-05-24T00:00:00.000000Z","page_key":"dse~A","request_seq":1}<LF>
```

| Component | Calculation | Bytes |
|---|---|---:|
| body_sha256 field (reference included) | 11+3 + 64+2 | 80 |
| capture_time field | 12+3 + 27+2 | 44 |
| page_key field | 8+3 + 5+2 | 18 |
| request_seq field | 11+3 + 1 | 15 |
| Three commas, braces, LF | 3+2+1 | 6 |
| **Packet** | 80+44+18+15+6 | **163** |

There is no separate object header/hash/reference record. é body = 2 bytes, so standalone admission = **163+2=165**. All B–G packets have the same width: one-letter ASCII key suffix, one-digit request_seq, fixed-width time and digest. A different hash costs the same, but identifies different bytes. Digest values can be independently checked using any SHA-256 implementation; cryptographic hashing is not a hand character-count requirement.

Body response header `{"outcome":"body"}<LF>` = (7+3)+(4+2)+2+1 = **19**; downloading é costs **19 metadata + 2 body = 21**, whether admitted, duplicated or later evicted. Hashes are locally computed, not extra downloaded fields.

## A — `A_feed.json`: feed record and batch framing

One poll receives one record: canonical array has the 86-byte record object without its standalone LF, plus two brackets and LF = **89 downloaded metadata bytes**. Retain standalone record JSONL = **87**. Request count 1, bodies/packets/references 0; final/peak S=0, final/peak M=87. Delivery 00:01, checkpoint 01:01: **87 byte-hours**.

Additional independent subcases: empty poll costs **1 request, 3 downloaded bytes (`[]`+LF), 0 new retained bytes**. Two physically distinct but identical records in one response cost 86+86+comma+brackets+LF = **176 downloaded**, **174 retained**; no feed-record dedup. These alternatives are not added to the main one-record scenario.

## B — `B_unique.json`: unique captured body

Known body é, hex c3a9, canonical hash in the literal packet. One packet **163**, one object **2**, total **165**. Cap 165 admits exactly. Store path **0 → 165**. One retained reference/object; request 1, download 19+2=21; peak/final 165. Retained for one hour: **165 byte-hours**. SHA field's 80 bytes already included, extra object/reference framing **0**.

## C — `C_duplicate.json`: duplicate body, dedup enabled

Two different page captures of identical é content at 00:00/01:00. Separate packets, global exact-content body sharing. Marginal admissions **165 then 163**; store **0 → 165 → 328**. Two packets 2×163=**326**, one object **2**, refcount 2; final/peak **328**. No eviction. Both GETs cost full download: 2×19 metadata + 2×2 bodies = **42**, requests **2**. At 02:00 checkpoint: 165×1h + 328×1h = **493 byte-hours**.

## D — `D_nondedup.json`: repeated body without dedup

Exactly C's packets/content/times, non-dedup storage. Two private objects, each addressed by its packet's request_seq+hash; no additional pointer bytes. Marginal **165,165**; store **0 → 165 → 330**. Packets **326**, bodies **4**, two objects of refcount 1. Peak/final **330**. Request/download identical to C: **2 / 42 bytes**. Byte-hours **165+330=495**. Tiny caps in C/D isolate no-eviction arithmetic; they are not budget-matched policy results.

## E — `E_fifo.json`: forced eviction, final-reference deletion

Cap **328**. First two captures are é as C; third at 02:00 is `xy`, raw hex **78 79**, 2 bytes, different hash. Incoming packet 163 + new body 2 = **165**. Its standalone size fits; it is not oversize.

| Operation | Packets retained | Object bytes | Packet bytes | S |
|---|---|---:|---:|---:|
| Initial | none | 0 | 0 | 0 |
| Admit 1 | 1 | 2 | 163 | 165 |
| Admit 2 | 1,2 | 2 | 326 | 328 |
| Test candidate (not admitted) | unchanged | — | — | 328+165=493 >328 |
| Evict 1 | 2 | 2 (still referenced) | 163 | 165 |
| Retest candidate (not admitted) | unchanged | — | — | 165+165=330 >328 |
| Evict 2 | none | 0 (last reference removed) | 0 | 0 |
| Admit 3 | 3 | 2 (xy) | 163 | 165 |

Actual store path **0,165,328,165,0,165**; peak **328**, NOT 493. Evicted packet bytes **326**, body bytes **2**. Final **165**, one packet/object/ref. Requests **3**, downloaded metadata **57**, bodies **6**, total **63**. 03:00 checkpoint: **165+328+165=658 byte-hours**. Same-time evictions at 02:00 consume zero integration time but are audited.

## F — `F_oversize.json`: rejection does not destroy retained evidence

Cap **165**. Admit first é packet at 00:00 →165. Attempt 2 at 01:00 returns ASCII `abc`, hex **61 62 63**, 3 bytes; packet163+body3=**166 >165** intrinsically. Reject **before evictions**. Store path **0 →165 →165**, retained request1 unchanged, no packet2 or abc object retained. Peak/final **165**; bytes evicted **0**. Two successful-body GET responses still count: requests **2**, metadata **38**, body transfers **2+3=5**, total **43**. 02:00 checkpoint byte-hours **165×2=330**. Audit facts include request2, outcome body, oversize disposition and empty eviction list, but no free retained body text.

## G — `G_shared_fifo.json`: repeated body keeps its remaining reference

Cap328, first two captures as C. Incoming third capture is also é; standalone165 fits, current marginal is packet-only **163**. Candidate **328+163=491** does not fit. Evict oldest packet1: S becomes **165**, object stays with packet2. Recompute marginal163, admit packet3: **165+163=328** fits. Path **0,165,328,165,328**. Final FIFO packet2,packet3; one body, refcount2. Evicted **163 packet bytes, 0 body bytes**; final/peak328. Requests3, downloads **57+6=63**; 03:00 byte-hours **165+328+328=821**. No recency refresh of packet2 and no cost-free repeated packet.

## H — `H_protocol.json`: headers, NA, directory arrays

Outcome header general length = **15 + ASCII outcome-string length** (key/colon10 + value quotes2 + braces2 + LF1). Thus body/missing/unknown/body_unknown/ambiguous/unsupported = **19,22,22,27,24,26**. Six isolated response-accounting attempts sum **140 metadata bytes** and **6 requests**. Known-empty body is 0; missing body payload is 0; four uncertain payload lengths are **null/NA**, never zero. Known-byte lower bound140; **total downloaded bytes=null**, not140 asserted complete. No store admission invoked: retained/peak/final S=0.

Separate F terminal-directory alternatives: empty `[]`+LF **3**; `["dse~A"]`+LF = 7+2+1=**10**; `["dse~A","dse~é"]`+LF = 7+8+1+2+1=**19**. Each costs one directory request and exactly that many downloaded/retained metadata bytes; final=peak=3/10/19 respectively. Terminal admission has **0 byte-hours** before T. These alternatives are not added together and contain no body-status/hash data.

## I — `I_encoding.json`: transcoding and serialization edge cases

- ASCII abc: source3, canonical3 bytes. UTF-8 é: source2, canonical2. Latin-1 é: source1 (`e9`), canonical2 (`c3a9`). Identical canonical é bytes/hash share one object regardless of source encoding; no encoding metadata is charged. Empty known ASCII body: source0/canonical0, genuine SHA-256 of empty bytes, not an unknown sentinel.
- Generic serializer probe (not a legal feed/packet schema) tests false, null, integer10, literal é, escaped LF/quote/backslash. Field sizes: flag **12**, n **6**, s **14**, z **8**, plus commas/braces/LF **6** = **46**. The literal escaped canonical string is in the JSON file; no newline normalization/ASCII escaping allowed.
- Packet-width probe uses page_key dse~é instead of dse~A (**+1 byte**) and request_seq10 instead of1 (**+1 byte**): packet **165**, plus é body2 gives standalone **167**. No stored admission is invoked; peak/final actual store0. Its candidate size is not a measured retained peak.

## Determinism, local checks, and independent acceptance

These totals depend solely on literal strings/hex, immutable schemas, fixed timestamps/one-hour gaps, and fixed operation order—not source history, policy outcomes or E08 code. Serialization sorting is never used to adjudicate historical event order.

Author-side local verification completed: **9/9 PASS, no byte-count mismatches**. A temporary standard-library calculation parsed all nine JSON files, compared each canonical string against reserialization, counted actual UTF-8 bytes, verified source/body hex/hash, and recomputed component totals and explicit FIFO arithmetic/byte-hour sums. It imported no `ebe` code and created no observer/store or saved implementation helper. Expectations were hand-authored before this check, not derived from future E08 output. This is author verification, not an independent human review.

**Sam or Aaron must independently recompute and accept these hand-counted fixtures without relying on future E08 code.** Required acceptance record: `audit/R04_ACCOUNTING_VERIFICATION.md`, reviewer identity, method, amendment/fixture hashes, nine case results and neutrality review. Author-side arithmetic checks alone do not satisfy that gate. No acceptance is present; **E08 STILL BLOCKED**. There are no collector results and no code implementation in this fixture directory.
