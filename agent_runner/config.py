"""Configuration for the local agent runner."""

from __future__ import annotations

import os


def get_host() -> str:
    return os.getenv("LLM_AGENT_RUNNER_HOST", "0.0.0.0")


def get_port() -> int:
    return int(os.getenv("LLM_AGENT_RUNNER_PORT", "8089"))


def get_llm_provider() -> str:
    return os.getenv("LLM_PROVIDER", "openai").strip().lower()


def get_llm_api_key() -> str:
    return os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY", "")


def get_llm_model() -> str:
    return os.getenv("LLM_MODEL") or os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def get_llm_project() -> str:
    return os.getenv("LLM_PROJECT") or os.getenv("OPENAI_PROJECT", "")


def get_llm_base_url() -> str:
    base_url = os.getenv("LLM_BASE_URL", "").strip()
    if base_url:
        return base_url
    if get_llm_provider() == "yandex_ai_studio":
        return "https://llm.api.cloud.yandex.net/v1"
    return ""


def get_llm_timeout_s() -> float:
    timeout_ms = os.getenv("LLM_TIMEOUT_MS")
    if timeout_ms:
        return float(timeout_ms) / 1000.0
    return float(os.getenv("OPENAI_TIMEOUT_S", "15"))


def get_llm_store() -> bool:
    value = os.getenv("LLM_STORE")
    if value is None:
        value = os.getenv("OPENAI_STORE", "false")
    return value.strip().lower() in {"1", "true", "yes"}


def get_llm_temperature() -> float:
    return float(os.getenv("LLM_TEMPERATURE") or os.getenv("OPENAI_TEMPERATURE", "0.1"))


def get_llm_max_output_tokens() -> int | None:
    value = os.getenv("LLM_MAX_OUTPUT_TOKENS")
    return int(value) if value else None
