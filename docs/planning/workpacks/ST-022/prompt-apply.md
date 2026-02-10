# Codex APPLY Prompt — ST-022: LLM Caller Startup Registration

## Role
You are a senior Python developer creating the LLM caller bootstrap module.

## Context (from PLAN findings)

- `set_llm_caller(caller: LlmCaller | None) -> None` at `llm_policy/runtime.py:24`.
- `get_llm_caller() -> LlmCaller | None` at `llm_policy/runtime.py:29`.
- `create_http_caller(*, api_key: str | None = None) -> HttpLlmCaller` at `llm_policy/http_caller.py:17`. Raises `ValueError` if no key.
- `is_llm_policy_enabled()` reads `LLM_POLICY_ENABLED`, default `"false"`.
- `get_llm_policy_allow_placeholders()` reads `LLM_POLICY_ALLOW_PLACEHOLDERS`, default `"false"`.
- Logger convention: `logging.getLogger("llm_policy")`.
- `tests/test_llm_policy_tasks.py` uses `set_llm_caller(StubCaller(...))` then resets to `None` — new tests must also reset.
- No naming conflicts for new files.

## Files to Create

### 1. `llm_policy/bootstrap.py` (NEW)

Create this file with EXACT content:

```python
"""LLM caller bootstrap — wire HTTP caller into runtime at startup."""

from __future__ import annotations

import logging
import os

_LOGGER = logging.getLogger("llm_policy")


def bootstrap_llm_caller() -> None:
    """Create and register the HTTP LLM caller if env vars are configured.

    Guard order:
    1. LLM_POLICY_ENABLED must be true
    2. LLM_POLICY_ALLOW_PLACEHOLDERS must be false
    3. LLM_API_KEY must be set
    """
    from llm_policy.config import (
        get_llm_policy_allow_placeholders,
        is_llm_policy_enabled,
    )

    if not is_llm_policy_enabled():
        _LOGGER.info("LLM policy disabled, skipping bootstrap")
        return

    if get_llm_policy_allow_placeholders():
        _LOGGER.error(
            "Cannot register real LLM caller with placeholders enabled. "
            "Set LLM_POLICY_ALLOW_PLACEHOLDERS=false to use a real caller."
        )
        return

    api_key = os.getenv("LLM_API_KEY", "")
    if not api_key:
        _LOGGER.warning("LLM_API_KEY not set, LLM caller not registered")
        return

    from llm_policy.http_caller import create_http_caller
    from llm_policy.runtime import set_llm_caller

    caller = create_http_caller(api_key=api_key)
    set_llm_caller(caller)
    _LOGGER.info("LLM caller registered successfully")
```

### 2. `tests/test_llm_bootstrap.py` (NEW)

Create this file with EXACT content:

```python
"""Tests for LLM caller bootstrap (ST-022)."""

import logging
import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from llm_policy.bootstrap import bootstrap_llm_caller
from llm_policy.runtime import get_llm_caller, set_llm_caller


@pytest.fixture(autouse=True)
def _reset_caller():
    """Reset global caller state before and after each test."""
    set_llm_caller(None)
    yield
    set_llm_caller(None)


def test_bootstrap_registers_caller_with_all_vars(monkeypatch) -> None:
    """AC-1: Caller registered when all env vars present."""
    monkeypatch.setenv("LLM_POLICY_ENABLED", "true")
    monkeypatch.setenv("LLM_POLICY_ALLOW_PLACEHOLDERS", "false")
    monkeypatch.setenv("LLM_API_KEY", "test-key-abc123")
    bootstrap_llm_caller()
    caller = get_llm_caller()
    assert caller is not None, "Caller should be registered"
    assert callable(caller), "Caller should be callable"


def test_bootstrap_skips_without_api_key(monkeypatch) -> None:
    """AC-2: Caller not registered when API key missing."""
    monkeypatch.setenv("LLM_POLICY_ENABLED", "true")
    monkeypatch.setenv("LLM_POLICY_ALLOW_PLACEHOLDERS", "false")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    bootstrap_llm_caller()
    assert get_llm_caller() is None, "Caller should not be registered without API key"


def test_bootstrap_skips_when_disabled(monkeypatch) -> None:
    """AC-2: Caller not registered when LLM policy disabled."""
    monkeypatch.setenv("LLM_POLICY_ENABLED", "false")
    monkeypatch.setenv("LLM_API_KEY", "test-key-abc123")
    bootstrap_llm_caller()
    assert get_llm_caller() is None, "Caller should not be registered when disabled"


def test_bootstrap_rejects_placeholder_mode(monkeypatch) -> None:
    """AC-3: Caller not registered when placeholders enabled."""
    monkeypatch.setenv("LLM_POLICY_ENABLED", "true")
    monkeypatch.setenv("LLM_POLICY_ALLOW_PLACEHOLDERS", "true")
    monkeypatch.setenv("LLM_API_KEY", "test-key-abc123")
    bootstrap_llm_caller()
    assert get_llm_caller() is None, "Caller should not be registered with placeholders"


def test_bootstrap_logs_warning_on_missing_vars(monkeypatch, caplog) -> None:
    """AC-2: Warning logged when API key missing."""
    monkeypatch.setenv("LLM_POLICY_ENABLED", "true")
    monkeypatch.setenv("LLM_POLICY_ALLOW_PLACEHOLDERS", "false")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    with caplog.at_level(logging.WARNING, logger="llm_policy"):
        bootstrap_llm_caller()
    assert any(
        "LLM_API_KEY not set" in record.message for record in caplog.records
    ), "Expected warning about missing LLM_API_KEY"
```

## Files NOT Modified (invariants)
- `llm_policy/runtime.py` — DO NOT CHANGE
- `llm_policy/http_caller.py` — DO NOT CHANGE
- `llm_policy/config.py` — DO NOT CHANGE
- `llm_policy/models.py` — DO NOT CHANGE
- `graphs/core_graph.py` — DO NOT CHANGE
- `tests/test_llm_policy_tasks.py` — DO NOT CHANGE
- `tests/test_http_llm_client.py` — DO NOT CHANGE

## Verification Commands

```bash
# New bootstrap tests
source .venv/bin/activate && python3 -m pytest tests/test_llm_bootstrap.py -v

# HTTP caller tests still pass
source .venv/bin/activate && python3 -m pytest tests/test_http_llm_client.py -v

# LLM policy tasks tests still pass (also uses set_llm_caller)
source .venv/bin/activate && python3 -m pytest tests/test_llm_policy_tasks.py -v

# Full test suite
source .venv/bin/activate && python3 -m pytest --tb=short -q
```

## STOP-THE-LINE
If any of the following occur, STOP and report:
- Existing tests fail after your changes
- Any file listed as "DO NOT CHANGE" needs modification
- Global caller state leaks between tests
