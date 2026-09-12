import hashlib
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Fixed 2026-09-12: this pointed at data/data/raw/export, the doubled path
# removed from git in commit b1c822e. Every other doc/test in the repo
# expects data/raw/export -- see sources/README.md's download recipe.
EXPORT_DIR = ROOT / "data" / "raw" / "export"
SUMS_FILE = ROOT / "sources" / "SHA256SUMS"
# Renamed from reconstruction_checks.csv 2026-09-12: that filename collided
# with V07's independent state-engine comparison output (unrelated content,
# same path) and a merge silently dropped this file's rows. Keep this script's
# output under its own name so it never collides with V07's file again.
OUTPUT_FILE = ROOT / "audit" / "raw_export_hash_verification.csv"

expected = {}
with open(SUMS_FILE, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 2:
            expected[parts[1]] = parts[0]

files = ["pages.jsonl", "revisions.jsonl", "events.jsonl", "labels.jsonl", "manifest.json"]

header = "file_name,verified_by,verification_timestamp_utc,row_count,raw_disk_bytes,crlf_detected,raw_sha256,lf_normalized_sha256,published_sha256,status"
rows = [header]

for name in files:
    file_path = EXPORT_DIR / name
    with open(file_path, "rb") as f:
        data = f.read()

    row_count = len(data.splitlines())
    raw_disk_bytes = len(data)
    has_crlf = b"\r\n" in data
    raw_hash = hashlib.sha256(data).hexdigest()
    lf_hash = hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()
    pub_hash = expected.get(name, "UNKNOWN")
    status = "MATCH" if lf_hash == pub_hash else "MISMATCH"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    rows.append(f"{name},Aaron,{timestamp},{row_count},{raw_disk_bytes},{str(has_crlf).lower()},{raw_hash},{lf_hash},{pub_hash},{status}")

output = "\n".join(rows) + "\n"
print(output, end="")
OUTPUT_FILE.write_text(output, encoding="utf-8")
print(f"\nwritten to {OUTPUT_FILE}")
