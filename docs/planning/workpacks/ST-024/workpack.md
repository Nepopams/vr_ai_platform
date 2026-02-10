# Workpack — ST-024: Smoke Test -- Real LLM Round-Trip Through Shadow Router

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-008/epic.md` |
| Story spec | `docs/planning/epics/EP-008/stories/ST-024-smoke-test-real-llm.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q4-production-hardening.md` |
| Sprint | `docs/planning/sprints/S08/sprint.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

A new integration test module `tests/test_llm_integration_smoke.py` that:
- Proves the full path from `start_shadow_router()` through `HttpLlmCaller` to a real LLM and back when credentials are available.
- Verifies deterministic fallback works when credentials are invalid.
- Verifies the kill-switch (`LLM_POLICY_ENABLED=false`) prevents any HTTP call to an LLM endpoint.
- Skips real-LLM tests gracefully in CI without credentials.

---

## Acceptance Criteria (from story spec)

| AC | Description | How to verify |
|----|-------------|---------------|
| AC-1 | Smoke test passes with valid LLM credentials | Run with `LLM_API_KEY` + `LLM_BASE_URL` set → at least one real LLM call succeeds, shadow log written |
| AC-2 | Fallback on invalid credentials | Set invalid key → `process_command()` returns valid DecisionDTO, no crash |
| AC-3 | Kill-switch prevents calls | `LLM_POLICY_ENABLED=false` → no HTTP call made (patch assertion) |
| AC-4 | Tests skipped in CI without credentials | Without `LLM_API_KEY` → tests skipped (not failed) |
| AC-5 | All 268 existing tests pass | Full test suite green |

---

## Architecture and Design Decisions

### Two categories of tests

1. **Real-LLM tests** (skip without credentials):
   - Marked with `@pytest.mark.skipif(not HAS_LLM_CREDENTIALS, ...)` where `HAS_LLM_CREDENTIALS = bool(os.getenv("LLM_API_KEY") and os.getenv("LLM_BASE_URL"))`
   - These test the full round-trip: bootstrap → shadow router → HTTP caller → real LLM → response → JSONL log
   - 3 tests: roundtrip, golden commands (3 entries), shadow log verification

2. **Always-run tests** (no real credentials needed):
   - Fallback test: invalid key + unreachable URL → shadow router logs error, `process_command()` returns valid decision
   - Kill-switch test: `LLM_POLICY_ENABLED=false` → httpx.Client never instantiated

### Shadow router synchronous execution

Existing test pattern from `tests/test_shadow_router.py`: replace `_submit_shadow_task` with synchronous call to `_run_shadow_router` (line 91). This avoids thread pool timing issues in tests.

### Fixture and cleanup

- `_reset_caller` autouse fixture (from `tests/test_llm_bootstrap.py`): resets global `set_llm_caller(None)` before/after each test.
- Shadow router log directed to `tmp_path` via `SHADOW_ROUTER_LOG_PATH` env var.
- LLM policy env vars set per-test via `monkeypatch`.

### Command helper

Use structure matching `skills/graph-sanity/fixtures/commands/buy_milk.json`:
```python
def _make_command(text="Купи молоко"):
    return {
        "command_id": "cmd-smoke-001",
        "user_id": "user-smoke",
        "timestamp": "2026-02-01T10:00:00+00:00",
        "text": text,
        "capabilities": ["start_job", "propose_create_task", "propose_add_shopping_item", "clarify"],
        "context": {
            "household": {
                "household_id": "house-smoke",
                "members": [{"user_id": "user-smoke", "display_name": "Test"}],
                "shopping_lists": [{"list_id": "list-1", "name": "Продукты"}],
            },
            "defaults": {"default_list_id": "list-1"},
        },
    }
```

### Key code paths

| Path | What it tests |
|------|--------------|
| `start_shadow_router()` → `_run_shadow_router()` → `_build_suggestion()` → `extract_shopping_item_name()` → `run_task_with_policy()` → `HttpLlmCaller.__call__()` | Full LLM round-trip |
| `process_command()` (deterministic) | Produces valid DecisionDTO regardless of LLM state |
| `is_llm_policy_enabled()` → `False` → shadow router skips at line 83 | Kill-switch |
| `bootstrap_llm_caller()` with invalid key → caller registered → HTTP call fails → `LlmUnavailableError` caught | Fallback |

### LLM policy YAML and placeholders

