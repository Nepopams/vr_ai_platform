# ST-013 — AC / DoD Verification Checklist

## Acceptance Criteria

- [ ] AC-1: Clarify prompt includes known fields (intent, items) and missing fields context
- [ ] AC-2: `_CLARIFY_SCHEMA` constrains missing_fields to enum of known identifiers
- [ ] AC-3: Safety gate rejects questions irrelevant to missing_fields
- [ ] AC-5: Assist disabled -> default baseline questions (unchanged)
- [ ] AC-6: No raw text in logs
- [ ] AC-7: All 182 existing tests pass

## DoD

- [ ] Code updated: `routers/assist/runner.py` (5 functions modified)
- [ ] Tests created: `tests/test_clarify_prompt.py` (~8 tests)
- [ ] All existing tests pass (182)
- [ ] New tests pass
- [ ] No secrets in changed files
- [ ] Invariants: v2.py, core_graph.py, schemas NOT modified
