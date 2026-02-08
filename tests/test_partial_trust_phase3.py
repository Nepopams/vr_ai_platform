import json
from pathlib import Path

import routers.partial_trust_candidate as partial_candidate
import routers.v2 as v2_module
from routers.partial_trust_types import LLMDecisionCandidate
from routers.v2 import RouterV2Pipeline


def _command(text: str = "Купи молоко"):
    return {
        "command_id": "cmd-123",
        "user_id": "user-1",
        "timestamp": "2026-01-12T10:00:00Z",
        "text": text,
        "capabilities": ["start_job", "propose_add_shopping_item", "clarify"],
        "context": {
            "household": {
                "members": [{"user_id": "user-1", "display_name": "Анна"}],
                "shopping_lists": [{"list_id": "list-1", "name": "Основной"}],
            }
        },
    }


def _read_log(path: Path):
    content = path.read_text(encoding="utf-8").strip().splitlines()
    return json.loads(content[-1])


def _candidate(item_name: str = "бананы", confidence: float | None = 0.9):
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
        model_meta={"profile": "partial_trust", "task_id": "partial_trust_shopping"},
        latency_ms=12,
        error_type=None,
    )


def test_partial_trust_disabled_no_llm(monkeypatch):
    monkeypatch.setenv("PARTIAL_TRUST_ENABLED", "false")
    monkeypatch.setattr(
        partial_candidate,
        "generate_llm_candidate_with_meta",
        lambda *_args, **_kwargs: (_raise_if_called()),
    )

    router = RouterV2Pipeline()
    decision = router.decide(_command())
    assert decision["action"] == "start_job"


def test_partial_trust_not_sampled_logs(monkeypatch, tmp_path):
    log_path = tmp_path / "risk.jsonl"
    monkeypatch.setenv("PARTIAL_TRUST_ENABLED", "true")
    monkeypatch.setenv("PARTIAL_TRUST_INTENT", "add_shopping_item")
    monkeypatch.setenv("PARTIAL_TRUST_SAMPLE_RATE", "0")
    monkeypatch.setenv("PARTIAL_TRUST_RISK_LOG_PATH", str(log_path))
    monkeypatch.setattr(partial_candidate, "policy_route_available", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(
        partial_candidate,
        "generate_llm_candidate_with_meta",
        lambda *_args, **_kwargs: (_raise_if_called()),
    )

    router = RouterV2Pipeline()
    decision = router.decide(_command())
    assert decision["action"] == "start_job"

    logged = _read_log(log_path)
    assert logged["status"] == "not_sampled"
    assert "Купи" not in json.dumps(logged, ensure_ascii=False)


def test_partial_trust_accepts_candidate(monkeypatch, tmp_path):
    log_path = tmp_path / "risk.jsonl"
    monkeypatch.setenv("PARTIAL_TRUST_ENABLED", "true")
    monkeypatch.setenv("PARTIAL_TRUST_INTENT", "add_shopping_item")
    monkeypatch.setenv("PARTIAL_TRUST_SAMPLE_RATE", "1")
    monkeypatch.setenv("PARTIAL_TRUST_RISK_LOG_PATH", str(log_path))
    monkeypatch.setattr(v2_module, "policy_route_available", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(
        v2_module,
        "generate_llm_candidate_with_meta",
        lambda *_args, **_kwargs: (_candidate(), None),
    )

    router = RouterV2Pipeline()
    decision = router.decide(_command())
    proposed = decision["payload"]["proposed_actions"][0]
    assert proposed["payload"]["item"]["name"] == "бананы"

    logged = _read_log(log_path)
    assert logged["status"] == "accepted_llm"
    assert "бананы" not in json.dumps(logged, ensure_ascii=False)


def test_partial_trust_rejected_candidate(monkeypatch, tmp_path):
    log_path = tmp_path / "risk.jsonl"
    monkeypatch.setenv("PARTIAL_TRUST_ENABLED", "true")
    monkeypatch.setenv("PARTIAL_TRUST_INTENT", "add_shopping_item")
    monkeypatch.setenv("PARTIAL_TRUST_SAMPLE_RATE", "1")
    monkeypatch.setenv("PARTIAL_TRUST_RISK_LOG_PATH", str(log_path))
    monkeypatch.setattr(v2_module, "policy_route_available", lambda *_args, **_kwargs: True)
    bad_candidate = LLMDecisionCandidate(
        intent="create_task",
        job_type="create_task",
        proposed_actions=_candidate().proposed_actions,
        clarify_question=None,
        clarify_missing_fields=None,
        confidence=0.9,
        model_meta=None,
        latency_ms=10,
        error_type=None,
    )
    monkeypatch.setattr(
        v2_module,
        "generate_llm_candidate_with_meta",
        lambda *_args, **_kwargs: (bad_candidate, None),
    )

    router = RouterV2Pipeline()
    decision = router.decide(_command())
    assert decision["action"] == "start_job"

    logged = _read_log(log_path)
    assert logged["status"] == "fallback_deterministic"
    assert logged["reason_code"] == "corridor_mismatch"


def _raise_if_called():
    raise AssertionError("LLM candidate should not be called")
