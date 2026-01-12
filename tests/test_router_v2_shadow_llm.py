import routers.v2 as router_v2
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


def test_router_v2_shadow_call(monkeypatch):
    monkeypatch.setenv("LLM_SHOPPING_EXTRACTOR_ENABLED", "true")
    called = {"value": False}

    def fake_shadow_invoke(**_kwargs):
        called["value"] = True

    monkeypatch.setattr(router_v2, "shadow_invoke", fake_shadow_invoke)
    router = RouterV2Pipeline()
    decision = router.decide(_command())
    assert called["value"] is True
    assert decision["action"] == "start_job"
