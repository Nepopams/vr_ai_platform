# Codex APPLY Prompt — ST-029: Unified Fallback Metrics Logging

## Role
You are a senior Python developer adding unified fallback metrics logging.

## Context (from PLAN findings)

- `process_command()` is at `graphs/core_graph.py:228-367` (post ST-028 with latency timing).
- Latency block: lines 347-365. Fallback block goes right after, before `return decision` at line 367.
- `is_llm_policy_enabled` currently imported at line 349 inside `if is_pipeline_latency_log_enabled():` — safe to move to function-level.
- `partial_trust_risk_log.py` has privacy comment: `# NO RAW USER OR LLM TEXT — PRIVACY GUARANTEE.`
- No naming conflicts for new files.
- No circular import risk.
- Test pattern: monkeypatch env vars + `tmp_path` (same as `test_pipeline_latency.py`).

## Files to Create/Modify

### 1. `app/logging/fallback_metrics_log.py` (NEW)

Create this file with EXACT content:

```python
"""Logging utilities for unified fallback and error rate metrics."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


DEFAULT_LOG_PATH = Path("logs/fallback_metrics.jsonl")


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def is_fallback_metrics_log_enabled() -> bool:
    return os.getenv("FALLBACK_METRICS_LOG_ENABLED", "true").lower() in {
        "1",
        "true",
        "yes",
    }


def resolve_log_path() -> Path:
    return Path(
        os.getenv("FALLBACK_METRICS_LOG_PATH", str(DEFAULT_LOG_PATH))
    )


def append_fallback_metrics_log(payload: Dict[str, Any]) -> Path:
    # NO RAW USER OR LLM TEXT — PRIVACY GUARANTEE.
    path = resolve_log_path()
    _ensure_parent(path)
    record = dict(payload)
    record.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{json.dumps(record, ensure_ascii=False)}\n")
    return path
```

### 2. `graphs/core_graph.py` (UPDATE)

Make these specific changes to `process_command()`:

**Change A: Add fallback_metrics imports (lines 231-234)**

Replace:
```python
    from app.logging.pipeline_latency_log import (
        append_pipeline_latency_log,
        is_pipeline_latency_log_enabled,
    )
```

With:
```python
    from app.logging.fallback_metrics_log import (
        append_fallback_metrics_log,
        is_fallback_metrics_log_enabled,
    )
    from app.logging.pipeline_latency_log import (
        append_pipeline_latency_log,
        is_pipeline_latency_log_enabled,
    )
    from llm_policy.config import is_llm_policy_enabled
```

**Change B: Replace the latency block + return (lines 347-367)**

Replace:
```python
    # Emit latency record
    if is_pipeline_latency_log_enabled():
        from llm_policy.config import is_llm_policy_enabled

        append_pipeline_latency_log(
            {
                "command_id": command.get("command_id"),
                "trace_id": decision.get("trace_id"),
                "total_ms": round(total_ms, 3),
                "steps": {
                    "validate_command_ms": round(validate_command_ms, 3),
                    "detect_intent_ms": round(detect_intent_ms, 3),
                    "registry_ms": round(registry_ms, 3),
                    "core_logic_ms": round(core_logic_ms, 3),
                    "validate_decision_ms": round(validate_decision_ms, 3),
                },
                "llm_enabled": is_llm_policy_enabled(),
            }
        )

    return decision
```

With:
```python
    llm_on = is_llm_policy_enabled()

    # Emit latency record
    if is_pipeline_latency_log_enabled():
        append_pipeline_latency_log(
            {
                "command_id": command.get("command_id"),
                "trace_id": decision.get("trace_id"),
                "total_ms": round(total_ms, 3),
                "steps": {
                    "validate_command_ms": round(validate_command_ms, 3),
                    "detect_intent_ms": round(detect_intent_ms, 3),
                    "registry_ms": round(registry_ms, 3),
                    "core_logic_ms": round(core_logic_ms, 3),
                    "validate_decision_ms": round(validate_decision_ms, 3),
                },
                "llm_enabled": llm_on,
            }
        )

    # Emit fallback metrics record
    if is_fallback_metrics_log_enabled():
        append_fallback_metrics_log(
            {
                "command_id": command.get("command_id"),
                "trace_id": decision.get("trace_id"),
                "intent": intent,
                "decision_action": decision.get("action"),
                "llm_outcome": "skipped" if not llm_on else "deterministic_only",
                "fallback_reason": "policy_disabled" if not llm_on else None,
                "deterministic_used": True,
                "llm_latency_ms": None,
                "components": {},
            }
        )

    return decision
```

**IMPORTANT:** The core logic block (Steps 1-5, lines 238-343) is NOT changed at all. Only the imports and the logging/return section change.

### 3. `tests/test_fallback_metrics.py` (NEW)

Create this file with EXACT content:

