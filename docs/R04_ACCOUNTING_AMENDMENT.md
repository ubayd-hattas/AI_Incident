# R04 accounting amendment v0.1 — pre-E08

**Contract/fixture definitions frozen for independent acceptance. Accounting gate: BLOCKED; E08 STILL BLOCKED until Sam or Aaron accepts the byte fixtures.** This document is not that independent acceptance and does not authorize implementation yet.

Scope: fill the accounting deferral in `R04_FROZEN_SPEC.md` §§3/6. Read with `E06_IMPLEMENTATION_CONTRACT.md`, `E06_TIMELINE_ENGINE.md`, `audit/V07_BLIND_VALIDATION.md`, `EXECUTION_SPEC_v0.1.md` and `DATA_AUDIT_2026-09-12.md`. All were read locally. V07 clears the state-engine dependency sufficiently to proceed, with its disclosed independence/reproduction limitations; it does not verify accounting. Older R04/E06 status prose predates V07. This amendment does not certify evidence labels or reopen V02. No observer, store, collector, scorer or policy outcome is created/used here.

No changes to population, horizon, phase grid, polling intervals, feed lag, GET delay, q, caps, policy roster or archive-validity requirement. The following are reproducible **modeled payload bytes**, not historical HTTP wire sizes or total physical storage/RAM.

## 1. Cost units and ledger boundaries

Maintain disjoint counters: requests (feed/directory/body attempts); downloaded metadata bytes; downloaded known-body bytes; unknown-body-byte attempt count; retained metadata bytes; retained body bytes. Never add request bytes to downloaded bytes or count a storage admission as a second download.

Two retained-payload components:

- **Capped store S:** retained capture JSONL packets plus their referenced raw UTF-8 body objects. Cap includes both, not bodies alone.
- **Discovery/context store M:** delivered feed records as JSONL for every P/PD/PCD/E, retained through T; F instead retains its one terminal directory JSON array through T. Outside S's cap, but fully charged. No extra copy of feed response array framing is retained.

Report S, M, and S+M separately: current, peak, final and byte-hours. Retained metadata = packet bytes + M; retained body bytes = raw body objects. A component contributes to peak when present, final iff still present at T, and byte-hours for its actual retained duration.

| Operation/unit | Request count | Downloaded bytes | Retained metadata / body bytes | Peak, final, byte-hours |
|---|---:|---|---|---|
| Feed poll (even empty) | +1 feed | Response only, not outgoing request | None from request | None from request |
| Feed response | 0 additional | Entire canonical JSON array including brackets, commas and LF | Each delivered record's standalone JSON+LF in M; no dedup of identical physical records | M increases at delivery, retained to T |
| F directory request | +1 directory | Response only | None from request | None from request |
| F directory response | 0 additional | Canonical array of strings + LF | Exactly that array in M once, including empty array | Final/peak charged; at T duration zero |
| Body GET attempt | +1 body, even failure/rejection | Response as below, counted at completion | None merely for attempt | No S charge before admission |
| Known-body response | No second request | Outcome header + raw canonical UTF-8 body on every GET, even duplicates or rejected bodies | Header not retained; packet/body only on admission | See admission |
| Deleted/missing response | No second request | `missing` header; 0 body bytes | No packet/body | None |
| Unknown prehistory response | No second request | `unknown` header; unknown body bytes = NA, not 0 | No packet/body | None |
| Live/body-unknown response | No second request | `body_unknown` header; unknown body bytes = NA | No packet/body | None |
| Ambiguous or unsupported response | No second request | Respective header; unknown body bytes = NA | No packet/body; no union of alternate bodies | None |
| Capture admission | 0 | 0 (already downloaded) | +full packet bytes and marginal body-object bytes | S changes atomically after evictions |
| Body object | 0 | 0 at storage | Raw UTF-8 bytes, once per referenced object | While referenced |
| Body reference/hash | 0 | Not supplied in feed or response header | Entire hash field is charged inside every packet; no extra ref record | While packet retained |
| Eviction/rejection/attempt audit record | 0 | 0 | **Not** policy-retained metadata; evaluator-only diagnostic artifact | None in modeled payload ledger; audit disk/RSS reported separately |
| Discovery map, dirty queues, request-order counters, dedup index/refcounts, FIFO pointers | 0 | 0 | Implementation overhead, not additional serialized retained payload | Separate measured peak memory/counts/RSS, not S/M or payload byte-hours |

