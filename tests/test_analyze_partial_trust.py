"""Tests for partial trust risk-log regression metrics analyzer."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# scripts/ is not a Python package; add to path for import
SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from analyze_partial_trust import (
    MetricsReport,
    compute_metrics,
    format_report_json,
    format_report_human,
    iter_risk_log,
    run_self_test,
)


def _record(
    status: str = "accepted_llm",
    reason_code: str = "accepted",
    latency_ms: int | None = 15,
    sampled: bool = True,
    diff_summary: dict | None = None,
) -> dict:
    return {
        "timestamp": "2026-02-08T12:00:00+00:00",
        "trace_id": "trace-test",
        "command_id": "cmd-test",
        "corridor_intent": "add_shopping_item",
        "sample_rate": 0.1,
        "sampled": sampled,
        "status": status,
        "reason_code": reason_code,
        "latency_ms": latency_ms,
        "model_meta": None,
        "baseline_summary": {"intent": "add_shopping_item", "decision_type": "start_job"},
        "llm_summary": {"intent": "add_shopping_item", "decision_type": "start_job"} if diff_summary else None,
        "diff_summary": diff_summary,
    }


def _write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def test_empty_jsonl(tmp_path):
    """Empty file -> total_records=0, all rates None."""
    log_path = tmp_path / "empty.jsonl"
    log_path.write_text("", encoding="utf-8")

    records = [r for r, ok in iter_risk_log(log_path) if ok]
    report = compute_metrics(records)

    assert report.total_records == 0
    assert report.acceptance_rate is None
    assert report.intent_mismatch_rate is None
    assert report.entity_key_mismatch_rate is None
    assert report.error_rate is None
    assert report.latency_p50 is None
    assert report.latency_p95 is None


def test_nonexistent_file(tmp_path):
    """Nonexistent file -> total_records=0."""
    log_path = tmp_path / "does_not_exist.jsonl"

    records = [r for r, ok in iter_risk_log(log_path) if ok]
    report = compute_metrics(records)

    assert report.total_records == 0


def test_single_accepted(tmp_path):
    """One accepted_llm record -> acceptance_rate=1.0."""
    log_path = tmp_path / "log.jsonl"
    _write_jsonl(log_path, [_record(status="accepted_llm", reason_code="accepted")])

    records = [r for r, ok in iter_risk_log(log_path) if ok]
    report = compute_metrics(records)

    assert report.total_records == 1
    assert report.acceptance_rate == 1.0
    assert report.status_breakdown["accepted_llm"] == 1


def test_single_fallback(tmp_path):
    """One fallback_deterministic -> acceptance_rate=0.0."""
    log_path = tmp_path / "log.jsonl"
    _write_jsonl(log_path, [_record(status="fallback_deterministic", reason_code="low_confidence")])

    records = [r for r, ok in iter_risk_log(log_path) if ok]
    report = compute_metrics(records)

    assert report.total_records == 1
    assert report.acceptance_rate == 0.0
    assert report.status_breakdown["fallback_deterministic"] == 1


def test_mixed_statuses(tmp_path):
    """3 accepted + 2 fallback + 5 not_sampled -> correct breakdown and rate."""
    log_path = tmp_path / "log.jsonl"
    records_data = (
        [_record(status="accepted_llm", reason_code="accepted") for _ in range(3)]
        + [_record(status="fallback_deterministic", reason_code="low_confidence") for _ in range(2)]
        + [_record(status="not_sampled", reason_code="not_sampled", sampled=False, latency_ms=None) for _ in range(5)]
    )
    _write_jsonl(log_path, records_data)

    records = [r for r, ok in iter_risk_log(log_path) if ok]
    report = compute_metrics(records)

    assert report.total_records == 10
    assert report.status_breakdown["accepted_llm"] == 3
    assert report.status_breakdown["fallback_deterministic"] == 2
    assert report.status_breakdown["not_sampled"] == 5
    assert report.acceptance_rate == 0.6
    assert report.sampled_records == 5  # 3 accepted + 2 fallback


def test_intent_mismatch_rate(tmp_path):
    """2 records with diff_summary, 1 has intent_mismatch -> rate=0.5."""
    log_path = tmp_path / "log.jsonl"
    _write_jsonl(
        log_path,
        [
            _record(diff_summary={"intent_mismatch": True, "entity_key_mismatch": False}),
            _record(diff_summary={"intent_mismatch": False, "entity_key_mismatch": False}),
        ],
    )

    records = [r for r, ok in iter_risk_log(log_path) if ok]
    report = compute_metrics(records)

    assert report.intent_mismatch_rate == 0.5


def test_entity_mismatch_rate(tmp_path):
    """2 records, 1 has entity_key_mismatch -> rate=0.5."""
    log_path = tmp_path / "log.jsonl"
    _write_jsonl(
        log_path,
        [
            _record(diff_summary={"intent_mismatch": False, "entity_key_mismatch": True}),
            _record(diff_summary={"intent_mismatch": False, "entity_key_mismatch": False}),
        ],
    )

    records = [r for r, ok in iter_risk_log(log_path) if ok]
    report = compute_metrics(records)

    assert report.entity_key_mismatch_rate == 0.5


def test_latency_percentiles(tmp_path):
    """Known latency values -> correct p50 and p95."""
    log_path = tmp_path / "log.jsonl"
    records_data = [_record(latency_ms=i) for i in range(1, 21)]
    _write_jsonl(log_path, records_data)

    records = [r for r, ok in iter_risk_log(log_path) if ok]
    report = compute_metrics(records)

    # sorted: [1..20], p50 index = int(19*0.5) = 9 -> value 10
    assert report.latency_p50 == 10
    # p95 index = int(19*0.95) = 18 -> value 19
    assert report.latency_p95 == 19


def test_reason_code_breakdown(tmp_path):
    """Multiple reason codes -> correct counts."""
    log_path = tmp_path / "log.jsonl"
    _write_jsonl(
        log_path,
        [
            _record(status="fallback_deterministic", reason_code="low_confidence"),
            _record(status="fallback_deterministic", reason_code="low_confidence"),
            _record(status="fallback_deterministic", reason_code="corridor_mismatch"),
            _record(status="accepted_llm", reason_code="accepted"),
        ],
    )

    records = [r for r, ok in iter_risk_log(log_path) if ok]
    report = compute_metrics(records)

    assert report.reason_code_breakdown["low_confidence"] == 2
    assert report.reason_code_breakdown["corridor_mismatch"] == 1
    assert report.reason_code_breakdown["accepted"] == 1


def test_error_rate(tmp_path):
    """1 error in 10 records -> error_rate=0.1."""
    log_path = tmp_path / "log.jsonl"
    records_data = [_record() for _ in range(9)] + [_record(status="error", reason_code="RuntimeError")]
    _write_jsonl(log_path, records_data)

    records = [r for r, ok in iter_risk_log(log_path) if ok]
    report = compute_metrics(records)

    assert report.error_rate == pytest.approx(0.1)


def test_records_without_diff_summary_excluded(tmp_path):
    """Records with status=not_sampled (no diff_summary) excluded from mismatch rates."""
    log_path = tmp_path / "log.jsonl"
    _write_jsonl(
        log_path,
        [
            _record(status="not_sampled", reason_code="not_sampled", sampled=False, latency_ms=None),
            _record(diff_summary={"intent_mismatch": True, "entity_key_mismatch": False}),
        ],
    )

    records = [r for r, ok in iter_risk_log(log_path) if ok]
    report = compute_metrics(records)

    # Only 1 record has diff_summary, and it has intent_mismatch=True
    assert report.intent_mismatch_rate == 1.0
    assert report.entity_key_mismatch_rate == 0.0


def test_privacy_no_raw_text(tmp_path):
    """Report output must not contain any raw text from records."""
    SECRET = "СЕКРЕТНОЕ_ЗНАЧЕНИЕ_PT_999"
    log_path = tmp_path / "log.jsonl"
    _write_jsonl(
        log_path,
        [
            {
                **_record(),
                "baseline_summary": {"intent": "add_shopping_item", "secret": SECRET},
                "llm_summary": {"intent": "add_shopping_item", "secret": SECRET},
            }
        ],
    )

    records = [r for r, ok in iter_risk_log(log_path) if ok]
    report = compute_metrics(records)

    json_output = json.dumps(format_report_json(report), ensure_ascii=False)
    human_output = format_report_human(report)

    assert SECRET not in json_output
    assert SECRET not in human_output


def test_json_output_has_all_fields(tmp_path):
    """JSON report contains all required metric fields."""
    log_path = tmp_path / "log.jsonl"
    _write_jsonl(log_path, [_record(diff_summary={"intent_mismatch": False, "entity_key_mismatch": False})])

    records = [r for r, ok in iter_risk_log(log_path) if ok]
    report = compute_metrics(records)
    data = format_report_json(report)

    required_fields = {
        "total_records",
        "sampled_records",
        "status_breakdown",
        "reason_code_breakdown",
        "acceptance_rate",
        "intent_mismatch_rate",
        "entity_key_mismatch_rate",
        "latency_p50",
        "latency_p95",
        "error_rate",
        "parse_errors",
    }
    missing = required_fields - set(data.keys())
    assert not missing, f"Missing fields: {missing}"


def test_self_test():
    """Self-test must pass without error."""
    run_self_test()
