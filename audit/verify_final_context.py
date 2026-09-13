"""Data-only context census/validation. Never imports collectors or evaluator.
--generate creates the new exact context occurrence census before the freeze.
Default verifies it byte-for-byte against the frozen rule. No network access.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
def rows(path):
    return [json.loads(s) for s in (ROOT / path).read_text(encoding="utf-8").splitlines() if s.strip()]

revisions = rows("data/raw/export/revisions.jsonl")
by_rev = {r["rev_id"]: r for r in revisions}
fragments = rows("annotations/context_fragments.jsonl")
eligibility = rows("annotations/context_eligibility.jsonl")
events = {e["event_id"]: e for e in rows("data/raw/export/events.jsonl")}
assert len(eligibility) == 65 and len(fragments) == 10
assert sum(e["context_needed"] for e in eligibility) == 8
assert {e["evidence_id"] for e in eligibility} == {e["evidence_id"] for e in rows("annotations/evidence.jsonl")}
ids = {f["context_fragment_id"] for f in fragments}
assert len(ids) == len(fragments)
assert {i for e in eligibility for i in e["context_fragment_ids"]} == ids
output = []
for f in fragments:
    if f.get("context_rev_id"):
        r = by_rev[f["context_rev_id"]]
        raw = r["body"].encode("latin-1")
        text = raw.decode(r["body_encoding"])
        a, b = f["char_span"]
        assert text[a:b] == f["quotation"]
        assert hashlib.sha256(raw).hexdigest() == f["body_sha256"] == r["body_sha256"]
        # Exhaustive DSE exact search; no normalization-based automatic support.
        for candidate in sorted(revisions, key=lambda r: r["rev_id"]):
            if not candidate["page_key"].startswith("dse~") or not isinstance(candidate.get("body"), str):
                continue
            raw = candidate["body"].encode("latin-1")
            text = raw.decode(candidate["body_encoding"])
            start = text.find(f["quotation"])
            if start < 0:
                continue
            # The full-corpus census finds only same-page carryforwards for
            # these eight accepted quotations. New cross-page hits fail review.
            assert candidate["page_key"] == r["page_key"], candidate["rev_id"]
            assert hashlib.sha256(raw).hexdigest() == candidate["body_sha256"]
            end = start + len(f["quotation"])
            codec = candidate["body_encoding"]
            source_span = [len(text[:start].encode(codec)), len(text[:end].encode(codec))]
            output.append(dict(context_fragment_id=f["context_fragment_id"], rev_id=candidate["rev_id"],
                page_key=candidate["page_key"], event_time=candidate["time"],
                source_body_sha256=candidate["body_sha256"], canonical_body_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
                canonical_char_span=[start, end], source_projection_span=source_span))
    else:
        event = events[f["context_event_id"]]
        predicate = f["event_predicate"]
        assert predicate == dict(page_key=event["page_key"], action="delete",
            event_time=event["time"].replace("Z", ".000000Z"), minimum_multiplicity=1)
        assert event["event_type"] == "delete" and event["success_observed"] is True
serialized = "".join(json.dumps(o, ensure_ascii=True, sort_keys=True) + "\n" for o in output)
path = ROOT / "annotations/context_occurrences.jsonl"
if "--generate" in sys.argv:
    if path.exists():
        raise RuntimeError("Refusing to overwrite a frozen census")
    path.write_text(serialized, encoding="utf-8", newline="\n")
else:
    assert path.read_text(encoding="utf-8") == serialized
print(f"PASS: 65 context dispositions, 10 fragments, {len(output)} exact body context occurrences; no policy scoring")