```python
"""Tests for unified fallback metrics logging (ST-029)."""

import json
import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.logging.fallback_metrics_log import append_fallback_metrics_log
from graphs.core_graph import process_command, sample_command


@pytest.fixture()
def _fallback_log_path(tmp_path, monkeypatch):
    """Redirect fallback metrics log to tmp_path and enable it."""
    log_file = tmp_path / "fallback_metrics.jsonl"
    monkeypatch.setenv("FALLBACK_METRICS_LOG_PATH", str(log_file))
    monkeypatch.setenv("FALLBACK_METRICS_LOG_ENABLED", "true")
    return log_file


def _run_and_read_fallback_log(_fallback_log_path):
    """Run process_command and return the last fallback record."""
    command = sample_command()
    process_command(command)
    text = _fallback_log_path.read_text(encoding="utf-8").strip()
    lines = text.split("\n")
    return json.loads(lines[-1])


def test_record_on_llm_success(tmp_path, monkeypatch) -> None:
    """AC-2: Log module records success outcome correctly."""
    log_file = tmp_path / "fallback_metrics.jsonl"
    monkeypatch.setenv("FALLBACK_METRICS_LOG_PATH", str(log_file))
    append_fallback_metrics_log(
        {
            "command_id": "cmd-test-001",
            "trace_id": "trace-test-001",
            "llm_outcome": "success",
            "fallback_reason": None,
            "deterministic_used": False,
            "llm_latency_ms": 120.5,
            "components": {"shadow": "ok", "assist": "ok"},
        }
    )
    record = json.loads(log_file.read_text(encoding="utf-8").strip())
    assert record["llm_outcome"] == "success"
    assert record["fallback_reason"] is None
    assert record["deterministic_used"] is False
    assert record["llm_latency_ms"] == 120.5
    assert "timestamp" in record


def test_record_on_llm_timeout(tmp_path, monkeypatch) -> None:
    """AC-3: Log module records fallback with timeout reason."""
    log_file = tmp_path / "fallback_metrics.jsonl"
    monkeypatch.setenv("FALLBACK_METRICS_LOG_PATH", str(log_file))
    append_fallback_metrics_log(
        {
            "command_id": "cmd-test-002",
            "trace_id": "trace-test-002",
            "llm_outcome": "fallback",
            "fallback_reason": "timeout",
            "deterministic_used": True,
            "llm_latency_ms": 5000.0,
            "components": {"shadow": "timeout"},
        }
    )
    record = json.loads(log_file.read_text(encoding="utf-8").strip())
    assert record["llm_outcome"] == "fallback"
    assert record["fallback_reason"] == "timeout"
    assert record["deterministic_used"] is True


def test_record_on_llm_unavailable(tmp_path, monkeypatch) -> None:
    """AC-3: Log module records error with unavailable reason."""
    log_file = tmp_path / "fallback_metrics.jsonl"
    monkeypatch.setenv("FALLBACK_METRICS_LOG_PATH", str(log_file))
    append_fallback_metrics_log(
        {
            "command_id": "cmd-test-003",
            "trace_id": "trace-test-003",
            "llm_outcome": "error",
            "fallback_reason": "llm_unavailable",
            "deterministic_used": True,
            "llm_latency_ms": None,
            "components": {"shadow": "error"},
        }
    )
    record = json.loads(log_file.read_text(encoding="utf-8").strip())
    assert record["llm_outcome"] == "error"
    assert record["fallback_reason"] == "llm_unavailable"


def test_record_skipped_when_disabled(_fallback_log_path, monkeypatch) -> None:
    """AC-4: llm_outcome=skipped when LLM disabled."""
    monkeypatch.setenv("LLM_POLICY_ENABLED", "false")
    record = _run_and_read_fallback_log(_fallback_log_path)
    assert record["llm_outcome"] == "skipped"
    assert record["fallback_reason"] == "policy_disabled"
    assert record["deterministic_used"] is True


def test_no_raw_text_in_record(_fallback_log_path) -> None:
    """AC-5: No raw user text or LLM output in records."""
    record = _run_and_read_fallback_log(_fallback_log_path)
    forbidden_keys = {"text", "prompt", "raw", "raw_output", "raw_text", "user_text"}
    found = forbidden_keys & set(record.keys())
    assert not found, f"Forbidden keys found in record: {found}"


def test_log_written_to_jsonl(_fallback_log_path) -> None:
    """AC-1: Log file has valid JSONL entries."""
    command = sample_command()
    process_command(command)
    process_command(command)
    text = _fallback_log_path.read_text(encoding="utf-8").strip()
    lines = text.split("\n")
    assert len(lines) == 2, f"Expected 2 lines, got {len(lines)}"
    for i, line in enumerate(lines):
        parsed = json.loads(line)
        assert "llm_outcome" in parsed, f"Line {i} missing llm_outcome"
        assert "timestamp" in parsed, f"Line {i} missing timestamp"
```

## Files NOT Modified (invariants)
- `contracts/schemas/command.schema.json` — DO NOT CHANGE
- `contracts/schemas/decision.schema.json` — DO NOT CHANGE
- `app/logging/shadow_router_log.py` — DO NOT CHANGE
- `app/logging/assist_log.py` — DO NOT CHANGE
- `app/logging/partial_trust_risk_log.py` — DO NOT CHANGE
- `app/logging/pipeline_latency_log.py` — DO NOT CHANGE
- `tests/test_pipeline_latency.py` — DO NOT CHANGE
- `tests/test_graph_execution.py` — DO NOT CHANGE
- `tests/test_core_graph_registry_gate.py` — DO NOT CHANGE

## Verification Commands

```bash
# New fallback metrics tests
source .venv/bin/activate && python3 -m pytest tests/test_fallback_metrics.py -v

# Latency tests still pass (both touch process_command)
source .venv/bin/activate && python3 -m pytest tests/test_pipeline_latency.py -v

# Core graph tests still pass
source .venv/bin/activate && python3 -m pytest tests/test_core_graph_registry_gate.py tests/test_graph_execution.py -v

# Full test suite
source .venv/bin/activate && python3 -m pytest --tb=short -q
```

## STOP-THE-LINE
If any of the following occur, STOP and report:
- Existing tests fail after your changes
- Decision output from `process_command()` changes
- Any file listed as "DO NOT CHANGE" needs modification
- Privacy violation: raw text appears in log records
