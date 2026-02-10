# Codex PLAN Prompt — ST-023: .env.example and LLM Configuration Documentation

## Role
You are a senior developer. This is a **PLAN-only** phase: read the codebase,
confirm assumptions, and report findings. **Do NOT create or modify any files.**

## Context
We are creating `.env.example` with all platform env vars, `docs/guides/llm-setup.md`
with LLM setup documentation, and updating `.gitignore` to include `.env`.

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

### 1. Confirm `.env.example` does not exist
Run: `ls .env.example` — confirm file does not exist.

### 2. Confirm `docs/guides/` directory does not exist
Run: `ls docs/guides/` — confirm directory does not exist.

### 3. Confirm `.env` is NOT in `.gitignore`
Run: `grep "^\.env$" .gitignore` — confirm no match (line needs to be added).

### 4. Collect all env vars from `llm_policy/config.py`
Read file. Expected:
- `LLM_POLICY_ENABLED` (default "false")
- `LLM_POLICY_PATH` (default None)
- `LLM_POLICY_PROFILE` (default "cheap")
- `LLM_POLICY_ALLOW_PLACEHOLDERS` (default "false")

### 5. Collect env vars from `llm_policy/http_caller.py`
Read file. Expected:
- `LLM_API_KEY` (no default, raises ValueError)
- `LLM_BASE_URL` (default "")

### 6. Collect env vars from `llm_policy/bootstrap.py`
Read file. Expected:
- `LLM_API_KEY` (same as http_caller)

### 7. Collect env vars from `routers/shadow_config.py`
Read file. Expected:
- `SHADOW_ROUTER_ENABLED` (default "false")
- `SHADOW_ROUTER_TIMEOUT_MS` (default "150")
- `SHADOW_ROUTER_LOG_PATH` (default "logs/shadow_router.jsonl")
- `SHADOW_ROUTER_MODE` (default "shadow")

### 8. Collect env vars from `routers/partial_trust_config.py`
Read file. Expected:
- `PARTIAL_TRUST_ENABLED` (default "false")
- `PARTIAL_TRUST_INTENT` (default "add_shopping_item")
- `PARTIAL_TRUST_SAMPLE_RATE` (default "0.01")
- `PARTIAL_TRUST_TIMEOUT_MS` (default "200")
- `PARTIAL_TRUST_PROFILE_ID` (default "")
- `PARTIAL_TRUST_RISK_LOG_PATH` (default "logs/partial_trust_risk.jsonl")

### 9. Collect env vars from `routers/assist/config.py`
Read file. List all env vars with defaults.

### 10. Collect env vars from `agent_runner/config.py`
Read file. List all env vars with defaults.

### 11. Collect env vars from `app/logging/` modules
Read logging modules. List all env vars with defaults:
- `pipeline_latency_log.py`
- `fallback_metrics_log.py`
- `shadow_router_log.py`
- `decision_log.py`
- `agent_run_log.py`
- `shadow_agent_diff_log.py`
- `partial_trust_risk_log.py`
- `assist_log.py`

### 12. Collect env vars from remaining config files
- `routers/config.py` — DECISION_ROUTER_STRATEGY
- `routers/shadow_agent_config.py` — all vars
- `agent_registry/config.py` — all vars
- `app/llm/agent_runner_client.py` — all vars

## Expected Output

Report:
1. `.env.example` does not exist: confirmed / found
2. `docs/guides/` does not exist: confirmed / found
3. `.env` NOT in `.gitignore`: confirmed / already present
4-12. Complete list of ALL env vars with: name, default value, source file
13. Any surprises or concerns (unexpected vars, naming conflicts)

## STOP-THE-LINE
If any of the following occur, STOP and report:
- `.env.example` already exists
- `docs/guides/llm-setup.md` already exists
- `.env` is already in `.gitignore`
