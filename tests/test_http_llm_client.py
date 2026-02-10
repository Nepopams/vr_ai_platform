import json
import logging
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from llm_policy.errors import LlmUnavailableError
from llm_policy.http_caller import HttpLlmCaller, create_http_caller
from llm_policy.models import CallSpec

# Reusable test fixtures

def _make_spec(
    provider: str = "yandex_ai_studio",
    model: str = "gpt-oss-20b",
    temperature: float | None = 0.2,
    max_tokens: int | None = 256,
    timeout_ms: int | None = 2000,
    base_url: str | None = "https://llm.example.com",
    project: str | None = "test-project",
) -> CallSpec:
    return CallSpec(
        provider=provider,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout_ms=timeout_ms,
        base_url=base_url,
        project=project,
    )


def _mock_success_response(content: str = "test response") -> MagicMock:
    response = MagicMock()
    response.json.return_value = {
        "choices": [{"message": {"content": content}}]
    }
    response.raise_for_status.return_value = None
    return response


# Tests

def test_sends_correct_request_yandex() -> None:
    """AC-1: Verify correct URL, headers (incl OpenAI-Project), and body for yandex_ai_studio."""
    spec = _make_spec(provider="yandex_ai_studio", project="my-folder")
    caller = HttpLlmCaller(api_key="test-key")

    with patch("llm_policy.http_caller.httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.post.return_value = _mock_success_response()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

        caller(spec, "test prompt")

        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "https://llm.example.com/chat/completions"
        headers = call_args[1]["headers"]
        assert headers["Authorization"] == "Bearer test-key"
        assert headers["OpenAI-Project"] == "my-folder"
        body = call_args[1]["json"]
        assert body["model"] == "gpt-oss-20b"
        assert body["temperature"] == 0.2
        assert body["max_tokens"] == 256


def test_sends_correct_request_openai_compatible() -> None:
    """AC-1: Verify no OpenAI-Project header for openai_compatible provider."""
    spec = _make_spec(provider="openai_compatible", project=None)
    caller = HttpLlmCaller(api_key="test-key")

    with patch("llm_policy.http_caller.httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.post.return_value = _mock_success_response()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

        caller(spec, "test prompt")

        headers = mock_client.post.call_args[1]["headers"]
        assert "OpenAI-Project" not in headers


def test_returns_response_text() -> None:
    """AC-1: Extracts content from OpenAI-format response."""
    spec = _make_spec()
    caller = HttpLlmCaller(api_key="test-key")

    with patch("llm_policy.http_caller.httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.post.return_value = _mock_success_response("extracted text")
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

        result = caller(spec, "test prompt")
        assert result == "extracted text"


def test_timeout_raises_timeout_error() -> None:
    """AC-2: httpx.TimeoutException maps to builtin TimeoutError."""
    import httpx as _httpx
    spec = _make_spec()
    caller = HttpLlmCaller(api_key="test-key")

    with patch("llm_policy.http_caller.httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.post.side_effect = _httpx.TimeoutException("timed out")
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

        with pytest.raises(TimeoutError):
            caller(spec, "test prompt")


def test_connection_failure_raises_unavailable() -> None:
    """AC-3: httpx.ConnectError maps to LlmUnavailableError."""
    import httpx as _httpx
    spec = _make_spec()
    caller = HttpLlmCaller(api_key="test-key")

    with patch("llm_policy.http_caller.httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.post.side_effect = _httpx.ConnectError("connection refused")
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

        with pytest.raises(LlmUnavailableError):
            caller(spec, "test prompt")


def test_http_error_raises_unavailable() -> None:
    """AC-3: HTTP 500 maps to LlmUnavailableError."""
    import httpx as _httpx
    spec = _make_spec()
    caller = HttpLlmCaller(api_key="test-key")

    with patch("llm_policy.http_caller.httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_client.post.return_value = mock_response
        mock_response.raise_for_status.side_effect = _httpx.HTTPStatusError(
            "500", request=MagicMock(), response=mock_response
        )
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

        with pytest.raises(LlmUnavailableError):
            caller(spec, "test prompt")


def test_no_api_key_in_logs(caplog: pytest.LogCaptureFixture) -> None:
    """AC-4: API key value never appears in log output."""
    secret_key = "sk-super-secret-key-12345"
    spec = _make_spec()
    caller = HttpLlmCaller(api_key=secret_key)

    with caplog.at_level(logging.DEBUG, logger="llm_policy.http_caller"):
        with patch("llm_policy.http_caller.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.post.return_value = _mock_success_response()
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

            caller(spec, "test prompt")

    for record in caplog.records:
        assert secret_key not in record.getMessage()


def test_respects_callspec_parameters() -> None:
    """AC-1: temperature, max_tokens, timeout_ms correctly mapped."""
    spec = _make_spec(temperature=0.7, max_tokens=512, timeout_ms=5000)
    caller = HttpLlmCaller(api_key="test-key")

    with patch("llm_policy.http_caller.httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.post.return_value = _mock_success_response()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

        caller(spec, "test prompt")

        # Verify timeout passed to Client constructor
        mock_client_cls.assert_called_once_with(timeout=5.0)

        # Verify body parameters
        body = mock_client.post.call_args[1]["json"]
        assert body["temperature"] == 0.7
        assert body["max_tokens"] == 512
