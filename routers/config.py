"""Configuration helpers for decision router selection."""

from __future__ import annotations

import os


def get_strategy_name() -> str:
    return os.getenv("DECISION_ROUTER_STRATEGY", "v1").strip().lower()
