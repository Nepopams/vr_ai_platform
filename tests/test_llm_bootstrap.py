"""Tests for LLM caller bootstrap (ST-022)."""

import logging
import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from llm_policy.bootstrap import bootstrap_llm_caller
from llm_policy.runtime import get_llm_caller, set_llm_caller


@pytest.fixture(autouse=True)
def _reset_caller():
    """Reset global caller state before and after each test."""
    set_llm_caller(None)
    yield
    set_llm_caller(None)


def test_bootstrap_registers_caller_with_all_vars(monkeypatch) -> None:
    """AC-1: Caller registered when all env vars present."""
    monkeypatch.setenv("LLM_POLICY_ENABLED", "true")
    monkeypatch.setenv("LLM_POLICY_ALLOW_PLACEHOLDERS", "false")
    monkeypatch.setenv("LLM_API_KEY", "test-key-abc123")
    bootstrap_llm_caller()
    caller = get_llm_caller()
    assert caller is not None, "Caller should be registered"
    assert callable(caller), "Caller should be callable"


def test_bootstrap_registers_caller_for_cloudru_env(monkeypatch) -> None:
    """Cloud.ru UAT env uses the same OpenAI-compatible caller path."""
    policy_path = BASE_DIR / "llm_policy" / "llm-policy.cloudru.yaml"
    monkeypatch.setenv("LLM_POLICY_ENABLED", "true")
    monkeypatch.setenv("LLM_POLICY_PATH", str(policy_path))
    monkeypatch.setenv("LLM_POLICY_PROFILE", "cheap")
    monkeypatch.setenv("LLM_POLICY_ALLOW_PLACEHOLDERS", "false")
    monkeypatch.setenv("LLM_API_KEY", "test-key-abc123")
    monkeypatch.setenv("LLM_BASE_URL", "https://foundation-models.api.cloud.ru/v1")
    monkeypatch.setenv("LLM_PROVIDER", "openai_compatible")
    monkeypatch.setenv("LLM_MODEL", "openai/gpt-oss-20b")

    bootstrap_llm_caller()

    assert get_llm_caller() is not None


def test_bootstrap_skips_without_api_key(monkeypatch) -> None:
    """AC-2: Caller not registered when API key missing."""
    monkeypatch.setenv("LLM_POLICY_ENABLED", "true")
    monkeypatch.setenv("LLM_POLICY_ALLOW_PLACEHOLDERS", "false")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    bootstrap_llm_caller()
    assert get_llm_caller() is None, "Caller should not be registered without API key"


def test_bootstrap_skips_when_disabled(monkeypatch) -> None:
    """AC-2: Caller not registered when LLM policy disabled."""
    monkeypatch.setenv("LLM_POLICY_ENABLED", "false")
    monkeypatch.setenv("LLM_API_KEY", "test-key-abc123")
    bootstrap_llm_caller()
    assert get_llm_caller() is None, "Caller should not be registered when disabled"


def test_bootstrap_rejects_placeholder_mode(monkeypatch) -> None:
    """AC-3: Caller not registered when placeholders enabled."""
    monkeypatch.setenv("LLM_POLICY_ENABLED", "true")
    monkeypatch.setenv("LLM_POLICY_ALLOW_PLACEHOLDERS", "true")
    monkeypatch.setenv("LLM_API_KEY", "test-key-abc123")
    bootstrap_llm_caller()
    assert get_llm_caller() is None, "Caller should not be registered with placeholders"


def test_bootstrap_logs_warning_on_missing_vars(monkeypatch, caplog) -> None:
    """AC-2: Warning logged when API key missing."""
    monkeypatch.setenv("LLM_POLICY_ENABLED", "true")
    monkeypatch.setenv("LLM_POLICY_ALLOW_PLACEHOLDERS", "false")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    with caplog.at_level(logging.WARNING, logger="llm_policy"):
        bootstrap_llm_caller()
    assert any(
        "LLM_API_KEY not set" in record.message for record in caplog.records
    ), "Expected warning about missing LLM_API_KEY"


def test_create_app_runs_bootstrap_path_when_disabled(monkeypatch) -> None:
    """App startup path calls bootstrap without registering a caller when disabled."""
    from app.main import create_app

    monkeypatch.setenv("LLM_POLICY_ENABLED", "false")
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    app = create_app()

    assert app.title == "HomeTask Decision API"
    assert get_llm_caller() is None
