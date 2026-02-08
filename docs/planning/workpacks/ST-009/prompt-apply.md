# Codex APPLY Prompt — ST-009: Baseline Multi-Item Extraction

## Role

You are an implementation agent. Modify and create ONLY the files listed below.

## Environment

- Python binary: `python3` (NOT `python`)

## STOP-THE-LINE

If you need to modify any file not listed in "Allowed files", STOP and report.

## Allowed files

### MODIFY
- `graphs/core_graph.py`
- `routers/v2.py`
- `agent_runner/schemas.py`
- `agents/baseline_shopping.py`
- `agents/baseline_clarify.py`
- `skills/graph-sanity/fixtures/golden_dataset.json`
- `tests/test_agent_baseline_v0.py` (ONLY if assertions break due to items type change)

### CREATE
- `tests/test_multi_item_extraction.py`

## Forbidden

- Any file under `routers/assist/`, `llm_policy/`, `routers/partial_trust_*`
- Any file under `docs/`
- `git commit`, `git push`

---

## Step 1: Add `extract_items()` to `graphs/core_graph.py`

Add these two functions AFTER the existing `extract_item_name()` function (after line 68), BEFORE `build_proposed_action()` (line 71):

```python
import re as _re


def extract_items(text: str) -> List[Dict[str, Any]]:
    """Split shopping text into individual items with optional quantity/unit.

    Supports comma and conjunction ("и"/"and") separation.
    Returns list of dicts: [{name, quantity?, unit?}].
    """
    lowered = text.lower()
    raw = None
    for pattern in SHOPPING_KEYWORDS:
        # find the keyword as a prefix of a word
        kw = pattern if pattern.endswith(" ") else pattern + " "
        # use same patterns as extract_item_name for consistency
        pass
    # Reuse the same keyword list as extract_item_name
    for pattern in ("купить ", "купи ", "buy ", "add ", "добавь ", "добавить "):
        if pattern in lowered:
            start = lowered.find(pattern) + len(pattern)
            raw = text[start:].strip()
            break
    if not raw:
        return []

    # Remove trailing context phrases
    for stop in (" в список", " в корзину", " in the list", " to the list"):
        idx = raw.lower().find(stop)
        if idx > 0:
            raw = raw[:idx].strip()

    # Split on comma and conjunctions
    parts = _re.split(r'\s*,\s*|\s+и\s+|\s+and\s+', raw)
    parts = [p.strip() for p in parts if p.strip()]

    items: List[Dict[str, Any]] = []
    for part in parts:
        item = _parse_item_part(part)
        if item:
            items.append(item)
    return items


def _parse_item_part(part: str) -> Optional[Dict[str, Any]]:
    """Parse a single item part, extracting optional quantity and unit."""
    # Pattern: "2 литра молока" or "3 liters milk"
    match = _re.match(r'^(\d+)\s+(\S+)\s+(.+)$', part)
    if match:
        return {
            "name": match.group(3).strip(),
            "quantity": match.group(1),
            "unit": match.group(2),
        }
    # Pattern: "3 яблока" (quantity without unit)
    match = _re.match(r'^(\d+)\s+(.+)$', part)
    if match:
        return {
            "name": match.group(2).strip(),
            "quantity": match.group(1),
        }
    # Just a name
    return {"name": part}
```

**IMPORTANT:** Place `import re as _re` at the top of the file (with the other imports, after line 8). Do NOT place it inside the function.

**IMPORTANT:** Do NOT modify `extract_item_name()`. It must remain exactly as-is.

---

## Step 2: Update `routers/v2.py` normalize()

### 2a: Add import

In the import block (line 7-14), add `extract_items` to the existing `graphs.core_graph` import:

Change:
```python
from graphs.core_graph import (
    build_clarify_decision,
    build_proposed_action,
    build_start_job_decision,
    detect_intent,
    _default_assignee_id,
    _default_list_id,
)
```

To:
```python
from graphs.core_graph import (
    build_clarify_decision,
    build_proposed_action,
    build_start_job_decision,
    detect_intent,
    extract_items,
    _default_assignee_id,
    _default_list_id,
)
```

### 2b: Add items to normalize()

In the `normalize()` method (lines 58-77), add `items` computation and include it in the return dict.

Replace the normalize method body with:

```python
    def normalize(self, command: Dict[str, Any]) -> Dict[str, Any]:
        text = command.get("text", "").strip()
        intent = detect_intent(text) if text else "clarify_needed"
        item_name = (
            extract_shopping_item_name(text, trace_id=command.get("trace_id")).item_name
            if intent == "add_shopping_item"
            else None
        )
        items = extract_items(text) if intent == "add_shopping_item" else []
        task_title = text if intent == "create_task" else None
        capabilities = set(command.get("capabilities", []))
        if intent == "add_shopping_item" and runner_enabled():
            trace_id = str(command.get("command_id", "unknown"))
            shadow_invoke(text=text, context=command.get("context", {}), trace_id=trace_id)
        return {
            "text": text,
            "intent": intent,
            "items": items,
            "item_name": item_name,
            "task_title": task_title,
            "capabilities": capabilities,
        }
```

