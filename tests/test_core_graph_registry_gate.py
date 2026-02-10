from unittest.mock import patch, MagicMock

from graphs.core_graph import _annotate_registry_capabilities, process_command, sample_command


def test_gate_disabled_by_default(monkeypatch):
    monkeypatch.delenv("AGENT_REGISTRY_CORE_ENABLED", raising=False)
    result = _annotate_registry_capabilities("add_shopping_item")
    assert result == {}


def test_gate_enabled_returns_snapshot(monkeypatch):
    monkeypatch.setenv("AGENT_REGISTRY_CORE_ENABLED", "true")

    mock_agent = MagicMock()
    mock_agent.agent_id = "test-agent"
    mock_agent.mode = "shadow"
    mock_agent.enabled = True

    mock_registry = MagicMock()
    mock_catalog = {}

    mock_lookup = MagicMock()
    mock_lookup.find_agents.side_effect = lambda intent, mode: (
        [mock_agent] if mode == "shadow" else []
    )

    with patch("agent_registry.v0_loader.AgentRegistryV0Loader.load", return_value=mock_registry), \
         patch("agent_registry.v0_loader.load_capability_catalog", return_value=mock_catalog), \
         patch("agent_registry.capabilities_lookup.CapabilitiesLookup", return_value=mock_lookup):
        result = _annotate_registry_capabilities("add_shopping_item")

    assert result["intent"] == "add_shopping_item"
    assert result["any_enabled"] is True
    assert len(result["available_agents"]) == 1
    assert result["available_agents"][0]["agent_id"] == "test-agent"
    assert result["available_agents"][0]["mode"] == "shadow"


def test_decision_unchanged_with_flag_off(monkeypatch):
    monkeypatch.delenv("AGENT_REGISTRY_CORE_ENABLED", raising=False)
    command = sample_command()
    decision = process_command(command)
    assert decision["action"] == "start_job"
    assert decision["status"] == "ok"
    assert "payload" in decision


def test_decision_unchanged_with_flag_on(monkeypatch):
    monkeypatch.setenv("AGENT_REGISTRY_CORE_ENABLED", "true")

    mock_lookup = MagicMock()
    mock_lookup.find_agents.return_value = []

    with patch("agent_registry.v0_loader.AgentRegistryV0Loader.load", return_value=MagicMock()), \
         patch("agent_registry.v0_loader.load_capability_catalog", return_value={}), \
         patch("agent_registry.capabilities_lookup.CapabilitiesLookup", return_value=mock_lookup):
        command = sample_command()
        decision = process_command(command)

    assert decision["action"] == "start_job"
    assert decision["status"] == "ok"
    assert "payload" in decision


def test_registry_load_failure_graceful(monkeypatch):
    monkeypatch.setenv("AGENT_REGISTRY_CORE_ENABLED", "true")

    with patch("agent_registry.v0_loader.AgentRegistryV0Loader.load", side_effect=ValueError("broken")):
        result = _annotate_registry_capabilities("add_shopping_item")

    assert result["intent"] == "add_shopping_item"
    assert "error" in result
    assert result["any_enabled"] is False

    # Also verify pipeline still works
    with patch("agent_registry.v0_loader.AgentRegistryV0Loader.load", side_effect=ValueError("broken")):
        command = sample_command()
        decision = process_command(command)
    assert decision["action"] == "start_job"


def test_annotation_returns_agent_ids(monkeypatch):
    monkeypatch.setenv("AGENT_REGISTRY_CORE_ENABLED", "true")

    agent1 = MagicMock()
    agent1.agent_id = "agent-shadow"
    agent1.mode = "shadow"
    agent2 = MagicMock()
    agent2.agent_id = "agent-assist"
    agent2.mode = "assist"

    mock_lookup = MagicMock()
    mock_lookup.find_agents.side_effect = lambda intent, mode: (
        [agent1] if mode == "shadow" else [agent2] if mode == "assist" else []
    )

    with patch("agent_registry.v0_loader.AgentRegistryV0Loader.load", return_value=MagicMock()), \
         patch("agent_registry.v0_loader.load_capability_catalog", return_value={}), \
         patch("agent_registry.capabilities_lookup.CapabilitiesLookup", return_value=mock_lookup):
        result = _annotate_registry_capabilities("add_shopping_item")

    assert len(result["available_agents"]) == 2
    ids = {a["agent_id"] for a in result["available_agents"]}
    assert ids == {"agent-shadow", "agent-assist"}


def test_no_raw_text_in_snapshot(monkeypatch):
    monkeypatch.setenv("AGENT_REGISTRY_CORE_ENABLED", "true")

    mock_lookup = MagicMock()
    mock_lookup.find_agents.return_value = []

    with patch("agent_registry.v0_loader.AgentRegistryV0Loader.load", return_value=MagicMock()), \
         patch("agent_registry.v0_loader.load_capability_catalog", return_value={}), \
         patch("agent_registry.capabilities_lookup.CapabilitiesLookup", return_value=mock_lookup):
        result = _annotate_registry_capabilities("add_shopping_item")

    assert "text" not in result
    assert "user_id" not in result
    assert "command" not in result
    assert result.get("intent") == "add_shopping_item"


def test_gate_empty_registry_returns_none_enabled(monkeypatch):
    monkeypatch.setenv("AGENT_REGISTRY_CORE_ENABLED", "true")

    mock_lookup = MagicMock()
    mock_lookup.find_agents.return_value = []

    with patch("agent_registry.v0_loader.AgentRegistryV0Loader.load", return_value=MagicMock()), \
         patch("agent_registry.v0_loader.load_capability_catalog", return_value={}), \
         patch("agent_registry.capabilities_lookup.CapabilitiesLookup", return_value=mock_lookup):
        result = _annotate_registry_capabilities("add_shopping_item")

    assert result["any_enabled"] is False
    assert result["available_agents"] == []
