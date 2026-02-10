# Codex PLAN Prompt — ST-022: LLM Caller Startup Registration

## Role
You are a senior Python developer. This is a **PLAN-only** phase: read the codebase,
confirm assumptions, and report findings. **Do NOT create or modify any files.**

## Context
We are creating `llm_policy/bootstrap.py` with `bootstrap_llm_caller()` that wires
the HTTP caller (ST-021) into the runtime via `set_llm_caller()`. Tests in
`tests/test_llm_bootstrap.py`.

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

### 1. Read `llm_policy/runtime.py` — set_llm_caller/get_llm_caller
Confirm:
- `set_llm_caller(caller: LlmCaller | None) -> None` at line 24
- `get_llm_caller() -> LlmCaller | None` at line 29
- Global `_LLM_CALLER` variable
- Import path: `from llm_policy.runtime import set_llm_caller, get_llm_caller`

### 2. Read `llm_policy/http_caller.py` — create_http_caller
Confirm:
- `create_http_caller(*, api_key: str | None = None) -> HttpLlmCaller` at line 17
- Reads `LLM_API_KEY` from env if not provided
- Raises `ValueError` if no key
- Import path: `from llm_policy.http_caller import create_http_caller`

### 3. Read `llm_policy/config.py`
Confirm all config functions:
- `is_llm_policy_enabled()` — reads `LLM_POLICY_ENABLED`, default `"false"`
- `get_llm_policy_allow_placeholders()` — reads `LLM_POLICY_ALLOW_PLACEHOLDERS`, default `"false"`
- Import path: `from llm_policy.config import ...`

### 4. Check for naming conflicts
Run: `ls llm_policy/bootstrap*` — confirm doesn't exist.
Run: `ls tests/test_llm_bootstrap*` — confirm doesn't exist.

### 5. Check existing tests that use set_llm_caller
Search for `set_llm_caller` in tests/. Check if any test sets the global caller state.
This matters for test isolation.

### 6. Check logging patterns in llm_policy/
Read existing logging usage (e.g., in `runtime.py`). Confirm logger name convention:
`logging.getLogger("llm_policy")` or similar.

## Expected Output

Report:
1. set_llm_caller/get_llm_caller signatures and imports confirmed
2. create_http_caller signature and imports confirmed
3. Config functions confirmed
4. Naming conflicts: none / found
5. Existing tests using set_llm_caller: list
6. Logger name convention: confirmed
7. Any surprises or concerns

## STOP-THE-LINE
If any of the following occur, STOP and report:
- `bootstrap.py` already exists in `llm_policy/`
- `set_llm_caller` signature differs from expected
- `create_http_caller` signature differs from expected
