# Codex PLAN Prompt — ST-011: V2 Planner Multi-Action Generation and E2E

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

We are implementing ST-011: V2 planner multi-action generation and end-to-end integration.

**Workpack:** `docs/planning/workpacks/ST-011/workpack.md`
**ADR-006-P:** `docs/adr/ADR-006-multi-item-internal-model.md`
**Contract:** `contracts/schemas/decision.schema.json`

**Key decisions:**
- `plan()` iterates `normalized["items"]` to build N proposed_actions
- `validate_and_build()` checks `items` OR `item_name`
- `decision.schema.json` already supports quantity/unit/list_id (no changes)
- Golden-like test updated for V1/V2 divergence on multi-item

---

## Exploration Tasks

### Task 1: Current `plan()` method

```bash
sed -n '82,116p' routers/v2.py
```

**Report:** Confirm line 87 condition uses `item_name`, lines 88-98 build single proposed_action.

### Task 2: Current `validate_and_build()` item check

```bash
sed -n '152,169p' routers/v2.py
```

**Report:** Confirm line 153 checks `normalized.get("item_name")`.

### Task 3: Decision schema — shopping_item_payload

```bash
sed -n '88,98p' contracts/schemas/decision.schema.json
```

**Report:** Confirm `shopping_item_payload` has: name (required), quantity, unit, list_id — all string.

### Task 4: Decision schema — proposed_action and start_job_payload

```bash
sed -n '99,132p' contracts/schemas/decision.schema.json
```

**Report:** Confirm `proposed_actions` is array of `proposed_action` refs.

### Task 5: Golden-like test

```bash
cat tests/test_router_golden_like.py
```

**Report:** Confirm `_load_fixture_commands(limit=3)` loads first 3 alphabetically. List the 3 fixture filenames.

### Task 6: First 3 fixtures (alphabetically)

```bash
ls skills/graph-sanity/fixtures/commands/ | head -3
```

```bash
cat skills/graph-sanity/fixtures/commands/add_sugar_ru.json
cat skills/graph-sanity/fixtures/commands/buy_apples_en.json
cat skills/graph-sanity/fixtures/commands/buy_bread_and_eggs.json
```

**Report:** Identify which are multi-item (will cause V1/V2 divergence).

### Task 7: normalize() — confirm items and item_name both populated

```bash
sed -n '59,80p' routers/v2.py
```

**Report:** Confirm line 67 populates `items` and line 62-65 populates `item_name`. Both in normalized dict.

### Task 8: _default_list_id helper

```bash
rg "_default_list_id" routers/v2.py graphs/core_graph.py
```

**Report:** Confirm import and availability.

### Task 9: build_proposed_action signature

```bash
rg "def build_proposed_action" graphs/core_graph.py
```

**Report:** Confirm signature `(action: str, payload: Dict) -> Dict`.

### Task 10: Partial trust — does it use item_name or items?

```bash
sed -n '209,378p' routers/v2.py
```

**Report:** Confirm `_maybe_apply_partial_trust` does NOT reference `normalized["items"]`. Confirm it uses `baseline` decision (which comes from plan via proposed_actions). Confirm partial trust path is safe.

### Task 11: Existing partial trust tests

```bash
rg "def test_" tests/test_partial_trust_phase3.py
```

**Report:** List all test names. These must pass unchanged.

### Task 12: Check for existing test file name collisions

```bash
ls tests/test_planner_multi* tests/test_multi_item_e2e* 2>/dev/null || echo "No existing files"
```

**Report:** Confirm no collisions.

### Task 13: V1 pipeline — confirm NOT to be modified

```bash
rg "class RouterV1" routers/v1.py
```

**Report:** Confirm V1 adapter exists and is separate from V2.

---

## Expected Output

Produce a numbered report (Task 1 through Task 13) with:
- All function signatures and line numbers confirmed
- Decision schema payload fields confirmed
- Golden-like test fixture list and multi-item identification
- Partial trust safety confirmed
- Any STOP-THE-LINE issues
