import json
import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from llm_policy.errors import LlmUnavailableError
from llm_policy.loader import LlmPolicyLoader
from llm_policy.runtime import resolve_call_spec, run_task_with_policy

SCHEMA = {
    "type": "object",
    "properties": {"item_name": {"type": "string"}},
    "required": ["item_name"],
    "additionalProperties": False,
}


class StubCaller:
    def __init__(self, responses: list[object]) -> None:
        self._responses = list(responses)
        self.calls: list[str] = []

    def __call__(self, spec, prompt: str) -> str:
        self.calls.append(spec.model)
        if not self._responses:
            raise AssertionError("no more responses")
        response = self._responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return str(response)


def test_resolve_call_spec() -> None:
    policy = LlmPolicyLoader.load(enabled=True, allow_placeholders=True)
    assert policy is not None

    spec = resolve_call_spec(policy, "shopping_extraction", "cheap")

    assert spec.provider == "yandex_ai_studio"
    assert spec.model == "gpt-oss-20b"


def test_escalation_sequence_invalid_json_then_reliable_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_POLICY_ENABLED", "true")
    policy = LlmPolicyLoader.load(enabled=True, allow_placeholders=True)
    assert policy is not None

    responses = [
        "not json",
        "still broken",
        json.dumps({"item_name": "молоко"}, ensure_ascii=False),
    ]
    caller = StubCaller(responses)

    result = run_task_with_policy(
        task_id="shopping_extraction",
        prompt="prompt",
        schema=SCHEMA,
        profile="cheap",
        policy=policy,
        caller=caller,
    )

    assert result.status == "ok"
    assert result.escalated is True
    assert result.attempts == 3
    assert caller.calls == ["gpt-oss-20b", "gpt-oss-20b", "gpt-oss-120b"]


def test_timeout_returns_error_without_escalation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_POLICY_ENABLED", "true")
    policy = LlmPolicyLoader.load(enabled=True, allow_placeholders=True)
    assert policy is not None

    caller = StubCaller([TimeoutError("timeout")])

    result = run_task_with_policy(
        task_id="shopping_extraction",
        prompt="prompt",
        schema=SCHEMA,
        profile="cheap",
        policy=policy,
        caller=caller,
    )

    assert result.status == "error"
    assert result.error_type == "timeout"
    assert result.escalated is False
    assert result.attempts == 1


def test_unavailable_returns_error_without_escalation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_POLICY_ENABLED", "true")
    policy = LlmPolicyLoader.load(enabled=True, allow_placeholders=True)
    assert policy is not None

    caller = StubCaller([LlmUnavailableError("down")])

    result = run_task_with_policy(
        task_id="shopping_extraction",
        prompt="prompt",
        schema=SCHEMA,
        profile="cheap",
        policy=policy,
        caller=caller,
    )

    assert result.status == "error"
    assert result.error_type == "llm_unavailable"
    assert result.escalated is False
    assert result.attempts == 1
