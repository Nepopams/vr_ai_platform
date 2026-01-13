"""LLM candidate generation for partial trust corridor (internal-only)."""

from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from typing import Any, Dict, Mapping, Optional

from llm_policy.config import (
    get_llm_policy_allow_placeholders,
    get_llm_policy_path,
    get_llm_policy_profile,
    is_llm_policy_enabled,
)
from llm_policy.loader import LlmPolicyLoader
from llm_policy.runtime import TaskRunResult, run_task_with_policy
from routers.partial_trust_types import LLMDecisionCandidate


PARTIAL_TRUST_TASK_ID = "partial_trust_shopping"
_EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix="partial-trust")

_CANDIDATE_SCHEMA: Mapping[str, object] = {
    "type": "object",
    "properties": {
        "item_name": {"type": "string", "minLength": 1},
        "quantity": {"type": "string"},
        "unit": {"type": "string"},
        "list_id": {"type": "string"},
        "confidence": {"type": "number"},
    },
    "required": ["item_name"],
    "additionalProperties": False,
}


def generate_llm_candidate(
    command: Dict[str, Any],
    *,
    trace_id: Optional[str] = None,
    timeout_ms: Optional[int] = None,
    profile_id: Optional[str] = None,
) -> LLMDecisionCandidate | None:
    candidate, _error_type = generate_llm_candidate_with_meta(
        command,
        trace_id=trace_id,
        timeout_ms=timeout_ms,
        profile_id=profile_id,
    )
    return candidate


def generate_llm_candidate_with_meta(
    command: Dict[str, Any],
    *,
    trace_id: Optional[str] = None,
    timeout_ms: Optional[int] = None,
    profile_id: Optional[str] = None,
) -> tuple[LLMDecisionCandidate | None, str | None]:
    text = command.get("text", "")
    if not isinstance(text, str) or not text.strip():
        return None, "empty_text"

    if not is_llm_policy_enabled():
        return None, "policy_disabled"

    started = time.monotonic()
    try:
        result = _run_policy_task(
            text=text,
            trace_id=trace_id,
            timeout_ms=timeout_ms,
            profile_id=profile_id,
        )
    except Exception:
        return None, "llm_error"
    if result is None:
        return None, "timeout"
    if result.status != "ok" or result.data is None:
        return None, result.error_type or "llm_error"

    payload = result.data
    item_name = payload.get("item_name")
    if not isinstance(item_name, str) or not item_name.strip():
        return None, "invalid_schema"

    item_payload: Dict[str, Any] = {"name": item_name.strip()}
    quantity = payload.get("quantity")
    if isinstance(quantity, str) and quantity.strip():
        item_payload["quantity"] = quantity.strip()
    unit = payload.get("unit")
    if isinstance(unit, str) and unit.strip():
        item_payload["unit"] = unit.strip()
    list_id = payload.get("list_id")
    if isinstance(list_id, str) and list_id.strip():
        item_payload["list_id"] = list_id.strip()

    proposed_actions = [
        {
            "action": "propose_add_shopping_item",
            "payload": {"item": item_payload},
        }
    ]
    latency_ms = int((time.monotonic() - started) * 1000)
    model_meta = {
        "profile": result.profile,
        "task_id": PARTIAL_TRUST_TASK_ID,
        "escalated": result.escalated,
    }
    confidence = _coerce_confidence(payload.get("confidence"))
    candidate = LLMDecisionCandidate(
        intent="add_shopping_item",
        job_type="add_shopping_item",
        proposed_actions=proposed_actions,
        clarify_question=None,
        clarify_missing_fields=None,
        confidence=confidence,
        model_meta=model_meta,
        latency_ms=latency_ms,
        error_type=None,
    )
    return candidate, None


def _run_policy_task(
    *,
    text: str,
    trace_id: Optional[str],
    timeout_ms: Optional[int],
    profile_id: Optional[str],
) -> TaskRunResult | None:
    prompt = _build_prompt(text)
    profile = profile_id or get_llm_policy_profile()
    future = _EXECUTOR.submit(
        run_task_with_policy,
        task_id=PARTIAL_TRUST_TASK_ID,
        prompt=prompt,
        schema=_CANDIDATE_SCHEMA,
        profile=profile,
        trace_id=trace_id,
        policy_enabled=True,
    )
    if timeout_ms is None or timeout_ms <= 0:
        try:
            return future.result()
        except Exception:
            return None
    try:
        return future.result(timeout=timeout_ms / 1000.0)
    except FutureTimeout:
        return None
    except Exception:
        return None


def policy_route_available(profile_id: Optional[str] = None) -> bool:
    if not is_llm_policy_enabled():
        return False
    try:
        policy = LlmPolicyLoader.load(
            enabled=True,
            path_override=get_llm_policy_path(),
            allow_placeholders=get_llm_policy_allow_placeholders(),
        )
    except Exception:
        return False
    if policy is None:
        return False
    profile = profile_id or get_llm_policy_profile()
    task_routes = policy.routing.get(PARTIAL_TRUST_TASK_ID, {})
    return profile in task_routes


def _build_prompt(text: str) -> str:
    schema_text = json.dumps(_CANDIDATE_SCHEMA, ensure_ascii=False)
    return (
        "Извлеки параметры покупки из текста пользователя. "
        "Верни только JSON по схеме.\n"
        f"Схема: {schema_text}\n"
        f"Текст: {text}"
    )


def _coerce_confidence(value: object) -> float | None:
    if isinstance(value, (int, float)):
        return max(0.0, min(float(value), 1.0))
    return None
