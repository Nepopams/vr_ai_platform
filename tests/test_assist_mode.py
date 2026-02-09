import json
from pathlib import Path

import routers.assist.runner as assist_runner
from routers.assist.types import ClarifyHint, EntityHints, NormalizationHint
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
        stable["question"] = payload.get("question")
    return stable


def _read_logs(path: Path):
    content = path.read_text(encoding="utf-8").strip().splitlines()
    return [json.loads(line) for line in content]


def test_assist_disabled_no_impact(monkeypatch):
    router = RouterV2Pipeline()
    monkeypatch.setenv("ASSIST_MODE_ENABLED", "false")
    baseline = router.decide(_command("Купи молоко"))

    monkeypatch.setenv("ASSIST_MODE_ENABLED", "true")
    monkeypatch.setenv("ASSIST_NORMALIZATION_ENABLED", "false")
    monkeypatch.setenv("ASSIST_ENTITY_EXTRACTION_ENABLED", "false")
    monkeypatch.setenv("ASSIST_CLARIFY_ENABLED", "false")
    decision = router.decide(_command("Купи молоко"))

    assert _stable_fields(baseline) == _stable_fields(decision)


def test_assist_timeout_fallback(monkeypatch):
    router = RouterV2Pipeline()
    monkeypatch.setenv("ASSIST_MODE_ENABLED", "false")
    baseline = router.decide(_command("Купи молоко"))

    monkeypatch.setenv("ASSIST_MODE_ENABLED", "true")
    monkeypatch.setenv("ASSIST_NORMALIZATION_ENABLED", "true")
    monkeypatch.setenv("ASSIST_ENTITY_EXTRACTION_ENABLED", "false")
    monkeypatch.setenv("ASSIST_CLARIFY_ENABLED", "false")

    timeout_hint = NormalizationHint(
        normalized_text=None,
        intent_hint=None,
        entities_hint=None,
        confidence=None,
        error_type="timeout",
        latency_ms=None,
    )
    monkeypatch.setattr(assist_runner, "_run_normalization_hint", lambda _text: timeout_hint)
    decision = router.decide(_command("Купи молоко"))

    assert _stable_fields(baseline) == _stable_fields(decision)


def test_assist_clarify_rejects_mismatched_missing_fields(monkeypatch):
    router = RouterV2Pipeline()
    monkeypatch.setenv("ASSIST_MODE_ENABLED", "true")
    monkeypatch.setenv("ASSIST_NORMALIZATION_ENABLED", "false")
    monkeypatch.setenv("ASSIST_ENTITY_EXTRACTION_ENABLED", "false")
    monkeypatch.setenv("ASSIST_CLARIFY_ENABLED", "true")

    clarify_hint = ClarifyHint(
        question="Что именно требуется сделать?",
        missing_fields=["item.name"],
        confidence=0.4,
        error_type=None,
        latency_ms=10,
    )
    monkeypatch.setattr(
        assist_runner,
        "_run_clarify_hint",
        lambda _text, _intent, _normalized=None: clarify_hint,
    )
    decision = router.decide(_command(""))

    assert decision["action"] == "clarify"
    assert decision["payload"]["question"] == "Опишите, что нужно сделать: задача или покупка?"


def test_assist_entity_whitelist(monkeypatch):
    router = RouterV2Pipeline()
    monkeypatch.setenv("ASSIST_MODE_ENABLED", "true")
    monkeypatch.setenv("ASSIST_NORMALIZATION_ENABLED", "false")
    monkeypatch.setenv("ASSIST_ENTITY_EXTRACTION_ENABLED", "true")
    monkeypatch.setenv("ASSIST_CLARIFY_ENABLED", "false")

    entity_hint = EntityHints(
        items=[{"name": "хлеб"}],
        task_hints={},
        confidence=0.4,
        error_type=None,
        latency_ms=10,
    )
    monkeypatch.setattr(assist_runner, "_run_entity_hint", lambda _text: entity_hint)
    decision = router.decide(_command("Купи"))

    assert decision["action"] == "clarify"
    assert decision["payload"]["missing_fields"] == ["item.name"]


def test_assist_log_no_raw_text(monkeypatch, tmp_path):
    log_path = tmp_path / "assist.jsonl"
    monkeypatch.setenv("ASSIST_LOG_PATH", str(log_path))
    monkeypatch.setenv("ASSIST_MODE_ENABLED", "true")
    monkeypatch.setenv("ASSIST_NORMALIZATION_ENABLED", "true")
    monkeypatch.setenv("ASSIST_ENTITY_EXTRACTION_ENABLED", "false")
    monkeypatch.setenv("ASSIST_CLARIFY_ENABLED", "false")

    policy_disabled_hint = NormalizationHint(
        normalized_text=None,
        intent_hint=None,
        entities_hint=None,
        confidence=None,
        error_type="policy_disabled",
        latency_ms=None,
    )
    monkeypatch.setattr(assist_runner, "_run_normalization_hint", lambda _text: policy_disabled_hint)

    router = RouterV2Pipeline()
    router.decide(_command("Купи молоко"))

    logs = _read_logs(log_path)
    assert any(entry["step"] == "normalizer" for entry in logs)
    assert all("text" not in entry for entry in logs)
