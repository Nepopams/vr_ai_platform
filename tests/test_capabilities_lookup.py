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
