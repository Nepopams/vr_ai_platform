"""Tests for unified fallback metrics logging (ST-029)."""

import json
import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.logging.fallback_metrics_log import append_fallback_metrics_log
from graphs.core_graph import process_command, sample_command


@pytest.fixture()
def _fallback_log_path(tmp_path, monkeypatch):
    """Redirect fallback metrics log to tmp_path and enable it."""
    log_file = tmp_path / "fallback_metrics.jsonl"
    monkeypatch.setenv("FALLBACK_METRICS_LOG_PATH", str(log_file))
    monkeypatch.setenv("FALLBACK_METRICS_LOG_ENABLED", "true")
    return log_file


def _run_and_read_fallback_log(_fallback_log_path):
    """Run process_command and return the last fallback record."""
    command = sample_command()
    process_command(command)
    text = _fallback_log_path.read_text(encoding="utf-8").strip()
    lines = text.split("\n")
    return json.loads(lines[-1])


def test_record_on_llm_success(tmp_path, monkeypatch) -> None:
    """AC-2: Log module records success outcome correctly."""
    log_file = tmp_path / "fallback_metrics.jsonl"
    monkeypatch.setenv("FALLBACK_METRICS_LOG_PATH", str(log_file))
    append_fallback_metrics_log(
        {
            "command_id": "cmd-test-001",
            "trace_id": "trace-test-001",
            "llm_outcome": "success",
            "fallback_reason": None,
            "deterministic_used": False,
            "llm_latency_ms": 120.5,
            "components": {"shadow": "ok", "assist": "ok"},
        }
    )
    record = json.loads(log_file.read_text(encoding="utf-8").strip())
    assert record["llm_outcome"] == "success"
    assert record["fallback_reason"] is None
    assert record["deterministic_used"] is False
    assert record["llm_latency_ms"] == 120.5
    assert "timestamp" in record


def test_record_on_llm_timeout(tmp_path, monkeypatch) -> None:
    """AC-3: Log module records fallback with timeout reason."""
    log_file = tmp_path / "fallback_metrics.jsonl"
    monkeypatch.setenv("FALLBACK_METRICS_LOG_PATH", str(log_file))
    append_fallback_metrics_log(
        {
            "command_id": "cmd-test-002",
            "trace_id": "trace-test-002",
            "llm_outcome": "fallback",
            "fallback_reason": "timeout",
            "deterministic_used": True,
            "llm_latency_ms": 5000.0,
            "components": {"shadow": "timeout"},
        }
    )
    record = json.loads(log_file.read_text(encoding="utf-8").strip())
    assert record["llm_outcome"] == "fallback"
    assert record["fallback_reason"] == "timeout"
    assert record["deterministic_used"] is True


def test_record_on_llm_unavailable(tmp_path, monkeypatch) -> None:
    """AC-3: Log module records error with unavailable reason."""
    log_file = tmp_path / "fallback_metrics.jsonl"
    monkeypatch.setenv("FALLBACK_METRICS_LOG_PATH", str(log_file))
    append_fallback_metrics_log(
        {
            "command_id": "cmd-test-003",
            "trace_id": "trace-test-003",
            "llm_outcome": "error",
            "fallback_reason": "llm_unavailable",
            "deterministic_used": True,
            "llm_latency_ms": None,
            "components": {"shadow": "error"},
        }
    )
    record = json.loads(log_file.read_text(encoding="utf-8").strip())
    assert record["llm_outcome"] == "error"
    assert record["fallback_reason"] == "llm_unavailable"


def test_record_skipped_when_disabled(_fallback_log_path, monkeypatch) -> None:
    """AC-4: llm_outcome=skipped when LLM disabled."""
    monkeypatch.setenv("LLM_POLICY_ENABLED", "false")
    record = _run_and_read_fallback_log(_fallback_log_path)
    assert record["llm_outcome"] == "skipped"
    assert record["fallback_reason"] == "policy_disabled"
    assert record["deterministic_used"] is True


def test_no_raw_text_in_record(_fallback_log_path) -> None:
    """AC-5: No raw user text or LLM output in records."""
    record = _run_and_read_fallback_log(_fallback_log_path)
    forbidden_keys = {"text", "prompt", "raw", "raw_output", "raw_text", "user_text"}
    found = forbidden_keys & set(record.keys())
    assert not found, f"Forbidden keys found in record: {found}"


def test_log_written_to_jsonl(_fallback_log_path) -> None:
    """AC-1: Log file has valid JSONL entries."""
    command = sample_command()
    process_command(command)
    process_command(command)
    text = _fallback_log_path.read_text(encoding="utf-8").strip()
    lines = text.split("\n")
    assert len(lines) == 2, f"Expected 2 lines, got {len(lines)}"
    for i, line in enumerate(lines):
        parsed = json.loads(line)
        assert "llm_outcome" in parsed, f"Line {i} missing llm_outcome"
        assert "timestamp" in parsed, f"Line {i} missing timestamp"
