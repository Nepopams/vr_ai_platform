from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Mapping

from graphs.core_graph import extract_item_name as fallback_extract_item_name
from llm_policy.config import get_llm_policy_profile, is_llm_policy_enabled
from llm_policy.runtime import TaskRunResult, run_task_with_policy

SHOPPING_EXTRACTION_TASK_ID = "shopping_extraction"
SHOPPING_EXTRACTION_SCHEMA: Mapping[str, object] = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "quantity": {"type": ["string", "number", "null"]},
                    "unit": {"type": ["string", "null"]},
                },
                "required": ["name"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["items"],
    "additionalProperties": False,
}


@dataclass(frozen=True)
class ExtractionResult:
    items: list[dict]
    used_policy: bool
    error_type: str | None

    @property
    def item_name(self) -> str | None:
        if self.items:
            return self.items[0].get("name")
        return None


def extract_shopping_item_name(
    text: str,
    *,
    policy_enabled: bool | None = None,
    profile: str | None = None,
    trace_id: str | None = None,
) -> ExtractionResult:
    enabled = is_llm_policy_enabled() if policy_enabled is None else policy_enabled
    if not enabled:
        fallback_name = fallback_extract_item_name(text)
        items = [{"name": fallback_name}] if fallback_name else []
        return ExtractionResult(
            items=items,
            used_policy=False,
            error_type=None,
        )

    result = _run_policy_extraction(
        text,
        profile=profile,
        trace_id=trace_id,
        policy_enabled=enabled,
    )
    if result.status == "skipped" and result.error_type == "policy_disabled":
        fallback_name = fallback_extract_item_name(text)
        items = [{"name": fallback_name}] if fallback_name else []
        return ExtractionResult(
            items=items,
            used_policy=False,
            error_type=None,
        )

    if result.status == "ok" and result.data is not None:
        raw_items = result.data.get("items", [])
        items = _normalize_shopping_items(raw_items)
        return ExtractionResult(items=items, used_policy=True, error_type=None)

    return ExtractionResult(items=[], used_policy=True, error_type=result.error_type)


def _run_policy_extraction(
    text: str,
    *,
    profile: str | None,
    trace_id: str | None,
    policy_enabled: bool,
) -> TaskRunResult:
    prompt = _build_shopping_prompt(text)
    return run_task_with_policy(
        task_id=SHOPPING_EXTRACTION_TASK_ID,
        prompt=prompt,
        schema=SHOPPING_EXTRACTION_SCHEMA,
        profile=profile or get_llm_policy_profile(),
        trace_id=trace_id,
        policy_enabled=policy_enabled,
    )


def _build_shopping_prompt(text: str) -> str:
    format_text = json.dumps(
        {
            "items": [
                {
                    "name": "string",
                    "quantity": "string|null",
                    "unit": "string|null",
                }
            ]
        },
        ensure_ascii=False,
    )
    return (
        "Верни только JSON object без markdown, пояснений и code fences. "
        f"Формат: {format_text}. "
        "quantity только string или null; unit string или null. "
        'Для "2 литра кефира": {"name":"кефир","quantity":"2","unit":"литра"}. '
        "Если количества или единицы нет, верни null.\n"
        f"Текст: {text}"
    )


def _normalize_shopping_items(raw_items: object) -> list[dict[str, str]]:
    if not isinstance(raw_items, list):
        return []

    normalized: list[dict[str, str]] = []
    for raw_item in raw_items:
        if not isinstance(raw_item, dict):
            continue

        name = _normalize_text_field(raw_item.get("name"))
        if name is None:
            continue

        item: dict[str, str] = {"name": name}
        quantity = _normalize_quantity(raw_item.get("quantity"))
        if quantity is not None:
            item["quantity"] = quantity

        unit = _normalize_text_field(raw_item.get("unit"))
        if unit is not None:
            item["unit"] = unit

        normalized.append(item)

    return normalized


def _normalize_text_field(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


def _normalize_quantity(value: object) -> str | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            return None
        return str(int(value)) if value.is_integer() else str(value)
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return None
