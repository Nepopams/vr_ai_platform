"""LLM assist mode runner (deterministic-first)."""

from __future__ import annotations

import re
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from typing import Any, Dict, Iterable, List, Optional

from app.logging.assist_log import append_assist_log
from graphs.core_graph import detect_intent, extract_item_name as fallback_extract_item_name
from llm_policy.config import get_llm_policy_profile, is_llm_policy_enabled
from llm_policy.runtime import run_task_with_policy
from routers.assist.config import (
    assist_clarify_enabled,
    assist_entity_extraction_enabled,
    assist_mode_enabled,
    assist_normalization_enabled,
    assist_timeout_ms,
)
from routers.assist.types import (
    AssistApplication,
    AssistHints,
    ClarifyHint,
    EntityHints,
    NormalizationHint,
)


ASSIST_VERSION = "assist-0.1"
_EXECUTOR = ThreadPoolExecutor(max_workers=3, thread_name_prefix="assist-mode")

_NORMALIZATION_TASK_ID = "assist_normalization"
_ENTITY_TASK_ID = "assist_entity_extraction"
_CLARIFY_TASK_ID = "assist_clarify"

_NORMALIZATION_SCHEMA = {
    "type": "object",
    "properties": {
        "normalized_text": {"type": "string", "minLength": 1},
        "intent_hint": {"type": "string"},
        "entities_hint": {"type": "object"},
        "confidence": {"type": "number"},
    },
    "required": ["normalized_text"],
    "additionalProperties": False,
}

_ENTITY_SCHEMA = {
    "type": "object",
    "properties": {
        "items": {"type": "array", "items": {"type": "string"}},
        "task_hints": {"type": "object"},
        "confidence": {"type": "number"},
    },
    "required": ["items"],
    "additionalProperties": False,
}

_CLARIFY_SCHEMA = {
    "type": "object",
    "properties": {
        "question": {"type": "string", "minLength": 1},
        "missing_fields": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "number"},
    },
    "required": ["question"],
    "additionalProperties": False,
}


def apply_assist_hints(command: Dict[str, Any], normalized: Dict[str, Any]) -> AssistApplication:
    if not assist_mode_enabled():
        return AssistApplication(normalized=normalized, clarify_question=None, clarify_missing_fields=None)

    hints = _build_assist_hints(command, normalized)
    updated, _ = _apply_normalization_hint(normalized, hints.normalization)
    updated, _ = _apply_entity_hints(updated, hints.entities, original_text=normalized.get("text", ""))
    clarify_question, clarify_missing_fields = _select_clarify_hint(
        hints.clarify, updated, command.get("text", "")
    )

    return AssistApplication(
        normalized=updated,
        clarify_question=clarify_question,
        clarify_missing_fields=clarify_missing_fields,
    )


def _build_assist_hints(command: Dict[str, Any], normalized: Dict[str, Any]) -> AssistHints:
    normalization = None
    entities = None
    clarify = None

    if assist_normalization_enabled():
        normalization = _run_normalization_hint(normalized.get("text", ""))
    else:
        _log_step("normalizer", "skipped", None, accepted=False, error_type="disabled")

    if assist_entity_extraction_enabled():
        entities = _run_entity_hint(normalized.get("text", ""))
    else:
        _log_step("entities", "skipped", None, accepted=False, error_type="disabled")

    if assist_clarify_enabled():
        clarify = _run_clarify_hint(command.get("text", ""), normalized.get("intent"))
    else:
        _log_step("clarify", "skipped", None, accepted=False, error_type="disabled")

    return AssistHints(normalization=normalization, entities=entities, clarify=clarify)


def _run_normalization_hint(text: str) -> NormalizationHint:
    result = _run_llm_task(
        task_id=_NORMALIZATION_TASK_ID,
        prompt=_build_normalization_prompt(text),
        schema=_NORMALIZATION_SCHEMA,
    )
    if result["status"] != "ok":
        return NormalizationHint(
            normalized_text=None,
            intent_hint=None,
            entities_hint=None,
            confidence=None,
            error_type=result["error_type"],
            latency_ms=result.get("latency_ms"),
        )
    payload = result["payload"]
    return NormalizationHint(
        normalized_text=payload.get("normalized_text"),
        intent_hint=payload.get("intent_hint"),
        entities_hint=payload.get("entities_hint"),
        confidence=payload.get("confidence"),
        error_type=None,
        latency_ms=result.get("latency_ms"),
    )


