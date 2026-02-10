# Checklist — ST-024: Smoke Test -- Real LLM Round-Trip

## Acceptance Criteria

- [ ] AC-1: Smoke test passes with valid LLM credentials (conditional test, verified manually)
- [ ] AC-2: Fallback on invalid credentials — deterministic fallback, no crash
- [ ] AC-3: Kill-switch prevents any HTTP call
- [ ] AC-4: Tests skipped gracefully in CI without credentials
- [ ] AC-5: All 268 existing tests pass (full suite green)

## DoD

- [ ] `tests/test_llm_integration_smoke.py` created with ~5 tests
- [ ] 2 always-run tests pass
- [ ] 3 conditional tests skip without `LLM_API_KEY`
- [ ] No invariant files modified
- [ ] No secrets in test code
- [ ] No regression in existing tests

## Verification

```bash
source .venv/bin/activate && python3 -m pytest tests/test_llm_integration_smoke.py -v
source .venv/bin/activate && python3 -m pytest --tb=short -q
```
