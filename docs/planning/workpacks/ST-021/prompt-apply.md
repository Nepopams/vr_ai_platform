# Codex APPLY Prompt — ST-021: HTTP LLM Client Implementing LlmCaller Interface

## Role
You are a senior Python developer implementing a real HTTP LLM client for the
`llm_policy` package.

## Context (from PLAN findings)
- `LlmCaller = Callable[[CallSpec, str], str]` (llm_policy/models.py:54)
- `CallSpec` fields: provider, model, temperature (float|None), max_tokens (int|None),
  timeout_ms (int|None), base_url (str|None), project (str|None)
- `LlmUnavailableError(RuntimeError)` in `llm_policy/errors.py`
- Runtime catches: `TimeoutError`, `LlmUnavailableError`, generic `Exception`
- `httpx` is a project dependency (via pyproject.toml)
- `llm-policy.yaml` has NO `base_url` — caller must fallback to `LLM_BASE_URL` env var
- `agent_runner/yandex_client.py` shows pattern: POST to `{base_url}/chat/completions`,
  headers `Authorization: Bearer {key}`, `OpenAI-Project: {project}` for Yandex,
  body `{model, messages, temperature, max_tokens}`,
  response extraction `choices[0].message.content`
- Test pattern: `StubCaller` with `__call__(spec, prompt)`, `monkeypatch` for env vars,
  `sys.path` injection in test files

## Files to Create

### 1. `llm_policy/http_caller.py` (NEW)

Create an HTTP LLM client implementing `LlmCaller`:

```python
"""HTTP LLM client implementing LlmCaller interface."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict

import httpx

from llm_policy.errors import LlmUnavailableError
from llm_policy.models import CallSpec

_LOGGER = logging.getLogger("llm_policy.http_caller")


def create_http_caller(*, api_key: str | None = None) -> HttpLlmCaller:
    """Factory: create caller. Reads LLM_API_KEY from env if not provided."""
    key = api_key or os.getenv("LLM_API_KEY", "")
    if not key:
        raise ValueError("LLM_API_KEY is required")
    return HttpLlmCaller(api_key=key)


class HttpLlmCaller:
    """Callable implementing LlmCaller = Callable[[CallSpec, str], str].

    Supports providers: yandex_ai_studio, openai_compatible.
    Uses OpenAI-compatible chat/completions API format.
    """

    def __init__(self, *, api_key: str) -> None:
        self._api_key = api_key

    def __call__(self, spec: CallSpec, prompt: str) -> str:
        url = self._build_url(spec)
        headers = self._build_headers(spec)
        body = self._build_body(spec, prompt)
        timeout_s = (spec.timeout_ms / 1000) if spec.timeout_ms else 30.0

        _LOGGER.info(
            "llm_http_request provider=%s model=%s timeout_s=%.1f",
            spec.provider,
            spec.model,
            timeout_s,
        )

        try:
            with httpx.Client(timeout=timeout_s) as client:
                response = client.post(url, headers=headers, json=body)
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise TimeoutError(f"LLM request timed out after {timeout_s}s") from exc
        except httpx.ConnectError as exc:
            raise LlmUnavailableError(f"LLM connection failed: {exc}") from exc
        except httpx.HTTPStatusError as exc:
            raise LlmUnavailableError(
                f"LLM HTTP error {exc.response.status_code}"
            ) from exc
        except httpx.HTTPError as exc:
            raise LlmUnavailableError(f"LLM HTTP error: {exc}") from exc

        return self._extract_content(response)

    def _build_url(self, spec: CallSpec) -> str:
        base = spec.base_url or os.getenv("LLM_BASE_URL", "")
        if not base:
            raise LlmUnavailableError("No base_url in CallSpec and LLM_BASE_URL not set")
        return f"{base.rstrip('/')}/chat/completions"

    def _build_headers(self, spec: CallSpec) -> Dict[str, str]:
        headers: Dict[str, str] = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        if spec.provider == "yandex_ai_studio" and spec.project:
            headers["OpenAI-Project"] = spec.project
        return headers

    def _build_body(self, spec: CallSpec, prompt: str) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "model": spec.model,
            "messages": [{"role": "user", "content": prompt}],
        }
        if spec.temperature is not None:
            body["temperature"] = spec.temperature
        if spec.max_tokens is not None:
            body["max_tokens"] = spec.max_tokens
        return body

    def _extract_content(self, response: httpx.Response) -> str:
        try:
            data = response.json()
        except ValueError as exc:
            raise LlmUnavailableError("LLM response is not valid JSON") from exc
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LlmUnavailableError("Cannot extract content from LLM response") from exc
```

Key design points:
- `__call__` matches `LlmCaller` signature exactly: `(CallSpec, str) -> str`
- Error mapping: `httpx.TimeoutException` → builtin `TimeoutError`, all other httpx errors → `LlmUnavailableError`
- Log line contains provider/model/timeout but NEVER the API key, prompt, or response
- `_build_url` falls back to `LLM_BASE_URL` env var when `spec.base_url` is None
- `_build_headers` adds `OpenAI-Project` only for `yandex_ai_studio` provider
- Factory `create_http_caller` reads `LLM_API_KEY` from env (or accepts explicit key for testing)

### 2. `tests/test_http_llm_client.py` (NEW)

Create 8 unit tests. Follow the project test pattern (sys.path injection, monkeypatch).

```python
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
```

## Files NOT Modified (invariants)
- `llm_policy/models.py` — DO NOT CHANGE
- `llm_policy/runtime.py` — DO NOT CHANGE
- `llm_policy/errors.py` — DO NOT CHANGE
- `llm_policy/config.py` — DO NOT CHANGE
- `llm_policy/loader.py` — DO NOT CHANGE
- `llm_policy/llm-policy.yaml` — DO NOT CHANGE
- `agent_runner/yandex_client.py` — DO NOT CHANGE (reference only)
- All existing test files — DO NOT CHANGE

## Verification Commands

After creating the files, run:

```bash
# New tests only
source .venv/bin/activate && python3 -m pytest tests/test_http_llm_client.py -v

# Full test suite (expect 228 existing + 8 new = 236)
source .venv/bin/activate && python3 -m pytest --tb=short -q

# Import check
source .venv/bin/activate && python3 -c "from llm_policy.http_caller import create_http_caller, HttpLlmCaller; print('OK')"
```

## STOP-THE-LINE
If any of the following occur, STOP and report:
- Existing tests fail after your changes
- `httpx` import fails
- `LlmUnavailableError` import fails
- Any file listed as "DO NOT CHANGE" needs modification
- The test mocking pattern does not work with the installed httpx version
