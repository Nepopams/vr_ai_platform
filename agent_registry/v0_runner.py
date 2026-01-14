from __future__ import annotations

import importlib
import inspect
import json
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from dataclasses import dataclass
from typing import Any, Dict, Mapping

from agent_registry.v0_loader import load_capability_catalog
from agent_registry.v0_models import AgentSpec
from agent_registry.v0_reason_codes import (
    REASON_CAPABILITY_NOT_ALLOWED,
    REASON_DISABLED,
    REASON_EXCEPTION,
    REASON_INVALID_INPUT,
    REASON_INVALID_OUTPUT,
    REASON_POLICY_DISABLED,
    REASON_TIMEOUT,
    REASON_UNKNOWN_RUNNER,
)
from agent_registry.validation import validate_agent_input, validate_agent_output_payload
from app.logging.agent_run_log import log_agent_run
from llm_policy.config import (
    get_llm_policy_allow_placeholders,
    get_llm_policy_path,
    get_llm_policy_profile,
    is_llm_policy_enabled,
)
from llm_policy.loader import LlmPolicyLoader
from llm_policy.runtime import run_task_with_policy


STATUS_OK = "ok"
STATUS_SKIPPED = "skipped"
STATUS_REJECTED = "rejected"
STATUS_ERROR = "error"

_EXECUTOR = ThreadPoolExecutor(max_workers=4, thread_name_prefix="agent-runner")


@dataclass(frozen=True)
class AgentOutput:
    status: str
    reason_code: str | None
    payload: Dict[str, Any] | None
    latency_ms: int | None


def run(agent_spec: AgentSpec, agent_input: Dict[str, Any], *, trace_id: str | None = None) -> AgentOutput:
    started = time.monotonic()
    if not agent_spec.enabled:
        output = _output(STATUS_SKIPPED, REASON_DISABLED, None, started)
        _log_run_event(output, agent_spec, capability_id=None, catalog=None, trace_id=trace_id, command_id=None)
        return output
    ok_input, reason, normalized_input = validate_agent_input(agent_input)
    if not ok_input:
        output = _output(STATUS_REJECTED, reason or REASON_INVALID_INPUT, None, started)
        _log_run_event(output, agent_spec, capability_id=None, catalog=None, trace_id=trace_id, command_id=None)
        return output
    if len(agent_spec.capabilities) != 1:
        output = _output(STATUS_REJECTED, REASON_INVALID_INPUT, None, started)
        _log_run_event(output, agent_spec, capability_id=None, catalog=None, trace_id=trace_id, command_id=None)
        return output

    capability_id = agent_spec.capabilities[0].capability_id
    try:
        catalog = load_capability_catalog()
    except Exception:
        output = _output(STATUS_REJECTED, REASON_INVALID_INPUT, None, started)
        _log_run_event(output, agent_spec, capability_id=capability_id, catalog=None, trace_id=trace_id, command_id=None)
        return output

    entry = catalog.get(capability_id)
    if entry is None:
        output = _output(STATUS_REJECTED, REASON_CAPABILITY_NOT_ALLOWED, None, started)
        _log_run_event(output, agent_spec, capability_id=capability_id, catalog=catalog, trace_id=trace_id, command_id=None)
        return output

    allowlist = entry["payload_allowlist"]
    timeout_ms = _resolve_timeout_ms(agent_spec)
    kind = agent_spec.runner.kind
    command_id = _resolve_command_id(normalized_input or {})

    if kind == "python_module":
        status, reason_code, payload = _run_python_module(
            agent_spec.runner.ref,
            normalized_input or {},
            timeout_ms=timeout_ms,
            trace_id=trace_id,
        )
    elif kind == "llm_policy_task":
        status, reason_code, payload = _run_llm_policy_task(
            task_id=agent_spec.runner.ref,
            profile_id=agent_spec.llm_profile_id or get_llm_policy_profile(),
            agent_input=agent_input,
            allowlist=allowlist,
            timeout_ms=timeout_ms,
            trace_id=trace_id,
        )
    else:
        return _output(STATUS_ERROR, REASON_UNKNOWN_RUNNER, None, started)

    if status == STATUS_OK:
        ok_payload, reason = validate_agent_output_payload(payload, capability_id, catalog)
        if not ok_payload:
            output = _output(STATUS_REJECTED, reason or REASON_INVALID_OUTPUT, None, started)
            _log_run_event(
                output,
                agent_spec,
                capability_id=capability_id,
                catalog=catalog,
                trace_id=trace_id,
                command_id=command_id,
                runner_kind=kind,
                model_meta=_model_meta(agent_spec, kind),
                payload=payload,
            )
            return output
    output = _output(status, reason_code, payload, started)
    _log_run_event(
        output,
        agent_spec,
        capability_id=capability_id,
        catalog=catalog,
        trace_id=trace_id,
        command_id=command_id,
        runner_kind=kind,
        model_meta=_model_meta(agent_spec, kind),
        payload=payload,
    )
    return output


