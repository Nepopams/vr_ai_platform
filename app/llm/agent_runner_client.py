"""Client for the local agent runner service."""

from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, Optional
from urllib import request as urlrequest
from uuid import uuid4

from app.logging.llm_runner_log import append_llm_runner_log


AGENT_ID = "shopping-list-llm-extractor"
INTENT = "add_shopping_item"
A2A_VERSION = "a2a.v1"


def _bool_env(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes"}


def runner_enabled() -> bool:
    return _bool_env("LLM_SHOPPING_EXTRACTOR_ENABLED", "false")


def runner_mode() -> str:
    return os.getenv("LLM_SHOPPING_EXTRACTOR_MODE", "shadow").strip().lower()


def runner_url() -> Optional[str]:
    value = os.getenv("LLM_AGENT_RUNNER_URL", "").strip()
    return value or None


def runner_timeout_s() -> float:
    return float(os.getenv("LLM_SHOPPING_EXTRACTOR_TIMEOUT_S", "5"))


def invoke_runner(
    *,
    text: str,
    context: Dict[str, Any],
    trace_id: str,
) -> Dict[str, Any]:
    url = runner_url()
    if not url:
        return {"ok": False, "error": {"type": "runner_unavailable", "message": "URL not set"}}

    envelope = {
        "a2a_version": A2A_VERSION,
        "message_id": f"msg-{uuid4().hex}",
        "trace_id": trace_id,
        "agent_id": AGENT_ID,
        "intent": INTENT,
        "input": {"text": text, "context": context},
        "constraints": {},
    }

    data = json.dumps(envelope, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    req = urlrequest.Request(f"{url}/a2a/v1/invoke", data=data, headers=headers)
    started = time.perf_counter()
    try:
        with urlrequest.urlopen(req, timeout=runner_timeout_s()) as resp:
            raw = resp.read()
        payload = json.loads(raw.decode("utf-8"))
        latency_ms = int((time.perf_counter() - started) * 1000)
        payload.setdefault("meta", {})
        payload["meta"]["latency_ms"] = latency_ms
        return payload
    except Exception as exc:
        latency_ms = int((time.perf_counter() - started) * 1000)
        return {
            "ok": False,
            "meta": {"latency_ms": latency_ms},
            "error": {"type": "runner_unavailable", "message": str(exc)},
        }


def shadow_invoke(
    *,
    text: str,
    context: Dict[str, Any],
    trace_id: str,
) -> None:
    if not runner_enabled():
        return

    payload = invoke_runner(text=text, context=context, trace_id=trace_id)
    meta = payload.get("meta") or {}
    output = payload.get("output") or {}
    items = output.get("items") or []
    append_llm_runner_log(
        {
            "trace_id": trace_id,
            "agent_id": AGENT_ID,
            "ok": bool(payload.get("ok")),
            "latency_ms": meta.get("latency_ms"),
            "error_type": (payload.get("error") or {}).get("type"),
            "items_count": len(items),
            "mode": runner_mode(),
        }
    )
