"""Router strategy V2 pipeline (Normalizer → Planner → Validator)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from graphs.core_graph import (
    build_clarify_decision,
    build_proposed_action,
    build_start_job_decision,
    detect_intent,
    _default_assignee_id,
    _default_list_id,
)
from llm_policy.tasks import extract_shopping_item_name
from app.llm.agent_runner_client import shadow_invoke, runner_enabled
from routers.base import RouterStrategy
from routers.assist.runner import apply_assist_hints
from routers.shadow_router import start_shadow_router


class RouterV2Pipeline(RouterStrategy):
    def decide(self, command: Dict[str, Any]) -> Dict[str, Any]:
        normalized = self.normalize(command)
        start_shadow_router(command, normalized)
        assist = apply_assist_hints(command, normalized)
        plan = self.plan(assist.normalized, command)
        return self.validate_and_build(plan, assist.normalized, command, assist)

    def normalize(self, command: Dict[str, Any]) -> Dict[str, Any]:
        text = command.get("text", "").strip()
        intent = detect_intent(text) if text else "clarify_needed"
        item_name = (
            extract_shopping_item_name(text, trace_id=command.get("trace_id")).item_name
            if intent == "add_shopping_item"
            else None
        )
        task_title = text if intent == "create_task" else None
        capabilities = set(command.get("capabilities", []))
        if intent == "add_shopping_item" and runner_enabled():
            trace_id = str(command.get("command_id", "unknown"))
            shadow_invoke(text=text, context=command.get("context", {}), trace_id=trace_id)
        return {
            "text": text,
            "intent": intent,
            "item_name": item_name,
            "task_title": task_title,
            "capabilities": capabilities,
        }

    def plan(self, normalized: Dict[str, Any], command: Dict[str, Any]) -> Dict[str, Any]:
        intent = normalized["intent"]
        proposed_actions: List[Dict[str, Any]] = []
        capabilities: Set[str] = normalized["capabilities"]

        if intent == "add_shopping_item" and normalized.get("item_name"):
            if "propose_add_shopping_item" in capabilities:
                list_id = _default_list_id(command)
                item_payload: Dict[str, Any] = {"name": normalized["item_name"]}
                if list_id:
                    item_payload["list_id"] = list_id
                proposed_actions.append(
                    build_proposed_action(
                        "propose_add_shopping_item",
                        {"item": item_payload},
                    )
                )
        elif intent == "create_task" and normalized.get("task_title"):
            if "propose_create_task" in capabilities:
                proposed_actions.append(
                    build_proposed_action(
                        "propose_create_task",
                        {
                            "task": {
                                "title": normalized["task_title"],
                                "assignee_id": _default_assignee_id(command),
                            }
                        },
                    )
                )

        return {
            "intent": intent,
            "proposed_actions": proposed_actions or None,
        }

    def validate_and_build(
        self,
        plan: Dict[str, Any],
        normalized: Dict[str, Any],
        command: Dict[str, Any],
        assist=None,
    ) -> Dict[str, Any]:
        capabilities: Set[str] = normalized["capabilities"]
        text = normalized["text"]
        intent = normalized["intent"]

        if "start_job" not in capabilities:
            return build_clarify_decision(
                command,
                question=self._clarify_question(
                    "Какие действия разрешены для выполнения?",
                    assist,
                    missing_fields=None,
                ),
                explanation="Отсутствует capability start_job.",
            )

        if not text:
            return build_clarify_decision(
                command,
                question=self._clarify_question(
                    "Опишите, что нужно сделать: задача или покупка?",
                    assist,
                    missing_fields=["text"],
                ),
                missing_fields=["text"],
                explanation="Текст команды пустой.",
            )

        if intent == "add_shopping_item":
            if not normalized.get("item_name"):
                return build_clarify_decision(
                    command,
                    question=self._clarify_question(
                        "Какой товар добавить в список покупок?",
                        assist,
                        missing_fields=["item.name"],
                    ),
                    missing_fields=["item.name"],
                    explanation="Не удалось извлечь название товара.",
                )
            return build_start_job_decision(
                command,
                job_type="add_shopping_item",
                proposed_actions=plan.get("proposed_actions"),
                explanation="Распознан запрос на добавление покупки.",
            )

        if intent == "create_task":
            if not normalized.get("task_title"):
                return build_clarify_decision(
                    command,
                    question=self._clarify_question(
                        "Какую задачу нужно создать?",
                        assist,
                        missing_fields=["task.title"],
                    ),
                    missing_fields=["task.title"],
                    explanation="Не удалось получить описание задачи.",
                )
            return build_start_job_decision(
                command,
                job_type="create_task",
                proposed_actions=plan.get("proposed_actions"),
                explanation="Распознан запрос на создание задачи.",
            )

        return build_clarify_decision(
            command,
            question=self._clarify_question(
                "Уточните, что нужно сделать: задача или покупка?",
                assist,
                missing_fields=None,
            ),
            explanation="Интент не распознан.",
        )

    @staticmethod
    def _clarify_question(default_question: str, assist, missing_fields: Optional[List[str]]) -> str:
        if not assist or not assist.clarify_question:
            return default_question
        if missing_fields and assist.clarify_missing_fields:
            if not set(assist.clarify_missing_fields).issubset(set(missing_fields)):
                return default_question
        return assist.clarify_question
