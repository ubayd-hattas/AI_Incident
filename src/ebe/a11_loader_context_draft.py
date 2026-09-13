"""DRAFT context-axis loader -- Sam's independent attempt, NOT accepted ground truth.

This is explicitly a comparison artifact: an independent attempt at the harder,
judgment-dependent half of acceptance-matrix items C (context fragments) and E
(context-eligibility), produced so it can be compared against whatever
Alex/Aaron/Jaswin produce, not to replace their adjudication. See
docs/A11_CONTEXT_AXIS_DRAFT_SAM.md for full methodology, disagreements found
against the independently-produced acceptance matrix, and known limitations.

Wires annotations/context_fragments_DRAFT_SAM.jsonl and
annotations/context_eligibility_DRAFT_SAM.jsonl into src/ebe/a11_loader.py's
otherwise-unchanged core loader. Never run through compute_core_coverage/
compute_context_coverage/compute_delay against real collector output in this
codebase -- that would be real semantic scoring, still not authorized.
"""
from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from .a11_loader import load_real_propositions
from .evaluator import Fragment

REPO_ROOT = Path(__file__).resolve().parents[2]


def load_draft_context(
    context_fragments_path: Path | None = None,
    context_eligibility_path: Path | None = None,
):
    """Returns (propositions, fragments_by_id) with DRAFT context wired in on
    top of the real core data. `propositions` carry Sam's draft
    context_alternatives; core alternatives/eligibility are unchanged from
    `load_real_propositions`. Context-eligibility from the draft file is
    exposed as a plain dict alongside (not merged into core `eligible`,
    which stays core-only per docs/E12_SUBSTRATE.md's original scope)."""

    context_fragments_path = context_fragments_path or REPO_ROOT / "annotations" / "context_fragments_DRAFT_SAM.jsonl"
    context_eligibility_path = context_eligibility_path or REPO_ROOT / "annotations" / "context_eligibility_DRAFT_SAM.jsonl"

    propositions, fragments_by_id = load_real_propositions()

    with open(context_fragments_path, encoding="utf-8") as f:
        context_rows = {row["evidence_id"]: row for row in (json.loads(line) for line in f if line.strip())}
    with open(context_eligibility_path, encoding="utf-8") as f:
        context_eligibility = {row["evidence_id"]: row for row in (json.loads(line) for line in f if line.strip())}

    updated: list = []
    for prop in propositions:
        row = context_rows.get(prop.evidence_id)
        if row is None:
            updated.append(prop)
            continue
        fragment_ids: list[str] = []
        for frag_row in row["context_fragments"]:
            fragment_id = frag_row["fragment_id"]
            if frag_row["kind"] == "body_span":
                fragments_by_id[fragment_id] = Fragment(
                    fragment_id=fragment_id,
                    page_key=frag_row["page_key"],
                    kind="body_span",
                    required_substring=frag_row["required_substring"].encode("utf-8"),
                )
            else:
                fragments_by_id[fragment_id] = Fragment(
                    fragment_id=fragment_id,
                    page_key=frag_row["page_key"],
                    kind="observable_feed",
                    feed_action=frag_row["feed_action"],
                )
            fragment_ids.append(fragment_id)
        updated.append(replace(prop, context_alternatives=(tuple(fragment_ids),)))

    return tuple(updated), fragments_by_id, context_eligibility


__all__ = ["load_draft_context"]
