"""Read-only repository census for report verification. Never runs collectors/scoring.

Outputs are audit-only: file inventories and structural counts, not scientific
coverage. Raw text/excerpts are not copied to the inventory.
"""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import io
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "audit" / "report_submission"
SKIP = {".git", "__pycache__", ".pytest_cache", ".venv", "node_modules"}


def records(relative):
    return [json.loads(line) for line in (ROOT / relative).read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def main():
    OUT.mkdir(exist_ok=True)
    inventory = []
    json_errors = []
    result_tables = {}
    synthetic_modes = Counter()
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or any(part in SKIP for part in path.parts):
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative.startswith(("audit/report_submission/", "report/build/")):
            continue
        data = path.read_bytes()
        entry = {"path": relative, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                 "records": "", "inspection": "byte inventory"}
        try:
            if path.suffix in {".json", ".jsonl"}:
                text = data.decode("utf-8-sig")
                values = ([json.loads(line) for line in text.splitlines() if line.strip()]
                          if path.suffix == ".jsonl" else [json.loads(text)])
                entry.update(records=len(values), inspection="JSON parsed; structural inspection")
                if "synthetic_rows/" in relative and path.suffix == ".json":
                    for value in values:
                        synthetic_modes[(value.get("mode"), value.get("result", {}).get("fixture"))] += 1
            elif path.suffix == ".csv":
                rows = list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))
                entry.update(records=len(rows), inspection="CSV parsed; structural inspection")
                if relative.startswith("runs/") and "/results/" in relative:
                    result_tables[relative] = len(rows)
            elif path.suffix in {".py", ".md", ".tex", ".svg", ".txt"}:
                text = data.decode("utf-8-sig")
                entry.update(records=len(text.splitlines()), inspection="text indexed; targeted review separately documented")
        except (ValueError, UnicodeError) as exc:
            json_errors.append({"path": relative, "error": str(exc)})
        inventory.append(entry)
    with (OUT / "repository_inventory.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(inventory[0]))
        writer.writeheader(); writer.writerows(inventory)

    evidence = records("annotations/evidence.jsonl")
    splits = json.loads((ROOT / "annotations/splits.json").read_text(encoding="utf-8-sig"))
    byid = {r["evidence_id"]: r for r in evidence}
    benchmark = {"propositions": len(evidence), "critical": sum(r["critical"] for r in evidence),
                 "groups": len(splits["groups"]), "splits": {}}
    for name, group in splits["splits"].items():
        ids = group["evidence_ids"]
        benchmark["splits"][name] = {"propositions": len(ids), "critical": sum(byid[i]["critical"] for i in ids),
                                      "groups": len(group["group_ids"]), "catalog_pages": len(group["page_keys"]),
                                      "declared_episode_ids": len(group["episode_ids"])}
    for name in ["occurrences", "context_fragments", "context_occurrences", "context_eligibility"]:
        benchmark[name + "_rows"] = len(records("annotations/" + name + ".jsonl"))

    revs = records("data/raw/export/revisions.jsonl")
    events = records("data/raw/export/events.jsonl")
    pages = records("data/raw/export/pages.jsonl")
    dse_revs = [r for r in revs if r["wiki"] == "dse"]
    deletions = [r for r in events if r.get("wiki") == "dse" and r["event_type"] == "delete"]
    held = {r["page_key"] for r in dse_revs}
    no_body = [r for r in deletions if r["page_key"] not in held]
    source = {"all_pages": len(pages), "all_revisions": len(revs), "all_events": len(events),
              "dse_pages": sum(r["wiki"] == "dse" for r in pages), "dse_revisions": len(dse_revs),
              "dse_deletions": len(deletions), "deletion_only_titles": len({r["page_key"] for r in no_body}),
              "deletion_events_without_held_revision": len(no_body),
              "event_types": dict(Counter(r["event_type"] for r in events))}
    source["checksums"] = {}
    for line in (ROOT / "sources/SHA256SUMS").read_text().splitlines():
        if not line.strip(): continue
        digest, name = line.split(maxsplit=1)
        actual = hashlib.sha256((ROOT / "data/raw/export" / name.lstrip(" *")).read_bytes()).hexdigest()
        source["checksums"][name] = {"expected": digest, "actual": actual, "match": digest == actual}
    checks = list(csv.DictReader((ROOT / "audit/reconstruction_checks.csv").open(encoding="utf-8-sig")))
    status_path = ROOT / "runs/FINAL_PRE_X13_DEADLINE_v1/results/status_index.json"
    result = {"commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "inventory_file_count": len(inventory), "parse_errors": json_errors,
              "benchmark": benchmark, "source": source,
              "result_csv_rows": result_tables, "real_status": json.loads(status_path.read_text()),
              "real_row_artifact_count": len(list((ROOT / "runs").glob("*/rows/*.json"))),
              "synthetic_modes": [{"mode": k[0], "fixture": k[1], "count": v} for k, v in synthetic_modes.items()],
              "reconstruction_csv_rows": len(checks), "reconstruction_columns": list(checks[0]),
              "reconstruction_classifications": dict(Counter(r.get("classification", "COLUMN_NOT_PRESENT") for r in checks))}
    (OUT / "verified_repository_facts.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
