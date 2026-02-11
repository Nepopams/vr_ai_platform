# Codex APPLY Prompt — ST-033: Versioned API Path `/v1/decide`

## Role

You are a senior Python/FastAPI developer implementing versioned API paths per ADR-007.

## Rules

- Create/modify ONLY the files listed below. Do NOT touch any other files.
- Do NOT modify `app/routes/decide.py` or `app/routes/health.py`.
- If anything contradicts the plan → **STOP and report** (STOP-THE-LINE).

## PLAN Findings Summary

- `app/main.py`: `create_app()` with `include_router(decide_router)` and `include_router(health_router)`. No middleware.
- `app/routes/decide.py`: `@router.post("/decide")` with `CommandRequest` param. Uses `model_dump(exclude_none=True)`.
- **Double-mount confirmed:** FastAPI registers both `/v1/test` and `/test` when same router mounted twice.
- **Starlette 0.52.1** available. `BaseHTTPMiddleware` importable.
- `tests/test_api_decide.py`: uses `/decide` path. `scripts/api_sanity.py`: uses `/decide` path.
- No existing middleware in codebase.

## Files to Create/Modify

### File 1: MODIFY `app/main.py`

Replace the entire file with:

```python
"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.routes.decide import router as decide_router
from app.routes.health import router as health_router


class APIVersionMiddleware(BaseHTTPMiddleware):
    """Add API-Version header to all /v1/* responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        if request.url.path.startswith("/v1/"):
            response.headers["API-Version"] = "v1"
        return response


def create_app() -> FastAPI:
    app = FastAPI(title="HomeTask Decision API")
    app.add_middleware(APIVersionMiddleware)
    app.include_router(decide_router, prefix="/v1")
    app.include_router(decide_router)
    app.include_router(health_router)
    return app


app = create_app()
```

Key changes:
- `APIVersionMiddleware`: adds `API-Version: v1` header on `/v1/*` responses
- `decide_router` mounted twice: with `/v1` prefix (canonical) and at root (backward compat)
- `health_router` stays at root (infrastructure, not versioned per ADR-007)
- Order: `/v1` prefix first, then root — FastAPI matches first-come

### File 2: CREATE `tests/test_api_versioned.py`

```python
"""Tests for versioned API paths (ST-033)."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app

BASE_DIR = Path(__file__).resolve().parents[1]
FIXTURE_PATH = (
    BASE_DIR
    / "skills"
    / "contract-checker"
    / "fixtures"
    / "valid_command_create_task.json"
)


def _client() -> TestClient:
    return TestClient(create_app())


def _valid_command() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_v1_decide_returns_valid_decision(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DECISION_LOG_PATH", str(tmp_path / "decisions.jsonl"))
    client = _client()
    response = client.post("/v1/decide", json=_valid_command())
    assert response.status_code == 200
    data = response.json()
    assert "decision_id" in data
    assert "action" in data


def test_v1_decide_returns_version_header(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DECISION_LOG_PATH", str(tmp_path / "decisions.jsonl"))
    client = _client()
    response = client.post("/v1/decide", json=_valid_command())
    assert response.headers.get("API-Version") == "v1"


def test_unversioned_decide_still_works(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DECISION_LOG_PATH", str(tmp_path / "decisions.jsonl"))
    client = _client()
    response = client.post("/decide", json=_valid_command())
    assert response.status_code == 200
    data = response.json()
    assert "decision_id" in data


def test_v1_invalid_command_returns_error_with_version_header(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DECISION_LOG_PATH", str(tmp_path / "decisions.jsonl"))
    client = _client()
    response = client.post("/v1/decide", json={"command_id": "cmd-1"})
    assert response.status_code == 422
    assert response.headers.get("API-Version") == "v1"


def test_health_no_version_header() -> None:
    client = _client()
    response = client.get("/health")
    assert response.status_code == 200
    assert "API-Version" not in response.headers
```

### File 3: MODIFY `tests/test_api_decide.py`

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

    response = client.post("/v1/decide", json=command)
    assert response.status_code == 200
    decision = response.json()
    validate(instance=decision, schema=schema)


def test_decide_rejects_invalid_command(monkeypatch, tmp_path):
    monkeypatch.setenv("DECISION_LOG_PATH", str(tmp_path / "decisions.jsonl"))
    client = TestClient(create_app())
    response = client.post("/v1/decide", json={"command_id": "cmd-1"})
    assert response.status_code == 422
    payload = response.json()
    assert "detail" in payload
```

Changes: `/decide` → `/v1/decide` in both tests.

### File 4: MODIFY `scripts/api_sanity.py`

Replace the entire file with:

```python
"""Smoke test for Decision API using FastAPI TestClient."""

from __future__ import annotations

import json
import os
import tempfile
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


def main() -> int:
    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ["DECISION_LOG_PATH"] = str(Path(temp_dir) / "decisions.jsonl")
        command = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        schema = json.loads(DECISION_SCHEMA_PATH.read_text(encoding="utf-8"))
        client = TestClient(create_app())

        response = client.post("/v1/decide", json=command)
        if response.status_code != 200:
            print(f"API sanity failed: {response.status_code} {response.text}")
            return 1

        decision = response.json()
        validate(instance=decision, schema=schema)
        print("API sanity passed.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Change: `/decide` → `/v1/decide`.

## Verification Commands

After implementation, run:

```bash
# New versioned tests
python3 -m pytest tests/test_api_versioned.py -v

# Updated API tests
python3 -m pytest tests/test_api_decide.py -v

# API sanity
python3 scripts/api_sanity.py

# Full regression
python3 -m pytest --tb=short -q
```

**Expected:**
- `tests/test_api_versioned.py`: 5 passed
- `tests/test_api_decide.py`: 2 passed
- `scripts/api_sanity.py`: "API sanity passed."
- Full suite: 288 passed, 3 skipped

## STOP-THE-LINE

If any of the following occur, stop and report:
- `from starlette.middleware.base import BaseHTTPMiddleware` fails
- Double-mount causes route conflicts or duplicate operation IDs
- Existing tests break in ways not covered by changes above
