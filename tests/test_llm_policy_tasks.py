import json
import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from llm_policy.runtime import set_llm_caller
from llm_policy.tasks import extract_shopping_item_name


class StubCaller:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls = 0

    def __call__(self, spec, prompt: str) -> str:
        self.calls += 1
        return self.response


def test_policy_disabled_uses_rule_based_fixture() -> None:
    fixture_path = (
        BASE_DIR
        / "skills"
        / "graph-sanity"
        / "fixtures"
        / "commands"
        / "grocery_run.json"
    )
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    text = payload["text"]

    result = extract_shopping_item_name(text, policy_enabled=False)

    assert result.used_policy is False
    assert result.item_name == "яблоки и молоко"


def test_policy_enabled_uses_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_POLICY_ENABLED", "true")
    set_llm_caller(StubCaller('{"item_name": "молоко"}'))

    result = extract_shopping_item_name("Купи молоко", policy_enabled=True)

    assert result.used_policy is True
    assert result.item_name == "молоко"
    set_llm_caller(None)
