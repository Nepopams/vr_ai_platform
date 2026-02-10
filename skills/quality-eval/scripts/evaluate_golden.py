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
