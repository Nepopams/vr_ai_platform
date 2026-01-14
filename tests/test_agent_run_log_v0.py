import json
from pathlib import Path

import pytest

from agent_registry.v0_runner import summarize_payload
from app.logging.agent_run_log import log_agent_run


def _read_log(path: Path) -> dict:
    content = path.read_text(encoding="utf-8").strip().splitlines()
    return json.loads(content[-1])


def test_agent_run_log_required_fields(tmp_path, monkeypatch):
    log_path = tmp_path / "agent_run.jsonl"
    monkeypatch.setenv("AGENT_RUN_LOG_ENABLED", "true")
    monkeypatch.setenv("AGENT_RUN_LOG_PATH", str(log_path))

    event = {
        "trace_id": "trace-1",
        "command_id": "cmd-1",
        "agent_id": "agent-1",
        "capability_id": "extract_entities.shopping",
        "mode": "assist",
        "status": "ok",
        "reason_code": None,
        "latency_ms": 12,
        "runner_kind": "python_module",
        "model_meta": None,
        "payload_summary": {"keys_present": []},
        "privacy": {"contains_sensitive_text": True, "raw_logged": False},
    }
    log_agent_run(event)

    logged = _read_log(log_path)
    for key in (
        "timestamp",
        "trace_id",
        "command_id",
        "agent_id",
        "capability_id",
        "mode",
        "status",
        "latency_ms",
        "runner_kind",
        "payload_summary",
        "privacy",
    ):
        assert key in logged


def test_summarize_payload_no_strings():
    payload = {"items": [{"name": "молоко"}], "list_id": "list-1", "count": 2}
    summary = summarize_payload(payload, contains_sensitive_text=True)
    serialized = json.dumps(summary, ensure_ascii=False)

    assert "молоко" not in serialized
    assert "list-1" not in serialized
    assert "items" in summary["keys_present"]


def test_log_errors_do_not_raise(monkeypatch):
    monkeypatch.setenv("AGENT_RUN_LOG_ENABLED", "true")

    def _fail_open(*_args, **_kwargs):
        raise OSError("disk error")

    monkeypatch.setattr("pathlib.Path.open", _fail_open)
    log_agent_run({"agent_id": "agent-1"})
