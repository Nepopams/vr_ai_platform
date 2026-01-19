"""Shadow agent invoker (registry-driven, zero-impact)."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from typing import Any, Dict, Iterable

from agent_registry.v0_loader import AgentRegistryV0Loader, load_capability_catalog
from agent_registry.v0_models import AgentRegistryV0, AgentSpec, TimeoutSpec
from agent_registry.v0_runner import AgentOutput, run as run_agent
from app.logging.shadow_agent_diff_log import log_shadow_agent_diff, summarize_agent_payload
from routers.partial_trust_sampling import stable_sample
from routers.shadow_agent_config import (
    shadow_agent_allowlist,
    shadow_agent_diff_log_enabled,
    shadow_agent_invoker_enabled,
    shadow_agent_registry_path,
    shadow_agent_sample_rate,
    shadow_agent_timeout_ms,
)


_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="shadow-agent-invoker")
_REGISTRY_CACHE: tuple[str, AgentRegistryV0] | None = None
_REGISTRY_ERROR: str | None = None
_CATALOG_CACHE: dict[str, dict[str, Any]] | None = None
_CATALOG_ERROR: str | None = None


def invoke_shadow_agents(
    command: Dict[str, Any],
    normalized: Dict[str, Any],
    baseline: Dict[str, Any],
    trace_id: str | None,
    command_id: str | None,
) -> None:
    try:
        if not shadow_agent_invoker_enabled():
            return
        allowlist = set(shadow_agent_allowlist())
        if not allowlist:
            return
        sample_rate = shadow_agent_sample_rate()
        if sample_rate <= 0.0:
            return
        if not stable_sample(command_id, sample_rate):
            return

        registry = _load_registry(shadow_agent_registry_path())
        if registry is None:
            return
        intent = normalized.get("intent")
        agent_input = _build_agent_input(command, normalized, trace_id, command_id)
        baseline_summary = _build_baseline_summary(baseline, intent)
        log_diff = shadow_agent_diff_log_enabled()
        catalog = _load_catalog() if log_diff else None

        for agent in registry.agents:
            if agent.agent_id not in allowlist:
                continue
            if agent.mode != "shadow":
                continue
            if not _intent_allowed(agent, intent):
                continue
            spec = _override_spec(agent, shadow_agent_timeout_ms())
            _submit_agent_run(
                spec,
                agent_input,
                trace_id,
                command_id,
                baseline_summary,
                catalog,
                log_diff,
            )
    except Exception:
        return


def _build_agent_input(
    command: Dict[str, Any],
    normalized: Dict[str, Any],
    trace_id: str | None,
    command_id: str | None,
) -> Dict[str, Any]:
    return {
        "command_id": command_id,
        "trace_id": trace_id,
        "intent": normalized.get("intent"),
        "text": normalized.get("text", ""),
        "context": command.get("context", {}),
    }


def _intent_allowed(agent: AgentSpec, intent: str | None) -> bool:
    if not agent.capabilities:
        return False
    allowed_intents = agent.capabilities[0].allowed_intents
    if not intent:
        return False
    if allowed_intents and intent not in allowed_intents:
        return False
    return True


def _override_spec(agent: AgentSpec, timeout_ms: int) -> AgentSpec:
    timeouts = agent.timeouts
    if timeout_ms > 0:
        timeouts = TimeoutSpec(timeout_ms=timeout_ms)
    return replace(agent, enabled=True, timeouts=timeouts)


def _load_registry(path: str) -> AgentRegistryV0 | None:
    global _REGISTRY_CACHE, _REGISTRY_ERROR
    if _REGISTRY_CACHE and _REGISTRY_CACHE[0] == path:
        return _REGISTRY_CACHE[1]
    if _REGISTRY_ERROR == path:
        return None
    try:
        registry = AgentRegistryV0Loader.load(path_override=path)
    except Exception:
        _REGISTRY_ERROR = path
        return None
    _REGISTRY_CACHE = (path, registry)
    return registry


def _load_catalog() -> dict[str, dict[str, Any]] | None:
    global _CATALOG_CACHE, _CATALOG_ERROR
    if _CATALOG_CACHE is not None:
        return _CATALOG_CACHE
    if _CATALOG_ERROR is not None:
        return None
    try:
        catalog = load_capability_catalog()
    except Exception:
        _CATALOG_ERROR = "error"
        return None
    _CATALOG_CACHE = catalog
    return catalog


def _submit_agent_run(
    agent: AgentSpec,
    agent_input: Dict[str, Any],
    trace_id: str | None,
    command_id: str | None,
    baseline_summary: Dict[str, Any],
    catalog: dict[str, dict[str, Any]] | None,
    log_diff: bool,
) -> None:
    try:
        future = _EXECUTOR.submit(
            _run_agent,
            agent,
            agent_input,
            trace_id,
            command_id,
            baseline_summary,
            catalog,
            log_diff,
        )
        future.add_done_callback(_consume_future_error)
    except Exception:
        return


def _run_agent(
    agent: AgentSpec,
    agent_input: Dict[str, Any],
    trace_id: str | None,
    command_id: str | None,
    baseline_summary: Dict[str, Any],
    catalog: dict[str, dict[str, Any]] | None,
    log_diff: bool,
) -> None:
    output = run_agent(agent, agent_input, trace_id=trace_id)
    if log_diff:
        _log_diff_event(output, agent, baseline_summary, catalog, trace_id, command_id)


def _consume_future_error(future) -> None:
    try:
        future.result()
    except Exception:
        return


def _log_diff_event(
    output: AgentOutput,
    agent: AgentSpec,
    baseline_summary: Dict[str, Any],
    catalog: dict[str, dict[str, Any]] | None,
    trace_id: str | None,
    command_id: str | None,
) -> None:
    try:
        capability_id = agent.capabilities[0].capability_id if agent.capabilities else None
        entry = catalog.get(capability_id) if catalog and capability_id else None
        contains_sensitive_text = bool(entry.get("contains_sensitive_text")) if entry else False
        payload_summary = summarize_agent_payload(output.payload or {})
        agent_keys = set(payload_summary.get("keys_present", []))
        baseline_keys = set(_baseline_keys(baseline_summary))
        diff_summary = {
            "keys_overlap_count": len(agent_keys & baseline_keys),
            "agent_keys_count": len(agent_keys),
            "baseline_keys_count": len(baseline_keys),
        }
        log_shadow_agent_diff(
            {
                "trace_id": trace_id,
                "command_id": command_id,
                "agent_id": agent.agent_id,
                "capability_id": capability_id,
                "status": output.status,
                "reason_code": output.reason_code,
                "baseline_summary": baseline_summary,
                "agent_summary": payload_summary,
                "diff_summary": diff_summary,
                "privacy": {"raw_logged": False, "contains_sensitive_text": contains_sensitive_text},
            }
        )
    except Exception:
        return


def _baseline_keys(summary: Dict[str, Any]) -> Iterable[str]:
    keys = []
    for key, value in summary.items():
        if value in (None, "", [], {}):
            continue
        keys.append(key)
    return keys


def _build_baseline_summary(baseline: Dict[str, Any], intent: str | None) -> Dict[str, Any]:
    payload = baseline.get("payload") or {}
    missing_fields = payload.get("missing_fields") or []
    proposed_actions = payload.get("proposed_actions") or []
    return {
        "intent": intent,
        "action": baseline.get("action"),
        "job_type": payload.get("job_type"),
        "missing_fields_count": len(missing_fields),
        "proposed_actions_count": len(proposed_actions),
    }
