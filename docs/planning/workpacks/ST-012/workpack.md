# Workpack: ST-012 — Enhanced missing_fields Detection in Baseline

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Story spec | `docs/planning/epics/EP-005/stories/ST-012-enhanced-missing-fields.md` |
| Contract schema | `contracts/schemas/decision.schema.json` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

Enrich `missing_fields` in all 5 clarify triggers in `validate_and_build()` so every clarify decision includes specific field identifiers telling the consumer exactly what information is missing.

## Current State

`validate_and_build()` in `routers/v2.py` lines 135-215 has 5 clarify triggers:

| # | Trigger | Current missing_fields | Target missing_fields |
|---|---------|----------------------|----------------------|
| 1 | No `start_job` capability (line 146) | **None** | `["capability.start_job"]` |
| 2 | Empty text (line 157) | `["text"]` | `["text"]` (unchanged) |
| 3 | Shopping, no items/item_name (line 169) | `["item.name"]` | `["item.name"]` (unchanged) |
| 4 | Task, no title (line 188) | `["task.title"]` | `["task.title"]` (unchanged) |
| 5 | Intent not detected (line 207) | **None** | `["intent"]` |

Only triggers #1 and #5 change. Triggers #2, #3, #4 are unchanged (backward compat).

---

## Acceptance Criteria

- AC-1: Intent not detected -> `missing_fields=["intent"]`
- AC-2: No start_job capability -> `missing_fields=["capability.start_job"]`
- AC-4: Empty text -> `missing_fields=["text"]` (backward compat)
- AC-5: Shopping, no items -> `missing_fields=["item.name"]` (backward compat)
- AC-6: Task, no title -> `missing_fields=["task.title"]` (backward compat)
- AC-7: All 176 existing tests pass

---

## Files to Change

| File | Action | Lines |
|------|--------|-------|
| `routers/v2.py` | Edit `validate_and_build()` -- 2 triggers | ~146-155, ~207-215 |
| `tests/test_clarify_missing_fields.py` | Create new test file | New |

---

## Implementation Plan

### Step 1: Update trigger #1 (no capability) in `routers/v2.py`

Lines 146-155: Add `missing_fields=["capability.start_job"]` to both the `_clarify_question()` call and the `build_clarify_decision()` call.

### Step 2: Update trigger #5 (intent not detected) in `routers/v2.py`

Lines 207-215: Add `missing_fields=["intent"]` to both the `_clarify_question()` call and the `build_clarify_decision()` call.

### Step 3: Create `tests/test_clarify_missing_fields.py`

6 unit tests covering all 5 triggers + 1 start_job regression test.

---

## Verification Commands

```bash
# 1. New clarify tests
python3 -m pytest tests/test_clarify_missing_fields.py -v

# 2. Full test suite
python3 -m pytest tests/ -v

# 3. No secrets
grep -rn 'sk-\|api_key\s*=\s*[\"'"'"']' routers/v2.py tests/test_clarify_missing_fields.py

# 4. Schema validation (clarify with missing_fields)
python3 -c "
from routers.v2 import RouterV2Pipeline
from jsonschema import validate
import json
from pathlib import Path

schema = json.loads(Path('contracts/schemas/decision.schema.json').read_text())

# Test unknown intent -> missing_fields=['intent']
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

# Test no capability -> missing_fields=['capability.start_job']
cmd2 = dict(cmd)
cmd2['text'] = 'Купи молоко'
cmd2['capabilities'] = ['propose_add_shopping_item', 'clarify']  # no start_job!
d2 = RouterV2Pipeline().decide(cmd2)
validate(instance=d2, schema=schema)
assert d2['action'] == 'clarify'
assert d2['payload']['missing_fields'] == ['capability.start_job']
print(f'OK: no capability -> missing_fields={d2[\"payload\"][\"missing_fields\"]}')
"
```

Expected: ALL tests pass, no secrets, schema validates.

---

## Tests

| Test | AC | Description |
|------|-----|-------------|
| `test_clarify_intent_unknown_has_missing_fields` | AC-1 | Intent not detected -> `["intent"]` |
| `test_clarify_no_capability_has_missing_fields` | AC-2 | No start_job cap -> `["capability.start_job"]` |
| `test_clarify_empty_text_backward_compat` | AC-4 | Empty text -> `["text"]` unchanged |
| `test_clarify_no_item_backward_compat` | AC-5 | Shopping, no items -> `["item.name"]` unchanged |
| `test_clarify_no_task_title_backward_compat` | AC-6 | Task, no title -> `["task.title"]` unchanged |
| `test_start_job_no_missing_fields` | AC-7 | start_job decision has no missing_fields in payload |

---

## DoD Checklist

- [ ] `routers/v2.py` updated (2 triggers enriched)
- [ ] `tests/test_clarify_missing_fields.py` created (6 tests)
- [ ] All 176 existing tests pass
- [ ] New tests pass
- [ ] Schema validation passes for enriched clarify decisions
- [ ] No secrets in changed files
- [ ] No changes to `graphs/core_graph.py`, `decision.schema.json`, `command.schema.json`

---

## Risks

| Risk | Mitigation |
|------|-----------|
| Enriched missing_fields break _clarify_question subset check | Only adding fields for triggers that currently pass None — subset check is not activated for None missing_fields |
| Existing tests fail | Changes are additive; existing triggers #2,3,4 unchanged |

## Rollback

Revert the 2 line changes in `validate_and_build()`. Delete test file.

---

## Invariants (DO NOT break)

- `graphs/core_graph.py` — NOT modified
- `contracts/schemas/decision.schema.json` — NOT modified
- `contracts/schemas/command.schema.json` — NOT modified
- `routers/assist/runner.py` — NOT modified
- Existing clarify triggers #2, #3, #4 behavior unchanged
- `_clarify_question()` logic unchanged
