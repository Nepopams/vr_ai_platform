"""A2A-like request/response helpers for the agent runner."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


SUPPORTED_AGENT_ID = "shopping-list-llm-extractor"
SUPPORTED_INTENT = "add_shopping_item"
A2A_VERSION = "a2a.v1"


@dataclass(frozen=True)
class AgentRequest:
    a2a_version: str
    message_id: str
    trace_id: str
    agent_id: str
    intent: str
    input_text: str
    input_context: Dict[str, Any]
    constraints: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None


def parse_request(payload: Dict[str, Any]) -> AgentRequest:
    required_fields = [
        "a2a_version",
        "message_id",
        "trace_id",
        "agent_id",
        "intent",
        "input",
    ]
    missing = [field for field in required_fields if field not in payload]
    if missing:
        raise ValueError(f"Missing fields: {', '.join(missing)}")

    input_payload = payload.get("input") or {}
    if "text" not in input_payload:
        raise ValueError("Missing input.text")

    return AgentRequest(
        a2a_version=str(payload["a2a_version"]),
        message_id=str(payload["message_id"]),
        trace_id=str(payload["trace_id"]),
        agent_id=str(payload["agent_id"]),
        intent=str(payload["intent"]),
        input_text=str(input_payload.get("text", "")),
        input_context=dict(input_payload.get("context") or {}),
        constraints=payload.get("constraints"),
        output_schema=payload.get("output_schema"),
    )


def build_response(
    *,
    request: AgentRequest,
    ok: bool,
    output: Optional[Dict[str, Any]] = None,
    meta: Optional[Dict[str, Any]] = None,
    error: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    response: Dict[str, Any] = {
        "a2a_version": request.a2a_version,
        "message_id": request.message_id,
        "trace_id": request.trace_id,
        "agent_id": request.agent_id,
        "ok": ok,
    }
    if output is not None:
        response["output"] = output
    if meta is not None:
        response["meta"] = meta
    if error is not None:
        response["error"] = error
    return response


def unsupported_response(request: AgentRequest) -> Dict[str, Any]:
    return build_response(
        request=request,
        ok=False,
        error={"type": "unsupported_agent_or_intent", "message": "Agent or intent unsupported."},
    )
