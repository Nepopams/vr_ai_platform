"""OpenAI Responses API client for structured outputs."""

from __future__ import annotations

import time
from typing import Any, Dict, Tuple

from openai import OpenAI

from agent_runner.llm_client import LLMClientError, validate_json_output


class OpenAIClient:
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        timeout_s: float,
        store: bool,
        temperature: float,
        base_url: str | None = None,
    ) -> None:
        if base_url:
            self._client = OpenAI(api_key=api_key, timeout=timeout_s, base_url=base_url)
        else:
            self._client = OpenAI(api_key=api_key, timeout=timeout_s)
        self._model = model
        self._store = store
        self._temperature = temperature

    def extract(self, payload: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        start = time.perf_counter()
        try:
            response = self._client.responses.create(
                model=self._model,
                input=[
                    {"role": "system", "content": payload["system_prompt"]},
                    {"role": "user", "content": payload["user_prompt"]},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "ShoppingExtractionResult",
                        "strict": True,
                        "schema": payload["schema"],
                    },
                },
                temperature=self._temperature,
                store=self._store,
            )
        except Exception as exc:
            raise LLMClientError("openai_error", str(exc)) from exc

        latency_ms = int((time.perf_counter() - start) * 1000)

        if getattr(response, "output_text", None):
            raise LLMClientError("invalid_output", "Получен текстовый ответ вместо JSON.")

        output = None
        if response.output:
            content = response.output[0].content[0]
            if getattr(content, "type", None) == "refusal":
                raise LLMClientError("refusal", "Ответ был отклонен моделью.")
            output = getattr(content, "parsed", None)
        if not isinstance(output, dict):
            raise LLMClientError("invalid_output", "Не удалось извлечь JSON по схеме.")

        validate_json_output(output, payload["schema"])

        meta = {
            "model": self._model,
            "latency_ms": latency_ms,
            "tokens": getattr(response, "usage", None),
        }
        return output, meta
