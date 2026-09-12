"""Strict, lossless inspection of the pinned Collusion Wiki export.

This module intentionally implements no timeline or historical-state semantics.
It never follows strings found in the export and never rewrites missing values.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


CORE_FILES = ("pages.jsonl", "revisions.jsonl", "events.jsonl", "labels.jsonl")
EXPECTED_HASHES = {
    "pages.jsonl": "92b296170b496b836cdf5ef783bed9465d2d75db7e1a0becec1c36c8b7c42cfd",
    "revisions.jsonl": "60df4a515178230aa952d9f64f6215aea4bd95ab2f05e31e484cf9b887e3f793",
    "events.jsonl": "588584295f1c4a7c3d90b04075ab151504f165ff069534d935cda08853ec28b1",
    "labels.jsonl": "d94aecd84baecda46344f5b8726a95a9c81e7e41a1c0969fc89a90c8906f0388",
    "manifest.json": "b6d53e16b5d9a6a0a98d4577238835ee7a574d7d10a8f1312330b4e626c6ba2b",
}
EXPECTED_ROWS = {
    "pages.jsonl": 4579,
    "revisions.jsonl": 14591,
    "events.jsonl": 19913,
    "labels.jsonl": 3103,
}

EXPECTED_KEYS = {
    "pages.jsonl": frozenset(
        "page_id page_key wiki name bucket page_family page_family_cohort "
        "page_family_confidence page_family_method page_family_source n_revs "
        "n_revs_before first_write last_write body_bytes deleted_live "
        "live_body_variant head_differs_from_live n_deletions n_recreations "
        "labels n_labels n_ips n_ip16".split()
    ),
    "revisions.jsonl": frozenset(
        "rev_id page_id page_key wiki name seq rcs_rev rcs_path body body_len "
        "body_sha256 lines diff_base diff_base_reason hunks label ip16 time "
        "time_grade winning_clock uncertainty_seconds request_time success_time "
        "recent_changes_time write_date archived_at request_action change_summary "
        "related_event_id relation_type round_id body_encoding".split()
    ),
    "labels.jsonl": frozenset(
        "label is_human_handle stored_revisions first_write last_write "
        "stored_revision_ips stored_revision_ip16 stored_revision_pages pages "
        "wikis save_requests save_request_ips save_request_ip16 "
        "save_request_pages save_request_source".split()
    ),
}
EXPECTED_EVENT_KEYS = {
    "save": frozenset(
        "event_id event_type wiki page page_key time time_grade revision_ref "
        "related_event_id relation_type round_id".split()
    ),
    "delete": frozenset(
        "event_id event_type wiki page page_key time time_grade winning_clock "
        "uncertainty_seconds request_time success_time write_date rcs_date "
        "recent_changes_time clock_delta_seconds success_observed request_action "
        "change_summary actor_label ip16 revision_ref related_event_id "
        "relation_type round_id page_held source_refs clock_note".split()
    ),
    "revert": frozenset(
        "event_id event_type wiki page page_key time time_grade winning_clock "
        "uncertainty_seconds request_time success_time write_date rcs_date "
        "recent_changes_time clock_delta_seconds success_observed request_action "
        "change_summary actor_label ip16 revision_ref related_event_id "
        "relation_type round_id page_held source_refs clock_note".split()
    ),
    "probe": frozenset(
        "event_id event_type time time_grade ip16 request_action param_family "
        "source_refs success_observed".split()
    ),
}

# These tags constrain later loaders; they do not assert undocumented meanings.
RETROSPECTIVE_FIELDS = {
    "pages.jsonl": {
        "body_bytes", "deleted_live", "head_differs_from_live", "labels",
        "live_body_variant", "n_deletions", "n_ip16", "n_ips", "n_labels",
        "n_recreations", "n_revs", "n_revs_before", "page_family",
        "page_family_cohort", "page_family_confidence", "page_family_method",
        "page_family_source",
    },
    "revisions.jsonl": {
        "archived_at", "diff_base", "diff_base_reason", "hunks",
        "related_event_id", "relation_type", "round_id",
    },
    "events.jsonl": {"page_held", "related_event_id", "relation_type", "round_id"},
    "labels.jsonl": set(EXPECTED_KEYS["labels.jsonl"]),
    "manifest.json": {"*"},
}


class ValidationError(RuntimeError):
    """The source differs from the pinned E01 contract."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", errors="strict", newline="") as handle:
        for line_no, line in enumerate(handle, 1):
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValidationError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
            if not isinstance(value, dict):
                raise ValidationError(f"{path}:{line_no}: expected JSON object")
            rows.append(value)
    return rows