All these exclusions apply to every policy. Uncharged diagnostic data must be write-only to the collector and unavailable for evidence retention, rediscovery, prioritization, body restoration or post-eviction lookup. Audit records must not retain rejected/evicted response text as a free policy cache. A private immutable source/evaluator copy is not a feasible collector store.

The store need not persist implementation maps or object filenames. Body bytes and packet references define the logical retained representation; OS/database/file/index overhead is outside this model. Do not call S+M “total disk usage.” Report peak discovery-title count, pending-title/request count, retained-index entries, actual runtime/RSS and audit-file sizes separately. If physical-index overhead is studied later, apply the same preregistered sensitivity to all policies, never selectively charge P or exempt E.

**Unknown transfer totals:** always report exact metadata bytes and known-body-byte subtotal with count of NA payloads. If any NA payload exists, total downloaded bytes is NA (or an explicitly labeled known-byte lower bound), not that subtotal presented as complete. Missing/deleted is the only no-body modeled success-path absence with exactly zero payload. No missing-content size is inferred from a prior body. Requests remain exact even when bytes are NA.

## 2. Canonical serialization C(x)

For metadata, C(x) is the UTF-8 encoding of compact JSON followed by **exactly one LF byte 0a**:

- Sort object keys ascending by Unicode code point; fixed ASCII schema keys below. No duplicate/extra keys. No spaces: separators comma `,`, colon `:`. Charge all quotes, braces, commas, colons, array brackets and the final LF. No BOM, CRLF, indentation or trailing spaces.
- String escaping: quote → `\"`, backslash → `\\`; backspace/formfeed/LF/CR/tab → `\b`, `\f`, `\n`, `\r`, `\t`; other U+0000–001F → lowercase four-hex `\u00xx`. Other valid Unicode scalars appear literally, including `/`, non-ASCII and U+2028/U+2029. Reject lone surrogates. No Unicode normalization, case folding, slash escaping, URI decoding or newline conversion inside values.
- Timestamps are UTC strings **`YYYY-MM-DDTHH:MM:SS.ffffffZ`**, always six fractional digits, 27 ASCII bytes inside quotes. No offsets, omitted fractions, floats or leap seconds. Feed timestamp is selected event time, NOT publication/delivery time. Capture timestamp is response completion time. Use integer microseconds internally.
- Integers: nonnegative base-10 JSON integers, no sign, exponent, decimal point or leading zero except `0`. Booleans, if required in audit/fixture data, are `true`/`false`, not integers. Null is `null`. No NaN/Infinity. Normative feed/packet schemas have no nullable fields; NA diagnostic quantities use JSON null.
- Enums are exactly the lowercase ASCII strings specified below, never language enum reprs. Page keys are opaque, verbatim Unicode strings with ordinary JSON escaping. Hashes are 64 lowercase ASCII hex characters, no `sha256:` prefix.
- Arrays preserve their explicitly specified order; do not recursively sort every array. A feed response is sorted by `(event_time, page_key, action)` using Unicode code-point order, retaining multiplicity of identical records. This is **serialization, not historical chronology**. Equal-time incompatible notifications must be handled as a group. A directory contains unique page-key strings in Unicode code-point order. Capture JSONL is in admission/FIFO order.
- A metadata object's size is the encoded byte length **including LF**. A response array has one LF after its closing bracket and no per-element LF. A JSONL log concatenates C(record), without an outer array/header/footer. Empty response array is `[]` plus LF = **3 bytes**.

Equivalent standard-library spelling for permitted values: `json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8') + b'\n'`, subject to schema validation and the exact escapes/timestamps above. This is a serialization definition, not E08 implementation.

## 3. Collector-visible feed and directory

Feed record has **exactly three required, non-null fields**:

| Field | Type / canonical value | Visibility reason | Download / retain |
|---|---|---|---|
| `action` | JSON string `"live_change"` or `"delete"` | R04 allows normalized successful mutation action. Both held save and audited successful bodyless form_edit map to live_change; no body-availability bit. | Field/framing counted in response; full record retained in M |
| `event_time` | Quoted fixed-width UTC timestamp | R04 allows selected event timestamp after lag/delivery | Same |
| `page_key` | Quoted opaque key | Required for delivered-record discovery/addressing | Same |