def _run_python_module(
    ref: str,
    agent_input: Dict[str, Any],
    *,
    timeout_ms: int | None,
    trace_id: str | None,
) -> tuple[str, str, Dict[str, Any] | None]:
    module_name, _, func_name = ref.partition(":")
    if not module_name or not func_name:
        return STATUS_REJECTED, REASON_INVALID_INPUT, None

    try:
        module = importlib.import_module(module_name)
        func = getattr(module, func_name)
    except Exception:
        return STATUS_ERROR, REASON_EXCEPTION, None

    def _invoke() -> Dict[str, Any]:
        if _accepts_trace_id(func):
            return func(agent_input, trace_id=trace_id)
        return func(agent_input)

    try:
        result = _run_with_timeout(_invoke, timeout_ms)
    except FutureTimeout:
        return STATUS_ERROR, REASON_TIMEOUT, None
    except Exception:
        return STATUS_ERROR, REASON_EXCEPTION, None

    if not isinstance(result, dict):
        return STATUS_REJECTED, REASON_INVALID_OUTPUT, None
    return STATUS_OK, "", result


def _run_llm_policy_task(
    *,
    task_id: str,
    profile_id: str,
    agent_input: Dict[str, Any],
    allowlist: set[str],
    timeout_ms: int | None,
    trace_id: str | None,
) -> tuple[str, str, Dict[str, Any] | None]:
    if not is_llm_policy_enabled():
        return STATUS_SKIPPED, REASON_POLICY_DISABLED, None
    if not _policy_route_available(task_id, profile_id):
        return STATUS_SKIPPED, REASON_POLICY_DISABLED, None

    schema = _build_schema(allowlist)
    prompt = _build_prompt(agent_input, schema)

    def _invoke():
        return run_task_with_policy(
            task_id=task_id,
            prompt=prompt,
            schema=schema,
            profile=profile_id,
            trace_id=trace_id,
            policy_enabled=True,
        )

    try:
        result = _run_with_timeout(_invoke, timeout_ms)
    except FutureTimeout:
        return STATUS_ERROR, REASON_TIMEOUT, None
    except Exception:
        return STATUS_ERROR, REASON_EXCEPTION, None

    if result.status == "skipped":
        return STATUS_SKIPPED, REASON_POLICY_DISABLED, None
    if result.status != "ok" or result.data is None:
        return STATUS_ERROR, REASON_EXCEPTION, None
    if not isinstance(result.data, dict):
        return STATUS_REJECTED, REASON_INVALID_OUTPUT, None
    payload = dict(result.data)
    ok_payload, reason = validate_agent_output_payload(payload, task_id, {task_id: {"payload_allowlist": allowlist}})
    if not ok_payload:
        return STATUS_REJECTED, reason or REASON_INVALID_OUTPUT, None
    return STATUS_OK, "", payload


def _policy_route_available(task_id: str, profile_id: str) -> bool:
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
    task_routes = policy.routing.get(task_id)
    if task_routes is None:
        return False
    return profile_id in task_routes


def _build_prompt(agent_input: Dict[str, Any], schema: Mapping[str, object]) -> str:
    try:
        input_text = json.dumps(agent_input, ensure_ascii=False)
    except TypeError:
        input_text = json.dumps(_stringify(agent_input), ensure_ascii=False)
    schema_text = json.dumps(schema, ensure_ascii=False)
    return (
        "Верни только JSON по схеме.\n"
        f"Схема: {schema_text}\n"
        f"Вход: {input_text}"
    )


def _build_schema(allowlist: set[str]) -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": {key: {} for key in sorted(allowlist)},
        "additionalProperties": False,
    }


def _resolve_timeout_ms(agent_spec: AgentSpec) -> int | None:
    if agent_spec.timeouts is None:
        return None
    return agent_spec.timeouts.timeout_ms


def _run_with_timeout(func, timeout_ms: int | None):
    if timeout_ms is None or timeout_ms <= 0:
        return func()
    future = _EXECUTOR.submit(func)
    return future.result(timeout=timeout_ms / 1000.0)


