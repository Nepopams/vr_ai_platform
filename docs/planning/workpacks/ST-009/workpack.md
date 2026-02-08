# Workpack — ST-009: Baseline Multi-Item Extraction and Golden Dataset Expansion

**Status:** Ready
**Story:** `docs/planning/epics/EP-004/stories/ST-009-baseline-multi-item-extraction.md`
**Epic:** `docs/planning/epics/EP-004/epic.md`
**Initiative:** `docs/planning/initiatives/INIT-2026Q2-multi-entity-extraction.md`

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q2-multi-entity-extraction.md` |
| ADR-006-P | `docs/adr/ADR-006-multi-item-internal-model.md` |
| Contract schema (decision) | `contracts/schemas/decision.schema.json` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

Baseline extraction splits multi-item shopping commands into individual items with optional
quantity/unit. The normalized dict carries `items: List[dict]` alongside backward-compatible
`item_name`. Golden dataset expanded with multi-item expectations. Agent runner schema quantity
aligned to `string` per ADR-006-P.

---

## Files to Change

### Modified files (EDIT)

| File | What changes |
|------|-------------|
| `graphs/core_graph.py` | Add `extract_items()` function (lines after 68). Keep `extract_item_name()` unchanged. |
| `routers/v2.py` | Update `normalize()` (lines 58-77) to call `extract_items()` and add `items` to normalized dict. Keep `item_name` from LLM extraction. |
| `agent_runner/schemas.py` | Change `quantity` type from `["number", "null"]` to `["string", "null"]` (line 22) |
| `agents/baseline_shopping.py` | Use `extract_items()` instead of `extract_item_name()`, return structured items list |
| `agents/baseline_clarify.py` | Use `extract_items()` for item presence check (line 21) |
| `skills/graph-sanity/fixtures/golden_dataset.json` | Update multi-item entries (cmd-wp000-002, cmd-wp000-010, cmd-graph-002) with `expected_item_count` and `expected_item_names` |

### New files (CREATE)

| File | Description |
|------|-------------|
| `tests/test_multi_item_extraction.py` | Unit tests for `extract_items()`, normalized dict, backward compat, schema alignment |

### Key files to READ (context, not modify)

| File | Why |
|------|-----|
| `llm_policy/tasks.py` | Current LLM extraction schema (unchanged in ST-009, changes in ST-010) |
| `routers/assist/runner.py` | Assist mode (unchanged in ST-009, changes in ST-010) |
| `contracts/schemas/decision.schema.json` | Contract schema reference (no changes needed) |
| `docs/adr/ADR-006-multi-item-internal-model.md` | Model decisions: items shape, quantity=string, backward compat |
| `tests/test_agent_baseline_v0.py` | Existing baseline agent tests (must still pass) |

---

## Implementation Plan

### Step 1: Add `extract_items()` to `graphs/core_graph.py`

Add after `extract_item_name()` (after line 68):

```python
def extract_items(text: str) -> List[Dict[str, Any]]:
    """Split shopping text into individual items with optional quantity/unit."""
    lowered = text.lower()
    patterns = ("купить ", "купи ", "buy ", "add ", "добавь ", "добавить ")
    raw = None
    for pattern in patterns:
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
    import re
    parts = re.split(r'\s*,\s*|\s+и\s+|\s+and\s+', raw)
    parts = [p.strip() for p in parts if p.strip()]

    items: List[Dict[str, Any]] = []
    for part in parts:
        item = _parse_item_part(part)
        if item:
            items.append(item)
    return items


def _parse_item_part(part: str) -> Optional[Dict[str, Any]]:
    """Parse a single item part, extracting optional quantity and unit."""
    import re
    # Pattern: "2 литра молока" or "3 eggs"
    match = re.match(r'^(\d+)\s+(\S+)\s+(.+)$', part)
    if match:
        return {
            "name": match.group(3).strip(),
            "quantity": match.group(1),
            "unit": match.group(2),
        }
    # Pattern: "3 яблока" (quantity without unit)
    match = re.match(r'^(\d+)\s+(.+)$', part)
    if match:
        return {
            "name": match.group(2).strip(),
            "quantity": match.group(1),
        }
    # Just a name
    return {"name": part}