def _run_entity_hint(text: str) -> EntityHints:
    result = _run_llm_task(
        task_id=_ENTITY_TASK_ID,
        prompt=_build_entity_prompt(text),
        schema=_ENTITY_SCHEMA,
    )
    if result["status"] != "ok":
        return EntityHints(
            items=[],
            task_hints={},
            confidence=None,
            error_type=result["error_type"],
            latency_ms=result.get("latency_ms"),
        )
    payload = result["payload"]
    items = [item for item in payload.get("items", []) if isinstance(item, str)]
    task_hints = payload.get("task_hints") if isinstance(payload.get("task_hints"), dict) else {}
    return EntityHints(
        items=items,
        task_hints=task_hints,
        confidence=payload.get("confidence"),
        error_type=None,
        latency_ms=result.get("latency_ms"),
    )


def _run_clarify_hint(text: str, intent: Optional[str]) -> ClarifyHint:
    result = _run_llm_task(
        task_id=_CLARIFY_TASK_ID,
        prompt=_build_clarify_prompt(text, intent),
        schema=_CLARIFY_SCHEMA,
    )
    if result["status"] != "ok":
        return ClarifyHint(
            question=None,
            missing_fields=None,
            confidence=None,
            error_type=result["error_type"],
            latency_ms=result.get("latency_ms"),
        )
    payload = result["payload"]
    missing_fields = payload.get("missing_fields")
    if not isinstance(missing_fields, list):
        missing_fields = None
    return ClarifyHint(
        question=payload.get("question"),
        missing_fields=missing_fields,
        confidence=payload.get("confidence"),
        error_type=None,
        latency_ms=result.get("latency_ms"),
    )


def _apply_normalization_hint(
    normalized: Dict[str, Any], hint: Optional[NormalizationHint]
) -> tuple[Dict[str, Any], bool]:
    if hint is None or not hint.normalized_text:
        _log_step(
            "normalizer",
            "skipped",
            None,
            accepted=False,
            error_type=hint.error_type if hint else "no_hint",
            latency_ms=hint.latency_ms if hint else None,
        )
        return dict(normalized), False

    original_text = normalized.get("text", "")
    candidate = hint.normalized_text.strip()
    if not _can_accept_normalized_text(original_text, candidate):
        _log_step("normalizer", "ok", None, accepted=False, error_type="rejected", latency_ms=hint.latency_ms)
        return dict(normalized), False

    updated = dict(normalized)
    updated["text"] = candidate
    updated["intent"] = detect_intent(candidate) if candidate else "clarify_needed"
    updated["item_name"] = (
        fallback_extract_item_name(candidate) if updated["intent"] == "add_shopping_item" else None
    )
    updated["task_title"] = candidate if updated["intent"] == "create_task" else None
    _log_step("normalizer", "ok", None, accepted=True, error_type=None, latency_ms=hint.latency_ms)
    return updated, True


def _apply_entity_hints(
    normalized: Dict[str, Any],
    hint: Optional[EntityHints],
    *,
    original_text: str,
) -> tuple[Dict[str, Any], bool]:
    if hint is None:
        _log_step("entities", "skipped", None, accepted=False, error_type="no_hint", latency_ms=None)
        return dict(normalized), False

    if hint.error_type:
        _log_step("entities", "error", hint, accepted=False, error_type=hint.error_type, latency_ms=hint.latency_ms)
        return dict(normalized), False

    updated = dict(normalized)
    accepted = False
    if normalized.get("intent") == "add_shopping_item" and not normalized.get("item_name"):
        item = _pick_matching_item(hint.items, original_text)
        if item:
            updated["item_name"] = item
            accepted = True
    _log_step("entities", "ok", hint, accepted=accepted, error_type=None, latency_ms=hint.latency_ms)
    return updated, accepted


def _select_clarify_hint(
    hint: Optional[ClarifyHint],
    normalized: Dict[str, Any],
    original_text: str,
) -> tuple[Optional[str], Optional[List[str]]]:
    if hint is None:
        _log_step("clarify", "skipped", None, accepted=False, error_type="no_hint", latency_ms=None)
        return None, None

    if hint.error_type:
        _log_step("clarify", "error", hint, accepted=False, error_type=hint.error_type, latency_ms=hint.latency_ms)
        return None, None

    question = hint.question.strip() if hint.question else ""
    if not _clarify_question_is_safe(question, normalized.get("intent"), original_text):
        _log_step("clarify", "ok", hint, accepted=False, error_type="rejected", latency_ms=hint.latency_ms)
        return None, None

    _log_step("clarify", "ok", hint, accepted=True, error_type=None, latency_ms=hint.latency_ms)
    return question, hint.missing_fields


