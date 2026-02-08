"""End-to-end integration tests for multi-item pipeline (ST-011)."""

import json
from pathlib import Path

from jsonschema import validate

from routers.v2 import RouterV2Pipeline


BASE_DIR = Path(__file__).resolve().parents[1]
DECISION_SCHEMA_PATH = BASE_DIR / "contracts" / "schemas" / "decision.schema.json"


def _load_decision_schema():
    return json.loads(DECISION_SCHEMA_PATH.read_text(encoding="utf-8"))


def _command(text, context=None):
    return {
        "command_id": "cmd-e2e",
        "user_id": "user-1",
        "timestamp": "2026-01-01T00:00:00Z",
        "text": text,
        "capabilities": ["start_job", "propose_add_shopping_item", "propose_create_task", "clarify"],
        "context": context
        or {
            "household": {
                "members": [{"user_id": "user-1", "display_name": "Тест"}],
                "shopping_lists": [{"list_id": "list-1", "name": "Продукты"}],
            }
        },
    }


def test_e2e_multi_item_russian():
    """AC-7: Full pipeline 'Купи молоко, хлеб и бананы' -> 3 proposed_actions."""
    router = RouterV2Pipeline()
    decision = router.decide(_command("Купи молоко, хлеб и бананы"))

    assert decision["action"] == "start_job"
    assert decision["status"] == "ok"
    actions = decision["payload"].get("proposed_actions", [])
    assert len(actions) == 3
    names = [a["payload"]["item"]["name"] for a in actions]
    assert "молоко" in names
    assert "хлеб" in names
    assert "бананы" in names


def test_e2e_multi_item_english():
    """E2E: 'Buy apples and oranges' -> 2 proposed_actions."""
    router = RouterV2Pipeline()
    decision = router.decide(_command("Buy apples and oranges"))

    assert decision["action"] == "start_job"
    actions = decision["payload"].get("proposed_actions", [])
    assert len(actions) == 2
    names = [a["payload"]["item"]["name"] for a in actions]
    assert "apples" in names
    assert "oranges" in names


def test_e2e_single_item_unchanged():
    """AC-3 regression: single item -> 1 proposed_action."""
    router = RouterV2Pipeline()
    decision = router.decide(_command("Купи молоко"))

    assert decision["action"] == "start_job"
    actions = decision["payload"].get("proposed_actions", [])
    assert len(actions) == 1
    assert actions[0]["payload"]["item"]["name"] == "молоко"


def test_e2e_decision_schema_valid():
    """AC-5: Multi-item decision validates against decision.schema.json."""
    schema = _load_decision_schema()
    router = RouterV2Pipeline()
    decision = router.decide(_command("Купи молоко, хлеб и бананы"))

    validate(instance=decision, schema=schema)


def test_e2e_partial_trust_not_broken(monkeypatch):
    """AC-6: Partial trust disabled -> single item still works (no crash)."""
    monkeypatch.setenv("PARTIAL_TRUST_ENABLED", "false")
    router = RouterV2Pipeline()
    decision = router.decide(_command("Купи молоко"))

    assert decision["action"] == "start_job"
    actions = decision["payload"].get("proposed_actions", [])
    assert len(actions) == 1


def test_e2e_multi_item_with_quantity():
    """AC-2: 'Купи 2 литра молока и хлеб' -> quantity/unit in first item."""
    router = RouterV2Pipeline()
    decision = router.decide(_command("Купи 2 литра молока и хлеб"))

    assert decision["action"] == "start_job"
    actions = decision["payload"].get("proposed_actions", [])
    assert len(actions) == 2
    first_item = actions[0]["payload"]["item"]
    assert first_item["name"] == "молока"
    assert first_item["quantity"] == "2"
    assert first_item["unit"] == "литра"
