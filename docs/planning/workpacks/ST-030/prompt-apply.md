# Codex APPLY Prompt — ST-030: Latency and Fallback Summary Aggregation Script

## Role
You are a senior Python developer creating a metrics aggregation script and its tests.

## Context (from PLAN findings)

- pipeline_latency.jsonl keys: command_id, trace_id, total_ms, steps, llm_enabled, timestamp.
- Steps keys: validate_command_ms, detect_intent_ms, registry_ms, core_logic_ms, validate_decision_ms.
- fallback_metrics.jsonl keys: command_id, trace_id, intent, decision_action, llm_outcome,
  fallback_reason, deterministic_used, llm_latency_ms, components, timestamp.
- Possible llm_outcome values: "success", "fallback", "error", "skipped", "deterministic_only".
- Default paths: `logs/pipeline_latency.jsonl`, `logs/fallback_metrics.jsonl`.
- No naming conflicts: `skills/observability/` and `tests/test_aggregate_metrics.py` don't exist.
- Skills pattern: REPO_ROOT + sys.path (from evaluate_golden.py).
- No external dependencies needed for percentile computation.

## Files to Create

### 1. `skills/observability/scripts/aggregate_metrics.py` (NEW)

Create directory `skills/observability/scripts/` first, then create this file with EXACT content:

```python
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
```

### 2. `tests/test_aggregate_metrics.py` (NEW)

Create this file with EXACT content:

