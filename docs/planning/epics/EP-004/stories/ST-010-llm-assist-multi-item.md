# ST-010: LLM Extraction and Assist Mode Multi-Item Support

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

As a platform developer, I need the LLM-assisted extraction and assist mode entity hints to
support multiple items, so that LLM suggestions can enrich multi-item shopping commands
and assist mode does not discard items beyond the first.

This story covers two tightly coupled LLM-path changes:
1. Update `SHOPPING_EXTRACTION_SCHEMA` in `llm_policy/tasks.py` to return a list of items
2. Update `_apply_entity_hints` in `routers/assist/runner.py` to use all items, not just the first

### Current code touchpoints

| File | Current behavior | Required change |
|------|-----------------|-----------------|
| `llm_policy/tasks.py:12-19` | `SHOPPING_EXTRACTION_SCHEMA = {item_name: string}` | Change to `{items: array of {name, quantity, unit}}` |
| `llm_policy/tasks.py:23-26` | `ExtractionResult` has `item_name: str \| None` | Change to `items: List[dict]`; keep `item_name` as computed property |
| `routers/assist/runner.py:64-73` | `_ENTITY_SCHEMA` returns `items: array of string` | Update to `items: array of {name, quantity, unit}` objects |
| `routers/assist/runner.py:405-481` | `_apply_entity_hints()` picks first matching item | Iterate all items, populate `normalized["items"]` |
| `routers/assist/runner.py:584-590` | `_pick_matching_item()` returns first match | Add `_pick_matching_items()` returning all matches |

## Acceptance Criteria

```gherkin
AC-1: LLM extraction schema supports multi-item
  Given SHOPPING_EXTRACTION_SCHEMA in llm_policy/tasks.py
  When a reviewer inspects it
  Then it defines items as an array of objects with name/quantity/unit fields

AC-2: ExtractionResult supports multi-item
  Given ExtractionResult dataclass in llm_policy/tasks.py
  When items field is accessed
  Then it returns a List[dict] with name/quantity/unit per item
  And item_name property returns first item's name for backward compat

AC-3: Assist mode applies all entity hint items
  Given an LLM entity hint with items=["молоко", "хлеб", "бананы"]
  And original_text="Купи молоко, хлеб и бананы"
  When _apply_entity_hints() is called
  Then normalized["items"] contains all three items that match original text

AC-4: Assist mode handles mixed matching
  Given an LLM entity hint with items=["молоко", "торт", "хлеб"]
  And original_text="Купи молоко и хлеб"
  When _apply_entity_hints() processes the hint
  Then only "молоко" and "хлеб" are accepted (matching original text)

AC-5: Agent hint path also populates multi-item
  Given an agent entity hint with items=["яблоки", "апельсины"]
  When _apply_entity_hints() processes the agent hint
  Then normalized["items"] contains items for both

AC-6: Fallback to baseline when hints are empty
  Given no LLM hint and no agent hint
  When _apply_entity_hints() is called
  Then normalized["items"] is unchanged (baseline items from ST-009 remain)

AC-7: Entity schema for assist LLM call uses structured items
  Given _ENTITY_SCHEMA in routers/assist/runner.py
  When a reviewer inspects it
  Then items is an array of objects with name/quantity/unit (not plain strings)
```

## Scope

### In scope

- Update `SHOPPING_EXTRACTION_SCHEMA` in `llm_policy/tasks.py` to multi-item format
- Update `ExtractionResult` dataclass for multi-item
- Update `_ENTITY_SCHEMA` in `routers/assist/runner.py` to structured item objects
- Update `_apply_entity_hints()` to populate all items (not just first)
- Add `_pick_matching_items()` helper (returns all matches)
- Keep `_pick_matching_item()` for backward compat where needed
- Update assist mode logging to reflect multi-item counts

### Out of scope

- V2 planner changes (ST-011)
- Baseline extraction changes (done in ST-009)
- Golden dataset changes (done in ST-009)
- Partial trust candidate generation schema
- Shadow router LLM extraction
- Attribute hints parsing

## Test Strategy

### Unit tests (new file `tests/test_llm_extraction_multi_item.py`)

- `test_schema_has_items_array` -- verify SHOPPING_EXTRACTION_SCHEMA structure
- `test_extraction_result_items_list` -- verify ExtractionResult.items returns list
- `test_extraction_result_item_name_compat` -- verify .item_name returns first item
- `test_extraction_result_empty` -- verify empty items -> item_name is None

### Unit tests (new file `tests/test_assist_multi_item.py` or extend existing)

- `test_entity_hints_all_items_applied` -- 3 items hint, all match -> 3 items
- `test_entity_hints_partial_match` -- 3 items hint, 2 match -> 2 items
- `test_entity_hints_no_match` -- items hint, none match -> items unchanged
- `test_agent_hint_multi_item` -- agent returns 2 items -> both applied
- `test_entity_hints_fallback_no_hint` -- no hint -> baseline items preserved
- `test_entity_schema_structure` -- verify _ENTITY_SCHEMA shape

## Flags

- contract_impact: no (LLM schemas and assist mode are internal)
- adr_needed: none
- diagrams_needed: none
- security_sensitive: no
- traceability_critical: no

## Blocked By

- **ST-009**: Internal model (`items` in normalized dict) and baseline extraction must be
  implemented first.
