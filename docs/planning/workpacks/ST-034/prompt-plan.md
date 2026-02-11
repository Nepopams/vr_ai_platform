# Codex PLAN Prompt — ST-034: Health and Readiness Endpoints

## Role

You are a senior Python/FastAPI developer performing a **read-only exploration** of the codebase to gather facts needed for implementation of health and readiness endpoints.

## Rules

- **NO file edits, NO file creation, NO writes of any kind.**
- Only use: `ls`, `find`, `cat`, `rg`/`grep`, `sed -n`, `head`, `tail`, `git status`, `git diff`
- If you discover something that contradicts the plan below → **STOP and report it** (STOP-THE-LINE)

## Context

We are adding `GET /health` and `GET /ready` endpoints to the FastAPI application. These are infrastructure-level endpoints (not versioned under `/v1/`). The app factory is in `app/main.py`, which currently includes a single router from `app/routes/decide.py`.

## Tasks

### Task 1: Confirm app factory structure
Read `app/main.py`. Confirm:
- `create_app()` function exists
- How routers are included (e.g., `app.include_router(...)`)
- Whether there's any middleware or startup events that could affect new routes

### Task 2: Confirm contracts/VERSION content
Read `contracts/VERSION`. Confirm the version string format (expect `2.0.0`).

### Task 3: Check how decision_service resolves paths
Read `app/services/decision_service.py`. Confirm:
- How `BASE_DIR` and `SCHEMA_DIR` are computed
- What files are loaded (command.schema.json, decision.schema.json)
- This is the pattern to reuse for version file reading and readiness checking

### Task 4: Check if app/routes/ directory exists and its structure
```
ls -la app/routes/
```
Confirm there's an `__init__.py` (or if the directory is an implicit namespace package).

### Task 5: Check if app/models/ directory exists
```
ls -la app/models/ 2>/dev/null || echo "DOES NOT EXIST"
```
We need to know if we should create it or if it already exists.

### Task 6: Check existing test patterns
Read `tests/test_api_decide.py`. Confirm:
- How TestClient is created (from `app.main.create_app()` or `app.main.app`?)
- How `monkeypatch` and `tmp_path` are used for isolation
- Import patterns

### Task 7: Check if FastAPI JSONResponse is available
```
rg "JSONResponse" app/ tests/
```
We need JSONResponse for the 503 readiness failure response.

### Task 8: Check if there's a conftest.py with shared fixtures
```
cat tests/conftest.py 2>/dev/null || echo "NO CONFTEST"
```

## Expected Output

For each task, report:
1. What you found (exact values, paths, patterns)
2. Any deviations from expectations
3. Any STOP-THE-LINE issues

## STOP-THE-LINE Triggers

- `app/main.py` structure is fundamentally different from expected
- `contracts/VERSION` doesn't exist or has unexpected format
- FastAPI version doesn't support plain dict responses (unlikely but check)
- `app/routes/` has no `__init__.py` and isn't a namespace package