No body/hash/revision ID/event ID, clock provenance, final state, family, annotation, criticality, future count or relation. Live-change notification conveys no historical body-fetch privilege. Deliver once per physical eligible mutation, not once per relation edge. No content dedup of feed records. Poll window/cursor is internal observer state; no cursor/count/header field is transmitted or retained. R04's lag and poll schedule remain unchanged.

Feed response = C(array of records). A nonempty batch of n records whose standalone C sizes are L1…Ln downloads **sum(Li)+2** bytes. Shared retained feed metadata grows by **sum(Li)**. An empty poll downloads 3, retains 0. This is intentional separation of array transfer framing from JSONL retention, not dropped accounting.

F directory response = C(array of current modeled live page keys, including BU titles), one assumed terminal directory request. No statuses, hashes or final export descriptors. Charge and retain the entire array once; no additional discovery record copies. Directory membership must follow the frozen state/realization model, not a union of uncertain titles or a final exported title list. Undefined/unsupported membership is review-required; do not fabricate a definite directory/cost. Archive enumeration is **not** this directory; a historical archive baseline still needs the separate archive contract.

## 4. Body responses and encoding

A modeled body response consists of two logical parts: **C({"outcome": value})** then, only for `body`, the raw canonical body byte string. No body JSON string wrapping, added LF, length field, encoding field, server-supplied hash or page key in the response header. The request context supplies the key. No modeled outgoing request/header/TLS/compression costs; requests are counted, not assigned invented historical wire overhead.

| Outcome string | Exact header length incl. LF | Canonical body payload |
|---|---:|---|
| body | 19 | Exact UTF-8 bytes; possibly zero for a genuinely known empty body |
| missing | 22 | 0 bytes; modeled deleted state only |
| unknown | 22 | NA, unavailable prehistory/state |
| body_unknown | 27 | NA, known live mutation without recoverable text |
| ambiguous | 24 | NA; no permissible-body union delivered |
| unsupported | 26 | NA; fail closed for review, not a invented response body |

Ambiguous/unsupported headers are modeled diagnostic outcomes, not assertions of historical HTTP status. E08 must not choose a trajectory on its own. In explicit later trajectory runs, each consistent realization pays for its own concrete response; do not count the diagnostic sentinel AND a concrete response for one attempt. A common byte-identical known-body outcome across all compatible alternatives may be returned without exposing source provenance; different text/state outcomes require the diagnostic/trajectory path. Bounds work must keep whole-trajectory consistency, not query-wise favorable choices.

Response completion reads E06's **current** modeled body, not triggering revision text. No hidden automatic retries: each attempt completes once; any later scheduled retry is a new charged attempt/sequence. Unsupported input before dispatch is a validation error with no network request; an unsupported state query after dispatch still costs the attempt and its diagnostic header. Completion after T cannot create retention at T; count its dispatch in requests by T, mark pending, and do not invent downloaded bytes before completion.

**Canonical body B = UTF-8 of the exact validated Unicode body string.** Source bytes/encoding/hash remain separate E05/evaluator provenance. This freezes canonical UTF-8 for BOTH modeled downloaded and stored body bytes; no mixing source lengths into download cost. No trimming, CRLF conversion, BOM removal, NFC normalization, semantic folding or terminal-newline insertion. Existing body newlines are real body bytes.

- ASCII: canonical bytes equal source ASCII bytes.
- UTF-8: canonical bytes equal the valid source UTF-8 representation of the same exact string.
- Latin-1: decode/validate through E05's source representation, then encode that Unicode string as UTF-8. Source byte `e9` for é becomes `c3 a9`, **2 canonical bytes**, not 1. Source hash is not the canonical-body hash.

Stored object is B alone: no object header/footer, length/encoding record or hash filename charge. Canonical encoding is fixed by contract and needs no per-object field. The hash is paid for in every retained packet as metadata. Exact zero-length body still requires a packet and a referenced object; unknown never becomes that object.

## 5. Retained capture packet

Only a successfully fetched known body can produce a capture packet. Every admitted successful response gets a separate packet, even when bytes/time/title repeat. Exact required schema, **no nullable/optional fields**:

