"""Router strategy V2 pipeline (Normalizer → Planner → Validator)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from graphs.core_graph import (
    build_clarify_decision,
    build_proposed_action,
    build_start_job_decision,
    detect_intent,
    extract_items,
    _default_assignee_id,
    _default_list_id,
)
from llm_policy.tasks import extract_shopping_item_name
from app.llm.agent_runner_client import shadow_invoke, runner_enabled
from app.logging.partial_trust_risk_log import append_partial_trust_risk_log
from routers.base import RouterStrategy
from routers.assist.runner import apply_assist_hints
from routers.partial_trust_acceptance import evaluate_candidate
from routers.partial_trust_candidate import (
    generate_llm_candidate_with_meta,
    policy_route_available,
)
from routers.partial_trust_config import (
    partial_trust_corridor_intent,
    partial_trust_enabled,
    partial_trust_profile_id,
    partial_trust_sample_rate,
    partial_trust_timeout_ms,
)
from routers.partial_trust_sampling import stable_sample
from routers.shadow_router import start_shadow_router
from routers.agent_invoker_shadow import invoke_shadow_agents


class RouterV2Pipeline(RouterStrategy):
    def decide(self, command: Dict[str, Any]) -> Dict[str, Any]:
        normalized = self.normalize(command)
        start_shadow_router(command, normalized)
        assist = apply_assist_hints(command, normalized)
        plan = self.plan(assist.normalized, command)
        baseline = self.validate_and_build(plan, assist.normalized, command, assist)
        invoke_shadow_agents(
            command,
            assist.normalized,
            baseline,
            baseline.get("trace_id"),
            command.get("command_id"),
        )
        partial_decision = self._maybe_apply_partial_trust(
            command=command,
            normalized=assist.normalized,
            baseline=baseline,
        )
        return partial_decision or baseline

    def normalize(self, command: Dict[str, Any]) -> Dict[str, Any]:
        text = command.get("text", "").strip()
        intent = detect_intent(text) if text else "clarify_needed"
        item_name = (
            extract_shopping_item_name(text, trace_id=command.get("trace_id")).item_name
            if intent == "add_shopping_item"
            else None
        )
        items = extract_items(text) if intent == "add_shopping_item" else []
        task_title = text if intent == "create_task" else None
        capabilities = set(command.get("capabilities", []))
        if intent == "add_shopping_item" and runner_enabled():
            trace_id = str(command.get("command_id", "unknown"))
            shadow_invoke(text=text, context=command.get("context", {}), trace_id=trace_id)
        return {
            "text": text,
            "intent": intent,
            "items": items,
            "item_name": item_name,
            "task_title": task_title,
            "capabilities": capabilities,
        }

    def plan(self, normalized: Dict[str, Any], command: Dict[str, Any]) -> Dict[str, Any]:
        intent = normalized["intent"]
        proposed_actions: List[Dict[str, Any]] = []
        capabilities: Set[str] = normalized["capabilities"]

        if intent == "add_shopping_item":
            items = normalized.get("items", [])
            if items and "propose_add_shopping_item" in capabilities:
                list_id = _default_list_id(command)
                for item in items:
                    item_payload: Dict[str, Any] = {"name": item["name"]}
                    if item.get("quantity"):
                        item_payload["quantity"] = item["quantity"]
                    if item.get("unit"):
                        item_payload["unit"] = item["unit"]
                    if list_id:
                        item_payload["list_id"] = list_id
                    proposed_actions.append(
                        build_proposed_action(
                            "propose_add_shopping_item",
                            {"item": item_payload},
                        )
                    )
            elif normalized.get("item_name") and "propose_add_shopping_item" in capabilities:
                list_id = _default_list_id(command)
                item_payload = {"name": normalized["item_name"]}
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
                    missing_fields=["capability.start_job"],
                ),
                missing_fields=["capability.start_job"],
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
            if not normalized.get("items") and not normalized.get("item_name"):
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
                missing_fields=["intent"],
            ),
            missing_fields=["intent"],
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

    def _maybe_apply_partial_trust(
        self,
        *,
        command: Dict[str, Any],
        normalized: Dict[str, Any],
        baseline: Dict[str, Any],
    ) -> Dict[str, Any] | None:
        if not partial_trust_enabled():
            return None

        corridor_intent = partial_trust_corridor_intent()
        sample_rate = partial_trust_sample_rate()
        command_id = command.get("command_id")
        trace_id = baseline.get("trace_id")
        baseline_summary = self._summarize_baseline(baseline, normalized.get("intent"))
        try:
            if corridor_intent is None or normalized.get("intent") != corridor_intent:
                self._log_partial_trust(
                    status="skipped",
                    reason_code="corridor_mismatch",
                    command_id=command_id,
                    trace_id=trace_id,
                    corridor_intent=corridor_intent or "",
                    sample_rate=sample_rate,
                    sampled=False,
                    latency_ms=None,
                    model_meta=None,
                    baseline_summary=baseline_summary,
                    llm_summary=None,
                    diff_summary=None,
                )
                return None

            if "start_job" not in normalized.get("capabilities", set()):
                self._log_partial_trust(
                    status="skipped",
                    reason_code="capability_mismatch",
                    command_id=command_id,
                    trace_id=trace_id,
                    corridor_intent=corridor_intent,
                    sample_rate=sample_rate,
                    sampled=False,
                    latency_ms=None,
                    model_meta=None,
                    baseline_summary=baseline_summary,
                    llm_summary=None,
                    diff_summary=None,
                )
                return None

            sampled = stable_sample(command_id, sample_rate)
            if not sampled:
                self._log_partial_trust(
                    status="not_sampled",
                    reason_code="not_sampled",
                    command_id=command_id,
                    trace_id=trace_id,
                    corridor_intent=corridor_intent,
                    sample_rate=sample_rate,
                    sampled=False,
                    latency_ms=None,
                    model_meta=None,
                    baseline_summary=baseline_summary,
                    llm_summary=None,
                    diff_summary=None,
                )
                return None

            profile_id = partial_trust_profile_id()
            if not policy_route_available(profile_id):
                self._log_partial_trust(
                    status="skipped",
                    reason_code="policy_disabled",
                    command_id=command_id,
                    trace_id=trace_id,
                    corridor_intent=corridor_intent,
                    sample_rate=sample_rate,
                    sampled=True,
                    latency_ms=None,
                    model_meta=None,
                    baseline_summary=baseline_summary,
                    llm_summary=None,
                    diff_summary=None,
                )
                return None

            candidate, error_type = generate_llm_candidate_with_meta(
                command,
                trace_id=trace_id,
                timeout_ms=partial_trust_timeout_ms(),
                profile_id=profile_id,
            )
            if candidate is None:
                self._log_partial_trust(
                    status="fallback_deterministic",
                    reason_code=error_type or "llm_error",
                    command_id=command_id,
                    trace_id=trace_id,
                    corridor_intent=corridor_intent,
                    sample_rate=sample_rate,
                    sampled=True,
                    latency_ms=None,
                    model_meta=None,
                    baseline_summary=baseline_summary,
                    llm_summary=None,
                    diff_summary=None,
                )
                return None

            accepted, reason_code, llm_summary = evaluate_candidate(
                candidate,
                corridor_intent=corridor_intent,
                policy_enabled=True,
                context=command.get("context"),
            )
            llm_summary = dict(llm_summary)
            llm_summary["intent"] = candidate.intent
            llm_summary["decision_type"] = "start_job"
            diff_summary = self._build_diff_summary(baseline_summary, llm_summary)

            if not accepted:
                self._log_partial_trust(
                    status="fallback_deterministic",
                    reason_code=reason_code,
                    command_id=command_id,
                    trace_id=trace_id,
                    corridor_intent=corridor_intent,
                    sample_rate=sample_rate,
                    sampled=True,
                    latency_ms=candidate.latency_ms,
                    model_meta=candidate.model_meta,
                    baseline_summary=baseline_summary,
                    llm_summary=llm_summary,
                    diff_summary=diff_summary,
                )
                return None

            decision = self._build_partial_trust_decision(command, candidate)
            self._log_partial_trust(
                status="accepted_llm",
                reason_code=reason_code,
                command_id=command_id,
                trace_id=trace_id,
                corridor_intent=corridor_intent,
                sample_rate=sample_rate,
                sampled=True,
                latency_ms=candidate.latency_ms,
                model_meta=candidate.model_meta,
                baseline_summary=baseline_summary,
                llm_summary=llm_summary,
                diff_summary=diff_summary,
            )
            return decision
        except Exception as exc:
            self._log_partial_trust(
                status="error",
                reason_code=type(exc).__name__,
                command_id=command_id,
                trace_id=trace_id,
                corridor_intent=corridor_intent or "",
                sample_rate=sample_rate,
                sampled=False,
                latency_ms=None,
                model_meta=None,
                baseline_summary=baseline_summary,
                llm_summary=None,
                diff_summary=None,
            )
            return None

    def _build_partial_trust_decision(
        self,
        command: Dict[str, Any],
        candidate,
    ) -> Dict[str, Any]:
        return build_start_job_decision(
            command,
            job_type="add_shopping_item",
            proposed_actions=candidate.proposed_actions,
            explanation="LLM-first принят для коридора add_shopping_item.",
        )

    @staticmethod
    def _summarize_baseline(decision: Dict[str, Any], intent: Optional[str]) -> Dict[str, Any]:
        payload = decision.get("payload", {})
        proposed_actions = payload.get("proposed_actions") or []
        entity_keys_count = 0
        has_list_id = False
        if proposed_actions:
            first = proposed_actions[0]
            item = first.get("payload", {}).get("item")
            if isinstance(item, dict):
                entity_keys_count = len(item.keys())
                list_id = item.get("list_id")
                has_list_id = isinstance(list_id, str) and bool(list_id.strip())
        return {
            "intent": intent,
            "decision_type": decision.get("action"),
            "action_count": len(proposed_actions),
            "entity_keys_count": entity_keys_count,
            "has_list_id": has_list_id,
        }

    @staticmethod
    def _build_diff_summary(
        baseline_summary: Dict[str, Any],
        llm_summary: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "intent_mismatch": baseline_summary.get("intent") != llm_summary.get("intent"),
            "decision_type_mismatch": baseline_summary.get("decision_type") != llm_summary.get("decision_type"),
            "action_count_mismatch": baseline_summary.get("action_count") != llm_summary.get("action_count"),
            "entity_key_mismatch": baseline_summary.get("entity_keys_count") != llm_summary.get("entity_keys_count"),
        }

    @staticmethod
    def _log_partial_trust(
        *,
        status: str,
        reason_code: str,
        command_id: Any,
        trace_id: Any,
        corridor_intent: str,
        sample_rate: float,
        sampled: bool,
        latency_ms: Optional[int],
        model_meta: Optional[Dict[str, Any]],
        baseline_summary: Optional[Dict[str, Any]],
        llm_summary: Optional[Dict[str, Any]],
        diff_summary: Optional[Dict[str, Any]],
    ) -> None:
        append_partial_trust_risk_log(
            {
                "trace_id": trace_id,
                "command_id": command_id,
                "corridor_intent": corridor_intent,
                "sample_rate": sample_rate,
                "sampled": sampled,
                "status": status,
                "reason_code": reason_code,
                "latency_ms": latency_ms,
                "model_meta": model_meta,
                "baseline_summary": baseline_summary,
                "llm_summary": llm_summary,
                "diff_summary": diff_summary,
            }
        )
