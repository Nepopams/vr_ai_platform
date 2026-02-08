# Workpack — ST-011: V2 Planner Multi-Action Generation and End-to-End Integration

**Status:** Ready
**Story:** `docs/planning/epics/EP-004/stories/ST-011-planner-multi-action-e2e.md`
**Epic:** `docs/planning/epics/EP-004/epic.md`

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-004/epic.md` |
| Story | `docs/planning/epics/EP-004/stories/ST-011-planner-multi-action-e2e.md` |
| ADR-006-P | `docs/adr/ADR-006-multi-item-internal-model.md` |
| Contract schema | `contracts/schemas/decision.schema.json` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

V2 planner generates one `proposed_action` per extracted item (from `normalized["items"]`),
including `quantity`, `unit`, and `list_id` when present. `validate_and_build()` uses `items`
list for shopping item presence check. End-to-end tests verify the full pipeline produces
valid multi-item decisions that comply with `decision.schema.json`.

---

## Acceptance Criteria Summary

- AC-1: `plan()` generates N proposed_actions for N items
- AC-2: proposed_actions include quantity/unit when present
- AC-3: Single item still produces exactly 1 proposed_action
- AC-4: Empty items + no item_name = clarify
- AC-5: Generated decisions validate against `decision.schema.json`
- AC-6: Partial trust path not broken
- AC-7: E2E multi-item pipeline: 3 items -> 3 proposed_actions
- AC-8: list_id propagated to all items

---

## Files to Change

### 1. `routers/v2.py` — plan() and validate_and_build()

**Current state of `plan()` (lines 82-116):**
- Line 87: `if intent == "add_shopping_item" and normalized.get("item_name"):`
- Lines 88-98: builds exactly 1 proposed_action from `normalized["item_name"]`
- Only `name` and `list_id` in item_payload (no quantity/unit)

**Change `plan()` to iterate `normalized["items"]`:**

```python
def plan(self, normalized: Dict[str, Any], command: Dict[str, Any]) -> Dict[str, Any]:
    intent = normalized["intent"]
    proposed_actions: List[Dict[str, Any]] = []
    capabilities: Set[str] = normalized["capabilities"]

    if intent == "add_shopping_item":
        items = normalized.get("items", [])
        if items and "propose_add_shopping_item" in capabilities:
            list_id = _default_list_id(command)
            for item in items:
                item_payload: Dict[str, Any] = {"name": item["name"]}
                if item.get("quantity"):
                    item_payload["quantity"] = item["quantity"]
                if item.get("unit"):
                    item_payload["unit"] = item["unit"]
                if list_id:
                    item_payload["list_id"] = list_id
                proposed_actions.append(
                    build_proposed_action(
                        "propose_add_shopping_item",
                        {"item": item_payload},
                    )
                )
        elif normalized.get("item_name") and "propose_add_shopping_item" in capabilities:
            list_id = _default_list_id(command)
            item_payload = {"name": normalized["item_name"]}
            if list_id:
                item_payload["list_id"] = list_id
            proposed_actions.append(
                build_proposed_action(
                    "propose_add_shopping_item",
                    {"item": item_payload},
                )
            )
    elif intent == "create_task" and normalized.get("task_title"):
        if "propose_create_task" in capabilities:
            proposed_actions.append(
                build_proposed_action(
                    "propose_create_task",
                    {
                        "task": {
                            "title": normalized["task_title"],
                            "assignee_id": _default_assignee_id(command),
                        }
                    },
                )
            )

    return {
        "intent": intent,
        "proposed_actions": proposed_actions or None,
    }
```

**Current state of `validate_and_build()` (lines 152-153):**
```python
if not normalized.get("item_name"):
    return build_clarify_decision(...)
```

**Change to check `items` OR `item_name`:**
```python
if not normalized.get("items") and not normalized.get("item_name"):
    return build_clarify_decision(...)
```

### 2. `tests/test_router_golden_like.py` — update for V1/V2 divergence

**Current state (lines 45-58):**
- Loads first 3 fixtures (alphabetically: `add_sugar_ru`, `buy_apples_en`, `buy_bread_and_eggs`)
- Asserts `_extract_stable_fields(decision_v1) == _extract_stable_fields(decision_v2)`
- `buy_apples_en` and `buy_bread_and_eggs` are multi-item, so V2 now produces N proposed_actions

**Change:** V1/V2 comparison is no longer valid for multi-item commands because V2
intentionally produces multiple proposed_actions. Update to:
- Both V1 and V2 produce valid schema decisions (keep `validate()`)
- Compare V1==V2 stable fields only for action type (start_job/clarify), not proposed_actions details
- Add separate assertions: V2 multi-item decisions have correct proposed_actions count

```python
def test_v1_and_v2_match_on_fixtures():
    schema = _load_decision_schema()
    commands = _load_fixture_commands()
    router_v1 = RouterV1Adapter()
    router_v2 = RouterV2Pipeline()

    for command in commands:
        decision_v1 = router_v1.decide(command)
        decision_v2 = router_v2.decide(command)

        validate(instance=decision_v1, schema=schema)
        validate(instance=decision_v2, schema=schema)

        # V1 and V2 produce same action type (start_job / clarify)
        assert decision_v1["action"] == decision_v2["action"]
