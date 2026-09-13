"""Independent A11 benchmark re-verification.

Written from scratch, not by importing or reusing `audit/verify_annotations.py`
(the author-side checker shipped alongside the A11 freeze). Uses the correct,
git-tracked-consistent raw export path (`data/raw/export`), not the doubled
`data/data/raw/export` path that checker hardcodes -- that path is not
reproducible outside a machine that happens to have a stale leftover
directory (see `audit/SAM_RESPONSE_TO_PRE_RESULTS_AUDIT.md` for how that
leftover came to exist here). Also checks page-level split consistency
directly from occurrence data, not just the declared split lists' mutual
disjointness (a stronger check: the existing checker doesn't confirm every
occurrence's own page is actually recorded under one of the two splits).
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REV_FILE = REPO / "data" / "raw" / "export" / "revisions.jsonl"
EV_FILE = REPO / "annotations" / "evidence.jsonl"
OCC_FILE = REPO / "annotations" / "occurrences.jsonl"
SPLITS_FILE = REPO / "annotations" / "splits.json"
ADJ_FILE = REPO / "annotations" / "adjudication.csv"

FAILURES: list[str] = []

CODECS = {"ascii": "ascii", "utf8": "utf-8", "latin1": "latin-1"}

def canonical_text(revision: dict) -> str:
    """E05: recover Latin-1-projected raw bytes before declared decoding."""
    raw = revision["body"].encode("latin-1")
    if hashlib.sha256(raw).hexdigest() != revision["body_sha256"]:
        raise ValueError(f"raw body_sha256 does not reproduce for {revision['rev_id']}")
    return raw.decode(CODECS[revision["body_encoding"]])



def check(label: str, cond: bool, detail: str = "") -> None:
    status = "PASS" if cond else "FAIL"
    print(f"  {status} {label}" + (f" -- {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append(f"{label}: {detail}")


print(f"=== Loading raw revisions from {REV_FILE.relative_to(REPO)} ===")
if not REV_FILE.exists():
    print(f"  FATAL: {REV_FILE} does not exist. Run the data-download recipe in sources/README.md first.")
    sys.exit(2)

revs: dict[str, dict] = {}
with open(REV_FILE, encoding="utf-8") as f:
    for line in f:
        if line.strip():
            r = json.loads(line)
            revs[r["rev_id"]] = r
print(f"  loaded {len(revs)} revisions")

with open(EV_FILE, encoding="utf-8") as f:
    evidence = [json.loads(line) for line in f if line.strip()]
with open(OCC_FILE, encoding="utf-8") as f:
    occurrences = [json.loads(line) for line in f if line.strip()]
with open(SPLITS_FILE, encoding="utf-8") as f:
    splits = json.load(f)
with open(ADJ_FILE, encoding="utf-8") as f:
    adjudication = list(csv.DictReader(f))

evidence_by_id = {e["evidence_id"]: e for e in evidence}

print("\n=== 1. evidence.jsonl: independently recomputed hash + span integrity (all 65) ===")
check("evidence.jsonl has exactly 65 propositions", len(evidence) == 65, str(len(evidence)))
ev_hash_fail = ev_span_fail = 0
for ev in evidence:
    rev = revs.get(ev["rev_id"])
    if rev is None:
        ev_hash_fail += 1
        print(f"  FAIL {ev['evidence_id']}: rev_id {ev['rev_id']!r} not found in raw export")
        continue
    body = canonical_text(rev)
    # docs/E05_TYPED_LOADER.md: the raw `body` string is ALWAYS a Latin-1 byte
    # projection of the true source bytes regardless of declared body_encoding.
    # This branch previously compared against the literal "latin-1" (with a
    # hyphen), which never matches the real field values ("ascii"/"utf8"/
    # "latin1" without one) -- so it always silently took the wrong UTF-8
    # path. Confirmed real: 2 evidence + 80 occurrence hash mismatches found
    # independently against the true (always-latin-1) source bytes.
    body_bytes = rev["body"].encode("latin-1")
    real_hash = hashlib.sha256(body_bytes).hexdigest()
    if real_hash != ev["source_body_hash"]:
        ev_hash_fail += 1
        print(f"  FAIL {ev['evidence_id']}: hash mismatch (recomputed {real_hash[:12]}... vs recorded {ev['source_body_hash'][:12]}...)")
    if len(body) != ev["body_len"]:
        ev_span_fail += 1
        print(f"  FAIL {ev['evidence_id']}: canonical body length mismatch")
    for span in ev["source_spans"]:
        if body[span["start"]:span["end"]] != span["quote"]:
            ev_span_fail += 1
            print(f"  FAIL {ev['evidence_id']}: span [{span['start']}:{span['end']}] does not match its recorded quote")
check("all 65 propositions' body hashes independently reproduce (own hashlib call, own encoding branch)", ev_hash_fail == 0, f"{ev_hash_fail} mismatches")
check("all recorded source_spans independently reproduce (own char-slice, not the author checker's)", ev_span_fail == 0, f"{ev_span_fail} mismatches")

print("\n=== 1b. Count reconciliation: does splits.json's own summary match a fresh count from evidence.jsonl? ===")
# Added 2026-09-13 after finding annotations/A11_BENCHMARK_SPEC.md's prose (49 critical /
# 16 non-critical, and a stale per-split table) did not match evidence.jsonl's own
# `critical` field or splits.json's own `summary` block (both of which already said
# 57/8). This check exists so that kind of doc/data drift fails loudly next time,
# instead of silently propagating into PROJECT_STATUS.md the way it did here.
real_critical = sum(1 for e in evidence if e["critical"])
real_noncritical = len(evidence) - real_critical
check("splits.json summary.critical_propositions matches a fresh count of evidence.jsonl's own critical field", splits["summary"]["critical_propositions"] == real_critical, f"summary={splits['summary']['critical_propositions']} recomputed={real_critical}")
check("splits.json summary.non_critical_propositions matches a fresh count", splits["summary"]["non_critical_propositions"] == real_noncritical, f"summary={splits['summary']['non_critical_propositions']} recomputed={real_noncritical}")
dev_ids_early = set(splits["splits"]["dev"]["evidence_ids"])
held_ids_early = set(splits["splits"]["held_out"]["evidence_ids"])
dev_rows = [e for e in evidence if e["evidence_id"] in dev_ids_early]
held_rows = [e for e in evidence if e["evidence_id"] in held_ids_early]
print(f"  INFO per-split (recomputed): dev={len(dev_rows)} evidence / {sum(1 for r in dev_rows if r['critical'])} critical -- held={len(held_rows)} evidence / {sum(1 for r in held_rows if r['critical'])} critical")

print("\n=== 2. occurrences.jsonl: independently recomputed hash + span integrity (all occurrences) ===")
check(f"occurrences.jsonl has {len(occurrences)} rows (claimed 1,421 after the 2026-09-13 exact-match completeness fix)", len(occurrences) == 1421, str(len(occurrences)))
occ_hash_fail = occ_span_fail = occ_orphan = occ_evhash_mismatch = 0
for occ in occurrences:
    rev = revs.get(occ["rev_id"])
    parent = evidence_by_id.get(occ["evidence_id"])
    if rev is None or parent is None:
        occ_orphan += 1
        continue
    body = canonical_text(rev)
    body_bytes = rev["body"].encode("latin-1")  # source bytes, not canonical UTF-8
    real_hash = hashlib.sha256(body_bytes).hexdigest()
    if real_hash != occ["body_sha256"]:
        occ_hash_fail += 1
    if occ["body_sha256"] != parent["source_body_hash"] and rev["rev_id"] == parent["rev_id"]:
        # only meaningful to compare directly when it's literally the same revision as the parent's anchor
        pass
    start, end = occ["char_span"]
    occ_text = body[start:end]
    # A proposition's `quotation` field is the FULL multi-span text (spans
    # joined with an ellipsis for multi-span propositions), which only equals
    # a single occurrence's own char_span slice when the proposition has
    # exactly one source_span. For multi-span propositions (currently just
    # PROP-20260619-01), each occurrence's slice must instead match ONE of
    # the parent's individual source_spans' quote text -- comparing against
    # the combined `quotation` would spuriously fail every correctly-recorded
    # multi-span occurrence.
    if len(parent["source_spans"]) == 1:
        expected_texts = {parent["quotation"]}
    else:
        expected_texts = {span["quote"] for span in parent["source_spans"]}
    if occ_text not in expected_texts:
        occ_span_fail += 1
check("no occurrence references a missing rev_id or evidence_id", occ_orphan == 0, f"{occ_orphan} orphaned")
check("every occurrence's own body_sha256 independently reproduces from its own rev_id's body", occ_hash_fail == 0, f"{occ_hash_fail} mismatches")
check("every occurrence's char_span independently reproduces one of its parent proposition's exact source_span quotes", occ_span_fail == 0, f"{occ_span_fail} mismatches")

print("\n=== 3. Cross-file hash chain: does splits.json actually pin the files on disk? ===")
# Normalize CRLF->LF before hashing. A raw read_bytes() hash depends on the local
# checkout's line-ending state (e.g. Windows core.autocrlf=true silently converts
# the repository's real LF content to CRLF), which is exactly the bug that made
# Sam's own hash checks unreproducible earlier in this project (see
# audit/SAM_RESPONSE_TO_PRE_RESULTS_AUDIT.md's retraction note). Hashing the
# canonical (LF) form matches what `git show HEAD:<path>` produces on any machine.
ev_sha = hashlib.sha256(EV_FILE.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
occ_sha = hashlib.sha256(OCC_FILE.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
check("splits.json's pinned evidence.jsonl SHA-256 matches the file on disk", ev_sha == splits["checksums"]["evidence_jsonl_sha256"], f"disk={ev_sha[:12]} pinned={splits['checksums']['evidence_jsonl_sha256'][:12]}")
check("splits.json's pinned occurrences.jsonl SHA-256 matches the file on disk", occ_sha == splits["checksums"]["occurrences_jsonl_sha256"], f"disk={occ_sha[:12]} pinned={splits['checksums']['occurrences_jsonl_sha256'][:12]}")

print("\n=== 4. Split isolation: stronger check -- every OCCURRENCE's actual page, not just the declared lists ===")
dev_pages = set(splits["splits"]["dev"]["page_keys"])
held_pages = set(splits["splits"]["held_out"]["page_keys"])
check("declared dev/held-out page_key lists are themselves disjoint", len(dev_pages & held_pages) == 0, str(dev_pages & held_pages))

occ_pages = {occ["page_key"] for occ in occurrences}
unassigned = occ_pages - dev_pages - held_pages
check("every page_key that actually appears in occurrences.jsonl is assigned to one of the two declared splits", len(unassigned) == 0, f"{len(unassigned)} unassigned pages: {sorted(unassigned)[:5]}")

ev_pages = {rev_id_page := ev["rev_id"].split("@")[0].split("~", 1)[1] and "dse~" + ev["rev_id"].split("~", 1)[1].split("@")[0] for ev in evidence}
ev_unassigned = ev_pages - dev_pages - held_pages
check("every page_key implied by evidence.jsonl's own rev_ids is assigned to one of the two declared splits", len(ev_unassigned) == 0, f"{len(ev_unassigned)} unassigned: {sorted(ev_unassigned)[:5]}")

# Group-level consistency: every evidence row's equivalent_occurrences_group must
# be wholly inside ONE split's declared group_ids, and its page must match that split.
group_to_split: dict[str, str] = {}
for split_name in ("dev", "held_out"):
    for gid in splits["splits"][split_name]["group_ids"]:
        group_to_split[gid] = split_name
mismatched_group_assignment = 0
for ev in evidence:
    grp = ev["equivalent_occurrences_group"]
    page = "dse~" + ev["rev_id"].split("~", 1)[1].split("@")[0]
    assigned_split = group_to_split.get(grp)
    if assigned_split is None:
        mismatched_group_assignment += 1
        continue
    page_split = "dev" if page in dev_pages else ("held_out" if page in held_pages else None)
    if page_split != assigned_split:
        mismatched_group_assignment += 1
check("every evidence row's group assignment agrees with its own page's declared split (no cross-split leakage inside one proposition)", mismatched_group_assignment == 0, f"{mismatched_group_assignment} mismatches")

print("\n=== 5. Adjudication completeness ===")
check("adjudication.csv has exactly 65 rows, one per proposition", len(adjudication) == 65, str(len(adjudication)))
adj_ids = {row.get("evidence_id") for row in adjudication}
ev_ids = set(evidence_by_id)
check("adjudication.csv covers exactly the same 65 evidence_ids as evidence.jsonl (no orphans, no gaps)", adj_ids == ev_ids, f"missing={ev_ids - adj_ids} extra={adj_ids - ev_ids}")

print("\n=== 6. Qualitative re-check: does the epistemic-leakage prose the pre-results audit flagged still exist? ===")
# Check for the SPECIFIC originally-flagged phrasing, not a bare "confirming"
# substring -- the fix deliberately reuses the word inside a negated clause
# ("not independently confirming"), which is the correct hedge, not the bug.
for eid, original_phrase in (
    ("PROP-20260620-09", "confirming widespread swarm adoption of bypass"),
    ("PROP-20260619-03", "confirming utilization of shared answer"),
):
    row = evidence_by_id.get(eid)
    if row is None:
        print(f"  INFO {eid} not present in this delivery")
        continue
    text = " ".join([row.get("critical_reason", ""), row.get("notes", "")])
    found = original_phrase.lower() in text.lower()
    # Previously this only printed STILL PRESENT/RESOLVED and never affected
    # the run's pass/fail outcome -- a prose regression could recur silently.
    check(f"{eid} no longer uses the exact originally-flagged phrasing ({original_phrase!r})", not found)

print("\n" + "=" * 60)
print(f"A11 INDEPENDENT VERIFICATION FAILURES: {len(FAILURES)}")
for f in FAILURES:
    print("  -", f)

if FAILURES:
    # Previously this script accumulated FAILURES but never exited nonzero --
    # a real fail-open gap in CI/automation use.
    import sys as _sys
    _sys.exit(1)
