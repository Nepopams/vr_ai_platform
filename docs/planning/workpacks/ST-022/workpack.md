# Workpack — ST-022: LLM Caller Startup Registration

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-008/epic.md` |
| Story | `docs/planning/epics/EP-008/stories/ST-022-llm-caller-bootstrap.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q4-production-hardening.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

## Outcome

A `bootstrap_llm_caller()` function that reads env vars, creates the HTTP caller (ST-021), and registers it via `set_llm_caller()`. Platform switches from stubs to real LLM by setting environment variables.

## Acceptance Criteria Summary

- AC-1: Caller registered when `LLM_POLICY_ENABLED=true` + `LLM_API_KEY` set
- AC-2: Caller NOT registered when API key missing (warning logged)
- AC-3: Caller NOT registered when `LLM_POLICY_ALLOW_PLACEHOLDERS=true` (error logged)
- AC-4: All 251 existing tests pass + 5 new = 256

## Files to Change

| File | Action | Description |
|------|--------|-------------|
| `llm_policy/bootstrap.py` | NEW | `bootstrap_llm_caller()` function |
| `tests/test_llm_bootstrap.py` | NEW | 5 unit tests |

## Files NOT Modified (invariants)

- `llm_policy/runtime.py` — DO NOT CHANGE (set_llm_caller/get_llm_caller used as-is)
- `llm_policy/http_caller.py` — DO NOT CHANGE (create_http_caller used as-is)
- `llm_policy/config.py` — DO NOT CHANGE (is_llm_policy_enabled etc. used as-is)
- `llm_policy/models.py` — DO NOT CHANGE
- `graphs/core_graph.py` — DO NOT CHANGE

## Implementation Plan

### Step 1: Create `llm_policy/bootstrap.py`

Key design:
- Import `is_llm_policy_enabled`, `get_llm_policy_allow_placeholders` from `llm_policy.config`
- Import `create_http_caller` from `llm_policy.http_caller`
- Import `set_llm_caller` from `llm_policy.runtime`
- Read env vars: `LLM_API_KEY`, `LLM_POLICY_ENABLED`, `LLM_POLICY_ALLOW_PLACEHOLDERS`
- Logic:
  1. If not `is_llm_policy_enabled()` → log info "LLM policy disabled, skipping bootstrap", return
  2. If `get_llm_policy_allow_placeholders()` → log error "Cannot register real caller with placeholders enabled", return
  3. Read `LLM_API_KEY` from env. If not set → log warning "LLM_API_KEY not set, caller not registered", return
  4. Call `create_http_caller(api_key=key)` → `set_llm_caller(caller)` → log info "LLM caller registered"

### Step 2: Create `tests/test_llm_bootstrap.py`

5 unit tests using monkeypatch:

1. `test_bootstrap_registers_caller_with_all_vars` — set all env vars, call bootstrap, verify `get_llm_caller()` is not None
2. `test_bootstrap_skips_without_api_key` — no LLM_API_KEY, verify get_llm_caller() is None
3. `test_bootstrap_skips_when_disabled` — `LLM_POLICY_ENABLED=false`, verify get_llm_caller() is None
4. `test_bootstrap_rejects_placeholder_mode` — `LLM_POLICY_ALLOW_PLACEHOLDERS=true`, verify get_llm_caller() is None
5. `test_bootstrap_logs_warning_on_missing_vars` — no LLM_API_KEY, verify warning logged (caplog)

Test pattern:
- Each test must reset caller state: call `set_llm_caller(None)` in setup/teardown
- Use monkeypatch for env vars
- Use `caplog` fixture for log assertions

## Verification Commands

```bash
# New bootstrap tests
source .venv/bin/activate && python3 -m pytest tests/test_llm_bootstrap.py -v

# HTTP caller tests still pass
source .venv/bin/activate && python3 -m pytest tests/test_http_llm_client.py -v

# Full test suite
source .venv/bin/activate && python3 -m pytest --tb=short -q
```

## Risks & Rollback

| Risk | Mitigation |
|------|-----------|
| Test pollution from set_llm_caller global state | Each test resets with set_llm_caller(None) |
| Real API key in test env | Tests use fake key ("test-key-xxx"), never call real LLM |
| Bootstrap called in test imports | bootstrap is explicit call, not auto-import |

Rollback: delete `llm_policy/bootstrap.py` and `tests/test_llm_bootstrap.py`.