| Field | Form | Purpose / byte charge |
|---|---|---|
| `body_sha256` | Quoted 64 lowercase hex SHA-256 of B | Locally computed content reference/integrity, charged with key/quotes/colon in every packet |
| `capture_time` | Quoted fixed-width UTC response timestamp | Actual acquisition time, not event/archive/write clock; full field charged |
| `page_key` | Quoted opaque requested key | Capture provenance available to collector; full field charged |
| `request_seq` | Positive JSON integer | Local sequence of body GET attempts, starts at 1 per policy run, increases at dispatch including failures; identifies fresh objects/captures and breaks same-time ties; full field charged |

No success outcome field: known-body success is implied by admission eligibility. No source request_time, revision ID, source hash/encoding, feed trigger, annotator, observer ID, policy name, latent episode or family. Local run configuration identifies the store; do not repeat it per packet. Dispatch/response times and outcome diagnostics can be audited privately; the minimal retained packet is not required to carry the request start time.

Packet = C(the four-field object), no outer capture-list framing. In dedup modes, `body_sha256` resolves the object (subject to byte-equality check); in non-dedup mode `(request_seq, body_sha256)` identifies that capture's private object. Both policies pay the exact same packet schema. Object addressing needs no extra serialized pointer. Scope request_seq to **body attempts only**, not feed polls, avoiding a hidden feed-frequency metadata penalty. Same sequence cannot be admitted twice; replaying an admission is an error, not a free duplicate capture.

## 6. Deduplication and FIFO admission

PD/PCD/E (and F as the exact-deduplicated final-only baseline) use the same dedup rule; P is deliberately non-deduplicated per the existing roster. F's choice is made before results to avoid a gratuitously weak final-only storage baseline. No change in F directory/GET access.

Hash B with SHA-256. Share an object iff **B is byte-for-byte equal**, using digest for lookup plus exact byte comparison. Hash collision with unequal bytes fails closed rather than merges evidence. Exact same Unicode string from UTF-8 versus Latin-1 sources deduplicates after canonical transcoding; merely semantically equivalent text, different normalization or line endings does not. Compute the hash from fetched bytes for all modes, never obtain a free hash through the feed. Repeated GETs download the full body; no 304/cache/conditional request convention.

Maintain packet references; evicting a packet decrements its object's count. Remove an object immediately when count reaches zero. No retained object at zero references, no resurrection from an evicted-object hash/index cache. Dedup indexes/refcounts are equally treated as implementation overhead (§1), while every serialized reference/hash is charged. Non-dedup allocates a fresh B copy for every admitted packet, even if hashes match globally.

Admission unit = **one packet plus any required body object**, ordered by `(response_time, request_seq, page_key)`; response_time dominates even if requests complete out of dispatch order. Existing FIFO order never changes on re-read. At each completed known-body response:

1. Compute packet bytes p, body bytes b. Download has already been charged.
2. **Intrinsic oversize test p+b > cap:** reject before any eviction, even if this body is currently shared. Log reason `oversize`, leave store unchanged. Uncapped mode never rejects on size. No truncation/split admission.
3. Otherwise calculate marginal size p+b for non-dedup, or p plus b iff no referenced equal B is currently retained for dedup.
4. If current S + marginal exceeds cap, evict the **oldest retained packet**. Charge freed packet bytes to metadata-evicted count; free/charge body bytes only at last reference. Recalculate marginal size from the remaining store after **each** eviction: the target body might have lost its last reference. Repeat until it fits.
5. Atomically install/reference B and append the packet. No provisional over-cap insertion. Record every intermediate post-eviction size and committed post-admission size. Peak S is the maximum initial/previous committed or actual post-operation retained size, **not the hypothetical oversized candidate sum**. Temporary response buffers are measured RAM overhead, not retained evidence.

Zero-cap store rejects all packets. A body rejection does not refund download/request cost, does not leave a stored packet, and never evicts existing evidence. Same-time admissions are sequential in the ordering above, not jointly optimized. No future information, semantics, recency refresh of old packets or importance enters eviction.

Byte-hours for S and M: accumulate exact integer byte-microseconds over half-open intervals between operations, then divide by **3,600,000,000** for reporting hours. Use each post-operation retained size until next timestamp; same-time intermediate operations have zero duration but count for peak. Integrate to T only. Final S/M at T include allowed terminal operations, even when their duration at T is zero. Retaining F's directory at T thus affects peak/final, not byte-hours before T.

