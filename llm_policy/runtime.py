from __future__ import annotations

import json
import logging
import time
from typing import Mapping

from jsonschema import ValidationError, validate

from llm_policy.config import (
    get_llm_policy_path,
    get_llm_policy_profile,
    is_llm_policy_enabled,
)
from llm_policy.errors import LlmUnavailableError
from llm_policy.loader import LlmPolicyLoader
from llm_policy.models import CallSpec, LlmCaller, LlmPolicy, TaskRunResult

_LOGGER = logging.getLogger("llm_policy")
_LLM_CALLER: LlmCaller | None = None


def set_llm_caller(caller: LlmCaller | None) -> None:
    global _LLM_CALLER
    _LLM_CALLER = caller


def get_llm_caller() -> LlmCaller | None:
    return _LLM_CALLER


def resolve_call_spec(policy: LlmPolicy, task_id: str, profile: str) -> CallSpec:
    task_routes = policy.routing.get(task_id)
    if task_routes is None:
        raise ValueError(f"no routing for task {task_id}")
    spec = task_routes.get(profile)
    if spec is None:
        raise ValueError(f"no routing for task {task_id} profile {profile}")
    return spec


def run_task_with_policy(
    *,
    task_id: str,
    prompt: str,
    schema: Mapping[str, object],
    profile: str | None = None,
    trace_id: str | None = None,
    policy: LlmPolicy | None = None,
    caller: LlmCaller | None = None,
    policy_enabled: bool | None = None,
) -> TaskRunResult:
    enabled = is_llm_policy_enabled() if policy_enabled is None else policy_enabled
    if not enabled:
        return TaskRunResult(
            status="error",
            data=None,
            error_type="llm_policy_disabled",
            attempts=0,
            profile=profile or get_llm_policy_profile(),
            escalated=False,
        )

    policy = policy or LlmPolicyLoader.load(
        enabled=True,
        path_override=get_llm_policy_path(),
    )
    if policy is None:
        return TaskRunResult(
            status="error",
            data=None,
            error_type="llm_policy_missing",
            attempts=0,
            profile=profile or get_llm_policy_profile(),
            escalated=False,
        )

    caller = caller or get_llm_caller()
    if caller is None:
        return TaskRunResult(
            status="error",
            data=None,
            error_type="llm_unavailable",
            attempts=0,
            profile=profile or get_llm_policy_profile(),
            escalated=False,
        )

    start_profile = profile or get_llm_policy_profile()
    profiles_to_try = [start_profile]
    if start_profile != "reliable":
        profiles_to_try.append("reliable")

    attempts = 0
    escalated = False

    for current_profile in profiles_to_try:
        if current_profile != start_profile:
            escalated = True
        result = _run_profile(
            policy=policy,
            task_id=task_id,
            profile=current_profile,
            prompt=prompt,
            schema=schema,
            caller=caller,
            trace_id=trace_id,
            escalated=escalated,
        )
        attempts += result.attempts
        if result.status == "ok":
            return TaskRunResult(
                status="ok",
                data=result.data,
                error_type=None,
                attempts=attempts,
                profile=current_profile,
                escalated=escalated,
            )
        if result.error_type in {"invalid_json", "schema_validation_failed"}:
            if current_profile != "reliable":
                continue
            return TaskRunResult(
                status="error",
                data=None,
                error_type=result.error_type,
                attempts=attempts,
                profile=current_profile,
                escalated=escalated,
            )
        return TaskRunResult(
            status="error",
            data=None,
            error_type=result.error_type,
            attempts=attempts,
            profile=current_profile,
            escalated=escalated,
        )

    return TaskRunResult(
        status="error",
        data=None,
        error_type="llm_error",
        attempts=attempts,
        profile=start_profile,
        escalated=escalated,
    )


