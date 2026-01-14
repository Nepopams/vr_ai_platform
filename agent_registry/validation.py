from __future__ import annotations

from typing import Any, Dict, Mapping

from agent_registry.v0_reason_codes import (
    REASON_CAPABILITY_NOT_ALLOWED,
    REASON_INVALID_INPUT,
    REASON_INVALID_OUTPUT,
)


def validate_agent_input(
    agent_input: Any,
) -> tuple[bool, str | None, Dict[str, Any] | None]:
    if not isinstance(agent_input, dict):
        return False, REASON_INVALID_INPUT, None
    return True, None, dict(agent_input)


def validate_agent_output_payload(
    payload: Any,
    capability_id: str,
    catalog: Mapping[str, Mapping[str, Any]],
) -> tuple[bool, str | None]:
    if not isinstance(payload, dict):
        return False, REASON_INVALID_OUTPUT
    entry = catalog.get(capability_id)
    if entry is None:
        return False, REASON_CAPABILITY_NOT_ALLOWED
    allowlist = entry.get("payload_allowlist", set())
    if not isinstance(allowlist, (set, list, tuple)):
        return False, REASON_INVALID_OUTPUT
    allowlist_set = set(allowlist)
    if set(payload.keys()) - allowlist_set:
        return False, REASON_INVALID_OUTPUT
    return True, None
