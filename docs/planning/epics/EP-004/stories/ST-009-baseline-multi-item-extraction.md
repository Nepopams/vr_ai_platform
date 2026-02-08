# ST-009: Baseline Multi-Item Extraction and Golden Dataset Expansion

**Status:** NOT READY
**Epic:** `docs/planning/epics/EP-004/epic.md`
**Owner:** TBD

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-004/epic.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q2-multi-entity-extraction.md` |
| ADR-006 (multi-item model) | `docs/adr/ADR-006-multi-item-internal-model.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Description

As a platform developer, I need the baseline extraction pipeline to split multi-item shopping
commands into individual items with optional quantity and unit, so that downstream components
(planner, assist, partial trust) can operate on each item independently.

This story covers three tightly coupled changes:
1. A new `extract_items()` function in `graphs/core_graph.py` that returns a list of item dicts
2. Changes to the `normalized` dict to carry `items: List[dict]` alongside backward-compatible `item_name`
3. Expanded golden dataset with multi-item expectations

### Current code touchpoints

| File | Current behavior | Required change |
|------|-----------------|-----------------|
| `graphs/core_graph.py:60-68` | `extract_item_name()` returns single `Optional[str]` | Add `extract_items()` returning `List[dict]`; keep `extract_item_name()` for backward compat |
| `routers/v2.py:58-77` | `normalize()` sets `item_name` from single extraction | Add `items` to normalized dict; keep `item_name` as first item for backward compat |
| `agent_runner/schemas.py` | `quantity: number` | Align to `string` per ADR-006 |
| `agents/baseline_shopping.py` | Uses `extract_item_name()`, returns single item | Update to use `extract_items()`, return all items |
| `agents/baseline_clarify.py` | Uses `extract_item_name()` for presence check | Update to check `extract_items()` result |
| `skills/graph-sanity/fixtures/golden_dataset.json` | Multi-item entries expect singular entity keys | Update to expect multiple items |

## Acceptance Criteria

```gherkin
AC-1: Baseline extraction splits comma-separated items
  Given text "Купи молоко, хлеб и бананы"
  When extract_items(text) is called
  Then it returns [{"name": "молоко"}, {"name": "хлеб"}, {"name": "бананы"}]

AC-2: Baseline extraction splits conjunction-separated items (Russian)
  Given text "Купи хлеб и яйца"
  When extract_items(text) is called
  Then it returns [{"name": "хлеб"}, {"name": "яйца"}]

AC-3: Baseline extraction splits conjunction-separated items (English)
  Given text "Buy apples and oranges"
  When extract_items(text) is called
  Then it returns [{"name": "apples"}, {"name": "oranges"}]

AC-4: Baseline extraction handles quantity and unit
  Given text "Купи 2 литра молока"
  When extract_items(text) is called
  Then it returns [{"name": "молока", "quantity": "2", "unit": "литра"}]

AC-5: Single item still works (backward compat)
  Given text "Купи молоко"
  When extract_items(text) is called
  Then it returns [{"name": "молоко"}]
  And extract_item_name(text) still returns "молоко"

AC-6: Normalized dict carries items list
  Given a command with text "Купи хлеб и молоко"
  When RouterV2Pipeline.normalize() is called
  Then normalized["items"] == [{"name": "хлеб"}, {"name": "молоко"}]
  And normalized["item_name"] == "хлеб" (first item, backward compat)

AC-7: Golden dataset has multi-item expectations
  Given golden_dataset.json
  When the test runner processes multi-item entries
  Then they expect multiple items with correct names

AC-8: Agent runner schema quantity aligned to string
  Given agent_runner/schemas.py shopping_extraction_schema()
  When a reviewer inspects the quantity field type
  Then it is "string" or ["string", "null"] (not "number")

AC-9: Baseline agents use multi-item extraction
  Given agents/baseline_shopping.py
  When processing text "Купи молоко и хлеб"
  Then the output items list contains both "молоко" and "хлеб"
```

## Scope

### In scope

- New `extract_items(text: str) -> List[dict]` function in `graphs/core_graph.py`
  - Splitting on comma, " и ", " and "
  - Basic quantity/unit parsing
  - Returns list of `{name: str, quantity: str|None, unit: str|None}`
- Keep existing `extract_item_name()` for backward compat
- Update `RouterV2Pipeline.normalize()` to populate `items` in normalized dict
- Keep `item_name` in normalized dict as first item for backward compat
- Update `agent_runner/schemas.py` quantity type: `number` -> `string`
- Update `agents/baseline_shopping.py` to use `extract_items()`
- Update `agents/baseline_clarify.py` to check `extract_items()` result
- Expand golden dataset with multi-item expectations
- Unit tests for all new/changed extraction logic

### Out of scope

- LLM extraction schema changes (ST-010)
- Assist mode entity hints changes (ST-010)
- V2 planner multi-action generation (ST-011)
- Attribute hints parsing (e.g., "обезжиренное молоко")
- Complex quantity patterns (e.g., "пару", "немного")
- Multi-intent commands (e.g., "купи молоко и убери кухню")

## Test Strategy

### Unit tests (new file `tests/test_multi_item_extraction.py`)

- `test_single_item_russian` -- "Купи молоко" -> [{"name": "молоко"}]
- `test_multi_item_comma_russian` -- "Купи молоко, хлеб, бананы" -> 3 items
- `test_multi_item_conjunction_russian` -- "Купи хлеб и яйца" -> 2 items
- `test_multi_item_comma_and_conjunction` -- "Купи молоко, хлеб и бананы" -> 3 items
- `test_multi_item_english` -- "Buy apples and oranges" -> 2 items
- `test_quantity_unit_russian` -- "Купи 2 литра молока" -> qty/unit parsed
- `test_quantity_no_unit` -- "Купи 3 яблока" -> qty parsed, no unit
- `test_empty_text` -- "" -> []
- `test_no_shopping_keyword` -- "Погода сегодня" -> []
- `test_backward_compat_extract_item_name` -- still returns single string
- `test_agent_runner_schema_quantity_type` -- verify quantity is string type

### Integration tests

- `test_normalize_multi_item_populates_items` -- normalized dict has items list
- `test_normalize_single_item_backward_compat` -- item_name still set
- `test_baseline_shopping_agent_multi_item` -- baseline_shopping returns multiple items

## Flags

- contract_impact: no
- adr_needed: none (ADR-006 covers this)
- diagrams_needed: none
- security_sensitive: no
- traceability_critical: no

## Blocked By

- **ST-008** (ADR-006): Must be accepted before implementation begins.
