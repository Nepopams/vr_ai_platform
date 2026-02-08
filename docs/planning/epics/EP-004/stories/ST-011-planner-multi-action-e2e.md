# ST-011: V2 Planner Multi-Action Generation and End-to-End Integration

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
| Contract schema (decision) | `contracts/schemas/decision.schema.json` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Description

As a platform developer, I need the V2 planner to generate one `proposed_action` per extracted
item, so that a multi-item command like "Купи молоко, хлеб и бананы" produces a `start_job`
decision with three `proposed_actions`, and I need end-to-end integration tests that prove the
entire pipeline works correctly for multi-item commands.

This story also validates that the generated decisions comply with `decision.schema.json` and
that partial trust is not broken by the multi-item changes.

### Current code touchpoints

| File | Current behavior | Required change |
|------|-----------------|-----------------|
| `routers/v2.py:79-95` | `plan()` builds exactly 1 proposed_action from `item_name` | Iterate `normalized["items"]`, build N proposed_actions |
| `routers/v2.py:149-166` | `validate_and_build()` checks `normalized.get("item_name")` | Check `normalized.get("items")` (empty list = clarify) |

## Acceptance Criteria

```gherkin
AC-1: Planner generates multiple proposed_actions for multi-item
  Given normalized dict with items=[{name: "молоко"}, {name: "хлеб"}, {name: "бананы"}]
  When plan() is called
  Then proposed_actions contains 3 entries
  And each has action="propose_add_shopping_item"

AC-2: Planner includes quantity and unit when present
  Given normalized dict with items=[{name: "молока", quantity: "2", unit: "литра"}]
  When plan() is called
  Then proposed_actions[0].payload.item has name="молока", quantity="2", unit="литра"

AC-3: Planner still works for single item
  Given normalized dict with items=[{name: "молоко"}]
  When plan() is called
  Then proposed_actions contains exactly 1 entry (identical to current behavior)

AC-4: Clarify when no items extracted
  Given normalized dict with items=[] and item_name=None
  When validate_and_build() is called
  Then a clarify decision is returned

AC-5: Generated decision validates against contract schema
  Given a multi-item command "Купи молоко, хлеб и бананы"
  When the full RouterV2Pipeline.decide() is called
  Then the returned decision validates against contracts/schemas/decision.schema.json

AC-6: Partial trust path is not broken
  Given partial trust is enabled for add_shopping_item
  And a single-item command "Купи молоко"
  When RouterV2Pipeline.decide() is called
  Then partial trust candidate generation still works

AC-7: End-to-end multi-item pipeline test
  Given a full command with text="Купи молоко, хлеб и бананы"
  When the pipeline processes it
  Then status="ok", action="start_job"
  And proposed_actions has 3 entries with correct item names

AC-8: list_id propagated to all items
  Given a command with default_list_id="list-1" in context
  And text="Купи молоко и хлеб"
  When plan() generates proposed_actions
  Then both proposed_actions have item.list_id="list-1"
```

## Scope

### In scope

- Update `RouterV2Pipeline.plan()` to iterate `normalized["items"]` and generate N proposed_actions
- Update `RouterV2Pipeline.validate_and_build()` to check `items` list
- Add list_id to each item from context defaults
- Add quantity/unit to item payloads when present
- End-to-end integration tests with multi-item commands
- Schema validation test (decision output vs decision.schema.json)
- Regression test: partial trust not broken
- Regression test: single-item commands still work

### Out of scope

- Changes to extraction logic (done in ST-009)
- Changes to LLM/assist mode (done in ST-010)
- Changes to partial trust candidate generation
- Contract schema modifications
- Attribute hints in proposed_actions
- Multi-intent support

## Test Strategy

### Unit tests (new file `tests/test_planner_multi_item.py`)

- `test_plan_multi_item_3_actions` -- 3 items -> 3 proposed_actions
- `test_plan_multi_item_with_quantity_unit` -- quantity/unit in payload
- `test_plan_single_item_backward_compat` -- single item -> 1 proposed_action
- `test_plan_empty_items_clarify` -- no items -> clarify
- `test_plan_list_id_propagated_to_all` -- list_id on every item

### Integration tests (new file `tests/test_multi_item_e2e.py`)

- `test_e2e_multi_item_russian` -- full pipeline "Купи молоко, хлеб и бананы"
- `test_e2e_multi_item_english` -- full pipeline "Buy apples and oranges"
- `test_e2e_single_item_unchanged` -- regression: single item still works
- `test_e2e_decision_schema_valid` -- validate output against decision.schema.json
- `test_e2e_partial_trust_not_broken` -- partial trust single item still works
- `test_e2e_multi_item_with_quantity` -- "Купи 2 литра молока и хлеб"

## Flags

- contract_impact: review (validates decisions comply with existing schema)
- adr_needed: none
- diagrams_needed: none
- security_sensitive: no
- traceability_critical: no

## Blocked By

- **ST-009**: Internal model and baseline extraction must be implemented first.
- **ST-010** (soft): End-to-end tests should run after LLM/assist changes.
