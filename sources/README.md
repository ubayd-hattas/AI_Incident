# Collusion Wiki core export retrieval

E01 uses only the official five-file bundle recorded in `registry.json`. Raw data are ignored by Git.

From the repository root in PowerShell, download into a new raw directory:

```powershell
New-Item -ItemType Directory -Path data/raw -ErrorAction Stop
Invoke-WebRequest -Uri 'https://collusion.wiki/explorer/download/full-wiki-logs.zip' -OutFile 'data/raw/full-wiki-logs.zip' -MaximumRedirection 5
New-Item -ItemType Directory -Path data/raw/export -ErrorAction Stop
Expand-Archive -LiteralPath data/raw/full-wiki-logs.zip -DestinationPath data/raw/export
```

Then validate offline and regenerate the inventory/notes:

```powershell
python src/ebe/ingest.py data/raw/export --inventory sources/schema_inventory.json --notes sources/E01_ANOMALIES.md
```

The validator fails before parsing if any expanded SHA-256 differs from the pinned values. It also fails on row-count, row-key, body-byte/hash, identity, relationship, or linkage differences. It never follows or executes URLs found inside exported bodies. Use a new directory rather than overwriting an earlier download; retain the original archive for provenance. The bundle SHA-256 observed on 2026-09-12 is recorded in `registry.json`, while `SHA256SUMS` contains the publisher-pinned expanded hashes.

