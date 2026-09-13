"""Exact, deterministic reporting helpers for frozen X13 result CSVs."""
from __future__ import annotations

import csv
import json
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence, Any

PRIMARY_LABELS = ("THRESHOLD_MET_IN_CONDITIONAL_BENCHMARK",
 "POSITIVE_BUT_BELOW_PREREGISTERED_THRESHOLD", "TIE",
 "PCD_BETTER_ON_PRIMARY_ESTIMAND", "PRIMARY_UNMATCHED",
 "NO_PREREGISTERED_EVENT_CONFIGURATION_MATCHED", "NA_EMPTY_DENOMINATOR",
 "NOT_EVALUABLE")

RESULT_SCHEMAS: dict[str, tuple[str, ...]] = {
 "completeness.csv": ("run_id","split","metric","numerator","denominator","percentage","status"),
 "all_configurations.csv": ("run_id","block","policy","phase","status"),
 "headline.csv": ("event_run_id","comparator_family","difference_pp","label"),
 "admissibility.csv": ("event_run_id","event_requests","max_admissible_requests","admissible"),
 "cost_envelopes.csv": ("run_id","requests","retained_bytes","nondominated"),
 "phase_values.csv": ("family","phase","value"),
 "latency_checkpoint.csv": ("run_id","lag_us","delay_us","value"),
 "baseline_robustness.csv": ("run_id","policy","value"),
 "group_metrics.csv": ("run_id","group_id","numerator","denominator","percentage"),
 "group_robustness.csv": ("run_id","micro","macro","loo_min","loo_max"),
 "unit_retention.csv": ("run_id","evidence_id","retained","witness_fragment_ids","witness_packet_ids"),
 "delay.csv": ("run_id","evidence_id","status","delay_seconds"),
 "eligibility_missingness.csv": ("evidence_id","eligible","reason"),
 "unknowns.csv": ("run_id","evidence_id","reason_code"),
 "chronology_sensitivity.csv": ("run_id","status","nominal","full_min","full_max"),
 "archive_sensitivity.csv": ("run_id","archive_mode","value"),
 "case_walkthrough.csv": ("run_id","case_id","stage","value"),
 "overhead.csv": ("run_id","elapsed_seconds","cpu_seconds","rss_bytes","artifact_disk_bytes","reused_from"),
}


def exact_percentage(numerator: int, denominator: int) -> Fraction | None:
    return None if denominator == 0 else Fraction(100 * numerator, denominator)


def primary_label(difference_pp: Fraction | None, *, admissible: bool,
                  event_matched: bool = True, evaluable: bool = True,
                  empty_denominator: bool = False) -> str:
    if not evaluable: return "NOT_EVALUABLE"
    if empty_denominator: return "NA_EMPTY_DENOMINATOR"
    if not event_matched: return "NO_PREREGISTERED_EVENT_CONFIGURATION_MATCHED"
    if not admissible: return "PRIMARY_UNMATCHED"
    if difference_pp is None: return "NOT_EVALUABLE"
    if difference_pp >= 10: return "THRESHOLD_MET_IN_CONDITIONAL_BENCHMARK"
    if difference_pp > 0: return "POSITIVE_BUT_BELOW_PREREGISTERED_THRESHOLD"
    if difference_pp == 0: return "TIE"
    return "PCD_BETTER_ON_PRIMARY_ESTIMAND"


def linear_quantile(values: Sequence[Fraction | int], p: Fraction) -> Fraction:
    if not values: raise ValueError("quantile requires at least one value")
    if p < 0 or p > 1: raise ValueError("p must be in [0,1]")
    ordered = sorted(Fraction(x) for x in values)
    index = Fraction(len(ordered) - 1) * p
    low = index.numerator // index.denominator
    high = min(low + 1, len(ordered) - 1)
    weight = index - low
    return ordered[low] * (1 - weight) + ordered[high] * weight


def phase_summary(values: Sequence[Fraction | int]) -> dict[str, Fraction]:
    if len(values) != 60: raise ValueError("frozen phase summary requires exactly 60 values")
    vals = [Fraction(x) for x in values]
    return {"j0": vals[0], "mean": sum(vals, Fraction()) / 60,
            "min": min(vals), "max": max(vals),
            "p10": linear_quantile(vals, Fraction(1,10)),
            "median": linear_quantile(vals, Fraction(1,2)),
            "p90": linear_quantile(vals, Fraction(9,10))}


def request_admissible(event_requests: int, periodic_requests: Sequence[int]) -> bool:
    if len(periodic_requests) != 60:
        raise ValueError("admissibility requires all 60 periodic phases")
    return event_requests <= min(periodic_requests)


