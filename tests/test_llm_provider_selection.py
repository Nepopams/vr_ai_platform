from agent_runner import config
from agent_runner.llm_factory import get_llm_client
from agent_runner.openai_client import OpenAIClient
from agent_runner.yandex_client import YandexAIStudioClient


def test_provider_openai(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    client = get_llm_client()
    assert isinstance(client, OpenAIClient)


def test_provider_yandex(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "yandex_ai_studio")
    monkeypatch.setenv("LLM_API_KEY", "test")
    monkeypatch.setenv("LLM_MODEL", "gpt://folder/gpt-oss-120b/latest")
    monkeypatch.setenv("LLM_PROJECT", "folder")
    client = get_llm_client()
    assert isinstance(client, YandexAIStudioClient)
    assert config.get_llm_base_url().startswith("https://")
