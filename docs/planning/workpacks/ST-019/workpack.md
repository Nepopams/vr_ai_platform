# Workpack: ST-019 — Capabilities Lookup Service for Agent Registry

**Status:** Ready
**Story:** `docs/planning/epics/EP-007/stories/ST-019-capabilities-lookup-service.md`

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-007/epic.md` |
| Story | `docs/planning/epics/EP-007/stories/ST-019-capabilities-lookup-service.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q3-agent-registry-integration.md` |
| ADR-005 | `docs/adr/ADR-005-internal-agent-contract-v0.md` |
| Agent registry models | `agent_registry/v0_models.py` |
| Agent registry loader | `agent_registry/v0_loader.py` |
| Capability catalog | `agent_registry/capabilities-v0.yaml` |
| Agent registry YAML | `agent_registry/agent-registry-v0.yaml` |
| Existing registry tests | `tests/test_agent_registry_v0.py`, `tests/test_agent_registry_capabilities_v0.py` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

A single `CapabilitiesLookup` class in `agent_registry/capabilities_lookup.py` that consolidates agent filtering logic. Given a loaded `AgentRegistryV0`, it answers: "which enabled agents can handle intent X in mode Y?" This service is the foundation for the core pipeline registry gate (ST-020).

## Acceptance Criteria

1. `find_agents(intent, mode)` returns enabled agents matching both intent and mode
2. `find_agents` filters out disabled agents (enabled=false)
3. `find_agents` returns empty list when intent doesn't match
4. `find_agents` returns empty list when mode doesn't match
5. `has_capability(intent, mode)` returns True/False based on find_agents result
6. `list_capabilities()` returns all capability IDs from the catalog
7. All 202 existing tests pass + ~10 new tests pass

---

## Files to Change

| File | Change |
|------|--------|
| `agent_registry/capabilities_lookup.py` | **New:** `CapabilitiesLookup` class |
| `tests/test_capabilities_lookup.py` | **New:** ~10 unit tests |

---

## Implementation Plan

### Step 1: Create `agent_registry/capabilities_lookup.py`

New module with `CapabilitiesLookup` class:

```python
from __future__ import annotations

from typing import Sequence

from agent_registry.v0_models import AgentRegistryV0, AgentSpec
from agent_registry.v0_loader import load_capability_catalog


class CapabilitiesLookup:
    def __init__(self, registry: AgentRegistryV0, catalog: dict[str, dict] | None = None):
        self._registry = registry
        self._catalog = catalog or {}

    def find_agents(self, intent: str, mode: str) -> list[AgentSpec]:
        result = []
        for agent in self._registry.agents:
            if not agent.enabled:
                continue
            if agent.mode != mode:
                continue
            for cap in agent.capabilities:
                if intent in cap.allowed_intents:
                    result.append(agent)
                    break
        return result

    def has_capability(self, intent: str, mode: str) -> bool:
        return len(self.find_agents(intent, mode)) > 0

    def list_capabilities(self) -> list[str]:
        return list(self._catalog.keys())
```

Key design decisions:
- Constructor takes `AgentRegistryV0` (from loader) and optional catalog dict (from `load_capability_catalog`)
- No new loading logic — consumers call `AgentRegistryV0Loader.load()` and `load_capability_catalog()` themselves
- `find_agents` filters by: enabled=True, mode match, intent in any capability's allowed_intents
- `list_capabilities` uses the catalog (not agents), returning all registered capability IDs

### Step 2: Create `tests/test_capabilities_lookup.py`

10 unit tests using in-memory test fixtures (no YAML files):

1. `test_find_agents_matching_intent_and_mode` — 1 enabled shadow agent with `add_shopping_item` → returns it
2. `test_find_agents_disabled_filtered` — 1 disabled agent → empty list
3. `test_find_agents_intent_mismatch` — agent for `add_shopping_item`, query `create_task` → empty
4. `test_find_agents_mode_mismatch` — shadow agent, query mode=`assist` → empty
5. `test_find_agents_empty_registry` — no agents → empty list
6. `test_find_agents_multiple_matches` — 2 enabled matching agents → both returned
7. `test_has_capability_true` — matching agent exists → True
8. `test_has_capability_false` — no match → False
9. `test_list_capabilities_returns_all` — catalog with 3 capabilities → returns all 3 IDs
10. `test_list_capabilities_empty_catalog` — no catalog → empty list

Test fixtures pattern:
```python
def _make_agent(agent_id, enabled, mode, intent):
    return AgentSpec(
        agent_id=agent_id,
        enabled=enabled,
        mode=mode,
        capabilities=(AgentCapability(
            capability_id="test_cap",
            allowed_intents=(intent,),
        ),),
        runner=RunnerSpec(kind="python_module", ref="test:run"),
    )

def _make_registry(*agents):
    return AgentRegistryV0(
        registry_version="v0",
        compat_adr=None,
        compat_note=None,
        agents=tuple(agents),
    )
```

---

## Verification Commands

```bash
# Full test suite (expect 212+ passed)
python3 -m pytest tests/ -v --tb=short

# Just capabilities lookup tests (expect 10 tests)
python3 -m pytest tests/test_capabilities_lookup.py -v --tb=short

# Import check
python3 -c "from agent_registry.capabilities_lookup import CapabilitiesLookup; print('OK')"
```

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| AgentSpec dataclass frozen — can't modify in tests | Low | Low | Use constructor (already frozen-compatible) |
| Catalog format changes | Low | Low | Uses existing `load_capability_catalog()` dict format |

## Rollback

- Delete 2 new files: `agent_registry/capabilities_lookup.py` and `tests/test_capabilities_lookup.py`
- No existing files modified

## APPLY Boundaries

**Allowed:** `agent_registry/capabilities_lookup.py`, `tests/test_capabilities_lookup.py`
**Forbidden:** `agent_registry/v0_models.py`, `agent_registry/v0_loader.py`, `agent_registry/*.yaml`, `graphs/`, `routers/`, `contracts/`
