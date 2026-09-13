"""Loader: real A11 annotation files -> src/ebe/evaluator.py's Proposition/Fragment types.

Scope discipline: this module performs ONLY mechanical reshaping of data
Alex/Aaron/Jaswin already authored (source_spans, occurrences, eligibility
dispositions). It invents no new semantic content:

- One body_span Fragment per recorded `source_spans` entry, on the
  proposition's own anchor page_key. This is a direct, lossless reshaping of
  already-authored spans into the OR-of-AND algebra src/ebe/evaluator.py
  expects -- not a new judgment about what the fragments are.
- `core_alternatives` is a single alternative requiring ALL of a
  proposition's span-fragments together (multi-span propositions require
  every disjoint span, per X13_RUN_CONTRACT.md SS4).
- `context_alternatives` is deliberately left empty: no typed context
  fragments exist yet (acceptance-matrix item C's context half is still
  unaddressed). Context coverage against real data is therefore not yet
  meaningful and callers must not treat an empty context result as "no
  context exists" -- it means "not modeled yet".
- `eligible`/`eligibility_reason` come directly from `annotations/eligibility.jsonl`
  (core eligibility only -- unknown-prehistory/BU/head-mismatch/unsupported-
  linkage/ambiguous-state checks; context eligibility is not assessed there
  either, for the same reason).

What this does NOT do, on purpose:
- No cross-title or near-copy alternative fragments beyond what
  `audit/occurrence_census_search.py` found as exact byte-identical matches
  (none were found across page boundaries for the current 65 propositions,
  so this is a no-op today, not a silent omission).
- No whole-DSE occurrence search is re-run here; it reads the existing,
  already-verified `occurrences.jsonl`.
"""
from __future__ import annotations

import json
from pathlib import Path

from .evaluator import Fragment, Proposition

REPO_ROOT = Path(__file__).resolve().parents[2]


def load_real_propositions(
    evidence_path: Path | None = None,
    eligibility_path: Path | None = None,
) -> tuple[tuple[Proposition, ...], dict[str, Fragment]]:
    """Returns (propositions, fragments_by_id) built from the real, currently
    accepted A11 annotation files. Does not read occurrences.jsonl directly --
    cross-page alternatives from the occurrence census are not yet wired in
    because none exist for the current 65 propositions (see module docstring).
    """

    evidence_path = evidence_path or REPO_ROOT / "annotations" / "evidence.jsonl"
    eligibility_path = eligibility_path or REPO_ROOT / "annotations" / "eligibility.jsonl"

    with open(evidence_path, encoding="utf-8") as f:
        evidence_rows = [json.loads(line) for line in f if line.strip()]
    with open(eligibility_path, encoding="utf-8") as f:
        eligibility_rows = {
            row["evidence_id"]: row for row in (json.loads(line) for line in f if line.strip())
        }

    fragments_by_id: dict[str, Fragment] = {}
    propositions: list[Proposition] = []

    for row in evidence_rows:
        evidence_id = row["evidence_id"]
        page_key = row["rev_id"].split("@")[0]
        fragment_ids: list[str] = []
        for i, span in enumerate(row["source_spans"]):
            fragment_id = f"{evidence_id}-frag-{i}"
            fragments_by_id[fragment_id] = Fragment(
                fragment_id=fragment_id,
                page_key=page_key,
                kind="body_span",
                required_substring=span["quote"].encode("utf-8"),
            )
            fragment_ids.append(fragment_id)

        elig = eligibility_rows.get(evidence_id)
        if elig is None:
            raise ValueError(f"{evidence_id}: no eligibility disposition recorded")

        propositions.append(Proposition(
            evidence_id=evidence_id,
            critical=row["critical"],
            core_alternatives=(tuple(fragment_ids),),
            context_alternatives=(),  # not yet modeled -- see module docstring
            eligible=elig["eligible"],
            eligibility_reason=elig["reason"],
        ))

    return tuple(propositions), fragments_by_id


__all__ = ["load_real_propositions"]
