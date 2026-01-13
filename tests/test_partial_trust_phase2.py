import json

import routers.partial_trust_candidate as partial_candidate
from routers.partial_trust_acceptance import evaluate_candidate
from routers.partial_trust_types import LLMDecisionCandidate


def _candidate(item_name: str = "молоко", confidence: float | None = 0.8):
    return LLMDecisionCandidate(
        intent="add_shopping_item",
        job_type="add_shopping_item",
        proposed_actions=[
            {
                "action": "propose_add_shopping_item",
                "payload": {"item": {"name": item_name}},
            }
        ],
        clarify_question=None,
        clarify_missing_fields=None,
        confidence=confidence,
        model_meta=None,
        latency_ms=12,
        error_type=None,
    )


def test_acceptance_valid_candidate():
    candidate = _candidate()
    accepted, reason, summary = evaluate_candidate(
        candidate,
        corridor_intent="add_shopping_item",
        policy_enabled=True,
        context=None,
    )
    assert accepted is True
    assert reason == "accepted"
    assert summary["action_count"] == 1


def test_acceptance_rejects_wrong_intent():
    candidate = _candidate()
    candidate = LLMDecisionCandidate(
        intent="create_task",
        job_type="create_task",
        proposed_actions=candidate.proposed_actions,
        clarify_question=None,
        clarify_missing_fields=None,
        confidence=0.9,
        model_meta=None,
        latency_ms=10,
        error_type=None,
    )
    accepted, reason, _summary = evaluate_candidate(
        candidate,
        corridor_intent="add_shopping_item",
        policy_enabled=True,
        context=None,
    )
    assert accepted is False
    assert reason == "corridor_mismatch"


def test_acceptance_rejects_invalid_schema():
    candidate = LLMDecisionCandidate(
        intent="add_shopping_item",
        job_type="add_shopping_item",
        proposed_actions=[
            {
                "action": "propose_create_task",
                "payload": {"item": {"name": "молоко"}},
            }
        ],
        clarify_question=None,
        clarify_missing_fields=None,
        confidence=0.9,
        model_meta=None,
        latency_ms=10,
        error_type=None,
    )
    accepted, reason, _summary = evaluate_candidate(
        candidate,
        corridor_intent="add_shopping_item",
        policy_enabled=True,
        context=None,
    )
    assert accepted is False
    assert reason == "invalid_schema"


def test_acceptance_summary_no_raw_item_name():
    candidate = _candidate(item_name="молоко")
    _accepted, _reason, summary = evaluate_candidate(
        candidate,
        corridor_intent="add_shopping_item",
        policy_enabled=True,
        context=None,
    )
    serialized = json.dumps(summary, ensure_ascii=False)
    assert "молоко" not in serialized


def test_candidate_generation_timeout(monkeypatch):
    monkeypatch.setenv("LLM_POLICY_ENABLED", "true")

    def _raise_timeout(*_args, **_kwargs):
        raise TimeoutError("timeout")

    monkeypatch.setattr(partial_candidate, "_run_policy_task", _raise_timeout)
    result = partial_candidate.generate_llm_candidate(
        {"text": "Купи молоко"},
        trace_id="trace-1",
        timeout_ms=10,
        profile_id="partial_trust",
    )
    assert result is None