def _accepts_trace_id(func) -> bool:
    try:
        signature = inspect.signature(func)
    except (TypeError, ValueError):
        return False
    return "trace_id" in signature.parameters


def _stringify(payload: Mapping[str, Any]) -> Dict[str, Any]:
    return {key: str(value) for key, value in payload.items()}


def _resolve_command_id(agent_input: Dict[str, Any]) -> str | None:
    value = agent_input.get("command_id")
    if isinstance(value, str):
        return value
    return None


def _model_meta(agent_spec: AgentSpec, runner_kind: str) -> Dict[str, Any] | None:
    if runner_kind != "llm_policy_task":
        return None
    return {
        "profile_id": agent_spec.llm_profile_id or get_llm_policy_profile(),
        "task_id": agent_spec.runner.ref,
    }


def _log_run_event(
    output: AgentOutput,
    agent_spec: AgentSpec,
    *,
    capability_id: str | None,
    catalog: Dict[str, Dict[str, Any]] | None,
    trace_id: str | None,
    command_id: str | None,
    runner_kind: str | None = None,
    model_meta: Dict[str, Any] | None = None,
    payload: Dict[str, Any] | None = None,
) -> None:
    entry = catalog.get(capability_id) if catalog and capability_id else None
    contains_sensitive = bool(entry.get("contains_sensitive_text")) if entry else False
    payload_summary = summarize_payload(payload or {}, contains_sensitive) if entry else {"keys_present": []}
    event = {
        "trace_id": trace_id,
        "command_id": command_id,
        "agent_id": agent_spec.agent_id,
        "capability_id": capability_id,
        "mode": agent_spec.mode,
        "status": output.status,
        "reason_code": output.reason_code or None,
        "latency_ms": output.latency_ms,
        "runner_kind": runner_kind or agent_spec.runner.kind,
        "model_meta": model_meta,
        "payload_summary": payload_summary,
        "privacy": {"contains_sensitive_text": contains_sensitive, "raw_logged": False},
    }
    log_agent_run(event)


def summarize_payload(payload: Dict[str, Any], contains_sensitive_text: bool) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        return {"keys_present": []}
    summary: Dict[str, Any] = {"keys_present": sorted(payload.keys())}
    counts: Dict[str, int] = {}
    flags: Dict[str, bool] = {}
    for key, value in payload.items():
        if isinstance(value, list):
            counts[f"{key}_count"] = len(value)
            nested_list_counts = _nested_list_counts(value)
            if nested_list_counts:
                counts.update(nested_list_counts)
            continue
        if isinstance(value, dict):
            counts[f"{key}_keys_count"] = len(value.keys())
            nested_keys = _nested_keys_count(value)
            if nested_keys:
                counts.update(nested_keys)
            if _looks_like_id_key(key) and value:
                flags[f"has_{key}"] = True
            continue
        if isinstance(value, bool):
            flags[f"has_{key}"] = value
            continue
        if isinstance(value, (int, float)):
            counts[f"{key}_count"] = 1
            continue
        if isinstance(value, str):
            flags[f"has_{key}"] = True
            continue
    if counts:
        summary["counts"] = counts
    if flags:
        summary["flags"] = flags
    summary["contains_sensitive_text"] = contains_sensitive_text
    return summary


def _nested_list_counts(values: list[Any]) -> Dict[str, int]:
    total_dicts = 0
    total_lists = 0
    for item in values:
        if isinstance(item, dict):
            total_dicts += 1
        if isinstance(item, list):
            total_lists += 1
    counts: Dict[str, int] = {}
    if total_dicts:
        counts["nested_dicts_count"] = total_dicts
    if total_lists:
        counts["nested_lists_count"] = total_lists
    return counts


def _nested_keys_count(payload: Dict[str, Any]) -> Dict[str, int]:
    count = 0
    for value in payload.values():
        if isinstance(value, dict):
            count += len(value.keys())
    if count:
        return {"nested_keys_count": count}
    return {}


def _looks_like_id_key(key: str) -> bool:
    return key.endswith("_id") or key.endswith("id")


def _output(status: str, reason_code: str, payload: Dict[str, Any] | None, start: float) -> AgentOutput:
    latency_ms = int((time.monotonic() - start) * 1000)
    normalized_reason = reason_code or None
    return AgentOutput(status=status, reason_code=normalized_reason, payload=payload, latency_ms=latency_ms)
