from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from llm_policy.models import CallSpec, FallbackRule, LlmPolicy

_ALLOWED_TOP_LEVEL_KEYS = {
    "schema_version",
    "compat",
    "profiles",
    "tasks",
    "routing",
    "fallback_chain",
}
_ALLOWED_ROUTING_KEYS = {
    "provider",
    "model",
    "temperature",
    "max_tokens",
    "timeout_ms",
    "base_url",
    "project",
}
_ALLOWED_EVENTS = {
    "invalid_json",
    "schema_validation_failed",
    "timeout",
    "llm_unavailable",
    "llm_error",
}
_ALLOWED_ACTIONS = {"repair_retry", "escalate_to", "return_error"}


class LlmPolicyLoader:
    @staticmethod
    def load(enabled: bool, path_override: str | None = None) -> LlmPolicy | None:
        if not enabled:
            return None

        policy_path = Path(path_override) if path_override else _default_policy_path()
        payload = _load_policy_payload(policy_path)
        _validate_policy(payload)
        return _to_policy(payload)


def _default_policy_path() -> Path:
    return Path(__file__).resolve().parent / "llm-policy.yaml"


def _load_policy_payload(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"llm policy not found: {path}") from exc

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = _parse_yaml(raw)

    if not isinstance(parsed, dict):
        raise ValueError("llm policy must be a mapping")

    return parsed


def _parse_yaml(raw: str) -> dict[str, Any]:
    tokens = _tokenize_yaml(raw)
    if not tokens:
        raise ValueError("llm policy is empty")

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
        raise ValueError("llm policy must be a mapping")
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
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    return value


def _validate_policy(payload: dict[str, Any]) -> None:
    _require_keys(payload, ["schema_version", "compat", "profiles", "tasks", "routing", "fallback_chain"])

    extra_keys = set(payload) - _ALLOWED_TOP_LEVEL_KEYS
    if extra_keys:
        extras = ", ".join(sorted(extra_keys))
        raise ValueError(f"unexpected top-level fields: {extras}")

    schema_version = str(payload["schema_version"])
    if schema_version != "1":
        raise ValueError("llm policy schema_version must be 1")

    compat = payload["compat"]
    if not isinstance(compat, dict):
        raise ValueError("compat must be a mapping")
    _require_keys(compat, ["adr", "note"])
    if compat["adr"] != "ADR-003":
        raise ValueError("llm policy must declare compat.adr=ADR-003")

    profiles = payload["profiles"]
    if not isinstance(profiles, dict):
        raise ValueError("profiles must be a mapping")
    for profile in ("cheap", "reliable"):
        if profile not in profiles:
            raise ValueError(f"profiles missing required profile: {profile}")

    tasks = payload["tasks"]
    if not isinstance(tasks, dict):
        raise ValueError("tasks must be a mapping")
    if "shopping_extraction" not in tasks:
        raise ValueError("tasks must include shopping_extraction")

    routing = payload["routing"]
    if not isinstance(routing, dict):
        raise ValueError("routing must be a mapping")
    if "shopping_extraction" not in routing:
        raise ValueError("routing must include shopping_extraction")
    for task_id, task_routes in routing.items():
        if not isinstance(task_routes, dict):
            raise ValueError(f"routing for {task_id} must be mapping")
        for profile, spec in task_routes.items():
            if profile not in profiles:
                raise ValueError(f"routing profile {profile} not declared in profiles")
            if not isinstance(spec, dict):
                raise ValueError(f"routing spec must be mapping: {task_id}.{profile}")
            _require_keys(spec, ["provider", "model"])
            extra_spec = set(spec) - _ALLOWED_ROUTING_KEYS
            if extra_spec:
                extras = ", ".join(sorted(extra_spec))
                raise ValueError(f"unexpected routing fields for {task_id}.{profile}: {extras}")

    fallback_chain = payload["fallback_chain"]
    if not isinstance(fallback_chain, list):
        raise ValueError("fallback_chain must be a list")

    for entry in fallback_chain:
        if not isinstance(entry, dict):
            raise ValueError("fallback_chain entries must be mappings")
        _require_keys(entry, ["event", "action"])
        event = entry["event"]
        action = entry["action"]
        if event not in _ALLOWED_EVENTS:
            raise ValueError(f"unknown fallback event: {event}")
        if action not in _ALLOWED_ACTIONS:
            raise ValueError(f"unknown fallback action: {action}")
        extra_entry = set(entry) - {"event", "action", "profile", "max_retries"}
        if extra_entry:
            extras = ", ".join(sorted(extra_entry))
            raise ValueError(f"unexpected fallback fields: {extras}")
        if action == "repair_retry":
            max_retries = _maybe_int(entry.get("max_retries"))
            if max_retries is None or max_retries < 1:
                raise ValueError("repair_retry must declare max_retries >= 1")
        if action == "escalate_to":
            profile = entry.get("profile")
            if profile not in profiles:
                raise ValueError("escalate_to must reference a known profile")


def _to_policy(payload: dict[str, Any]) -> LlmPolicy:
    compat = payload["compat"]
    profiles = tuple(payload["profiles"].keys())
    tasks = tuple(payload["tasks"].keys())
    routing: dict[str, dict[str, CallSpec]] = {}
    for task_id, task_routes in payload["routing"].items():
        routing[task_id] = {}
        for profile, spec in task_routes.items():
            routing[task_id][profile] = CallSpec(
                provider=str(spec["provider"]),
                model=str(spec["model"]),
                temperature=_maybe_float(spec.get("temperature")),
                max_tokens=_maybe_int(spec.get("max_tokens")),
                timeout_ms=_maybe_int(spec.get("timeout_ms")),
                base_url=_maybe_str(spec.get("base_url")),
                project=_maybe_str(spec.get("project")),
            )

    fallback_chain = tuple(
        FallbackRule(
            event=str(entry["event"]),
            action=str(entry["action"]),
            profile=_maybe_str(entry.get("profile")),
            max_retries=_maybe_int(entry.get("max_retries")),
        )
        for entry in payload["fallback_chain"]
    )

    return LlmPolicy(
        schema_version=str(payload["schema_version"]),
        compat_adr=str(compat["adr"]),
        compat_note=str(compat["note"]),
        profiles=profiles,
        tasks=tasks,
        routing=routing,
        fallback_chain=fallback_chain,
    )


def _maybe_float(value: object | None) -> float | None:
    if value is None:
        return None
    return float(value)


def _maybe_int(value: object | None) -> int | None:
    if value is None:
        return None
    return int(value)


def _maybe_str(value: object | None) -> str | None:
    if value is None:
        return None
    return str(value)


def _require_keys(payload: Mapping[str, Any], keys: list[str]) -> None:
    for key in keys:
        if key not in payload:
            raise ValueError(f"missing required field: {key}")
