"""Shopping list extraction agent."""

from __future__ import annotations

from typing import Any, Dict, Tuple

from agent_runner.llm_client import LLMClientError
from agent_runner.llm_factory import get_llm_client
from agent_runner.schemas import shopping_extraction_schema


SYSTEM_PROMPT = (
    "Ты извлекаешь товары из фразы для списка покупок. "
    "Верни один ответ строго в JSON без markdown и комментариев. "
    "Только поля ShoppingExtractionResult, без лишних. "
    "Если товар не найден — items: []. "
    "Нормализуй названия, убери слова 'добавь' и 'в список покупок'. "
    "quantity/unit только если явно указано; иначе null."
)


def build_user_prompt(text: str, schema: Dict[str, Any]) -> str:
    return (
        "Верни ТОЛЬКО JSON, без markdown и комментариев.\n"
        f"Текст: {text}\n"
        f"JSON Schema: {schema}"
    )


def extract_shopping_items(text: str, context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    client = get_llm_client()
    schema = shopping_extraction_schema()
    payload = {
        "input_text": text,
        "context": context,
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": build_user_prompt(text, schema),
        "schema": schema,
    }
    try:
        output, meta = client.extract(payload)
        return True, {"output": output, "meta": meta}
    except LLMClientError as exc:
        error_type = exc.error_type
        if error_type in {"openai_error", "yandex_error", "llm_error"}:
            error_type = "llm_error"
        return False, {"error": {"type": error_type, "message": exc.message}}
