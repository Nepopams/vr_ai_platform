"""LLM assist mode runner (deterministic-first)."""

from __future__ import annotations

import re
import time
from dataclasses import replace
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from typing import Any, Dict, Iterable, List, Optional

from app.logging.assist_log import append_assist_log
from agent_registry.v0_loader import AgentRegistryV0Loader
from agent_registry.v0_models import AgentRegistryV0, AgentSpec, TimeoutSpec
from agent_registry.v0_runner import run as run_agent
from graphs.core_graph import detect_intent, extract_item_name as fallback_extract_item_name
from llm_policy.config import get_llm_policy_profile, is_llm_policy_enabled
from llm_policy.runtime import run_task_with_policy
from routers.assist.config import (
    assist_agent_hints_agent_id,
    assist_agent_hints_capability,
    assist_agent_hints_allowlist,
    assist_agent_hints_enabled,
    assist_agent_hints_sample_rate,
    assist_agent_hints_timeout_ms,
    assist_clarify_enabled,
    assist_entity_extraction_enabled,
    assist_mode_enabled,
    assist_normalization_enabled,
    assist_timeout_ms,
)
from routers.assist.agent_scoring import AgentHintCandidate, select_best_candidate
from routers.assist.types import (
    AssistApplication,
    AssistHints,
    AgentEntityHint,
    ClarifyHint,
    EntityHints,
    NormalizationHint,
)
from routers.partial_trust_sampling import stable_sample


ASSIST_VERSION = "assist-0.1"
_EXECUTOR = ThreadPoolExecutor(max_workers=3, thread_name_prefix="assist-mode")
_AGENT_REGISTRY_CACHE: Optional[AgentRegistryV0] = None
_AGENT_REGISTRY_ERROR: bool = False

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
    agent_hint = _run_agent_entity_hint(command, updated)
    updated, _ = _apply_entity_hints(
        updated,
        hints.entities,
        original_text=updated.get("text", ""),
        agent_hint=agent_hint,
    )
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


