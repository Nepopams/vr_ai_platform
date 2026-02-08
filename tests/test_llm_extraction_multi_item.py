"""Tests for multi-item LLM extraction (ST-010)."""

from llm_policy.tasks import ExtractionResult, SHOPPING_EXTRACTION_SCHEMA


def test_shopping_schema_has_items_array():
    """AC-1: Schema defines items as array of objects."""
    props = SHOPPING_EXTRACTION_SCHEMA["properties"]
    assert "items" in props
    items_schema = props["items"]
    assert items_schema["type"] == "array"
    item_obj = items_schema["items"]
    assert item_obj["type"] == "object"
    assert "name" in item_obj["properties"]
    assert "quantity" in item_obj["properties"]
    assert "unit" in item_obj["properties"]
    assert item_obj["required"] == ["name"]


def test_extraction_result_items_list():
    """AC-2: ExtractionResult.items returns list of dicts."""
    result = ExtractionResult(
        items=[{"name": "молоко"}, {"name": "хлеб"}],
        used_policy=True,
        error_type=None,
    )
    assert len(result.items) == 2
    assert result.items[0]["name"] == "молоко"
    assert result.items[1]["name"] == "хлеб"


def test_extraction_result_item_name_compat():
    """AC-2: .item_name returns first item's name for backward compat."""
    result = ExtractionResult(
        items=[{"name": "молоко"}, {"name": "хлеб"}],
        used_policy=True,
        error_type=None,
    )
    assert result.item_name == "молоко"


def test_extraction_result_empty_items():
    """AC-2: Empty items -> item_name is None."""
    result = ExtractionResult(items=[], used_policy=True, error_type="timeout")
    assert result.item_name is None
    assert result.items == []


def test_extraction_result_single_item():
    """Backward compat: single item works like old item_name."""
    result = ExtractionResult(
        items=[{"name": "бананы", "quantity": "3", "unit": "шт"}],
        used_policy=False,
        error_type=None,
    )
    assert result.item_name == "бананы"
    assert result.items[0]["quantity"] == "3"
    assert result.items[0]["unit"] == "шт"
