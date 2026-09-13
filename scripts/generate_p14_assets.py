#!/usr/bin/env python3
"""Generate P14 SVG figures from authorized X13 CSVs or labeled schematics.

When ``runs/FINAL_PRE_X13_DEADLINE_v1/results/`` contains no CSVs, this script
renders round-number illustrative points.  They are not experiment findings:
each output carries repeated in-image ``SYNTHETIC — pending X13 execution``
watermarks.  If CSVs are present but cannot supply the required columns, the
script stops instead of replacing real, incomplete data with placeholders.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from html import escape
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = REPO_ROOT / "runs" / "FINAL_PRE_X13_DEADLINE_v1" / "results"
FIGURES_DIR = REPO_ROOT / "figures"
EVIDENCE_PATH = REPO_ROOT / "annotations" / "evidence.jsonl"
WATERMARK = "SYNTHETIC — pending X13 execution"

WARNING_ID = "PROP-20260619-04"
BACKUP_ID = "PROP-20260619-05"

EXPECTED_EVIDENCE = {
    WARNING_ID: {
        "rev_id": "dse~DataUSAConstructionWageSep18Live@16",
        "char_span": [3387, 3547],
        "starts_with": "AUG17 NOTICE: wiki cleanup/deletion sweep",
    },
    BACKUP_ID: {
        "rev_id": "dse~ZZZDataUSAConstructionWageLive@1",
        "char_span": [32, 276],
        "starts_with": "BACKUP LIVE COORDINATION",
    },
}


def verify_construction_evidence() -> dict[str, dict[str, Any]]:
    """Read the frozen annotation file and reject a swapped case mapping."""
    found: dict[str, dict[str, Any]] = {}
    with EVIDENCE_PATH.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            if record.get("evidence_id") in EXPECTED_EVIDENCE:
                found[record["evidence_id"]] = record

    for evidence_id, expected in EXPECTED_EVIDENCE.items():
        record = found.get(evidence_id)
        if record is None:
            raise ValueError(f"Frozen evidence record is absent: {evidence_id}")
        if record.get("rev_id") != expected["rev_id"]:
            raise ValueError(f"Unexpected revision for {evidence_id}: {record.get('rev_id')}")
        if record.get("char_span") != expected["char_span"]:
            raise ValueError(f"Unexpected span for {evidence_id}: {record.get('char_span')}")
        if not record.get("quotation", "").startswith(expected["starts_with"]):
            raise ValueError(f"Unexpected quotation for {evidence_id}")

    print(
        "Verified frozen evidence mapping: "
        f"{WARNING_ID}=warning; {BACKUP_ID}=ZZZ backup body."
    )
    return found


def number(value: str | None) -> float | None:
    """Parse a CSV numeric field; blank/NA values remain unavailable."""
    if value is None:
        return None
    cleaned = value.strip().replace("%", "").replace(",", "")
    if not cleaned or cleaned.lower() in {"na", "n/a", "null", "none"}:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def first_value(row: dict[str, str], names: tuple[str, ...]) -> str | None:
    lowered = {key.lower(): value for key, value in row.items()}
    for name in names:
        if name in lowered:
            return lowered[name]
    return None


def real_csvs() -> list[Path]:
    if not RESULTS_DIR.exists():
        return []
    return sorted(path for path in RESULTS_DIR.glob("*.csv") if path.is_file())


def load_real_points(paths: list[Path]) -> list[dict[str, Any]]:
    """Load a plottable policy table without manufacturing unavailable values."""
    policy_names = ("policy", "policy_name", "configuration", "config", "config_name", "label")
    coverage_names = (
        "critical_core_coverage_pct",
        "core_coverage_pct",
        "coverage_pct",
        "coverage",
    )
    request_names = ("requests", "request_count", "total_requests", "live_body_requests")
    unmatched_names = ("admissibility", "admissibility_status", "match_status", "primary_status")

    for path in paths:
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        if not rows:
            continue
        points: list[dict[str, Any]] = []
        for row in rows:
            label = first_value(row, policy_names)
            coverage = number(first_value(row, coverage_names))
            requests = number(first_value(row, request_names))
            if label is None or coverage is None or requests is None:
                continue  # NA is not plotted as zero.
            if not 0 <= coverage <= 100 or requests < 0:
                raise ValueError(f"Out-of-range real value in {path.name}: {row}")
            status = (first_value(row, unmatched_names) or "").upper()
            points.append(
                {
                    "label": label,
                    "coverage": coverage,
                    "requests": requests,
                    "unmatched": "UNMATCHED" in status,
                }
            )
        if points:
            print(f"Loaded {len(points)} real plot rows from {path.relative_to(REPO_ROOT)}")
            return points
    raise ValueError(
        "REAL mode was selected because CSVs exist, but none expose a supported "
        "policy, coverage, and request column set. Refusing synthetic fallback."
    )


def synthetic_points() -> list[dict[str, Any]]:
    """Round-number schematic points, intentionally not plausible experiment output."""
    return [
        {"label": "final live", "requests": 40.0, "coverage": 20.0, "unmatched": False},
        {"label": "periodic 15m", "requests": 120.0, "coverage": 40.0, "unmatched": False},
        {"label": "periodic + feed", "requests": 200.0, "coverage": 50.0, "unmatched": True},
        {"label": "event queue", "requests": 280.0, "coverage": 70.0, "unmatched": False},
        {"label": "archive sensitivity", "requests": 360.0, "coverage": 90.0, "unmatched": True},
    ]


def synthetic_watermark(width: int, height: int) -> list[str]:
    """Repeat the warning in header, body, and footer of every synthetic SVG."""
    text = escape(WATERMARK)
    return [
        f'<rect x="0" y="0" width="{width}" height="42" fill="#7f1d1d"/>',
        f'<text x="{width / 2}" y="28" text-anchor="middle" font-size="18" '
        f'font-weight="700" fill="#ffffff">{text}</text>',
        f'<text x="{width / 2}" y="{height / 2}" text-anchor="middle" font-size="34" '
        f'font-weight="700" fill="#991b1b" opacity="0.24" '
        f'transform="rotate(-24 {width / 2} {height / 2})">{text}</text>',
        f'<text x="{width / 2}" y="{height - 16}" text-anchor="middle" font-size="14" '
        f'font-weight="700" fill="#991b1b">{text}</text>',
    ]


def svg_root(width: int, height: int) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text { font-family: Arial, Helvetica, sans-serif; }</style>',
    ]


def write_svg(path: Path, parts: list[str]) -> None:
    path.write_text("\n".join([*parts, "</svg>"]), encoding="utf-8")
    print(f"Wrote {path.relative_to(REPO_ROOT)}")


def rounded_max(values: list[float]) -> float:
    maximum = max(values, default=1.0)
    scale = 10 ** max(0, int(math.floor(math.log10(maximum))) - 1)
    return max(scale * math.ceil(maximum / scale), scale)


def coverage_cost_svg(path: Path, points: list[dict[str, Any]], synthetic: bool) -> None:
    width, height = 1000, 650
    left, top, right, bottom = 110, 110, 70, 100
    plot_w, plot_h = width - left - right, height - top - bottom
    x_max = rounded_max([point["requests"] for point in points])
    parts = svg_root(width, height)
    parts.extend(
        [
            f'<text x="{left}" y="72" font-size="25" font-weight="700" fill="#172554">'
            'Evidence coverage vs. request cost</text>',
            f'<text x="{left}" y="96" font-size="14" fill="#475569">'
            + (
                'Schematic only: round-number illustrative positions; no X13 result.'
                if synthetic
                else 'Rendered from available X13 CSV rows; unavailable values are omitted.'
            )
            + '</text>',
        ]
    )
    for value in range(0, 101, 20):
        y = top + plot_h - value * plot_h / 100
        parts.append(f'<line x1="{left}" y1="{y}" x2="{left + plot_w}" y2="{y}" stroke="#dbeafe"/>')
        parts.append(f'<text x="{left - 14}" y="{y + 5}" text-anchor="end" font-size="13" fill="#475569">{value}%</text>')
    for index in range(6):
        value = x_max * index / 5
        x = left + plot_w * index / 5
        parts.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{top + plot_h}" stroke="#f1f5f9"/>')
        parts.append(f'<text x="{x}" y="{top + plot_h + 24}" text-anchor="middle" font-size="12" fill="#475569">{value:.0f}</text>')
    parts.extend(
        [
            f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" stroke="#1e293b" stroke-width="2"/>',
            f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" stroke="#1e293b" stroke-width="2"/>',
            f'<text x="{left + plot_w / 2}" y="{height - 48}" text-anchor="middle" font-size="15" font-weight="700" fill="#1e293b">Requests (count)</text>',
            f'<text x="30" y="{top + plot_h / 2}" text-anchor="middle" font-size="15" font-weight="700" fill="#1e293b" transform="rotate(-90 30 {top + plot_h / 2})">Critical evidence coverage (0–100%)</text>',
        ]
    )
    colors = ["#2563eb", "#ea580c", "#7c3aed", "#059669", "#be123c", "#0369a1"]
    for index, point in enumerate(points):
        x = left + point["requests"] * plot_w / x_max
        y = top + plot_h - point["coverage"] * plot_h / 100
        color = colors[index % len(colors)]
        fill = "#ffffff" if point["unmatched"] else color
        parts.append(f'<circle cx="{x}" cy="{y}" r="9" fill="{fill}" stroke="{color}" stroke-width="3"/>')
        suffix = " (unmatched)" if point["unmatched"] else ""
        parts.append(f'<text x="{x + 13}" y="{y - 10}" font-size="12" font-weight="700" fill="{color}">{escape(point["label"])}{suffix}</text>')
    parts.extend(
        [
            f'<rect x="{left + 12}" y="{top + plot_h - 54}" width="340" height="38" rx="5" fill="#f8fafc" stroke="#cbd5e1"/>',
            f'<circle cx="{left + 32}" cy="{top + plot_h - 35}" r="7" fill="#ffffff" stroke="#475569" stroke-width="2"/>',
            f'<text x="{left + 48}" y="{top + plot_h - 30}" font-size="12" fill="#334155">Hollow point = unmatched comparison</text>',
            f'<text x="{left + 12}" y="{top + plot_h - 68}" font-size="11" fill="#475569">No connecting lines. NA values are omitted, never shown as zero.</text>',
        ]
    )
    if synthetic:
        parts.extend(synthetic_watermark(width, height))
    write_svg(path, parts)


def text_lines(value: str, limit: int = 27) -> list[str]:
    words, lines, current = value.split(), [], []
    for word in words:
        proposal = " ".join([*current, word])
        if current and len(proposal) > limit:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines


def case_walkthrough_svg(path: Path, evidence: dict[str, dict[str, Any]], synthetic: bool) -> None:
    width, height = 1060, 720
    parts = svg_root(width, height)
    parts.extend(
        [
            '<text x="70" y="76" font-size="25" font-weight="700" fill="#172554">Construction / ZZZ: source-grounded history panel</text>',
            '<text x="70" y="101" font-size="14" fill="#475569">Development case GRP-01-CONSTRUCT — mechanism sketch, not a scored collector result</text>',
            '<line x1="100" y1="180" x2="960" y2="180" stroke="#94a3b8" stroke-width="4"/>',
        ]
    )
    timeline = [
        (150, "14:05:02 UTC", f"Warning published ({WARNING_ID})", "Warning names the ZZZ fallback.", "#b45309"),
        (390, "14:06:38 UTC", f"ZZZ body published ({BACKUP_ID})", "Backup body names the original page.", "#2563eb"),
        (690, "15:46:37 UTC", "Original title deleted", "Successful deletion event recorded.", "#dc2626"),
        (900, "15:46:49 UTC", "ZZZ title deleted", "Recorded 12 seconds after original.", "#991b1b"),
    ]
    for x, time_label, heading, body, color in timeline:
        parts.extend(
            [
                f'<circle cx="{x}" cy="180" r="12" fill="{color}" stroke="#ffffff" stroke-width="3"/>',
                f'<text x="{x}" y="150" text-anchor="middle" font-size="12" font-weight="700" fill="#334155">{time_label}</text>',
                f'<rect x="{x - 100}" y="205" width="200" height="96" rx="8" fill="#f8fafc" stroke="{color}"/>',
                f'<text x="{x}" y="230" text-anchor="middle" font-size="12" font-weight="700" fill="#1e293b">{escape(heading)}</text>',
            ]
        )
        for offset, line in enumerate(text_lines(body)):
            parts.append(f'<text x="{x}" y="{253 + 15 * offset}" text-anchor="middle" font-size="11" fill="#475569">{escape(line)}</text>')
    parts.extend(
        [
            '<rect x="70" y="340" width="920" height="38" rx="6" fill="#e0f2fe"/>',
            '<text x="90" y="365" font-size="14" font-weight="700" fill="#0c4a6e">What the collection mechanisms imply — not measured outcomes</text>',
        ]
    )
    mechanisms = [
        ("P15", "Fixed periodic sweep", "Whether it sees the ZZZ body depends on phase and discovery timing."),
        ("PCD15", "Feed can name a title", "The GET schedule still follows its periodic sweep."),
        ("E30", "Event can schedule a GET", "Admission, completion, and FIFO retention still determine availability."),
    ]
    for index, (label, heading, description) in enumerate(mechanisms):
        x = 70 + index * 310
        parts.extend(
            [
                f'<rect x="{x}" y="400" width="290" height="142" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="2"/>',
                f'<rect x="{x}" y="400" width="290" height="31" rx="8" fill="#1e3a8a"/>',
                f'<text x="{x + 14}" y="421" font-size="13" font-weight="700" fill="#ffffff">{label}: {heading}</text>',
            ]
        )
        for line_index, line in enumerate(text_lines(description, 33)):
            parts.append(f'<text x="{x + 14}" y="{462 + line_index * 17}" font-size="12" fill="#334155">{escape(line)}</text>')
    parts.extend(
        [
            '<rect x="70" y="576" width="920" height="67" rx="8" fill="#fffbeb" stroke="#d97706"/>',
            '<text x="90" y="603" font-size="13" font-weight="700" fill="#78350f">Interpretive limit</text>',
            '<text x="90" y="625" font-size="12" fill="#78350f">The source records a warning and later backup body; it does not establish intent, distinct agents, permanent erasure, or a measured policy advantage.</text>',
        ]
    )
    if synthetic:
        parts.extend(synthetic_watermark(width, height))
    write_svg(path, parts)


def main() -> int:
    evidence = verify_construction_evidence()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    csv_paths = real_csvs()
    if csv_paths:
        print(f"MODE: REAL — found {len(csv_paths)} CSV file(s) in {RESULTS_DIR.relative_to(REPO_ROOT)}")
        points = load_real_points(csv_paths)
        synthetic = False
    else:
        location = RESULTS_DIR.relative_to(REPO_ROOT)
        print(f"MODE: SYNTHETIC — no real CSVs found at {location}; rendering labeled schematics.")
        points = synthetic_points()
        synthetic = True

    coverage_cost_svg(FIGURES_DIR / "coverage_cost.svg", points, synthetic)
    case_walkthrough_svg(FIGURES_DIR / "case_walkthrough.svg", evidence, synthetic)
    print("No X13 result claim was generated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
