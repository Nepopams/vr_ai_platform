# ST-032 Checklist

## Acceptance Criteria

- [ ] AC-1: CommandRequest matches command.schema.json (6 required + nested context)
- [ ] AC-2: DecisionResponse matches decision.schema.json (11 required fields)
- [ ] AC-3: Route handler uses Pydantic models (auto-validation, typed return)
- [ ] AC-4: Invalid input → 422 with Pydantic validation errors
- [ ] AC-5: Jsonschema validation retained as safety net
- [ ] AC-6: All 275 existing tests pass

## DoD

- [ ] `pydantic` added to `pyproject.toml`
- [ ] `app/models/__init__.py` created
- [ ] `app/models/api_models.py` created
- [ ] `app/routes/decide.py` updated
- [ ] `tests/test_api_models.py` created (8 tests)
- [ ] `tests/test_api_decide.py` updated (422 format)
- [ ] `scripts/api_sanity.py` still works
- [ ] 8 new tests pass
- [ ] 275 existing tests pass (283 total, 3 skipped)
- [ ] No modifications to forbidden paths