## 7. Diagnostics, fairness and limits

Attempt/rejection/eviction diagnostics must identify at least body request_seq, requested key, local dispatch/completion times (null if pending), outcome, header byte count, canonical body length (null if unavailable), admission disposition (`admitted`, `oversize`, `no_body`, `pending`, `review_required`) and evicted request_seq list in FIFO order. These are **evaluator-only audit facts**, not additional collector-retained evidence or download payload. Log explicit ambiguity/unsupported reasons privately without leaking trajectories to policies. Their file serialization may use C, but their file sizes are separate experiment-artifact costs, not S/M. The fixture manifests below are also test descriptions, not charged collector records.

| Red-team question | Frozen answer / remaining limitation |
|---|---|
| Does periodic get artificially large metadata? | Identical four fields and encoding for all policies, including P. P's fresh copies are its preregistered distinction, not extra packet fields; PD/PCD are required controls. Variable-width request_seq costs grow with actual attempts for every policy; no policy-specific ID width. |
| Does dedup receive free references? | No, full 64-character hash and request provenance in every packet; repeated captures never vanish. Index machine overhead excluded for everyone and reported separately. |
| Does E avoid attempts, failures or body transfers that P pays? | No. Same feed and GET protocol; duplicates transfer fully; all dispatched attempts count, including missing/unknown/oversize. Rate is not retuned. |
| Are feed costs shared? | Same physical records, poll epoch/lag and array framing; empty polls charged; identical JSONL history charge P/PD/PCD/E. F is explicitly different with charged terminal directory, not an equal-discovery contrast. |
| Are discovery costs hidden? | Discovery payloads are paid in transfer and M; auxiliary maps/queues measured separately for all, no final title-list preload. |
| Are hashes/indexes free selectively? | Hash generated locally only after GET for every policy; packet pays reference. No server/trigger hash. Index overhead exclusion is uniform, not a zero-memory claim. |
| Can these choices change the headline materially? | Yes: packet-heavy small-body traces, FIFO, UTF-8 transcoding and unbounded shared feed history can matter. Publish S/M/body/packet/download components and PCD comparison, not just body-only bytes. Retain frozen grid and nulls; physical-overhead sensitivity requires a separate outcome-blind amendment. |
| Are unknown bytes silently favorable? | No: request counts exact, downloaded-byte totals NA/lower bounds when incomplete; no exact-byte matching claim from a subtotal. Ambiguity is not a free multi-body read or policy-specific exclusion. |

No policy-dependent exception remains besides preregistered P non-dedup and F's separate access model; F's exact-dedup choice above is explicit. Unanswered historical wire/encoding/latency questions cannot change these hypothetical accounting bytes. Actual HTTP/archive availability, physical-memory comparability and missing payload sizes remain limitations, not a reason to invent favorable costs.

## 8. Frozen fixtures and independent gate

`tests/fixtures/accounting/README.md` and **nine data-only cases A–I** define literal serialized strings/hex bytes and hand arithmetic. Author-side local checks completed: **9/9 PASS**, with no count mismatches. They reserialized all literal metadata, counted UTF-8 bytes including LF/framing, verified source transcoding/body hashes and directly recalculated retained/download/FIFO/byte-hour totals. No `ebe` imports or saved implementation helper was used. These checks are **not** independent Sam/Aaron verification. No future E08 implementation may generate expected totals or “fix” them to agree with itself.

**Required before E08 implementation:** Sam or Aaron independently reconstructs the serialized streams and component totals from this specification (no `ebe` imports, no future E08 code, no reused author counting helper), checks hashes/source transcoding/framing/FIFO/byte-hours and the policy-neutrality table, and records named acceptance with fixture-file hashes and amendment hash in `audit/R04_ACCOUNTING_VERIFICATION.md`. Resolve any disagreement before authorization; preserve a versioned correction log if a fixture changes. No signatures or independent PASS are asserted by this pass.

Once that acceptance records all nine cases as matched and no policy-advantaging ambiguity remains, update `PROJECT_STATUS.md` explicitly to **E08 AUTHORIZED** for observer/storage only. Until then **E08 STILL BLOCKED**. Evidence scoring, collectors and archive-aware implementation retain their own ticket gates. The present remaining accounting blocker is independent acceptance, not missing field definitions.
