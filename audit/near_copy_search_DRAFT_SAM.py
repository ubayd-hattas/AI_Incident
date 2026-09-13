"""DRAFT normalized (whitespace/case-insensitive) near-copy search -- one step
more permissive than audit/occurrence_census_search.py's byte-exact search,
still objective (no semantic/paraphrase judgment). Part of Sam's independent
context-axis draft; see docs/A11_CONTEXT_AXIS_DRAFT_SAM.md for the one finding
and its recommended (non-final) disposition. Read-only: writes nothing.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def main() -> int:
    revs: dict[str, dict] = {}
    with open(ROOT / "data" / "raw" / "export" / "revisions.jsonl", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                revs[r["rev_id"]] = r

    with open(ROOT / "annotations" / "evidence.jsonl", encoding="utf-8") as f:
        evidence = [json.loads(line) for line in f if line.strip()]
    with open(ROOT / "annotations" / "occurrences.jsonl", encoding="utf-8") as f:
        occurrences = [json.loads(line) for line in f if line.strip()]

    already_recorded: dict[str, set[str]] = {}
    for occ in occurrences:
        already_recorded.setdefault(occ["evidence_id"], set()).add(occ["rev_id"])

    found_any = False
    for prop in evidence:
        for span in prop["source_spans"]:
            quote_norm = normalize(span["quote"])
            if len(quote_norm) < 20:
                continue
            for rev_id, rev in revs.items():
                if rev_id in already_recorded.get(prop["evidence_id"], set()):
                    continue
                if quote_norm in normalize(rev["body"]):
                    print(f"{prop['evidence_id']} -> normalized match in {rev_id} (page_key={rev['page_key']}, not in exact-match census)")
                    found_any = True
    if not found_any:
        print("No additional normalized-match candidates found beyond the exact-match census.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
