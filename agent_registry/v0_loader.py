from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from agent_registry.v0_models import (
    AgentCapability,
    AgentRegistryV0,
    AgentSpec,
    PrivacySpec,
    RunnerSpec,
    TimeoutSpec,
)

_ALLOWED_TOP_LEVEL_KEYS = {"registry_version", "agents", "compat"}
_ALLOWED_COMPAT_KEYS = {"adr", "note"}
_ALLOWED_AGENT_KEYS = {
    "agent_id",
    "enabled",
    "mode",
    "capabilities",
    "runner",
    "timeouts",
    "privacy",
    "llm_profile_id",
}
_ALLOWED_CAPABILITY_KEYS = {"capability_id", "allowed_intents", "risk_level"}
_ALLOWED_RUNNER_KEYS = {"kind", "ref"}
_ALLOWED_TIMEOUT_KEYS = {"timeout_ms"}
_ALLOWED_PRIVACY_KEYS = {"allow_raw_logs"}
_ALLOWED_CATALOG_KEYS = {"catalog_version", "capabilities"}
_ALLOWED_CATALOG_CAPABILITY_KEYS = {
    "capability_id",
    "purpose",
    "allowed_modes",
    "risk_level",
    "allowed_intents",
    "payload_allowlist",
    "contains_sensitive_text",
}

_ALLOWED_MODES = {"shadow", "assist", "partial_trust"}
_ALLOWED_RUNNER_KINDS = {"python_module", "llm_policy_task"}
_ALLOWED_RISK_LEVELS = {"low", "medium", "high"}
_ALLOWED_INTENTS = {"create_task", "add_shopping_item", "clarify_needed"}


class AgentRegistryV0Loader:
    @staticmethod
    def load(
        path_override: str | None = None,
        *,
        catalog_path_override: str | None = None,
    ) -> AgentRegistryV0:
        registry_path = Path(path_override) if path_override else _default_registry_path()
        payload = _load_registry_payload(registry_path)
        _validate_registry(payload)
        _validate_registry_capabilities(payload, catalog_path_override)
        return _to_registry(payload)


def load_capability_catalog(catalog_path_override: str | None = None) -> dict[str, dict[str, Any]]:
    catalog_path = Path(catalog_path_override) if catalog_path_override else _default_catalog_path()
    catalog_payload = _load_catalog_payload(catalog_path)
    return _validate_catalog(catalog_payload)


def _default_registry_path() -> Path:
    return Path(__file__).resolve().parent / "agent-registry-v0.yaml"


def _default_catalog_path() -> Path:
    return Path(__file__).resolve().parent / "capabilities-v0.yaml"


def _load_registry_payload(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"agent registry v0 not found: {path}") from exc

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = _parse_yaml(raw)

    if not isinstance(parsed, dict):
        raise ValueError("agent registry v0 must be a mapping")

    return parsed


def _load_catalog_payload(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"capability catalog v0 not found: {path}") from exc

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = _parse_yaml(raw)

    if not isinstance(parsed, dict):
        raise ValueError("capability catalog v0 must be a mapping")

    return parsed


def _parse_yaml(raw: str) -> dict[str, Any]:
    tokens = _tokenize_yaml(raw)
    if not tokens:
        raise ValueError("agent registry v0 is empty")

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
        raise ValueError("agent registry v0 must be a mapping")
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


def _validate_registry(payload: dict[str, Any]) -> None:
    _require_keys(payload, ["registry_version", "agents"])
    _ensure_no_extra_keys(payload, _ALLOWED_TOP_LEVEL_KEYS)

    if payload["registry_version"] != "v0":
        raise ValueError("invalid registry_version: expected v0")

    compat = payload.get("compat")
    if compat is not None:
        if not isinstance(compat, dict):
            raise ValueError("compat must be a mapping")
        _ensure_no_extra_keys(compat, _ALLOWED_COMPAT_KEYS)
        _require_keys(compat, ["adr", "note"])

    agents = payload["agents"]
    if not isinstance(agents, list):
        raise ValueError("agent registry v0 agents must be a list")

    for agent in agents:
        if not isinstance(agent, dict):
            raise ValueError("agent registry v0 agent entries must be mappings")
        _require_keys(agent, ["agent_id", "enabled", "mode", "capabilities", "runner"])
        _ensure_no_extra_keys(agent, _ALLOWED_AGENT_KEYS)

        if not isinstance(agent["agent_id"], str) or not agent["agent_id"]:
            raise ValueError("agent_id must be non-empty string")
        if not _is_bool_like(agent["enabled"]):
            raise ValueError("enabled must be bool")
        mode = agent["mode"]
        if mode not in _ALLOWED_MODES:
            raise ValueError(f"invalid mode: {mode}")
        llm_profile_id = agent.get("llm_profile_id")
        if llm_profile_id is not None and not isinstance(llm_profile_id, str):
            raise ValueError("llm_profile_id must be string")

        capabilities = agent["capabilities"]
        if not isinstance(capabilities, list):
            raise ValueError("capabilities must be a list")
        if len(capabilities) != 1:
            raise ValueError("capabilities must contain exactly 1 entry")
        for capability in capabilities:
            _validate_capability(capability)

        runner = agent["runner"]
        _validate_runner(runner)

        timeouts = agent.get("timeouts")
        if timeouts is not None:
            _validate_timeouts(timeouts)

        privacy = agent.get("privacy")
        if privacy is not None:
            _validate_privacy(privacy)


