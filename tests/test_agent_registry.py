import json
import sys
from pathlib import Path

import pytest


def _write_registry(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _load_registry_payload() -> dict:
    registry_path = Path(__file__).resolve().parents[1] / "agent_registry" / "agent-registry.yaml"
    return json.loads(registry_path.read_text(encoding="utf-8"))


def test_load_valid_registry() -> None:
    from agent_registry.loader import AgentRegistryLoader

    registry = AgentRegistryLoader.load(enabled=True)

    assert registry is not None
    assert registry.compat_adr == "ADR-002"


def test_invalid_missing_required_field(tmp_path: Path) -> None:
    from agent_registry.loader import AgentRegistryLoader

    payload = _load_registry_payload()
    payload.pop("agents")
    registry_path = _write_registry(tmp_path / "invalid.yaml", payload)

    with pytest.raises(ValueError, match="missing required field"):
        AgentRegistryLoader.load(enabled=True, path_override=str(registry_path))


def test_invalid_duplicate_agent_id(tmp_path: Path) -> None:
    from agent_registry.loader import AgentRegistryLoader

    payload = _load_registry_payload()
    payload["agents"].append(payload["agents"][0])
    registry_path = _write_registry(tmp_path / "invalid.yaml", payload)

    with pytest.raises(ValueError, match="duplicate agent_id"):
        AgentRegistryLoader.load(enabled=True, path_override=str(registry_path))


def test_intent_coverage_has_executors(tmp_path: Path) -> None:
    from agent_registry.loader import AgentRegistryLoader

    payload = _load_registry_payload()
    payload["agents"] = [agent for agent in payload["agents"] if agent["agent_id"] != "task"]
    registry_path = _write_registry(tmp_path / "invalid.yaml", payload)

    with pytest.raises(ValueError, match="missing propose_create_task executor"):
        AgentRegistryLoader.load(enabled=True, path_override=str(registry_path))


def test_disabled_registry_no_side_effects() -> None:
    for module in list(sys.modules):
        if module == "agent_registry" or module.startswith("agent_registry."):
            sys.modules.pop(module, None)

    sys.modules.pop("graphs.core_graph", None)

    import graphs.core_graph

    assert "agent_registry" not in sys.modules

    from agent_registry.loader import AgentRegistryLoader

    assert AgentRegistryLoader.load(enabled=False) is None
