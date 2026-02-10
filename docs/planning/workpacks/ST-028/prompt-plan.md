# Codex PLAN Prompt — ST-028: Pipeline-Wide Latency Instrumentation

## Role
You are a senior Python developer. This is a **PLAN-only** phase: read the codebase,
confirm assumptions, and report findings. **Do NOT create or modify any files.**

## Context
We are adding pipeline-wide latency instrumentation to `graphs/core_graph.py`.
A new logging module `app/logging/pipeline_latency_log.py` will follow the existing
pattern (shadow_router_log.py). Tests in `tests/test_pipeline_latency.py`.

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

### 1. Read `graphs/core_graph.py` — `process_command()` function
Confirm:
- Function signature and line range
- Steps: schema validation, detect_intent, registry annotation, core logic, decision validation
- Return value is a single dict (decision)
- No existing timing or latency logic

### 2. Read existing logging pattern
Read `app/logging/shadow_router_log.py` and confirm pattern:
- `DEFAULT_LOG_PATH`, `_ensure_parent`, `resolve_log_path`, `append_*_log`
- Env var naming convention for path and enable/disable
- JSONL format with `ensure_ascii=False`

### 3. Read `app/logging/__init__.py`
Confirm it's empty or minimal — no barrel exports that auto-import all modules.

### 4. Check `llm_policy/config.py`
Confirm `is_llm_policy_enabled()` exists and returns bool.
Note the import path: `from llm_policy.config import is_llm_policy_enabled`.

### 5. Check existing tests that call `process_command()`
Read `tests/test_graph_execution.py` and `tests/test_core_graph_registry_gate.py`.
Confirm they will not be affected by adding timing to process_command().
Check if they use any monkeypatching of process_command or env vars.

### 6. Check for naming conflicts
Run: `ls tests/test_pipeline_latency*` — confirm test file doesn't exist.
Run: `ls app/logging/pipeline_latency*` — confirm module doesn't exist.

### 7. Verify `time` module availability
Confirm `time.monotonic()` is available in Python 3.x (stdlib). No new dependencies needed.

### 8. Check import safety
Verify that importing `from app.logging.pipeline_latency_log import ...` inside
`graphs/core_graph.py:process_command()` won't cause circular imports.
Trace: `core_graph.py` ← `app/logging/*` — do any logging modules import from `graphs/`?

## Expected Output

Report:
1. process_command() line range and step boundaries confirmed
2. Logging pattern confirmed (env vars, JSONL format)
3. `__init__.py` state: empty / minimal
4. `is_llm_policy_enabled()` import path confirmed
5. Existing tests: will/won't be affected
6. Naming conflicts: none / found
7. time.monotonic: available
8. Circular import risk: none / found
9. Any surprises or concerns

## STOP-THE-LINE
If any of the following occur, STOP and report:
- `process_command()` already has timing/latency logic
- Logging modules import from `graphs/`
- `app/logging/__init__.py` has barrel exports that could cause issues
