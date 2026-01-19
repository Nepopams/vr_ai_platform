import routers.agent_invoker_shadow as invoker
from agent_registry.v0_models import AgentCapability, AgentRegistryV0, AgentSpec, RunnerSpec
from routers.v2 import RouterV2Pipeline


def _command():
    return {
        "command_id": "cmd-123",
        "user_id": "user-1",
        "timestamp": "2026-01-12T10:00:00Z",
        "text": "Купи молоко",
        "capabilities": ["start_job", "propose_add_shopping_item", "clarify"],
        "context": {
            "household": {
                "members": [{"user_id": "user-1", "display_name": "Анна"}],
                "shopping_lists": [{"list_id": "list-1", "name": "Основной"}],
            }
        },
    }


def _stable_fields(decision):
    action = decision.get("action")
    payload = decision.get("payload", {})
    stable = {"action": action}
    if action == "start_job":
        stable["job_type"] = payload.get("job_type")
        proposed_actions = payload.get("proposed_actions") or []
        stable["proposed_actions"] = [
            {
                "action": proposed.get("action"),
                "item_name": proposed.get("payload", {}).get("item", {}).get("name"),
            }
            for proposed in proposed_actions
        ]
    elif action == "clarify":
        stable["missing_fields"] = payload.get("missing_fields")
    return stable


def _registry(agents):
    return AgentRegistryV0(
        registry_version="v0",
        compat_adr=None,
        compat_note=None,
        agents=agents,
    )


def _agent(agent_id, mode, allowed_intents):
    return AgentSpec(
        agent_id=agent_id,
        enabled=False,
        mode=mode,
        capabilities=[AgentCapability(capability_id="extract_entities.shopping", allowed_intents=allowed_intents)],
        runner=RunnerSpec(kind="python_module", ref="agents.baseline_shopping:run"),
    )


def test_shadow_agent_invoker_no_impact(monkeypatch):
    router = RouterV2Pipeline()
    monkeypatch.setenv("SHADOW_AGENT_INVOKER_ENABLED", "false")
    baseline = router.decide(_command())

    monkeypatch.setenv("SHADOW_AGENT_INVOKER_ENABLED", "true")
    monkeypatch.setenv("SHADOW_AGENT_ALLOWLIST", "agent-shadow")
    monkeypatch.setenv("SHADOW_AGENT_SAMPLE_RATE", "1.0")
    monkeypatch.setattr(invoker, "_load_registry", lambda *_args, **_kwargs: _registry([]))

    decision_with_shadow = router.decide(_command())
    assert _stable_fields(baseline) == _stable_fields(decision_with_shadow)


def test_shadow_agent_invoker_selection_allowlist(monkeypatch):
    agents = [
        _agent("agent-shadow", "shadow", ["add_shopping_item"]),
        _agent("agent-assist", "assist", ["add_shopping_item"]),
        _agent("agent-other", "shadow", ["create_task"]),
    ]
    registry = _registry(agents)
    captured = []

    monkeypatch.setenv("SHADOW_AGENT_INVOKER_ENABLED", "true")
    monkeypatch.setenv("SHADOW_AGENT_ALLOWLIST", "agent-shadow,agent-assist,agent-other")
    monkeypatch.setenv("SHADOW_AGENT_SAMPLE_RATE", "1.0")
    monkeypatch.setattr(invoker, "_load_registry", lambda *_args, **_kwargs: registry)
    monkeypatch.setattr(invoker, "_submit_agent_run", lambda spec, *_args, **_kwargs: captured.append(spec.agent_id))

    invoker.invoke_shadow_agents(
        _command(),
        {"intent": "add_shopping_item", "text": "Купи молоко"},
        {"action": "start_job", "payload": {"job_type": "add_shopping_item"}},
        "trace-1",
        "cmd-1",
    )

    assert captured == ["agent-shadow"]


def test_shadow_agent_invoker_swallows_errors(monkeypatch):
    registry = _registry([_agent("agent-shadow", "shadow", ["add_shopping_item"])])

    monkeypatch.setenv("SHADOW_AGENT_INVOKER_ENABLED", "true")
    monkeypatch.setenv("SHADOW_AGENT_ALLOWLIST", "agent-shadow")
    monkeypatch.setenv("SHADOW_AGENT_SAMPLE_RATE", "1.0")
    monkeypatch.setattr(invoker, "_load_registry", lambda *_args, **_kwargs: registry)

    def _boom(*_args, **_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(invoker, "_submit_agent_run", _boom)
    invoker.invoke_shadow_agents(
        _command(),
        {"intent": "add_shopping_item", "text": "Купи молоко"},
        {"action": "start_job", "payload": {"job_type": "add_shopping_item"}},
        "trace-1",
        "cmd-1",
    )
