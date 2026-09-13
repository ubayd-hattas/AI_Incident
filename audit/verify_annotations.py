import json
import hashlib
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Was "data" / "data" / "raw" / "export" -- a doubled, git-untracked path that only
# "worked" on a machine with a stale leftover directory (see
# audit/SAM_RESPONSE_TO_PRE_RESULTS_AUDIT.md). data/ is never git-tracked (clean-room
# download recipe in sources/README.md); the correct, single-nested path is below.
rev_file = ROOT / "data" / "raw" / "export" / "revisions.jsonl"
ev_file = ROOT / "annotations" / "evidence.jsonl"
occ_file = ROOT / "annotations" / "occurrences.jsonl"
splits_file = ROOT / "annotations" / "splits.json"
adj_file = ROOT / "annotations" / "adjudication.csv"

print("--- 1. Loading revisions ---")
revs = {}
with open(rev_file, "r", encoding="utf-8") as f:
    for line in f:
        r = json.loads(line)
        revs[r["rev_id"]] = r

all_pass = True

print("\n--- 2. Verifying evidence.jsonl (65 propositions) ---")
with open(ev_file, "r", encoding="utf-8") as f:
    evidence = [json.loads(line) for line in f if line.strip()]

assert len(evidence) == 65, f"Expected 65 propositions, got {len(evidence)}"

ev_pass_count = 0
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
            
    if hash_match and spans_ok:
        ev_pass_count += 1

print(f"Evidence propositions verified: {ev_pass_count}/65 PASS")

print("\n--- 3. Verifying occurrences.jsonl census ---")
with open(occ_file, "r", encoding="utf-8") as f:
    occurrences = [json.loads(line) for line in f if line.strip()]

occ_pass_count = 0
for occ in occurrences:
    rid = occ["rev_id"]
    if rid not in revs:
        print(f"FAIL: occ {occ['occurrence_id']} rev {rid} not found")
        all_pass = False
        continue
    r = revs[rid]
    body = r["body"]
    start, end = occ["char_span"]
    parent_ev = next((e for e in evidence if e["evidence_id"] == occ["evidence_id"]), None)
    if parent_ev:
        quote = parent_ev["quotation"]
        actual = body[start:end]
        if actual != quote:
            print(f"OCC MISMATCH: {occ['occurrence_id']}")
            all_pass = False
            continue
    occ_pass_count += 1

print(f"Occurrences census verified: {occ_pass_count}/{len(occurrences)} PASS")

print("\n--- 4. Verifying splits.json and isolation ---")
with open(splits_file, "r", encoding="utf-8") as f:
    splits_data = json.load(f)

# Normalize CRLF->LF before hashing so this matches the canonical git blob
# (`git show HEAD:<path>`) regardless of the local checkout's line-ending
# handling -- see splits.json's _checksum_domain_note for why this matters.
ev_bytes = open(ev_file, "rb").read().replace(b"\r\n", b"\n")
occ_bytes = open(occ_file, "rb").read().replace(b"\r\n", b"\n")
ev_sha = hashlib.sha256(ev_bytes).hexdigest()
occ_sha = hashlib.sha256(occ_bytes).hexdigest()

assert ev_sha == splits_data["checksums"]["evidence_jsonl_sha256"], "evidence.jsonl hash mismatch in splits.json"
assert occ_sha == splits_data["checksums"]["occurrences_jsonl_sha256"], "occurrences.jsonl hash mismatch in splits.json"

dev_pages = set(splits_data["splits"]["dev"]["page_keys"])
held_pages = set(splits_data["splits"]["held_out"]["page_keys"])
overlap = dev_pages.intersection(held_pages)
assert len(overlap) == 0, f"Split leakage detected: {overlap}"
print(f"Splits verified: Dev pages={len(dev_pages)}, Held-out pages={len(held_pages)}, Overlap=0 (PERFECT ISOLATION)")

print("\n--- 5. Verifying adjudication.csv ---")
adj_rows = []
with open(adj_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        adj_rows.append(row)

assert len(adj_rows) == 65, f"Expected 65 adjudication rows, got {len(adj_rows)}"
adj_agree = all(r["agreement_status"] == "AGREE" and r["adjudication_decision"] == "APPROVED" for r in adj_rows)
assert adj_agree, "Disagreement or unapproved row in adjudication.csv"
print(f"Adjudication verified: 65/65 APPROVED by {adj_rows[0]['adjudicator']} with second review by {evidence[0]['reviewer_id']}")

print(f"\n==========================================")
print(f"OVERALL A11 BENCHMARK VERIFICATION: {'SUCCESS' if all_pass else 'FAILED'}")
print(f"==========================================")

if not all_pass:
    sys.exit(1)

