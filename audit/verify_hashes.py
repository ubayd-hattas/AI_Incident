import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPORT_DIR = ROOT / "data" / "data" / "raw" / "export"
SUMS_FILE = ROOT / "sources" / "SHA256SUMS"

expected = {}
with open(SUMS_FILE, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 2:
            expected[parts[1]] = parts[0]

files = ["pages.jsonl", "revisions.jsonl", "events.jsonl", "labels.jsonl", "manifest.json"]

print("file_name,verified_by,verification_timestamp_utc,row_count,raw_disk_bytes,crlf_detected,raw_sha256,lf_normalized_sha256,published_sha256,status")

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

    print(f"{name},Aaron,2026-09-12T13:42:00Z,{row_count},{raw_disk_bytes},{str(has_crlf).lower()},{raw_hash},{lf_hash},{pub_hash},{status}")
