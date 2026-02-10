# Codex PLAN Prompt — ST-021: HTTP LLM Client Implementing LlmCaller Interface

## Role
You are a senior Python developer. This is a **PLAN-only** phase: read the codebase,
confirm assumptions, and report findings. **Do NOT create or modify any files.**

## Context
We are adding a real HTTP LLM client to the `llm_policy` package. The client must
implement the `LlmCaller` callable signature (`Callable[[CallSpec, str], str]`) using
`httpx` (already a project dependency). It will be a new file `llm_policy/http_caller.py`
with unit tests in `tests/test_http_llm_client.py`.

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

### 1. Confirm LlmCaller signature and CallSpec fields
Read `llm_policy/models.py` and confirm:
- Exact `LlmCaller` type alias
- All `CallSpec` fields and their types
- Report the exact signature Codex must implement

### 2. Confirm error types
Read `llm_policy/errors.py` and confirm:
- `LlmUnavailableError` exists and its base class
- Confirm `TimeoutError` is builtin (no custom class needed)

### 3. Examine runtime.py caller injection
Read `llm_policy/runtime.py` and confirm:
- `set_llm_caller()` / `get_llm_caller()` signatures
- How caller is invoked in `_call_llm()`
- What exceptions runtime catches (`TimeoutError`, `LlmUnavailableError`, generic `Exception`)

### 4. Study existing HTTP client pattern
Read `agent_runner/yandex_client.py` and note:
- URL construction pattern (`{base_url}/chat/completions`)
- Headers pattern (`Authorization: Bearer`, `OpenAI-Project`)
- Request body format (model, messages, temperature, max_tokens)
- Response extraction (`choices[0].message.content`)
- How httpx is used (Client context manager, timeout, raise_for_status)

### 5. Verify httpx is available
Run: `rg "httpx" requirements*.txt setup.cfg pyproject.toml` or check installed packages.
Confirm httpx version available.

### 6. Check for naming conflicts
Run: `ls llm_policy/` — confirm `http_caller.py` does not exist.
Run: `ls tests/test_http*` — confirm `test_http_llm_client.py` does not exist.

### 7. Review existing test patterns
Read `tests/test_llm_policy_runtime.py` to understand:
- How `StubCaller` is structured (for reference, not reuse)
- How `monkeypatch` is used for env vars
- Import patterns (sys.path handling)

### 8. Check CallSpec.base_url usage
Run: `rg "base_url" llm_policy/` — check if any existing code sets `base_url` in CallSpec.
Check `llm-policy.yaml` — does any route have `base_url` set? (Expected: no, it uses `project` instead.)
This confirms the HTTP caller must fallback to `LLM_BASE_URL` env var when `spec.base_url` is None.

## Expected Output

Report findings as a structured list:
1. LlmCaller exact signature: `...`
2. CallSpec fields: `...`
3. LlmUnavailableError base class: `...`
4. Runtime error handling: catches `TimeoutError`, `LlmUnavailableError`, `Exception`
5. httpx version: `...`
6. Naming conflicts: none / found
7. base_url in YAML: present / absent
8. Any surprises or concerns

## STOP-THE-LINE
If you find anything unexpected (e.g., `http_caller.py` already exists, LlmCaller
signature differs, httpx not available), **STOP and report** — do not proceed with
assumptions.
