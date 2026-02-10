# Codex PLAN Prompt — ST-031: Observability Documentation and Runbook

## Role
You are a senior technical writer creating operator-facing documentation for platform observability.

## Goal
Verify all log schemas, env vars, and aggregation script behavior before generating the guide. **NO file modifications allowed.**

## Allowed commands
- `ls`, `find`
- `cat`, `head`, `tail`
- `rg` / `grep`
- `sed -n`
- `git status`, `git diff` (read-only)

## Forbidden
- Any file edits/writes/moves/deletes
- Any network access
- Package install / system changes
- `git commit`, `git push`, migrations, DB ops

## Context

**Story:** Create `docs/guides/observability.md` documenting all JSONL logs, env vars, and the aggregation script.

**5 primary log types:**
1. Pipeline latency — `app/logging/pipeline_latency_log.py` → `logs/pipeline_latency.jsonl`
2. Fallback metrics — `app/logging/fallback_metrics_log.py` → `logs/fallback_metrics.jsonl`
3. Shadow router — `app/logging/shadow_router_log.py` → `logs/shadow_router.jsonl`
4. Assist — `app/logging/assist_log.py` → `logs/assist.jsonl`
5. Partial trust risk — `app/logging/partial_trust_risk_log.py` → `logs/partial_trust_risk.jsonl`

**Aggregation script:** `skills/observability/scripts/aggregate_metrics.py`

**Existing guides:** `docs/guides/llm-setup.md` (151 lines), `docs/guides/golden-dataset.md` (190 lines).

---

## Tasks

### Task 1: Confirm pipeline latency log schema
Read `app/logging/pipeline_latency_log.py` and `graphs/core_graph.py` (the caller).
List:
1. All record keys written to `pipeline_latency.jsonl`.
2. The `steps` dict structure (which step names).
3. Env vars: `PIPELINE_LATENCY_LOG_ENABLED`, `PIPELINE_LATENCY_LOG_PATH` defaults.

### Task 2: Confirm fallback metrics log schema
Read `app/logging/fallback_metrics_log.py` and its caller in `graphs/core_graph.py`.
List:
1. All record keys written to `fallback_metrics.jsonl`.
2. Possible values for `llm_outcome`.
3. Env vars and defaults.

### Task 3: Confirm shadow router log schema
Read `app/logging/shadow_router_log.py` and `routers/shadow_router.py` (caller, `_log_shadow_result`).
List all 17 keys in a shadow router log record.

### Task 4: Confirm assist log schema
Read `app/logging/assist_log.py` and `routers/assist/runner.py` (the caller).
List typical record keys.

### Task 5: Confirm partial trust risk log schema
Read `app/logging/partial_trust_risk_log.py` and its caller (grep for `append_partial_trust_risk_log`).
List typical record keys and privacy guarantees.

### Task 6: Confirm aggregation script output format
Read `skills/observability/scripts/aggregate_metrics.py`.
List:
1. Exact output JSON structure (keys at each level).
2. Percentile computation method.
3. How missing files are handled.

### Task 7: Grep all logging env vars
```
rg "os\.getenv|os\.environ" app/logging/ .env.example
```
Build the complete env var reference table for the guide.

### Task 8: Confirm docs/guides/ has no observability.md
```
ls docs/guides/
```
No naming conflict.

---

## STOP-THE-LINE
If any of the following occur, STOP and report:
- Log schemas differ from what's documented in the workpack
- Aggregation script has undocumented dependencies
- `docs/guides/observability.md` already exists