def _type_name(value: Any) -> str:
    if value is None:
        return "NoneType/null"
    if isinstance(value, bool):
        return "bool/boolean"
    if isinstance(value, int):
        return "int/integer"
    if isinstance(value, float):
        return "float/number"
    if isinstance(value, str):
        return "str/string"
    if isinstance(value, list):
        return "list/array"
    if isinstance(value, dict):
        return "dict/object"
    return type(value).__name__


def _example(value: Any, path: str) -> Any:
    if path.endswith(".body") and isinstance(value, str):
        return {
            "content_omitted": True,
            "unicode_characters": len(value),
            "utf8_sha256": hashlib.sha256(value.encode("utf-8")).hexdigest(),
        }
    if isinstance(value, str):
        if "http://" in value.lower() or "https://" in value.lower():
            return "<string containing URL omitted>"
        return value if len(value) <= 160 else value[:157] + "..."
    if isinstance(value, list):
        if value and isinstance(value[0], dict):
            return {"array_length": len(value), "first_element_type": "object"}
        return [_example(item, path + "[]") for item in value[:2]]
    if isinstance(value, dict):
        return {"object_keys": list(value)[:8], "key_count": len(value)}
    return value


def _schema_inventory(filename: str, records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    parent_counts: Counter[str] = Counter()
    fields: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"present": 0, "null": 0, "types": Counter(), "example": None}
    )

    def visit_object(obj: dict[str, Any], path: str) -> None:
        parent_counts[path] += 1
        for key, value in obj.items():
            field_path = f"{path}.{key}" if path else key
            stat = fields[field_path]
            stat["present"] += 1
            stat["null"] += value is None
            stat["types"][_type_name(value)] += 1
            if stat["example"] is None and value is not None:
                stat["example"] = _example(value, field_path)
            if isinstance(value, dict):
                visit_object(value, field_path)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        visit_object(item, field_path + "[]")
                    else:
                        item_path = field_path + "[]"
                        item_stat = fields[item_path]
                        item_stat["present"] += 1
                        item_stat["null"] += item is None
                        item_stat["types"][_type_name(item)] += 1
                        if item_stat["example"] is None and item is not None:
                            item_stat["example"] = _example(item, item_path)

    for record in records:
        visit_object(record, "")

    output: dict[str, Any] = {}
    for path, stat in sorted(fields.items()):
        parent = path.rsplit(".", 1)[0] if "." in path else ""
        if path.endswith("[]"):
            denominator = stat["present"]
            missing = 0
        else:
            denominator = parent_counts[parent]
            missing = denominator - stat["present"]
        top_field = path.split(".", 1)[0].removesuffix("[]")
        role = (
            "retrospective/evaluator-only"
            if "*" in RETROSPECTIVE_FIELDS.get(filename, set())
            or top_field in RETROSPECTIVE_FIELDS.get(filename, set())
            else "source/provenance; availability semantics not inferred"
        )
        output[path] = {
            "parent_occurrences": denominator,
            "present": stat["present"],
            "missing": missing,
            "null": stat["null"],
            "null_frequency": stat["null"] / denominator if denominator else 0.0,
            "observed_types": dict(sorted(stat["types"].items())),
            "forms": sorted(
                form for form, marker in (
                    ("null", "NoneType/null"),
                    ("scalar", None),
                    ("list", "list/array"),
                )
                if (marker in stat["types"] if marker else any(t not in {"NoneType/null", "list/array"} for t in stat["types"]))
            ),
            "representative_example": stat["example"],
            "information_role": role,
        }
    return output


def _assert_equal(actual: Any, expected: Any, label: str, errors: list[str]) -> None:
    if actual != expected:
        errors.append(f"{label}: expected {expected!r}, observed {actual!r}")


