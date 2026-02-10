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
