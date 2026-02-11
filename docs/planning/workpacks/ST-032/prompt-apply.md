# Codex APPLY Prompt — ST-032: Pydantic Models for CommandDTO and DecisionDTO

## Role

You are a senior Python/FastAPI developer implementing Pydantic request/response models for the AI Platform API boundary.

## Rules

- Create/modify ONLY the files listed below. Do NOT touch any other files.
- Use Pydantic **v2** API: `model_dump()`, `model_validate()`, `ConfigDict(extra="forbid")`. Do NOT use v1 API (`dict()`, `parse_obj()`, `class Config`).
- Do NOT modify internal pipeline files (`app/services/`, `routers/`, `graphs/`).
- If anything contradicts the plan → **STOP and report** (STOP-THE-LINE).

## PLAN Findings Summary

- **Pydantic 2.12.5** available (transitive via FastAPI). Not in Codex sandbox but installed in real .venv.
- `command.schema.json`: 6 required fields, nested context with `additionalProperties: false` everywhere.
- `decision.schema.json`: 11 required fields, `additionalProperties: false` at top level. Payload is action-specific via allOf/oneOf.
- `decide()` accepts `Dict[str, Any]`, returns `Dict[str, Any]`. Validated by jsonschema both ways.
- Real pipeline output: exactly 11 fields, no extras. `model_validate()` will work with `extra="forbid"`.
- `app/models/` does not exist. `app/__init__.py` exists (app is a proper package).
- `pyproject.toml` includes `app*` in packages.find.
- `test_decide_rejects_invalid_command` expects status 400 + `detail.error == "CommandDTO validation failed."` — must change to 422.
- `scripts/api_sanity.py` checks status 200 only — should still work.

## Files to Create/Modify

### File 1: CREATE `app/models/__init__.py`

Empty file:

```python
```

### File 2: CREATE `app/models/api_models.py`

```python
"""Pydantic models for API request/response (ST-032).

These models mirror contracts/schemas/command.schema.json and
contracts/schemas/decision.schema.json at the API boundary.
Internal pipeline continues to use Dict[str, Any].
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# --- Command sub-models (from command.schema.json) ---

class HouseholdMember(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str
    display_name: Optional[str] = None
    role: Optional[str] = None
    workload_score: Optional[float] = None


class Zone(BaseModel):
    model_config = ConfigDict(extra="forbid")

    zone_id: str
    name: str


class ShoppingList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    list_id: str
    name: str


class Household(BaseModel):
    model_config = ConfigDict(extra="forbid")

    household_id: Optional[str] = None
    members: List[HouseholdMember] = Field(min_length=1)
    zones: Optional[List[Zone]] = None
    shopping_lists: Optional[List[ShoppingList]] = None


class Defaults(BaseModel):
    model_config = ConfigDict(extra="forbid")

    default_assignee_id: Optional[str] = None
    default_list_id: Optional[str] = None


class Policies(BaseModel):
    model_config = ConfigDict(extra="forbid")

    quiet_hours: Optional[str] = None
    max_open_tasks_per_user: Optional[int] = Field(default=None, ge=0)


class Context(BaseModel):
    model_config = ConfigDict(extra="forbid")

    household: Household
    defaults: Optional[Defaults] = None
    policies: Optional[Policies] = None


CapabilityType = Literal[
    "start_job",
    "propose_create_task",
    "propose_add_shopping_item",
    "clarify",
]


class CommandRequest(BaseModel):
    """API input model — mirrors command.schema.json."""

    model_config = ConfigDict(extra="forbid")

    command_id: str
    user_id: str
    timestamp: str
    text: str
    capabilities: List[CapabilityType] = Field(min_length=1)
    context: Context


# --- Decision sub-models (from decision.schema.json) ---

StatusType = Literal["ok", "clarify", "error"]
ActionType = Literal[
    "start_job",
    "propose_create_task",
    "propose_add_shopping_item",
    "clarify",
]


class DecisionResponse(BaseModel):
    """API output model — mirrors decision.schema.json (top-level fields).

    payload is kept as Dict[str, Any] because the internal pipeline
    produces dicts, and jsonschema validates the action-specific shape
    in decision_service.py.
    """

    model_config = ConfigDict(extra="forbid")

    decision_id: str
    command_id: str
    status: StatusType
    action: ActionType
    confidence: float = Field(ge=0, le=1)
    payload: Dict[str, Any]
    explanation: str
    trace_id: str
    schema_version: str
    decision_version: str
    created_at: str
```

### File 3: MODIFY `app/routes/decide.py`

Replace the entire file with:

```python
"""Decision API route."""

from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.models.api_models import CommandRequest, DecisionResponse
from app.services.decision_service import (
    CommandValidationError,
    decide,
)


router = APIRouter()


@router.post("/decide")
async def decide_route(command: CommandRequest) -> DecisionResponse:
    try:
        decision = decide(command.model_dump())
    except CommandValidationError:
        # Safety net: Pydantic already validates input, but jsonschema
        # inside decide() may catch edge cases. Re-raise as 400.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "CommandDTO validation failed (jsonschema)."},
        )
    except Exception:
        trace_id = f"trace-{uuid4().hex}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal error.", "trace_id": trace_id},
        )

    return DecisionResponse.model_validate(decision)
```

Key changes from original:
- Removed `Request` import (no longer needed)
- Removed `Dict, Any` imports (no longer needed)
- Removed manual `request.json()` with try/except (FastAPI auto-parses)
- Removed `format_validation_error` import (Pydantic handles input errors)
- `command: CommandRequest` as parameter (FastAPI auto-validates)
- `decide(command.model_dump())` converts Pydantic model to dict for internal pipeline
- `DecisionResponse.model_validate(decision)` wraps output dict
- Kept `CommandValidationError` catch as safety net (should rarely fire)
- Kept internal error handler (500 with trace_id)

