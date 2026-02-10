# Codex APPLY Prompt — ST-028: Pipeline-Wide Latency Instrumentation

## Role
You are a senior Python developer adding pipeline-wide latency instrumentation.

## Context (from PLAN findings)

- `process_command()` is at `graphs/core_graph.py:227-318`.
- 5 timed steps: validate_command, detect_intent, registry, core_logic, validate_decision.
- No existing timing/latency logic.
- Logging pattern: `app/logging/shadow_router_log.py` — `DEFAULT_LOG_PATH`, `_ensure_parent`, `resolve_log_path`, `append_*_log`.
- `app/logging/__init__.py` is minimal (docstring only), no barrel exports.
- `is_llm_policy_enabled()` at `llm_policy/config.py:6`, import: `from llm_policy.config import is_llm_policy_enabled`.
- No circular import risk: `app/logging/` does not import from `graphs/`.
- Existing tests (`test_graph_execution.py`, `test_core_graph_registry_gate.py`) won't break — timing is transparent.
- No naming conflicts for new files.

## Files to Create/Modify

### 1. `app/logging/pipeline_latency_log.py` (NEW)

Create this file with EXACT content:

```python
"""Logging utilities for pipeline-wide latency instrumentation."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


DEFAULT_LOG_PATH = Path("logs/pipeline_latency.jsonl")


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def is_pipeline_latency_log_enabled() -> bool:
    return os.getenv("PIPELINE_LATENCY_LOG_ENABLED", "true").lower() in {
        "1",
        "true",
        "yes",
    }


def resolve_log_path() -> Path:
    return Path(
        os.getenv("PIPELINE_LATENCY_LOG_PATH", str(DEFAULT_LOG_PATH))
    )


def append_pipeline_latency_log(payload: Dict[str, Any]) -> Path:
    path = resolve_log_path()
    _ensure_parent(path)
    record = dict(payload)
    record.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{json.dumps(record, ensure_ascii=False)}\n")
    return path
```

### 2. `graphs/core_graph.py` (UPDATE)

Add `import time` to the top-level imports (after `from uuid import uuid4`, before `from jsonschema import validate`).

**Replace the ENTIRE `process_command` function** (lines 227-318) with:

```python
def process_command(command: Dict[str, Any]) -> Dict[str, Any]:
    import time

    from app.logging.pipeline_latency_log import (
        append_pipeline_latency_log,
        is_pipeline_latency_log_enabled,
    )

    t_start = time.monotonic()

    # Step 1: validate command
    t0 = time.monotonic()
    command_schema = load_schema(COMMAND_SCHEMA_PATH)
    validate(instance=command, schema=command_schema)
    validate_command_ms = (time.monotonic() - t0) * 1000

    # Step 2: detect intent
    t0 = time.monotonic()
    text = command.get("text", "").strip()
    intent = detect_intent(text)
    detect_intent_ms = (time.monotonic() - t0) * 1000

    # Step 3: registry annotation
    t0 = time.monotonic()
    registry_snapshot = _annotate_registry_capabilities(intent)
    registry_ms = (time.monotonic() - t0) * 1000

    # Step 4: core logic
    t0 = time.monotonic()
    capabilities = set(command.get("capabilities", []))

    if "start_job" not in capabilities:
        decision = build_clarify_decision(
            command,
            question="Какие действия разрешены для выполнения?",
            explanation="Отсутствует capability start_job.",
        )
    elif not text:
        decision = build_clarify_decision(
            command,
            question="Опишите, что нужно сделать: задача или покупка?",
            missing_fields=["text"],
            explanation="Текст команды пустой.",
        )
    elif intent == "add_shopping_item":
        item_name = extract_item_name(text)
        if not item_name:
            decision = build_clarify_decision(
                command,
                question="Какой товар добавить в список покупок?",
                missing_fields=["item.name"],
                explanation="Не удалось извлечь название товара.",
            )
        else:
            proposed_actions: List[Dict[str, Any]] = []
            if "propose_add_shopping_item" in capabilities:
                list_id = _default_list_id(command)
                item_payload = {"name": item_name}
                if list_id:
                    item_payload["list_id"] = list_id
                proposed_actions.append(
                    build_proposed_action(
                        "propose_add_shopping_item",
                        {
                            "item": item_payload
                        },
                    )
                )
            decision = build_start_job_decision(
                command,
                job_type="add_shopping_item",
                proposed_actions=proposed_actions or None,
                explanation="Распознан запрос на добавление покупки.",
            )
    elif intent == "create_task":
        title = text.strip()
        if not title:
            decision = build_clarify_decision(
                command,
                question="Какую задачу нужно создать?",
                missing_fields=["task.title"],
                explanation="Не удалось получить описание задачи.",
            )
        else:
            proposed_actions = []
            if "propose_create_task" in capabilities:
                proposed_actions.append(
                    build_proposed_action(
                        "propose_create_task",
                        {
                            "task": {
                                "title": title,
                                "assignee_id": _default_assignee_id(command),
                            }
                        },
                    )
                )
            decision = build_start_job_decision(
                command,
                job_type="create_task",
                proposed_actions=proposed_actions or None,
                explanation="Распознан запрос на создание задачи.",
            )
    else:
        decision = build_clarify_decision(
            command,
            question="Уточните, что нужно сделать: задача или покупка?",
            explanation="Интент не распознан.",
        )
    core_logic_ms = (time.monotonic() - t0) * 1000

    # Step 5: validate decision
    t0 = time.monotonic()
    decision_schema = load_schema(DECISION_SCHEMA_PATH)
    validate(instance=decision, schema=decision_schema)
    validate_decision_ms = (time.monotonic() - t0) * 1000

    total_ms = (time.monotonic() - t_start) * 1000

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

**IMPORTANT:** The core logic block (the entire if/elif/else) is copied EXACTLY from the original. Do NOT change any logic, variable names, or indentation within it.

### 3. `tests/test_pipeline_latency.py` (NEW)

Create this file with EXACT content:

```python
"""Tests for pipeline-wide latency instrumentation (ST-028)."""