def _validate_registry_capabilities(
    payload: dict[str, Any],
    catalog_path_override: str | None,
) -> None:
    agents = payload.get("agents", [])
    if not agents:
        return
    catalog_path = Path(catalog_path_override) if catalog_path_override else _default_catalog_path()
    catalog_payload = _load_catalog_payload(catalog_path)
    catalog = _validate_catalog(catalog_payload)
    _validate_agent_capabilities(agents, catalog)


def _validate_capability(payload: Mapping[str, Any]) -> None:
    if not isinstance(payload, dict):
        raise ValueError("capability entries must be mappings")
    _require_keys(payload, ["capability_id", "allowed_intents"])
    _ensure_no_extra_keys(payload, _ALLOWED_CAPABILITY_KEYS)

    if not isinstance(payload["capability_id"], str) or not payload["capability_id"]:
        raise ValueError("capability_id must be non-empty string")
    intents = payload["allowed_intents"]
    if not isinstance(intents, list) or not all(isinstance(intent, str) for intent in intents):
        raise ValueError("allowed_intents must be a list of strings")
    risk_level = payload.get("risk_level")
    if risk_level is not None and not isinstance(risk_level, str):
        raise ValueError("risk_level must be string")


def _validate_runner(payload: Mapping[str, Any]) -> None:
    if not isinstance(payload, dict):
        raise ValueError("runner must be a mapping")
    _require_keys(payload, ["kind", "ref"])
    _ensure_no_extra_keys(payload, _ALLOWED_RUNNER_KEYS)

    kind = payload["kind"]
    if kind not in _ALLOWED_RUNNER_KINDS:
        raise ValueError(f"invalid runner.kind: {kind}")
    ref = payload["ref"]
    if not isinstance(ref, str) or not ref:
        raise ValueError("runner.ref must be non-empty string")


def _validate_timeouts(payload: Mapping[str, Any]) -> None:
    if not isinstance(payload, dict):
        raise ValueError("timeouts must be a mapping")
    _ensure_no_extra_keys(payload, _ALLOWED_TIMEOUT_KEYS)
    timeout_ms = payload.get("timeout_ms")
    if timeout_ms is not None and not _is_int_like(timeout_ms):
        raise ValueError("timeouts.timeout_ms must be int")


def _validate_privacy(payload: Mapping[str, Any]) -> None:
    if not isinstance(payload, dict):
        raise ValueError("privacy must be a mapping")
    _ensure_no_extra_keys(payload, _ALLOWED_PRIVACY_KEYS)
    allow_raw_logs = payload.get("allow_raw_logs")
    if allow_raw_logs is not None and not _is_bool_like(allow_raw_logs):
        raise ValueError("privacy.allow_raw_logs must be bool")


