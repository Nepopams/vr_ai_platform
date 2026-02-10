# Codex PLAN Prompt (continuation #2) — ST-024: Smoke Test -- Real LLM Round-Trip

## Role
You are a senior Python developer planning an integration smoke test module for LLM round-trip through the shadow router.

## Goal
Continue the PLAN. Tasks 1–3 are done. Task 2b confirmed: loader does NOT substitute env vars — `${YANDEX_FOLDER_ID}` stays as-is, validation fails.

**Final strategy (approved by PO):** Use a custom test YAML without placeholders, loaded via `LLM_POLICY_PATH` env var. This preserves the full production path including `bootstrap_llm_caller()`.

Complete Tasks 4–8 below. **NO file modifications allowed.**

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

**Confirmed from Tasks 1–3 + 2b:**

- Shadow router synchronous pattern: `monkeypatch.setattr(shadow_router, "_submit_shadow_task", lambda payload: shadow_router._run_shadow_router(payload))`
- Env flags: `SHADOW_ROUTER_ENABLED`, `SHADOW_ROUTER_LOG_PATH`, `LLM_POLICY_ENABLED`
- YAML routing has `project: "${YANDEX_FOLDER_ID}"` — placeholder, NO env var substitution in loader
- `_validate_no_placeholders()` rejects `${...}` when `allow_placeholders=False`
- `HttpLlmCaller._build_url()` uses `spec.base_url` or `LLM_BASE_URL` env var → `{base}/chat/completions`
- YAML routing has NO `base_url` field → `LLM_BASE_URL` env var is mandatory

**Final strategy: Custom test YAML via `LLM_POLICY_PATH`**

Tests will create a minimal YAML in `tmp_path` without `${...}` placeholders:
```yaml
schema_version: 1
compat:
  adr: "ADR-003"
  note: "smoke-test"
profiles:
  cheap:
    description: "test profile"
tasks:
  shopping_extraction:
    description: "test task"
routing:
  shopping_extraction:
    cheap:
      provider: "openai_compatible"
      model: "test-model"
      temperature: 0.2
      max_tokens: 256
      timeout_ms: 5000
fallback_chain: []
```

Then: `monkeypatch.setenv("LLM_POLICY_PATH", str(yaml_path))`

This way:
- `allow_placeholders=false` (default) → validation passes (no placeholders)
- `bootstrap_llm_caller()` works fully (all 3 guards pass)
- Full production code path tested

**Test categories:**
- 2 always-run: fallback (invalid creds + unreachable URL) and kill-switch
- 3 conditional: skip without `LLM_API_KEY` + `LLM_BASE_URL`

For conditional real-LLM tests, the custom YAML uses `provider: "openai_compatible"` (works with any OpenAI-compatible endpoint). The `model` field will need to match the real provider's model name. PLAN should check if `model` in the YAML can be overridden via env var or if it's hardcoded from the routing entry.

---

## Tasks

### Task 4: Confirm bootstrap guards
Read `llm_policy/bootstrap.py`. List the 3 guard clauses and their exact behavior:
1. `is_llm_policy_enabled()` — when does it skip?
2. `get_llm_policy_allow_placeholders()` — when does it reject?
3. `LLM_API_KEY` — empty/missing behavior?

Confirm: with custom YAML (no placeholders) + `LLM_POLICY_ENABLED=true` + `LLM_POLICY_ALLOW_PLACEHOLDERS=false` + `LLM_API_KEY=some-key`, does `bootstrap_llm_caller()` successfully register the caller?

### Task 5: Confirm error path through shadow router
Trace the error path when `HttpLlmCaller.__call__` raises `LlmUnavailableError` (e.g., connection refused to `http://localhost:1`):

1. `_run_profile()` in `llm_policy/runtime.py` — does it catch `LlmUnavailableError`? What does it return?
2. `run_task_with_policy()` — what `TaskRunResult` is returned?
3. `extract_shopping_item_name()` in `llm_policy/tasks.py` — what `ExtractionResult` is returned?
4. `_build_suggestion()` in `routers/shadow_router.py` — what `RouterSuggestion` fields?
5. `_run_shadow_router()` — does the outer `except Exception` on line 113 catch? Or does the error propagate through `_build_suggestion` and get handled as normal flow?

Confirm: does `_run_shadow_router()` catch ALL exceptions (line 113)?

### Task 6: Confirm fixture file structure
Read these 3 fixture files:
- `skills/graph-sanity/fixtures/commands/buy_milk.json`
- `skills/graph-sanity/fixtures/commands/clean_bathroom.json`
- `skills/graph-sanity/fixtures/commands/unknown_intent.json`

For each, confirm:
- JSON structure matches what `process_command()` expects
- All required fields present: `command_id`, `user_id`, `timestamp`, `text`, `capabilities`, `context`

### Task 7: Check for naming conflicts
```
ls tests/test_llm_integration*
```
Verify `tests/test_llm_integration_smoke.py` does not exist.

### Task 8: Confirm shadow router log keys
Read `routers/shadow_router.py` lines 156-183 (`_log_shadow_result`) and `app/logging/shadow_router_log.py` (`append_shadow_router_log`).

List ALL keys that appear in a shadow router JSONL log record, including `timestamp` added by the logging module. These keys will be asserted in the log content test.

---

## STOP-THE-LINE
If any of the following occur, STOP and report:
- `_run_shadow_router()` does NOT catch all exceptions (would need different test design)
- Custom YAML approach incompatible with `LlmPolicyLoader.load()` (schema mismatch etc.)
- Fixture files missing or incompatible with `process_command()`
