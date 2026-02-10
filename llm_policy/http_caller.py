"""HTTP LLM client implementing LlmCaller interface."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict

import httpx

from llm_policy.errors import LlmUnavailableError
from llm_policy.models import CallSpec

_LOGGER = logging.getLogger("llm_policy.http_caller")


def create_http_caller(*, api_key: str | None = None) -> "HttpLlmCaller":
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
