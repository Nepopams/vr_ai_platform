# ST-022: LLM Caller Startup Registration and Env-Var Configuration

**Epic:** EP-008 (Real LLM Client Integration)
**Status:** Ready
**Flags:** contract_impact=no, adr_needed=none, diagrams_needed=none

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-008/epic.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q4-production-hardening.md` |
| LLM runtime | `llm_policy/runtime.py` |
| LLM config | `llm_policy/config.py` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

The runtime exposes `set_llm_caller()` for injecting a caller at startup. ST-021 creates
the HTTP caller. This story wires the two together: read env vars, create the caller,
and register it at application startup.

## User Value

As a platform operator, I want the real LLM caller to be automatically registered at
startup when `LLM_POLICY_ENABLED=true` and `LLM_API_KEY` is set, so that the platform
can switch from stubs to real LLM by changing environment variables.

## Scope

### In scope

- New module `llm_policy/bootstrap.py` with `bootstrap_llm_caller()` function
- Reads `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_PROVIDER` from env vars
- If all required vars set: creates HTTP caller (ST-021) and calls `set_llm_caller()`
- If not: logs warning, leaves caller as None (existing fallback behavior)
- Validation: `LLM_POLICY_ALLOW_PLACEHOLDERS` must be `false` when real caller active

### Out of scope

- Hot-reloading of config
- Multiple simultaneous callers
- Health-check endpoint for LLM connectivity

---

## Acceptance Criteria

### AC-1: Caller registered when env vars present
```
Given LLM_POLICY_ENABLED=true, LLM_API_KEY=<key>, LLM_BASE_URL=<url>
When bootstrap_llm_caller() runs
Then get_llm_caller() returns the HTTP caller instance
```

### AC-2: Caller not registered when API key missing
```
Given LLM_POLICY_ENABLED=true, LLM_API_KEY not set
When bootstrap_llm_caller() runs
Then get_llm_caller() returns None
And a warning is logged
```

### AC-3: Placeholder validation
```
Given LLM_POLICY_ENABLED=true, LLM_API_KEY set, LLM_POLICY_ALLOW_PLACEHOLDERS=true
When bootstrap_llm_caller() runs
Then it logs an error and does NOT register the caller
```

### AC-4: All 228 existing tests pass
```
Given the test suite (no real LLM env vars)
When ST-022 changes are applied
Then all 228 tests pass and new tests also pass
```

---

## Test Strategy

### Unit tests (~5 new in `tests/test_llm_bootstrap.py`)
- `test_bootstrap_registers_caller_with_all_vars`
- `test_bootstrap_skips_without_api_key`
- `test_bootstrap_skips_when_disabled`
- `test_bootstrap_rejects_placeholder_mode`
- `test_bootstrap_logs_warning_on_missing_vars`

### Regression
- Full test suite: 228 tests must pass

---

## Code Touchpoints

| File | Change |
|------|--------|
| `llm_policy/bootstrap.py` | New: bootstrap_llm_caller() |
| `tests/test_llm_bootstrap.py` | New: unit tests |

---

## Dependencies

- ST-021 (HTTP caller must exist)
- Blocks: ST-023, ST-024
