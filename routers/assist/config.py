"""Configuration helpers for LLM assist mode."""

from __future__ import annotations

import os


def assist_mode_enabled() -> bool:
    return os.getenv("ASSIST_MODE_ENABLED", "false").strip().lower() in {"1", "true", "yes"}


def assist_normalization_enabled() -> bool:
    return os.getenv("ASSIST_NORMALIZATION_ENABLED", "false").strip().lower() in {"1", "true", "yes"}


def assist_entity_extraction_enabled() -> bool:
    return os.getenv("ASSIST_ENTITY_EXTRACTION_ENABLED", "false").strip().lower() in {"1", "true", "yes"}


def assist_clarify_enabled() -> bool:
    return os.getenv("ASSIST_CLARIFY_ENABLED", "false").strip().lower() in {"1", "true", "yes"}


def assist_timeout_ms() -> int:
    value = os.getenv("ASSIST_TIMEOUT_MS", "200").strip()
    try:
        return int(value)
    except ValueError:
        return 200


def assist_log_path() -> str:
    return os.getenv("ASSIST_LOG_PATH", "logs/assist.jsonl").strip()


def assist_agent_hints_enabled() -> bool:
    return os.getenv("ASSIST_AGENT_HINTS_ENABLED", "false").strip().lower() in {"1", "true", "yes"}


def assist_agent_hints_agent_id() -> str:
    return os.getenv("ASSIST_AGENT_HINTS_AGENT_ID", "").strip()


def assist_agent_hints_capability() -> str:
    return os.getenv("ASSIST_AGENT_HINTS_CAPABILITY", "extract_entities.shopping").strip()


def assist_agent_hints_allowlist() -> list[str]:
    raw = os.getenv("ASSIST_AGENT_HINTS_ALLOWLIST", "")
    return [value.strip() for value in raw.split(",") if value.strip()]


def assist_agent_hints_sample_rate() -> float:
    value = os.getenv("ASSIST_AGENT_HINTS_SAMPLE_RATE", "0.0").strip()
    try:
        rate = float(value)
    except ValueError:
        return 0.0
    return min(max(rate, 0.0), 1.0)


def assist_agent_hints_timeout_ms() -> int:
    value = os.getenv("ASSIST_AGENT_HINTS_TIMEOUT_MS", "120").strip()
    try:
        timeout = int(value)
    except ValueError:
        return 120
    return max(timeout, 0)
