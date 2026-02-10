# Codex APPLY Prompt — ST-025: Expand Golden Dataset to 20+ Commands

## Role
You are a senior Python developer expanding the golden dataset for quality evaluation.

## Context (from PLAN findings + clarification)

- `golden_dataset.json` has 14 entries. Intent distribution: 7 add_shopping_item, 5 create_task, 2 clarify_needed.
- `command.schema.json` has `additionalProperties: false` — this applies ONLY to command fixture files, NOT to golden_dataset.json.
- **golden_dataset.json has NO schema validation** — new fields (`expected_action`, `difficulty`) can be safely added.
- New command fixture files (`fixtures/commands/*.json`) MUST follow the existing schema exactly: `command_id`, `user_id`, `timestamp`, `text`, `capabilities`, `context`. No extra fields.
- 2 fixture files exist without golden_dataset entries:
  - `clarify_partial_shopping.json` → command_id: `cmd-wp000-015`
  - `clarify_ambiguous_intent.json` → command_id: `cmd-wp000-016`
- `load_golden_dataset()` in `scripts/analyze_shadow_router.py:49-59` reads only `command_id`, `expected_intent`, `expected_entity_keys`. New fields are safely ignored.
- `run_graph_suite.py` globs `fixtures/commands/*.json` — new fixture files are automatically picked up and must produce valid decisions.
- `tests/test_analyze_shadow_router.py:261` asserts `len(data) == 14` — MUST be updated.

## Files to Modify

### 1. `skills/graph-sanity/fixtures/golden_dataset.json` (UPDATE)

Expand from 14 to 22 entries. Changes:

**A) Add new fields to ALL 14 existing entries:**

For each existing entry, add two new fields:
- `"expected_action"`: derived from intent:
  - `add_shopping_item` → `"propose_add_shopping_item"`
  - `create_task` → `"propose_create_task"`
  - `clarify_needed` → `"clarify"`
- `"difficulty"`: use these values:
  - `"easy"` for: cmd-wp000-001, 003, 004, 005, 008, 009, cmd-graph-001
  - `"medium"` for: cmd-wp000-002, 007, 010, 011, 012, cmd-graph-002
  - `"hard"` for: cmd-wp000-006

**B) Add 8 new entries at the end of the array:**

```json
{
  "command_id": "cmd-wp000-015",
  "fixture_file": "clarify_partial_shopping.json",
  "expected_intent": "clarify_needed",
  "expected_entity_keys": [],
  "expected_action": "clarify",
  "difficulty": "medium",
  "notes": "Добавь... что-то — incomplete shopping request, existing fixture"
},
{
  "command_id": "cmd-wp000-016",
  "fixture_file": "clarify_ambiguous_intent.json",
  "expected_intent": "clarify_needed",
  "expected_entity_keys": [],
  "expected_action": "clarify",
  "difficulty": "hard",
  "notes": "Ambiguous intent — could be shopping or task, existing fixture"
},
{
  "command_id": "cmd-gd-017",
  "fixture_file": "buy_three_items_quantities.json",
  "expected_intent": "add_shopping_item",
  "expected_entity_keys": ["item"],
  "expected_item_count": 3,
  "expected_item_names": ["молоко", "хлеб", "масло"],
  "expected_action": "propose_add_shopping_item",
  "difficulty": "medium",
  "notes": "Купи 2 литра молока, хлеб и масло — multi-item with quantity"
},
{
  "command_id": "cmd-gd-018",
  "fixture_file": "typo_shopping.json",
  "expected_intent": "add_shopping_item",
  "expected_entity_keys": ["item"],
  "expected_item_count": 1,
  "expected_action": "propose_add_shopping_item",
  "difficulty": "hard",
  "notes": "Купии малако — typo in keyword and item name"
},
{
  "command_id": "cmd-gd-019",
  "fixture_file": "mixed_lang_task.json",
  "expected_intent": "create_task",
  "expected_entity_keys": [],
  "expected_action": "propose_create_task",
  "difficulty": "hard",
  "notes": "Clean the кухня please — mixed Russian/English"
},
{
  "command_id": "cmd-gd-020",
  "fixture_file": "single_word_clarify.json",
  "expected_intent": "clarify_needed",
  "expected_entity_keys": [],
  "expected_action": "clarify",
  "difficulty": "easy",
  "notes": "Да — single word, no intent keywords"
},
{
  "command_id": "cmd-gd-021",
  "fixture_file": "long_shopping_list.json",
  "expected_intent": "add_shopping_item",
  "expected_entity_keys": ["item"],
  "expected_item_count": 5,
  "expected_item_names": ["молоко", "хлеб", "масло", "сыр", "яйца"],
  "expected_action": "propose_add_shopping_item",
  "difficulty": "medium",
  "notes": "Купи молоко, хлеб, масло, сыр и яйца — 5 items"
},
{
  "command_id": "cmd-gd-022",
  "fixture_file": "polite_task.json",
  "expected_intent": "create_task",
  "expected_entity_keys": [],
  "expected_action": "propose_create_task",
  "difficulty": "easy",
  "notes": "Пожалуйста, помоги убрать комнату — polite form with 'убрать'"
}
```