def _validate_catalog(payload: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    _require_keys(payload, ["catalog_version", "capabilities"])
    _ensure_no_extra_keys(payload, _ALLOWED_CATALOG_KEYS)

    if payload["catalog_version"] != "v0":
        raise ValueError("invalid catalog_version: expected v0")

    capabilities = payload["capabilities"]
    if not isinstance(capabilities, list):
        raise ValueError("capability catalog v0 capabilities must be a list")

    catalog: dict[str, dict[str, Any]] = {}
    for capability in capabilities:
        if not isinstance(capability, dict):
            raise ValueError("capability catalog entries must be mappings")
        _ensure_no_extra_keys(capability, _ALLOWED_CATALOG_CAPABILITY_KEYS)
        _require_keys(
            capability,
            [
                "capability_id",
                "purpose",
                "allowed_modes",
                "risk_level",
                "payload_allowlist",
                "contains_sensitive_text",
            ],
        )
        capability_id = capability["capability_id"]
        if not isinstance(capability_id, str) or not capability_id:
            raise ValueError("capability_id must be non-empty string")
        if capability_id in catalog:
            raise ValueError(f"duplicate capability_id: {capability_id}")
        if not isinstance(capability["purpose"], str):
            raise ValueError("purpose must be string")
        allowed_modes = capability["allowed_modes"]
        if not isinstance(allowed_modes, list):
            raise ValueError("allowed_modes must be a list")
        for mode in allowed_modes:
            if mode not in _ALLOWED_MODES:
                raise ValueError(f"invalid allowed_mode: {mode}")
        risk_level = capability["risk_level"]
        if risk_level not in _ALLOWED_RISK_LEVELS:
            raise ValueError(f"invalid risk_level: {risk_level}")
        allowlist = capability["payload_allowlist"]
        if not isinstance(allowlist, list) or not all(isinstance(item, str) for item in allowlist):
            raise ValueError("payload_allowlist must be a list of strings")
        contains_sensitive_text = capability.get("contains_sensitive_text")
        if not _is_bool_like(contains_sensitive_text):
            raise ValueError("contains_sensitive_text must be bool")
        allowed_intents = capability.get("allowed_intents")
        if allowed_intents is not None:
            if not isinstance(allowed_intents, list):
                raise ValueError("allowed_intents must be a list")
            for intent in allowed_intents:
                if intent not in _ALLOWED_INTENTS:
                    raise ValueError(f"invalid allowed_intent: {intent}")
        catalog[capability_id] = {
            "allowed_modes": set(allowed_modes),
            "payload_allowlist": set(allowlist),
            "contains_sensitive_text": _to_bool(contains_sensitive_text),
            "risk_level": risk_level,
            "allowed_intents": tuple(allowed_intents or []),
        }
    return catalog


def _validate_agent_capabilities(
    agents: list[dict[str, Any]],
    catalog: Mapping[str, dict[str, Any]],
) -> None:
    for agent in agents:
        mode = agent.get("mode")
        for capability in agent.get("capabilities", []):
            capability_id = capability.get("capability_id")
            if capability_id not in catalog:
                raise ValueError(f"unknown capability_id: {capability_id}")
            allowed_modes = catalog[capability_id]["allowed_modes"]
            if mode not in allowed_modes:
                raise ValueError(f"capability mode mismatch: {capability_id}")


def _to_registry(payload: dict[str, Any]) -> AgentRegistryV0:
    compat = payload.get("compat") or {}
    agents = []
    for agent in payload["agents"]:
        runner = RunnerSpec(
            kind=agent["runner"]["kind"],
            ref=agent["runner"]["ref"],
        )
        capabilities = [
            AgentCapability(
                capability_id=capability["capability_id"],
                allowed_intents=tuple(capability["allowed_intents"]),
                risk_level=capability.get("risk_level"),
            )
            for capability in agent["capabilities"]
        ]
        timeouts_payload = agent.get("timeouts")
        timeouts = None
        if timeouts_payload is not None:
            timeouts = TimeoutSpec(timeout_ms=_to_int(timeouts_payload.get("timeout_ms")))
        privacy_payload = agent.get("privacy") or {}
        privacy = PrivacySpec(allow_raw_logs=_to_bool(privacy_payload.get("allow_raw_logs", False)))
        agents.append(
            AgentSpec(
                agent_id=agent["agent_id"],
                enabled=_to_bool(agent["enabled"]),
                mode=agent["mode"],
                capabilities=tuple(capabilities),
                runner=runner,
                timeouts=timeouts,
                privacy=privacy,
                llm_profile_id=agent.get("llm_profile_id"),
            )
        )
    return AgentRegistryV0(
        registry_version=payload["registry_version"],
        compat_adr=compat.get("adr"),
        compat_note=compat.get("note"),
        agents=tuple(agents),
    )


def _ensure_no_extra_keys(payload: Mapping[str, Any], allowed: set[str]) -> None:
    extra = set(payload) - allowed
    if extra:
        name = sorted(extra)[0]
        raise ValueError(f"unexpected field: {name}")


def _require_keys(payload: Mapping[str, Any], keys: list[str]) -> None:
    for key in keys:
        if key not in payload:
            raise ValueError(f"missing required field: {key}")


def _is_bool_like(value: Any) -> bool:
    if isinstance(value, bool):
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"true", "false"}
    return False


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return False


def _is_int_like(value: Any) -> bool:
    if isinstance(value, int):
        return True
    if isinstance(value, str):
        return value.isdigit()
    return False


def _to_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None
