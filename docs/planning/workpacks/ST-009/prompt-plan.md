# Codex PLAN Prompt — ST-009: Baseline Multi-Item Extraction

## Role

You are a read-only explorer. You MUST NOT edit, create, or delete any files.

## Allowed commands (whitelist)

- `ls`, `find`
- `cat`, `head`, `tail`
- `rg`, `grep`
- `sed -n`
- `git status`, `git diff`

## Forbidden

- Any file modifications
- Package management, network access
- `git commit`, `git push`

## Environment

- Python binary: `python3` (NOT `python`)

## STOP-THE-LINE

If you discover something that contradicts the workpack assumptions, STOP and report it.

---

## Context

We are implementing ST-009: baseline multi-item extraction for shopping commands.

**Workpack:** `docs/planning/workpacks/ST-009/workpack.md`
**ADR-006-P:** `docs/adr/ADR-006-multi-item-internal-model.md`

**Key decisions from ADR-006-P:**
- Internal model: `items: List[dict]` with `{name, quantity, unit}`
- Quantity type: `string` (aligned with contract)
- Backward compat: `item_name` kept as-is in normalized dict

---

## Exploration Tasks

### Task 1: Current `extract_item_name()` function

```bash
sed -n '60,68p' graphs/core_graph.py
```

**Report:** Confirm function signature, patterns list, and return type.

### Task 2: Current `process_command()` usage of `extract_item_name`

```bash
grep -n "extract_item_name" graphs/core_graph.py
```

**Report:** Confirm all call sites within core_graph.py. These must NOT change.

### Task 3: V2 normalize() function

```bash
sed -n '58,77p' routers/v2.py
```

**Report:** Confirm current normalized dict structure and where to add `items`.

### Task 4: V2 import block

```bash
sed -n '1,35p' routers/v2.py
```

**Report:** Confirm existing imports from `graphs.core_graph` to plan the new import.

### Task 5: Agent runner schema quantity type

```bash
cat agent_runner/schemas.py
```

**Report:** Confirm current `quantity` type is `["number", "null"]` at line 22.

### Task 6: Baseline shopping agent

```bash
cat agents/baseline_shopping.py
```

**Report:** Confirm imports, `extract_item_name` usage, and return structure.

### Task 7: Baseline clarify agent

```bash
cat agents/baseline_clarify.py
```

**Report:** Confirm `extract_item_name` usage at line 21.

### Task 8: Golden dataset structure

```bash
cat skills/graph-sanity/fixtures/golden_dataset.json
```

**Report:** List all multi-item entries (buy_bread_and_eggs, buy_apples_en, grocery_run) and their current `expected_entity_keys`.

### Task 9: Existing baseline agent tests

```bash
cat tests/test_agent_baseline_v0.py
```

**Report:** Confirm what tests exist for baseline_shopping and what they assert. These must still pass.

### Task 10: All callers of `extract_item_name` across codebase

```bash
rg "extract_item_name" --type py
```

**Report:** Complete list of all files importing/using `extract_item_name`. All must continue working.

### Task 11: Check for existing `extract_items` to avoid name collision

```bash
rg "extract_items" --type py
```

**Report:** Confirm no existing function named `extract_items`.

### Task 12: Graph sanity test (how golden dataset is used)

```bash
rg -n "golden_dataset" tests/
```

**Report:** Find which test reads golden_dataset.json and how `expected_entity_keys` is validated. This determines what fields we can add.

### Task 13: Verify `re` module availability

```bash
python3 -c "import re; print('re available')"
```

**Report:** Confirm `re` is available for splitting patterns.

---

## Expected Output

Produce a numbered report (Task 1 through Task 13) with:
- All function signatures and import paths confirmed
- Complete list of `extract_item_name` callers
- Golden dataset multi-item entries with current expectations
- Any STOP-THE-LINE issues
