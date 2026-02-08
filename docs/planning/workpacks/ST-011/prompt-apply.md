# Codex APPLY Prompt — ST-011: V2 Planner Multi-Action Generation and E2E

## Role

You are an implementation agent. Apply changes exactly as specified below.

## Environment

- Python binary: `python3` (NOT `python`)
- All tests: `python3 -m pytest tests/ -v`

## STOP-THE-LINE

If any instruction contradicts what you see in the codebase, STOP and report.

---

## Context

Implementing ST-011: V2 planner multi-action generation and end-to-end integration tests.

**ADR-006-P decisions:** items = `List[dict]` with `{name, quantity, unit}`, quantity=string.

**Prerequisites (already done):**
- ST-009: `extract_items()` populates `normalized["items"]` in baseline
- ST-010: LLM/assist populate `normalized["items"]` with structured dicts
- `normalized["item_name"]` still populated via `ExtractionResult.item_name` property (backward compat)

**Contract verified:** `decision.schema.json` `shopping_item_payload` already has name, quantity, unit, list_id.

---

## Step 1: Update `routers/v2.py` — plan() method

Find lines 82-116 (the `plan` method). Replace the ENTIRE method with:

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

## Step 2: Update `routers/v2.py` — validate_and_build() item check

Find lines 152-153:
```python
        if intent == "add_shopping_item":
            if not normalized.get("item_name"):
```

Replace with:
```python
        if intent == "add_shopping_item":
            if not normalized.get("items") and not normalized.get("item_name"):
```

This is the ONLY change in validate_and_build(). Everything else stays the same.

---

## Step 3: Update `tests/test_router_golden_like.py`

Replace the ENTIRE file content with:

```python
import json
from pathlib import Path

from jsonschema import validate

from routers.v1 import RouterV1Adapter
from routers.v2 import RouterV2Pipeline


BASE_DIR = Path(__file__).resolve().parents[1]
FIXTURE_DIR = BASE_DIR / "skills" / "graph-sanity" / "fixtures" / "commands"
DECISION_SCHEMA_PATH = BASE_DIR / "contracts" / "schemas" / "decision.schema.json"


def _load_decision_schema():
    return json.loads(DECISION_SCHEMA_PATH.read_text(encoding="utf-8"))


def _load_fixture_commands(limit: int = 3):
    fixtures = sorted(FIXTURE_DIR.glob("*.json"))
    return [json.loads(path.read_text(encoding="utf-8")) for path in fixtures[:limit]]


def test_v1_and_v2_match_on_fixtures():
    """Both V1 and V2 produce valid decisions for all fixtures.

    V2 may produce more proposed_actions for multi-item commands (intentional).
    Both must produce valid schema and agree on action type (start_job/clarify).
    """
    schema = _load_decision_schema()
    commands = _load_fixture_commands()
    router_v1 = RouterV1Adapter()
    router_v2 = RouterV2Pipeline()

    for command in commands:
        decision_v1 = router_v1.decide(command)
        decision_v2 = router_v2.decide(command)

        validate(instance=decision_v1, schema=schema)
        validate(instance=decision_v2, schema=schema)

        # V1 and V2 agree on action type (start_job / clarify)
        assert decision_v1["action"] == decision_v2["action"]
        assert decision_v1["status"] == decision_v2["status"]
```

---

## Step 4: Create `tests/test_planner_multi_item.py`

Create this NEW file with the following content:

```python
"""Unit tests for V2 planner multi-item proposed_actions (ST-011)."""

from routers.v2 import RouterV2Pipeline


def _command(text="", context=None):
    cmd = {
        "command_id": "cmd-test",
        "user_id": "user-1",
        "timestamp": "2026-01-01T00:00:00Z",
        "text": text,
        "capabilities": ["start_job", "propose_add_shopping_item", "propose_create_task", "clarify"],
        "context": context or {
            "household": {
                "members": [{"user_id": "user-1", "display_name": "Тест"}],
                "shopping_lists": [{"list_id": "list-1", "name": "Продукты"}],
            }
        },
    }
    return cmd


def _normalized(items=None, item_name=None, intent="add_shopping_item", text="Купи молоко"):
    return {
        "text": text,
        "intent": intent,
        "items": items or [],
        "item_name": item_name,
        "task_title": None,
        "capabilities": {"start_job", "propose_add_shopping_item", "propose_create_task", "clarify"},
    }


def test_plan_multi_item_3_actions():
    """AC-1: 3 items -> 3 proposed_actions."""
    router = RouterV2Pipeline()
    items = [{"name": "молоко"}, {"name": "хлеб"}, {"name": "бананы"}]
    normalized = _normalized(items=items, text="Купи молоко, хлеб и бананы")
    plan = router.plan(normalized, _command("Купи молоко, хлеб и бананы"))

    actions = plan["proposed_actions"]
    assert len(actions) == 3
    names = [a["payload"]["item"]["name"] for a in actions]
    assert names == ["молоко", "хлеб", "бананы"]
    assert all(a["action"] == "propose_add_shopping_item" for a in actions)


def test_plan_multi_item_with_quantity_unit():
    """AC-2: quantity and unit propagated to proposed_action payload."""
    router = RouterV2Pipeline()
    items = [{"name": "молока", "quantity": "2", "unit": "литра"}, {"name": "хлеб"}]
    normalized = _normalized(items=items, text="Купи 2 литра молока и хлеб")
    plan = router.plan(normalized, _command("Купи 2 литра молока и хлеб"))

    actions = plan["proposed_actions"]
    assert len(actions) == 2
    first_item = actions[0]["payload"]["item"]
    assert first_item["name"] == "молока"
    assert first_item["quantity"] == "2"
    assert first_item["unit"] == "литра"
    second_item = actions[1]["payload"]["item"]
    assert second_item["name"] == "хлеб"
    assert "quantity" not in second_item
    assert "unit" not in second_item


def test_plan_single_item_backward_compat():
    """AC-3: single item -> exactly 1 proposed_action."""
    router = RouterV2Pipeline()
    items = [{"name": "молоко"}]
    normalized = _normalized(items=items, item_name="молоко", text="Купи молоко")
    plan = router.plan(normalized, _command("Купи молоко"))

    actions = plan["proposed_actions"]
    assert len(actions) == 1
    assert actions[0]["payload"]["item"]["name"] == "молоко"


def test_plan_empty_items_fallback_to_item_name():
    """Fallback: empty items but item_name present -> 1 proposed_action from item_name."""
    router = RouterV2Pipeline()
    normalized = _normalized(items=[], item_name="молоко", text="Купи молоко")
    plan = router.plan(normalized, _command("Купи молоко"))

    actions = plan["proposed_actions"]
    assert len(actions) == 1
    assert actions[0]["payload"]["item"]["name"] == "молоко"


def test_plan_list_id_propagated_to_all():
    """AC-8: list_id propagated to every item."""
    router = RouterV2Pipeline()
    items = [{"name": "молоко"}, {"name": "хлеб"}]
    normalized = _normalized(items=items, text="Купи молоко и хлеб")
    context = {
        "household": {
            "members": [{"user_id": "user-1", "display_name": "Тест"}],
            "shopping_lists": [{"list_id": "list-42", "name": "Еда"}],
        },
        "defaults": {"default_list_id": "list-42"},
    }
    plan = router.plan(normalized, _command("Купи молоко и хлеб", context=context))

    actions = plan["proposed_actions"]
    assert len(actions) == 2
    assert actions[0]["payload"]["item"]["list_id"] == "list-42"
    assert actions[1]["payload"]["item"]["list_id"] == "list-42"
```

---

## Step 5: Create `tests/test_multi_item_e2e.py`

Create this NEW file with the following content:

```python
"""End-to-end integration tests for multi-item pipeline (ST-011)."""

import json
from pathlib import Path

from jsonschema import validate

from routers.v2 import RouterV2Pipeline


BASE_DIR = Path(__file__).resolve().parents[1]
DECISION_SCHEMA_PATH = BASE_DIR / "contracts" / "schemas" / "decision.schema.json"


def _load_decision_schema():
    return json.loads(DECISION_SCHEMA_PATH.read_text(encoding="utf-8"))


def _command(text, context=None):
    return {
        "command_id": "cmd-e2e",
        "user_id": "user-1",
        "timestamp": "2026-01-01T00:00:00Z",
        "text": text,
        "capabilities": ["start_job", "propose_add_shopping_item", "propose_create_task", "clarify"],
        "context": context or {
            "household": {
                "members": [{"user_id": "user-1", "display_name": "Тест"}],
                "shopping_lists": [{"list_id": "list-1", "name": "Продукты"}],
            }
        },
    }


def test_e2e_multi_item_russian():
    """AC-7: Full pipeline 'Купи молоко, хлеб и бананы' -> 3 proposed_actions."""
    router = RouterV2Pipeline()
    decision = router.decide(_command("Купи молоко, хлеб и бананы"))

    assert decision["action"] == "start_job"
    assert decision["status"] == "ok"
    actions = decision["payload"].get("proposed_actions", [])
    assert len(actions) == 3
    names = [a["payload"]["item"]["name"] for a in actions]
    assert "молоко" in names
    assert "хлеб" in names
    assert "бананы" in names


def test_e2e_multi_item_english():
    """E2E: 'Buy apples and oranges' -> 2 proposed_actions."""
    router = RouterV2Pipeline()
    decision = router.decide(_command("Buy apples and oranges"))

    assert decision["action"] == "start_job"
    actions = decision["payload"].get("proposed_actions", [])
    assert len(actions) == 2
    names = [a["payload"]["item"]["name"] for a in actions]
    assert "apples" in names
    assert "oranges" in names


def test_e2e_single_item_unchanged():
    """AC-3 regression: single item -> 1 proposed_action."""
    router = RouterV2Pipeline()
    decision = router.decide(_command("Купи молоко"))

    assert decision["action"] == "start_job"
    actions = decision["payload"].get("proposed_actions", [])
    assert len(actions) == 1
    assert actions[0]["payload"]["item"]["name"] == "молоко"


def test_e2e_decision_schema_valid():
    """AC-5: Multi-item decision validates against decision.schema.json."""
    schema = _load_decision_schema()
    router = RouterV2Pipeline()
    decision = router.decide(_command("Купи молоко, хлеб и бананы"))

    validate(instance=decision, schema=schema)


def test_e2e_partial_trust_not_broken(monkeypatch):
    """AC-6: Partial trust disabled -> single item still works (no crash)."""
    monkeypatch.setenv("PARTIAL_TRUST_ENABLED", "false")
    router = RouterV2Pipeline()
    decision = router.decide(_command("Купи молоко"))

    assert decision["action"] == "start_job"
    actions = decision["payload"].get("proposed_actions", [])
    assert len(actions) == 1


def test_e2e_multi_item_with_quantity():
    """AC-2: 'Купи 2 литра молока и хлеб' -> quantity/unit in first item."""
    router = RouterV2Pipeline()
    decision = router.decide(_command("Купи 2 литра молока и хлеб"))

    assert decision["action"] == "start_job"
    actions = decision["payload"].get("proposed_actions", [])
    assert len(actions) == 2
    first_item = actions[0]["payload"]["item"]
    assert first_item["name"] == "молока"
    assert first_item["quantity"] == "2"
    assert first_item["unit"] == "литра"
```

---

## Verification

Run ALL tests after completing all steps:

```bash
# 1. New planner tests
python3 -m pytest tests/test_planner_multi_item.py -v

# 2. New e2e tests
python3 -m pytest tests/test_multi_item_e2e.py -v

# 3. Golden-like test
python3 -m pytest tests/test_router_golden_like.py -v

# 4. Full test suite
python3 -m pytest tests/ -v

# 5. No secrets
grep -rn "sk-\|api_key\s*=\s*[\"']" routers/v2.py tests/test_planner_multi_item.py tests/test_multi_item_e2e.py tests/test_router_golden_like.py

# 6. Schema validation check
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
```

Expected: ALL tests pass, no secrets found, schema validation passes.

---

## Files summary

| File | Action |
|------|--------|
| `routers/v2.py` | Update plan() and validate_and_build() (Steps 1-2) |
| `tests/test_router_golden_like.py` | Replace entire file (Step 3) |
| `tests/test_planner_multi_item.py` | Create new file (Step 4) |
| `tests/test_multi_item_e2e.py` | Create new file (Step 5) |

## Invariants (DO NOT break)

- `graphs/core_graph.py` — NOT modified
- `llm_policy/tasks.py` — NOT modified
- `routers/assist/runner.py` — NOT modified
- `decision.schema.json` — NOT modified
- `command.schema.json` — NOT modified
- `normalized["item_name"]` — still populated (backward compat for partial trust)
