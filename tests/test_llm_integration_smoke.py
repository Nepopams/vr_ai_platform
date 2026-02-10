"""Integration smoke tests for real LLM round-trip through shadow router (ST-024)."""

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import routers.shadow_router as shadow_router
from graphs.core_graph import process_command
from llm_policy.bootstrap import bootstrap_llm_caller
from llm_policy.runtime import get_llm_caller, set_llm_caller


# ---------------------------------------------------------------------------
# Skip condition for real-LLM tests
# ---------------------------------------------------------------------------

_LLM_API_KEY = os.getenv("LLM_API_KEY", "")
_LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")
_LLM_MODEL = os.getenv("LLM_MODEL", "")
HAS_LLM_CREDENTIALS = bool(_LLM_API_KEY and _LLM_BASE_URL and _LLM_MODEL)

requires_llm = pytest.mark.skipif(
    not HAS_LLM_CREDENTIALS,
    reason="LLM_API_KEY, LLM_BASE_URL, and LLM_MODEL required",
)


# ---------------------------------------------------------------------------
# Test YAML policy template (no ${...} placeholders)
# ---------------------------------------------------------------------------

_POLICY_TEMPLATE = """\
schema_version: 1
compat:
  adr: "ADR-003"
  note: "smoke-test"
profiles:
  cheap:
    description: "test profile"
  reliable:
    description: "test reliable"
tasks:
  shopping_extraction:
    description: "test task"
routing:
  shopping_extraction:
    cheap:
      provider: "openai_compatible"
      model: "{model}"
      temperature: 0.2
      max_tokens: 256
      timeout_ms: 5000
    reliable:
      provider: "openai_compatible"
      model: "{model}"
      temperature: 0.2
      max_tokens: 256
      timeout_ms: 10000
fallback_chain: []
"""


# ---------------------------------------------------------------------------
# Fixtures & helpers
# ---------------------------------------------------------------------------

FIXTURES_DIR = BASE_DIR / "skills" / "graph-sanity" / "fixtures" / "commands"


@pytest.fixture(autouse=True)
def _reset_caller():
    """Reset global caller state before and after each test."""
    set_llm_caller(None)
    yield
    set_llm_caller(None)


def _write_test_policy(tmp_path: Path, model: str = "test-model") -> Path:
    """Write placeholder-free test policy YAML to tmp_path."""
    policy_path = tmp_path / "test-policy.yaml"
    content = _POLICY_TEMPLATE.format(model=model)
    policy_path.write_text(content, encoding="utf-8")
    return policy_path


def _make_command(text: str = "Купи молоко") -> dict:
    """Create a minimal valid command for process_command()."""
    return {
        "command_id": "cmd-smoke-001",
        "user_id": "user-smoke",
        "timestamp": "2026-02-01T10:00:00+00:00",
        "text": text,
        "capabilities": [
            "start_job",
            "propose_create_task",
            "propose_add_shopping_item",
            "clarify",
        ],
        "context": {
            "household": {
                "household_id": "house-smoke",
                "members": [{"user_id": "user-smoke", "display_name": "Test"}],
                "shopping_lists": [{"list_id": "list-1", "name": "Продукты"}],
            },
            "defaults": {"default_list_id": "list-1"},
        },
    }


def _read_log(path: Path) -> dict:
    """Read the last JSONL record from a log file."""
    content = path.read_text(encoding="utf-8").strip().splitlines()
    return json.loads(content[-1])


def _read_all_logs(path: Path) -> list:
    """Read all JSONL records from a log file."""
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def _load_fixture(name: str) -> dict:
    """Load a command fixture from the golden dataset fixtures directory."""
    return json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8"))


def _setup_shadow_sync(monkeypatch):
    """Replace shadow router thread pool with synchronous execution."""
    monkeypatch.setattr(
        shadow_router,
        "_submit_shadow_task",
        lambda payload: shadow_router._run_shadow_router(payload),
    )


# ---------------------------------------------------------------------------
# Always-run tests
# ---------------------------------------------------------------------------


def test_fallback_on_invalid_credentials(monkeypatch, tmp_path) -> None:
    """AC-2: Invalid credentials -> error logged, deterministic pipeline unaffected."""
    log_path = tmp_path / "shadow.jsonl"
    policy_path = _write_test_policy(tmp_path)

    monkeypatch.setenv("LLM_POLICY_ENABLED", "true")
    monkeypatch.setenv("LLM_POLICY_ALLOW_PLACEHOLDERS", "false")
    monkeypatch.setenv("LLM_API_KEY", "invalid-key-for-testing")
    monkeypatch.setenv("LLM_BASE_URL", "http://localhost:1")
    monkeypatch.setenv("LLM_POLICY_PATH", str(policy_path))
    monkeypatch.setenv("SHADOW_ROUTER_ENABLED", "true")
    monkeypatch.setenv("SHADOW_ROUTER_LOG_PATH", str(log_path))

    # Bootstrap registers caller (all 3 guards pass with custom YAML)
    bootstrap_llm_caller()
    assert get_llm_caller() is not None

    # Shadow router: run synchronously, expect error (connection refused)
    _setup_shadow_sync(monkeypatch)
    command = _make_command("Купи молоко")
    normalized = {"text": "Купи молоко", "intent": "add_shopping_item", "capabilities": []}
    shadow_router.start_shadow_router(command, normalized)

    # Shadow router logged an error
    assert log_path.exists(), "Shadow router log should be written"
    logged = _read_log(log_path)
    assert logged["status"] == "error"

    # Deterministic pipeline produces valid decision regardless of LLM state
    decision = process_command(command)
    assert decision["action"] in ("start_job", "clarify")
    assert "decision_id" in decision