**IMPORTANT:** `item_name` still comes from `extract_shopping_item_name()` (LLM extraction). It is NOT derived from `items`. This preserves backward compat with partial trust.

---

## Step 3: Update `agent_runner/schemas.py`

Change line 22 from:
```python
                        "quantity": {"type": ["number", "null"], "minimum": 0},
```
To:
```python
                        "quantity": {"type": ["string", "null"], "maxLength": 32},
```

This aligns with `contracts/schemas/decision.schema.json` where `quantity` is `string` (per ADR-006-P).

---

## Step 4: Update `agents/baseline_shopping.py`

Replace the entire file with:

```python
from __future__ import annotations

from typing import Any, Dict, List

from graphs.core_graph import extract_items, _default_list_id


def run(agent_input: Dict[str, Any], trace_id: str | None = None) -> Dict[str, Any]:
    text = agent_input.get("text", "")
    items: List[Dict[str, Any]] = extract_items(text) if isinstance(text, str) else []

    context = agent_input.get("context")
    list_id = None
    if isinstance(context, dict):
        list_id = _default_list_id({"context": context})

    payload: Dict[str, Any] = {"items": items, "confidence": 0.6 if items else 0.0}
    if list_id:
        payload["list_id"] = list_id
    return payload
```

**Note:** `items` is now `List[Dict[str, Any]]` (list of dicts with `name`/`quantity`/`unit`) instead of `List[str]` (list of strings).

---

## Step 5: Update `agents/baseline_clarify.py`

Replace the entire file with:

```python
from __future__ import annotations

from typing import Any, Dict, List

from graphs.core_graph import detect_intent, extract_items


def run(agent_input: Dict[str, Any], trace_id: str | None = None) -> Dict[str, Any]:
    text = agent_input.get("text", "")
    if not isinstance(text, str):
        text = ""

    intent = detect_intent(text) if text else "clarify_needed"
    missing_fields: List[str] = []
    question = "Нужны уточнения."

    if not text:
        question = "Опишите запрос подробнее."
        missing_fields = ["text"]
    elif intent == "add_shopping_item":
        if not extract_items(text):
            question = "Уточните, что добавить в список."
            missing_fields = ["item.name"]
    elif intent == "create_task":
        question = "Уточните детали задачи."
        missing_fields = ["task.title"]

    return {
        "question": question,
        "missing_fields": missing_fields,
        "confidence": 0.2,
    }
```

---

## Step 6: Update golden dataset

Replace `skills/graph-sanity/fixtures/golden_dataset.json` with EXACTLY this content:

```json
[
  {
    "command_id": "cmd-wp000-001",
    "fixture_file": "buy_milk.json",
    "expected_intent": "add_shopping_item",
    "expected_entity_keys": ["item"],
    "expected_item_count": 1,
    "notes": "Купи молоко — keyword 'куп'"
  },
  {
    "command_id": "cmd-wp000-002",
    "fixture_file": "buy_bread_and_eggs.json",
    "expected_intent": "add_shopping_item",
    "expected_entity_keys": ["item"],
    "expected_item_count": 2,
    "expected_item_names": ["хлеб", "яйца"],
    "notes": "Купить хлеб и яйца — keyword 'куп', multi-item conjunction"
  },
  {
    "command_id": "cmd-wp000-003",
    "fixture_file": "clean_bathroom.json",
    "expected_intent": "create_task",
    "expected_entity_keys": [],
    "notes": "Убраться в ванной — keyword 'убраться'"
  },
  {
    "command_id": "cmd-wp000-004",
    "fixture_file": "fix_faucet.json",
    "expected_intent": "create_task",
    "expected_entity_keys": [],
    "notes": "Починить кран на кухне — keyword 'починить'"
  },
  {
    "command_id": "cmd-wp000-005",
    "fixture_file": "empty_text.json",
    "expected_intent": "clarify_needed",
    "expected_entity_keys": [],
    "notes": "Whitespace-only text — no keywords"
  },
  {
    "command_id": "cmd-wp000-006",
    "fixture_file": "unknown_intent.json",
    "expected_intent": "clarify_needed",
    "expected_entity_keys": [],
    "notes": "Что-то непонятное про погоду — no keywords match"
  },
  {
    "command_id": "cmd-wp000-007",
    "fixture_file": "minimal_context.json",
    "expected_intent": "create_task",
    "expected_entity_keys": [],
    "notes": "Сделай что-нибудь полезное — keyword 'сделай'"
  },
  {
    "command_id": "cmd-wp000-008",
    "fixture_file": "shopping_no_list.json",
    "expected_intent": "add_shopping_item",
    "expected_entity_keys": ["item"],
    "expected_item_count": 1,
    "notes": "Купи бананы — keyword 'куп', no shopping list in context"
  },
  {
    "command_id": "cmd-wp000-009",
    "fixture_file": "task_no_zones.json",
    "expected_intent": "create_task",
    "expected_entity_keys": [],
    "notes": "Нужно помыть окна — keyword 'нужно'"
  },
  {
    "command_id": "cmd-wp000-010",
    "fixture_file": "buy_apples_en.json",
    "expected_intent": "add_shopping_item",
    "expected_entity_keys": ["item"],
    "expected_item_count": 2,
    "expected_item_names": ["apples", "oranges"],
    "notes": "Buy apples and oranges — keyword 'buy', multi-item conjunction (English)"
  },
  {
    "command_id": "cmd-wp000-011",
    "fixture_file": "multiple_tasks.json",
    "expected_intent": "add_shopping_item",
    "expected_entity_keys": ["item"],
    "expected_item_count": 1,
    "notes": "Купи молоко и убери кухню — keyword 'куп' wins, multi-intent not split"
  },
  {
    "command_id": "cmd-wp000-012",
    "fixture_file": "add_sugar_ru.json",
    "expected_intent": "add_shopping_item",
    "expected_entity_keys": ["item"],
    "expected_item_count": 1,
    "notes": "Добавь сахар в список покупок — 'куп' substring in 'покупок', trailing context removed"
  },
  {
    "command_id": "cmd-graph-002",
    "fixture_file": "grocery_run.json",
    "expected_intent": "add_shopping_item",
    "expected_entity_keys": ["item"],
    "expected_item_count": 2,
    "expected_item_names": ["яблоки", "молоко"],
    "notes": "Купи яблоки и молоко — keyword 'куп', multi-item conjunction"
  },
  {
    "command_id": "cmd-graph-001",
    "fixture_file": "weekly_chores.json",
    "expected_intent": "create_task",
    "expected_entity_keys": [],
    "notes": "Нужно убрать кухню и составить план — keyword 'нужно'"
  }
]
```

---

## Step 7: Update `tests/test_agent_baseline_v0.py` (if needed)

Read `tests/test_agent_baseline_v0.py`. If `test_runner_baseline_agents` asserts that the shopping agent's `items` list contains strings (e.g., `assert result["items"] == ["молоко"]`), update the assertion to match the new dict format:

```python
# Old: assert result["items"] == ["молоко"]  (or similar string check)
# New: assert result["items"][0]["name"] == "молоко"  (or similar dict check)
```

Also check that `test_agent_run_log_privacy` still works with dict items. The summarizer should recursively strip string values from dicts, so "молоко" should still not appear.

If NO assertions reference the items type (only checking key existence), then NO changes are needed.

---

## Step 8: Create `tests/test_multi_item_extraction.py`

Create `tests/test_multi_item_extraction.py` with EXACTLY this content:

