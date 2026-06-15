"""Mock decision-making pipeline for HomeTask AI System."""

from __future__ import annotations

import json
import re as _re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

import time
from jsonschema import validate
import logging

_logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]
SCHEMA_DIR = BASE_DIR / "contracts" / "schemas"
CONTRACTS_VERSION_PATH = BASE_DIR / "contracts" / "VERSION"

COMMAND_SCHEMA_PATH = SCHEMA_DIR / "command.schema.json"
DECISION_SCHEMA_PATH = SCHEMA_DIR / "decision.schema.json"


def load_schema(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sample_command() -> Dict[str, Any]:
    return {
        "command_id": "cmd-001",
        "user_id": "user-123",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "text": "Добавь молоко в список покупок",
        "capabilities": [
            "start_job",
            "propose_create_task",
            "propose_add_shopping_item",
            "clarify",
        ],
        "context": {
            "household": {
                "household_id": "house-1",
                "members": [{"user_id": "user-123", "display_name": "Аня"}],
                "shopping_lists": [{"list_id": "list-1", "name": "Продукты"}],
            }
        },
    }


SHOPPING_KEYWORDS = (
    "куп",
    "shopping",
    "grocery",
    "buy",
    "add",
    "добав",
    "закин",
    "покупк",
)
TASK_KEYWORDS = (
    "task",
    "todo",
    "сделай",
    "сделать",
    "нужно",
    "надо",
    "починить",
    "убраться",
    "вынести",
)
DOMAIN_TASK_KEYWORDS = TASK_KEYWORDS + (
    "задач",
    "дело",
    "напомни",
    "remind",
    "assign",
)
CONFIRM_OR_CLARIFY_KEYWORDS = (
    "confirm",
    "подтверд",
    "перенеси",
    "сдвин",
    "reschedule",
    "заверш",
    "complete",
    "done",
    "завтра",
    "план",
    "plan",
    "redistribute",
    "перераспредел",
    "workload",
    "status",
    "статус",
)
SAFE_REJECT_KEYWORDS = (
    "everyone",
    "everybody",
    "all members",
    "all tasks",
    "всем",
    "всех",
    "все задачи",
    "всю работу",
    "невозможно",
    "impossible",
    "unsafe",
)
UNSUPPORTED_POLICY_KEYWORDS = (
    "always",
    "policy",
    "rule",
    "всегда",
    "правил",
)
FOREIGN_HOUSEHOLD_KEYWORDS = (
    "other household",
    "another household",
    "foreign household",
    "другого дома",
    "другой дом",
    "чужого дома",
    "чужой дом",
    "чужой список",
    "чужого списка",
)
DEVICE_CONTROL_VERBS = (
    "turn on",
    "turn off",
    "включ",
    "выключ",
    "запусти",
)
UNSUPPORTED_DEVICE_KEYWORDS = (
    "device",
    "robot vacuum",
    "робот-пылесос",
    "пылесос",
    "умную ламп",
)
UNSUPPORTED_PAYMENT_KEYWORDS = (
    "pay",
    "payment",
    "transfer money",
    "переведи деньг",
    "деньг",
    "оплат",
)
SHOPPING_CONTEXT_MARKER_WORDS = ("к", "для", "на")
DEICTIC_SHOPPING_REFERENCES = ("это", "этот", "эту", "this", "that")
TASK_COMMAND_LEADS = (
    "task",
    "todo",
    "сделай",
    "сделать",
    "нужно",
    "надо",
    "почини",
    "убер",
    "вынеси",
)
TASK_SCHEDULE_MARKERS = (
    "завтра",
    "сегодня",
    "послезавтра",
    "tomorrow",
    "today",
)


def detect_intent(text: str) -> str:
    lowered = text.lower()
    if any(keyword in lowered for keyword in SHOPPING_KEYWORDS):
        return "add_shopping_item"
    if any(keyword in lowered for keyword in TASK_KEYWORDS):
        return "create_task"
    return "clarify_needed"


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def has_unresolved_task_modifier(text: str, intent: str) -> bool:
    if intent != "create_task":
        return False
    lowered = text.lower()
    if _contains_any(lowered, TASK_SCHEDULE_MARKERS):
        return True
    match = _re.match(r"^\s*(\w+)", text, flags=_re.UNICODE)
    if not match:
        return False
    first_word = match.group(1)
    first_lowered = first_word.lower()
    if any(first_lowered.startswith(lead) for lead in TASK_COMMAND_LEADS):
        return False
    return first_word[:1].isupper()


def should_safe_reject(text: str) -> bool:
    lowered = text.lower()
    if _contains_any(lowered, SAFE_REJECT_KEYWORDS):
        return True
    if _contains_any(lowered, UNSUPPORTED_POLICY_KEYWORDS):
        return True
    if _contains_any(lowered, FOREIGN_HOUSEHOLD_KEYWORDS):
        return True
    if _contains_any(lowered, UNSUPPORTED_PAYMENT_KEYWORDS):
        return True
    return _contains_any(lowered, DEVICE_CONTROL_VERBS) and _contains_any(
        lowered,
        UNSUPPORTED_DEVICE_KEYWORDS,
    )


def should_clarify_outside_narrow_corridor(text: str, intent: str) -> bool:
    lowered = text.lower()
    has_shopping = _contains_any(lowered, SHOPPING_KEYWORDS)
    has_task = _contains_any(lowered, DOMAIN_TASK_KEYWORDS)
    if has_shopping and has_task:
        return True
    if intent == "add_shopping_item":
        if _contains_any(lowered, DEICTIC_SHOPPING_REFERENCES):
            return True
        words = set(_re.findall(r"\w+", lowered, flags=_re.UNICODE))
        if words & set(SHOPPING_CONTEXT_MARKER_WORDS):
            return True
    if has_unresolved_task_modifier(text, intent):
        return True
    if intent not in {"add_shopping_item", "create_task"}:
        return _contains_any(lowered, CONFIRM_OR_CLARIFY_KEYWORDS)
    return _contains_any(lowered, CONFIRM_OR_CLARIFY_KEYWORDS) and not (
        intent == "create_task" and ("task" in lowered or "задач" in lowered)
    )


def extract_item_name(text: str) -> Optional[str]:
    lowered = text.lower()
    patterns = ("купить ", "купи ", "buy ", "add ", "добавь ", "добавить ", "закинь ")
    for pattern in patterns:
        if pattern in lowered:
            start = lowered.find(pattern) + len(pattern)
            candidate = text[start:].strip()
            return candidate or None
    return None


def extract_items(text: str) -> List[Dict[str, Any]]:
    """Split shopping text into individual items with optional quantity/unit.

    Supports comma and conjunction ("и"/"and") separation.
    Returns list of dicts: [{name, quantity?, unit?}].
    """
    lowered = text.lower()
    raw = None
    for pattern in ("купить ", "купи ", "buy ", "add ", "добавь ", "добавить ", "закинь "):
        if pattern in lowered:
            start = lowered.find(pattern) + len(pattern)
            raw = text[start:].strip()
            break
    if not raw:
        return []

    # Remove trailing context phrases
    for stop in (" в список", " в корзину", " в покупки", " in the list", " to the list"):
        idx = raw.lower().find(stop)
        if idx > 0:
            raw = raw[:idx].strip()

    # Split on comma and conjunctions
    parts = _re.split(r"\s*,\s*|\s+и\s+|\s+and\s+", raw)
    parts = [p.strip() for p in parts if p.strip()]

    items: List[Dict[str, Any]] = []
    for part in parts:
        item = _parse_item_part(part)
        if item:
            items.append(item)
    return items


def _parse_item_part(part: str) -> Optional[Dict[str, Any]]:
    """Parse a single item part, extracting optional quantity and unit."""
    # Pattern: "2 литра молока" or "3 liters milk"
    match = _re.match(r"^(\d+)\s+(\S+)\s+(.+)$", part)
    if match:
        return {
            "name": match.group(3).strip(),
            "quantity": match.group(1),
            "unit": match.group(2),
        }
    # Pattern: "3 яблока" (quantity without unit)
    match = _re.match(r"^(\d+)\s+(.+)$", part)
    if match:
        return {
            "name": match.group(2).strip(),
            "quantity": match.group(1),
        }
    # Just a name
    return {"name": part}


def build_proposed_action(action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return {"action": action, "payload": payload}


def build_clarify_decision(
    command: Dict[str, Any],
    question: str,
    missing_fields: Optional[List[str]] = None,
    explanation: str = "Нужны уточнения для выполнения запроса.",
) -> Dict[str, Any]:
    schema_version = CONTRACTS_VERSION_PATH.read_text(encoding="utf-8").strip()
    payload: Dict[str, Any] = {"question": question}
    if missing_fields:
        payload["missing_fields"] = missing_fields
    return {
        "decision_id": f"dec-{uuid4().hex}",
        "command_id": command["command_id"],
        "status": "clarify",
        "action": "clarify",
        "confidence": 0.35,
        "payload": payload,
        "explanation": explanation,
        "trace_id": f"trace-{uuid4().hex}",
        "schema_version": schema_version,
        "decision_version": "mvp1-graph-0.1",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def build_reject_decision(
    command: Dict[str, Any],
    *,
    code: str = "unsupported_action",
    reason: str = "Request is outside the supported household command corridor.",
    ui_message: str = "I cannot safely handle this request.",
    details: Optional[Dict[str, Any]] = None,
    explanation: str = "Unsupported command is rejected without proposed mutation.",
) -> Dict[str, Any]:
    schema_version = CONTRACTS_VERSION_PATH.read_text(encoding="utf-8").strip()
    payload: Dict[str, Any] = {
        "code": code,
        "reason": reason,
        "ui_message": ui_message,
    }
    if details:
        payload["details"] = details
    return {
        "decision_id": f"dec-{uuid4().hex}",
        "command_id": command["command_id"],
        "status": "error",
        "action": "reject",
        "decision_outcome": "reject",
        "confidence": 0.2,
        "payload": payload,
        "explanation": explanation,
        "trace_id": f"trace-{uuid4().hex}",
        "schema_version": schema_version,
        "decision_version": "mvp1-graph-0.1",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def build_safe_reject_decision(
    command: Dict[str, Any],
    question: str = "Запрос не может быть выполнен в текущем безопасном коридоре.",
    missing_fields: Optional[List[str]] = None,
    explanation: str = "Запрос отклонен безопасным current-schema mapping.",
) -> Dict[str, Any]:
    details = {"missing_fields": missing_fields} if missing_fields else None
    return build_reject_decision(
        command,
        code="unsupported_or_unsafe_command",
        reason=question,
        ui_message=question,
        details=details,
        explanation=explanation,
    )


def build_start_job_decision(
    command: Dict[str, Any],
    job_type: str,
    proposed_actions: Optional[List[Dict[str, Any]]] = None,
    explanation: str = "Запрос принят, запускаю выполнение.",
) -> Dict[str, Any]:
    schema_version = CONTRACTS_VERSION_PATH.read_text(encoding="utf-8").strip()
    payload: Dict[str, Any] = {
        "job_id": f"job-{uuid4().hex}",
        "job_type": job_type,
    }
    if proposed_actions:
        payload["proposed_actions"] = proposed_actions
    payload["ui_message"] = "Принял, начинаю работу."
    return {
        "decision_id": f"dec-{uuid4().hex}",
        "command_id": command["command_id"],
        "status": "ok",
        "action": "start_job",
        "confidence": 0.78,
        "payload": payload,
        "explanation": explanation,
        "trace_id": f"trace-{uuid4().hex}",
        "schema_version": schema_version,
        "decision_version": "mvp1-graph-0.1",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def _annotate_registry_capabilities(intent: str) -> Dict[str, Any]:
    """Read-only probe: query registry for agents matching intent.

    Returns a registry_snapshot dict for logging. Never raises.
    """
    try:
        from agent_registry.config import is_agent_registry_core_enabled

        if not is_agent_registry_core_enabled():
            return {}

        from agent_registry.v0_loader import AgentRegistryV0Loader, load_capability_catalog
        from agent_registry.capabilities_lookup import CapabilitiesLookup

        registry = AgentRegistryV0Loader.load()
        catalog = load_capability_catalog()
        lookup = CapabilitiesLookup(registry, catalog)

        agents_shadow = lookup.find_agents(intent, "shadow")
        agents_assist = lookup.find_agents(intent, "assist")
        all_agents = agents_shadow + agents_assist

        snapshot: Dict[str, Any] = {
            "intent": intent,
            "available_agents": [
                {"agent_id": a.agent_id, "mode": a.mode}
                for a in all_agents
            ],
            "any_enabled": len(all_agents) > 0,
        }

        _logger.info("registry_snapshot: %s", snapshot)
        return snapshot

    except Exception as exc:
        _logger.warning("registry annotation failed: %s", exc)
        return {"intent": intent, "error": str(exc), "any_enabled": False}


def process_command(command: Dict[str, Any]) -> Dict[str, Any]:
    import time

    from app.logging.fallback_metrics_log import (
        append_fallback_metrics_log,
        is_fallback_metrics_log_enabled,
    )
    from app.logging.pipeline_latency_log import (
        append_pipeline_latency_log,
        is_pipeline_latency_log_enabled,
    )
    from llm_policy.config import is_llm_policy_enabled

    t_start = time.monotonic()

    # Step 1: validate command
    t0 = time.monotonic()
    command_schema = load_schema(COMMAND_SCHEMA_PATH)
    validate(instance=command, schema=command_schema)
    validate_command_ms = (time.monotonic() - t0) * 1000

    # Step 2: detect intent
    t0 = time.monotonic()
    text = command.get("text", "").strip()
    intent = detect_intent(text)
    detect_intent_ms = (time.monotonic() - t0) * 1000

    # Step 3: registry annotation
    t0 = time.monotonic()
    registry_snapshot = _annotate_registry_capabilities(intent)
    registry_ms = (time.monotonic() - t0) * 1000

    # Step 4: core logic
    t0 = time.monotonic()
    capabilities = set(command.get("capabilities", []))

    if "start_job" not in capabilities:
        decision = build_clarify_decision(
            command,
            question="Какие действия разрешены для выполнения?",
            explanation="Отсутствует capability start_job.",
        )
    elif not text:
        decision = build_clarify_decision(
            command,
            question="Опишите, что нужно сделать: задача или покупка?",
            missing_fields=["text"],
            explanation="Текст команды пустой.",
        )
    elif should_safe_reject(text):
        decision = build_safe_reject_decision(
            command,
            missing_fields=["intent.safe_corridor"],
            explanation="Запрос небезопасен или невозможен для узкого коридора.",
        )
    elif should_clarify_outside_narrow_corridor(text, intent):
        decision = build_clarify_decision(
            command,
            question="Уточните один безопасный сценарий: задача или покупка?",
            missing_fields=["intent"],
            explanation="Запрос требует подтверждения или выходит за узкий коридор.",
        )
    elif intent == "add_shopping_item":
        items = extract_items(text)
        item_name = extract_item_name(text)
        if not items and item_name:
            items = [{"name": item_name}]
        if not items:
            decision = build_clarify_decision(
                command,
                question="Какой товар добавить в список покупок?",
                missing_fields=["item.name"],
                explanation="Не удалось извлечь название товара.",
            )
        elif "propose_add_shopping_item" not in capabilities:
            decision = build_clarify_decision(
                command,
                question="Какие действия разрешены для добавления покупки?",
                missing_fields=["capability.propose_add_shopping_item"],
                explanation="Отсутствует capability propose_add_shopping_item.",
            )
        elif not _default_list_id(command):
            decision = build_clarify_decision(
                command,
                question="В какой список покупок добавить товары?",
                missing_fields=["item.list_id"],
                explanation="Список покупок не может быть однозначно определен.",
            )
        else:
            proposed_actions: List[Dict[str, Any]] = []
            list_id = _default_list_id(command)
            for item in items:
                item_payload: Dict[str, Any] = {"name": item["name"]}
                if item.get("quantity"):
                    item_payload["quantity"] = item["quantity"]
                if item.get("unit"):
                    item_payload["unit"] = item["unit"]
                item_payload["list_id"] = list_id
                proposed_actions.append(
                    build_proposed_action(
                        "propose_add_shopping_item",
                        {
                            "item": item_payload
                        },
                    )
                )
            decision = build_start_job_decision(
                command,
                job_type="add_shopping_item",
                proposed_actions=proposed_actions or None,
                explanation="Распознан запрос на добавление покупки.",
            )
    elif intent == "create_task":
        title = text.strip()
        if not title:
            decision = build_clarify_decision(
                command,
                question="Какую задачу нужно создать?",
                missing_fields=["task.title"],
                explanation="Не удалось получить описание задачи.",
            )
        elif "propose_create_task" not in capabilities:
            decision = build_clarify_decision(
                command,
                question="Какие действия разрешены для создания задачи?",
                missing_fields=["capability.propose_create_task"],
                explanation="Отсутствует capability propose_create_task.",
            )
        else:
            proposed_actions = [
                build_proposed_action(
                    "propose_create_task",
                    {
                        "task": {
                            "title": title,
                            "assignee_id": _default_assignee_id(command),
                        }
                    },
                )
            ]
            decision = build_start_job_decision(
                command,
                job_type="create_task",
                proposed_actions=proposed_actions or None,
                explanation="Распознан запрос на создание задачи.",
            )
    else:
        decision = build_clarify_decision(
            command,
            question="Уточните, что нужно сделать: задача или покупка?",
            explanation="Интент не распознан.",
        )
    core_logic_ms = (time.monotonic() - t0) * 1000

    # Step 5: validate decision
    t0 = time.monotonic()
    decision_schema = load_schema(DECISION_SCHEMA_PATH)
    validate(instance=decision, schema=decision_schema)
    validate_decision_ms = (time.monotonic() - t0) * 1000

    total_ms = (time.monotonic() - t_start) * 1000

    llm_on = is_llm_policy_enabled()

    # Emit latency record
    if is_pipeline_latency_log_enabled():
        append_pipeline_latency_log(
            {
                "command_id": command.get("command_id"),
                "trace_id": decision.get("trace_id"),
                "total_ms": round(total_ms, 3),
                "steps": {
                    "validate_command_ms": round(validate_command_ms, 3),
                    "detect_intent_ms": round(detect_intent_ms, 3),
                    "registry_ms": round(registry_ms, 3),
                    "core_logic_ms": round(core_logic_ms, 3),
                    "validate_decision_ms": round(validate_decision_ms, 3),
                },
                "llm_enabled": llm_on,
            }
        )

    # Emit fallback metrics record
    if is_fallback_metrics_log_enabled():
        append_fallback_metrics_log(
            {
                "command_id": command.get("command_id"),
                "trace_id": decision.get("trace_id"),
                "intent": intent,
                "decision_action": decision.get("action"),
                "llm_outcome": "skipped" if not llm_on else "deterministic_only",
                "fallback_reason": "policy_disabled" if not llm_on else None,
                "deterministic_used": True,
                "llm_latency_ms": None,
                "components": {},
            }
        )

    return decision


def _default_list_id(command: Dict[str, Any]) -> Optional[str]:
    defaults = command.get("context", {}).get("defaults", {})
    if defaults.get("default_list_id"):
        return defaults["default_list_id"]

    lists = command.get("context", {}).get("household", {}).get("shopping_lists", [])
    if len(lists) == 1:
        return lists[0].get("list_id")
    return None


def _default_assignee_id(command: Dict[str, Any]) -> Optional[str]:
    defaults = command.get("context", {}).get("defaults", {})
    if defaults.get("default_assignee_id"):
        return defaults["default_assignee_id"]
    return command.get("user_id")


def main() -> None:
    command = sample_command()
    decision = process_command(command)
    print(json.dumps(decision, indent=2))


if __name__ == "__main__":
    main()
