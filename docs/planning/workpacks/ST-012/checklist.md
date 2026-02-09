# ST-012 — AC / DoD Verification Checklist

## Acceptance Criteria

- [ ] AC-1: Unknown intent -> `missing_fields=["intent"]` in clarify decision
- [ ] AC-2: No start_job capability -> `missing_fields=["capability.start_job"]` in clarify decision
- [ ] AC-4: Empty text -> `missing_fields=["text"]` (backward compat, unchanged)
- [ ] AC-5: Shopping, no items -> `missing_fields=["item.name"]` (backward compat, unchanged)
- [ ] AC-6: Task, no title -> `missing_fields=["task.title"]` (backward compat, unchanged)
- [ ] AC-7: All 176 existing tests pass

## DoD

- [ ] Code updated: `routers/v2.py` (2 triggers enriched)
- [ ] Tests created: `tests/test_clarify_missing_fields.py` (6 tests)
- [ ] All existing tests pass (176)
- [ ] New tests pass (6)
- [ ] Schema validation: enriched clarify decisions validate against decision.schema.json
- [ ] No secrets in changed files
- [ ] Invariants: core_graph.py, schemas, assist/runner.py NOT modified
