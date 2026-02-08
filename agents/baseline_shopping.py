from __future__ import annotations

from typing import Any, Dict, List

from graphs.core_graph import extract_items, _default_list_id


def run(agent_input: Dict[str, Any], trace_id: str | None = None) -> Dict[str, Any]:
    text = agent_input.get("text", "")
    items: List[Dict[str, Any]] = extract_items(text) if isinstance(text, str) else []

    context = agent_input.get("context")
    list_id = None
    if isinstance(context, dict):
        list_id = _default_list_id({"context": context})

    payload: Dict[str, Any] = {"items": items, "confidence": 0.6 if items else 0.0}
    if list_id:
        payload["list_id"] = list_id
    return payload
