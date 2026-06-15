"""Regression tests for Domain Planner v1 narrow corridor."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from jsonschema import validate

from app.asr.client import AsrTranscriptionResult
from app.main import create_app
from graphs.core_graph import process_command
from routers.v2 import RouterV2Pipeline


BASE_DIR = Path(__file__).resolve().parents[1]
DECISION_SCHEMA_PATH = BASE_DIR / "contracts" / "schemas" / "decision.schema.json"


def _decision_schema():
    return json.loads(DECISION_SCHEMA_PATH.read_text(encoding="utf-8"))


def _context(*, shopping_lists=None):
    return {
        "household": {
            "household_id": "house-test",
            "members": [{"user_id": "user-1", "display_name": "Tester"}],
            "shopping_lists": shopping_lists
            if shopping_lists is not None
            else [{"list_id": "list-1", "name": "Groceries"}],
        },
        "defaults": {"default_assignee_id": "user-1", "default_list_id": "list-1"},
    }


def _command(text: str, *, context=None):
    return {
        "command_id": "cmd-domain-planner",
        "user_id": "user-1",
        "timestamp": "2026-06-15T12:00:00Z",
        "text": text,
        "capabilities": [
            "start_job",
            "propose_create_task",
            "propose_add_shopping_item",
            "clarify",
        ],
        "context": context or _context(),
    }


def test_default_graph_preserves_multi_item_boundaries() -> None:
    decision = process_command(_command("Buy milk, bread and apples"))

    validate(instance=decision, schema=_decision_schema())
    assert decision["status"] == "ok"
    assert decision["action"] == "start_job"
    actions = decision["payload"]["proposed_actions"]
    assert [action["action"] for action in actions] == [
        "propose_add_shopping_item",
        "propose_add_shopping_item",
        "propose_add_shopping_item",
    ]
    assert [action["payload"]["item"]["name"] for action in actions] == [
        "milk",
        "bread",
        "apples",
    ]


def test_default_graph_clarifies_without_grounded_list() -> None:
    context = _context(shopping_lists=[])
    context.pop("defaults")

    decision = process_command(_command("Buy milk and bread", context=context))

    validate(instance=decision, schema=_decision_schema())
    assert decision["status"] == "clarify"
    assert decision["action"] == "clarify"
    assert "item.list_id" in decision["payload"]["missing_fields"]


def test_safe_reject_uses_first_class_reject() -> None:
    decision = process_command(_command("Assign all tasks to everyone"))

    validate(instance=decision, schema=_decision_schema())
    assert decision["status"] == "error"
    assert decision["action"] == "reject"
    assert decision["decision_outcome"] == "reject"
    assert decision["payload"]["code"] == "unsupported_or_unsafe_command"


def test_simple_russian_task_command_executes() -> None:
    decision = process_command(_command("надо полить цветы"))

    validate(instance=decision, schema=_decision_schema())
    assert decision["status"] == "ok"
    assert decision["action"] == "start_job"
    assert decision["payload"]["job_type"] == "create_task"
    assert decision["payload"]["proposed_actions"][0]["action"] == "propose_create_task"


def test_russian_shopping_add_preserves_quantity_item_boundaries() -> None:
    decision = process_command(_command("добавь 2 литра сока и 3 груши"))

    validate(instance=decision, schema=_decision_schema())
    assert decision["status"] == "ok"
    assert decision["action"] == "start_job"
    actions = decision["payload"]["proposed_actions"]
    assert [action["payload"]["item"]["name"] for action in actions] == ["сока", "груши"]
    assert actions[0]["payload"]["item"]["quantity"] == "2"
    assert actions[0]["payload"]["item"]["unit"] == "литра"
    assert actions[1]["payload"]["item"]["quantity"] == "3"


def test_russian_shopping_drop_in_list_phrase_preserves_boundaries() -> None:
    decision = process_command(_command("закинь чай и сахар в покупки"))

    validate(instance=decision, schema=_decision_schema())
    assert decision["status"] == "ok"
    assert decision["action"] == "start_job"
    actions = decision["payload"]["proposed_actions"]
    assert [action["payload"]["item"]["name"] for action in actions] == ["чай", "сахар"]


def test_unsupported_policy_device_payment_and_foreign_reference_reject() -> None:
    commands = [
        "сделай так чтобы уборка всегда назначалась автоматически",
        "закрой задачу из чужого дома",
        "включи умную лампу",
        "оплати продукты",
    ]

    for text in commands:
        decision = process_command(_command(text))

        validate(instance=decision, schema=_decision_schema())
        assert decision["status"] == "error"
        assert decision["action"] == "reject"
        assert decision["decision_outcome"] == "reject"


def test_assignment_due_and_deictic_references_do_not_execute() -> None:
    commands = [
        "Саше вынести коробки",
        "надо завтра полить цветы",
        "добавь это в список",
    ]

    for text in commands:
        decision = process_command(_command(text))

        validate(instance=decision, schema=_decision_schema())
        assert decision["status"] == "clarify"
        assert decision["action"] == "clarify"


def test_router_v2_mixed_task_shopping_does_not_execute() -> None:
    router = RouterV2Pipeline()

    decision = router.decide(_command("Add milk and create a task"))

    validate(instance=decision, schema=_decision_schema())
    assert decision["status"] == "clarify"
    assert decision["action"] == "clarify"
    assert "intent" in decision["payload"]["missing_fields"]


def test_contextual_shopping_clarifies_instead_of_execute() -> None:
    decision = process_command(_command("Купи молоко и хлеб к ужину"))

    validate(instance=decision, schema=_decision_schema())
    assert decision["status"] == "clarify"
    assert decision["action"] == "clarify"
    assert "intent" in decision["payload"]["missing_fields"]


def test_decide_route_still_returns_schema_valid(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DECISION_LOG_PATH", str(tmp_path / "decisions.jsonl"))
    monkeypatch.setenv("LOG_USER_TEXT", "false")
    client = TestClient(create_app())

    response = client.post("/v1/decide", json=_command("Fix the kitchen sink"))

    assert response.status_code == 200
    validate(instance=response.json(), schema=_decision_schema())


def test_asr_transcribe_does_not_call_decision_service(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("ASR_BASE_URL", "https://foundation-models.api.cloud.ru/v1")
    monkeypatch.setenv("ASR_API_KEY", "secret")
    monkeypatch.setenv("ASR_LOG_PATH", str(tmp_path / "asr.jsonl"))
    client = TestClient(create_app())
    result = AsrTranscriptionResult(
        transcript="Buy milk",
        provider="cloudru",
        model="openai/whisper-large-v3",
        latency_ms=123,
        upstream_status=200,
    )

    with patch("app.services.decision_service.decide") as mock_decide:
        with patch("app.routes.asr.CloudRuAsrClient") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.transcribe.return_value = result
            mock_client_cls.return_value = mock_client

            response = client.post(
                "/v1/asr/transcribe",
                files={"file": ("sample.wav", b"fake-audio", "audio/wav")},
            )

    assert response.status_code == 200
    mock_client.transcribe.assert_called_once()
    mock_decide.assert_not_called()