def _run_llm_task(*, task_id: str, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
    if not is_llm_policy_enabled():
        return {"status": "skipped", "payload": {}, "error_type": "policy_disabled", "latency_ms": None}

    start = time.monotonic()
    timeout_s = max(assist_timeout_ms(), 1) / 1000
    try:
        payload = _run_with_timeout(
            lambda: run_task_with_policy(
                task_id=task_id,
                prompt=prompt,
                schema=schema,
                profile=get_llm_policy_profile(),
                trace_id=None,
                policy_enabled=True,
            ),
            timeout_s,
        )
    except FutureTimeout:
        return {"status": "error", "payload": {}, "error_type": "timeout", "latency_ms": None}
    except Exception as exc:
        return {"status": "error", "payload": {}, "error_type": type(exc).__name__, "latency_ms": None}

    latency_ms = int((time.monotonic() - start) * 1000)
    if payload.status == "ok" and payload.data is not None:
        return {"status": "ok", "payload": payload.data, "error_type": None, "latency_ms": latency_ms}
    error_type = payload.error_type or "llm_error"
    return {"status": "error", "payload": {}, "error_type": error_type, "latency_ms": latency_ms}


def _run_with_timeout(func, timeout_s: float):
    future = _EXECUTOR.submit(func)
    return future.result(timeout=timeout_s)


def _build_normalization_prompt(text: str) -> str:
    return (
        "Нормализуй пользовательский текст: исправь опечатки, убери шум, приведи к доменной лексике. "
        "Верни JSON с normalized_text и при необходимости intent_hint/entities_hint.\n"
        f"Текст: {text}"
    )


def _build_entity_prompt(text: str) -> str:
    return (
        "Извлеки сущности для shopping/task. "
        "Верни JSON со списком items и task_hints.\n"
        f"Текст: {text}"
    )


def _build_clarify_prompt(text: str, intent: Optional[str]) -> str:
    intent_label = intent or "unknown"
    return (
        "Предложи один уточняющий вопрос и missing_fields. "
        "Вопрос должен быть конкретным и релевантным.\n"
        f"Интент: {intent_label}\n"
        f"Текст: {text}"
    )


def _can_accept_normalized_text(original: str, candidate: str) -> bool:
    if not candidate:
        return False
    if len(candidate) > max(len(original) * 2, 10):
        return False
    original_tokens = _tokens(original)
    candidate_tokens = _tokens(candidate)
    if not original_tokens or not candidate_tokens:
        return False
    return bool(original_tokens & candidate_tokens)


def _tokens(text: str) -> set[str]:
    words = re.findall(r"[\\w\\-]+", text.lower())
    return set(words)


def _pick_matching_item(items: Iterable[str], text: str) -> Optional[str]:
    lowered = text.lower()
    for item in items:
        candidate = item.strip()
        if candidate and candidate.lower() in lowered:
            return candidate
    return None


def _clarify_question_is_safe(question: str, intent: Optional[str], original_text: str) -> bool:
    if not question:
        return False
    if len(question) < 5:
        return False
    if len(question) > 200:
        return False
    lowered = question.lower()
    if original_text and original_text.lower() in lowered:
        return False
    if intent in {"add_shopping_item", "create_task"}:
        return True
    return "?" in question


def _summarize_entities(items: Iterable[str]) -> Dict[str, Any]:
    items_list = list(items)
    keys = ["items"] if items_list else []
    counts = {"items": len(items_list)} if keys else {}
    return {"keys": keys, "counts": counts}


def _log_step(
    step: str,
    status: str,
    payload: Any,
    *,
    accepted: bool,
    error_type: Optional[str],
    latency_ms: Optional[int] = None,
) -> None:
    entities_summary = None
    missing_fields_count = None
    if step == "entities":
        if isinstance(payload, dict):
            entities_summary = _summarize_entities(payload.get("items", []))
        elif hasattr(payload, "items"):
            entities_summary = _summarize_entities(payload.items)
    if step == "clarify" and hasattr(payload, "missing_fields") and payload.missing_fields:
        missing_fields_count = len(payload.missing_fields)
    append_assist_log(
        {
            "step": step,
            "status": status,
            "accepted": accepted,
            "error_type": error_type,
            "latency_ms": latency_ms,
            "entities_summary": entities_summary,
            "missing_fields_count": missing_fields_count,
            "clarify_used": accepted if step == "clarify" else None,
            "assist_version": ASSIST_VERSION,
        }
    )