### File 4: MODIFY `pyproject.toml`

Add `"pydantic"` to the dependencies list. Change this:

```
dependencies = [
  "fastapi",
  "httpx",
  "jsonschema",
  "openai",
]
```

To:

```
dependencies = [
  "fastapi",
  "httpx",
  "jsonschema",
  "openai",
  "pydantic",
]
```

### File 5: MODIFY `tests/test_api_decide.py`

Replace the entire file with:

```python
import json
from pathlib import Path

from fastapi.testclient import TestClient
from jsonschema import validate

from app.main import create_app


BASE_DIR = Path(__file__).resolve().parents[1]
FIXTURE_PATH = (
    BASE_DIR
    / "skills"
    / "contract-checker"
    / "fixtures"
    / "valid_command_create_task.json"
)
DECISION_SCHEMA_PATH = BASE_DIR / "contracts" / "schemas" / "decision.schema.json"


def test_decide_returns_valid_decision(monkeypatch, tmp_path):
    monkeypatch.setenv("DECISION_LOG_PATH", str(tmp_path / "decisions.jsonl"))
    command = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    schema = json.loads(DECISION_SCHEMA_PATH.read_text(encoding="utf-8"))
    client = TestClient(create_app())

    response = client.post("/decide", json=command)
    assert response.status_code == 200
    decision = response.json()
    validate(instance=decision, schema=schema)


def test_decide_rejects_invalid_command(monkeypatch, tmp_path):
    monkeypatch.setenv("DECISION_LOG_PATH", str(tmp_path / "decisions.jsonl"))
    client = TestClient(create_app())
    response = client.post("/decide", json={"command_id": "cmd-1"})
    assert response.status_code == 422
    payload = response.json()
    assert "detail" in payload
```

Changes:
- `test_decide_rejects_invalid_command`: status 400 → 422, simplified assertion (Pydantic format)

### File 6: CREATE `tests/test_api_models.py`

```python
"""Tests for Pydantic API models (ST-032)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.models.api_models import CommandRequest, DecisionResponse


def _valid_command_dict() -> dict:
    return {
        "command_id": "cmd-test-001",
        "user_id": "user-test-001",
        "timestamp": "2026-01-01T12:00:00+00:00",
        "text": "Тестовая команда",
        "capabilities": ["start_job", "clarify"],
        "context": {
            "household": {
                "members": [{"user_id": "user-test-001"}]
            }
        },
    }


def _valid_decision_dict() -> dict:
    return {
        "decision_id": "dec-001",
        "command_id": "cmd-001",
        "status": "ok",
        "action": "start_job",
        "confidence": 0.78,
        "payload": {
            "job_id": "job-001",
            "job_type": "create_task",
            "proposed_actions": [],
        },
        "explanation": "Тестовое решение.",
        "trace_id": "trace-001",
        "schema_version": "2.0.0",
        "decision_version": "mvp1-graph-0.1",
        "created_at": "2026-01-01T12:00:00+00:00",
    }


def test_command_request_valid() -> None:
    cmd = CommandRequest.model_validate(_valid_command_dict())
    assert cmd.command_id == "cmd-test-001"
    assert cmd.context.household.members[0].user_id == "user-test-001"


def test_command_request_missing_field() -> None:
    data = _valid_command_dict()
    del data["text"]
    with pytest.raises(ValidationError):
        CommandRequest.model_validate(data)


def test_command_request_invalid_capability() -> None:
    data = _valid_command_dict()
    data["capabilities"] = ["start_job", "unknown_cap"]
    with pytest.raises(ValidationError):
        CommandRequest.model_validate(data)


def test_command_request_extra_field_rejected() -> None:
    data = _valid_command_dict()
    data["extra_field"] = "should fail"
    with pytest.raises(ValidationError):
        CommandRequest.model_validate(data)


def test_decision_response_valid() -> None:
    dec = DecisionResponse.model_validate(_valid_decision_dict())
    assert dec.decision_id == "dec-001"
    assert dec.action == "start_job"


def test_decision_response_confidence_bounds() -> None:
    data = _valid_decision_dict()
    data["confidence"] = 1.5
    with pytest.raises(ValidationError):
        DecisionResponse.model_validate(data)

    data["confidence"] = -0.1
    with pytest.raises(ValidationError):
        DecisionResponse.model_validate(data)


def test_decision_response_roundtrip() -> None:
    data = _valid_decision_dict()
    dec = DecisionResponse.model_validate(data)
    dumped = dec.model_dump()
    dec2 = DecisionResponse.model_validate(dumped)
    assert dec == dec2


def test_command_context_nested_validation() -> None:
    data = _valid_command_dict()
    data["context"]["household"]["members"] = []
    with pytest.raises(ValidationError):
        CommandRequest.model_validate(data)
```

## Verification Commands

After implementation, run:

```bash
# New model tests
python3 -m pytest tests/test_api_models.py -v

# Updated API tests
python3 -m pytest tests/test_api_decide.py -v

# API sanity script
python3 scripts/api_sanity.py

# Full regression
python3 -m pytest --tb=short -q
```

**Expected:**
- `tests/test_api_models.py`: 8 passed
- `tests/test_api_decide.py`: 2 passed
- `scripts/api_sanity.py`: "API sanity passed."
- Full suite: 283 passed, 3 skipped

## STOP-THE-LINE

If any of the following occur, stop and report:
- `from pydantic import BaseModel` fails (should not — Pydantic 2.12.5 confirmed)
- Existing tests break in ways not covered by the changes above
- `DecisionResponse.model_validate(decision_dict)` raises ValidationError on real pipeline output
- `scripts/api_sanity.py` fails after route change
