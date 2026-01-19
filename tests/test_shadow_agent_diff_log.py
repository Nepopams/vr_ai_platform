import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import routers.agent_invoker_shadow as invoker
from agent_registry.v0_models import AgentCapability, AgentRegistryV0, AgentSpec, RunnerSpec
from agent_registry.v0_runner import AgentOutput


def _registry(agent):
    return AgentRegistryV0(
        registry_version="v0",
        compat_adr=None,
        compat_note=None,
        agents=[agent],
    )


def _agent():
    return AgentSpec(
        agent_id="agent-shadow",
        enabled=False,
        mode="shadow",
        capabilities=[AgentCapability(capability_id="extract_entities.shopping", allowed_intents=["add_shopping_item"])],
        runner=RunnerSpec(kind="python_module", ref="agents.baseline_shopping:run"),
    )


def _command():
    return {
        "command_id": "cmd-123",
        "text": "Купи молоко",
        "capabilities": ["start_job", "propose_add_shopping_item", "clarify"],
    }


def _baseline():
    return {"action": "start_job", "payload": {"job_type": "add_shopping_item"}}


def _read_log(path: Path) -> dict:
    content = path.read_text(encoding="utf-8").strip().splitlines()
    return json.loads(content[-1])


def test_shadow_agent_diff_log_privacy(monkeypatch, tmp_path):
    log_path = tmp_path / "diff.jsonl"
    registry = _registry(_agent())

    monkeypatch.setenv("SHADOW_AGENT_INVOKER_ENABLED", "true")
    monkeypatch.setenv("SHADOW_AGENT_ALLOWLIST", "agent-shadow")
    monkeypatch.setenv("SHADOW_AGENT_SAMPLE_RATE", "1.0")
    monkeypatch.setenv("SHADOW_AGENT_DIFF_LOG_ENABLED", "true")
    monkeypatch.setenv("SHADOW_AGENT_DIFF_LOG_PATH", str(log_path))

    monkeypatch.setattr(invoker, "_load_registry", lambda *_args, **_kwargs: registry)
    monkeypatch.setattr(invoker, "_load_catalog", lambda: {"extract_entities.shopping": {"contains_sensitive_text": True}})

    def fake_run_agent(_spec, _input, trace_id=None):
        return AgentOutput(status="ok", reason_code=None, payload={"items": ["молоко"], "question": "?"}, latency_ms=1)

    monkeypatch.setattr(invoker, "run_agent", fake_run_agent)
    monkeypatch.setattr(invoker, "_submit_agent_run", lambda *args, **kwargs: invoker._run_agent(*args, **kwargs))

    invoker.invoke_shadow_agents(
        _command(),
        {"intent": "add_shopping_item", "text": "Купи молоко"},
        _baseline(),
        "trace-1",
        "cmd-1",
    )

    logged = _read_log(log_path)
    summary = logged.get("agent_summary", {})
    serialized = json.dumps(summary, ensure_ascii=False)
    assert "молоко" not in serialized
    _assert_no_string_values(summary)


def test_shadow_agent_diff_log_disabled(monkeypatch, tmp_path):
    log_path = tmp_path / "diff.jsonl"
    registry = _registry(_agent())

    monkeypatch.setenv("SHADOW_AGENT_INVOKER_ENABLED", "true")
    monkeypatch.setenv("SHADOW_AGENT_ALLOWLIST", "agent-shadow")
    monkeypatch.setenv("SHADOW_AGENT_SAMPLE_RATE", "1.0")
    monkeypatch.setenv("SHADOW_AGENT_DIFF_LOG_ENABLED", "false")
    monkeypatch.setenv("SHADOW_AGENT_DIFF_LOG_PATH", str(log_path))

    monkeypatch.setattr(invoker, "_load_registry", lambda *_args, **_kwargs: registry)
    monkeypatch.setattr(invoker, "_load_catalog", lambda: {"extract_entities.shopping": {"contains_sensitive_text": True}})
    monkeypatch.setattr(invoker, "_submit_agent_run", lambda *args, **kwargs: invoker._run_agent(*args, **kwargs))

    invoker.invoke_shadow_agents(
        _command(),
        {"intent": "add_shopping_item", "text": "Купи молоко"},
        _baseline(),
        "trace-1",
        "cmd-1",
    )

    assert not log_path.exists()


def test_shadow_agent_diff_log_errors_swallowed(monkeypatch, tmp_path):
    registry = _registry(_agent())

    monkeypatch.setenv("SHADOW_AGENT_INVOKER_ENABLED", "true")
    monkeypatch.setenv("SHADOW_AGENT_ALLOWLIST", "agent-shadow")
    monkeypatch.setenv("SHADOW_AGENT_SAMPLE_RATE", "1.0")
    monkeypatch.setenv("SHADOW_AGENT_DIFF_LOG_ENABLED", "true")
    monkeypatch.setenv("SHADOW_AGENT_DIFF_LOG_PATH", str(tmp_path / "diff.jsonl"))

    monkeypatch.setattr(invoker, "_load_registry", lambda *_args, **_kwargs: registry)
    monkeypatch.setattr(invoker, "_load_catalog", lambda: {"extract_entities.shopping": {"contains_sensitive_text": True}})
    monkeypatch.setattr(invoker, "_submit_agent_run", lambda *args, **kwargs: invoker._run_agent(*args, **kwargs))

    def fake_run_agent(_spec, _input, trace_id=None):
        return AgentOutput(status="ok", reason_code=None, payload={"items": ["молоко"]}, latency_ms=1)

    monkeypatch.setattr(invoker, "run_agent", fake_run_agent)

    def boom_log(*_args, **_kwargs):
        raise OSError("boom")

    monkeypatch.setattr(invoker, "log_shadow_agent_diff", boom_log)

    invoker.invoke_shadow_agents(
        _command(),
        {"intent": "add_shopping_item", "text": "Купи молоко"},
        _baseline(),
        "trace-1",
        "cmd-1",
    )


def _assert_no_string_values(summary):
    for key, value in summary.items():
        if key == "keys_present":
            assert isinstance(value, list)
            assert all(isinstance(item, str) for item in value)
            continue
        _assert_value_safe(value)


def _assert_value_safe(value):
    if isinstance(value, str):
        raise AssertionError("string values are not allowed in agent_summary")
    if isinstance(value, list):
        if any(isinstance(item, str) for item in value):
            raise AssertionError("string values are not allowed in agent_summary lists")
        for item in value:
            _assert_value_safe(item)
    if isinstance(value, dict):
        for item in value.values():
            _assert_value_safe(item)
