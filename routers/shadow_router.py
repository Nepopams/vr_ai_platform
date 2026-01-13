"""Shadow router implementation (best-effort, zero-impact)."""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict
from uuid import uuid4

from app.logging.shadow_router_log import append_shadow_router_log
from llm_policy.config import get_llm_policy_profile, is_llm_policy_enabled
from llm_policy.tasks import extract_shopping_item_name
from routers.shadow_config import (
    shadow_router_enabled,
    shadow_router_mode,
    shadow_router_timeout_ms,
)
from routers.shadow_types import RouterSuggestion


ROUTER_VERSION = "shadow-router-0.1"
_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="shadow-router")


def start_shadow_router(command: Dict[str, Any], normalized: Dict[str, Any]) -> None:
    if not shadow_router_enabled():
        return

    payload = {
        "command_id": command.get("command_id"),
        "trace_id": _resolve_trace_id(command),
        "text": normalized.get("text", ""),
        "normalized_intent": normalized.get("intent"),
        "capabilities": sorted(normalized.get("capabilities", [])),
    }
    _submit_shadow_task(payload)


def _resolve_trace_id(command: Dict[str, Any]) -> str:
    trace_id = command.get("trace_id")
    if trace_id:
        return str(trace_id)
    return f"shadow-{uuid4().hex}"


def _submit_shadow_task(payload: Dict[str, Any]) -> None:
    try:
        future = _EXECUTOR.submit(_run_shadow_router, payload)
        future.add_done_callback(_consume_future_error)
    except Exception:
        _log_shadow_result(
            payload,
            status="error",
            error_type="executor_unavailable",
            suggestion=None,
            latency_ms=0,
        )


def _consume_future_error(future) -> None:
    try:
        future.result()
    except Exception:
        # Ошибки фонового потока глушим.
        return


def _run_shadow_router(payload: Dict[str, Any]) -> None:
    started = time.monotonic()
    timeout_ms = shadow_router_timeout_ms()
    mode = shadow_router_mode()

    if mode != "shadow":
        _log_shadow_result(
            payload,
            status="skipped",
            error_type="invalid_mode",
            suggestion=None,
            latency_ms=0,
        )
        return

    if not is_llm_policy_enabled():
        _log_shadow_result(
            payload,
            status="skipped",
            error_type="policy_disabled",
            suggestion=None,
            latency_ms=0,
        )
        return

    try:
        suggestion = _build_suggestion(payload)
        latency_ms = int((time.monotonic() - started) * 1000)
        if latency_ms > timeout_ms:
            _log_shadow_result(
                payload,
                status="error",
                error_type="timeout_exceeded",
                suggestion=suggestion,
                latency_ms=latency_ms,
            )
            return
        status = "ok" if suggestion.error_type is None else "error"
        _log_shadow_result(
            payload,
            status=status,
            error_type=suggestion.error_type,
            suggestion=suggestion,
            latency_ms=latency_ms,
        )
    except Exception as exc:
        latency_ms = int((time.monotonic() - started) * 1000)
        _log_shadow_result(
            payload,
            status="error",
            error_type=type(exc).__name__,
            suggestion=None,
            latency_ms=latency_ms,
        )


def _build_suggestion(payload: Dict[str, Any]) -> RouterSuggestion:
    text = payload.get("text", "")
    trace_id = payload.get("trace_id")
    extraction = extract_shopping_item_name(
        text,
        policy_enabled=True,
        trace_id=trace_id,
    )
    item_name = extraction.item_name
    suggested_intent = "add_shopping_item" if item_name else None
    entities: Dict[str, Any] = {}
    if item_name:
        entities["item"] = {"name": item_name}
    missing_fields = ["item.name"] if suggested_intent and not item_name else None
    explain = "llm_policy_shopping_extraction" if extraction.used_policy else "policy_disabled"
    model_meta = {
        "profile": get_llm_policy_profile(),
        "task_id": "shopping_extraction",
    }
    return RouterSuggestion(
        suggested_intent=suggested_intent,
        entities=entities,
        missing_fields=missing_fields,
        clarify_question=None,
        confidence=None,
        explain=explain,
        error_type=extraction.error_type,
        latency_ms=None,
        model_meta=model_meta,
    )


def _log_shadow_result(
    payload: Dict[str, Any],
    *,
    status: str,
    error_type: str | None,
    suggestion: RouterSuggestion | None,
    latency_ms: int,
) -> None:
    append_shadow_router_log(
        {
            "trace_id": payload.get("trace_id"),
            "command_id": payload.get("command_id"),
            "router_version": ROUTER_VERSION,
            "router_strategy": "v2",
            "status": status,
            "latency_ms": latency_ms,
            "error_type": error_type,
            "suggested_intent": suggestion.suggested_intent if suggestion else None,
            "missing_fields": suggestion.missing_fields if suggestion else None,
            "clarify_question": suggestion.clarify_question if suggestion else None,
            "entities_summary": _summarize_entities(suggestion.entities) if suggestion else None,
            "confidence": suggestion.confidence if suggestion else None,
            "model_meta": suggestion.model_meta if suggestion else None,
            "baseline_intent": payload.get("normalized_intent"),
            "baseline_action": None,
            "baseline_job_type": None,
        }
    )


def _summarize_entities(entities: Dict[str, Any]) -> Dict[str, Any]:
    keys = sorted(entities.keys())
    counts = {key: 1 for key in keys}
    return {"keys": keys, "counts": counts}