Total after expansion: 22 entries.
Distribution: add_shopping_item 10, create_task 7, clarify_needed 5.

### 2. New fixture command files (6 files in `skills/graph-sanity/fixtures/commands/`)

**IMPORTANT:** These files MUST have ONLY the standard command fields. NO extra fields.
Follow the exact pattern of existing fixtures like `buy_milk.json`.

Create these 6 files (the 2 clarify fixtures already exist):

**`buy_three_items_quantities.json`:**
```json
{
  "command_id": "cmd-gd-017",
  "user_id": "user-217",
  "timestamp": "2026-02-10T10:00:00+00:00",
  "text": "Купи 2 литра молока, хлеб и масло",
  "capabilities": ["start_job", "propose_create_task", "propose_add_shopping_item", "clarify"],
  "context": {
    "household": {
      "household_id": "house-217",
      "members": [{"user_id": "user-217", "display_name": "Анна"}],
      "shopping_lists": [{"list_id": "list-1", "name": "Продукты"}]
    },
    "defaults": {"default_list_id": "list-1"}
  }
}
```

**`typo_shopping.json`:**
```json
{
  "command_id": "cmd-gd-018",
  "user_id": "user-218",
  "timestamp": "2026-02-10T10:01:00+00:00",
  "text": "Купии малако",
  "capabilities": ["start_job", "propose_create_task", "propose_add_shopping_item", "clarify"],
  "context": {
    "household": {
      "household_id": "house-218",
      "members": [{"user_id": "user-218", "display_name": "Петя"}],
      "shopping_lists": [{"list_id": "list-1", "name": "Продукты"}]
    },
    "defaults": {"default_list_id": "list-1"}
  }
}
```

**`mixed_lang_task.json`:**
```json
{
  "command_id": "cmd-gd-019",
  "user_id": "user-219",
  "timestamp": "2026-02-10T10:02:00+00:00",
  "text": "Clean the кухня please",
  "capabilities": ["start_job", "propose_create_task", "propose_add_shopping_item", "clarify"],
  "context": {
    "household": {
      "household_id": "house-219",
      "members": [{"user_id": "user-219", "display_name": "Mike"}]
    }
  }
}
```

**`single_word_clarify.json`:**
```json
{
  "command_id": "cmd-gd-020",
  "user_id": "user-220",
  "timestamp": "2026-02-10T10:03:00+00:00",
  "text": "Да",
  "capabilities": ["start_job", "propose_create_task", "propose_add_shopping_item", "clarify"],
  "context": {
    "household": {
      "household_id": "house-220",
      "members": [{"user_id": "user-220", "display_name": "Коля"}]
    }
  }
}
```

**`long_shopping_list.json`:**
```json
{
  "command_id": "cmd-gd-021",
  "user_id": "user-221",
  "timestamp": "2026-02-10T10:04:00+00:00",
  "text": "Купи молоко, хлеб, масло, сыр и яйца",
  "capabilities": ["start_job", "propose_create_task", "propose_add_shopping_item", "clarify"],
  "context": {
    "household": {
      "household_id": "house-221",
      "members": [{"user_id": "user-221", "display_name": "Лена"}],
      "shopping_lists": [{"list_id": "list-1", "name": "Продукты"}]
    },
    "defaults": {"default_list_id": "list-1"}
  }
}
```

