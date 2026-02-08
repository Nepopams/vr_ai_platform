"""Edge case tests for partial trust acceptance rules, v2 error catch-all, and privacy."""

import json
from pathlib import Path

import routers.partial_trust_candidate as partial_candidate
import routers.v2 as v2_module
from routers.partial_trust_acceptance import evaluate_candidate
from routers.partial_trust_types import LLMDecisionCandidate
from routers.v2 import RouterV2Pipeline


# ---------------------------------------------------------------------------
# Helpers (reuse patterns from phase2/phase3)
# ---------------------------------------------------------------------------

def _candidate(
    item_name: str = "молоко",
    confidence: float | None = 0.8,
    list_id: str | None = None,
):
    item = {"name": item_name}
    if list_id is not None:
        item["list_id"] = list_id
    return LLMDecisionCandidate(
        intent="add_shopping_item",
        job_type="add_shopping_item",
        proposed_actions=[
            {
                "action": "propose_add_shopping_item",
                "payload": {"item": item},
            }
        ],
        clarify_question=None,
        clarify_missing_fields=None,
        confidence=confidence,
        model_meta={"profile": "partial_trust", "task_id": "partial_trust_shopping"},
        latency_ms=12,
        error_type=None,
    )


def _context_with_lists(*list_ids: str):
    return {
        "household": {
            "members": [{"user_id": "user-1", "display_name": "Анна"}],
            "shopping_lists": [{"list_id": lid, "name": f"List {lid}"} for lid in list_ids],
        }
    }


def _command(text: str = "Купи молоко"):
    return {
        "command_id": "cmd-edge-1",
        "user_id": "user-1",
        "timestamp": "2026-02-08T10:00:00Z",
        "text": text,
        "capabilities": ["start_job", "propose_add_shopping_item", "clarify"],
        "context": _context_with_lists("list-1"),
    }


def _read_all_logs(path: Path):
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    return [json.loads(line) for line in lines]


# ---------------------------------------------------------------------------
# Confidence boundary tests (AC-3 of story, initiative AC2)
# ---------------------------------------------------------------------------

def test_confidence_059_rejected():
    """confidence=0.59 must be rejected (threshold is >= 0.6)."""
    candidate = _candidate(confidence=0.59)
    accepted, reason, _summary = evaluate_candidate(
        candidate,
        corridor_intent="add_shopping_item",
        policy_enabled=True,
        context=None,
    )
    assert accepted is False
    assert reason == "low_confidence"


def test_confidence_060_accepted():
    """confidence=0.60 must be accepted (threshold is >= 0.6)."""
    candidate = _candidate(confidence=0.60)
    accepted, reason, _summary = evaluate_candidate(
        candidate,
        corridor_intent="add_shopping_item",
        policy_enabled=True,
        context=None,
    )
    assert accepted is True
    assert reason == "accepted"


def test_confidence_none_accepted():
    """confidence=None must be accepted (passthrough when no confidence)."""
    candidate = _candidate(confidence=None)
    accepted, reason, _summary = evaluate_candidate(
        candidate,
        corridor_intent="add_shopping_item",
        policy_enabled=True,
        context=None,
    )
    assert accepted is True
    assert reason == "accepted"


# ---------------------------------------------------------------------------
# list_id validation tests (AC-4 of story, initiative AC2)
# ---------------------------------------------------------------------------

def test_list_id_known_accepted():
    """list_id='list-1' with context containing list-1 → accepted."""
    candidate = _candidate(list_id="list-1")
    context = _context_with_lists("list-1")
    accepted, reason, _summary = evaluate_candidate(
        candidate,
        corridor_intent="add_shopping_item",
        policy_enabled=True,
        context=context,
    )
    assert accepted is True
    assert reason == "accepted"


def test_list_id_unknown_rejected():
    """list_id='unknown' with context containing only list-1 → rejected."""
    candidate = _candidate(list_id="unknown-list")
    context = _context_with_lists("list-1")
    accepted, reason, _summary = evaluate_candidate(
        candidate,
        corridor_intent="add_shopping_item",
        policy_enabled=True,
        context=context,
    )
    assert accepted is False
    assert reason == "list_id_unknown"


