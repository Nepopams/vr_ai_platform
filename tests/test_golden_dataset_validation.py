"""Validation tests for the expanded golden dataset."""

import json
import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

GOLDEN_PATH = BASE_DIR / "skills" / "graph-sanity" / "fixtures" / "golden_dataset.json"


def _load_golden():
    return json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))


def test_golden_dataset_has_20_plus_entries() -> None:
    """AC-1: Dataset has 20+ entries."""
    data = _load_golden()
    assert len(data) >= 20, f"Expected >= 20 entries, got {len(data)}"


def test_golden_dataset_all_intents_represented() -> None:
    """AC-2: Each intent has >= 3 entries."""
    data = _load_golden()
    by_intent: dict[str, list] = {}
    for entry in data:
        by_intent.setdefault(entry["expected_intent"], []).append(entry)
    for intent in ["add_shopping_item", "create_task", "clarify_needed"]:
        count = len(by_intent.get(intent, []))
        assert count >= 3, f"Intent '{intent}' has only {count} entries, expected >= 3"


def test_golden_dataset_has_hard_cases() -> None:
    """AC-3: At least 3 entries with difficulty='hard'."""
    data = _load_golden()
    hard = [e for e in data if e.get("difficulty") == "hard"]
    assert len(hard) >= 3, f"Only {len(hard)} hard entries, expected >= 3"
