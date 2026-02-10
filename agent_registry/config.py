from __future__ import annotations

import os


def is_agent_registry_enabled() -> bool:
    return os.getenv("AGENT_REGISTRY_ENABLED", "false").lower() in {"1", "true", "yes"}


def get_agent_registry_path() -> str | None:
    return os.getenv("AGENT_REGISTRY_PATH")


def is_agent_registry_core_enabled() -> bool:
    return os.getenv("AGENT_REGISTRY_CORE_ENABLED", "false").lower() in {"1", "true", "yes"}
