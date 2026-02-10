# Codex APPLY Prompt — ST-020: Core Pipeline Registry-Aware Gate

## Role
You are an implementation agent. Apply the changes described below exactly.

## Allowed files (whitelist)
- `agent_registry/config.py`
- `graphs/core_graph.py`
- `tests/test_core_graph_registry_gate.py` (NEW)

## Forbidden files
- `agent_registry/v0_models.py`, `agent_registry/v0_loader.py`, `agent_registry/capabilities_lookup.py`
- `agent_registry/*.yaml`
- `routers/**`, `contracts/**`, `.github/workflows/ci.yml`
- Any existing test files

## STOP-THE-LINE
If anything deviates from expectations or you need to modify files outside the whitelist, STOP and report.

---

## Context

Story ST-020 adds a flag-gated read-only registry annotation to `process_command()` in `graphs/core_graph.py`. When `AGENT_REGISTRY_CORE_ENABLED=true`, it queries `CapabilitiesLookup` for agents matching the detected intent, logs a snapshot, but does NOT change decision logic. Any error → silently caught.

### Key findings from PLAN
- `process_command()` at lines ~185-275, `intent = detect_intent(text)` right after `text = command.get("text", "").strip()`
- No existing `logging` import in core_graph.py
- No existing direct tests for core_graph.py (tested indirectly)
- No monkeypatch/mock patterns in existing tests — this will be the first
- `is_agent_registry_core_enabled()` does not yet exist in config.py
- 220 test functions currently

---

## Step 1: Add flag to `agent_registry/config.py`

**Current file:**

```python
from __future__ import annotations

import os


def is_agent_registry_enabled() -> bool:
    return os.getenv("AGENT_REGISTRY_ENABLED", "false").lower() in {"1", "true", "yes"}


def get_agent_registry_path() -> str | None:
    return os.getenv("AGENT_REGISTRY_PATH")
```

**Replace with:**

```python
from __future__ import annotations

import os


def is_agent_registry_enabled() -> bool:
    return os.getenv("AGENT_REGISTRY_ENABLED", "false").lower() in {"1", "true", "yes"}


def get_agent_registry_path() -> str | None:
    return os.getenv("AGENT_REGISTRY_PATH")


def is_agent_registry_core_enabled() -> bool:
    return os.getenv("AGENT_REGISTRY_CORE_ENABLED", "false").lower() in {"1", "true", "yes"}
```

---

## Step 2: Add annotation function and logging to `graphs/core_graph.py`

### 2a: Add logging import

After the existing imports (after `from jsonschema import validate`), add:

```python
import logging

_logger = logging.getLogger(__name__)
```

### 2b: Add `_annotate_registry_capabilities()` function

Insert this function **before** `process_command()` (i.e., after `build_start_job_decision()` and before `process_command()`):

```python
def _annotate_registry_capabilities(intent: str) -> Dict[str, Any]:
    """Read-only probe: query registry for agents matching intent.

    Returns a registry_snapshot dict for logging. Never raises.
    """
    try:
        from agent_registry.config import is_agent_registry_core_enabled

        if not is_agent_registry_core_enabled():
            return {}

        from agent_registry.v0_loader import AgentRegistryV0Loader, load_capability_catalog
        from agent_registry.capabilities_lookup import CapabilitiesLookup

        registry = AgentRegistryV0Loader.load()
        catalog = load_capability_catalog()
        lookup = CapabilitiesLookup(registry, catalog)

        agents_shadow = lookup.find_agents(intent, "shadow")
        agents_assist = lookup.find_agents(intent, "assist")
        all_agents = agents_shadow + agents_assist

        snapshot: Dict[str, Any] = {
            "intent": intent,
            "available_agents": [
                {"agent_id": a.agent_id, "mode": a.mode}
                for a in all_agents
            ],
            "any_enabled": len(all_agents) > 0,
        }

        _logger.info("registry_snapshot: %s", snapshot)
        return snapshot

    except Exception as exc:
        _logger.warning("registry annotation failed: %s", exc)
        return {"intent": intent, "error": str(exc), "any_enabled": False}
```

### 2c: Call annotation from `process_command()`

In `process_command()`, right after the line:
```python
    intent = detect_intent(text)
```

Add this single line:
```python
    registry_snapshot = _annotate_registry_capabilities(intent)
```

The `registry_snapshot` variable is not used further — the annotation is logged inside the function. This is intentional (read-only probe).

---

## Step 3: Create `tests/test_core_graph_registry_gate.py`

**Create new file** with exact content:

```python
from unittest.mock import patch, MagicMock

from graphs.core_graph import _annotate_registry_capabilities, process_command, sample_command


def test_gate_disabled_by_default(monkeypatch):
    monkeypatch.delenv("AGENT_REGISTRY_CORE_ENABLED", raising=False)
    result = _annotate_registry_capabilities("add_shopping_item")
    assert result == {}


def test_gate_enabled_returns_snapshot(monkeypatch):
    monkeypatch.setenv("AGENT_REGISTRY_CORE_ENABLED", "true")

    mock_agent = MagicMock()
    mock_agent.agent_id = "test-agent"
    mock_agent.mode = "shadow"
    mock_agent.enabled = True

    mock_registry = MagicMock()
    mock_catalog = {}

    mock_lookup = MagicMock()
    mock_lookup.find_agents.side_effect = lambda intent, mode: (
        [mock_agent] if mode == "shadow" else []
    )

    with patch("agent_registry.v0_loader.AgentRegistryV0Loader.load", return_value=mock_registry), \
         patch("agent_registry.v0_loader.load_capability_catalog", return_value=mock_catalog), \
         patch("agent_registry.capabilities_lookup.CapabilitiesLookup", return_value=mock_lookup):
        result = _annotate_registry_capabilities("add_shopping_item")

    assert result["intent"] == "add_shopping_item"
    assert result["any_enabled"] is True
    assert len(result["available_agents"]) == 1
    assert result["available_agents"][0]["agent_id"] == "test-agent"
    assert result["available_agents"][0]["mode"] == "shadow"


def test_decision_unchanged_with_flag_off(monkeypatch):
    monkeypatch.delenv("AGENT_REGISTRY_CORE_ENABLED", raising=False)
    command = sample_command()
    decision = process_command(command)
    assert decision["action"] == "start_job"
    assert decision["status"] == "ok"
    assert "payload" in decision


def test_decision_unchanged_with_flag_on(monkeypatch):
    monkeypatch.setenv("AGENT_REGISTRY_CORE_ENABLED", "true")

    mock_lookup = MagicMock()
    mock_lookup.find_agents.return_value = []

    with patch("agent_registry.v0_loader.AgentRegistryV0Loader.load", return_value=MagicMock()), \
         patch("agent_registry.v0_loader.load_capability_catalog", return_value={}), \
         patch("agent_registry.capabilities_lookup.CapabilitiesLookup", return_value=mock_lookup):
        command = sample_command()
        decision = process_command(command)

    assert decision["action"] == "start_job"
    assert decision["status"] == "ok"
    assert "payload" in decision


def test_registry_load_failure_graceful(monkeypatch):
    monkeypatch.setenv("AGENT_REGISTRY_CORE_ENABLED", "true")

    with patch("agent_registry.v0_loader.AgentRegistryV0Loader.load", side_effect=ValueError("broken")):
        result = _annotate_registry_capabilities("add_shopping_item")

    assert result["intent"] == "add_shopping_item"
    assert "error" in result
    assert result["any_enabled"] is False

    # Also verify pipeline still works
    with patch("agent_registry.v0_loader.AgentRegistryV0Loader.load", side_effect=ValueError("broken")):
        command = sample_command()
        decision = process_command(command)
    assert decision["action"] == "start_job"


def test_annotation_returns_agent_ids(monkeypatch):
    monkeypatch.setenv("AGENT_REGISTRY_CORE_ENABLED", "true")

    agent1 = MagicMock()
    agent1.agent_id = "agent-shadow"
    agent1.mode = "shadow"
    agent2 = MagicMock()
    agent2.agent_id = "agent-assist"
    agent2.mode = "assist"

    mock_lookup = MagicMock()
    mock_lookup.find_agents.side_effect = lambda intent, mode: (
        [agent1] if mode == "shadow" else [agent2] if mode == "assist" else []
    )

    with patch("agent_registry.v0_loader.AgentRegistryV0Loader.load", return_value=MagicMock()), \
         patch("agent_registry.v0_loader.load_capability_catalog", return_value={}), \
         patch("agent_registry.capabilities_lookup.CapabilitiesLookup", return_value=mock_lookup):
        result = _annotate_registry_capabilities("add_shopping_item")

    assert len(result["available_agents"]) == 2
    ids = {a["agent_id"] for a in result["available_agents"]}
    assert ids == {"agent-shadow", "agent-assist"}


def test_no_raw_text_in_snapshot(monkeypatch):
    monkeypatch.setenv("AGENT_REGISTRY_CORE_ENABLED", "true")

    mock_lookup = MagicMock()
    mock_lookup.find_agents.return_value = []

    with patch("agent_registry.v0_loader.AgentRegistryV0Loader.load", return_value=MagicMock()), \
         patch("agent_registry.v0_loader.load_capability_catalog", return_value={}), \
         patch("agent_registry.capabilities_lookup.CapabilitiesLookup", return_value=mock_lookup):
        result = _annotate_registry_capabilities("add_shopping_item")

    assert "text" not in result
    assert "user_id" not in result
    assert "command" not in result
    assert result.get("intent") == "add_shopping_item"


def test_gate_empty_registry_returns_none_enabled(monkeypatch):
    monkeypatch.setenv("AGENT_REGISTRY_CORE_ENABLED", "true")

    mock_lookup = MagicMock()
    mock_lookup.find_agents.return_value = []

    with patch("agent_registry.v0_loader.AgentRegistryV0Loader.load", return_value=MagicMock()), \
         patch("agent_registry.v0_loader.load_capability_catalog", return_value={}), \
         patch("agent_registry.capabilities_lookup.CapabilitiesLookup", return_value=mock_lookup):
        result = _annotate_registry_capabilities("add_shopping_item")

    assert result["any_enabled"] is False
    assert result["available_agents"] == []
```

---

## Verification

After applying all changes, run:

```bash
# Full test suite (expect 228 passed)
python3 -m pytest tests/ -v --tb=short

# Just registry gate tests (expect 8 tests)
python3 -m pytest tests/test_core_graph_registry_gate.py -v --tb=short

# Import check
python3 -c "from graphs.core_graph import _annotate_registry_capabilities; print('OK')"

# Flag default check
python3 -c "from agent_registry.config import is_agent_registry_core_enabled; print(is_agent_registry_core_enabled())"
# expect: False
```
