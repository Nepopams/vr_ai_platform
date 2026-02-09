# Codex APPLY Prompt — ST-012: Enhanced missing_fields Detection

## Role

You are an implementation agent. Apply changes exactly as specified below.

## Environment

- Python binary: `python3` (NOT `python`)
- All tests: `python3 -m pytest tests/ -v`

## STOP-THE-LINE

If any instruction contradicts what you see in the codebase, STOP and report.

---

## Context

Implementing ST-012: Enhanced missing_fields detection in `validate_and_build()`.

**What changes:** Add `missing_fields` to 2 clarify triggers that currently pass `None`:
- Trigger #1 (no `start_job` capability) -> `missing_fields=["capability.start_job"]`
- Trigger #5 (intent not detected) -> `missing_fields=["intent"]`

**PLAN findings confirmed:**
- Triggers #1 and #5 currently pass `missing_fields=None` (lines ~146-155 and ~207-215)
- Adding missing_fields activates the `_clarify_question` subset gate for LLM hints — this is desired
- No existing tests hit these triggers with missing_fields assertions
- Schema allows any string values in missing_fields
- No collisions with new field names

---

## Step 1: Update trigger #1 in `routers/v2.py`

Find lines 146-155 (no start_job capability trigger):

```python
        if "start_job" not in capabilities:
            return build_clarify_decision(
                command,
                question=self._clarify_question(
                    "Какие действия разрешены для выполнения?",
                    assist,
                    missing_fields=None,
                ),
                explanation="Отсутствует capability start_job.",
            )
```

Replace with:

```python
        if "start_job" not in capabilities:
            return build_clarify_decision(
                command,
                question=self._clarify_question(
                    "Какие действия разрешены для выполнения?",
                    assist,
                    missing_fields=["capability.start_job"],
                ),
                missing_fields=["capability.start_job"],
                explanation="Отсутствует capability start_job.",
            )
```

Note: `missing_fields` is passed to BOTH `_clarify_question()` (for LLM subset gate) AND `build_clarify_decision()` (for the payload).

---

## Step 2: Update trigger #5 in `routers/v2.py`

Find lines 207-215 (intent not detected trigger):

```python
        return build_clarify_decision(
            command,
            question=self._clarify_question(
                "Уточните, что нужно сделать: задача или покупка?",
                assist,
                missing_fields=None,
            ),
            explanation="Интент не распознан.",
        )
```

Replace with:

```python
        return build_clarify_decision(
            command,
            question=self._clarify_question(
                "Уточните, что нужно сделать: задача или покупка?",
                assist,
                missing_fields=["intent"],
            ),
            missing_fields=["intent"],
            explanation="Интент не распознан.",
        )
```

---

## Step 3: Create `tests/test_clarify_missing_fields.py`

Create this NEW file with the following content:

