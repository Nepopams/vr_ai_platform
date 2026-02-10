"""Tests for shadow router golden-dataset analyzer."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# scripts/ is not a Python package; add to path for import
SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from analyze_shadow_router import (
    GoldenEntry,
    MetricsReport,
    compute_metrics,
    format_report_json,
    format_report_human,
    iter_shadow_log,
    load_golden_dataset,
    run_self_test,
)

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "skills" / "graph-sanity" / "fixtures"


def _make_record(
    command_id: str = "cmd-test-001",
    suggested_intent: str = "add_shopping_item",
    entity_keys: list[str] | None = None,
    latency_ms: int = 50,
    error_type: str | None = None,
) -> dict:
    return {
        "timestamp": "2026-02-01T10:00:00+00:00",
        "trace_id": "trace-test",
        "command_id": command_id,
        "router_version": "shadow-router-0.1",
        "router_strategy": "v2",
        "status": "ok" if error_type is None else "error",
        "latency_ms": latency_ms,
        "error_type": error_type,
        "suggested_intent": suggested_intent,
        "missing_fields": None,
        "clarify_question": None,
        "entities_summary": {"keys": entity_keys or [], "counts": {}},
        "confidence": None,
        "model_meta": None,
        "baseline_intent": "add_shopping_item",
        "baseline_action": None,
        "baseline_job_type": None,
    }


def _write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _write_golden(path: Path, entries: list[dict]) -> None:
    path.write_text(json.dumps(entries, ensure_ascii=False), encoding="utf-8")


def _golden_entry(
    command_id: str = "cmd-test-001",
    expected_intent: str = "add_shopping_item",
    expected_entity_keys: list[str] | None = None,
) -> dict:
    return {
        "command_id": command_id,
        "fixture_file": "test.json",
        "expected_intent": expected_intent,
        "expected_entity_keys": expected_entity_keys or [],
        "notes": "test entry",
    }


def test_empty_jsonl_produces_zero_report(tmp_path):
    """Empty JSONL -> total_records=0, all rates None."""
    log_path = tmp_path / "empty.jsonl"
    log_path.write_text("", encoding="utf-8")
    golden_path = tmp_path / "golden.json"
    _write_golden(golden_path, [_golden_entry()])

    golden = load_golden_dataset(golden_path)
    records = [r for r, ok in iter_shadow_log(log_path) if ok]
    report = compute_metrics(records, golden)

    assert report.total_records == 0
    assert report.matched_records == 0
    assert report.intent_match_rate is None
    assert report.entity_hit_rate is None
    assert report.latency_p50 is None
    assert report.latency_p95 is None


def test_single_matching_record_correct_intent(tmp_path):
    """One record matching golden entry with correct intent -> rate 1.0."""
    log_path = tmp_path / "log.jsonl"
    _write_jsonl(log_path, [_make_record()])
    golden_path = tmp_path / "golden.json"
    _write_golden(golden_path, [_golden_entry()])

    golden = load_golden_dataset(golden_path)
    records = [r for r, ok in iter_shadow_log(log_path) if ok]
    report = compute_metrics(records, golden)

    assert report.total_records == 1
    assert report.matched_records == 1
    assert report.intent_match_rate == 1.0


def test_single_matching_record_wrong_intent(tmp_path):
    """One record with wrong intent -> rate 0.0."""
    log_path = tmp_path / "log.jsonl"
    _write_jsonl(log_path, [_make_record(suggested_intent="create_task")])
    golden_path = tmp_path / "golden.json"
    _write_golden(golden_path, [_golden_entry(expected_intent="add_shopping_item")])

    golden = load_golden_dataset(golden_path)
    records = [r for r, ok in iter_shadow_log(log_path) if ok]
    report = compute_metrics(records, golden)

    assert report.matched_records == 1
    assert report.intent_match_rate == 0.0


def test_entity_hit_rate_calculation(tmp_path):
    """Two records: one matching entities, one not -> rate 0.5."""
    log_path = tmp_path / "log.jsonl"
    _write_jsonl(
        log_path,
        [
            _make_record(command_id="cmd-1", entity_keys=["item"]),
            _make_record(command_id="cmd-2", entity_keys=["wrong"]),
        ],
    )
    golden_path = tmp_path / "golden.json"
    _write_golden(
        golden_path,
        [
            _golden_entry(command_id="cmd-1", expected_entity_keys=["item"]),
            _golden_entry(command_id="cmd-2", expected_entity_keys=["item"]),
        ],
    )

    golden = load_golden_dataset(golden_path)
    records = [r for r, ok in iter_shadow_log(log_path) if ok]
    report = compute_metrics(records, golden)

    assert report.matched_records == 2
    assert report.entity_hit_rate == 0.5


def test_latency_percentiles(tmp_path):
    """Known latency values -> verify p50 and p95."""
    log_path = tmp_path / "log.jsonl"
    # 20 records with latencies 1..20
    records_data = [
        _make_record(command_id=f"cmd-{i}", latency_ms=i) for i in range(1, 21)
    ]
    _write_jsonl(log_path, records_data)
    golden_path = tmp_path / "golden.json"
    _write_golden(golden_path, [])  # no golden entries needed for latency

    golden = load_golden_dataset(golden_path)
    records = [r for r, ok in iter_shadow_log(log_path) if ok]
    report = compute_metrics(records, golden)

    assert report.total_records == 20
    # sorted: [1..20], p50 index = int(19*0.5) = 9 -> value 10
    assert report.latency_p50 == 10
    # p95 index = int(19*0.95) = 18 -> value 19
    assert report.latency_p95 == 19


def test_error_breakdown_counts(tmp_path):
    """Records with various error types -> correct counts."""
    log_path = tmp_path / "log.jsonl"
    _write_jsonl(
        log_path,
        [
            _make_record(command_id="c1", error_type="timeout"),
            _make_record(command_id="c2", error_type="timeout"),
            _make_record(command_id="c3", error_type="invalid_json"),
            _make_record(command_id="c4", error_type=None),
        ],
    )
    golden_path = tmp_path / "golden.json"
    _write_golden(golden_path, [])

    golden = load_golden_dataset(golden_path)
    records = [r for r, ok in iter_shadow_log(log_path) if ok]
    report = compute_metrics(records, golden)

    assert report.error_breakdown == {"timeout": 2, "invalid_json": 1}


def test_unmatched_records_excluded(tmp_path):
    """Records with command_ids NOT in golden dataset -> matched=0, rates None."""
    log_path = tmp_path / "log.jsonl"
    _write_jsonl(
        log_path,
        [
            _make_record(command_id="cmd-unknown-1"),
            _make_record(command_id="cmd-unknown-2"),
        ],
    )
    golden_path = tmp_path / "golden.json"
    _write_golden(golden_path, [_golden_entry(command_id="cmd-other")])

    golden = load_golden_dataset(golden_path)
    records = [r for r, ok in iter_shadow_log(log_path) if ok]
    report = compute_metrics(records, golden)

    assert report.total_records == 2
    assert report.matched_records == 0
    assert report.intent_match_rate is None
    assert report.entity_hit_rate is None


def test_privacy_no_raw_text(tmp_path):
    """Report must not contain any planted secret text."""
    SECRET = "СЕКРЕТНОЕ_ЗНАЧЕНИЕ_ABC_999"
    log_path = tmp_path / "log.jsonl"
    _write_jsonl(
        log_path,
        [
            {
                **_make_record(),
                "clarify_question": SECRET,
                "model_meta": {"task_id": SECRET},
            }
        ],
    )
    golden_path = tmp_path / "golden.json"
    _write_golden(golden_path, [_golden_entry()])

    golden = load_golden_dataset(golden_path)
    records = [r for r, ok in iter_shadow_log(log_path) if ok]
    report = compute_metrics(records, golden)

    json_output = json.dumps(format_report_json(report), ensure_ascii=False)
    human_output = format_report_human(report)

    assert SECRET not in json_output
    assert SECRET not in human_output


def test_golden_dataset_manifest_schema():
    """Validate actual golden_dataset.json: 14 entries, required fields."""
    golden_path = FIXTURES_DIR / "golden_dataset.json"
    assert golden_path.exists(), f"golden_dataset.json not found at {golden_path}"

    data = json.loads(golden_path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) >= 20, f"Expected >= 20 entries, got {len(data)}"

    required_fields = {"command_id", "expected_intent", "expected_entity_keys"}
    for entry in data:
        missing = required_fields - set(entry.keys())
        assert not missing, f"Entry {entry.get('command_id')} missing fields: {missing}"
        assert isinstance(entry["expected_entity_keys"], list)


def test_end_to_end_with_json_output(tmp_path):
    """Full run: synthetic JSONL + real golden dataset -> valid JSON report."""
    golden_path = FIXTURES_DIR / "golden_dataset.json"
    if not golden_path.exists():
        pytest.skip("golden_dataset.json not yet created")

    golden = load_golden_dataset(golden_path)
    # Create synthetic JSONL with 3 records matching golden entries
    sample_ids = list(golden.keys())[:3]
    log_records = []
    for cid in sample_ids:
        entry = golden[cid]
        log_records.append(
            _make_record(
                command_id=cid,
                suggested_intent=entry.expected_intent,
                entity_keys=entry.expected_entity_keys,
                latency_ms=42,
            )
        )
    log_path = tmp_path / "log.jsonl"
    _write_jsonl(log_path, log_records)

    records = [r for r, ok in iter_shadow_log(log_path) if ok]
    report = compute_metrics(records, golden)

    assert report.total_records == 3
    assert report.matched_records == 3
    assert report.intent_match_rate == 1.0

    # Test JSON output
    output_path = tmp_path / "report.json"
    output_path.write_text(
        json.dumps(format_report_json(report), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert "intent_match_rate" in loaded
    assert "entity_hit_rate" in loaded
    assert "latency_p50" in loaded
    assert "latency_p95" in loaded
    assert "error_breakdown" in loaded
    assert "total_records" in loaded
    assert "matched_records" in loaded
