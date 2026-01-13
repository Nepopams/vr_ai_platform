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