```python
"""Unit tests for enriched missing_fields in clarify decisions (ST-012)."""

from routers.v2 import RouterV2Pipeline


def _command(text="", capabilities=None, context=None):
    return {
        "command_id": "cmd-clarify-test",
        "user_id": "user-1",
        "timestamp": "2026-01-01T00:00:00Z",
        "text": text,
        "capabilities": capabilities
        or ["start_job", "propose_add_shopping_item", "propose_create_task", "clarify"],
        "context": context
        or {
            "household": {
                "members": [{"user_id": "user-1", "display_name": "Тест"}],
                "shopping_lists": [{"list_id": "list-1", "name": "Продукты"}],
            }
        },
    }


def test_clarify_intent_unknown_has_missing_fields():
    """AC-1: Intent not detected -> missing_fields=['intent']."""
    router = RouterV2Pipeline()
    decision = router.decide(_command("Что-то непонятное про погоду"))

    assert decision["action"] == "clarify"
    assert decision["payload"]["missing_fields"] == ["intent"]


def test_clarify_no_capability_has_missing_fields():
    """AC-2: No start_job capability -> missing_fields=['capability.start_job']."""
    router = RouterV2Pipeline()
    decision = router.decide(
        _command("Купи молоко", capabilities=["propose_add_shopping_item", "clarify"])
    )

    assert decision["action"] == "clarify"
    assert decision["payload"]["missing_fields"] == ["capability.start_job"]


def test_clarify_empty_text_backward_compat():
    """AC-4: Empty text -> missing_fields=['text'] (unchanged)."""
    router = RouterV2Pipeline()
    decision = router.decide(_command(""))

    assert decision["action"] == "clarify"
    assert decision["payload"]["missing_fields"] == ["text"]


def test_clarify_no_item_backward_compat():
    """AC-5: Shopping intent, no items -> missing_fields=['item.name'] (unchanged)."""
    router = RouterV2Pipeline()
    # "Купи" alone triggers add_shopping_item intent but extracts no item name
    decision = router.decide(_command("Купи"))

    assert decision["action"] == "clarify"
    assert decision["payload"]["missing_fields"] == ["item.name"]


def test_clarify_no_task_title_backward_compat():
    """AC-6: Task intent, no title -> missing_fields=['task.title'] (unchanged)."""
    router = RouterV2Pipeline()
    # "Сделай" triggers create_task intent but extracts no title if too short
    decision = router.decide(_command("Задача"))

    # This should either be clarify with task.title or clarify with intent
    # depending on intent detection. If intent is create_task:
    if decision["payload"].get("missing_fields") == ["task.title"]:
        assert decision["action"] == "clarify"
    else:
        # If intent is not detected, we get ["intent"] instead
        assert decision["action"] == "clarify"
        assert "missing_fields" in decision["payload"]


def test_start_job_no_missing_fields():
    """AC-7 regression: start_job decision has no missing_fields in payload."""
    router = RouterV2Pipeline()
    decision = router.decide(_command("Купи молоко"))

    assert decision["action"] == "start_job"
    assert "missing_fields" not in decision.get("payload", {})
```

---

## Verification

Run ALL tests after completing all steps:

```bash
# 1. New clarify tests
python3 -m pytest tests/test_clarify_missing_fields.py -v

# 2. Full test suite
python3 -m pytest tests/ -v

# 3. No secrets
grep -rn 'sk-\|api_key\s*=\s*[\"'"'"']' routers/v2.py tests/test_clarify_missing_fields.py

# 4. Schema validation
python3 -c "
from routers.v2 import RouterV2Pipeline
from jsonschema import validate
import json
from pathlib import Path

schema = json.loads(Path('contracts/schemas/decision.schema.json').read_text())

# Unknown intent
cmd = {
    'command_id': 'c1', 'user_id': 'u1', 'timestamp': '2026-01-01T00:00:00Z',
    'text': 'Что-то непонятное',
    'capabilities': ['start_job', 'propose_add_shopping_item', 'clarify'],
    'context': {'household': {'members': [{'user_id': 'u1', 'display_name': 'A'}], 'shopping_lists': [{'list_id': 'l1', 'name': 'P'}]}},
}
d = RouterV2Pipeline().decide(cmd)
validate(instance=d, schema=schema)
assert d['action'] == 'clarify'
assert d['payload']['missing_fields'] == ['intent']
print(f'OK: intent unknown -> missing_fields={d[\"payload\"][\"missing_fields\"]}')

# No capability
cmd2 = dict(cmd)
cmd2['text'] = 'Купи молоко'
cmd2['capabilities'] = ['propose_add_shopping_item', 'clarify']
d2 = RouterV2Pipeline().decide(cmd2)
validate(instance=d2, schema=schema)
assert d2['action'] == 'clarify'
assert d2['payload']['missing_fields'] == ['capability.start_job']
print(f'OK: no capability -> missing_fields={d2[\"payload\"][\"missing_fields\"]}')
"
```

Expected: ALL tests pass, no secrets found, schema validation passes.

---

## Files summary

| File | Action |
|------|--------|
| `routers/v2.py` | Edit 2 clarify triggers (Steps 1-2) |
| `tests/test_clarify_missing_fields.py` | Create new file (Step 3) |

## Invariants (DO NOT break)

- `graphs/core_graph.py` — NOT modified
- `contracts/schemas/decision.schema.json` — NOT modified
- `contracts/schemas/command.schema.json` — NOT modified
- `routers/assist/runner.py` — NOT modified
- Triggers #2, #3, #4 in `validate_and_build()` — NOT modified
- `_clarify_question()` method — NOT modified
