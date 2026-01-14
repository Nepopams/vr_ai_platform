from __future__ import annotations

from typing import Any, Dict, List

from graphs.core_graph import detect_intent, extract_item_name


def run(agent_input: Dict[str, Any], trace_id: str | None = None) -> Dict[str, Any]:
    text = agent_input.get("text", "")
    if not isinstance(text, str):
        text = ""

    intent = detect_intent(text) if text else "clarify_needed"
    missing_fields: List[str] = []
    question = "Нужны уточнения."

    if not text:
        question = "Опишите запрос подробнее."
        missing_fields = ["text"]
    elif intent == "add_shopping_item":
        if not extract_item_name(text):
            question = "Уточните, что добавить в список."
            missing_fields = ["item.name"]
    elif intent == "create_task":
        question = "Уточните детали задачи."
        missing_fields = ["task.title"]

    return {
        "question": question,
        "missing_fields": missing_fields,
        "confidence": 0.2,
    }
