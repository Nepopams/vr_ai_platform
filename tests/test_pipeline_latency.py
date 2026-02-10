"""Tests for pipeline-wide latency instrumentation (ST-028)."""

import json
import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from graphs.core_graph import process_command, sample_command


@pytest.fixture()
def _latency_log_path(tmp_path, monkeypatch):
    """Redirect latency log to tmp_path and enable it."""
    log_file = tmp_path / "pipeline_latency.jsonl"
    monkeypatch.setenv("PIPELINE_LATENCY_LOG_PATH", str(log_file))
    monkeypatch.setenv("PIPELINE_LATENCY_LOG_ENABLED", "true")
    return log_file


def _run_and_read_log(_latency_log_path):
    """Run process_command and return the last latency record."""
    command = sample_command()
    process_command(command)
    text = _latency_log_path.read_text(encoding="utf-8").strip()
    lines = text.split("\n")
    return json.loads(lines[-1])


def test_latency_record_structure(_latency_log_path) -> None:
    """AC-1: Latency record has required keys."""
    record = _run_and_read_log(_latency_log_path)
    assert "command_id" in record
    assert "trace_id" in record
    assert "total_ms" in record
    assert "steps" in record
    assert "llm_enabled" in record
    assert "timestamp" in record
    steps = record["steps"]
    expected_steps = {
        "validate_command_ms",
        "detect_intent_ms",
        "registry_ms",
        "core_logic_ms",
        "validate_decision_ms",
    }
    assert set(steps.keys()) == expected_steps


def test_step_breakdown_non_negative(_latency_log_path) -> None:
    """AC-2: All step values are non-negative."""
    record = _run_and_read_log(_latency_log_path)
    for step_name, value in record["steps"].items():
        assert value >= 0, f"Step '{step_name}' has negative value: {value}"


def test_total_ms_gte_step_sum(_latency_log_path) -> None:
    """AC-2: total_ms >= sum of step values."""
    record = _run_and_read_log(_latency_log_path)
    step_sum = sum(record["steps"].values())
    assert record["total_ms"] >= step_sum - 0.1, (
        f"total_ms={record['total_ms']} < step_sum={step_sum}"
    )


def test_disabled_no_log(tmp_path, monkeypatch) -> None:
    """AC-3: No log when disabled."""
    log_file = tmp_path / "pipeline_latency.jsonl"
    monkeypatch.setenv("PIPELINE_LATENCY_LOG_PATH", str(log_file))
    monkeypatch.setenv("PIPELINE_LATENCY_LOG_ENABLED", "false")
    command = sample_command()
    process_command(command)
    assert not log_file.exists(), "Log file should not exist when disabled"


def test_llm_enabled_flag(_latency_log_path, monkeypatch) -> None:
    """AC-4: llm_enabled reflects LLM_POLICY_ENABLED."""
    monkeypatch.setenv("LLM_POLICY_ENABLED", "true")
    record = _run_and_read_log(_latency_log_path)
    assert record["llm_enabled"] is True


def test_log_written_to_jsonl(_latency_log_path) -> None:
    """AC-1: Log file exists and each line is valid JSON."""
    command = sample_command()
    process_command(command)
    process_command(command)
    text = _latency_log_path.read_text(encoding="utf-8").strip()
    lines = text.split("\n")
    assert len(lines) == 2, f"Expected 2 lines, got {len(lines)}"
    for i, line in enumerate(lines):
        parsed = json.loads(line)
        assert "total_ms" in parsed, f"Line {i} missing total_ms"
