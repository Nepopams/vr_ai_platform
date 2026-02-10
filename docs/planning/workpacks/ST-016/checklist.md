# Checklist: ST-016 — Real Schema Breaking-Change Detection

## Acceptance Criteria

- [ ] AC-1: Detect field deletion → "Removed property: X"
- [ ] AC-2: Detect type change → "Type changed for property 'X': old -> new"
- [ ] AC-3: Detect new required field → "New required field: X"
- [ ] AC-4: Removed required field still detected (backward compat)
- [ ] AC-5: Non-breaking optional addition not flagged
- [ ] AC-6: CI checks real schemas against baseline (default behavior)
- [ ] AC-7: `.baseline/` contains copies matching current schemas
- [ ] AC-8: All existing tests pass + new tests pass

## DoD Checklist

- [ ] `find_breaking_changes()` extended with 3 new categories
- [ ] `compare_all_schemas()` added for baseline comparison
- [ ] `main()` defaults to baseline when no --old/--new
- [ ] Baseline directory created with current schema copies
- [ ] 4 test fixtures created
- [ ] 6 new tests written and passing
- [ ] All tests pass: `python3 -m pytest tests/ -v --tb=short`
- [ ] `python3 -m skills.schema_bump check` passes
- [ ] Backward compat: explicit --old/--new still works
