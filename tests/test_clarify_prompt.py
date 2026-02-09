"""Unit tests for context-aware clarify prompt and safety refinement (ST-013)."""

from routers.assist import runner as assist_runner
from routers.assist.runner import (
    _build_clarify_prompt,
    _build_known_context,
    _clarify_question_is_safe,
    _CLARIFY_MISSING_FIELDS_VOCAB,
    _CLARIFY_SCHEMA,
)


def test_clarify_prompt_includes_intent_context():
    """AC-1: Prompt includes known intent."""
    normalized = {
        "text": "Купи молоко",
        "intent": "add_shopping_item",
        "items": [{"name": "молоко"}],
        "item_name": "молоко",
        "task_title": None,
    }
    prompt = _build_clarify_prompt("Купи молоко", "add_shopping_item", normalized)

    assert "интент=add_shopping_item" in prompt
    assert "товаров=1" in prompt


def test_clarify_prompt_includes_missing_fields_vocab():
    """AC-1: Prompt lists allowed missing_fields."""
    prompt = _build_clarify_prompt("Купи", "add_shopping_item", {})

    assert "item.name" in prompt
    assert "task.title" in prompt
    assert "intent" in prompt


def test_clarify_prompt_no_normalized_backward_compat():
    """Backward compat: no normalized -> 'нет данных'."""
    prompt = _build_clarify_prompt("текст", "unknown")

    assert "нет данных" in prompt
    assert "Текст: текст" in prompt


def test_known_context_nothing_extracted():
    """Known context with empty normalized."""
    ctx = _build_known_context({"intent": "clarify_needed", "items": []})
    assert ctx == "ничего не извлечено"


def test_known_context_shopping_with_items():
    """Known context shows item count without raw names."""
    ctx = _build_known_context(
        {
            "intent": "add_shopping_item",
            "items": [{"name": "молоко"}, {"name": "хлеб"}],
            "item_name": "молоко",
        }
    )
    assert "интент=add_shopping_item" in ctx
    assert "товаров=2" in ctx
    assert "название_товара=есть" in ctx
    assert "молоко" not in ctx  # AC-6: no raw text in context string


def test_clarify_schema_constrains_vocabulary():
    """AC-2: Schema missing_fields items have enum constraint."""
    items_schema = _CLARIFY_SCHEMA["properties"]["missing_fields"]["items"]
    assert "enum" in items_schema
    assert set(items_schema["enum"]) == set(_CLARIFY_MISSING_FIELDS_VOCAB)


def test_safety_rejects_irrelevant_question():
    """AC-3: Off-topic question rejected when missing_fields provided."""
    result = _clarify_question_is_safe(
        "Какая погода завтра?",
        "add_shopping_item",
        "Купи молоко",
        missing_fields=["item.name"],
    )
    assert result is False


def test_safety_accepts_relevant_question():
    """AC-3: Relevant question accepted when missing_fields provided."""
    result = _clarify_question_is_safe(
        "Какой товар добавить в список покупок?",
        "add_shopping_item",
        "Купи",
        missing_fields=["item.name"],
    )
    assert result is True


def test_safety_backward_compat_no_missing_fields():
    """Existing behavior unchanged when missing_fields=None."""
    # Known intent, no missing_fields -> accepted (existing behavior)
    result = _clarify_question_is_safe(
        "Что-нибудь ещё?",
        "add_shopping_item",
        "Купи молоко",
        missing_fields=None,
    )
    assert result is True

    # Unknown intent, has "?" -> accepted (existing behavior)
    result2 = _clarify_question_is_safe(
        "Какая погода завтра?",
        "unknown",
        "текст",
        missing_fields=None,
    )
    assert result2 is True


def test_safety_echo_still_rejected():
    """Existing echo-prevention not weakened."""
    result = _clarify_question_is_safe(
        "Купи молоко — уточните товар?",
        "add_shopping_item",
        "Купи молоко",
        missing_fields=["item.name"],
    )
    assert result is False
