# Codex PLAN Prompt — ST-025: Expand Golden Dataset to 20+ Commands

## Role
You are a senior Python developer. This is a **PLAN-only** phase: read the codebase,
confirm assumptions, and report findings. **Do NOT create or modify any files.**

## Context
We are expanding the golden dataset at `skills/graph-sanity/fixtures/golden_dataset.json`
from 14 to 22+ entries. New entries need corresponding fixture command files in
`skills/graph-sanity/fixtures/commands/`. We also need to update a hardcoded assertion
and add validation tests.

## Read-Only Commands Allowed
- `ls`, `find`
- `cat`, `head`, `tail`
- `rg`, `grep`
- `sed -n`
- `git status`, `git diff`

## FORBIDDEN
- Any file creation, modification, or deletion
- Any package installation
- Any git commit/push
- Any network access

## Tasks

### 1. Read golden_dataset.json
Read `skills/graph-sanity/fixtures/golden_dataset.json` and confirm:
- Current entry count (expected: 14)
- Current fields per entry
- Intent distribution: how many add_shopping_item, create_task, clarify_needed

### 2. Read existing fixture command files
List `skills/graph-sanity/fixtures/commands/` and note:
- How many .json files exist
- Which ones have golden_dataset entries and which don't
- Read `clarify_partial_shopping.json` and `clarify_ambiguous_intent.json` — get their command_ids

### 3. Examine fixture command schema
Read 2-3 fixture files (e.g., `buy_milk.json`, `empty_text.json`, `clarify_partial_shopping.json`).
Confirm the required fields: command_id, user_id, timestamp, text, capabilities, context.
Check: do all have `shopping_lists` in context? (Answer: not all — only shopping commands.)

### 4. Check command.schema.json
Read `contracts/schemas/command.schema.json`. Confirm new fixture files must conform.
Note required vs optional fields.

### 5. Find hardcoded count assertion
Read `tests/test_analyze_shadow_router.py` around line 254-267.
Confirm: `assert len(data) == 14` exists and needs update.

### 6. Verify load_golden_dataset() tolerance
Read `scripts/analyze_shadow_router.py` lines 49-59.
Confirm: reads only `command_id`, `expected_intent`, `expected_entity_keys`.
New fields like `expected_action`, `difficulty` will be safely ignored.

### 7. Check graph-sanity suite behavior
Read `skills/graph-sanity/scripts/run_graph_suite.py`.
Confirm: it reads `fixtures/commands/*.json` via glob — new fixture files will be
automatically picked up and must produce valid decisions.

### 8. Check for naming conflicts
Run: `ls tests/test_golden_dataset*` — confirm test file doesn't exist.

## Expected Output

Report:
1. Entry count confirmed: 14
2. Intent distribution: X add_shopping_item, Y create_task, Z clarify_needed
3. Extra fixture files (no golden entry): list them with command_ids
4. Command fixture required fields: list
5. Hardcoded assertion location: file:line
6. load_golden_dataset safe for new fields: yes/no
7. graph-sanity auto-picks new fixtures: yes/no
8. Naming conflicts: none / found
9. Any surprises or concerns

## STOP-THE-LINE
If golden_dataset.json has more or fewer than 14 entries, or if the command schema
has strict additionalProperties:false that would reject new fields, STOP and report.
