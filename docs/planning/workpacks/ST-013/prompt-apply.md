# Codex APPLY Prompt — ST-013: Context-Aware LLM Clarify Prompt

## Role

You are an implementation agent. Apply changes exactly as specified below.

## Environment

- Python binary: `python3` (NOT `python`)
- All tests: `python3 -m pytest tests/ -v`

## STOP-THE-LINE

If any instruction contradicts what you see in the codebase, STOP and report.

---

## Context

Implementing ST-013: Context-aware LLM clarify prompt and safety refinement in `routers/assist/runner.py`.

**PLAN findings confirmed:**
- `_CLARIFY_SCHEMA` missing_fields unconstrained (line 91)
- `_run_clarify_hint(text, intent)` has no `normalized` param (line 302)
- `_build_clarify_prompt(text, intent)` has no context about known/missing fields (line 578)
- `_build_assist_hints` has `normalized` in scope (line 139)
- `_clarify_question_is_safe` has no relevance check (line 628)
- `_select_clarify_hint` doesn't pass missing_fields to safety (line 519)
- Mock in `test_assist_mode.py:102` uses `lambda _text, _intent:` — MUST be updated

---

## Step 1: Update `_CLARIFY_SCHEMA` in `routers/assist/runner.py`

Find lines 87-96:
```python
_CLARIFY_SCHEMA = {
    "type": "object",
    "properties": {
        "question": {"type": "string", "minLength": 1},
        "missing_fields": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "number"},
    },
    "required": ["question"],
    "additionalProperties": False,
}
```

Replace with:
```python
_CLARIFY_MISSING_FIELDS_VOCAB = [
    "text", "intent", "item.name", "item.list_id",
    "task.title", "capability.start_job",
]

_CLARIFY_SCHEMA = {
    "type": "object",
    "properties": {
        "question": {"type": "string", "minLength": 1},
        "missing_fields": {
            "type": "array",
            "items": {"type": "string", "enum": _CLARIFY_MISSING_FIELDS_VOCAB},
        },
        "confidence": {"type": "number"},
    },
    "required": ["question"],
    "additionalProperties": False,
}
```

---

## Step 2: Update `_run_clarify_hint()` in `routers/assist/runner.py`

Find lines 302-326:
```python
def _run_clarify_hint(text: str, intent: Optional[str]) -> ClarifyHint:
    result = _run_llm_task(
        task_id=_CLARIFY_TASK_ID,
        prompt=_build_clarify_prompt(text, intent),
        schema=_CLARIFY_SCHEMA,
    )
```

Replace the function signature and first lines ONLY (keep the rest of the function body unchanged):
```python
def _run_clarify_hint(text: str, intent: Optional[str], normalized: Optional[Dict[str, Any]] = None) -> ClarifyHint:
    result = _run_llm_task(
        task_id=_CLARIFY_TASK_ID,
        prompt=_build_clarify_prompt(text, intent, normalized),
        schema=_CLARIFY_SCHEMA,
    )
```

Everything from `if result["status"] != "ok":` onward stays identical.

---

## Step 3: Update `_build_assist_hints()` call in `routers/assist/runner.py`

Find line 139:
```python
        clarify = _run_clarify_hint(command.get("text", ""), normalized.get("intent"))
```

Replace with:
```python
        clarify = _run_clarify_hint(command.get("text", ""), normalized.get("intent"), normalized)
```

---

## Step 4: Add `_DOMAIN_RELEVANCE_TOKENS` and update `_clarify_question_is_safe()` in `routers/assist/runner.py`

Find lines 628-640:
```python
def _clarify_question_is_safe(question: str, intent: Optional[str], original_text: str) -> bool:
    if not question:
        return False
    if len(question) < 5:
        return False
    if len(question) > 200:
        return False
    lowered = question.lower()
    if original_text and original_text.lower() in lowered:
        return False
    if intent in {"add_shopping_item", "create_task"}:
        return True
    return "?" in question
```

