from __future__ import annotations

import json
import warnings
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
        payload = _load_registry_payload(registry_path)
        _validate_registry(payload)
        return _to_registry(payload)


def _default_registry_path() -> Path:
    return Path(__file__).resolve().parent / "agent-registry.yaml"


def _load_registry_payload(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"agent registry not found: {path}") from exc

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = _parse_yaml(raw)

    if not isinstance(parsed, dict):
        raise ValueError("agent registry must be a mapping")

    return parsed


def _parse_yaml(raw: str) -> dict[str, Any]:
    tokens = _tokenize_yaml(raw)
    if not tokens:
        raise ValueError("agent registry is empty")

    index = 0

    def parse_node(expected_indent: int) -> Any:
        nonlocal index
        if index >= len(tokens):
            return {}
        indent, content = tokens[index]
        if indent < expected_indent:
            return {}
        if content.startswith("- "):
            return parse_list(expected_indent)
        return parse_mapping(expected_indent)

    def parse_mapping(expected_indent: int) -> dict[str, Any]:
        nonlocal index
        mapping: dict[str, Any] = {}
        while index < len(tokens):
            indent, content = tokens[index]
            if indent < expected_indent:
                break
            if content.startswith("- "):
                break
            key, sep, rest = content.partition(":")
            if not sep:
                raise ValueError(f"invalid mapping entry: {content}")
            key = key.strip()
            rest = rest.strip()
            index += 1
            if rest == "":
                if index < len(tokens) and tokens[index][0] > indent:
                    mapping[key] = parse_node(tokens[index][0])
                else:
                    mapping[key] = {}
            else:
                mapping[key] = _parse_scalar(rest)
        return mapping

    def parse_list(expected_indent: int) -> list[Any]:
        nonlocal index
        items: list[Any] = []
        while index < len(tokens):
            indent, content = tokens[index]
            if indent < expected_indent or not content.startswith("- "):
                break
            item_content = content[2:].strip()
            index += 1
            if item_content == "":
                if index < len(tokens) and tokens[index][0] > indent:
                    items.append(parse_node(tokens[index][0]))
                else:
                    items.append(None)
                continue
            if ":" in item_content:
                key, _, rest = item_content.partition(":")
                key = key.strip()
                rest = rest.strip()
                item: dict[str, Any] = {}
                if rest == "":
                    if index < len(tokens) and tokens[index][0] > indent:
                        item[key] = parse_node(tokens[index][0])
                    else:
                        item[key] = {}
                else:
                    item[key] = _parse_scalar(rest)
                if index < len(tokens) and tokens[index][0] > indent:
                    extra = parse_mapping(tokens[index][0])
                    item.update(extra)
                items.append(item)
            else:
                items.append(_parse_scalar(item_content))
        return items

    result = parse_mapping(tokens[0][0])
    if not isinstance(result, dict):
        raise ValueError("agent registry must be a mapping")
    return result


def _tokenize_yaml(raw: str) -> list[tuple[int, str]]:
    tokens: list[tuple[int, str]] = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        stripped = line.lstrip(" ")
        if stripped.startswith("#"):
            continue
        indent = len(line) - len(stripped)
        tokens.append((indent, stripped))
    return tokens


def _parse_scalar(value: str) -> str:
    if value.startswith("\"") and value.endswith("\""):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    return value


def _normalize_compat(payload: dict[str, Any]) -> dict[str, Any]:
    compat = payload.get("compat")
    legacy_keys = {
        "compat.adr": "adr",
        "compat.mvp": "mvp",
        "compat.contracts_version": "contracts_version",
    }
    legacy_present = any(key in payload for key in legacy_keys)

    if compat is None and legacy_present:
        compat = {target: payload.get(source) for source, target in legacy_keys.items()}
        warnings.warn("legacy compat.* keys detected; migrate to compat: {...}", UserWarning)

    if not isinstance(compat, dict):
        raise ValueError("compat must be a mapping")

    _require_keys(compat, ["adr", "mvp", "contracts_version"])
    return compat


def _validate_registry(payload: dict[str, Any]) -> None:
    _require_keys(payload, ["registry_version", "agents", "intents"])

    compat = _normalize_compat(payload)
    if compat["adr"] != "ADR-002":
        raise ValueError("agent registry must declare compat.adr=ADR-002")

    if compat["mvp"] != "AI_PLATFORM_MVP_v1":
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
    compat = _normalize_compat(payload)
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
        compat_adr=str(compat["adr"]),
        compat_mvp=str(compat["mvp"]),
        compat_contracts_version=str(compat["contracts_version"]),
        agents=tuple(agents),
        intents=intents,
    )


def _require_keys(payload: dict[str, Any], keys: list[str]) -> None:
    for key in keys:
        if key not in payload:
            raise ValueError(f"missing required field: {key}")
