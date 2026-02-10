"""Tests for quality evaluation script (ST-026)."""

import json
import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
EVAL_SCRIPTS_DIR = BASE_DIR / "skills" / "quality-eval" / "scripts"

if str(EVAL_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(EVAL_SCRIPTS_DIR))
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from evaluate_golden import build_report, compute_metrics


def _make_result(
    intent_match=True,
    actual_action="clarify",
    expected_action="clarify",
    expected_item_names=None,
    actual_item_names=None,
):
    """Helper to create a synthetic evaluation result dict."""
    return {
        "command_id": "cmd-test",
        "expected_intent": "add_shopping_item",
        "actual_intent": "add_shopping_item" if intent_match else "clarify_needed",
        "intent_match": intent_match,
        "expected_action": expected_action,
        "actual_action": actual_action,
        "action_match": actual_action == expected_action,
        "expected_item_names": expected_item_names or [],
        "actual_item_names": actual_item_names or [],
    }


def test_compute_metrics_deterministic() -> None:
    """AC-1: Deterministic metrics computed correctly from mixed results."""
    results = [
        _make_result(
            intent_match=True,
            actual_action="propose_add_shopping_item",
            expected_action="propose_add_shopping_item",
            expected_item_names=["молоко"],
            actual_item_names=["молоко"],
        ),
        _make_result(
            intent_match=True,
            actual_action="clarify",
            expected_action="clarify",
        ),
        _make_result(
            intent_match=False,
            actual_action="clarify",
            expected_action="propose_create_task",
        ),
    ]
    m = compute_metrics(results)
    assert m["total_entries"] == 3
    assert m["intent_accuracy"] == round(2 / 3, 4)
    assert m["entity_precision"] == 1.0
    assert m["entity_recall"] == 1.0
    assert m["clarify_rate"] == round(2 / 3, 4)
    assert m["start_job_rate"] == round(1 / 3, 4)


def test_intent_accuracy_computation() -> None:
    """Verify intent accuracy fraction with 4 known results."""
    results = [
        _make_result(intent_match=True),
        _make_result(intent_match=True),
        _make_result(intent_match=False),
        _make_result(intent_match=True),
    ]
    m = compute_metrics(results)
    assert m["intent_accuracy"] == 0.75
    assert m["total_entries"] == 4


def test_entity_precision_recall() -> None:
    """Verify entity precision/recall with TP, FP, FN across entries."""
    results = [
        _make_result(
            expected_item_names=["молоко", "хлеб"],
            actual_item_names=["молоко", "масло"],
        ),
        _make_result(
            expected_item_names=["яйца"],
            actual_item_names=["яйца"],
        ),
    ]
    m = compute_metrics(results)
    # Total: TP=2 (молоко, яйца), FP=1 (масло), FN=1 (хлеб)
    assert m["entity_precision"] == round(2 / 3, 4)
    assert m["entity_recall"] == round(2 / 3, 4)


def test_clarify_rate_computation() -> None:
    """Verify clarify and start_job rates with even split."""
    results = [
        _make_result(actual_action="clarify"),
        _make_result(actual_action="propose_add_shopping_item"),
        _make_result(actual_action="propose_create_task"),
        _make_result(actual_action="clarify"),
    ]
    m = compute_metrics(results)
    assert m["clarify_rate"] == 0.5
    assert m["start_job_rate"] == 0.5


def test_report_valid_json() -> None:
    """AC-3: Report is valid JSON with deterministic, llm_assisted, delta keys."""
    det = compute_metrics([_make_result()])
    llm = compute_metrics([_make_result()])
    report = build_report(det, llm)
    serialized = json.dumps(report, ensure_ascii=False)
    parsed = json.loads(serialized)
    assert "deterministic" in parsed
    assert "llm_assisted" in parsed
    assert "delta" in parsed
    for key in (
        "intent_accuracy",
        "entity_precision",
        "entity_recall",
        "clarify_rate",
        "start_job_rate",
    ):
        assert key in parsed["deterministic"]
        assert key in parsed["delta"]


def test_empty_dataset_no_crash() -> None:
    """Edge case: empty dataset produces zero metrics without errors."""
    m = compute_metrics([])
    assert m["total_entries"] == 0
    assert m["intent_accuracy"] == 0.0
    assert m["entity_precision"] == 0.0
    assert m["entity_recall"] == 0.0
    assert m["clarify_rate"] == 0.0
    assert m["start_job_rate"] == 0.0
