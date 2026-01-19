import json
from pathlib import Path

import routers.assist.runner as assist_runner
from agent_registry.v0_models import AgentCapability, AgentRegistryV0, AgentSpec, RunnerSpec
from agent_registry.v0_runner import AgentOutput
from routers.assist.types import EntityHints
from routers.v2 import RouterV2Pipeline


def _command(text: str):
    return {
        "command_id": "cmd-123",
        "user_id": "user-1",
        "timestamp": "2026-01-12T10:00:00Z",
        "text": text,
        "capabilities": ["start_job", "propose_add_shopping_item", "clarify"],
        "context": {
            "household": {
                "members": [{"user_id": "user-1", "display_name": "Анна"}],
                "shopping_lists": [{"list_id": "list-1", "name": "Основной"}],
            }
        },
    }


def _read_logs(path: Path):
    content = path.read_text(encoding="utf-8").strip().splitlines()
    return [json.loads(line) for line in content]


def _agent_spec(
    agent_id: str = "baseline-shopping-extractor-assist",
    *,
    enabled: bool = True,
    mode: str = "assist",
):
    return AgentSpec(
        agent_id=agent_id,
        enabled=enabled,
        mode=mode,
        capabilities=[AgentCapability(capability_id="extract_entities.shopping", allowed_intents=["add_shopping_item"])],
        runner=RunnerSpec(kind="python_module", ref="agents.baseline_shopping:run"),
    )


def _registry(*agents: AgentSpec) -> AgentRegistryV0:
    return AgentRegistryV0(
        registry_version="v0",
        compat_adr=None,
        compat_note=None,
        agents=tuple(agents),
    )


def test_agent_hints_disabled_no_runner(monkeypatch):
    monkeypatch.setenv("ASSIST_MODE_ENABLED", "true")
    monkeypatch.setenv("ASSIST_ENTITY_EXTRACTION_ENABLED", "false")
    monkeypatch.setenv("ASSIST_NORMALIZATION_ENABLED", "false")
    monkeypatch.setenv("ASSIST_CLARIFY_ENABLED", "false")
    monkeypatch.setenv("ASSIST_AGENT_HINTS_ENABLED", "false")

    called = {"runner": False, "registry": False}

    def fake_run(*_args, **_kwargs):
        called["runner"] = True
        raise AssertionError("agent runner should not be called")

    def fake_registry():
        called["registry"] = True
        return _registry(_agent_spec())

    monkeypatch.setattr(assist_runner, "_load_agent_registry", fake_registry)
    monkeypatch.setattr(assist_runner, "run_agent", fake_run)
    router = RouterV2Pipeline()
    router.decide(_command("Покупки: молоко"))

    assert called["runner"] is False
    assert called["registry"] is False


def test_agent_hints_apply_only_when_missing(monkeypatch):
    monkeypatch.setenv("ASSIST_MODE_ENABLED", "true")
    monkeypatch.setenv("ASSIST_ENTITY_EXTRACTION_ENABLED", "false")
    monkeypatch.setenv("ASSIST_NORMALIZATION_ENABLED", "false")
    monkeypatch.setenv("ASSIST_CLARIFY_ENABLED", "false")
    monkeypatch.setenv("ASSIST_AGENT_HINTS_ENABLED", "true")
    monkeypatch.setenv("ASSIST_AGENT_HINTS_SAMPLE_RATE", "1.0")

    monkeypatch.setattr(assist_runner, "_load_agent_registry", lambda: _registry(_agent_spec()))

    def fake_run(_spec, _input, trace_id=None):
        return AgentOutput(status="ok", reason_code=None, payload={"items": ["молоко"]}, latency_ms=5)

    monkeypatch.setattr(assist_runner, "run_agent", fake_run)

    normalized = {
        "text": "Покупки: молоко",
        "intent": "add_shopping_item",
        "item_name": None,
        "task_title": None,
        "capabilities": set(),
    }
    app = assist_runner.apply_assist_hints(_command("Покупки: молоко"), normalized)

    assert app.normalized.get("item_name") == "молоко"


def test_agent_hint_priority_over_llm(monkeypatch):
    monkeypatch.setenv("ASSIST_MODE_ENABLED", "true")
    monkeypatch.setenv("ASSIST_ENTITY_EXTRACTION_ENABLED", "true")
    monkeypatch.setenv("ASSIST_NORMALIZATION_ENABLED", "false")
    monkeypatch.setenv("ASSIST_CLARIFY_ENABLED", "false")
    monkeypatch.setenv("ASSIST_AGENT_HINTS_ENABLED", "true")
    monkeypatch.setenv("ASSIST_AGENT_HINTS_SAMPLE_RATE", "1.0")

    monkeypatch.setattr(assist_runner, "_load_agent_registry", lambda: _registry(_agent_spec()))

    def fake_run(_spec, _input, trace_id=None):
        return AgentOutput(status="ok", reason_code=None, payload={"items": ["молоко"]}, latency_ms=5)

    monkeypatch.setattr(assist_runner, "run_agent", fake_run)

    llm_hint = EntityHints(
        items=["хлеб"],
        task_hints={},
        confidence=0.4,
        error_type=None,
        latency_ms=10,
    )
    monkeypatch.setattr(assist_runner, "_run_entity_hint", lambda _text: llm_hint)

    normalized = {
        "text": "Покупки: молоко и хлеб",
        "intent": "add_shopping_item",
        "item_name": None,
        "task_title": None,
        "capabilities": set(),
    }
    app = assist_runner.apply_assist_hints(_command("Покупки: молоко и хлеб"), normalized)

    assert app.normalized.get("item_name") == "молоко"