def test_killswitch_prevents_llm_calls(monkeypatch, tmp_path) -> None:
    """AC-3: LLM_POLICY_ENABLED=false -> no HTTP call, shadow router skips."""
    log_path = tmp_path / "shadow.jsonl"

    monkeypatch.setenv("LLM_POLICY_ENABLED", "false")
    monkeypatch.setenv("SHADOW_ROUTER_ENABLED", "true")
    monkeypatch.setenv("SHADOW_ROUTER_LOG_PATH", str(log_path))

    with patch("llm_policy.http_caller.httpx.Client") as mock_client:
        _setup_shadow_sync(monkeypatch)
        command = _make_command("Купи молоко")
        normalized = {"text": "Купи молоко", "intent": "add_shopping_item", "capabilities": []}
        shadow_router.start_shadow_router(command, normalized)

        # httpx.Client never instantiated
        mock_client.assert_not_called()

    # Shadow router logged skip with policy_disabled
    assert log_path.exists()
    logged = _read_log(log_path)
    assert logged["status"] == "skipped"
    assert logged["error_type"] == "policy_disabled"

    # Deterministic pipeline still works
    decision = process_command(command)
    assert decision["action"] == "start_job"


# ---------------------------------------------------------------------------
# Conditional tests (require real LLM credentials)
# ---------------------------------------------------------------------------


@requires_llm
def test_real_llm_shadow_router_roundtrip(monkeypatch, tmp_path) -> None:
    """AC-1: Full round-trip through shadow router with real LLM."""
    log_path = tmp_path / "shadow.jsonl"
    policy_path = _write_test_policy(tmp_path, model=_LLM_MODEL)

    monkeypatch.setenv("LLM_POLICY_ENABLED", "true")
    monkeypatch.setenv("LLM_POLICY_ALLOW_PLACEHOLDERS", "false")
    monkeypatch.setenv("LLM_POLICY_PATH", str(policy_path))
    monkeypatch.setenv("SHADOW_ROUTER_ENABLED", "true")
    monkeypatch.setenv("SHADOW_ROUTER_LOG_PATH", str(log_path))

    bootstrap_llm_caller()
    assert get_llm_caller() is not None

    _setup_shadow_sync(monkeypatch)
    command = _make_command("Купи молоко")
    normalized = {"text": "Купи молоко", "intent": "add_shopping_item", "capabilities": []}
    shadow_router.start_shadow_router(command, normalized)

    assert log_path.exists(), "Shadow router log should be written"
    logged = _read_log(log_path)
    assert logged["status"] != "skipped", f"Expected real LLM call, got: {logged}"


@requires_llm
def test_golden_commands_with_real_llm(monkeypatch, tmp_path) -> None:
    """AC-1: Three golden commands produce shadow router log entries."""
    log_path = tmp_path / "shadow.jsonl"
    policy_path = _write_test_policy(tmp_path, model=_LLM_MODEL)

    monkeypatch.setenv("LLM_POLICY_ENABLED", "true")
    monkeypatch.setenv("LLM_POLICY_ALLOW_PLACEHOLDERS", "false")
    monkeypatch.setenv("LLM_POLICY_PATH", str(policy_path))
    monkeypatch.setenv("SHADOW_ROUTER_ENABLED", "true")
    monkeypatch.setenv("SHADOW_ROUTER_LOG_PATH", str(log_path))

    bootstrap_llm_caller()
    _setup_shadow_sync(monkeypatch)

    fixtures = ["buy_milk.json", "clean_bathroom.json", "unknown_intent.json"]
    for fixture_name in fixtures:
        command = _load_fixture(fixture_name)
        normalized = {"text": command["text"], "intent": "unknown", "capabilities": []}
        shadow_router.start_shadow_router(command, normalized)

    assert log_path.exists()
    logs = _read_all_logs(log_path)
    assert len(logs) == 3, f"Expected 3 log entries, got {len(logs)}"


@requires_llm
def test_shadow_log_written_on_success(monkeypatch, tmp_path) -> None:
    """AC-1: Shadow router JSONL log contains all required keys."""
    log_path = tmp_path / "shadow.jsonl"
    policy_path = _write_test_policy(tmp_path, model=_LLM_MODEL)

    monkeypatch.setenv("LLM_POLICY_ENABLED", "true")
    monkeypatch.setenv("LLM_POLICY_ALLOW_PLACEHOLDERS", "false")
    monkeypatch.setenv("LLM_POLICY_PATH", str(policy_path))
    monkeypatch.setenv("SHADOW_ROUTER_ENABLED", "true")
    monkeypatch.setenv("SHADOW_ROUTER_LOG_PATH", str(log_path))

    bootstrap_llm_caller()
    _setup_shadow_sync(monkeypatch)

    command = _make_command("Купи молоко")
    normalized = {"text": "Купи молоко", "intent": "add_shopping_item", "capabilities": []}
    shadow_router.start_shadow_router(command, normalized)

    assert log_path.exists()
    logged = _read_log(log_path)
    required_keys = {
        "timestamp",
        "trace_id",
        "command_id",
        "router_version",
        "router_strategy",
        "status",
        "latency_ms",
        "error_type",
        "suggested_intent",
        "missing_fields",
        "clarify_question",
        "entities_summary",
        "confidence",
        "model_meta",
        "baseline_intent",
        "baseline_action",
        "baseline_job_type",
    }
    assert required_keys.issubset(logged.keys()), f"Missing keys: {required_keys - logged.keys()}"
