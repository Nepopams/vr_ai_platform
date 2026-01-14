import json
import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agent_registry.v0_loader import AgentRegistryV0Loader


def _write_registry(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _base_agent() -> dict:
    return {
        "agent_id": "agent-1",
        "enabled": False,
        "mode": "shadow",
        "capabilities": [
            {
                "capability_id": "shopping.add",
                "allowed_intents": ["add_shopping_item"],
            }
        ],
        "runner": {"kind": "python_module", "ref": "agents.shopping:run"},
    }


def test_registry_v0_empty_ok(tmp_path: Path) -> None:
    payload = {"registry_version": "v0", "agents": []}
    registry_path = _write_registry(tmp_path / "registry.json", payload)

    registry = AgentRegistryV0Loader.load(path_override=str(registry_path))

    assert registry.registry_version == "v0"
    assert registry.agents == ()


def test_registry_v0_rejects_extra_field(tmp_path: Path) -> None:
    payload = {"registry_version": "v0", "agents": [], "extra": True}
    registry_path = _write_registry(tmp_path / "registry.json", payload)

    with pytest.raises(ValueError, match="unexpected field"):
        AgentRegistryV0Loader.load(path_override=str(registry_path))


def test_registry_v0_invalid_mode(tmp_path: Path) -> None:
    agent = _base_agent()
    agent["mode"] = "invalid"
    payload = {"registry_version": "v0", "agents": [agent]}
    registry_path = _write_registry(tmp_path / "registry.json", payload)

    with pytest.raises(ValueError, match="invalid mode"):
        AgentRegistryV0Loader.load(path_override=str(registry_path))


def test_registry_v0_invalid_runner_kind(tmp_path: Path) -> None:
    agent = _base_agent()
    agent["runner"]["kind"] = "invalid"
    payload = {"registry_version": "v0", "agents": [agent]}
    registry_path = _write_registry(tmp_path / "registry.json", payload)

    with pytest.raises(ValueError, match="invalid runner.kind"):
        AgentRegistryV0Loader.load(path_override=str(registry_path))