```python
"""Tests for latency and fallback aggregation script (ST-030)."""

import json
import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
AGG_SCRIPTS_DIR = BASE_DIR / "skills" / "observability" / "scripts"

if str(AGG_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(AGG_SCRIPTS_DIR))
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from aggregate_metrics import (
    build_report,
    compute_fallback_rates,
    compute_latency_comparison,
    compute_latency_stats,
)


def _make_latency_record(total_ms=10.0, llm_enabled=False, steps=None):
    """Helper to create a synthetic latency record."""
    return {
        "command_id": "cmd-test",
        "trace_id": "trace-test",
        "total_ms": total_ms,
        "steps": steps or {
            "validate_command_ms": 1.0,
            "detect_intent_ms": 1.0,
            "registry_ms": 1.0,
            "core_logic_ms": 5.0,
            "validate_decision_ms": 2.0,
        },
        "llm_enabled": llm_enabled,
        "timestamp": "2026-02-01T10:00:00+00:00",
    }


def _make_fallback_record(llm_outcome="skipped", fallback_reason="policy_disabled"):
    """Helper to create a synthetic fallback record."""
    return {
        "command_id": "cmd-test",
        "trace_id": "trace-test",
        "intent": "add_shopping_item",
        "decision_action": "start_job",
        "llm_outcome": llm_outcome,
        "fallback_reason": fallback_reason,
        "deterministic_used": True,
        "llm_latency_ms": None,
        "components": {},
        "timestamp": "2026-02-01T10:00:00+00:00",
    }


def test_latency_percentiles_computation() -> None:
    """AC-1: p50/p95/p99 computed correctly for total_ms and steps."""
    records = [_make_latency_record(total_ms=float(i)) for i in [10, 20, 30, 40, 50]]
    stats = compute_latency_stats(records)
    assert stats["count"] == 5
    assert stats["total_ms"]["p50"] == 30.0
    assert stats["total_ms"]["p95"] == 48.0
    assert stats["total_ms"]["p99"] == 49.6
    assert "validate_command_ms" in stats["steps"]
    assert stats["steps"]["validate_command_ms"]["p50"] == 1.0


def test_fallback_rate_computation() -> None:
    """AC-2: Fallback, error, success rates computed correctly."""
    records = [
        _make_fallback_record(llm_outcome="success", fallback_reason=None),
        _make_fallback_record(llm_outcome="success", fallback_reason=None),
        _make_fallback_record(llm_outcome="fallback", fallback_reason="timeout"),
        _make_fallback_record(llm_outcome="error", fallback_reason="llm_unavailable"),
        _make_fallback_record(llm_outcome="skipped", fallback_reason="policy_disabled"),
    ]
    rates = compute_fallback_rates(records)
    assert rates["count"] == 5
    assert rates["success_rate"] == 0.4
    assert rates["fallback_rate"] == 0.2
    assert rates["error_rate"] == 0.2
    assert rates["outcome_counts"]["success"] == 2
    assert rates["outcome_counts"]["skipped"] == 1


def test_llm_comparison_split() -> None:
    """AC-3: Records split by llm_enabled with separate stats."""
    records = [
        _make_latency_record(total_ms=10.0, llm_enabled=False),
        _make_latency_record(total_ms=20.0, llm_enabled=False),
        _make_latency_record(total_ms=30.0, llm_enabled=True),
        _make_latency_record(total_ms=40.0, llm_enabled=True),
    ]
    comparison = compute_latency_comparison(records)
    assert comparison["all"]["count"] == 4
    assert comparison["without_llm"]["count"] == 2
    assert comparison["with_llm"]["count"] == 2
    assert comparison["without_llm"]["total_ms"]["p50"] == 15.0
    assert comparison["with_llm"]["total_ms"]["p50"] == 35.0


def test_empty_logs_no_crash() -> None:
    """AC-4: Empty inputs produce zero counts and null percentiles."""
    report = build_report([], [])
    assert report["latency"]["all"]["count"] == 0
    assert report["latency"]["all"]["total_ms"]["p50"] is None
    assert report["latency"]["with_llm"]["count"] == 0
    assert report["latency"]["without_llm"]["count"] == 0
    assert report["fallback"]["count"] == 0
    assert report["fallback"]["fallback_rate"] == 0.0
    assert report["time_range"]["first"] is None
    assert report["time_range"]["last"] is None


def test_single_record() -> None:
    """Single record produces valid percentiles and rates."""
    lat = [_make_latency_record(total_ms=42.5)]
    fb = [_make_fallback_record(llm_outcome="success", fallback_reason=None)]
    report = build_report(lat, fb)
    assert report["latency"]["all"]["count"] == 1
    assert report["latency"]["all"]["total_ms"]["p50"] == 42.5
    assert report["latency"]["all"]["total_ms"]["p95"] == 42.5
    assert report["fallback"]["count"] == 1
    assert report["fallback"]["success_rate"] == 1.0


def test_report_valid_json() -> None:
    """Report is valid JSON with required top-level keys."""
    report = build_report(
        [_make_latency_record()],
        [_make_fallback_record()],
    )
    serialized = json.dumps(report, ensure_ascii=False)
    parsed = json.loads(serialized)
    assert "latency" in parsed
    assert "fallback" in parsed
    assert "time_range" in parsed
    assert "all" in parsed["latency"]
    assert "with_llm" in parsed["latency"]
    assert "without_llm" in parsed["latency"]
```

## Files NOT Modified (invariants)
- `app/logging/pipeline_latency_log.py` — DO NOT CHANGE
- `app/logging/fallback_metrics_log.py` — DO NOT CHANGE
- `graphs/core_graph.py` — DO NOT CHANGE
- `tests/test_pipeline_latency.py` — DO NOT CHANGE
- `tests/test_fallback_metrics.py` — DO NOT CHANGE
- `tests/test_quality_eval.py` — DO NOT CHANGE

## Verification Commands

```bash
# New aggregation tests
source .venv/bin/activate && python3 -m pytest tests/test_aggregate_metrics.py -v

# Latency and fallback tests still pass
source .venv/bin/activate && python3 -m pytest tests/test_pipeline_latency.py tests/test_fallback_metrics.py -v

# Full test suite
source .venv/bin/activate && python3 -m pytest --tb=short -q
```

## STOP-THE-LINE
If any of the following occur, STOP and report:
- Existing tests fail after your changes
- Any file listed as "DO NOT CHANGE" needs modification
- Percentile computation produces incorrect results for known inputs