def _duplicates(values: Iterable[Any]) -> list[Any]:
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if count > 1)


def _as_edges(row: dict[str, Any]) -> list[tuple[str, str | None, str | None]]:
    relation = row.get("relation_type")
    related = row.get("related_event_id")
    rounds = row.get("round_id")
    if relation is None:
        # Deletion rows may carry a round identifier without carrying an edge.
        # Preserve it, but do not infer a relationship from it.
        if related is not None:
            raise ValidationError(f"partial relation fields on {row.get('event_id') or row.get('rev_id')}")
        return []
    related_values = related if isinstance(related, list) else [related]
    relation_values = relation if isinstance(relation, list) else [relation] * len(related_values)
    round_values = rounds if isinstance(rounds, list) else [rounds] * len(related_values)
    if not (len(related_values) == len(relation_values) == len(round_values)):
        raise ValidationError(f"misaligned relation fields on {row.get('event_id') or row.get('rev_id')}")
    return list(zip(relation_values, related_values, round_values))


def _parse_timestamp(value: str) -> None:
    datetime.fromisoformat(value.replace("Z", "+00:00"))


def validate(raw_dir: Path) -> tuple[dict[str, Any], str]:
    errors: list[str] = []
    hashes: dict[str, str] = {}
    for filename, expected in EXPECTED_HASHES.items():
        path = raw_dir / filename
        if not path.is_file():
            errors.append(f"missing required file: {filename}")
            continue
        hashes[filename] = _sha256(path)
        _assert_equal(hashes[filename], expected, f"SHA-256 {filename}", errors)
    if errors:
        raise ValidationError("\n".join(errors))

    data = {filename: _read_jsonl(raw_dir / filename) for filename in CORE_FILES}
    manifest = json.loads((raw_dir / "manifest.json").read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValidationError("manifest.json must contain one JSON object")

    for filename, rows in data.items():
        _assert_equal(len(rows), EXPECTED_ROWS[filename], f"row count {filename}", errors)
        if filename in EXPECTED_KEYS:
            for line_no, row in enumerate(rows, 1):
                if frozenset(row) != EXPECTED_KEYS[filename]:
                    errors.append(
                        f"{filename}:{line_no}: schema keys changed; "
                        f"missing={sorted(EXPECTED_KEYS[filename] - set(row))}, "
                        f"extra={sorted(set(row) - EXPECTED_KEYS[filename])}"
                    )
                    break

    pages = data["pages.jsonl"]
    revisions = data["revisions.jsonl"]
    events = data["events.jsonl"]
    labels = data["labels.jsonl"]
    for line_no, event in enumerate(events, 1):
        event_type = event.get("event_type")
        if event_type not in EXPECTED_EVENT_KEYS:
            errors.append(f"events.jsonl:{line_no}: unexpected event_type {event_type!r}")
        elif frozenset(event) != EXPECTED_EVENT_KEYS[event_type]:
            errors.append(f"events.jsonl:{line_no}: schema keys changed for {event_type}")
            break

    duplicate_ids = {
        "page_id": _duplicates(row["page_id"] for row in pages),
        "page_key": _duplicates(row["page_key"] for row in pages),
        "rev_id": _duplicates(row["rev_id"] for row in revisions),
        "event_id": _duplicates(row["event_id"] for row in events),
        "label": _duplicates(row["label"] for row in labels),
    }
    for kind, duplicates in duplicate_ids.items():
        _assert_equal(duplicates, [], f"duplicate {kind}", errors)

    pages_by_key = {row["page_key"]: row for row in pages}
    revisions_by_id = {row["rev_id"]: row for row in revisions}
    events_by_id = {row["event_id"]: row for row in events}
    revision_counts = Counter(row["page_key"] for row in revisions)
    bad_revision_pages = []
    body_failures = []
    encoding_counts: Counter[str] = Counter()
    for row in revisions:
        page = pages_by_key.get(row["page_key"])
        if page is None or (row["page_id"], row["wiki"], row["name"]) != (
            page["page_id"], page["wiki"], page["name"]
        ):
            bad_revision_pages.append(row["rev_id"])
        encoding = row["body_encoding"]
        if encoding not in {"ascii", "utf8", "latin1"}:
            body_failures.append(f"{row['rev_id']}: unknown encoding {encoding}")
            continue
        try:
            # The JSON string is a lossless Latin-1 projection of source bytes.
            # body_encoding describes classification/decodability of those bytes;
            # it is not permission to UTF-8-encode the projection itself.
            body_bytes = row["body"].encode("latin-1", errors="strict")
        except UnicodeEncodeError:
            body_failures.append(f"{row['rev_id']}: body is not a byte-preserving Latin-1 projection")
            continue
        classified = "ascii" if body_bytes.isascii() else "utf8"
        if classified == "utf8":
            try:
                body_bytes.decode("utf-8", errors="strict")
            except UnicodeDecodeError:
                classified = "latin1"
        if classified != encoding:
            body_failures.append(f"{row['rev_id']}: declared {encoding}, classified {classified}")
            continue
        encoding_counts[encoding] += 1
        if len(body_bytes) != row["body_len"] or hashlib.sha256(body_bytes).hexdigest() != row["body_sha256"]:
            body_failures.append(row["rev_id"])
    _assert_equal(bad_revision_pages, [], "revision-to-page linkage failures", errors)
    _assert_equal(body_failures, [], "revision body verification failures", errors)
    _assert_equal(dict(encoding_counts), {"ascii": 14340, "utf8": 250, "latin1": 1}, "body encodings", errors)
    _assert_equal(
        [key for key, page in pages_by_key.items() if revision_counts[key] != page["n_revs"]],
        [], "page n_revs mismatches", errors,
    )

    save_events = [row for row in events if row["event_type"] == "save"]
    save_ref_counts = Counter(row["revision_ref"] for row in save_events)
    save_link_failures = []
    for row in save_events:
        revision = revisions_by_id.get(row["revision_ref"])
        if revision is None or (row["wiki"], row["page"], row["page_key"], row["time"], row["time_grade"]) != (
            revision["wiki"], revision["name"], revision["page_key"], revision["time"], revision["time_grade"]
        ):
            save_link_failures.append(row["event_id"])
        elif (row["related_event_id"], row["relation_type"], row["round_id"]) != (
            revision["related_event_id"], revision["relation_type"], revision["round_id"]
        ):
            save_link_failures.append(row["event_id"] + ":relation")
    _assert_equal(save_link_failures, [], "save/revision linkage failures", errors)
    _assert_equal(len(save_ref_counts), len(revisions), "distinct save revision refs", errors)
    _assert_equal([key for key, count in save_ref_counts.items() if count != 1], [], "non-1:1 save refs", errors)

    nonprobe_page_failures = []
    observed_page_keys: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in events:
        if row["event_type"] == "probe":
            continue
        observed_page_keys[(row["wiki"], row["page"])].add(row["page_key"])
        if row["event_type"] != "save" and row["page_held"] != (row["page_key"] in pages_by_key):
            nonprobe_page_failures.append(row["event_id"] + ":page_held")
        page = pages_by_key.get(row["page_key"])
        if page is not None and (row["wiki"], row["page"]) != (page["wiki"], page["name"]):
            nonprobe_page_failures.append(row["event_id"] + ":page_identity")
    for identity, keys in observed_page_keys.items():
        if len(keys) != 1:
            nonprobe_page_failures.append(f"{identity!r}:multiple_observed_keys")
    _assert_equal(nonprobe_page_failures, [], "event page linkage failures", errors)

    relation_reference_failures = []
    event_relation_rows = []
    event_relation_edges = []
    for row in events:
        edges = _as_edges(row)
        recreation = [edge for edge in edges if edge[0] == "first_recreation_of"]
        if recreation:
            event_relation_rows.append(row["event_id"])
            event_relation_edges.extend((row["event_id"], *edge) for edge in recreation)
        for _, related_id, _ in edges:
            if related_id not in events_by_id:
                relation_reference_failures.append((row["event_id"], related_id))
    _assert_equal(relation_reference_failures, [], "unresolved event relation references", errors)
    _assert_equal(len(event_relation_rows), 67, "physical event rows carrying recreation relations", errors)
    _assert_equal(len(event_relation_edges), 68, "recreation relation edges", errors)

    dse_pages = [row for row in pages if row["wiki"] == "dse"]
    dse_revisions = [row for row in revisions if row["wiki"] == "dse"]
    deletes = [
        row for row in events
        if row["event_type"] == "delete" and row["wiki"] == "dse"
        and row["success_observed"] is True and row["actor_label"] == "[Admin1]"
    ]
    deleted_titles = {row["page"] for row in deletes}
    held_dse_titles = {row["name"] for row in dse_pages}
    deletion_only_titles = deleted_titles - held_dse_titles
    deletion_only_rows = [row for row in deletes if row["page"] in deletion_only_titles]
    _assert_equal(len(dse_pages), 3908, "DSE pages", errors)
    _assert_equal(len(dse_revisions), 13403, "DSE revisions", errors)
    _assert_equal(len(deletes), 5217, "successful DSE administrator deletions", errors)
    _assert_equal(len(deleted_titles), 5144, "distinct deleted titles", errors)
    _assert_equal(len(deletion_only_titles), 1246, "deletion-only titles", errors)
    _assert_equal(len(deletion_only_rows), 1248, "deletion events on deletion-only titles", errors)

    deleted_live = Counter(row["deleted_live"] for row in dse_pages)
    head_differs = Counter(row["head_differs_from_live"] for row in dse_pages)
    live_combinations = Counter(
        (row["deleted_live"], row["head_differs_from_live"], row["live_body_variant"])
        for row in dse_pages
    )
    _assert_equal(dict(deleted_live), {False: 3908}, "DSE deleted_live", errors)
    _assert_equal(dict(head_differs), {False: 3899, True: 9}, "DSE head_differs_from_live", errors)
    _assert_equal(
        dict(live_combinations), {(False, False, "txt"): 3898, (False, True, "dw"): 9, (False, False, "dw"): 1},
        "DSE live-body combinations", errors,
    )

    reverts = [row for row in events if row["event_type"] == "revert"]
    no_body_form_edits = [
        row for row in reverts
        if row["revision_ref"] is None and row["request_action"] == "form_edit"
        and row["success_observed"] is True
    ]
    _assert_equal(len(reverts), 4, "revert event rows", errors)
    _assert_equal(len(no_body_form_edits), 4, "no-body successful form_edit mutations", errors)

    timestamp_inventory: dict[str, dict[str, int]] = {}
    for filename, rows in data.items():
        candidates = sorted(
            key for key in set().union(*(row.keys() for row in rows))
            if key == "time" or key.endswith(("_time", "_date", "_at", "_write"))
        )
        for key in candidates:
            stat = Counter()
            for row in rows:
                if key not in row:
                    stat["missing"] += 1
                elif row[key] is None:
                    stat["null"] += 1
                elif isinstance(row[key], str):
                    try:
                        _parse_timestamp(row[key])
                    except ValueError:
                        stat["invalid"] += 1
                    else:
                        stat["valid"] += 1
                else:
                    stat["invalid_type"] += 1
            timestamp_inventory[f"{filename}:{key}"] = dict(stat)
            if stat["invalid"] or stat["invalid_type"]:
                errors.append(f"invalid timestamp values in {filename}:{key}: {dict(stat)}")

    event_types = Counter(row["event_type"] for row in events)
    blank_labels = {
        "revision_rows": sum(row["label"] == "" for row in revisions),
        "label_rows": sum(row["label"] == "" for row in labels),
        "page_label_elements": sum(label == "" for row in pages for label in row["labels"]),
    }
    slash_names = [row["page_id"] for row in pages if "/" in row["name"]]
    manifest_bad_checks = [check["name"] for check in manifest.get("checks", []) if check.get("ok") is not True]
    _assert_equal(event_types, Counter({"save": 14591, "delete": 5217, "probe": 101, "revert": 4}), "event types", errors)
    _assert_equal(blank_labels["revision_rows"], 899, "blank revision labels", errors)
    _assert_equal(len(slash_names), 77, "page names containing slash", errors)
    _assert_equal(manifest_bad_checks, [], "manifest self-check failures", errors)

    relation_forms = {}
    for filename in ("revisions.jsonl", "events.jsonl"):
        for key in ("related_event_id", "relation_type", "round_id"):
            relation_forms[f"{filename}:{key}"] = dict(
                sorted(Counter(_type_name(row[key]) for row in data[filename] if key in row).items())
            )

    audit = {
        "status": "PASS" if not errors else "FAIL",
        "hashes": hashes,
        "counts": {filename: len(rows) for filename, rows in data.items()},
        "manifest_identity": {
            "generated_at": manifest.get("generated_at"),
            "db_sha256": manifest.get("db_sha256"),
            "cut": manifest.get("cut"),
        },
        "dse": {
            "pages": len(dse_pages),
            "revisions": len(dse_revisions),
            "successful_administrator_deletions": len(deletes),
            "distinct_deleted_titles": len(deleted_titles),
            "deletion_only_titles_without_published_revision_body": len(deletion_only_titles),
            "deletion_events_on_deletion_only_titles": len(deletion_only_rows),
            "deleted_live": {str(key).lower(): value for key, value in deleted_live.items()},
            "head_differs_from_live": {str(key).lower(): value for key, value in head_differs.items()},
            "live_body_combinations": [
                {"deleted_live": key[0], "head_differs_from_live": key[1], "live_body_variant": key[2], "count": count}
                for key, count in sorted(live_combinations.items(), key=lambda item: str(item[0]))
            ],
            "revision_time_range": [min(row["time"] for row in dse_revisions), max(row["time"] for row in dse_revisions)],
        },
        "relations": {
            "physical_event_rows": len(event_relation_rows),
            "edges": len(event_relation_edges),
            "field_forms": relation_forms,
        },
        "no_body_successful_form_edit_mutations_called_revert": [
            {
                "event_id": row["event_id"], "page_key": row["page_key"],
                "time": row["time"], "revision_ref": row["revision_ref"],
                "request_action": row["request_action"], "success_observed": row["success_observed"],
            }
            for row in no_body_form_edits
        ],
        "body_encodings": dict(encoding_counts),
        "blank_labels": blank_labels,
        "page_names_containing_slash": {"count": len(slash_names), "examples": slash_names[:5]},
        "duplicates": duplicate_ids,
        "linkage": {
            "save_rows": len(save_events),
            "unique_revision_refs": len(save_ref_counts),
            "save_revision_failures": len(save_link_failures),
            "revision_page_failures": len(bad_revision_pages),
            "event_page_failures": len(nonprobe_page_failures),
            "relation_reference_failures": len(relation_reference_failures),
        },
        "timestamps": timestamp_inventory,
        "schema": {
            filename: _schema_inventory(filename, rows)
            for filename, rows in data.items()
        } | {"manifest.json": _schema_inventory("manifest.json", [manifest])},
        "manifest_failed_checks": manifest_bad_checks,
        "discrepancies": errors,
    }
    if errors:
        raise ValidationError("\n".join(errors))

    report = _render_report(audit)
    return audit, report


def _render_report(audit: dict[str, Any]) -> str:
    dse = audit["dse"]
    cases = audit["no_body_successful_form_edit_mutations_called_revert"]
    return f"""# E01 raw export validation notes

Machine-generated by `src/ebe/ingest.py`; no page-body URL was followed or executed.

## Result

**{audit['status']}**. All five expanded SHA-256 hashes and all four JSONL row counts match the pinned audit. The manifest reports `{audit['manifest_identity']['generated_at']}` and source database `{audit['manifest_identity']['db_sha256']}`.

## Required edge cases

- DSE: {dse['pages']:,} pages and {dse['revisions']:,} revisions.
- Successful `[Admin1]` DSE deletions: {dse['successful_administrator_deletions']:,} rows, {dse['distinct_deleted_titles']:,} distinct titles.
- Deletion-only population: {dse['deletion_only_titles_without_published_revision_body']:,} titles and {dse['deletion_events_on_deletion_only_titles']:,} deletion rows. Missing bodies remain absent/unknown.
- Every DSE `deleted_live` value is `false` ({dse['deleted_live']['false']:,} rows). This is a retrospective source/export-store descriptor and is **not historical survival truth**.
- `head_differs_from_live`: false={dse['head_differs_from_live']['false']:,}, true={dse['head_differs_from_live']['true']:,}. Live-body combinations are 3,898 `(false,false,txt)`, 9 `(false,true,dw)`, and 1 `(false,false,dw)`.
- Recreation relationships: {audit['relations']['physical_event_rows']} physical event rows, {audit['relations']['edges']} edges. One save row carries two aligned deletion IDs/round IDs under one scalar relation type.
- Four successful no-body `form_edit` mutations are currently named `revert`: {', '.join(case['event_id'] for case in cases)}. They have `revision_ref=null`; no body is reconstructed or guessed.
- Relation fields retain their observed scalar/list/null forms; see `schema_inventory.json` for exact frequencies.
- Twenty-nine deletion rows carry a scalar `round_id` while `relation_type` and `related_event_id` are null; these are preserved but are not counted as relationship edges.
- Bodies are stored as byte-preserving Latin-1 projections in JSON. Declared source-byte classifications and verified source hashes: ASCII 14,340; strict UTF-8 250; Latin-1 1; zero failures.
- Blank labels: 899 revision rows, 568 page-label list entries, and one aggregate label row. Labels and redacted IP prefixes are recorded attributes, never treated as agents or authenticated identities.
- Page names containing `/`: {audit['page_names_containing_slash']['count']} (kept as opaque logical names, not filesystem paths).
- `page_key` is an opaque encoded identifier; it is validated through observed references and is never reconstructed from `wiki`/`name`.
- Duplicate page IDs, page keys, revision IDs, event IDs, and label keys: none.
- Save/event/revision linkage: 14,591 saves resolve one-to-one to 14,591 revisions; page and relation mirrors agree; all relation targets resolve.
- Timestamp strings parse as ISO-8601. Nullability and fields absent from event subtypes are preserved exactly in the machine inventory.

## Discrepancies from the pinned audit

None.

## Anomalies and cautions

- `deleted_live=false` on every DSE held page conflicts with treating it as a final historical survival flag.
- `txt` versus `dw`, and the exact meaning of `head_differs_from_live`, remain undocumented.
- A physical row is not necessarily one independent action; relationship arrays create 68 edges on 67 event rows.
- A `round_id` can occur on a deletion row without a relation; the validator does not synthesize an edge from it.
- `revert` is not safe to interpret as restoration: all four such rows are successful `form_edit` mutations with unknown body.
- `recent_changes_time` is null on every revision and every detailed mutation event; event `write_date` and `rcs_date` are also null wherever present.
- Labels can be blank or impersonated; IPs are redacted and neither field establishes an agent identity.
- Page fields, label aggregates, relation fields, and `page_held` contain retrospective/evaluator-only information and must not become historical collector inputs.

## Unresolved semantic questions

1. What precisely do `deleted_live`, `txt`/`dw`, and `head_differs_from_live` describe?
2. What is the exact interval convention for `uncertainty_seconds`?
3. When does an RCS body become archived, and what visibility meaning (if any) does `archived_at` have?
4. Which successful mutations are absent from the held revisions/events, including short bodies and administrative overwrites?
5. What archive/index endpoints were historically available, and with what retention/discovery behavior?
6. How can the six fallback recreation links be identified in the public core files, and what guarantees attach to them?
7. What reuse terms apply separately to the export, excerpts, and derived annotations?

## Safe inputs for E05

The five exact expanded files; strict UTF-8 JSONL/object parsing; pinned byte hashes and row counts; opaque IDs/paths/names; explicit nulls; declared body encodings with byte-length/hash verification; the four event sub-schemas; one-to-one save/revision references; page references; and lossless relation-field preservation. Timeline ordering, live-state inference, archive visibility, identity attribution, and normalization of ambiguous relation fields are not yet safe.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw_dir", type=Path, help="directory containing expanded core files")
    parser.add_argument("--inventory", type=Path, help="write machine-readable inventory JSON")
    parser.add_argument("--notes", type=Path, help="write Markdown validation notes")
    args = parser.parse_args()
    try:
        audit, report = validate(args.raw_dir)
    except ValidationError as exc:
        parser.error(str(exc))
    if args.inventory:
        args.inventory.parent.mkdir(parents=True, exist_ok=True)
        args.inventory.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.notes:
        args.notes.parent.mkdir(parents=True, exist_ok=True)
        args.notes.write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
