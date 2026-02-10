# Codex PLAN Prompt — ST-026: Quality Evaluation Script with Metrics

## Role
You are a senior Python developer. This is a **PLAN-only** phase: read the codebase,
confirm assumptions, and report findings. **Do NOT create or modify any files.**

## Context
We are creating `skills/quality-eval/scripts/evaluate_golden.py` — an evaluation script
that runs golden dataset entries through `process_command`, computes quality metrics,
and outputs a JSON report. Tests in `tests/test_quality_eval.py`.

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

### 1. Read `graphs/core_graph.py` — process_command signature
Confirm:
- `process_command(command: Dict[str, Any]) -> Dict[str, Any]` at line 228
- Returns decision dict with `action`, `payload`, `confidence`, etc.
- Uses `detect_intent(text)` at line 252
- Import path: `from graphs.core_graph import process_command, detect_intent, extract_items`

### 2. Read `graphs/core_graph.py` — extract_items function
Confirm:
- `extract_items(text: str) -> List[Dict[str, Any]]` at line 76
- Returns list of dicts with "name" key (and optional "quantity", "unit")
- Splits on comma and conjunctions ("и"/"and")

### 3. Read `graphs/core_graph.py` — detect_intent function
Confirm:
- `detect_intent(text: str) -> str` at line 56
- Returns "add_shopping_item", "create_task", or "clarify_needed"

### 4. Read golden dataset structure
Read `skills/graph-sanity/fixtures/golden_dataset.json`.
Confirm:
- 22 entries
- Each has: command_id, fixture_file, expected_intent, expected_entity_keys, expected_action
- Optional: expected_item_count, expected_item_names, difficulty, notes
- fixture_file references files in `skills/graph-sanity/fixtures/commands/`

### 5. Read a fixture command file
Read `skills/graph-sanity/fixtures/commands/buy_milk.json`.
Confirm structure matches CommandDTO schema (command_id, user_id, timestamp, text,
capabilities, context).

### 6. Read decision structure
Read `contracts/schemas/decision.schema.json`.
Confirm decision fields: decision_id, command_id, status, action, confidence, payload,
explanation, trace_id, schema_version, decision_version, created_at.
Confirm `payload.proposed_actions[].action` and `payload.proposed_actions[].payload.item.name`.

### 7. Check for naming conflicts
Run: `ls skills/quality-eval/` — confirm doesn't exist.
Run: `ls tests/test_quality_eval.py` — confirm doesn't exist.

### 8. Check existing skills structure for pattern
Read `skills/graph-sanity/scripts/run_graph_suite.py`.
Note: how it resolves REPO_ROOT, FIXTURE_DIR, loads process_command via importlib.
The evaluation script should follow a similar pattern.

### 9. Check `llm_policy/config.py` — is_llm_policy_enabled
Confirm import path and return type for detecting LLM mode.

### 10. Check side effects of process_command
Confirm that process_command writes to log files (pipeline_latency, fallback_metrics).
Tests will need to handle these side effects (monkeypatch log paths or disable logging).

## Expected Output

Report:
1. process_command signature and behavior confirmed
2. extract_items signature confirmed (returns list of dicts with "name")
3. detect_intent signature confirmed
4. Golden dataset: 22 entries, structure confirmed
5. Fixture command structure confirmed
6. Decision schema fields confirmed
7. Naming conflicts: none / found
8. Skills script pattern (importlib, REPO_ROOT) confirmed
9. is_llm_policy_enabled import path confirmed
10. Side effects: list log writes that need handling in tests
11. Any surprises or concerns

## STOP-THE-LINE
If any of the following occur, STOP and report:
- `skills/quality-eval/` already exists
- `tests/test_quality_eval.py` already exists
- `extract_items` function doesn't exist or has different signature
- Golden dataset has fewer than 20 entries