Replace with:
```python
_DOMAIN_RELEVANCE_TOKENS = frozenset({
    "товар", "продукт", "купить", "покупк", "список", "добавить", "магазин",
    "задач", "дел", "сделать", "создать", "выполн",
    "нужн", "хотите", "помочь", "уточн",
    "item", "product", "buy", "shop", "list", "add",
    "task", "todo", "create",
})


def _clarify_question_is_safe(
    question: str,
    intent: Optional[str],
    original_text: str,
    missing_fields: Optional[List[str]] = None,
) -> bool:
    if not question:
        return False
    if len(question) < 5:
        return False
    if len(question) > 200:
        return False
    lowered = question.lower()
    if original_text and original_text.lower() in lowered:
        return False
    if missing_fields:
        if not any(token in lowered for token in _DOMAIN_RELEVANCE_TOKENS):
            return False
    if intent in {"add_shopping_item", "create_task"}:
        return True
    return "?" in question
```

---

## Step 5: Update `_select_clarify_hint()` to pass missing_fields in `routers/assist/runner.py`

Find line 519:
```python
    if not _clarify_question_is_safe(question, normalized.get("intent"), original_text):
```

Replace with:
```python
    if not _clarify_question_is_safe(question, normalized.get("intent"), original_text, missing_fields=hint.missing_fields):
```

---

## Step 6: Replace `_build_clarify_prompt()` in `routers/assist/runner.py`

Find lines 578-585:
```python
def _build_clarify_prompt(text: str, intent: Optional[str]) -> str:
    intent_label = intent or "unknown"
    return (
        "Предложи один уточняющий вопрос и missing_fields. "
        "Вопрос должен быть конкретным и релевантным.\n"
        f"Интент: {intent_label}\n"
        f"Текст: {text}"
    )
```

Replace with:
```python
def _build_clarify_prompt(text: str, intent: Optional[str], normalized: Optional[Dict[str, Any]] = None) -> str:
    intent_label = intent or "unknown"
    known = _build_known_context(normalized) if normalized else "нет данных"
    vocab = ", ".join(_CLARIFY_MISSING_FIELDS_VOCAB)
    return (
        "Предложи один уточняющий вопрос и missing_fields. "
        "Вопрос должен быть конкретным и помогать пользователю дополнить недостающую информацию.\n"
        f"Допустимые missing_fields: {vocab}.\n"
        f"Интент: {intent_label}\n"
        f"Известно: {known}\n"
        f"Текст: {text}"
    )


def _build_known_context(normalized: Dict[str, Any]) -> str:
    parts: List[str] = []
    intent = normalized.get("intent")
    if intent and intent != "clarify_needed":
        parts.append(f"интент={intent}")
    items = normalized.get("items", [])
    if items:
        parts.append(f"товаров={len(items)}")
    if normalized.get("item_name"):
        parts.append("название_товара=есть")
    if normalized.get("task_title"):
        parts.append("задача=есть")
    return ", ".join(parts) if parts else "ничего не извлечено"
```

---

## Step 7: Update mock in `tests/test_assist_mode.py`

Find line 102:
```python
    monkeypatch.setattr(assist_runner, "_run_clarify_hint", lambda _text, _intent: clarify_hint)
```

Replace with:
```python
    monkeypatch.setattr(assist_runner, "_run_clarify_hint", lambda _text, _intent, _normalized=None: clarify_hint)
```

---

## Step 8: Create `tests/test_clarify_prompt.py`

Create this NEW file with the following content:

```python
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
    ctx = _build_known_context({
        "intent": "add_shopping_item",
        "items": [{"name": "молоко"}, {"name": "хлеб"}],
        "item_name": "молоко",
    })
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
```

---

## Verification

Run ALL tests after completing all steps:

```bash
# 1. New tests
python3 -m pytest tests/test_clarify_prompt.py -v

# 2. Full test suite
python3 -m pytest tests/ -v

# 3. No secrets
grep -rn 'sk-\|api_key' routers/assist/runner.py tests/test_clarify_prompt.py tests/test_assist_mode.py
```

Expected: ALL tests pass, no secrets.

---

## Files summary

| File | Action |
|------|--------|
| `routers/assist/runner.py` | Edit 6 locations (Steps 1-6) |
| `tests/test_assist_mode.py` | Edit 1 mock (Step 7) |
| `tests/test_clarify_prompt.py` | Create new file (Step 8) |

## Invariants (DO NOT break)

- `graphs/core_graph.py` — NOT modified
- `contracts/schemas/decision.schema.json` — NOT modified
- `routers/v2.py` — NOT modified
- Existing safety checks in `_clarify_question_is_safe` (non-empty, length, echo) — NOT removed
- `apply_assist_hints()` return type (`AssistApplication`) — NOT changed
- `ClarifyHint` type — NOT changed
- No raw user text in logs (AC-6)
