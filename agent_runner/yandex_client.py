"""Yandex AI Studio OpenAI-compatible client."""

from __future__ import annotations

import time
from typing import Any, Dict, Tuple

import httpx

from agent_runner.llm_client import LLMClientError, parse_json_strict, validate_json_output


class YandexAIStudioClient:
    def __init__(
        self,
        *,
        api_key: str,
        project: str,
        model: str,
        base_url: str,
        timeout_s: float,
        temperature: float,
        max_output_tokens: int | None,
    ) -> None:
        self._api_key = api_key
        self._project = project
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._timeout_s = timeout_s
        self._temperature = temperature
        self._max_output_tokens = max_output_tokens

    def extract(self, payload: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        start = time.perf_counter()
        content = self._request_completion(payload["system_prompt"], payload["user_prompt"])
        try:
            parsed = parse_json_strict(content)
            validate_json_output(parsed, payload["schema"])
        except LLMClientError:
            content = self._request_completion(
                payload["system_prompt"],
                self._repair_prompt(content, payload["schema"]),
            )
            parsed = parse_json_strict(content)
            validate_json_output(parsed, payload["schema"])

        latency_ms = int((time.perf_counter() - start) * 1000)
        return parsed, {"model": self._model, "latency_ms": latency_ms}

    def _request_completion(self, system_prompt: str, user_prompt: str) -> str:
        payload: Dict[str, Any] = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self._temperature,
        }
        if self._max_output_tokens is not None:
            payload["max_tokens"] = self._max_output_tokens
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        if self._project:
            headers["OpenAI-Project"] = self._project
        url = f"{self._base_url}/chat/completions"
        try:
            response = self._post(url, headers=headers, json_payload=payload)
        except Exception as exc:
            raise LLMClientError("llm_error", str(exc)) from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise LLMClientError("invalid_output", "Ответ не является JSON.") from exc
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMClientError("invalid_output", "Не удалось извлечь content.") from exc

    def _post(self, url: str, headers: Dict[str, str], json_payload: Dict[str, Any]) -> httpx.Response:
        with httpx.Client(timeout=self._timeout_s) as client:
            response = client.post(url, headers=headers, json=json_payload)
            response.raise_for_status()
            return response

    @staticmethod
    def _repair_prompt(content: str, schema: Dict[str, Any]) -> str:
        return (
            "Исправь JSON так, чтобы он строго соответствовал схеме. "
            "Верни ТОЛЬКО JSON, без комментариев и markdown.\n"
            f"Схема: {schema}\n"
            f"Исходный ответ: {content}"
        )
