import json
from pathlib import Path

import routers.shadow_router as shadow_router
from routers.shadow_types import RouterSuggestion
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


def _read_log(path: Path):
    content = path.read_text(encoding="utf-8").strip().splitlines()
    return json.loads(content[-1])


def test_shadow_router_no_impact(monkeypatch):
    router = RouterV2Pipeline()
    monkeypatch.setenv("SHADOW_ROUTER_ENABLED", "false")
    decision_without_shadow = router.decide(_command())

    monkeypatch.setenv("SHADOW_ROUTER_ENABLED", "true")
    monkeypatch.setattr(shadow_router, "_submit_shadow_task", lambda payload: None)
    decision_with_shadow = router.decide(_command())

    assert _stable_fields(decision_without_shadow) == _stable_fields(decision_with_shadow)


def test_shadow_router_timeout_no_impact(monkeypatch, tmp_path):
    log_path = tmp_path / "shadow.jsonl"
    router = RouterV2Pipeline()
    monkeypatch.setenv("SHADOW_ROUTER_ENABLED", "false")
    baseline = router.decide(_command())

    monkeypatch.setenv("SHADOW_ROUTER_ENABLED", "true")
    monkeypatch.setenv("SHADOW_ROUTER_LOG_PATH", str(log_path))
    monkeypatch.setenv("LLM_POLICY_ENABLED", "false")

    times = [0.0, 1.0]
    monkeypatch.setattr(shadow_router.time, "monotonic", lambda: times.pop(0))
    monkeypatch.setattr(shadow_router, "shadow_router_timeout_ms", lambda: 0)
    monkeypatch.setattr(shadow_router, "is_llm_policy_enabled", lambda: True)

    suggestion = RouterSuggestion(
        suggested_intent=None,
        entities={},
        missing_fields=None,
        clarify_question=None,
        confidence=None,
        explain=None,
        error_type=None,
        latency_ms=None,
        model_meta={"profile": "cheap"},
    )
    monkeypatch.setattr(shadow_router, "_build_suggestion", lambda payload: suggestion)
    monkeypatch.setattr(
        shadow_router,
        "_submit_shadow_task",
        lambda payload: shadow_router._run_shadow_router(payload),
    )
    decision_with_shadow = router.decide(_command())

    assert _stable_fields(baseline) == _stable_fields(decision_with_shadow)
    logged = _read_log(log_path)
    assert logged["status"] == "error"
    assert logged["error_type"] == "timeout_exceeded"


def test_shadow_router_logging_shape(monkeypatch, tmp_path):
    log_path = tmp_path / "shadow.jsonl"
    monkeypatch.setenv("SHADOW_ROUTER_ENABLED", "true")
    monkeypatch.setenv("SHADOW_ROUTER_LOG_PATH", str(log_path))
    monkeypatch.setenv("LLM_POLICY_ENABLED", "false")
    monkeypatch.setattr(
        shadow_router,
        "_submit_shadow_task",
        lambda payload: shadow_router._run_shadow_router(payload),
    )

    router = RouterV2Pipeline()
    normalized = router.normalize(_command())
    shadow_router.start_shadow_router(_command(), normalized)

    logged = _read_log(log_path)
    required_keys = {
        "timestamp",
        "trace_id",
        "command_id",
        "router_version",
        "router_strategy",
        "status",
        "latency_ms",
        "error_type",
        "suggested_intent",
        "missing_fields",
        "clarify_question",
        "entities_summary",
        "confidence",
        "model_meta",
        "baseline_intent",
        "baseline_action",
        "baseline_job_type",
    }
    assert required_keys.issubset(logged.keys())
    assert "text" not in logged


def test_shadow_router_policy_disabled(monkeypatch, tmp_path):
    log_path = tmp_path / "shadow.jsonl"
    monkeypatch.setenv("SHADOW_ROUTER_ENABLED", "true")
    monkeypatch.setenv("SHADOW_ROUTER_LOG_PATH", str(log_path))
    monkeypatch.setenv("LLM_POLICY_ENABLED", "false")

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("LLM should not be called when policy is disabled")

    monkeypatch.setattr(shadow_router, "extract_shopping_item_name", fail_if_called)
    monkeypatch.setattr(
        shadow_router,
        "_submit_shadow_task",
        lambda payload: shadow_router._run_shadow_router(payload),
    )

    router = RouterV2Pipeline()
    normalized = router.normalize(_command())
    shadow_router.start_shadow_router(_command(), normalized)

    logged = _read_log(log_path)
    assert logged["status"] == "skipped"
    assert logged["error_type"] == "policy_disabled"
