import json
import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agent_registry.v0_loader import AgentRegistryV0Loader


def _write_payload(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _catalog_payload(allowed_modes=None) -> dict:
    return {
        "catalog_version": "v0",
        "capabilities": [
            {
                "capability_id": "extract_entities.shopping",
                "purpose": "test",
                "allowed_modes": allowed_modes or ["assist"],
                "risk_level": "low",
                "payload_allowlist": ["items"],
                "contains_sensitive_text": True,
            }
        ],
    }


def _registry_payload(capability_id: str, mode: str) -> dict:
    return {
        "registry_version": "v0",
        "agents": [
            {
                "agent_id": "agent-1",
                "enabled": False,
                "mode": mode,
                "capabilities": [
                    {
                        "capability_id": capability_id,
                        "allowed_intents": ["add_shopping_item"],
                    }
                ],
                "runner": {"kind": "python_module", "ref": "agents.shopping:run"},
            }
        ],
    }


def test_unknown_capability_id(tmp_path: Path) -> None:
    registry_path = _write_payload(tmp_path / "registry.json", _registry_payload("unknown", "assist"))
    catalog_path = _write_payload(tmp_path / "catalog.json", _catalog_payload())

    with pytest.raises(ValueError, match="unknown capability_id"):
        AgentRegistryV0Loader.load(
            path_override=str(registry_path),
            catalog_path_override=str(catalog_path),
        )


def test_capability_mode_mismatch(tmp_path: Path) -> None:
    registry_path = _write_payload(tmp_path / "registry.json", _registry_payload("extract_entities.shopping", "assist"))
    catalog_path = _write_payload(tmp_path / "catalog.json", _catalog_payload(["shadow"]))

    with pytest.raises(ValueError, match="capability mode mismatch"):
        AgentRegistryV0Loader.load(
            path_override=str(registry_path),
            catalog_path_override=str(catalog_path),
        )


def test_valid_registry_with_capabilities(tmp_path: Path) -> None:
    registry_path = _write_payload(
        tmp_path / "registry.json",
        _registry_payload("extract_entities.shopping", "assist"),
    )
    catalog_path = _write_payload(tmp_path / "catalog.json", _catalog_payload(["assist", "shadow"]))

    registry = AgentRegistryV0Loader.load(
        path_override=str(registry_path),
        catalog_path_override=str(catalog_path),
    )

    assert registry.registry_version == "v0"
    assert len(registry.agents) == 1


def test_empty_registry_skips_catalog(tmp_path: Path) -> None:
    registry_path = _write_payload(tmp_path / "registry.json", {"registry_version": "v0", "agents": []})

    registry = AgentRegistryV0Loader.load(path_override=str(registry_path))

    assert registry.registry_version == "v0"
    assert registry.agents == ()
