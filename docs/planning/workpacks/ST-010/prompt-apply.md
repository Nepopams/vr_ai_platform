# Codex APPLY Prompt — ST-010: LLM Extraction and Assist Mode Multi-Item Support

## Role

You are an implementation agent. Apply changes exactly as specified below.

## Environment

- Python binary: `python3` (NOT `python`)
- All tests: `python3 -m pytest tests/ -v`

## STOP-THE-LINE

If any instruction contradicts what you see in the codebase, STOP and report.

---

## Context

Implementing ST-010: multi-item support in LLM extraction and assist mode.

**ADR-006-P decisions:**
- Internal model: `items: List[dict]` with `{name, quantity, unit}`
- Quantity type: `string`
- Backward compat: `item_name` kept as computed property (first item's name)

**Dependency:** ST-009 already added `extract_items()` to `graphs/core_graph.py` and
`normalized["items"]` to v2 normalize. This story upgrades the LLM and assist layers.

---

## Step 1: Update `llm_policy/tasks.py`

Replace the ENTIRE file content with:

```python
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Mapping

from graphs.core_graph import extract_item_name as fallback_extract_item_name
from llm_policy.config import get_llm_policy_profile, is_llm_policy_enabled
from llm_policy.runtime import TaskRunResult, run_task_with_policy

SHOPPING_EXTRACTION_TASK_ID = "shopping_extraction"
SHOPPING_EXTRACTION_SCHEMA: Mapping[str, object] = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "quantity": {"type": ["string", "null"]},
                    "unit": {"type": ["string", "null"]},
                },
                "required": ["name"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["items"],
    "additionalProperties": False,
}


@dataclass(frozen=True)
class ExtractionResult:
    items: list[dict]
    used_policy: bool
    error_type: str | None

    @property
    def item_name(self) -> str | None:
        if self.items:
            return self.items[0].get("name")
        return None


def extract_shopping_item_name(
    text: str,
    *,
    policy_enabled: bool | None = None,
    profile: str | None = None,
    trace_id: str | None = None,
) -> ExtractionResult:
    enabled = is_llm_policy_enabled() if policy_enabled is None else policy_enabled
    if not enabled:
        fallback_name = fallback_extract_item_name(text)
        items = [{"name": fallback_name}] if fallback_name else []
        return ExtractionResult(
            items=items,
            used_policy=False,
            error_type=None,
        )

    result = _run_policy_extraction(
        text,
        profile=profile,
        trace_id=trace_id,
        policy_enabled=enabled,
    )
    if result.status == "skipped" and result.error_type == "policy_disabled":
        fallback_name = fallback_extract_item_name(text)
        items = [{"name": fallback_name}] if fallback_name else []
        return ExtractionResult(
            items=items,
            used_policy=False,
            error_type=None,
        )

    if result.status == "ok" and result.data is not None:
        raw_items = result.data.get("items", [])
        items = [item for item in raw_items if isinstance(item, dict) and item.get("name")]
        return ExtractionResult(items=items, used_policy=True, error_type=None)

    return ExtractionResult(items=[], used_policy=True, error_type=result.error_type)


def _run_policy_extraction(
    text: str,
    *,
    profile: str | None,
    trace_id: str | None,
    policy_enabled: bool,
) -> TaskRunResult:
    prompt = _build_shopping_prompt(text)
    return run_task_with_policy(
        task_id=SHOPPING_EXTRACTION_TASK_ID,
        prompt=prompt,
        schema=SHOPPING_EXTRACTION_SCHEMA,
        profile=profile or get_llm_policy_profile(),
        trace_id=trace_id,
        policy_enabled=policy_enabled,
    )


def _build_shopping_prompt(text: str) -> str:
    schema_text = json.dumps(SHOPPING_EXTRACTION_SCHEMA, ensure_ascii=False)
    return (
        "Извлеки все товары из текста пользователя. "
        "Верни JSON со списком items по схеме.\n"
        f"Схема: {schema_text}\n"
        f"Текст: {text}"
    )
```

---

## Step 2: Update `routers/assist/types.py`

Replace the ENTIRE file content with:

```python
"""Internal types for LLM assist hints (not part of public contracts)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class NormalizationHint:
    normalized_text: Optional[str]
    intent_hint: Optional[str]
    entities_hint: Optional[Dict[str, object]]
    confidence: Optional[float]
    error_type: Optional[str]
    latency_ms: Optional[int]


@dataclass(frozen=True)
class EntityHints:
    items: List[dict]
    task_hints: Dict[str, object]
    confidence: Optional[float]
    error_type: Optional[str]
    latency_ms: Optional[int]


@dataclass(frozen=True)
class AgentEntityHint:
    status: str
    items: List[dict]
    latency_ms: Optional[int]
    candidates_count: int = 0
    selected_agent_id: Optional[str] = None
    selected_status: Optional[str] = None
    selection_reason: Optional[str] = None


@dataclass(frozen=True)
class ClarifyHint:
    question: Optional[str]
    missing_fields: Optional[List[str]]
    confidence: Optional[float]
    error_type: Optional[str]
    latency_ms: Optional[int]


@dataclass(frozen=True)
class AssistHints:
    normalization: Optional[NormalizationHint]
    entities: Optional[EntityHints]
    clarify: Optional[ClarifyHint]


@dataclass(frozen=True)
class AssistApplication:
    normalized: Dict[str, object]
    clarify_question: Optional[str]
    clarify_missing_fields: Optional[List[str]]
```

---

## Step 3: Update `routers/assist/agent_scoring.py`

Replace the ENTIRE file content with:

```python
"""Deterministic scoring policy for assist agent hints (v0)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence


_STATUS_RANK = {"ok": 0, "rejected": 1, "error": 2, "skipped": 3}
_MAX_LATENCY = 1_000_000_000


@dataclass(frozen=True)
class AgentHintCandidate:
    agent_id: str
    status: str
    applicable: bool
    latency_ms: Optional[int]
    payload: dict | None
    items: list[dict]


def select_best_candidate(
    candidates: Sequence[AgentHintCandidate],
) -> tuple[AgentHintCandidate | None, str | None]:
    if not candidates:
        return None, None
    ordered = sorted(candidates, key=_score)
    best = ordered[0]
    if len(ordered) == 1:
        return best, "single_candidate"
    reason = _selection_reason(best, ordered[1])
    return best, reason


def _score(candidate: AgentHintCandidate) -> tuple[int, int, int, str]:
    status_rank = _STATUS_RANK.get(candidate.status, 99)
    applicable_rank = 0 if candidate.applicable else 1
    if status_rank != 0:
        applicable_rank = 0
    latency_rank = candidate.latency_ms if candidate.latency_ms is not None else _MAX_LATENCY
    return (status_rank, applicable_rank, latency_rank, candidate.agent_id)


def _selection_reason(best: AgentHintCandidate, runner_up: AgentHintCandidate) -> str:
    best_score = _score(best)
    runner_score = _score(runner_up)
    if best_score[0] != runner_score[0]:
        return "status_rank"
    if best_score[1] != runner_score[1]:
        return "applicable_tiebreak"
    if best_score[2] != runner_score[2]:
        return "latency_tiebreak"
    return "agent_id_tiebreak"
```

---

## Step 4: Update `routers/assist/runner.py`

Replace the ENTIRE file content with:

```python
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
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "quantity": {"type": ["string", "null"]},
                    "unit": {"type": ["string", "null"]},
                },
                "required": ["name"],
                "additionalProperties": False,
            },
        },
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
    items = [item for item in payload.get("items", []) if isinstance(item, dict) and item.get("name")]
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
        items: List[dict] = []
        if isinstance(items_payload, list):
            for item in items_payload:
                if isinstance(item, dict) and item.get("name"):
                    items.append(item)
                elif isinstance(item, str) and item.strip():
                    items.append({"name": item.strip()})
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
        ):
            matched = _pick_matching_items(agent_hint.items, original_text)
            if matched:
                updated["items"] = matched
                if not updated.get("item_name"):
                    updated["item_name"] = matched[0].get("name")
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
            if normalized.get("intent") == "add_shopping_item":
                matched = _pick_matching_items(hint.items, original_text)
                if matched:
                    updated["items"] = matched
                    if not updated.get("item_name"):
                        updated["item_name"] = matched[0].get("name")
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
        "Извлеки все сущности для shopping/task. "
        "Верни JSON со списком items (объекты с name, quantity, unit) и task_hints.\n"
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


def _pick_matching_item(items: Iterable[dict], text: str) -> Optional[dict]:
    """Return the first item whose name appears in text."""
    lowered = text.lower()
    for item in items:
        name = item.get("name", "") if isinstance(item, dict) else str(item)
        candidate = name.strip()
        if candidate and candidate.lower() in lowered:
            return item
    return None


def _pick_matching_items(items: Iterable[dict], text: str) -> List[dict]:
    """Return all items whose name appears in text."""
    lowered = text.lower()
    matched: List[dict] = []
    for item in items:
        name = item.get("name", "") if isinstance(item, dict) else str(item)
        candidate = name.strip()
        if candidate and candidate.lower() in lowered:
            matched.append(item)
    return matched


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


def _summarize_entities(items: Iterable) -> Dict[str, Any]:
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
```

---

## Step 5: Update `tests/test_assist_mode.py`

In `tests/test_assist_mode.py`, update the `test_assist_entity_whitelist` test.

Find line 117:
```python
    entity_hint = EntityHints(
        items=["хлеб"],
```

Replace with:
```python
    entity_hint = EntityHints(
        items=[{"name": "хлеб"}],
```

This is the ONLY change in this file. All other tests use `NormalizationHint` and `ClarifyHint` which are unchanged.

---

## Step 6: Create `tests/test_llm_extraction_multi_item.py`

Create this NEW file with the following content:

```python
"""Tests for multi-item LLM extraction (ST-010)."""

from llm_policy.tasks import ExtractionResult, SHOPPING_EXTRACTION_SCHEMA


def test_shopping_schema_has_items_array():
    """AC-1: Schema defines items as array of objects."""
    props = SHOPPING_EXTRACTION_SCHEMA["properties"]
    assert "items" in props
    items_schema = props["items"]
    assert items_schema["type"] == "array"
    item_obj = items_schema["items"]
    assert item_obj["type"] == "object"
    assert "name" in item_obj["properties"]
    assert "quantity" in item_obj["properties"]
    assert "unit" in item_obj["properties"]
    assert item_obj["required"] == ["name"]


def test_extraction_result_items_list():
    """AC-2: ExtractionResult.items returns list of dicts."""
    result = ExtractionResult(
        items=[{"name": "молоко"}, {"name": "хлеб"}],
        used_policy=True,
        error_type=None,
    )
    assert len(result.items) == 2
    assert result.items[0]["name"] == "молоко"
    assert result.items[1]["name"] == "хлеб"


def test_extraction_result_item_name_compat():
    """AC-2: .item_name returns first item's name for backward compat."""
    result = ExtractionResult(
        items=[{"name": "молоко"}, {"name": "хлеб"}],
        used_policy=True,
        error_type=None,
    )
    assert result.item_name == "молоко"


def test_extraction_result_empty_items():
    """AC-2: Empty items -> item_name is None."""
    result = ExtractionResult(items=[], used_policy=True, error_type="timeout")
    assert result.item_name is None
    assert result.items == []


def test_extraction_result_single_item():
    """Backward compat: single item works like old item_name."""
    result = ExtractionResult(
        items=[{"name": "бананы", "quantity": "3", "unit": "шт"}],
        used_policy=False,
        error_type=None,
    )
    assert result.item_name == "бананы"
    assert result.items[0]["quantity"] == "3"
    assert result.items[0]["unit"] == "шт"
```

---

## Step 7: Create `tests/test_assist_multi_item.py`

Create this NEW file with the following content:

```python
"""Tests for assist mode multi-item entity hints (ST-010)."""

import routers.assist.runner as assist_runner
from routers.assist.runner import _pick_matching_item, _pick_matching_items, _ENTITY_SCHEMA
from routers.assist.types import AgentEntityHint, EntityHints


def test_entity_schema_has_structured_items():
    """AC-7: _ENTITY_SCHEMA items is array of objects with name/quantity/unit."""
    items_schema = _ENTITY_SCHEMA["properties"]["items"]
    assert items_schema["type"] == "array"
    item_obj = items_schema["items"]
    assert item_obj["type"] == "object"
    assert "name" in item_obj["properties"]
    assert "quantity" in item_obj["properties"]
    assert "unit" in item_obj["properties"]
    assert item_obj["required"] == ["name"]


def test_pick_matching_item_returns_first_dict():
    """_pick_matching_item returns first matching dict."""
    items = [{"name": "молоко"}, {"name": "хлеб"}, {"name": "бананы"}]
    result = _pick_matching_item(items, "Купи молоко и хлеб")
    assert result == {"name": "молоко"}


def test_pick_matching_item_no_match():
    """_pick_matching_item returns None when no match."""
    items = [{"name": "торт"}]
    result = _pick_matching_item(items, "Купи молоко")
    assert result is None


def test_pick_matching_items_all():
    """_pick_matching_items returns all matching dicts."""
    items = [{"name": "молоко"}, {"name": "хлеб"}, {"name": "бананы"}]
    result = _pick_matching_items(items, "Купи молоко, хлеб и бананы")
    assert len(result) == 3
    names = [item["name"] for item in result]
    assert names == ["молоко", "хлеб", "бананы"]


def test_pick_matching_items_partial():
    """_pick_matching_items returns only matches."""
    items = [{"name": "молоко"}, {"name": "торт"}, {"name": "хлеб"}]
    result = _pick_matching_items(items, "Купи молоко и хлеб")
    assert len(result) == 2
    names = [item["name"] for item in result]
    assert "молоко" in names
    assert "хлеб" in names
    assert "торт" not in names


def test_pick_matching_items_no_match():
    """_pick_matching_items returns empty list when no match."""
    items = [{"name": "торт"}, {"name": "печенье"}]
    result = _pick_matching_items(items, "Купи молоко")
    assert result == []


def test_entity_hints_all_items_applied(monkeypatch):
    """AC-3: All matching LLM entity hint items populate normalized['items']."""
    hint = EntityHints(
        items=[{"name": "молоко"}, {"name": "хлеб"}, {"name": "бананы"}],
        task_hints={},
        confidence=0.9,
        error_type=None,
        latency_ms=10,
    )
    normalized = {
        "text": "Купи молоко, хлеб и бананы",
        "intent": "add_shopping_item",
        "item_name": None,
        "items": [],
    }
    monkeypatch.setattr(assist_runner, "_log_step", lambda *a, **kw: None)
    updated, accepted = assist_runner._apply_entity_hints(
        normalized, hint, original_text="Купи молоко, хлеб и бананы"
    )
    assert accepted is True
    assert len(updated["items"]) == 3
    names = [item["name"] for item in updated["items"]]
    assert names == ["молоко", "хлеб", "бананы"]
    assert updated["item_name"] == "молоко"


def test_entity_hints_partial_match(monkeypatch):
    """AC-4: Only items confirmed in original text are accepted."""
    hint = EntityHints(
        items=[{"name": "молоко"}, {"name": "торт"}, {"name": "хлеб"}],
        task_hints={},
        confidence=0.9,
        error_type=None,
        latency_ms=10,
    )
    normalized = {
        "text": "Купи молоко и хлеб",
        "intent": "add_shopping_item",
        "item_name": None,
        "items": [],
    }
    monkeypatch.setattr(assist_runner, "_log_step", lambda *a, **kw: None)
    updated, accepted = assist_runner._apply_entity_hints(
        normalized, hint, original_text="Купи молоко и хлеб"
    )
    assert accepted is True
    assert len(updated["items"]) == 2
    names = [item["name"] for item in updated["items"]]
    assert "молоко" in names
    assert "хлеб" in names
    assert "торт" not in names


def test_entity_hints_no_match(monkeypatch):
    """AC-4 edge: No items match -> items unchanged."""
    hint = EntityHints(
        items=[{"name": "торт"}],
        task_hints={},
        confidence=0.9,
        error_type=None,
        latency_ms=10,
    )
    baseline_items = [{"name": "молоко"}]
    normalized = {
        "text": "Купи молоко",
        "intent": "add_shopping_item",
        "item_name": None,
        "items": baseline_items,
    }
    monkeypatch.setattr(assist_runner, "_log_step", lambda *a, **kw: None)
    updated, accepted = assist_runner._apply_entity_hints(
        normalized, hint, original_text="Купи молоко"
    )
    assert accepted is False
    assert updated["items"] == baseline_items


def test_agent_hint_multi_item(monkeypatch):
    """AC-5: Agent hint path populates multi-item."""
    agent_hint = AgentEntityHint(
        status="ok",
        items=[{"name": "яблоки"}, {"name": "апельсины"}],
        latency_ms=5,
    )
    normalized = {
        "text": "Купи яблоки и апельсины",
        "intent": "add_shopping_item",
        "item_name": None,
        "items": [],
    }
    monkeypatch.setattr(assist_runner, "_log_step", lambda *a, **kw: None)
    updated, accepted = assist_runner._apply_entity_hints(
        normalized, None, original_text="Купи яблоки и апельсины", agent_hint=agent_hint
    )
    assert accepted is True
    assert len(updated["items"]) == 2
    names = [item["name"] for item in updated["items"]]
    assert "яблоки" in names
    assert "апельсины" in names
    assert updated["item_name"] == "яблоки"


def test_entity_hints_fallback_no_hint(monkeypatch):
    """AC-6: No hint = baseline items unchanged."""
    baseline_items = [{"name": "молоко"}, {"name": "хлеб"}]
    normalized = {
        "text": "Купи молоко и хлеб",
        "intent": "add_shopping_item",
        "item_name": "молоко",
        "items": baseline_items,
    }
    monkeypatch.setattr(assist_runner, "_log_step", lambda *a, **kw: None)
    updated, accepted = assist_runner._apply_entity_hints(
        normalized, None, original_text="Купи молоко и хлеб"
    )
    assert accepted is False
    assert updated["items"] == baseline_items
```

---

## Verification

Run ALL tests after completing all steps:

```bash
# 1. New LLM extraction tests
python3 -m pytest tests/test_llm_extraction_multi_item.py -v

# 2. New assist multi-item tests
python3 -m pytest tests/test_assist_multi_item.py -v

# 3. Existing assist tests
python3 -m pytest tests/test_assist_mode.py -v

# 4. Full test suite
python3 -m pytest tests/ -v

# 5. No secrets
grep -rn "sk-\|api_key\s*=\s*[\"']" llm_policy/tasks.py routers/assist/runner.py routers/assist/types.py routers/assist/agent_scoring.py tests/test_llm_extraction_multi_item.py tests/test_assist_multi_item.py

# 6. Schema check
python3 -c "from llm_policy.tasks import SHOPPING_EXTRACTION_SCHEMA; assert 'items' in SHOPPING_EXTRACTION_SCHEMA['properties']"

# 7. Backward compat check
python3 -c "from llm_policy.tasks import ExtractionResult; r = ExtractionResult(items=[{'name': 'молоко'}], used_policy=False, error_type=None); assert r.item_name == 'молоко'"
```

Expected: ALL tests pass, no secrets found, schema and backward compat checks pass.

---

## Files summary

| File | Action |
|------|--------|
| `llm_policy/tasks.py` | Replace entire file (Step 1) |
| `routers/assist/types.py` | Replace entire file (Step 2) |
| `routers/assist/agent_scoring.py` | Replace entire file (Step 3) |
| `routers/assist/runner.py` | Replace entire file (Step 4) |
| `tests/test_assist_mode.py` | Update line 117-118 (Step 5) |
| `tests/test_llm_extraction_multi_item.py` | Create new file (Step 6) |
| `tests/test_assist_multi_item.py` | Create new file (Step 7) |

## Invariants (DO NOT break)

- `extract_item_name()` in `graphs/core_graph.py` — NOT modified
- `extract_items()` in `graphs/core_graph.py` — NOT modified
- `process_command()` in `graphs/core_graph.py` — NOT modified
- `decision.schema.json` — NOT modified
- `command.schema.json` — NOT modified
- `routers/v2.py` — NOT modified (uses `.item_name` property transparently)
