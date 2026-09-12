# E06 conditional released-trace timeline engine

## Status and scope

The engine implements the frozen E06 state and timing contract over E05's validated,
immutable records. Its answers are **conditional released-trace states**, not claims
about exact historical DSEWiki HTTP responses. It is entirely offline and contains no
collector, polling, storage-budget, evidence-label, scoring, policy, figure, or
experiment code.

Full E06 certification remains conditional under the repository's authoritative
documents: V02 packets 04 and 08 are held back, and packets 09/10 lack the required
independent comparison. The six released manual packets are implemented and tested.

## API

```python
from datetime import datetime, timezone
from ebe import TraceModel, load_export

export = load_export("data/raw/export")
model = TraceModel(export)
query = model.state_at(
    "dse~AgentLinkma21JuneAA",
    datetime(2026, 6, 18, 18, 26, 23, tzinfo=timezone.utc),
)
```

`TraceModel.timeline(page_key)` returns a page-specific `PageTimeline` with the same
`state_at(timestamp, mode=...)` query and inspectable transition/no-op provenance.
Page keys are exact opaque strings. Timestamps must be timezone-aware UTC datetimes;
queries before `2026-05-24T00:00:00Z` or after `2026-07-15T00:00:00Z` fail explicitly.

## State representation

Each `StateAlternative.state` is exactly one of:

- `unknown`, with no body reference;
- `live_body_ref`, with a `BodyReference` resolving to the exact E05 revision ID,
  source bytes/encoding, SHA-256, body string, and source location;
- `live_body_unknown`, with no body or hash;
- `deleted`, with no body or hash.

Ambiguity is not a fifth state. `StateQuery.alternatives` contains every admissible
state/trajectory pair and preserves distinct provenance paths even when they converge
to the same physical state. A stable trajectory handle records applied events, pending
events, and ordering choices for later evaluator consistency.

## Transition rules

- A validated held save installs its full immutable revision body.
- A successful deletion installs `deleted` and ends a current modeled live episode.
  Repeated deletion is allowed and does not invent an episode.
- Each of the four audited successful bodyless `form_edit` records installs
  `live_body_unknown`, clearing any previous body.
- A supported live mutation after deletion begins a new episode. Ordinary live edits
  remain in their current episode.
- State carries to the next supported mutation or censoring only under the explicit
  `no-unobserved-intervening-mutation` released-trace assumption.
- Initial state is unknown. A first held `seq=1` revision never proves prior absence or
  first-ever creation.

Episode IDs are opaque and prefix-stable (`episode:<supported-start-event-id>`). Query
alternatives expose current and last-ended episode IDs. At the terminal checkpoint,
ongoing live/body-unknown episodes are right-censored; post-deletion observation is
also marked limited by the endpoint. Initial prehistory remains left-censored.

## Timestamp and ambiguity semantics

Nominal mode uses selected exported `time`. Events at a boundary are applied before a
read at that boundary, producing half-open `[start,end)` state intervals. All events at
one selected timestamp form an atomic group. Every source-permitted ordering is
applied; event IDs are used only to serialize output, never as historical chronology.

Uncertainty mode uses the separately labeled project convention that each mutation
may occur anywhere in its closed `[time-u,time+u]` interval. It is not a confidence
interval or measured clock-error guarantee. Non-overlapping windows force order;
overlapping or touching windows admit feasible event sets and orders. At a lower
endpoint predecessor and successor may both be possible; at the upper endpoint an
isolated mutation has occurred. If complete enumeration exceeds the configured
resource limit, the engine raises `AmbiguityLimitError` instead of pruning or choosing
a winner.

## Provenance and non-effects

Every applied transition records source event ID/location, revision ID/location when
present, body hash when present, selected time and uncertainty window, transition type,
model classification, and relation edges. Relation effect is explicitly `none`.

Revision archival clocks are available as `PageTimeline.ignored_markers`; they are
inspectable no-ops. Relation/copy metadata, archival clocks, final page descriptors,
page-family fields, future revisions, labels, and aggregate counts never create or
backdate state transitions.

## Verification fixtures

The released fixture file is `tests/fixtures/manual/released_v02.json`. Tests cover all
76 published mutation rows in V02 packets 01, 02, 03, 05, 06, and 07, including every
before/at/after boundary, exact revision body reference/hash/bytes, archive no-ops,
deletion/recreation episodes, unknown prehistory, the PoliceBridge body-unknown state,
and AgentOfficialDirectQueryAA3's uncertainty endpoints.

Public diagnostics cover `AI`, the `AgentNacoPovertyTexas2015XQ` same-time tie and
later convergence, and the right-censored `AgentBridgeOct2142X` control. These are not
reported as independently accepted manual packets. Blind packets 04
(`AgentProxyCountyNext987111`) and 08 (`OAIEquityDec30Raw` /
`OECDJun26PrecisionScout`) were deliberately not consumed or transcribed.

Synthetic tests isolate save, delete, delete-to-save, body-unknown invalidation,
replacement after body-unknown, repeated deletion, save/save and save/delete ties,
identical-body provenance, touching uncertainty windows, later convergence, opaque
keys, horizon errors, relation non-effects, unsupported-action failure, missing
prehistory, and nominal/uncertainty future-suffix invariance.

## Deliberately not modeled

The engine does not infer exact public visibility, native archive availability,
historical creation, missing mutations, publisher-calibrated clock uncertainty,
directory membership, copy equivalence, retrospective recreation timing, semantic
evidence, or policy behavior. Unknown is never converted to deletion, a missing body is
never treated as empty, and a bodyless mutation never carries the old body forward.
