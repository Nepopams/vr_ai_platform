# Codex PLAN Prompt — ST-033: Versioned API Path `/v1/decide`

## Role

You are a senior Python/FastAPI developer performing a **read-only exploration** to gather facts for implementing versioned API paths.

## Rules

- **NO file edits, NO file creation, NO writes of any kind.**
- Only use: `ls`, `find`, `cat`, `rg`/`grep`, `sed -n`, `head`, `tail`, `git status`, `git diff`
- If you discover something that contradicts the plan → **STOP and report** (STOP-THE-LINE)

## Context

We are adding a `/v1` prefix to the decide endpoint (per ADR-007). The plan is to mount the decide router twice in `app/main.py` — once with `/v1` prefix (canonical) and once at root (backward compat). A middleware adds `API-Version: v1` header to `/v1/*` responses.

## Tasks

### Task 1: Read current app/main.py
```bash
cat app/main.py
```
Confirm: `create_app()` factory, `include_router(decide_router)` and `include_router(health_router)`. We need to add a second mount with prefix.

### Task 2: Confirm FastAPI middleware pattern
```bash
rg "middleware" app/ tests/ --files-with-matches
```
Check if any middleware exists already. We need to add one for the API-Version header.

### Task 3: Read current app/routes/decide.py
```bash
cat app/routes/decide.py
```
Confirm the route is `@router.post("/decide")` — the prefix will be added by `include_router(prefix="/v1")`.

### Task 4: Read tests/test_api_decide.py
```bash
cat tests/test_api_decide.py
```
Confirm current paths used (`/decide`). We'll update to `/v1/decide`.

### Task 5: Read scripts/api_sanity.py
```bash
cat scripts/api_sanity.py
```
Confirm path used. Update to `/v1/decide`.

### Task 6: Check if double-mounting a router works in FastAPI
```bash
python3 -c "
from fastapi import FastAPI, APIRouter
r = APIRouter()
@r.get('/test')
async def t(): return {'ok': True}
app = FastAPI()
app.include_router(r, prefix='/v1')
app.include_router(r)
routes = [route.path for route in app.routes]
print(routes)
"
```
Verify both `/v1/test` and `/test` appear in routes.

### Task 7: Check FastAPI middleware for adding response headers
```bash
python3 -c "
from starlette.middleware.base import BaseHTTPMiddleware
print('BaseHTTPMiddleware available')
"
```
Confirm starlette middleware is available (FastAPI uses Starlette).

## Expected Output

For each task: what you found + any deviations.

## STOP-THE-LINE Triggers

- Double-mounting router causes duplicate route errors
- FastAPI/Starlette middleware not available
- `app/routes/decide.py` has hard-coded paths that prevent prefix mounting
