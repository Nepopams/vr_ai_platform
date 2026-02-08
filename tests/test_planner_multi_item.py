"""Unit tests for V2 planner multi-item proposed_actions (ST-011)."""

from routers.v2 import RouterV2Pipeline


def _command(text="", context=None):
    cmd = {
        "command_id": "cmd-test",
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
    return cmd


def _normalized(items=None, item_name=None, intent="add_shopping_item", text="Купи молоко"):
    return {
        "text": text,
        "intent": intent,
        "items": items or [],
        "item_name": item_name,
        "task_title": None,
        "capabilities": {"start_job", "propose_add_shopping_item", "propose_create_task", "clarify"},
    }


def test_plan_multi_item_3_actions():
    """AC-1: 3 items -> 3 proposed_actions."""
    router = RouterV2Pipeline()
    items = [{"name": "молоко"}, {"name": "хлеб"}, {"name": "бананы"}]
    normalized = _normalized(items=items, text="Купи молоко, хлеб и бананы")
    plan = router.plan(normalized, _command("Купи молоко, хлеб и бананы"))

    actions = plan["proposed_actions"]
    assert len(actions) == 3
    names = [a["payload"]["item"]["name"] for a in actions]
    assert names == ["молоко", "хлеб", "бананы"]
    assert all(a["action"] == "propose_add_shopping_item" for a in actions)


def test_plan_multi_item_with_quantity_unit():
    """AC-2: quantity and unit propagated to proposed_action payload."""
    router = RouterV2Pipeline()
    items = [{"name": "молока", "quantity": "2", "unit": "литра"}, {"name": "хлеб"}]
    normalized = _normalized(items=items, text="Купи 2 литра молока и хлеб")
    plan = router.plan(normalized, _command("Купи 2 литра молока и хлеб"))

    actions = plan["proposed_actions"]
    assert len(actions) == 2
    first_item = actions[0]["payload"]["item"]
    assert first_item["name"] == "молока"
    assert first_item["quantity"] == "2"
    assert first_item["unit"] == "литра"
    second_item = actions[1]["payload"]["item"]
    assert second_item["name"] == "хлеб"
    assert "quantity" not in second_item
    assert "unit" not in second_item


def test_plan_single_item_backward_compat():
    """AC-3: single item -> exactly 1 proposed_action."""
    router = RouterV2Pipeline()
    items = [{"name": "молоко"}]
    normalized = _normalized(items=items, item_name="молоко", text="Купи молоко")
    plan = router.plan(normalized, _command("Купи молоко"))

    actions = plan["proposed_actions"]
    assert len(actions) == 1
    assert actions[0]["payload"]["item"]["name"] == "молоко"


def test_plan_empty_items_fallback_to_item_name():
    """Fallback: empty items but item_name present -> 1 proposed_action from item_name."""
    router = RouterV2Pipeline()
    normalized = _normalized(items=[], item_name="молоко", text="Купи молоко")
    plan = router.plan(normalized, _command("Купи молоко"))

    actions = plan["proposed_actions"]
    assert len(actions) == 1
    assert actions[0]["payload"]["item"]["name"] == "молоко"


def test_plan_list_id_propagated_to_all():
    """AC-8: list_id propagated to every item."""
    router = RouterV2Pipeline()
    items = [{"name": "молоко"}, {"name": "хлеб"}]
    normalized = _normalized(items=items, text="Купи молоко и хлеб")
    context = {
        "household": {
            "members": [{"user_id": "user-1", "display_name": "Тест"}],
            "shopping_lists": [{"list_id": "list-42", "name": "Еда"}],
        },
        "defaults": {"default_list_id": "list-42"},
    }
    plan = router.plan(normalized, _command("Купи молоко и хлеб", context=context))

    actions = plan["proposed_actions"]
    assert len(actions) == 2
    assert actions[0]["payload"]["item"]["list_id"] == "list-42"
    assert actions[1]["payload"]["item"]["list_id"] == "list-42"