def test_agent_hints_selects_first_ok(monkeypatch):
    monkeypatch.setenv("ASSIST_MODE_ENABLED", "true")
    monkeypatch.setenv("ASSIST_ENTITY_EXTRACTION_ENABLED", "false")
    monkeypatch.setenv("ASSIST_NORMALIZATION_ENABLED", "false")
    monkeypatch.setenv("ASSIST_CLARIFY_ENABLED", "false")
    monkeypatch.setenv("ASSIST_AGENT_HINTS_ENABLED", "true")
    monkeypatch.setenv("ASSIST_AGENT_HINTS_SAMPLE_RATE", "1.0")

    agent_a = _agent_spec(agent_id="agent-a")
    agent_b = _agent_spec(agent_id="agent-b")
    monkeypatch.setattr(assist_runner, "_load_agent_registry", lambda: _registry(agent_a, agent_b))

    calls = []

    def fake_run(spec, _input, trace_id=None):
        calls.append(spec.agent_id)
        if spec.agent_id == "agent-a":
            return AgentOutput(status="error", reason_code="exception", payload=None, latency_ms=3)
        return AgentOutput(status="ok", reason_code=None, payload={"items": ["молоко"]}, latency_ms=5)

    monkeypatch.setattr(assist_runner, "run_agent", fake_run)

    normalized = {
        "text": "Покупки: молоко",
        "intent": "add_shopping_item",
        "item_name": None,
        "task_title": None,
        "capabilities": set(),
    }
    app = assist_runner.apply_assist_hints(_command("Покупки: молоко"), normalized)

    assert app.normalized.get("item_name") == "молоко"
    assert calls == ["agent-a", "agent-b"]


def test_agent_hints_tiebreak_latency(monkeypatch):
    monkeypatch.setenv("ASSIST_MODE_ENABLED", "true")
    monkeypatch.setenv("ASSIST_ENTITY_EXTRACTION_ENABLED", "false")
    monkeypatch.setenv("ASSIST_NORMALIZATION_ENABLED", "false")
    monkeypatch.setenv("ASSIST_CLARIFY_ENABLED", "false")
    monkeypatch.setenv("ASSIST_AGENT_HINTS_ENABLED", "true")
    monkeypatch.setenv("ASSIST_AGENT_HINTS_SAMPLE_RATE", "1.0")

    agent_a = _agent_spec(agent_id="agent-a")
    agent_b = _agent_spec(agent_id="agent-b")
    monkeypatch.setattr(assist_runner, "_load_agent_registry", lambda: _registry(agent_a, agent_b))

    def fake_run(spec, _input, trace_id=None):
        latency = 12 if spec.agent_id == "agent-a" else 5
        return AgentOutput(status="ok", reason_code=None, payload={"items": ["молоко"]}, latency_ms=latency)

    monkeypatch.setattr(assist_runner, "run_agent", fake_run)

    normalized = {
        "text": "Покупки: молоко",
        "intent": "add_shopping_item",
        "item_name": None,
        "task_title": None,
        "capabilities": set(),
    }
    hint = assist_runner._run_agent_entity_hint(_command("Покупки: молоко"), normalized)

    assert hint.selected_agent_id == "agent-b"
    assert hint.selection_reason == "latency_tiebreak"


def test_agent_hints_tiebreak_agent_id(monkeypatch):
    monkeypatch.setenv("ASSIST_MODE_ENABLED", "true")
    monkeypatch.setenv("ASSIST_ENTITY_EXTRACTION_ENABLED", "false")
    monkeypatch.setenv("ASSIST_NORMALIZATION_ENABLED", "false")
    monkeypatch.setenv("ASSIST_CLARIFY_ENABLED", "false")
    monkeypatch.setenv("ASSIST_AGENT_HINTS_ENABLED", "true")
    monkeypatch.setenv("ASSIST_AGENT_HINTS_SAMPLE_RATE", "1.0")

    agent_a = _agent_spec(agent_id="agent-a")
    agent_b = _agent_spec(agent_id="agent-b")
    monkeypatch.setattr(assist_runner, "_load_agent_registry", lambda: _registry(agent_a, agent_b))

    def fake_run(_spec, _input, trace_id=None):
        return AgentOutput(status="ok", reason_code=None, payload={"items": ["молоко"]}, latency_ms=5)

    monkeypatch.setattr(assist_runner, "run_agent", fake_run)

    normalized = {
        "text": "Покупки: молоко",
        "intent": "add_shopping_item",
        "item_name": None,
        "task_title": None,
        "capabilities": set(),
    }
    hint = assist_runner._run_agent_entity_hint(_command("Покупки: молоко"), normalized)

    assert hint.selected_agent_id == "agent-a"
    assert hint.selection_reason == "agent_id_tiebreak"


