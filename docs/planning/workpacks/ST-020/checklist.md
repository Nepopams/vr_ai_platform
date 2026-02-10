# Checklist: ST-020 — Core Pipeline Registry-Aware Gate

## Acceptance Criteria

- [ ] AC-1: Flag defaults to false; no registry code runs when disabled
- [ ] AC-2: Flag enabled → registry_snapshot logged with intent, agent_ids, any_enabled
- [ ] AC-3: DecisionDTO unchanged regardless of flag state
- [ ] AC-4: Registry load failure → graceful fallback, decision produced normally
- [ ] AC-5: No raw user text in registry log entries
- [ ] AC-6: All 220 existing tests pass + new tests pass

## DoD Checklist

- [ ] `is_agent_registry_core_enabled()` added to config
- [ ] `_annotate_registry_capabilities()` added to core_graph
- [ ] Called from `process_command()` after intent detection
- [ ] Lazy imports — no import errors when flag disabled
- [ ] All exceptions caught — deterministic fallback
- [ ] ~8 unit tests written and passing
- [ ] All tests pass: `python3 -m pytest tests/ -v --tb=short`
- [ ] No modification to DecisionDTO schema or payload
