# ST-033 Checklist

## Acceptance Criteria

- [ ] AC-1: `POST /v1/decide` → 200 + valid response + `API-Version: v1` header
- [ ] AC-2: `POST /decide` (unversioned) → 200 (backward compat)
- [ ] AC-3: `API-Version: v1` header on all /v1 responses (including errors)
- [ ] AC-4: ADR-007 created (already done)
- [ ] AC-5: All 283 existing tests pass

## DoD

- [ ] `app/main.py` updated
- [ ] `tests/test_api_versioned.py` created (5 tests)
- [ ] `tests/test_api_decide.py` updated
- [ ] `scripts/api_sanity.py` updated
- [ ] 5 new tests pass
- [ ] 283 existing tests pass (288 total, 3 skipped)
- [ ] No modifications to forbidden paths