**`polite_task.json`:**
```json
{
  "command_id": "cmd-gd-022",
  "user_id": "user-222",
  "timestamp": "2026-02-10T10:05:00+00:00",
  "text": "Пожалуйста, помоги убрать комнату",
  "capabilities": ["start_job", "propose_create_task", "propose_add_shopping_item", "clarify"],
  "context": {
    "household": {
      "household_id": "house-222",
      "members": [{"user_id": "user-222", "display_name": "Маша"}]
    }
  }
}
```

### 3. `tests/test_analyze_shadow_router.py` (UPDATE)

Change line 261 (inside `test_golden_dataset_manifest_schema`):

```python
# FROM:
assert len(data) == 14, f"Expected 14 entries, got {len(data)}"
# TO:
assert len(data) >= 20, f"Expected >= 20 entries, got {len(data)}"
```

### 4. `tests/test_golden_dataset_validation.py` (NEW)

```python
"""Validation tests for the expanded golden dataset."""

import json
import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

GOLDEN_PATH = BASE_DIR / "skills" / "graph-sanity" / "fixtures" / "golden_dataset.json"


def _load_golden():
    return json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))


def test_golden_dataset_has_20_plus_entries() -> None:
    """AC-1: Dataset has 20+ entries."""
    data = _load_golden()
    assert len(data) >= 20, f"Expected >= 20 entries, got {len(data)}"


def test_golden_dataset_all_intents_represented() -> None:
    """AC-2: Each intent has >= 3 entries."""
    data = _load_golden()
    by_intent: dict[str, list] = {}
    for entry in data:
        by_intent.setdefault(entry["expected_intent"], []).append(entry)
    for intent in ["add_shopping_item", "create_task", "clarify_needed"]:
        count = len(by_intent.get(intent, []))
        assert count >= 3, f"Intent '{intent}' has only {count} entries, expected >= 3"


def test_golden_dataset_has_hard_cases() -> None:
    """AC-3: At least 3 entries with difficulty='hard'."""
    data = _load_golden()
    hard = [e for e in data if e.get("difficulty") == "hard"]
    assert len(hard) >= 3, f"Only {len(hard)} hard entries, expected >= 3"
```

## Files NOT Modified (invariants)
- `contracts/schemas/command.schema.json` — DO NOT CHANGE
- `contracts/schemas/decision.schema.json` — DO NOT CHANGE
- `scripts/analyze_shadow_router.py` — DO NOT CHANGE
- `skills/graph-sanity/scripts/run_graph_suite.py` — DO NOT CHANGE
- `skills/graph-sanity/fixtures/commands/clarify_partial_shopping.json` — already exists, DO NOT CHANGE
- `skills/graph-sanity/fixtures/commands/clarify_ambiguous_intent.json` — already exists, DO NOT CHANGE
- All existing fixture command files — DO NOT CHANGE

## Verification Commands

```bash
# New validation tests
source .venv/bin/activate && python3 -m pytest tests/test_golden_dataset_validation.py -v

# Shadow analyzer tests (must pass with updated count)
source .venv/bin/activate && python3 -m pytest tests/test_analyze_shadow_router.py -v

# Graph-sanity suite (new fixtures must process cleanly)
source .venv/bin/activate && python3 skills/graph-sanity/scripts/run_graph_suite.py > /dev/null && echo "OK"

# Full test suite
source .venv/bin/activate && python3 -m pytest --tb=short -q

# Quick count check
python3 -c "import json; d=json.loads(open('skills/graph-sanity/fixtures/golden_dataset.json').read()); print(f'Entries: {len(d)}')"
```

## STOP-THE-LINE
If any of the following occur, STOP and report:
- Existing tests fail after your changes
- New fixture files fail command schema validation
- graph-sanity suite crashes on new fixtures
- Any file listed as "DO NOT CHANGE" needs modification
