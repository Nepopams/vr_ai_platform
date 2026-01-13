from __future__ import annotations

import os


def is_llm_policy_enabled() -> bool:
    return os.getenv("LLM_POLICY_ENABLED", "false").lower() in {"1", "true", "yes"}


def get_llm_policy_path() -> str | None:
    return os.getenv("LLM_POLICY_PATH")


def get_llm_policy_profile() -> str:
    return os.getenv("LLM_POLICY_PROFILE", "cheap")


def get_llm_policy_allow_placeholders() -> bool:
    return os.getenv("LLM_POLICY_ALLOW_PLACEHOLDERS", "false").lower() in {"1", "true", "yes"}