def _run_agent_entity_hint(command: Dict[str, Any], normalized: Dict[str, Any]) -> AgentEntityHint:
    if not assist_agent_hints_enabled():
        return AgentEntityHint(status="skipped", items=[], latency_ms=None)
    if normalized.get("intent") != "add_shopping_item":
        return AgentEntityHint(status="skipped", items=[], latency_ms=None)
    if normalized.get("item_name"):
        return AgentEntityHint(status="skipped", items=[], latency_ms=None)

    sample_rate = assist_agent_hints_sample_rate()
    if sample_rate <= 0.0:
        return AgentEntityHint(status="skipped", items=[], latency_ms=None)
    if not stable_sample(command.get("command_id"), sample_rate):
        return AgentEntityHint(status="skipped", items=[], latency_ms=None)

    capability_id = assist_agent_hints_capability()
    if not capability_id:
        return AgentEntityHint(status="skipped", items=[], latency_ms=None)

    allowlist = assist_agent_hints_allowlist()
    override_agent_id = assist_agent_hints_agent_id() or None
    candidates = _load_agent_candidates(capability_id, normalized.get("intent"), allowlist, override_agent_id)
    candidates_count = len(candidates)
    if not candidates:
        return AgentEntityHint(status="skipped", items=[], latency_ms=None, candidates_count=candidates_count)

    agent_input = {
        "text": normalized.get("text", ""),
        "context": command.get("context", {}),
        "command_id": command.get("command_id"),
    }
    text = normalized.get("text", "")
    scored_candidates: List[AgentHintCandidate] = []
    for candidate in candidates:
        spec = _apply_agent_timeout(candidate)
        try:
            output = run_agent(spec, agent_input, trace_id=command.get("trace_id"))
        except Exception:
            scored_candidates.append(
                AgentHintCandidate(
                    agent_id=candidate.agent_id,
                    status="error",
                    applicable=False,
                    latency_ms=None,
                    payload=None,
                    items=[],
                )
            )
            continue
        payload = output.payload if isinstance(output.payload, dict) else None
        items_payload = payload.get("items") if isinstance(payload, dict) else None
        items = [item for item in items_payload if isinstance(item, str)] if isinstance(items_payload, list) else []
        applicable = bool(_pick_matching_item(items, text)) if output.status == "ok" else False
        scored_candidates.append(
            AgentHintCandidate(
                agent_id=candidate.agent_id,
                status=output.status,
                applicable=applicable,
                latency_ms=output.latency_ms,
                payload=payload,
                items=items,
            )
        )

    selected, selection_reason = select_best_candidate(scored_candidates)
    if selected is None:
        return AgentEntityHint(
            status="skipped",
            items=[],
            latency_ms=None,
            candidates_count=candidates_count,
            selected_agent_id=None,
            selected_status=None,
            selection_reason=None,
        )

    if selected.status != "ok" or not isinstance(selected.payload, dict):
        return AgentEntityHint(
            status=selected.status,
            items=[],
            latency_ms=selected.latency_ms,
            candidates_count=candidates_count,
            selected_agent_id=selected.agent_id,
            selected_status=selected.status,
            selection_reason=selection_reason,
        )

    filtered = list(selected.items)
    return AgentEntityHint(
        status="ok",
        items=filtered,
        latency_ms=selected.latency_ms,
        candidates_count=candidates_count,
        selected_agent_id=selected.agent_id,
        selected_status=selected.status,
        selection_reason=selection_reason,
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


def _load_agent_registry() -> AgentRegistryV0 | None:
    global _AGENT_REGISTRY_CACHE, _AGENT_REGISTRY_ERROR
    if _AGENT_REGISTRY_CACHE is not None:
        return _AGENT_REGISTRY_CACHE
    if _AGENT_REGISTRY_ERROR:
        return None
    try:
        registry = AgentRegistryV0Loader.load()
    except Exception:
        _AGENT_REGISTRY_ERROR = True
        return None
    _AGENT_REGISTRY_CACHE = registry
    return registry


def _load_agent_candidates(
    capability_id: str,
    intent: Optional[str],
    allowlist: List[str],
    override_agent_id: Optional[str],
) -> List[AgentSpec]:
    registry = _load_agent_registry()
    if registry is None:
        return []
    allowed_ids = set(allowlist) if allowlist else set()
    candidates: List[AgentSpec] = []
    for agent in registry.agents:
        if override_agent_id and agent.agent_id != override_agent_id:
            continue
        if allowed_ids and agent.agent_id not in allowed_ids:
            continue
        if not agent.enabled:
            continue
        if agent.mode != "assist":
            continue
        if len(agent.capabilities) != 1:
            continue
        capability = agent.capabilities[0]
        if capability.capability_id != capability_id:
            continue
        if not _agent_intent_allowed(capability.allowed_intents, intent):
            continue
        candidates.append(agent)
    return candidates


def _apply_agent_timeout(agent: AgentSpec) -> AgentSpec:
    timeout_ms = assist_agent_hints_timeout_ms()
    if timeout_ms <= 0:
        return agent
    timeouts = TimeoutSpec(timeout_ms=timeout_ms)
    return replace(agent, timeouts=timeouts)


def _agent_intent_allowed(allowed_intents: Iterable[str], intent: Optional[str]) -> bool:
    if not intent:
        return False
    allowed = list(allowed_intents)
    if allowed and intent not in allowed:
        return False
    return True


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
    agent_hint: Optional[AgentEntityHint] = None,
) -> tuple[Dict[str, Any], bool]:
    updated = dict(normalized)
    accepted = False

    agent_status = "skipped"
    agent_latency_ms = None
    agent_items_count = 0
    agent_applied = False
    agent_candidates_count = 0
    agent_selected_id = None
    agent_selected_status = None
    agent_selection_reason = None
    if agent_hint is not None:
        agent_status = agent_hint.status
        agent_latency_ms = agent_hint.latency_ms
        agent_items_count = len(agent_hint.items)
        agent_candidates_count = agent_hint.candidates_count
        agent_selected_id = agent_hint.selected_agent_id
        agent_selected_status = agent_hint.selected_status
        agent_selection_reason = agent_hint.selection_reason
        if (
            agent_hint.status == "ok"
            and normalized.get("intent") == "add_shopping_item"
            and not updated.get("item_name")
        ):
            item = _pick_matching_item(agent_hint.items, original_text)
            if item:
                updated["item_name"] = item
                agent_applied = True
                accepted = True

    llm_status = "skipped"
    llm_error_type: Optional[str] = "no_hint"
    llm_latency_ms = None
    if hint is not None:
        llm_latency_ms = hint.latency_ms
        if hint.error_type:
            llm_status = "error"
            llm_error_type = hint.error_type
        else:
            llm_status = "ok"
            llm_error_type = None
            if normalized.get("intent") == "add_shopping_item" and not updated.get("item_name"):
                item = _pick_matching_item(hint.items, original_text)
                if item:
                    updated["item_name"] = item
                    accepted = True

    status = llm_status
    error_type = llm_error_type
    if agent_applied and llm_status in {"skipped", "error"}:
        status = "ok"
        error_type = None

    _log_step(
        "entities",
        status,
        hint,
        accepted=accepted,
        error_type=error_type,
        latency_ms=llm_latency_ms,
        agent_hint_status=agent_status,
        agent_hint_latency_ms=agent_latency_ms,
        agent_hint_items_count=agent_items_count,
        agent_hint_applied=agent_applied,
        agent_hint_candidates_count=agent_candidates_count,
        agent_hint_selected_agent_id=agent_selected_id,
        agent_hint_selected_status=agent_selected_status,
        agent_hint_selection_reason=agent_selection_reason,
    )
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
    agent_hint_status: Optional[str] = None,
    agent_hint_latency_ms: Optional[int] = None,
    agent_hint_items_count: Optional[int] = None,
    agent_hint_applied: Optional[bool] = None,
    agent_hint_candidates_count: Optional[int] = None,
    agent_hint_selected_agent_id: Optional[str] = None,
    agent_hint_selected_status: Optional[str] = None,
    agent_hint_selection_reason: Optional[str] = None,
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
    record = {
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
    if agent_hint_status is not None:
        record["agent_hint_status"] = agent_hint_status
    if agent_hint_latency_ms is not None:
        record["agent_hint_latency_ms"] = agent_hint_latency_ms
    if agent_hint_items_count is not None:
        record["agent_hint_items_count"] = agent_hint_items_count
    if agent_hint_applied is not None:
        record["agent_hint_applied"] = agent_hint_applied
    if agent_hint_candidates_count is not None:
        record["agent_hint_candidates_count"] = agent_hint_candidates_count
    if agent_hint_selected_agent_id is not None:
        record["agent_hint_selected_agent_id"] = agent_hint_selected_agent_id
    if agent_hint_selected_status is not None:
        record["agent_hint_selected_status"] = agent_hint_selected_status
    if agent_hint_selection_reason is not None:
        record["agent_hint_selection_reason"] = agent_hint_selection_reason
    append_assist_log(record)
