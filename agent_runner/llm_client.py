"""Base LLM client interfaces and helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict

from jsonschema import ValidationError, validate


@dataclass(frozen=True)
class LLMClientError(Exception):
    error_type: str
    message: str

    def to_error(self) -> Dict[str, Any]:
        return {"type": self.error_type, "message": self.message}


def validate_json_output(payload: Dict[str, Any], schema: Dict[str, Any]) -> None:
    try:
        validate(instance=payload, schema=schema)
    except ValidationError as exc:
        raise LLMClientError("invalid_output", str(exc)) from exc


def parse_json_strict(value: str) -> Dict[str, Any]:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise LLMClientError("invalid_output", "Ответ не является валидным JSON.") from exc
    if not isinstance(parsed, dict):
        raise LLMClientError("invalid_output", "Ожидался JSON-объект.")
    return parsed
