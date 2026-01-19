"""Configuration helpers for shadow agent invoker."""

from __future__ import annotations

import os


def shadow_agent_invoker_enabled() -> bool:
    return os.getenv("SHADOW_AGENT_INVOKER_ENABLED", "false").strip().lower() in {"1", "true", "yes"}


def shadow_agent_registry_path() -> str:
    return os.getenv("SHADOW_AGENT_REGISTRY_PATH", "agent_registry/agent-registry-v0.yaml").strip()


def shadow_agent_allowlist() -> list[str]:
    raw = os.getenv("SHADOW_AGENT_ALLOWLIST", "")
    return [value.strip() for value in raw.split(",") if value.strip()]


def shadow_agent_sample_rate() -> float:
    value = os.getenv("SHADOW_AGENT_SAMPLE_RATE", "0.0").strip()
    try:
        rate = float(value)
    except ValueError:
        return 0.0
    return min(max(rate, 0.0), 1.0)


def shadow_agent_timeout_ms() -> int:
    value = os.getenv("SHADOW_AGENT_TIMEOUT_MS", "150").strip()
    try:
        timeout = int(value)
    except ValueError:
        return 150
    return max(timeout, 0)


def shadow_agent_diff_log_enabled() -> bool:
    return os.getenv("SHADOW_AGENT_DIFF_LOG_ENABLED", "false").strip().lower() in {"1", "true", "yes"}


def shadow_agent_diff_log_path() -> str:
    return os.getenv("SHADOW_AGENT_DIFF_LOG_PATH", "logs/shadow_agent_diff.jsonl").strip()