```python
"""Tests for multi-item extraction (ST-009)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import patch

import pytest

# ---- helpers ----------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from graphs.core_graph import extract_item_name, extract_items  # noqa: E402


# ---- extract_items: single item ---------------------------------------------


def test_single_item_russian():
    result = extract_items("Купи молоко")
    assert len(result) == 1
    assert result[0]["name"] == "молоко"


def test_single_item_english():
    result = extract_items("Buy milk")
    assert len(result) == 1
    assert result[0]["name"] == "milk"


# ---- extract_items: multi-item ----------------------------------------------


def test_multi_item_comma_russian():
    result = extract_items("Купи молоко, хлеб, бананы")
    assert len(result) == 3
    names = [item["name"] for item in result]
    assert names == ["молоко", "хлеб", "бананы"]


def test_multi_item_conjunction_russian():
    result = extract_items("Купи хлеб и яйца")
    assert len(result) == 2
    names = [item["name"] for item in result]
    assert names == ["хлеб", "яйца"]


def test_multi_item_conjunction_english():
    result = extract_items("Buy apples and oranges")
    assert len(result) == 2
    names = [item["name"] for item in result]
    assert names == ["apples", "oranges"]


def test_multi_item_comma_and_conjunction():
    result = extract_items("Купи молоко, хлеб и бананы")
    assert len(result) == 3
    names = [item["name"] for item in result]
    assert names == ["молоко", "хлеб", "бананы"]


# ---- extract_items: quantity/unit -------------------------------------------


def test_quantity_and_unit_russian():
    result = extract_items("Купи 2 литра молока")
    assert len(result) == 1
    assert result[0]["name"] == "молока"
    assert result[0]["quantity"] == "2"
    assert result[0]["unit"] == "литра"


def test_quantity_no_unit():
    result = extract_items("Купи 3 яблока")
    assert len(result) == 1
    assert result[0]["name"] == "яблока"
    assert result[0]["quantity"] == "3"
    assert "unit" not in result[0]


# ---- extract_items: edge cases ----------------------------------------------


def test_empty_text():
    assert extract_items("") == []


def test_no_shopping_keyword():
    assert extract_items("Погода сегодня хорошая") == []


def test_trailing_context_removed():
    result = extract_items("Добавь сахар в список покупок")
    assert len(result) == 1
    assert result[0]["name"] == "сахар"


# ---- backward compat: extract_item_name unchanged ---------------------------


def test_backward_compat_extract_item_name_single():
    """extract_item_name still returns the full string (not split)."""
    result = extract_item_name("Купи молоко")
    assert result == "молоко"


def test_backward_compat_extract_item_name_multi():
    """extract_item_name returns FULL string after keyword (not split)."""
    result = extract_item_name("Купи хлеб и яйца")
    assert result == "хлеб и яйца"


# ---- agent_runner schema: quantity is string --------------------------------


def test_agent_runner_schema_quantity_type():
    from agent_runner.schemas import shopping_extraction_schema

    schema = shopping_extraction_schema()
    item_props = schema["properties"]["items"]["items"]["properties"]
    qty_type = item_props["quantity"]["type"]
    assert "string" in qty_type, f"quantity type should be string, got {qty_type}"
    assert "number" not in qty_type, f"quantity should not be number"


# ---- V2 normalize: items in normalized dict ---------------------------------


def test_normalize_has_items():
    """V2 normalize() returns 'items' in normalized dict."""
    from routers.v2 import RouterV2Pipeline

    pipeline = RouterV2Pipeline()
    command = {
        "text": "Купи хлеб и молоко",
        "capabilities": ["start_job", "propose_add_shopping_item"],
        "context": {"household": {"shopping_lists": []}},
    }
    with patch("routers.v2.extract_shopping_item_name") as mock_llm:
        mock_llm.return_value = type("R", (), {"item_name": "хлеб и молоко"})()
        with patch("routers.v2.runner_enabled", return_value=False):
            normalized = pipeline.normalize(command)

    assert "items" in normalized
    assert isinstance(normalized["items"], list)
    assert len(normalized["items"]) == 2
    names = [item["name"] for item in normalized["items"]]
    assert names == ["хлеб", "молоко"]


def test_normalize_item_name_backward_compat():
    """V2 normalize() still has 'item_name' from LLM extraction."""
    from routers.v2 import RouterV2Pipeline

    pipeline = RouterV2Pipeline()
    command = {
        "text": "Купи молоко",
        "capabilities": ["start_job"],
        "context": {"household": {"shopping_lists": []}},
    }
    with patch("routers.v2.extract_shopping_item_name") as mock_llm:
        mock_llm.return_value = type("R", (), {"item_name": "молоко"})()
        with patch("routers.v2.runner_enabled", return_value=False):
            normalized = pipeline.normalize(command)

    assert normalized["item_name"] == "молоко"
    assert len(normalized["items"]) == 1


# ---- baseline shopping agent: multi-item ------------------------------------


def test_baseline_shopping_multi_item():
    from agents.baseline_shopping import run

    result = run({"text": "Купи молоко и хлеб"})
    items = result["items"]
    assert len(items) == 2
    assert items[0]["name"] == "молоко"
    assert items[1]["name"] == "хлеб"


def test_baseline_shopping_empty():
    from agents.baseline_shopping import run

    result = run({"text": "Погода"})
    assert result["items"] == []
    assert result["confidence"] == 0.0
```

---

## Verification

After creating/modifying all files, run:

```bash
# 1. New function exists
grep -n "def extract_items" graphs/core_graph.py

# 2. Normalized dict has items
grep -n '"items"' routers/v2.py

# 3. Agent runner quantity is string
grep -n "quantity" agent_runner/schemas.py

# 4. Baseline shopping uses extract_items
grep -n "extract_items" agents/baseline_shopping.py

# 5. Golden dataset has expected_item_count
grep -c "expected_item_count" skills/graph-sanity/fixtures/golden_dataset.json

# 6. New tests exist
test -f tests/test_multi_item_extraction.py && echo "OK" || echo "MISSING"

# 7. No secrets
grep -ri "api.key\|secret\|password\|token" tests/test_multi_item_extraction.py || echo "NO SECRETS"
```