import json
import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from graphs.core_graph import process_command, sample_command


@pytest.fixture()
def _latency_log_path(tmp_path, monkeypatch):
    """Redirect latency log to tmp_path and enable it."""
    log_file = tmp_path / "pipeline_latency.jsonl"
    monkeypatch.setenv("PIPELINE_LATENCY_LOG_PATH", str(log_file))
    monkeypatch.setenv("PIPELINE_LATENCY_LOG_ENABLED", "true")
    return log_file


def _run_and_read_log(_latency_log_path):
    """Run process_command and return the last latency record."""
    command = sample_command()
    process_command(command)
    text = _latency_log_path.read_text(encoding="utf-8").strip()
    lines = text.split("\n")
    return json.loads(lines[-1])


def test_latency_record_structure(_latency_log_path) -> None:
    """AC-1: Latency record has required keys."""
    record = _run_and_read_log(_latency_log_path)
    assert "command_id" in record
    assert "trace_id" in record
    assert "total_ms" in record
    assert "steps" in record
    assert "llm_enabled" in record
    assert "timestamp" in record
    steps = record["steps"]
    expected_steps = {
        "validate_command_ms",
        "detect_intent_ms",
        "registry_ms",
        "core_logic_ms",
        "validate_decision_ms",
    }
    assert set(steps.keys()) == expected_steps


def test_step_breakdown_non_negative(_latency_log_path) -> None:
    """AC-2: All step values are non-negative."""
    record = _run_and_read_log(_latency_log_path)
    for step_name, value in record["steps"].items():
        assert value >= 0, f"Step '{step_name}' has negative value: {value}"


def test_total_ms_gte_step_sum(_latency_log_path) -> None:
    """AC-2: total_ms >= sum of step values."""
    record = _run_and_read_log(_latency_log_path)
    step_sum = sum(record["steps"].values())
    assert record["total_ms"] >= step_sum - 0.1, (
        f"total_ms={record['total_ms']} < step_sum={step_sum}"
    )


def test_disabled_no_log(tmp_path, monkeypatch) -> None:
    """AC-3: No log when disabled."""
    log_file = tmp_path / "pipeline_latency.jsonl"
    monkeypatch.setenv("PIPELINE_LATENCY_LOG_PATH", str(log_file))
    monkeypatch.setenv("PIPELINE_LATENCY_LOG_ENABLED", "false")
    command = sample_command()
    process_command(command)
    assert not log_file.exists(), "Log file should not exist when disabled"


def test_llm_enabled_flag(_latency_log_path, monkeypatch) -> None:
    """AC-4: llm_enabled reflects LLM_POLICY_ENABLED."""
    monkeypatch.setenv("LLM_POLICY_ENABLED", "true")
    record = _run_and_read_log(_latency_log_path)
    assert record["llm_enabled"] is True


def test_log_written_to_jsonl(_latency_log_path) -> None:
    """AC-1: Log file exists and each line is valid JSON."""
    command = sample_command()
    process_command(command)
    process_command(command)
    text = _latency_log_path.read_text(encoding="utf-8").strip()
    lines = text.split("\n")
    assert len(lines) == 2, f"Expected 2 lines, got {len(lines)}"
    for i, line in enumerate(lines):
        parsed = json.loads(line)
        assert "total_ms" in parsed, f"Line {i} missing total_ms"
```

## Files NOT Modified (invariants)
- `contracts/schemas/command.schema.json` — DO NOT CHANGE
- `contracts/schemas/decision.schema.json` — DO NOT CHANGE
- `app/logging/shadow_router_log.py` — DO NOT CHANGE
- `app/logging/assist_log.py` — DO NOT CHANGE
- `tests/test_graph_execution.py` — DO NOT CHANGE
- `tests/test_core_graph_registry_gate.py` — DO NOT CHANGE

## Verification Commands

```bash
# New latency tests
source .venv/bin/activate && python3 -m pytest tests/test_pipeline_latency.py -v

# Core graph tests (must still pass)
source .venv/bin/activate && python3 -m pytest tests/test_core_graph_registry_gate.py tests/test_graph_execution.py -v

# Full test suite
source .venv/bin/activate && python3 -m pytest --tb=short -q
```

## STOP-THE-LINE
If any of the following occur, STOP and report:
- Existing tests fail after your changes
- Decision output from `process_command()` changes
- Any file listed as "DO NOT CHANGE" needs modification
