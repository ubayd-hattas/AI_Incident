import json
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
rev_file = ROOT / "data" / "data" / "raw" / "export" / "revisions.jsonl"
ev_file = ROOT / "annotations" / "evidence.jsonl"

revs = {}
with open(rev_file, "r", encoding="utf-8") as f:
    for line in f:
        r = json.loads(line)
        revs[r["rev_id"]] = r

with open(ev_file, "r", encoding="utf-8") as f:
    evidence = [json.loads(line) for line in f if line.strip()]

all_pass = True
for ev in evidence:
    eid = ev["evidence_id"]
    rev_id = ev["rev_id"]
    if rev_id not in revs:
        print(f"FAIL: {eid} {rev_id} not found in revisions")
        all_pass = False
        continue
    rev = revs[rev_id]
    body = rev["body"]
    enc = rev.get("body_encoding", "ascii")
    body_bytes = body.encode("latin-1") if enc == "latin-1" else body.encode("utf-8")
    b_hash = hashlib.sha256(body_bytes).hexdigest()
    hash_match = (b_hash == ev["source_body_hash"])
    
    spans_ok = True
    for s in ev["source_spans"]:
        start, end = s["start"], s["end"]
        actual = body[start:end]
        if actual != s["quote"]:
            spans_ok = False
            all_pass = False
            print(f"MISMATCH in {eid}: expected {repr(s['quote'][:25])}, got {repr(actual[:25])}")
            
    status = ev["claim_status"]
    print(f"{eid:18} | hash: {hash_match} | spans: {spans_ok} | status: {status}")

print(f"OVERALL VERIFICATION SUCCESS: {all_pass}")
