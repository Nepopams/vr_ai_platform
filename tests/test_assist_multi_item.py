"""Tests for assist mode multi-item entity hints (ST-010)."""

import routers.assist.runner as assist_runner
from routers.assist.runner import _pick_matching_item, _pick_matching_items, _ENTITY_SCHEMA
from routers.assist.types import AgentEntityHint, EntityHints


def test_entity_schema_has_structured_items():
    """AC-7: _ENTITY_SCHEMA items is array of objects with name/quantity/unit."""
    items_schema = _ENTITY_SCHEMA["properties"]["items"]
    assert items_schema["type"] == "array"
    item_obj = items_schema["items"]
    assert item_obj["type"] == "object"
    assert "name" in item_obj["properties"]
    assert "quantity" in item_obj["properties"]
    assert "unit" in item_obj["properties"]
    assert item_obj["required"] == ["name"]


def test_pick_matching_item_returns_first_dict():
    """_pick_matching_item returns first matching dict."""
    items = [{"name": "молоко"}, {"name": "хлеб"}, {"name": "бананы"}]
    result = _pick_matching_item(items, "Купи молоко и хлеб")
    assert result == {"name": "молоко"}


def test_pick_matching_item_no_match():
    """_pick_matching_item returns None when no match."""
    items = [{"name": "торт"}]
    result = _pick_matching_item(items, "Купи молоко")
    assert result is None


def test_pick_matching_items_all():
    """_pick_matching_items returns all matching dicts."""
    items = [{"name": "молоко"}, {"name": "хлеб"}, {"name": "бананы"}]
    result = _pick_matching_items(items, "Купи молоко, хлеб и бананы")
    assert len(result) == 3
    names = [item["name"] for item in result]
    assert names == ["молоко", "хлеб", "бананы"]


def test_pick_matching_items_partial():
    """_pick_matching_items returns only matches."""
    items = [{"name": "молоко"}, {"name": "торт"}, {"name": "хлеб"}]
    result = _pick_matching_items(items, "Купи молоко и хлеб")
    assert len(result) == 2
    names = [item["name"] for item in result]
    assert "молоко" in names
    assert "хлеб" in names
    assert "торт" not in names


def test_pick_matching_items_no_match():
    """_pick_matching_items returns empty list when no match."""
    items = [{"name": "торт"}, {"name": "печенье"}]
    result = _pick_matching_items(items, "Купи молоко")
    assert result == []


def test_entity_hints_all_items_applied(monkeypatch):
    """AC-3: All matching LLM entity hint items populate normalized['items']."""
    hint = EntityHints(
        items=[{"name": "молоко"}, {"name": "хлеб"}, {"name": "бананы"}],
        task_hints={},
        confidence=0.9,
        error_type=None,
        latency_ms=10,
    )
    normalized = {
        "text": "Купи молоко, хлеб и бананы",
        "intent": "add_shopping_item",
        "item_name": None,
        "items": [],
    }
    monkeypatch.setattr(assist_runner, "_log_step", lambda *a, **kw: None)
    updated, accepted = assist_runner._apply_entity_hints(
        normalized, hint, original_text="Купи молоко, хлеб и бананы"
    )
    assert accepted is True
    assert len(updated["items"]) == 3
    names = [item["name"] for item in updated["items"]]
    assert names == ["молоко", "хлеб", "бананы"]
    assert updated["item_name"] == "молоко"


def test_entity_hints_partial_match(monkeypatch):
    """AC-4: Only items confirmed in original text are accepted."""
    hint = EntityHints(
        items=[{"name": "молоко"}, {"name": "торт"}, {"name": "хлеб"}],
        task_hints={},
        confidence=0.9,
        error_type=None,
        latency_ms=10,
    )
    normalized = {
        "text": "Купи молоко и хлеб",
        "intent": "add_shopping_item",
        "item_name": None,
        "items": [],
    }
    monkeypatch.setattr(assist_runner, "_log_step", lambda *a, **kw: None)
    updated, accepted = assist_runner._apply_entity_hints(
        normalized, hint, original_text="Купи молоко и хлеб"
    )
    assert accepted is True
    assert len(updated["items"]) == 2
    names = [item["name"] for item in updated["items"]]
    assert "молоко" in names
    assert "хлеб" in names
    assert "торт" not in names


def test_entity_hints_no_match(monkeypatch):
    """AC-4 edge: No items match -> items unchanged."""
    hint = EntityHints(
        items=[{"name": "торт"}],
        task_hints={},
        confidence=0.9,
        error_type=None,
        latency_ms=10,
    )
    baseline_items = [{"name": "молоко"}]
    normalized = {
        "text": "Купи молоко",
        "intent": "add_shopping_item",
        "item_name": None,
        "items": baseline_items,
    }
    monkeypatch.setattr(assist_runner, "_log_step", lambda *a, **kw: None)
    updated, accepted = assist_runner._apply_entity_hints(
        normalized, hint, original_text="Купи молоко"
    )
    assert accepted is False
    assert updated["items"] == baseline_items


def test_agent_hint_multi_item(monkeypatch):
    """AC-5: Agent hint path populates multi-item."""
    agent_hint = AgentEntityHint(
        status="ok",
        items=[{"name": "яблоки"}, {"name": "апельсины"}],
        latency_ms=5,
    )
    normalized = {
        "text": "Купи яблоки и апельсины",
        "intent": "add_shopping_item",
        "item_name": None,
        "items": [],
    }
    monkeypatch.setattr(assist_runner, "_log_step", lambda *a, **kw: None)
    updated, accepted = assist_runner._apply_entity_hints(
        normalized, None, original_text="Купи яблоки и апельсины", agent_hint=agent_hint
    )
    assert accepted is True
    assert len(updated["items"]) == 2
    names = [item["name"] for item in updated["items"]]
    assert "яблоки" in names
    assert "апельсины" in names
    assert updated["item_name"] == "яблоки"


def test_entity_hints_fallback_no_hint(monkeypatch):
    """AC-6: No hint = baseline items unchanged."""
    baseline_items = [{"name": "молоко"}, {"name": "хлеб"}]
    normalized = {
        "text": "Купи молоко и хлеб",
        "intent": "add_shopping_item",
        "item_name": "молоко",
        "items": baseline_items,
    }
    monkeypatch.setattr(assist_runner, "_log_step", lambda *a, **kw: None)
    updated, accepted = assist_runner._apply_entity_hints(
        normalized, None, original_text="Купи молоко и хлеб"
    )
    assert accepted is False
    assert updated["items"] == baseline_items