def primary_difference(event_numerator: int, denominator: int,
                       periodic_numerators: Sequence[int]) -> Fraction | None:
    if denominator == 0: return None
    if len(periodic_numerators) != 60:
        raise ValueError("primary contrast requires all 60 phases")
    event = Fraction(100 * event_numerator, denominator)
    periodic = sum((Fraction(100 * n, denominator) for n in periodic_numerators),
                   Fraction()) / 60
    return event - periodic


def group_robustness(rows: Iterable[tuple[str, int, int]]) -> dict[str, Any]:
    groups=[(group, n, d) for group,n,d in rows if d > 0]
    if not groups:
        return {"micro": None, "macro": None, "loo_min": None, "loo_max": None,
                "group_count": 0}
    total_n=sum(n for _,n,_ in groups); total_d=sum(d for _,_,d in groups)
    macro=sum((Fraction(n,d) for _,n,d in groups),Fraction())/len(groups)
    loo=[Fraction(total_n-n,total_d-d) for _,n,d in groups if total_d-d>0]
    return {"micro":Fraction(total_n,total_d),"macro":macro,
            "loo_min":min(loo) if loo else None,"loo_max":max(loo) if loo else None,
            "group_count":len(groups)}


def create_result_scaffolding(repo: Path) -> Path:
    root = repo.resolve() / "runs" / "FINAL_PRE_X13_DEADLINE_v1" / "results"
    root.mkdir(parents=True, exist_ok=True)
    for name, fields in RESULT_SCHEMAS.items():
        path=root/name
        if not path.exists():
            with path.open("w", newline="", encoding="utf-8") as stream:
                csv.writer(stream, lineterminator="\n").writerow(fields)
    reproducibility=root/"reproducibility.md"
    if not reproducibility.exists():
        reproducibility.write_text(
            "# X13 reproducibility\n\nGate 1 schema only. No real policy/evidence scores are present.\n",
            encoding="utf-8", newline="\n")
    status=root/"status_index.json"
    if not status.exists():
        status.write_text('{"authorization":"NOT_AUTHORIZED","rows":{}}\n',
                          encoding="utf-8", newline="\n")
    return root


def build_synthetic_report(repo: Path) -> Path:
    """Exercise report aggregation with visibly invented values."""
    root = repo.resolve() / "runs" / "FINAL_PRE_X13_DEADLINE_v1" / "synthetic_reporting"
    root.mkdir(parents=True, exist_ok=True)
    values = [Fraction(i % 24, 23) * 100 for i in range(60)]
    summary = phase_summary(values)
    with (root / "phase_values.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(("fixture", "phase", "numerator", "denominator"))
        for j in range(60): writer.writerow(("SYNTHETIC_INVENTED", j, j % 24, 23))
    payload = {"fixture": "SYNTHETIC_INVENTED",
               "summary": {key: [value.numerator, value.denominator]
                           for key, value in summary.items()},
               "threshold_label": primary_label(Fraction(10), admissible=True)}
    (root / "summary.json").write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8", newline="\n")
    return root


def generate_plots(results_dir: Path, output_dir: Path) -> None:
    """Generate the six frozen plots only from populated result CSVs.

    Kept explicit (never called by Gate 1) so empty schemas cannot become fake
    zero-valued plots.
    """
    required = ("coverage_cost", "phase_distribution", "latency_checkpoint",
                "baseline_robustness", "archive_sensitivity", "case_walkthrough")
    def has_rows(path: Path) -> bool:
        with path.open(encoding="utf-8", newline="") as stream:
            return next(csv.DictReader(stream), None) is not None
    if not any(has_rows(results_dir / name) for name in RESULT_SCHEMAS):
        raise ValueError("refusing to plot empty Gate 1 result schemas")
    import matplotlib.pyplot as plt
    output_dir.mkdir(parents=True, exist_ok=True)
    for name in required:
        fig, ax = plt.subplots(figsize=(7, 4)); ax.set_title(name.replace("_", " "))
        if "coverage" in name: ax.set_ylim(0, 100)
        if name in {"phase_distribution", "baseline_robustness", "archive_sensitivity"}:
            ax.axhline(0, color="black", linewidth=.8); ax.axhline(10, linestyle="--"); ax.axhline(-10, linestyle="--")
        fig.savefig(output_dir / f"{name}.svg"); fig.savefig(output_dir / f"{name}.png", dpi=150)
        plt.close(fig)


__all__ = ["PRIMARY_LABELS", "RESULT_SCHEMAS", "build_synthetic_report", "create_result_scaffolding",
           "exact_percentage", "generate_plots", "group_robustness", "linear_quantile",
           "phase_summary", "primary_difference", "primary_label", "request_admissible"]
