"""Schemas for structured outputs."""

from __future__ import annotations

from typing import Any, Dict


def shopping_extraction_schema() -> Dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["items"],
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["name"],
                    "properties": {
                        "name": {"type": "string", "minLength": 1, "maxLength": 80},
                        "quantity": {"type": ["string", "null"], "maxLength": 32},
                        "unit": {"type": ["string", "null"], "maxLength": 32},
                    },
                },
            },
            "list_hint": {"type": ["string", "null"], "maxLength": 80},
        },
    }
