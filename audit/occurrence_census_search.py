"""Whole-DSE exact-match occurrence census search (X13_RUN_CONTRACT.md SS4 item D).

Read-only analysis: for every proposition's recorded source_spans quote text,
searches the ENTIRE DSE revision corpus (14,591 revisions, not just already-
recorded occurrences) for byte-exact substring matches, and reports any
revision containing an exact match that is NOT already present in
occurrences.jsonl.

This performs only the FIRST step the contract requires ("exact/multi-span...
candidate search"). It deliberately does NOT perform normalized/near-copy
search or auto-accept anything requiring semantic judgment about equivalence
-- those need human review. Exact byte-identical substring matches are
reported here as high-confidence candidates; whether to add them to
occurrences.jsonl is a decision made after reviewing this report, not by
this script silently writing to annotation files.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

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

already_recorded: set[tuple[str, str, int, int]] = {
    (o["evidence_id"], o["rev_id"], o["char_span"][0], o["char_span"][1]) for o in occurrences
}

total_new_candidates = 0
report: list[dict] = []

for prop in evidence:
    for span in prop["source_spans"]:
        quote = span["quote"]
        if len(quote) < 12:
            continue  # too short a substring risks spurious matches; skip trivial fragments
        matches_by_rev: list[tuple[str, int, int]] = []
        for rev_id, rev in revs.items():
            body = rev["body"]
            start = 0
            while True:
                idx = body.find(quote, start)
                if idx == -1:
                    break
                matches_by_rev.append((rev_id, idx, idx + len(quote)))
                start = idx + 1
        new_here = [
            (rev_id, s, e) for (rev_id, s, e) in matches_by_rev
            if (prop["evidence_id"], rev_id, s, e) not in already_recorded
        ]
        if new_here:
            total_new_candidates += len(new_here)
            report.append({
                "evidence_id": prop["evidence_id"],
                "quote_preview": quote[:60],
                "anchor_rev_id": prop["rev_id"],
                "new_candidates": [
                    {"rev_id": r, "page_key": revs[r]["page_key"], "char_span": [s, e],
                     "same_page_as_anchor": revs[r]["page_key"] == prop.get("rev_id", "").split("@")[0],
                     "is_anchor_revision": r == prop["rev_id"]}
                    for r, s, e in new_here
                ],
            })

print(f"Propositions with new exact-match candidates: {len(report)}")
print(f"Total new candidate occurrences found: {total_new_candidates}")
print()
for item in report:
    print(f"=== {item['evidence_id']} ({item['quote_preview']!r}...) ===")
    print(f"  anchor rev_id: {item['anchor_rev_id']}")
    for cand in item["new_candidates"]:
        tag = "ANCHOR-REVISION-ITSELF" if cand["is_anchor_revision"] else (
            "SAME-PAGE" if cand["same_page_as_anchor"] else "CROSS-TITLE"
        )
        print(f"    [{tag}] rev_id={cand['rev_id']} page_key={cand['page_key']} char_span={cand['char_span']}")

out_path = ROOT / "audit" / "occurrence_census_candidates.json"
out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nFull machine-readable report written to {out_path.relative_to(ROOT)}")
