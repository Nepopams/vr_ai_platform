"""Configuration helpers for partial trust corridor."""

from __future__ import annotations

import os


DEFAULT_CORRIDOR_INTENT = "add_shopping_item"
ALLOWED_CORRIDOR_INTENTS = {DEFAULT_CORRIDOR_INTENT}


def partial_trust_enabled() -> bool:
    return os.getenv("PARTIAL_TRUST_ENABLED", "false").strip().lower() in {"1", "true", "yes"}


def partial_trust_intent() -> str | None:
    if not partial_trust_enabled():
        return None
    value = os.getenv("PARTIAL_TRUST_INTENT", DEFAULT_CORRIDOR_INTENT).strip()
    return value or None


def partial_trust_corridor_intent() -> str | None:
    intent = partial_trust_intent()
    if intent in ALLOWED_CORRIDOR_INTENTS:
        return intent
    return None


def partial_trust_sample_rate() -> float:
    if not partial_trust_enabled():
        return 0.0
    value = os.getenv("PARTIAL_TRUST_SAMPLE_RATE", "0.01").strip()
    try:
        rate = float(value)
    except ValueError:
        return 0.0
    return min(max(rate, 0.0), 1.0)


def partial_trust_timeout_ms() -> int:
    if not partial_trust_enabled():
        return 0
    value = os.getenv("PARTIAL_TRUST_TIMEOUT_MS", "200").strip()
    try:
        return int(value)
    except ValueError:
        return 0


def partial_trust_profile_id() -> str | None:
    if not partial_trust_enabled():
        return None
    value = os.getenv("PARTIAL_TRUST_PROFILE_ID", "").strip()
    return value or None


def partial_trust_risk_log_path() -> str:
    return os.getenv("PARTIAL_TRUST_RISK_LOG_PATH", "logs/partial_trust_risk.jsonl").strip()
