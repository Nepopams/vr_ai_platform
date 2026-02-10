# ST-024: Smoke Test -- Real LLM Round-Trip Through Shadow Router

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
| Shadow router | `routers/shadow_router.py` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

ST-021 creates the HTTP caller, ST-022 wires it to startup. We need an integration
test that proves the full path works end-to-end: shadow router -> HTTP caller -> LLM -> response.
The test must be conditional (skipped when no LLM credentials).

## User Value

As a platform developer, I want an integration test that proves the full path from
`start_shadow_router()` through the real HTTP caller to the LLM and back, so that
I can verify end-to-end connectivity before production.

## Scope

### In scope

- New test module `tests/test_llm_integration_smoke.py`
- Tests marked `@pytest.mark.skipif(not LLM_API_KEY)` -- skipped without credentials
- Verify: shadow router calls real LLM, gets response, logs to JSONL
- Verify: fallback works when API key is intentionally invalid
- Verify: kill-switch (`LLM_POLICY_ENABLED=false`) prevents any LLM call
- Run at least 3 golden dataset commands through full pipeline with real LLM

### Out of scope

- Performance benchmarks
- Automated CI execution with real LLM (requires secrets)
- Testing all golden dataset entries (that is ST-026)

---

## Acceptance Criteria

### AC-1: Smoke test passes with valid LLM credentials
```
Given valid LLM_API_KEY and LLM_BASE_URL
When test_llm_integration_smoke.py runs
Then at least one real LLM call succeeds and shadow router log is written
```

### AC-2: Fallback on invalid credentials
```
Given invalid LLM_API_KEY
When pipeline processes a command
Then deterministic fallback produces a valid DecisionDTO
And no crash occurs
```

### AC-3: Kill-switch prevents calls
```
Given LLM_POLICY_ENABLED=false
When pipeline processes a command
Then no HTTP call is made to any LLM endpoint
```

### AC-4: Test is skipped in CI without credentials
```
Given LLM_API_KEY is not set
When pytest runs
Then test_llm_integration_smoke.py tests are skipped (not failed)
```

### AC-5: All 228 existing tests pass
```
Given the test suite
When ST-024 changes are applied
Then all 228 tests pass
```

---

## Test Strategy

### Integration tests (~5 new, conditional)
- `test_real_llm_shadow_router_roundtrip`
- `test_fallback_on_invalid_credentials`
- `test_killswitch_prevents_llm_calls`
- `test_golden_commands_with_real_llm`
- `test_shadow_log_written_on_success`

### Regression
- Full test suite: 228 tests must pass

---

## Code Touchpoints

| File | Change |
|------|--------|
| `tests/test_llm_integration_smoke.py` | New: conditional integration tests |

---

## Dependencies

- ST-021, ST-022 (HTTP caller + bootstrap must exist)
