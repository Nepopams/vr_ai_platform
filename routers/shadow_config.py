"""Configuration helpers for shadow router."""

from __future__ import annotations

import os


def shadow_router_enabled() -> bool:
    return os.getenv("SHADOW_ROUTER_ENABLED", "false").strip().lower() in {"1", "true", "yes"}


def shadow_router_timeout_ms() -> int:
    value = os.getenv("SHADOW_ROUTER_TIMEOUT_MS", "150").strip()
    try:
        return int(value)
    except ValueError:
        return 150


def shadow_router_log_path() -> str:
    return os.getenv("SHADOW_ROUTER_LOG_PATH", "logs/shadow_router.jsonl").strip()


def shadow_router_mode() -> str:
    return os.getenv("SHADOW_ROUTER_MODE", "shadow").strip().lower()
