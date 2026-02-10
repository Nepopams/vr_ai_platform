# Codex PLAN Prompt — ST-029: Unified Fallback Metrics Logging

## Role
You are a senior Python developer. This is a **PLAN-only** phase: read the codebase,
confirm assumptions, and report findings. **Do NOT create or modify any files.**

## Context
We are adding a unified fallback metrics JSONL log to `graphs/core_graph.py:process_command()`.
A new logging module `app/logging/fallback_metrics_log.py` follows the existing pattern.
Tests in `tests/test_fallback_metrics.py`.

Note: `process_command()` was recently updated (ST-028) to include pipeline latency
instrumentation. The fallback metrics block goes right after the latency block.

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

### 1. Read `graphs/core_graph.py` — current `process_command()` function
Confirm the function now includes (from ST-028):
- `import time` at line 229
- Import of `pipeline_latency_log` at lines 231-234
- `is_llm_policy_enabled` imported inside the latency `if` block at line 349
- Latency record emission at lines 347-365
- `return decision` at line 367

Confirm that fallback metrics can be added between the latency block and `return`.

### 2. Read existing logging pattern
Read `app/logging/partial_trust_risk_log.py` — confirm it has the privacy comment:
`# NO RAW USER OR LLM TEXT — PRIVACY GUARANTEE.`
This comment should be replicated in the fallback metrics logger.

### 3. Verify `is_llm_policy_enabled` import location
Currently at line 349 inside `if is_pipeline_latency_log_enabled():`.
Confirm moving it to function-level (alongside other imports at lines 231-234)
will not break anything. Both the latency and fallback blocks need it.

### 4. Check for naming conflicts
Run: `ls tests/test_fallback*` — confirm test file doesn't exist.
Run: `ls app/logging/fallback*` — confirm module doesn't exist.

### 5. Read existing tests for process_command
Check `tests/test_pipeline_latency.py` — confirm these tests use monkeypatching
for `PIPELINE_LATENCY_LOG_PATH` and `PIPELINE_LATENCY_LOG_ENABLED`.
New fallback tests will follow the same pattern with `FALLBACK_METRICS_LOG_PATH`
and `FALLBACK_METRICS_LOG_ENABLED`.

### 6. Confirm privacy requirements
Search for "raw" or "text" or "prompt" in existing logging modules to understand
which fields are safe. Confirm: no `text`, `prompt`, or `raw_output` fields in fallback records.

## Expected Output

Report:
1. process_command() current structure (post ST-028) confirmed
2. Privacy comment pattern confirmed
3. is_llm_policy_enabled refactor safe: yes/no
4. Naming conflicts: none / found
5. Test pattern confirmed (monkeypatch env vars + tmp_path)
6. Privacy fields to exclude confirmed
7. Any surprises or concerns

## STOP-THE-LINE
If any of the following occur, STOP and report:
- process_command() structure differs from expected (post ST-028)
- Logging modules have changed since last review
- Any file we plan to create already exists
