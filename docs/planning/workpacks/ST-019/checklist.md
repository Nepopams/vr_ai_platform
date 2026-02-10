# Checklist: ST-019 — Capabilities Lookup Service

## Acceptance Criteria

- [ ] AC-1: `find_agents(intent, mode)` returns matching enabled agents
- [ ] AC-2: `find_agents` filters out disabled agents
- [ ] AC-3: `find_agents` returns empty for intent mismatch
- [ ] AC-4: `find_agents` returns empty for mode mismatch
- [ ] AC-5: `has_capability` returns True/False correctly
- [ ] AC-6: `list_capabilities` returns all catalog IDs
- [ ] AC-7: All 202 existing tests pass + new tests pass

## DoD Checklist

- [ ] Code follows project conventions (Python, dataclasses)
- [ ] No new dependencies introduced
- [ ] Unit tests written and passing (~10 new)
- [ ] All tests pass: `python3 -m pytest tests/ -v --tb=short`
- [ ] Module importable: `python3 -c "from agent_registry.capabilities_lookup import CapabilitiesLookup"`
- [ ] No modification to existing agent_registry files
- [ ] No modification to existing tests
