# Codex PLAN Prompt — ST-030: Latency and Fallback Summary Aggregation Script

## Role
You are a senior Python developer. This is a **PLAN-only** phase: read the codebase,
confirm assumptions, and report findings. **Do NOT create or modify any files.**

## Context
We are creating `skills/observability/scripts/aggregate_metrics.py` — a script that reads
pipeline_latency.jsonl and fallback_metrics.jsonl and produces aggregate statistics.
Tests in `tests/test_aggregate_metrics.py`.

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

### 1. Read `app/logging/pipeline_latency_log.py`
Confirm record format written by `append_pipeline_latency_log`:
- Keys: command_id, trace_id, total_ms, steps (dict), llm_enabled, timestamp
- Steps dict keys: validate_command_ms, detect_intent_ms, registry_ms, core_logic_ms, validate_decision_ms
- timestamp added via `record.setdefault("timestamp", ...)`

### 2. Read `app/logging/fallback_metrics_log.py`
Confirm record format written by `append_fallback_metrics_log`:
- Keys: command_id, trace_id, intent, decision_action, llm_outcome, fallback_reason,
  deterministic_used, llm_latency_ms, components, timestamp

### 3. Read `graphs/core_graph.py` lines 354-388
Confirm the exact payloads passed to both log functions to verify field names match.

### 4. Check for naming conflicts
Run: `ls skills/observability/` — confirm doesn't exist.
Run: `ls tests/test_aggregate_metrics.py` — confirm doesn't exist.

### 5. Check existing skills structure
Read `skills/quality-eval/scripts/evaluate_golden.py` header.
Note REPO_ROOT pattern, sys.path setup. The aggregation script follows same pattern.

### 6. Check Python standard library for percentile
Confirm: `statistics.quantiles` available in Python 3.8+ but requires `n` parameter.
Our custom `_percentile` function with linear interpolation is simpler and more predictable
for testing. Confirm no external dependencies needed.

### 7. Check default log paths
- pipeline_latency: `logs/pipeline_latency.jsonl` (from DEFAULT_LOG_PATH in pipeline_latency_log.py)
- fallback_metrics: `logs/fallback_metrics.jsonl` (from DEFAULT_LOG_PATH in fallback_metrics_log.py)

## Expected Output

Report:
1. pipeline_latency record format confirmed (keys + types)
2. fallback_metrics record format confirmed (keys + types)
3. Payload field names match between core_graph and log modules
4. Naming conflicts: none / found
5. Skills script pattern confirmed
6. No external dependencies needed for percentile computation
7. Default log paths confirmed
8. Any surprises or concerns

## STOP-THE-LINE
If any of the following occur, STOP and report:
- `skills/observability/` already exists
- `tests/test_aggregate_metrics.py` already exists
- Record format differs from expected (field names mismatch)
