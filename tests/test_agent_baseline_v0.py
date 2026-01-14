import json
import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agent_registry.v0_loader import AgentRegistryV0Loader
from agent_registry.v0_runner import run


def _read_log(path: Path) -> dict:
    content = path.read_text(encoding="utf-8").strip().splitlines()
    return json.loads(content[-1])


def _load_registry() -> dict:
    registry = AgentRegistryV0Loader.load()
    return {agent.agent_id: agent for agent in registry.agents}


def test_registry_contains_baseline_agents():
    agents = _load_registry()
    assert "baseline-shopping-extractor" in agents
    assert "baseline-clarify-suggestor" in agents


def test_runner_baseline_agents(tmp_path, monkeypatch):
    monkeypatch.setenv("AGENT_RUN_LOG_ENABLED", "false")
    agents = _load_registry()

    shopping_output = run(
        agents["baseline-shopping-extractor"],
        {"text": "Купи молоко", "context": {"household": {"shopping_lists": []}}},
    )
    assert shopping_output.status == "ok"
    assert "items" in (shopping_output.payload or {})

    clarify_output = run(
        agents["baseline-clarify-suggestor"],
        {"text": ""},
    )
    assert clarify_output.status == "ok"
    assert "question" in (clarify_output.payload or {})


def test_agent_run_log_privacy(tmp_path, monkeypatch):
    log_path = tmp_path / "agent_run.jsonl"
    monkeypatch.setenv("AGENT_RUN_LOG_ENABLED", "true")
    monkeypatch.setenv("AGENT_RUN_LOG_PATH", str(log_path))
    agents = _load_registry()

    run(
        agents["baseline-shopping-extractor"],
        {"text": "Купи молоко", "command_id": "cmd-1"},
    )
    logged = _read_log(log_path)
    summary = logged.get("payload_summary", {})
    serialized = json.dumps(summary, ensure_ascii=False)

    assert "молоко" not in serialized
    _assert_no_string_values(summary)


def _assert_no_string_values(summary):
    for key, value in summary.items():
        if key == "keys_present":
            assert isinstance(value, list)
            assert all(isinstance(item, str) for item in value)
            continue
        _assert_value_safe(value)


def _assert_value_safe(value):
    if isinstance(value, str):
        raise AssertionError("string values are not allowed in payload_summary")
    if isinstance(value, list):
        if any(isinstance(item, str) for item in value):
            raise AssertionError("string values are not allowed in payload_summary lists")
        for item in value:
            _assert_value_safe(item)
    if isinstance(value, dict):
        for item in value.values():
            _assert_value_safe(item)
