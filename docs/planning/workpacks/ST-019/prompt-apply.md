# Codex APPLY Prompt — ST-019: Capabilities Lookup Service for Agent Registry

## Role
You are an implementation agent. Apply the changes described below exactly.

## Allowed files (whitelist)
- `agent_registry/capabilities_lookup.py` (NEW)
- `tests/test_capabilities_lookup.py` (NEW)

## Forbidden files
- `agent_registry/v0_models.py`, `agent_registry/v0_loader.py`, `agent_registry/*.yaml`
- `agent_registry/__init__.py`, `agent_registry/config.py`
- `routers/**`, `graphs/**`, `contracts/**`, `app/**`
- Any existing test files

## STOP-THE-LINE
If anything deviates from expectations or you need to modify files outside the whitelist, STOP and report.

---

## Context

Story ST-019 creates a `CapabilitiesLookup` class that consolidates agent filtering logic. Existing consumers (shadow invoker, assist hints) iterate `registry.agents` with ad-hoc filtering. This class provides a clean API: `find_agents(intent, mode)`, `has_capability(intent, mode)`, `list_capabilities()`.

### Key facts from PLAN
- `AgentSpec`, `AgentCapability`, `AgentRegistryV0` — all frozen dataclasses in `agent_registry/v0_models.py`
- `AgentCapability.allowed_intents` is `Sequence[str]` (tuple at runtime)
- `load_capability_catalog()` returns `dict[str, dict[str, Any]]` keyed by capability_id
- Catalog has 5 capabilities: normalize_text, extract_entities.shopping, suggest_clarify, propose_plan.executionless, decision_candidate.shopping
- `RunnerSpec` fields: kind, ref
- Existing test pattern: inline fixtures with helper functions, direct model construction

---

## Step 1: Create `agent_registry/capabilities_lookup.py`

**Create new file** with exact content:

```python
from __future__ import annotations

from typing import Any

from agent_registry.v0_models import AgentRegistryV0, AgentSpec


class CapabilitiesLookup:
    """Consolidated agent filtering by intent and mode."""

    def __init__(
        self,
        registry: AgentRegistryV0,
        catalog: dict[str, dict[str, Any]] | None = None,
    ):
        self._registry = registry
        self._catalog = catalog or {}

    def find_agents(self, intent: str, mode: str) -> list[AgentSpec]:
        """Return enabled agents matching both intent and mode."""
        result: list[AgentSpec] = []
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
        """Check if any enabled agent can handle intent in given mode."""
        return len(self.find_agents(intent, mode)) > 0

    def list_capabilities(self) -> list[str]:
        """Return all capability IDs from the catalog."""
        return list(self._catalog.keys())
```

---

## Step 2: Create `tests/test_capabilities_lookup.py`

**Create new file** with exact content:

```python
from agent_registry.capabilities_lookup import CapabilitiesLookup
from agent_registry.v0_models import (
    AgentCapability,
    AgentRegistryV0,
    AgentSpec,
    RunnerSpec,
)


def _make_agent(agent_id: str, enabled: bool, mode: str, intent: str) -> AgentSpec:
    return AgentSpec(
        agent_id=agent_id,
        enabled=enabled,
        mode=mode,
        capabilities=(
            AgentCapability(
                capability_id="test_cap",
                allowed_intents=(intent,),
            ),
        ),
        runner=RunnerSpec(kind="python_module", ref="test:run"),
    )


def _make_registry(*agents: AgentSpec) -> AgentRegistryV0:
    return AgentRegistryV0(
        registry_version="v0",
        compat_adr=None,
        compat_note=None,
        agents=tuple(agents),
    )


def test_find_agents_matching_intent_and_mode():
    agent = _make_agent("a1", enabled=True, mode="shadow", intent="add_shopping_item")
    registry = _make_registry(agent)
    lookup = CapabilitiesLookup(registry)
    result = lookup.find_agents(intent="add_shopping_item", mode="shadow")
    assert len(result) == 1
    assert result[0].agent_id == "a1"


def test_find_agents_disabled_filtered():
    agent = _make_agent("a1", enabled=False, mode="shadow", intent="add_shopping_item")
    registry = _make_registry(agent)
    lookup = CapabilitiesLookup(registry)
    result = lookup.find_agents(intent="add_shopping_item", mode="shadow")
    assert result == []


def test_find_agents_intent_mismatch():
    agent = _make_agent("a1", enabled=True, mode="shadow", intent="add_shopping_item")
    registry = _make_registry(agent)
    lookup = CapabilitiesLookup(registry)
    result = lookup.find_agents(intent="create_task", mode="shadow")
    assert result == []


def test_find_agents_mode_mismatch():
    agent = _make_agent("a1", enabled=True, mode="shadow", intent="add_shopping_item")
    registry = _make_registry(agent)
    lookup = CapabilitiesLookup(registry)
    result = lookup.find_agents(intent="add_shopping_item", mode="assist")
    assert result == []


def test_find_agents_empty_registry():
    registry = _make_registry()
    lookup = CapabilitiesLookup(registry)
    result = lookup.find_agents(intent="add_shopping_item", mode="shadow")
    assert result == []


def test_find_agents_multiple_matches():
    a1 = _make_agent("a1", enabled=True, mode="shadow", intent="add_shopping_item")
    a2 = _make_agent("a2", enabled=True, mode="shadow", intent="add_shopping_item")
    registry = _make_registry(a1, a2)
    lookup = CapabilitiesLookup(registry)
    result = lookup.find_agents(intent="add_shopping_item", mode="shadow")
    assert len(result) == 2
    assert {a.agent_id for a in result} == {"a1", "a2"}


def test_has_capability_true():
    agent = _make_agent("a1", enabled=True, mode="shadow", intent="add_shopping_item")
    registry = _make_registry(agent)
    lookup = CapabilitiesLookup(registry)
    assert lookup.has_capability(intent="add_shopping_item", mode="shadow") is True


def test_has_capability_false():
    agent = _make_agent("a1", enabled=True, mode="shadow", intent="add_shopping_item")
    registry = _make_registry(agent)
    lookup = CapabilitiesLookup(registry)
    assert lookup.has_capability(intent="create_task", mode="shadow") is False


def test_list_capabilities_returns_all():
    registry = _make_registry()
    catalog = {
        "normalize_text": {"risk_level": "low"},
        "extract_entities.shopping": {"risk_level": "medium"},
        "suggest_clarify": {"risk_level": "medium"},
    }
    lookup = CapabilitiesLookup(registry, catalog=catalog)
    result = lookup.list_capabilities()
    assert sorted(result) == ["extract_entities.shopping", "normalize_text", "suggest_clarify"]


def test_list_capabilities_empty_catalog():
    registry = _make_registry()
    lookup = CapabilitiesLookup(registry)
    assert lookup.list_capabilities() == []
```

---

## Verification

After applying changes, run:

```bash
# Import check
python3 -c "from agent_registry.capabilities_lookup import CapabilitiesLookup; print('OK')"

# Just capabilities lookup tests (expect 10 tests)
python3 -m pytest tests/test_capabilities_lookup.py -v --tb=short

# Full test suite (expect 214 passed)
python3 -m pytest tests/ -v --tb=short
```