- YAML (`llm_policy/llm-policy.yaml`) has `project: "${YANDEX_FOLDER_ID}"` — a placeholder.
- `bootstrap_llm_caller()` guard: `get_llm_policy_allow_placeholders()` must be `false` (default).
- For real LLM tests: `LLM_POLICY_ALLOW_PLACEHOLDERS=false`, `YANDEX_FOLDER_ID` must be set if using `yandex_ai_studio` provider.
- PLAN phase must confirm how the loader handles placeholders when `allow_placeholders=false` and whether `base_url` in YAML is None (it's not in the YAML — comes from `LLM_BASE_URL` env var via `_build_url()`).

---

## Files to Change

| File | Change | New/Modify |
|------|--------|------------|
| `tests/test_llm_integration_smoke.py` | New: integration smoke test module (~5 tests) | New |

### Invariants (DO NOT CHANGE)

- `llm_policy/http_caller.py`
- `llm_policy/bootstrap.py`
- `llm_policy/runtime.py`
- `llm_policy/config.py`
- `llm_policy/tasks.py`
- `routers/shadow_router.py`
- `graphs/core_graph.py`
- `tests/test_shadow_router.py`
- `tests/test_http_llm_client.py`
- `tests/test_llm_bootstrap.py`

---

## Implementation Plan

### Step 1: Create test module with helpers and fixtures

- `_make_command(text)` helper
- `_read_log(path)` helper (from test_shadow_router.py pattern)
- `_reset_caller` autouse fixture
- `HAS_LLM_CREDENTIALS` constant + `requires_llm` skip marker
- sys.path setup (BASE_DIR pattern from other tests)

### Step 2: Always-run test — fallback on invalid credentials (AC-2)

- Set `LLM_POLICY_ENABLED=true`, `LLM_POLICY_ALLOW_PLACEHOLDERS=false`
- Set `LLM_API_KEY=invalid-key-for-testing`, `LLM_BASE_URL=http://localhost:1`
- `bootstrap_llm_caller()` → caller registered (invalid but callable)
- Run shadow router synchronously → expect error logged (connection refused)
- Run `process_command()` → valid DecisionDTO returned, no crash

### Step 3: Always-run test — kill-switch prevents LLM calls (AC-3)

- Set `LLM_POLICY_ENABLED=false`
- Patch `httpx.Client` to raise `AssertionError("HTTP should not be called")`
- Run shadow router synchronously → status=skipped, error_type=policy_disabled
- Verify httpx.Client was never instantiated

### Step 4: Conditional test — real LLM roundtrip (AC-1, requires credentials)

- Skip if no `LLM_API_KEY`/`LLM_BASE_URL`
- Bootstrap real caller
- Run shadow router synchronously with "Купи молоко"
- Verify shadow log written with status != "skipped"

### Step 5: Conditional test — golden commands with real LLM (AC-1)

- Skip if no credentials
- Load 3 fixture files: `buy_milk.json`, `clean_bathroom.json`, `unknown_intent.json`
- Run each through shadow router synchronously
- Verify each produces a log entry

### Step 6: Conditional test — shadow log content verification (AC-1)

- Skip if no credentials
- Run shadow router with real LLM
- Verify JSONL log contains required keys (same set as test_shadow_router.py line 117-136)

---

## Verification Commands

```bash
# ST-024 tests (always-run tests, skip real-LLM tests without creds)
source .venv/bin/activate && python3 -m pytest tests/test_llm_integration_smoke.py -v

# Shadow router and bootstrap tests still pass
source .venv/bin/activate && python3 -m pytest tests/test_shadow_router.py tests/test_llm_bootstrap.py tests/test_http_llm_client.py -v

# Full test suite
source .venv/bin/activate && python3 -m pytest --tb=short -q
```

---

## Tests

| Test | Category | What it verifies |
|------|----------|-----------------|
| `test_fallback_on_invalid_credentials` | Always-run | AC-2: invalid key → error logged, `process_command()` returns valid decision |
| `test_killswitch_prevents_llm_calls` | Always-run | AC-3: `LLM_POLICY_ENABLED=false` → no HTTP calls, shadow router skips |
| `test_real_llm_shadow_router_roundtrip` | Conditional | AC-1: full LLM round-trip through shadow router |
| `test_golden_commands_with_real_llm` | Conditional | AC-1: 3 golden commands produce log entries |
| `test_shadow_log_written_on_success` | Conditional | AC-1: JSONL log has required keys |

Expected: ~5 new tests. 2 always-run, 3 conditional (skipped without creds).

---

## DoD Checklist

- [ ] `tests/test_llm_integration_smoke.py` created
- [ ] 2 always-run tests pass in all environments
- [ ] 3 conditional tests skip gracefully without `LLM_API_KEY`
- [ ] No existing tests broken (268 tests still pass)
- [ ] No secrets, raw user text, or raw LLM output in test code
- [ ] No changes to invariant files

---

## Risks

| Risk | Mitigation |
|------|-----------|
| Fallback test flaky due to network timing (connecting to localhost:1) | Connection to unreachable port fails immediately with `ConnectError`, no real delay |
| Real-LLM tests never run in our pipeline (no creds) | Accepted — manual verification. Always-run tests cover the critical invariants |
| YAML placeholders (`${YANDEX_FOLDER_ID}`) affect loader | PLAN phase must confirm loader behavior; tests may need `LLM_POLICY_PATH` override |

---

## Rollback

Delete `tests/test_llm_integration_smoke.py`. No other files modified.