```

### 3. `tests/test_planner_multi_item.py` — NEW unit tests for planner

Unit tests exercising `plan()` and `validate_and_build()` directly:
- `test_plan_multi_item_3_actions` — AC-1
- `test_plan_multi_item_with_quantity_unit` — AC-2
- `test_plan_single_item_backward_compat` — AC-3
- `test_plan_empty_items_clarify` — AC-4
- `test_plan_list_id_propagated_to_all` — AC-8

### 4. `tests/test_multi_item_e2e.py` — NEW integration tests

End-to-end tests through full `RouterV2Pipeline.decide()`:
- `test_e2e_multi_item_russian` — AC-7: "Купи молоко, хлеб и бананы" -> 3 proposed_actions
- `test_e2e_multi_item_english` — "Buy apples and oranges" -> 2 proposed_actions
- `test_e2e_single_item_unchanged` — AC-3 regression: single item -> 1 proposed_action
- `test_e2e_decision_schema_valid` — AC-5: output validates against decision.schema.json
- `test_e2e_partial_trust_not_broken` — AC-6: single item partial trust still works
- `test_e2e_multi_item_with_quantity` — AC-2: "Купи 2 литра молока и хлеб" -> quantity/unit

---

## Contract Schema Validation

`decision.schema.json` already supports everything needed:
- `shopping_item_payload` (lines 88-98): `name` (required), `quantity`, `unit`, `list_id` — all string
- `proposed_action` (lines 99-115): array in `start_job_payload.proposed_actions`
- NO contract changes needed. Only validate compliance.

---

## Implementation Plan (commit-sized)

### Commit 1: V2 planner multi-item
1. Update `plan()` in `routers/v2.py` to iterate items
2. Update `validate_and_build()` to check items OR item_name

### Commit 2: Tests
1. Update `tests/test_router_golden_like.py` for V1/V2 divergence
2. Create `tests/test_planner_multi_item.py` (5 unit tests)
3. Create `tests/test_multi_item_e2e.py` (6 integration tests)

---

## Verification Commands

```bash
# 1. All tests pass
python3 -m pytest tests/ -v

# 2. New planner tests pass
python3 -m pytest tests/test_planner_multi_item.py -v

# 3. New e2e tests pass
python3 -m pytest tests/test_multi_item_e2e.py -v

# 4. Golden-like test still passes
python3 -m pytest tests/test_router_golden_like.py -v

# 5. Existing tests pass (regression)
python3 -m pytest tests/test_assist_mode.py tests/test_partial_trust_phase3.py -v

# 6. Schema validation
python3 -c "
from routers.v2 import RouterV2Pipeline
from jsonschema import validate
import json
from pathlib import Path

schema = json.loads(Path('contracts/schemas/decision.schema.json').read_text())
cmd = {
    'command_id': 'cmd-test', 'user_id': 'u1', 'timestamp': '2026-01-01T00:00:00Z',
    'text': 'Купи молоко, хлеб и бананы',
    'capabilities': ['start_job', 'propose_add_shopping_item', 'clarify'],
    'context': {'household': {'members': [{'user_id': 'u1', 'display_name': 'A'}], 'shopping_lists': [{'list_id': 'l1', 'name': 'P'}]}},
}
decision = RouterV2Pipeline().decide(cmd)
validate(instance=decision, schema=schema)
actions = decision['payload'].get('proposed_actions', [])
assert len(actions) == 3, f'Expected 3 actions, got {len(actions)}'
print(f'OK: {len(actions)} proposed_actions, schema valid')
"

# 7. No secrets
grep -rn "sk-\|api_key\s*=\s*[\"']" routers/v2.py tests/test_planner_multi_item.py tests/test_multi_item_e2e.py
```

---

## DoD Checklist

See `docs/planning/workpacks/ST-011/checklist.md`.

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Golden-like test V1!=V2 for multi-item | Test failure | Update test to compare action type only (Step 2) |
| Partial trust uses `item_name` not `items` | Partial trust breaks | Keep `item_name` in normalized dict (backward compat) |
| Contract schema doesn't support quantity/unit | Schema validation fails | Verified: `shopping_item_payload` already has quantity/unit/list_id |
| Empty items + None item_name = clarify regression | Decision logic change | Both conditions checked in validate_and_build |

---

## Rollback

Revert commit(s). No data migration, no contract changes.

---

## Invariants (DO NOT break)

- `graphs/core_graph.py` — NOT modified
- `llm_policy/tasks.py` — NOT modified
- `routers/assist/runner.py` — NOT modified
- `decision.schema.json` — NOT modified
- `command.schema.json` — NOT modified
- V1 pipeline (`process_command`) — NOT modified
- `normalized["item_name"]` — still populated (backward compat for partial trust)
- `normalized["items"]` — still populated (from ST-009 baseline + ST-010 assist)
