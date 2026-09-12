# E05 typed loader summary

Status: implemented and verified against the pinned 2026-09-03 Collusion Wiki core export.

## Public interface

```python
from ebe import load_export

export = load_export("data/raw/export")
```

`export.pages`, `export.revisions`, `export.events`, and `export.labels` are immutable,
deterministically ordered tuples. `export.manifest` is the typed manifest record. Exact-ID
lookup maps are available as `pages_by_id`, `pages_by_key`, `revisions_by_id`,
`events_by_id`, and `labels_by_label`.

## Types and normalization

`schema.py` defines `PageRecord`, `RevisionRecord`, `EventRecord`, `LabelRecord`,
`ManifestRecord`, source locations, lossless timestamp wrappers, declared body encodings,
and relation records. Every row retains an independent copy of its raw JSON object plus its
source file, row number, and identifier.

All source clocks remain separate `SourceTimestamp` fields. Each retains the original string
and a timezone-aware UTC `datetime`. Null remains null; event-field absence remains visible in
`present_fields`; `uncertainty_seconds` is retained as a scalar without an interval convention.

Relation fields retain their original absent/null/scalar/list form and also expose aligned,
iterable `RelationEdge` tuples. A round ID without a relation type and related event produces
no edge. Edges are references, not mutations.

Revision bodies retain the JSON string and reconstructed source bytes separately. The loader
verifies the Latin-1 byte projection, declared ASCII/UTF-8/Latin-1 classification, source byte
length, and SHA-256. It performs no content execution or URL access.

## Validation guarantees

The default load verifies all five pinned expanded-file hashes and four JSONL row counts,
strict top-level row schemas and required value types, unique page/page-key/revision/event/label
IDs, revision-to-page identity, declared page revision counts, one-to-one save/revision links,
event/page identity, `page_held`, relation mirrors, and relation targets. Failures identify the
source file and row/identifier where available.

`verify_pinned=False` exists only to load small synthetic fixtures. It disables fixed hashes and
fixed row totals, but leaves schema, body, uniqueness, and linkage checks enabled.

## Semantics deliberately not encoded

There is no historical state reconstruction, clock priority, page episode, body carry-forward,
deletion-survival rule, archive-accessibility rule, agent inference from labels/IP prefixes,
collector, polling, evidence score, policy simulation, or figure logic. In particular, exported
`revert` records are typed as body-unknown successful `form_edit` observations and never as
restoration of an earlier body. Page-family fields and retrospective relationships remain source
provenance/evaluator data.
