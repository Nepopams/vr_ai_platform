# Codex APPLY Prompt — ST-034: Health and Readiness Endpoints

## Role

You are a senior Python/FastAPI developer implementing health and readiness endpoints for the AI Platform.

## Rules

- Create/modify ONLY the files listed below. Do NOT touch any other files.
- Follow existing code patterns exactly (imports, path resolution, docstrings).
- Do NOT add Pydantic — use plain dict responses (ST-032 adds Pydantic later).
- Do NOT create `app/models/` directory or `app/routes/__init__.py` — they don't exist and aren't needed.
- If anything contradicts the plan → **STOP and report** (STOP-THE-LINE).

## PLAN Findings Summary

- `app/main.py`: `create_app()` factory, single `app.include_router(decide_router)`, no middleware
- `contracts/VERSION`: contains `2.0.0`
- Path pattern: `BASE_DIR = Path(__file__).resolve().parents[2]` (from `decision_service.py`)
- `app/routes/`: has `decide.py`, no `__init__.py` (works via implicit namespace)
- `app/models/`: does not exist — not needed for this story
- Tests: use `TestClient(create_app())`, `monkeypatch` for env vars
- `JSONResponse`: not yet used in codebase, but available from `fastapi.responses`
- `tests/conftest.py`: exists with shared fixtures

## Files to Create/Modify

### File 1: CREATE `app/routes/health.py`

```python
"""Health and readiness endpoints."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter
from fastapi.responses import JSONResponse

BASE_DIR = Path(__file__).resolve().parents[2]
VERSION_PATH = BASE_DIR / "contracts" / "VERSION"
COMMAND_SCHEMA_PATH = BASE_DIR / "contracts" / "schemas" / "command.schema.json"
DECISION_SCHEMA_PATH = BASE_DIR / "contracts" / "schemas" / "decision.schema.json"


def _read_version() -> str:
    try:
        return VERSION_PATH.read_text(encoding="utf-8").strip()
    except OSError:
        return "unknown"


router = APIRouter()


@router.get("/health")
async def health() -> Dict[str, Any]:
    return {"status": "ok", "version": _read_version()}


@router.get("/ready")
async def ready() -> JSONResponse:
    checks: Dict[str, str] = {}
    try:
        COMMAND_SCHEMA_PATH.read_text(encoding="utf-8")
        DECISION_SCHEMA_PATH.read_text(encoding="utf-8")
        checks["decision_service"] = "ok"
    except Exception as exc:
        checks["decision_service"] = f"error: {exc}"
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "checks": checks},
        )
    return JSONResponse(
        status_code=200,
        content={"status": "ready", "checks": checks},
    )
```

### File 2: MODIFY `app/main.py`

Replace the entire file with:

```python
"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI

from app.routes.decide import router as decide_router
from app.routes.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(title="HomeTask Decision API")
    app.include_router(decide_router)
    app.include_router(health_router)
    return app


app = create_app()
```

### File 3: CREATE `tests/test_health_ready.py`

```python
"""Tests for health and readiness endpoints (ST-034)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import create_app

BASE_DIR = Path(__file__).resolve().parents[1]
VERSION_PATH = BASE_DIR / "contracts" / "VERSION"


def _client() -> TestClient:
    return TestClient(create_app())


def test_health_returns_ok() -> None:
    client = _client()
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_health_contains_version() -> None:
    expected_version = VERSION_PATH.read_text(encoding="utf-8").strip()
    client = _client()
    response = client.get("/health")
    data = response.json()
    assert data["version"] == expected_version


def test_ready_returns_ok_when_service_available() -> None:
    client = _client()
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


def test_ready_returns_503_when_service_unavailable() -> None:
    fake_path = Path("/nonexistent/command.schema.json")
    with patch("app.routes.health.COMMAND_SCHEMA_PATH", fake_path):
        client = _client()
        response = client.get("/ready")
    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "not_ready"
    assert "error" in data["checks"]["decision_service"]


def test_ready_checks_dict_structure() -> None:
    client = _client()
    response = client.get("/ready")
    data = response.json()
    assert "checks" in data
    assert "decision_service" in data["checks"]
```

## Verification Commands

After implementation, run:

```bash
# New tests
python3 -m pytest tests/test_health_ready.py -v

# Full regression
python3 -m pytest --tb=short -q
```

**Expected:**
- `tests/test_health_ready.py`: 5 passed
- Full suite: 275 passed, 3 skipped

## STOP-THE-LINE

If any of the following occur, stop and report:
- `app/routes/health.py` import fails due to missing package structure
- Existing tests break after `app/main.py` modification
- `contracts/VERSION` path resolution differs at test time vs module time
