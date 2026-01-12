"""LLM client factory."""

from __future__ import annotations

from agent_runner import config
from agent_runner.openai_client import OpenAIClient
from agent_runner.yandex_client import YandexAIStudioClient


def get_llm_client():
    provider = config.get_llm_provider()
    if provider == "yandex_ai_studio":
        return YandexAIStudioClient(
            api_key=config.get_llm_api_key(),
            project=config.get_llm_project(),
            model=config.get_llm_model(),
            base_url=config.get_llm_base_url(),
            timeout_s=config.get_llm_timeout_s(),
            temperature=config.get_llm_temperature(),
            max_output_tokens=config.get_llm_max_output_tokens(),
        )
    return OpenAIClient(
        api_key=config.get_llm_api_key(),
        model=config.get_llm_model(),
        timeout_s=config.get_llm_timeout_s(),
        store=config.get_llm_store(),
        temperature=config.get_llm_temperature(),
        base_url=config.get_llm_base_url() or None,
    )
