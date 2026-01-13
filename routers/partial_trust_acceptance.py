"""Acceptance rules for partial trust corridor (internal-only)."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional, Tuple

from llm_policy.config import is_llm_policy_enabled
from routers.partial_trust_types import LLMDecisionCandidate


_ALLOWED_ACTION = "propose_add_shopping_item"
_ALLOWED_PAYLOAD_KEYS = {"item", "idempotency_key"}
_ALLOWED_ITEM_KEYS = {"name", "quantity", "unit", "list_id"}
_MIN_ITEM_NAME_LEN = 1
_MAX_ITEM_NAME_LEN = 120
_MIN_CONFIDENCE = 0.6


def evaluate_candidate(
    candidate: LLMDecisionCandidate | None,
    *,
    corridor_intent: str | None,
    policy_enabled: bool | None = None,
    context: Optional[Dict[str, Any]] = None,
) -> Tuple[bool, str, Dict[str, Any]]:
    summary = _build_summary(candidate)
    if corridor_intent is None:
        return False, "corridor_disabled", summary
    if candidate is None:
        return False, "candidate_missing", summary
    if not _policy_gate(policy_enabled):
        return False, "policy_disabled", summary
    if candidate.intent != corridor_intent or (
        candidate.job_type is not None and candidate.job_type != corridor_intent
    ):
        return False, "corridor_mismatch", summary
    if not _validate_shape(candidate):
        return False, "invalid_schema", summary
    if not _validate_item_name(candidate):
        return False, "invalid_item_name", summary
    if not _validate_list_id(candidate, context):
        return False, "list_id_unknown", summary
    if not _passes_confidence(candidate):
        return False, "low_confidence", summary
    return True, "accepted", summary


def _policy_gate(policy_enabled: bool | None) -> bool:
    if policy_enabled is None:
        return is_llm_policy_enabled()
    return policy_enabled


def _validate_shape(candidate: LLMDecisionCandidate) -> bool:
    proposed_actions = candidate.proposed_actions
    if not isinstance(proposed_actions, list) or len(proposed_actions) != 1:
        return False
    action = proposed_actions[0]
    if not isinstance(action, dict):
        return False
    if set(action.keys()) - {"action", "payload"}:
        return False
    if action.get("action") != _ALLOWED_ACTION:
        return False
    payload = action.get("payload")
    if not isinstance(payload, dict):
        return False
    if set(payload.keys()) - _ALLOWED_PAYLOAD_KEYS:
        return False
    item = payload.get("item")
    if not isinstance(item, dict):
        return False
    if set(item.keys()) - _ALLOWED_ITEM_KEYS:
        return False
    return _validate_item_payload(item)


def _validate_item_payload(item: Dict[str, Any]) -> bool:
    name = item.get("name")
    if not isinstance(name, str) or not name.strip():
        return False
    for key in ("quantity", "unit", "list_id"):
        value = item.get(key)
        if value is None:
            continue
        if not isinstance(value, str) or not value.strip():
            return False
    return True


def _validate_item_name(candidate: LLMDecisionCandidate) -> bool:
    item = _extract_item(candidate)
    if item is None:
        return False
    name = item.get("name", "")
    if not isinstance(name, str):
        return False
    length = len(name.strip())
    return _MIN_ITEM_NAME_LEN <= length <= _MAX_ITEM_NAME_LEN


def _validate_list_id(candidate: LLMDecisionCandidate, context: Optional[Dict[str, Any]]) -> bool:
    item = _extract_item(candidate)
    if item is None:
        return False
    list_id = item.get("list_id")
    if list_id is None:
        return True
    if not isinstance(list_id, str) or not list_id.strip():
        return False
    known_lists = _collect_list_ids(context)
    if not known_lists:
        return False
    return list_id in known_lists


def _passes_confidence(candidate: LLMDecisionCandidate) -> bool:
    if candidate.confidence is None:
        return True
    return candidate.confidence >= _MIN_CONFIDENCE


def _extract_item(candidate: LLMDecisionCandidate) -> Optional[Dict[str, Any]]:
    if not candidate.proposed_actions:
        return None
    payload = candidate.proposed_actions[0].get("payload", {})
    if not isinstance(payload, dict):
        return None
    item = payload.get("item")
    if not isinstance(item, dict):
        return None
    return item


def _collect_list_ids(context: Optional[Dict[str, Any]]) -> set[str]:
    if not context:
        return set()
    household = context.get("household", {})
    lists = household.get("shopping_lists", [])
    if not isinstance(lists, list):
        return set()
    return {item.get("list_id") for item in lists if isinstance(item, dict) and item.get("list_id")}


def _build_summary(candidate: LLMDecisionCandidate | None) -> Dict[str, Any]:
    if candidate is None:
        return {
            "action_count": 0,
            "entity_keys_count": 0,
            "has_list_id": False,
            "item_name_len": 0,
            "confidence_bucket": "missing",
        }
    item = _extract_item(candidate)
    item_name_len = 0
    has_list_id = False
    entity_keys_count = 0
    if item:
        name = item.get("name")
        if isinstance(name, str):
            item_name_len = len(name.strip())
        list_id = item.get("list_id")
        has_list_id = isinstance(list_id, str) and bool(list_id.strip())
        entity_keys_count = len(item.keys())
    return {
        "action_count": len(candidate.proposed_actions or []),
        "entity_keys_count": entity_keys_count,
        "has_list_id": has_list_id,
        "item_name_len": item_name_len,
        "confidence_bucket": _bucket_confidence(candidate.confidence),
    }


def _bucket_confidence(value: float | None) -> str:
    if value is None:
        return "missing"
    if value >= 0.8:
        return "high"
    if value >= 0.6:
        return "medium"
    return "low"
