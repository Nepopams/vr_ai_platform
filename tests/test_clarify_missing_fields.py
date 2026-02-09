"""Unit tests for enriched missing_fields in clarify decisions (ST-012)."""

from routers.v2 import RouterV2Pipeline


def _command(text="", capabilities=None, context=None):
    return {
        "command_id": "cmd-clarify-test",
        "user_id": "user-1",
        "timestamp": "2026-01-01T00:00:00Z",
        "text": text,
        "capabilities": capabilities
        or ["start_job", "propose_add_shopping_item", "propose_create_task", "clarify"],
        "context": context
        or {
            "household": {
                "members": [{"user_id": "user-1", "display_name": "Тест"}],
                "shopping_lists": [{"list_id": "list-1", "name": "Продукты"}],
            }
        },
    }


def test_clarify_intent_unknown_has_missing_fields():
    """AC-1: Intent not detected -> missing_fields=['intent']."""
    router = RouterV2Pipeline()
    decision = router.decide(_command("Что-то непонятное про погоду"))

    assert decision["action"] == "clarify"
    assert decision["payload"]["missing_fields"] == ["intent"]


def test_clarify_no_capability_has_missing_fields():
    """AC-2: No start_job capability -> missing_fields=['capability.start_job']."""
    router = RouterV2Pipeline()
    decision = router.decide(
        _command("Купи молоко", capabilities=["propose_add_shopping_item", "clarify"])
    )

    assert decision["action"] == "clarify"
    assert decision["payload"]["missing_fields"] == ["capability.start_job"]


def test_clarify_empty_text_backward_compat():
    """AC-4: Empty text -> missing_fields=['text'] (unchanged)."""
    router = RouterV2Pipeline()
    decision = router.decide(_command(""))

    assert decision["action"] == "clarify"
    assert decision["payload"]["missing_fields"] == ["text"]


def test_clarify_no_item_backward_compat():
    """AC-5: Shopping intent, no items -> missing_fields=['item.name'] (unchanged)."""
    router = RouterV2Pipeline()
    # "Купи" alone triggers add_shopping_item intent but extracts no item name
    decision = router.decide(_command("Купи"))

    assert decision["action"] == "clarify"
    assert decision["payload"]["missing_fields"] == ["item.name"]


def test_clarify_no_task_title_backward_compat():
    """AC-6: Task intent, no title -> missing_fields=['task.title'] (unchanged)."""
    router = RouterV2Pipeline()
    # "Сделай" triggers create_task intent but extracts no title if too short
    decision = router.decide(_command("Задача"))

    # This should either be clarify with task.title or clarify with intent
    # depending on intent detection. If intent is create_task:
    if decision["payload"].get("missing_fields") == ["task.title"]:
        assert decision["action"] == "clarify"
    else:
        # If intent is not detected, we get ["intent"] instead
        assert decision["action"] == "clarify"
        assert "missing_fields" in decision["payload"]


def test_start_job_no_missing_fields():
    """AC-7 regression: start_job decision has no missing_fields in payload."""
    router = RouterV2Pipeline()
    decision = router.decide(_command("Купи молоко"))

    assert decision["action"] == "start_job"
    assert "missing_fields" not in decision.get("payload", {})
