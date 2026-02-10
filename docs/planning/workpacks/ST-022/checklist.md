# ST-022 Checklist

## Acceptance Criteria

- [ ] AC-1: Caller registered when LLM_POLICY_ENABLED=true + LLM_API_KEY set
- [ ] AC-2: Caller NOT registered when API key missing (warning logged)
- [ ] AC-3: Caller NOT registered when ALLOW_PLACEHOLDERS=true (error logged)
- [ ] AC-4: All 251 existing tests pass + 5 new = 256

## DoD Items

- [ ] `llm_policy/bootstrap.py` created with `bootstrap_llm_caller()`
- [ ] Reads LLM_API_KEY, checks LLM_POLICY_ENABLED, checks ALLOW_PLACEHOLDERS
- [ ] Logs appropriate messages (info/warning/error)
- [ ] `tests/test_llm_bootstrap.py` — 5 new tests
- [ ] Tests reset global caller state (no pollution)
- [ ] HTTP caller tests still pass
- [ ] Full test suite passes (256 total)
