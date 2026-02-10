"""Latency and fallback summary aggregation script (ST-030)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEFAULT_LATENCY_LOG = REPO_ROOT / "logs" / "pipeline_latency.jsonl"
DEFAULT_FALLBACK_LOG = REPO_ROOT / "logs" / "fallback_metrics.jsonl"


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Load JSONL file into a list of dicts. Returns empty list if missing."""
    if not path.exists():
        return []
    records: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").strip().splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def _percentile(values: List[float], p: float) -> Optional[float]:
    """Compute p-th percentile using linear interpolation."""
    if not values:
        return None
    s = sorted(values)
    k = (len(s) - 1) * p / 100.0
    f = int(k)
    c = min(f + 1, len(s) - 1)
    d = k - f
    return round(s[f] + d * (s[c] - s[f]), 3)


def _percentile_set(values: List[float]) -> Dict[str, Optional[float]]:
    """Compute p50, p95, p99 for a list of values."""
    return {
        "p50": _percentile(values, 50),
        "p95": _percentile(values, 95),
        "p99": _percentile(values, 99),
    }


def compute_latency_stats(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute latency percentiles for total_ms and per-step."""
    if not records:
        return {
            "count": 0,
            "total_ms": _percentile_set([]),
            "steps": {},
        }

    total_values = [r["total_ms"] for r in records]

    step_names: set = set()
    for r in records:
        step_names.update(r.get("steps", {}).keys())

    steps_stats: Dict[str, Any] = {}
    for name in sorted(step_names):
        values = [r["steps"][name] for r in records if name in r.get("steps", {})]
        steps_stats[name] = _percentile_set(values)

    return {
        "count": len(records),
        "total_ms": _percentile_set(total_values),
        "steps": steps_stats,
    }


def compute_latency_comparison(
    records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Split records by llm_enabled and compute stats for each group."""
    with_llm = [r for r in records if r.get("llm_enabled") is True]
    without_llm = [r for r in records if r.get("llm_enabled") is not True]
    return {
        "all": compute_latency_stats(records),
        "with_llm": compute_latency_stats(with_llm),
        "without_llm": compute_latency_stats(without_llm),
    }


def compute_fallback_rates(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute fallback, error, and success rates."""
    total = len(records)
    if total == 0:
        return {
            "count": 0,
            "fallback_rate": 0.0,
            "error_rate": 0.0,
            "success_rate": 0.0,
            "outcome_counts": {},
        }

    outcome_counts: Dict[str, int] = {}
    for r in records:
        outcome = r.get("llm_outcome", "unknown")
        outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1

    return {
        "count": total,
        "fallback_rate": round(outcome_counts.get("fallback", 0) / total, 4),
        "error_rate": round(outcome_counts.get("error", 0) / total, 4),
        "success_rate": round(outcome_counts.get("success", 0) / total, 4),
        "outcome_counts": outcome_counts,
    }


def _time_range(
    latency_records: List[Dict[str, Any]],
    fallback_records: List[Dict[str, Any]],
) -> Dict[str, Optional[str]]:
    """Extract first and last timestamps across both log files."""
    timestamps: List[str] = []
    for r in latency_records + fallback_records:
        ts = r.get("timestamp")
        if ts:
            timestamps.append(ts)
    if not timestamps:
        return {"first": None, "last": None}
    timestamps.sort()
    return {"first": timestamps[0], "last": timestamps[-1]}


def build_report(
    latency_records: List[Dict[str, Any]],
    fallback_records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Build the full aggregation report."""
    return {
        "latency": compute_latency_comparison(latency_records),
        "fallback": compute_fallback_rates(fallback_records),
        "time_range": _time_range(latency_records, fallback_records),
    }


def main() -> None:
    """Load logs from default paths and print JSON report."""
    latency_records = load_jsonl(DEFAULT_LATENCY_LOG)
    fallback_records = load_jsonl(DEFAULT_FALLBACK_LOG)

    report = build_report(latency_records, fallback_records)
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