def _run_profile(
    *,
    policy: LlmPolicy,
    task_id: str,
    profile: str,
    prompt: str,
    schema: Mapping[str, object],
    caller: LlmCaller,
    trace_id: str | None,
    escalated: bool,
) -> TaskRunResult:
    last_raw: str | None = None
    attempts = 0
    for attempt_index in range(2):
        attempts += 1
        spec = resolve_call_spec(policy, task_id, profile)
        call_prompt = prompt if attempt_index == 0 else _build_repair_prompt(schema, last_raw or "")
        try:
            raw, latency_ms = _call_llm(caller, spec, call_prompt)
        except TimeoutError:
            _log_attempt(
                trace_id=trace_id,
                profile=profile,
                spec=spec,
                ok=False,
                latency_ms=None,
                error_type="timeout",
                attempts=attempts,
                escalated=escalated,
            )
            return TaskRunResult(
                status="error",
                data=None,
                error_type="timeout",
                attempts=attempts,
                profile=profile,
                escalated=False,
            )
        except LlmUnavailableError:
            _log_attempt(
                trace_id=trace_id,
                profile=profile,
                spec=spec,
                ok=False,
                latency_ms=None,
                error_type="llm_unavailable",
                attempts=attempts,
                escalated=escalated,
            )
            return TaskRunResult(
                status="error",
                data=None,
                error_type="llm_unavailable",
                attempts=attempts,
                profile=profile,
                escalated=False,
            )
        except Exception:
            _log_attempt(
                trace_id=trace_id,
                profile=profile,
                spec=spec,
                ok=False,
                latency_ms=None,
                error_type="llm_error",
                attempts=attempts,
                escalated=escalated,
            )
            return TaskRunResult(
                status="error",
                data=None,
                error_type="llm_error",
                attempts=attempts,
                profile=profile,
                escalated=False,
            )

        last_raw = raw
        parsed = _parse_json(raw)
        if parsed is None:
            _log_attempt(
                trace_id=trace_id,
                profile=profile,
                spec=spec,
                ok=False,
                latency_ms=latency_ms,
                error_type="invalid_json",
                attempts=attempts,
                escalated=escalated,
            )
            if attempt_index == 0:
                continue
            return TaskRunResult(
                status="error",
                data=None,
                error_type="invalid_json",
                attempts=attempts,
                profile=profile,
                escalated=False,
            )

        if not _validate_schema(parsed, schema):
            _log_attempt(
                trace_id=trace_id,
                profile=profile,
                spec=spec,
                ok=False,
                latency_ms=latency_ms,
                error_type="schema_validation_failed",
                attempts=attempts,
                escalated=escalated,
            )
            if attempt_index == 0:
                continue
            return TaskRunResult(
                status="error",
                data=None,
                error_type="schema_validation_failed",
                attempts=attempts,
                profile=profile,
                escalated=False,
            )

        _log_attempt(
            trace_id=trace_id,
            profile=profile,
            spec=spec,
            ok=True,
            latency_ms=latency_ms,
            error_type=None,
            attempts=attempts,
            escalated=escalated,
        )
        return TaskRunResult(
            status="ok",
            data=parsed,
            error_type=None,
            attempts=attempts,
            profile=profile,
            escalated=False,
        )

    return TaskRunResult(
        status="error",
        data=None,
        error_type="llm_error",
        attempts=attempts,
        profile=profile,
        escalated=False,
    )


def _call_llm(caller: LlmCaller, spec: CallSpec, prompt: str) -> tuple[str, float]:
    start = time.monotonic()
    raw = caller(spec, prompt)
    latency_ms = (time.monotonic() - start) * 1000
    return raw, latency_ms


def _parse_json(raw: str) -> Mapping[str, object] | None:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    return parsed


def _validate_schema(payload: Mapping[str, object], schema: Mapping[str, object]) -> bool:
    try:
        validate(instance=payload, schema=schema)
    except ValidationError:
        return False
    return True


def _build_repair_prompt(schema: Mapping[str, object], raw: str) -> str:
    schema_text = json.dumps(schema, ensure_ascii=False)
    return (
        "Исправь JSON так, чтобы он соответствовал схеме. "
        "Верни только JSON без пояснений.\n"
        f"Схема: {schema_text}\n"
        f"Ответ: {raw}"
    )


def _log_attempt(
    *,
    trace_id: str | None,
    profile: str,
    spec: CallSpec,
    ok: bool,
    latency_ms: float | None,
    error_type: str | None,
    attempts: int,
    escalated: bool,
) -> None:
    payload = {
        "trace_id": trace_id,
        "provider": spec.provider,
        "model": spec.model,
        "profile": profile,
        "ok": ok,
        "latency_ms": round(latency_ms, 2) if latency_ms is not None else None,
        "attempts": attempts,
        "escalated": escalated,
        "error_type": error_type,
    }
    _LOGGER.info("llm_policy_attempt %s", payload)
