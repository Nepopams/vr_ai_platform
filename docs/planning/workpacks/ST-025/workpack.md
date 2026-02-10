# Workpack: ST-025 — Expand Golden Dataset to 20+ Commands

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Story spec | `docs/planning/epics/EP-009/stories/ST-025-expand-golden-dataset.md` |
| Epic | `docs/planning/epics/EP-009/epic.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q4-production-hardening.md` |
| Sprint | `docs/planning/sprints/S06/sprint.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

Golden dataset expanded from 14 to 22+ entries with new fields (`expected_action`,
`difficulty`) and new edge cases (ambiguous, typo, multi-entity with quantities).
All existing tests updated for new count. All 3 intents have >= 3 entries.

---

## Acceptance Criteria Summary

1. Dataset has 20+ entries
2. All intents (add_shopping_item, create_task, clarify_needed) have >= 3 entries
3. Edge cases with difficulty="hard" >= 3
4. Backward compatible — all existing graph-sanity and shadow-analyzer tests pass
5. All 236 existing tests pass; ~3 new validation tests pass

---

## Key Design Decisions

### New fields are additive (backward compatible)
Add `expected_action`, `difficulty` to each entry. Existing consumers
(`load_golden_dataset` in `scripts/analyze_shadow_router.py:49-59`) read only
`command_id`, `expected_intent`, `expected_entity_keys` — new fields are safely ignored.

### CRITICAL: Update hardcoded count assertion
`tests/test_analyze_shadow_router.py:261` asserts `len(data) == 14`.
Must change to `len(data) >= 20` to accommodate expansion.

### Reuse existing extra fixture files
Two fixture command files already exist without golden dataset entries:
- `skills/graph-sanity/fixtures/commands/clarify_partial_shopping.json`
- `skills/graph-sanity/fixtures/commands/clarify_ambiguous_intent.json`

These should be added to golden_dataset.json (adds 2 clarify_needed entries for free).

### New fixture command files needed
For new entries, create matching command fixture files in
`skills/graph-sanity/fixtures/commands/`. Follow existing schema
(command_id, user_id, timestamp, text, capabilities, context).

### Current intent distribution (14 entries)
- add_shopping_item: 7 (cmd-001, 002, 008, 010, 011, 012, cmd-graph-002)
- create_task: 5 (cmd-003, 004, 007, 009, cmd-graph-001)
- clarify_needed: 2 (cmd-005, 006)

Target: add 8+ entries, emphasizing clarify_needed (need +1 minimum) and hard cases.

---

## Files to Change

| File | Action | Description |
|------|--------|-------------|
| `skills/graph-sanity/fixtures/golden_dataset.json` | **Update** | Expand from 14 to 22+ entries, add new fields |
| `skills/graph-sanity/fixtures/commands/*.json` | **New** (6-8 files) | Fixture command files for new entries |
| `tests/test_analyze_shadow_router.py` | **Update** | Change `len(data) == 14` to `len(data) >= 20` |
| `tests/test_golden_dataset_validation.py` | **New** | 3 validation tests |

### Files NOT changed (invariants)
- `scripts/analyze_shadow_router.py` — load_golden_dataset reads existing fields only
- `skills/graph-sanity/scripts/run_graph_suite.py` — reads commands dir, not golden_dataset.json
- `contracts/schemas/command.schema.json` — command fixtures must conform
- `contracts/schemas/decision.schema.json` — no change

---

## Implementation Plan

### Step 1: Add new golden dataset entries to `golden_dataset.json`

Add 8+ new entries. Example new entries:

```json
{
  "command_id": "cmd-gd-015",
  "fixture_file": "clarify_partial_shopping.json",
  "expected_intent": "clarify_needed",
  "expected_entity_keys": [],
  "expected_action": "clarify",
  "difficulty": "medium",
  "notes": "Добавь... что-то — incomplete shopping request"
},
{
  "command_id": "cmd-gd-016",
  "fixture_file": "clarify_ambiguous_intent.json",
  "expected_intent": "clarify_needed",
  "expected_entity_keys": [],
  "expected_action": "clarify",
  "difficulty": "hard",
  "notes": "Нужно что-то с молоком — ambiguous: shopping or task?"
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
  "notes": "Купии малако — typo in keyword and item"
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
  "notes": "Пожалуйста, помоги убрать комнату — polite form with keyword 'убрать'"
}
```

Also add `expected_action` and `difficulty` fields to all 14 existing entries.

### Step 2: Add `expected_action` and `difficulty` to existing entries

For each of the 14 existing entries, add:
- `expected_action`: based on `expected_intent` mapping:
  - `add_shopping_item` → `"propose_add_shopping_item"`
  - `create_task` → `"propose_create_task"`
  - `clarify_needed` → `"clarify"`
- `difficulty`: `"easy"` for most, `"medium"` for multi-item, `"hard"` for ambiguous

### Step 3: Create fixture command files for new entries

Create 6-8 new `.json` files in `skills/graph-sanity/fixtures/commands/`.
Follow existing schema pattern (see `buy_milk.json`):

```json
{
  "command_id": "cmd-gd-XXX",
  "user_id": "user-XXX",
  "timestamp": "2026-02-10T10:XX:00+00:00",
  "text": "<command text>",
  "capabilities": ["start_job", "propose_create_task", "propose_add_shopping_item", "clarify"],
  "context": {
    "household": {
      "household_id": "house-XXX",
      "members": [{"user_id": "user-XXX", "display_name": "<name>"}],
      "shopping_lists": [{"list_id": "list-1", "name": "Продукты"}]
    },
    "defaults": {"default_list_id": "list-1"}
  }
}
```

Note: `clarify_partial_shopping.json` and `clarify_ambiguous_intent.json` already exist — just add their golden_dataset entries. Read their command_ids before referencing them.

### Step 4: Update `tests/test_analyze_shadow_router.py`

Change line 261:
```python
# FROM:
assert len(data) == 14, f"Expected 14 entries, got {len(data)}"
# TO:
assert len(data) >= 20, f"Expected >= 20 entries, got {len(data)}"
```

### Step 5: Create `tests/test_golden_dataset_validation.py`

3 new validation tests:

```python
def test_golden_dataset_has_20_plus_entries():
    """AC-1: Dataset has 20+ entries."""
    data = json.loads(golden_path.read_text())
    assert len(data) >= 20

def test_golden_dataset_all_intents_represented():
    """AC-2: Each intent has >= 3 entries."""
    data = json.loads(golden_path.read_text())
    by_intent = {}
    for e in data:
        by_intent.setdefault(e["expected_intent"], []).append(e)
    for intent in ["add_shopping_item", "create_task", "clarify_needed"]:
        assert len(by_intent.get(intent, [])) >= 3

def test_golden_dataset_has_hard_cases():
    """AC-3: At least 3 entries with difficulty='hard'."""
    data = json.loads(golden_path.read_text())
    hard = [e for e in data if e.get("difficulty") == "hard"]
    assert len(hard) >= 3
```

---

## Verification Commands

```bash
# Run new validation tests
source .venv/bin/activate && python3 -m pytest tests/test_golden_dataset_validation.py -v

# Run shadow analyzer tests (must still pass, especially manifest schema test)
source .venv/bin/activate && python3 -m pytest tests/test_analyze_shadow_router.py -v

# Run graph-sanity suite (new fixtures must process cleanly)
source .venv/bin/activate && python3 skills/graph-sanity/scripts/run_graph_suite.py

# Full test suite
source .venv/bin/activate && python3 -m pytest --tb=short -q

# Quick count check
python3 -c "import json; d=json.loads(open('skills/graph-sanity/fixtures/golden_dataset.json').read()); print(f'Entries: {len(d)}')"
```

---

## Tests

### New tests (~3 in `tests/test_golden_dataset_validation.py`)
| Test | Validates |
|------|-----------|
| `test_golden_dataset_has_20_plus_entries` | AC-1 |
| `test_golden_dataset_all_intents_represented` | AC-2 |
| `test_golden_dataset_has_hard_cases` | AC-3 |

### Modified tests
| Test | Change |
|------|--------|
| `test_golden_dataset_manifest_schema` (test_analyze_shadow_router.py:254) | `== 14` → `>= 20` |

### Regression
- All 236 existing tests must pass (AC-4, AC-5)

---

## DoD Checklist

- [ ] `golden_dataset.json` expanded to 22+ entries
- [ ] New fields `expected_action` and `difficulty` on ALL entries
- [ ] add_shopping_item >= 3 entries
- [ ] create_task >= 3 entries
- [ ] clarify_needed >= 3 entries
- [ ] difficulty="hard" entries >= 3
- [ ] New fixture command files created for new entries
- [ ] `test_analyze_shadow_router.py` assertion updated (14 → >= 20)
- [ ] 3 new validation tests pass
- [ ] All 236 existing tests pass
- [ ] graph-sanity suite runs cleanly with new fixtures

---

## Risks

| Risk | Mitigation |
|------|------------|
| New fixture files break command schema validation | Follow exact schema pattern from buy_milk.json. Verify via run_graph_suite.py. |
| Hardcoded `== 14` assertion in test_analyze_shadow_router.py | Explicitly update to `>= 20`. |
| New golden entries reference non-existent fixture files | Create all referenced fixture files. Check with `ls`. |
| `load_golden_dataset` breaks with new fields | Already confirmed: reads only command_id, expected_intent, expected_entity_keys. New fields ignored. |
| Existing clarify fixtures have different command_ids | Read clarify_partial_shopping.json and clarify_ambiguous_intent.json first to get actual command_ids. |

---

## Rollback

- Revert `golden_dataset.json` to 14-entry version
- Delete new fixture command files
- Revert `tests/test_analyze_shadow_router.py` assertion
- Delete `tests/test_golden_dataset_validation.py`
