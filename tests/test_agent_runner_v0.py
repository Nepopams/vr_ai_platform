import sys
import time
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agent_registry.v0_models import AgentCapability, AgentSpec, RunnerSpec, TimeoutSpec
from agent_registry.v0_reason_codes import (
    REASON_EXCEPTION,
    REASON_POLICY_DISABLED,
    REASON_TIMEOUT,
)
from agent_registry.v0_runner import STATUS_ERROR, STATUS_OK, STATUS_SKIPPED, run
from llm_policy.models import TaskRunResult


def _agent_spec(kind: str, ref: str, timeout_ms: int | None = None) -> AgentSpec:
    return AgentSpec(
        agent_id="agent-1",
        enabled=True,
        mode="assist",
        capabilities=(
            AgentCapability(
                capability_id="extract_entities.shopping",
                allowed_intents=("add_shopping_item",),
                risk_level=None,
            ),
        ),
        runner=RunnerSpec(kind=kind, ref=ref),
        timeouts=TimeoutSpec(timeout_ms=timeout_ms),
        privacy=None,
        llm_profile_id=None,
    )


def _catalog_payload():
    return {
        "extract_entities.shopping": {
            "payload_allowlist": {"items"},
            "allowed_modes": {"assist"},
            "contains_sensitive_text": True,
            "risk_level": "low",
            "allowed_intents": ("add_shopping_item",),
        }
    }


def _write_module(tmp_path: Path) -> str:
    module_path = tmp_path / "tmp_agent.py"
    module_path.write_text(
        "\n".join(
            [
                "import time",
                "def ok(input, trace_id=None):",
                "    return {'items': []}",
                "def fail(input, trace_id=None):",
                "    raise RuntimeError('boom')",
                "def slow(input, trace_id=None):",
                "    time.sleep(0.2)",
                "    return {'items': []}",
            ]
        ),
        encoding="utf-8",
    )
    return "tmp_agent"


def test_python_module_success(monkeypatch, tmp_path):
    module_name = _write_module(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.setattr("agent_registry.v0_runner.load_capability_catalog", lambda *_args, **_kwargs: _catalog_payload())

    output = run(_agent_spec("python_module", f"{module_name}:ok"), {"text": "x"})

    assert output.status == STATUS_OK


def test_python_module_exception(monkeypatch, tmp_path):
    module_name = _write_module(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.setattr("agent_registry.v0_runner.load_capability_catalog", lambda *_args, **_kwargs: _catalog_payload())

    output = run(_agent_spec("python_module", f"{module_name}:fail"), {"text": "x"})

    assert output.status == STATUS_ERROR
    assert output.reason_code == REASON_EXCEPTION


def test_python_module_timeout(monkeypatch, tmp_path):
    module_name = _write_module(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.setattr("agent_registry.v0_runner.load_capability_catalog", lambda *_args, **_kwargs: _catalog_payload())

    output = run(_agent_spec("python_module", f"{module_name}:slow", timeout_ms=10), {"text": "x"})

    assert output.status == STATUS_ERROR
    assert output.reason_code == REASON_TIMEOUT


def test_llm_policy_task_disabled(monkeypatch):
    monkeypatch.setattr("agent_registry.v0_runner.load_capability_catalog", lambda *_args, **_kwargs: _catalog_payload())
    monkeypatch.setattr("agent_registry.v0_runner.is_llm_policy_enabled", lambda: False)

    output = run(_agent_spec("llm_policy_task", "assist_entity_extraction"), {"text": "x"})

    assert output.status == STATUS_SKIPPED
    assert output.reason_code == REASON_POLICY_DISABLED


def test_llm_policy_task_ok(monkeypatch):
    monkeypatch.setattr("agent_registry.v0_runner.load_capability_catalog", lambda *_args, **_kwargs: _catalog_payload())
    monkeypatch.setattr("agent_registry.v0_runner.is_llm_policy_enabled", lambda: True)
    monkeypatch.setattr("agent_registry.v0_runner._policy_route_available", lambda *_args, **_kwargs: True)

    def _run_task(*_args, **_kwargs):
        return TaskRunResult(
            status="ok",
            data={"items": []},
            error_type=None,
            attempts=1,
            profile="cheap",
            escalated=False,
        )

    monkeypatch.setattr("agent_registry.v0_runner.run_task_with_policy", _run_task)

    output = run(_agent_spec("llm_policy_task", "assist_entity_extraction"), {"text": "x"})

    assert output.status == STATUS_OK
