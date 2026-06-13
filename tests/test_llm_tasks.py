import sys
from pathlib import Path

from jsonschema import validate

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from llm_policy.runtime import set_llm_caller
from llm_policy.tasks import (
    SHOPPING_EXTRACTION_SCHEMA,
    _build_shopping_prompt,
    _normalize_shopping_items,
    extract_shopping_item_name,
)


class StubCaller:
    def __init__(self, response: str) -> None:
        self.response = response

    def __call__(self, spec, prompt: str) -> str:
        return self.response


def test_normalize_numeric_quantity_to_string() -> None:
    items = _normalize_shopping_items(
        [
            {"name": "кефир", "quantity": 2, "unit": "литра"},
            {"name": "сок", "quantity": 2.0},
            {"name": "сыр", "quantity": 2.5},
            {"name": " хлеб ", "quantity": " 2 ", "unit": " шт "},
        ]
    )

    assert items == [
        {"name": "кефир", "quantity": "2", "unit": "литра"},
        {"name": "сок", "quantity": "2"},
        {"name": "сыр", "quantity": "2.5"},
        {"name": "хлеб", "quantity": "2", "unit": "шт"},
    ]


def test_normalize_omits_empty_or_missing_quantity_and_unit() -> None:
    items = _normalize_shopping_items(
        [
            {"name": "молоко", "quantity": None, "unit": None},
            {"name": "хлеб", "quantity": "", "unit": " "},
            {"name": "чай"},
        ]
    )

    assert items == [{"name": "молоко"}, {"name": "хлеб"}, {"name": "чай"}]
    assert all(not isinstance(item.get("quantity"), (int, float)) for item in items)


def test_normalize_skips_invalid_items_and_trims_name() -> None:
    items = _normalize_shopping_items(
        [
            {"quantity": 2, "unit": "шт"},
            {"name": ""},
            {"name": "  яблоки  ", "quantity": {"value": 2}, "unit": 10},
            "not an item",
        ]
    )

    assert items == [{"name": "яблоки"}]


def test_shopping_schema_accepts_numeric_quantity() -> None:
    validate(
        instance={"items": [{"name": "кефир", "quantity": 2, "unit": "литра"}]},
        schema=SHOPPING_EXTRACTION_SCHEMA,
    )


def test_shopping_prompt_contains_json_only_and_quantity_rules() -> None:
    prompt = _build_shopping_prompt("купи 2 литра кефира")

    assert "только JSON object" in prompt
    assert "без markdown" in prompt
    assert "code fences" in prompt
    assert "quantity только string или null" in prompt
    assert '"quantity":"2"' in prompt


def test_extract_shopping_item_name_normalizes_mocked_llm_quantity(
    monkeypatch,
) -> None:
    monkeypatch.setenv("LLM_POLICY_ENABLED", "true")
    monkeypatch.setenv("LLM_POLICY_ALLOW_PLACEHOLDERS", "true")
    set_llm_caller(
        StubCaller('{"items":[{"name":"кефир","quantity":2,"unit":"литра"}]}')
    )

    try:
        result = extract_shopping_item_name("купи 2 литра кефира", policy_enabled=True)

        assert result.used_policy is True
        assert result.error_type is None
        assert result.items == [{"name": "кефир", "quantity": "2", "unit": "литра"}]
    finally:
        set_llm_caller(None)
