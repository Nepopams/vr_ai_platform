from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Mapping

from graphs.core_graph import extract_item_name as fallback_extract_item_name
from llm_policy.config import get_llm_policy_profile, is_llm_policy_enabled
from llm_policy.runtime import TaskRunResult, run_task_with_policy

SHOPPING_EXTRACTION_TASK_ID = "shopping_extraction"
SHOPPING_EXTRACTION_SCHEMA: Mapping[str, object] = {
    "type": "object",
    "properties": {
        "item_name": {"type": "string", "minLength": 1},
    },
    "required": ["item_name"],
    "additionalProperties": False,
}


@dataclass(frozen=True)
class ExtractionResult:
    item_name: str | None
    used_policy: bool
    error_type: str | None


def extract_shopping_item_name(
    text: str,
    *,
    policy_enabled: bool | None = None,
    profile: str | None = None,
    trace_id: str | None = None,
) -> ExtractionResult:
    enabled = is_llm_policy_enabled() if policy_enabled is None else policy_enabled
    if not enabled:
        return ExtractionResult(
            item_name=fallback_extract_item_name(text),
            used_policy=False,
            error_type=None,
        )

    result = _run_policy_extraction(
        text,
        profile=profile,
        trace_id=trace_id,
        policy_enabled=enabled,
    )
    if result.status == "ok" and result.data is not None:
        item_name = result.data.get("item_name")
        if isinstance(item_name, str):
            return ExtractionResult(item_name=item_name, used_policy=True, error_type=None)

    return ExtractionResult(item_name=None, used_policy=True, error_type=result.error_type)


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
    schema_text = json.dumps(SHOPPING_EXTRACTION_SCHEMA, ensure_ascii=False)
    return (
        "Извлеки название товара из текста пользователя. "
        "Верни только JSON по схеме.\n"
        f"Схема: {schema_text}\n"
        f"Текст: {text}"
    )
