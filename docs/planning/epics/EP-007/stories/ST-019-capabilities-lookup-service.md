# ST-019: Capabilities Lookup Service for Agent Registry

**Epic:** EP-007 (Agent Registry Integration)
**Status:** Ready
**Flags:** contract_impact=no, adr_needed=none, diagrams_needed=none

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-007/epic.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q3-agent-registry-integration.md` |
| ADR-005 | `docs/adr/ADR-005-internal-agent-contract-v0.md` |
| Agent registry models | `agent_registry/v0_models.py` |
| Agent registry loader | `agent_registry/v0_loader.py` |
| Capabilities catalog | `agent_registry/capabilities-v0.yaml` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

Current consumers (shadow invoker, assist hints) each have ad-hoc filtering logic:

- Shadow invoker: iterates agents, checks allowlist, mode, intent match
- Assist hints: iterates agents, checks allowlist, enabled, mode, capability match

This duplicated filtering should be consolidated into a single lookup service
reusable by the core pipeline (ST-020).

## User Value

As a platform developer, I want a single capabilities lookup service that answers
"which enabled agents can handle intent X in mode Y?", so that the core pipeline
can query agent capabilities without reimplementing filtering logic.

## Scope

### In scope

- New module `agent_registry/capabilities_lookup.py` with `CapabilitiesLookup` class
- Methods:
  - `find_agents(intent: str, mode: str) -> List[AgentSpec]`
  - `has_capability(intent: str, mode: str) -> bool`
  - `list_capabilities() -> List[str]`
- Uses cached registry from loader (no new loading logic)
- Unit tests for all methods
- Edge cases: no match, disabled agents filtered, intent mismatch

### Out of scope

- Modifying existing shadow invoker or assist hints (future refactor)
- Registry YAML changes
- New capabilities or agents
- Feature flags (gating happens in consumers)

---

## Acceptance Criteria

### AC-1: find_agents returns matching agents
```
Given a test registry with one agent: mode="shadow", intent="add_shopping_item", enabled=true
When find_agents(intent="add_shopping_item", mode="shadow") is called
Then it returns a list with exactly that agent
```

### AC-2: find_agents respects enabled flag
```
Given a test registry with one agent: enabled=false
When find_agents() is called with matching intent and mode
Then it returns an empty list
```

### AC-3: find_agents filters by intent
```
Given a test registry with agent for "add_shopping_item"
When find_agents(intent="create_task", mode="shadow") is called
Then it returns an empty list
```

### AC-4: find_agents filters by mode
```
Given a test registry with agent mode="shadow"
When find_agents(intent="add_shopping_item", mode="assist") is called
Then it returns an empty list
```

### AC-5: has_capability returns boolean
```
Given a test registry with one enabled shadow agent for "add_shopping_item"
When has_capability(intent="add_shopping_item", mode="shadow")
Then returns True
When has_capability(intent="create_task", mode="shadow")
Then returns False
```

### AC-6: list_capabilities returns all catalog IDs
```
Given the capability catalog
When list_capabilities() is called
Then it returns all capability IDs from the catalog
```

### AC-7: All 202 existing tests pass
```
Given the test suite
When ST-019 changes are applied
Then all 202 tests pass and new tests also pass
```

---

## Test Strategy

### Unit tests (~10 new in `tests/test_capabilities_lookup.py`)
- `test_find_agents_matching_intent_and_mode`
- `test_find_agents_disabled_filtered`
- `test_find_agents_intent_mismatch`
- `test_find_agents_mode_mismatch`
- `test_find_agents_empty_registry`
- `test_find_agents_multiple_matches`
- `test_has_capability_true`
- `test_has_capability_false`
- `test_list_capabilities_returns_all`
- `test_list_capabilities_empty_catalog`

### Regression
- Full test suite: 202 tests must pass

---

## Code Touchpoints

| File | Change |
|------|--------|
| `agent_registry/capabilities_lookup.py` | New: CapabilitiesLookup class |
| `tests/test_capabilities_lookup.py` | New: unit tests |

---

## Dependencies

- ST-018 (ADR update): conceptual dependency (architecture documented)
- Blocks: ST-020 (core pipeline gate needs lookup service)