def test_agent_hints_allowlist_filters(monkeypatch):
    monkeypatch.setenv("ASSIST_MODE_ENABLED", "true")
    monkeypatch.setenv("ASSIST_ENTITY_EXTRACTION_ENABLED", "false")
    monkeypatch.setenv("ASSIST_NORMALIZATION_ENABLED", "false")
    monkeypatch.setenv("ASSIST_CLARIFY_ENABLED", "false")
    monkeypatch.setenv("ASSIST_AGENT_HINTS_ENABLED", "true")
    monkeypatch.setenv("ASSIST_AGENT_HINTS_SAMPLE_RATE", "1.0")
    monkeypatch.setenv("ASSIST_AGENT_HINTS_ALLOWLIST", "agent-b")

    agent_a = _agent_spec(agent_id="agent-a")
    agent_b = _agent_spec(agent_id="agent-b")
    monkeypatch.setattr(assist_runner, "_load_agent_registry", lambda: _registry(agent_a, agent_b))

    calls = []

    def fake_run(spec, _input, trace_id=None):
        calls.append(spec.agent_id)
        return AgentOutput(status="ok", reason_code=None, payload={"items": ["молоко"]}, latency_ms=4)

    monkeypatch.setattr(assist_runner, "run_agent", fake_run)

    normalized = {
        "text": "Покупки: молоко",
        "intent": "add_shopping_item",
        "item_name": None,
        "task_title": None,
        "capabilities": set(),
    }
    app = assist_runner.apply_assist_hints(_command("Покупки: молоко"), normalized)

    assert app.normalized.get("item_name") == "молоко"
    assert calls == ["agent-b"]


def test_agent_hints_timeout_fallback(monkeypatch):
    monkeypatch.setenv("ASSIST_MODE_ENABLED", "true")
    monkeypatch.setenv("ASSIST_ENTITY_EXTRACTION_ENABLED", "false")
    monkeypatch.setenv("ASSIST_NORMALIZATION_ENABLED", "false")
    monkeypatch.setenv("ASSIST_CLARIFY_ENABLED", "false")
    monkeypatch.setenv("ASSIST_AGENT_HINTS_ENABLED", "true")
    monkeypatch.setenv("ASSIST_AGENT_HINTS_SAMPLE_RATE", "1.0")

    monkeypatch.setattr(assist_runner, "_load_agent_registry", lambda: _registry(_agent_spec()))

    def fake_run(*_args, **_kwargs):
        raise TimeoutError("timeout")

    monkeypatch.setattr(assist_runner, "run_agent", fake_run)

    normalized = {
        "text": "Покупки: молоко",
        "intent": "add_shopping_item",
        "item_name": None,
        "task_title": None,
        "capabilities": set(),
    }
    app = assist_runner.apply_assist_hints(_command("Покупки: молоко"), normalized)

    assert app.normalized.get("item_name") is None


def test_agent_hints_privacy_in_logs(monkeypatch, tmp_path):
    log_path = tmp_path / "assist.jsonl"
    monkeypatch.setenv("ASSIST_LOG_PATH", str(log_path))
    monkeypatch.setenv("ASSIST_MODE_ENABLED", "true")
    monkeypatch.setenv("ASSIST_ENTITY_EXTRACTION_ENABLED", "false")
    monkeypatch.setenv("ASSIST_NORMALIZATION_ENABLED", "false")
    monkeypatch.setenv("ASSIST_CLARIFY_ENABLED", "false")
    monkeypatch.setenv("ASSIST_AGENT_HINTS_ENABLED", "true")
    monkeypatch.setenv("ASSIST_AGENT_HINTS_SAMPLE_RATE", "1.0")

    monkeypatch.setattr(assist_runner, "_load_agent_registry", lambda: _registry(_agent_spec()))

    def fake_run(_spec, _input, trace_id=None):
        return AgentOutput(status="ok", reason_code=None, payload={"items": ["молоко"]}, latency_ms=7)

    monkeypatch.setattr(assist_runner, "run_agent", fake_run)

    router = RouterV2Pipeline()
    router.decide(_command("Покупки: молоко"))

    logs = _read_logs(log_path)
    serialized = json.dumps(logs, ensure_ascii=False)
    assert "молоко" not in serialized
    assert any("agent_hint_status" in entry for entry in logs)