def test_list_id_no_context_rejected():
    """list_id='list-1' but context=None → rejected (no known lists)."""
    candidate = _candidate(list_id="list-1")
    accepted, reason, _summary = evaluate_candidate(
        candidate,
        corridor_intent="add_shopping_item",
        policy_enabled=True,
        context=None,
    )
    assert accepted is False
    assert reason == "list_id_unknown"


# ---------------------------------------------------------------------------
# Error catch-all test (AC-5 of story, initiative AC3)
# ---------------------------------------------------------------------------

def test_v2_partial_trust_error_catchall(monkeypatch, tmp_path):
    """Exception during LLM candidate generation → baseline used, risk-log status='error'."""
    log_path = tmp_path / "risk.jsonl"
    monkeypatch.setenv("PARTIAL_TRUST_ENABLED", "true")
    monkeypatch.setenv("PARTIAL_TRUST_INTENT", "add_shopping_item")
    monkeypatch.setenv("PARTIAL_TRUST_SAMPLE_RATE", "1")
    monkeypatch.setenv("PARTIAL_TRUST_RISK_LOG_PATH", str(log_path))
    monkeypatch.setattr(v2_module, "policy_route_available", lambda *_a, **_kw: True)
    monkeypatch.setattr(
        v2_module,
        "generate_llm_candidate_with_meta",
        lambda *_a, **_kw: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    router = RouterV2Pipeline()
    decision = router.decide(_command())
    # Baseline must be used (deterministic fallback)
    assert decision["action"] == "start_job"

    logs = _read_all_logs(log_path)
    error_logs = [e for e in logs if e["status"] == "error"]
    assert len(error_logs) >= 1
    assert error_logs[0]["reason_code"] == "RuntimeError"


# ---------------------------------------------------------------------------
# Privacy re-verification (AC-6 of story, initiative AC4)
# ---------------------------------------------------------------------------

def test_risk_log_privacy_all_paths(monkeypatch, tmp_path):
    """No raw user text or item names in risk-log across all paths."""
    log_path = tmp_path / "risk.jsonl"
    monkeypatch.setenv("PARTIAL_TRUST_ENABLED", "true")
    monkeypatch.setenv("PARTIAL_TRUST_INTENT", "add_shopping_item")
    monkeypatch.setenv("PARTIAL_TRUST_SAMPLE_RATE", "1")
    monkeypatch.setenv("PARTIAL_TRUST_RISK_LOG_PATH", str(log_path))
    monkeypatch.setattr(v2_module, "policy_route_available", lambda *_a, **_kw: True)

    good_candidate = _candidate(item_name="бананы", confidence=0.9)
    bad_candidate = _candidate(item_name="яблоки", confidence=0.1)

    # Path 1: accepted_llm
    monkeypatch.setattr(
        v2_module,
        "generate_llm_candidate_with_meta",
        lambda *_a, **_kw: (good_candidate, None),
    )
    router = RouterV2Pipeline()
    router.decide(_command("Купи бананы"))

    # Path 2: fallback_deterministic (low confidence)
    monkeypatch.setattr(
        v2_module,
        "generate_llm_candidate_with_meta",
        lambda *_a, **_kw: (bad_candidate, None),
    )
    router2 = RouterV2Pipeline()
    router2.decide(_command("Купи яблоки"))

    # Path 3: error
    monkeypatch.setattr(
        v2_module,
        "generate_llm_candidate_with_meta",
        lambda *_a, **_kw: (_ for _ in ()).throw(RuntimeError("fail")),
    )
    router3 = RouterV2Pipeline()
    router3.decide(_command("Купи молоко"))

    # Verify privacy across all logged entries
    all_logs_text = log_path.read_text(encoding="utf-8")
    for raw_text in ("бананы", "яблоки", "молоко", "Купи"):
        assert raw_text not in all_logs_text, f"Raw text '{raw_text}' found in risk-log"
