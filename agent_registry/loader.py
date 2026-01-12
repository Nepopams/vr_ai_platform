from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent_registry.models import AgentRegistry, IntentSpec, RegistryAgent

_ALLOWED_INTENTS = {"create_task", "add_shopping_item", "clarify_needed"}
_ALLOWED_ACTIONS = {
    "start_job",
    "propose_create_task",
    "propose_add_shopping_item",
    "clarify",
}
_REQUIRED_AGENTS = {
    "decision-router",
    "clarifier",
    "shopping-list",
    "task",
    "job-manager",
}
_REQUIRED_FIELDS_BY_INTENT = {
    "create_task": {"payload.task.title"},
    "add_shopping_item": {"payload.item.name"},
    "clarify_needed": {"payload.question"},
}


class AgentRegistryLoader:
    @staticmethod
    def load(enabled: bool, path_override: str | None = None) -> AgentRegistry | None:
        if not enabled:
            return None

        registry_path = Path(path_override) if path_override else _default_registry_path()
        payload = _load_json_payload(registry_path)
        _validate_registry(payload)
        return _to_registry(payload)


def _default_registry_path() -> Path:
    return Path(__file__).resolve().parent / "agent-registry.yaml"


def _load_json_payload(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"agent registry not found: {path}") from exc

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"agent registry is not valid JSON/YAML: {path}") from exc

    if not isinstance(parsed, dict):
        raise ValueError("agent registry must be a mapping")

    return parsed


def _validate_registry(payload: dict[str, Any]) -> None:
    _require_keys(payload, [
        "registry_version",
        "compat.adr",
        "compat.mvp",
        "compat.contracts_version",
        "agents",
        "intents",
    ])

    if payload["compat.adr"] != "ADR-002":
        raise ValueError("agent registry must declare compat.adr=ADR-002")

    if payload["compat.mvp"] != "AI_PLATFORM_MVP_v1":
        raise ValueError("agent registry must declare compat.mvp=AI_PLATFORM_MVP_v1")

    agents = payload["agents"]
    if not isinstance(agents, list):
        raise ValueError("agent registry agents must be a list")

    agent_ids: set[str] = set()
    for agent in agents:
        if not isinstance(agent, dict):
            raise ValueError("agent registry agent entries must be mappings")
        _require_keys(agent, ["agent_id", "role", "intents"])
        agent_id = agent["agent_id"]
        if agent_id in agent_ids:
            raise ValueError(f"duplicate agent_id: {agent_id}")
        agent_ids.add(agent_id)

        intents = agent["intents"]
        if not isinstance(intents, list):
            raise ValueError(f"agent intents must be list: {agent_id}")
        for intent in intents:
            if intent not in _ALLOWED_INTENTS:
                raise ValueError(f"unknown intent in registry: {intent}")

        action = agent.get("action")
        if action is not None and action not in _ALLOWED_ACTIONS:
            raise ValueError(f"unknown action in registry: {action}")

    missing_agents = _REQUIRED_AGENTS - agent_ids
    if missing_agents:
        missing = ", ".join(sorted(missing_agents))
        raise ValueError(f"required agents missing: {missing}")

    intents_payload = payload["intents"]
    if not isinstance(intents_payload, dict):
        raise ValueError("agent registry intents must be mapping")

    for intent, spec in intents_payload.items():
        if intent not in _ALLOWED_INTENTS:
            raise ValueError(f"unknown intent in registry intents: {intent}")
        if not isinstance(spec, dict):
            raise ValueError(f"intent spec must be mapping: {intent}")
        _require_keys(spec, ["required_fields_for_execution"])
        fields = spec["required_fields_for_execution"]
        if not isinstance(fields, list):
            raise ValueError(f"required_fields_for_execution must be list: {intent}")
        allowed_fields = _REQUIRED_FIELDS_BY_INTENT[intent]
        for field in fields:
            if field not in allowed_fields:
                raise ValueError(f"invalid required field for {intent}: {field}")

    _validate_intent_coverage(agents)


def _validate_intent_coverage(agents: list[dict[str, Any]]) -> None:
    action_by_intent: dict[str, set[str]] = {intent: set() for intent in _ALLOWED_INTENTS}
    for agent in agents:
        action = agent.get("action")
        intents = agent.get("intents", [])
        if action is None:
            continue
        for intent in intents:
            action_by_intent[intent].add(action)

    if "propose_create_task" not in action_by_intent["create_task"]:
        raise ValueError("intent create_task missing propose_create_task executor")
    if "propose_add_shopping_item" not in action_by_intent["add_shopping_item"]:
        raise ValueError("intent add_shopping_item missing propose_add_shopping_item executor")
    if "clarify" not in action_by_intent["clarify_needed"]:
        raise ValueError("intent clarify_needed missing clarify executor")


def _to_registry(payload: dict[str, Any]) -> AgentRegistry:
    agents = [
        RegistryAgent(
            agent_id=agent["agent_id"],
            role=agent["role"],
            intents=tuple(agent["intents"]),
            action=agent.get("action"),
        )
        for agent in payload["agents"]
    ]

    intents = {
        intent: IntentSpec(
            intent=intent,
            required_fields_for_execution=tuple(spec["required_fields_for_execution"]),
        )
        for intent, spec in payload["intents"].items()
    }

    return AgentRegistry(
        registry_version=str(payload["registry_version"]),
        compat_adr=str(payload["compat.adr"]),
        compat_mvp=str(payload["compat.mvp"]),
        compat_contracts_version=str(payload["compat.contracts_version"]),
        agents=tuple(agents),
        intents=intents,
    )


def _require_keys(payload: dict[str, Any], keys: list[str]) -> None:
    for key in keys:
        if key not in payload:
            raise ValueError(f"missing required field: {key}")
