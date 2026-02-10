# Codex APPLY Prompt — ST-026: Quality Evaluation Script with Metrics

## Role
You are a senior Python developer creating a quality evaluation script and its tests.

## Context (from PLAN findings)

- `process_command(command: Dict) -> Dict` at `graphs/core_graph.py:228`.
- `detect_intent(text: str) -> str` at `graphs/core_graph.py:56`. Returns `"add_shopping_item"`, `"create_task"`, or `"clarify_needed"`.
- `extract_items(text: str) -> List[Dict]` at `graphs/core_graph.py:76`. Returns list of `{"name": ..., "quantity"?: ..., "unit"?: ...}`.
- `is_llm_policy_enabled()` at `llm_policy/config.py:7`.
- Golden dataset: 22 entries at `skills/graph-sanity/fixtures/golden_dataset.json`.
- Fixture commands: `skills/graph-sanity/fixtures/commands/{fixture_file}`.
- Decision has `action` ("start_job" or "clarify"), `payload.proposed_actions[].action`.
- process_command writes to pipeline_latency_log and fallback_metrics_log (side effects).
- No naming conflicts: `skills/quality-eval/` and `tests/test_quality_eval.py` don't exist.
- Pattern: `run_graph_suite.py` uses REPO_ROOT + sys.path for imports.

## Files to Create

### 1. `skills/quality-eval/scripts/evaluate_golden.py` (NEW)

Create directory `skills/quality-eval/scripts/` first, then create this file with EXACT content:

```python
"""Quality evaluation script for golden dataset (ST-026)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
FIXTURE_DIR = REPO_ROOT / "skills" / "graph-sanity" / "fixtures"
GOLDEN_DATASET_PATH = FIXTURE_DIR / "golden_dataset.json"
COMMANDS_DIR = FIXTURE_DIR / "commands"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def load_golden_dataset(path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Load golden dataset entries from JSON file."""
    p = path or GOLDEN_DATASET_PATH
    return json.loads(p.read_text(encoding="utf-8"))


def load_fixture_command(fixture_dir: Path, filename: str) -> Dict[str, Any]:
    """Load a single command fixture by filename."""
    return json.loads((fixture_dir / filename).read_text(encoding="utf-8"))


def evaluate_entry(
    entry: Dict[str, Any],
    fixture_dir: Path,
) -> Dict[str, Any]:
    """Run a single golden dataset entry through the pipeline and return result."""
    from graphs.core_graph import detect_intent, extract_items, process_command

    command = load_fixture_command(fixture_dir, entry["fixture_file"])
    decision = process_command(command)
    text = command.get("text", "").strip()

    actual_intent = detect_intent(text)

    # Determine actual action from decision
    if decision["action"] == "clarify":
        actual_action = "clarify"
    else:
        proposed = decision.get("payload", {}).get("proposed_actions", [])
        actual_action = proposed[0]["action"] if proposed else decision["action"]

    # Extract actual item names via extract_items
    actual_item_names: List[str] = []
    if actual_intent == "add_shopping_item" and decision["action"] != "clarify":
        items = extract_items(text)
        actual_item_names = [item["name"] for item in items]

    return {
        "command_id": entry["command_id"],
        "expected_intent": entry["expected_intent"],
        "actual_intent": actual_intent,
        "intent_match": actual_intent == entry["expected_intent"],
        "expected_action": entry["expected_action"],
        "actual_action": actual_action,
        "action_match": actual_action == entry["expected_action"],
        "expected_item_names": entry.get("expected_item_names", []),
        "actual_item_names": actual_item_names,
    }


def compute_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute aggregate quality metrics from evaluation results."""
    total = len(results)
    if total == 0:
        return {
            "intent_accuracy": 0.0,
            "entity_precision": 0.0,
            "entity_recall": 0.0,
            "clarify_rate": 0.0,
            "start_job_rate": 0.0,
            "total_entries": 0,
        }

    intent_correct = sum(1 for r in results if r["intent_match"])

    # Entity precision/recall — only entries with expected_item_names
    tp = 0
    fp = 0
    fn = 0
    for r in results:
        expected = r.get("expected_item_names", [])
        if not expected:
            continue
        expected_lower = {n.lower() for n in expected}
        actual_lower = {n.lower() for n in r.get("actual_item_names", [])}
        tp += len(expected_lower & actual_lower)
        fp += len(actual_lower - expected_lower)
        fn += len(expected_lower - actual_lower)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

    clarify_count = sum(1 for r in results if r["actual_action"] == "clarify")
    start_job_count = total - clarify_count

    return {
        "intent_accuracy": round(intent_correct / total, 4),
        "entity_precision": round(precision, 4),
        "entity_recall": round(recall, 4),
        "clarify_rate": round(clarify_count / total, 4),
        "start_job_rate": round(start_job_count / total, 4),
        "total_entries": total,
    }


def build_report(
    deterministic_metrics: Dict[str, Any],
    llm_metrics: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a JSON-serializable evaluation report."""
    report: Dict[str, Any] = {
        "deterministic": deterministic_metrics,
    }
    if llm_metrics is not None:
        report["llm_assisted"] = llm_metrics
        report["delta"] = {
            k: round(llm_metrics[k] - deterministic_metrics[k], 4)
            for k in deterministic_metrics
            if isinstance(deterministic_metrics[k], float)
        }
    return report


def main() -> None:
    """Run evaluation and print JSON report to stdout."""
    from llm_policy.config import is_llm_policy_enabled

    entries = load_golden_dataset()
    results = [evaluate_entry(e, COMMANDS_DIR) for e in entries]
    det_metrics = compute_metrics(results)

    llm_on = is_llm_policy_enabled()
    llm_metrics = det_metrics if llm_on else None

    report = build_report(det_metrics, llm_metrics)
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
```

### 2. `tests/test_quality_eval.py` (NEW)

Create this file with EXACT content:

```python
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
```

## Files NOT Modified (invariants)
- `graphs/core_graph.py` — DO NOT CHANGE
- `skills/graph-sanity/**` — DO NOT CHANGE
- `llm_policy/**` — DO NOT CHANGE
- `tests/test_golden_dataset_validation.py` — DO NOT CHANGE
- `tests/test_core_graph_registry_gate.py` — DO NOT CHANGE
- `tests/test_pipeline_latency.py` — DO NOT CHANGE
- `tests/test_fallback_metrics.py` — DO NOT CHANGE

## Verification Commands

```bash
# New evaluation tests
source .venv/bin/activate && python3 -m pytest tests/test_quality_eval.py -v

# Run evaluation script in stub mode (deterministic only)
source .venv/bin/activate && python3 skills/quality-eval/scripts/evaluate_golden.py

# Graph sanity tests still pass
source .venv/bin/activate && python3 -m pytest tests/test_golden_dataset_validation.py -v

# Full test suite
source .venv/bin/activate && python3 -m pytest --tb=short -q
```

## STOP-THE-LINE
If any of the following occur, STOP and report:
- Existing tests fail after your changes
- Any file listed as "DO NOT CHANGE" needs modification
- evaluate_golden.py crashes on any of the 22 golden dataset entries
- Import errors from graphs.core_graph
