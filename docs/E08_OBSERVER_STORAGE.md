# E08 modeled observer and deterministic storage

## Scope

E08 provides the neutral interface and retained-payload primitives shared by later
collection policies. It is a **modeled monitored-wiki interface**, not a reconstruction
of the exact historical DSEWiki HTTP/API behaviour. It implements no periodic,
changed-only, event-derived, evidence-scoring, annotation, coverage, sweep, or plotting
logic.

The dependency boundary is:

```text
private E06 TraceModel -> Observer -> future collectors -> CaptureStore
```

Collectors receive sanitized observer values. They do not receive `TraceModel`,
`StateQuery`, revision identifiers, source provenance, relation fields, annotations, or
the export's final title list.

## Observer interface

`Observer(export, config=ObserverConfig())` owns the private E06 model. Frozen defaults
are a 5-second feed publication lag, a 60-second UTC schedule from t0, and zero GET
response delay. Configuration values are nonnegative integer microseconds so later
pre-authorized sensitivity runs can select 5/30-second response delay or 30/60-second
publication lag without floating-point timestamps.

`poll_feed(poll_time)` accepts only epoch-aligned common feed times and delivers every
previously-undelivered physical mutation whose selected event time plus publication lag
is at or before that poll. Batch serialization order is `(event_time, page_key, action)`;
same-time ordering is not treated as source chronology. A record contains exactly:

- `action`: `live_change` or `delete`;
- `event_time`: selected event time in fixed six-digit UTC form;
- `page_key`: the opaque visible title key.

Save and audited bodyless form-edit records both become `live_change`. Probes do not
appear. Records contain no body/hash/revision/event ID, relation, final-state flag,
family, label, criticality, evidence identifier, future count, or future copy.

Delivered records are the sole continuous-observer discovery mechanism. The observer
starts with an empty discovered-title set. A GET for an undiscovered key receives the
same frozen `unknown` payload as unavailable prehistory; it cannot use a guessed future
key to bypass discovery.

`terminal_directory()` is the separate F-compatible primitive and is available only at
T on an observer that has not used the continuous feed. It derives unique current-live
membership from modeled states, includes body-unknown live titles, and fails if
membership is ambiguous. It never consults `pages.jsonl` final-state fields.

## GET semantics and outcomes

`get_body(page_key, request_time)` increments the body-attempt sequence at dispatch.
The response reads E06 state at `request_time + get_response_delay`, never at the feed
event time. Consequently an overwritten trigger returns the replacement current at
response time, and a deleted trigger returns no archived body. Responses completing
after T remain pending and download nothing by T.

The six serialized outcomes are exactly `body`, `missing`, `unknown`, `body_unknown`,
`ambiguous`, and `unsupported`. Only `body` carries raw canonical UTF-8 bytes. Missing
has a known zero-byte body payload; unknown, body-unknown, ambiguous, and unsupported
have unknown/NA payload size rather than a fabricated zero. If all E06 alternatives
produce the same byte-identical body/outcome, that common response can be returned
without provenance; otherwise the result is `ambiguous` and exposes no body union.

The canonical body is the exact validated source byte string decoded according to its
E05 encoding and re-encoded as UTF-8. No trimming, normalization, newline conversion,
or terminal newline is introduced. This is a modeled payload encoding and not an
assertion about historical transfer encoding.

## Accounting

Canonical metadata is compact sorted-key JSON, literal Unicode (`ensure_ascii=false`),
no spaces, and exactly one trailing LF. Timestamps always have six fractional digits.
Feed and directory downloads include array framing; retained feed metadata is standalone
JSONL records without retained response-array framing. Response headers are
`{"outcome":"..."}` plus LF. Modeled outgoing requests, TLS, compression, and exact HTTP
wire overhead are deliberately not invented.

Observer accounting keeps request counts, downloaded metadata, downloaded known-body
bytes, unknown-body attempt count, retained shared metadata M, peak/final M, and exact
integer byte-microseconds. If any completed response has an NA body length, total
downloaded bytes is NA and the exact known-byte subtotal is reported as a lower bound.
Evaluator-only audit facts are outside M and cannot restore or prioritize content.

## Capture storage

`Capture(page_key, capture_time, request_seq, body)` represents one successful known
body response. `CaptureStore(capacity_bytes, deduplicate=...)` selects one run-wide
neutral storage mode. `capacity_bytes=None` is the explicit uncapped diagnostic.
`admit(capture)` constructs the exact four-field packet:

- SHA-256 of canonical body bytes;
- response/capture time;
- opaque page key;
- positive body-attempt sequence.

Every capture pays the complete packet, including its hash reference. Deduplicated mode
shares only byte-for-byte equal canonical bodies after hash and equality verification.
Non-deduplicated mode allocates a fresh body object for every admitted packet. Repeated
deduplicated content still produces a separately charged packet.

Admission order is `(response_time, request_seq, page_key)`. A standalone packet plus
body larger than the cap is rejected before eviction; bodies are never truncated.
Otherwise the oldest packets are evicted until the true recomputed marginal cost fits.
A shared object survives while any retained packet references it and is removed
immediately after its last reference disappears. There is no zero-reference body cache,
resurrection cache, recency refresh, semantic compression, annotation-aware eviction,
or policy-specific retention rule.

Storage snapshots report packet/body components, objects/refcounts, retained sequences,
current/peak/final bytes, evicted packet/body bytes, oversize count, and exact
byte-microseconds (with a byte-hours convenience value). Hypothetical candidate sizes
never inflate peak bytes. Implementation indexes and diagnostics are outside modeled S
and must be measured separately in later authorized experiment work.

## Future-information protections and limitations

The private feed index may contain the released trace, but only lag-eligible prefix
records can cross the observer boundary. GET queries are discovery-gated and performed
at response time. Prefix-equivalent traces therefore produce identical observations and
costs through their common prefix. Retrospective source descriptors, archive clocks,
relations, page families, labels, and future revisions never influence visible records.

E08 models neither archives nor retries, cache validators, historical availability,
missing-mutation probabilities, physical storage overhead, or semantic evidence. Those
questions require separate frozen contracts and cannot be inferred from this layer.