```

### Step 2: Update `routers/v2.py` normalize()

In `normalize()` (lines 58-77), add import of `extract_items` and populate `items` in returned dict:

- Import: `from graphs.core_graph import extract_items` (add to existing import block, line 7-14)
- After computing `item_name`, also compute `items`:
  ```python
  items = extract_items(text) if intent == "add_shopping_item" else []
  ```
- Add `"items": items` to the returned dict (line 71-77)
- Keep `item_name` from LLM extraction unchanged (backward compat with partial trust)

### Step 3: Update `agent_runner/schemas.py`

Change line 22:
```python
"quantity": {"type": ["number", "null"], "minimum": 0},
```
to:
```python
"quantity": {"type": ["string", "null"], "maxLength": 32},
```

### Step 4: Update `agents/baseline_shopping.py`

- Import `extract_items` instead of `extract_item_name`
- Use `extract_items(text)` to get items list
- Return structured items (list of dicts with name/quantity/unit) instead of list of strings
- Keep `_default_list_id` import and usage

### Step 5: Update `agents/baseline_clarify.py`

- Import `extract_items` instead of `extract_item_name`
- Change line 21: `if not extract_item_name(text):` -> `if not extract_items(text):`

### Step 6: Update golden dataset

Update `skills/graph-sanity/fixtures/golden_dataset.json`:
- For `cmd-wp000-002` (buy_bread_and_eggs): add `"expected_item_count": 2, "expected_item_names": ["хлеб", "яйца"]`
- For `cmd-wp000-010` (buy_apples_en): add `"expected_item_count": 2, "expected_item_names": ["apples", "oranges"]`
- For `cmd-graph-002` (grocery_run): add `"expected_item_count": 2, "expected_item_names": ["яблоки", "молоко"]`
- Single-item entries (buy_milk, shopping_no_list, add_sugar_ru): add `"expected_item_count": 1`

### Step 7: Create tests

Create `tests/test_multi_item_extraction.py` with tests covering:

1. `test_single_item_russian` -- "Купи молоко" -> [{"name": "молоко"}]
2. `test_multi_item_comma_russian` -- "Купи молоко, хлеб, бананы" -> 3 items
3. `test_multi_item_conjunction_russian` -- "Купи хлеб и яйца" -> 2 items
4. `test_multi_item_comma_and_conjunction` -- "Купи молоко, хлеб и бананы" -> 3 items
5. `test_multi_item_english` -- "Buy apples and oranges" -> 2 items
6. `test_quantity_unit_russian` -- "Купи 2 литра молока" -> qty="2", unit="литра"
7. `test_quantity_no_unit` -- "Купи 3 яблока" -> qty="3", no unit
8. `test_empty_text` -- "" -> []
9. `test_no_shopping_keyword` -- "Погода сегодня" -> []
10. `test_backward_compat_extract_item_name` -- `extract_item_name()` still returns full string
11. `test_agent_runner_schema_quantity_type` -- verify quantity is string type
12. `test_normalize_has_items` -- V2 normalize returns `items` in dict
13. `test_normalize_item_name_backward_compat` -- `item_name` still present
14. `test_baseline_shopping_multi_item` -- baseline agent returns multiple items

---

## Verification Commands

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

# 7. Full test suite
python3 -m pytest tests/ -v

# 8. No secrets
grep -ri "api.key\|secret\|password\|token" tests/test_multi_item_extraction.py || echo "NO SECRETS"
```

---

## DoD Checklist

- [ ] `extract_items()` function exists in `graphs/core_graph.py`
- [ ] `extract_item_name()` unchanged (backward compat)
- [ ] `normalized["items"]` populated in V2 normalize
- [ ] `normalized["item_name"]` still present (backward compat)
- [ ] `agent_runner/schemas.py` quantity type is `string`
- [ ] `agents/baseline_shopping.py` uses `extract_items()`
- [ ] `agents/baseline_clarify.py` uses `extract_items()`
- [ ] Golden dataset entries have `expected_item_count` and `expected_item_names`
- [ ] Unit tests cover single-item, multi-item, quantity/unit, empty, backward compat
- [ ] All existing tests still pass (131 baseline)
- [ ] No existing files broken (V1 pipeline, partial trust, shadow router)

---

## Risks

| Risk | Mitigation |
|------|-----------|
| Splitting on "и"/"and" may break compound product names like "хлеб и масло" | Conservative splitting: only split when surrounded by spaces. Golden dataset must include this edge case. |
| `extract_item_name()` callers get different results | `extract_item_name()` is NOT changed -- returns full string as before. Only `extract_items()` splits. |
| Partial trust breaks | `item_name` kept unchanged in normalized dict. Partial trust reads `item_name`. |

---

## Rollback

Revert changes to 6 modified files. Delete `tests/test_multi_item_extraction.py`.
