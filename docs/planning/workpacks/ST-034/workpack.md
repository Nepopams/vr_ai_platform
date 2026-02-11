# Workpack: ST-034 — Health and Readiness Endpoints

**Status:** Ready
**Story:** `docs/planning/epics/EP-011/stories/ST-034-health-readiness.md`

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/pi/2026Q1-PI02/pi.md` |
| Epic | `docs/planning/epics/EP-011/epic.md` |
| Story spec | `docs/planning/epics/EP-011/stories/ST-034-health-readiness.md` |
| App factory | `app/main.py` |
| Contract VERSION | `contracts/VERSION` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

Two new endpoints (`GET /health`, `GET /ready`) at root level, with Pydantic response models, integrated into the FastAPI app. Health returns liveness status + version. Ready checks decision service availability and returns 200 or 503.

---

## Acceptance Criteria (from story spec)

1. **AC-1:** `GET /health` → 200 + `{"status": "ok", "version": "2.0.0"}`
2. **AC-2:** `GET /ready` → 200 + `{"status": "ready", "checks": {"decision_service": "ok"}}`
3. **AC-3:** `GET /ready` with broken decision service → 503 + `{"status": "not_ready", "checks": {"decision_service": "error: ..."}}`
4. **AC-4:** All 270 existing tests pass

---

## Files to Change

| File | Action | Description |
|------|--------|-------------|
| `app/routes/health.py` | **Create** | Route handlers for `/health` and `/ready` |
| `app/main.py` | **Modify** | Include health router |
| `tests/test_health_ready.py` | **Create** | 5 endpoint tests |

### Forbidden paths (do not modify)

- `app/routes/decide.py` — untouched by this story
- `app/services/decision_service.py` — read-only (readiness check calls it, does not modify)
- `contracts/schemas/*.json` — stable boundary
- `routers/**` — not related
- `graphs/**` — not related

---

## Implementation Plan

### Step 1: Create `app/routes/health.py`

New file with two endpoints:

**`GET /health`** (liveness):
- Always returns 200
- Response body: `{"status": "ok", "version": "<version>"}`
- Version read from `contracts/VERSION` file (same as `app/services/decision_service.py` reads schemas from `contracts/`)
- Use `pathlib.Path` to read version at module level

**`GET /ready`** (readiness):
- Checks decision service availability by calling a lightweight probe
- Probe: attempt to load command schema + decision schema (same files `decision_service.py` uses). If both load successfully → ready
- On success: return 200 + `{"status": "ready", "checks": {"decision_service": "ok"}}`
- On failure: return 503 + `{"status": "not_ready", "checks": {"decision_service": "error: <message>"}}`
- Use `JSONResponse` with `status_code=503` for not-ready case

**Response models** (inline in same file — lightweight, no separate models file needed):
- `HealthResponse`: `status: str`, `version: str`
- `ReadyResponse`: `status: str`, `checks: Dict[str, str]`

Both are plain dataclasses or Pydantic models. Since ST-032 hasn't run yet and Pydantic isn't explicitly declared, use **plain dicts with type hints** for now (FastAPI supports `Dict` return types). ST-032 will add Pydantic later.

**Important:** Do NOT import Pydantic. This story is independent of ST-032. Use `Dict[str, Any]` return types and plain dict responses.

### Step 2: Modify `app/main.py`

Add import and include health router:

```python
from app.routes.health import router as health_router
# ... existing code ...
app.include_router(health_router)
```

### Step 3: Create `tests/test_health_ready.py`

5 tests using FastAPI TestClient:

1. `test_health_returns_ok` — `GET /health` → 200, `status == "ok"`
2. `test_health_contains_version` — response has `version` field matching `contracts/VERSION`
3. `test_ready_returns_ok_when_service_available` — `GET /ready` → 200, `status == "ready"`
4. `test_ready_returns_503_when_service_unavailable` — monkeypatch schema path to nonexistent file → 503, `status == "not_ready"`
5. `test_ready_checks_dict_structure` — `checks` dict has `decision_service` key

---

## Verification Commands

```bash
# Run new tests
python3 -m pytest tests/test_health_ready.py -v

# Run full suite (must still pass 270)
python3 -m pytest --tb=short -q

# Verify health endpoint manually
python3 -c "
from fastapi.testclient import TestClient
from app.main import create_app
c = TestClient(create_app())
print('health:', c.get('/health').json())
print('ready:', c.get('/ready').json())
"
```

**Expected outcomes:**
- `tests/test_health_ready.py`: 5 passed
- Full suite: 275 passed, 3 skipped
- Manual check: both endpoints return valid JSON

---

## Tests

| Test | File | Validates |
|------|------|-----------|
| `test_health_returns_ok` | `tests/test_health_ready.py` | AC-1 |
| `test_health_contains_version` | `tests/test_health_ready.py` | AC-1 |
| `test_ready_returns_ok_when_service_available` | `tests/test_health_ready.py` | AC-2 |
| `test_ready_returns_503_when_service_unavailable` | `tests/test_health_ready.py` | AC-3 |
| `test_ready_checks_dict_structure` | `tests/test_health_ready.py` | AC-2 |
| Full regression (270 existing) | all test files | AC-4 |

---

## DoD Checklist

- [ ] `app/routes/health.py` created with `/health` and `/ready`
- [ ] `app/main.py` includes health router
- [ ] `tests/test_health_ready.py` created with 5 tests
- [ ] All 5 new tests pass
- [ ] All 270 existing tests pass (275 total, 3 skipped)
- [ ] No modifications to forbidden paths
- [ ] No new dependencies added

---

## Risks

| Risk | Mitigation |
|------|------------|
| Schema file path differs in test vs prod | Use same `BASE_DIR` pattern as `decision_service.py` |
| Readiness check too expensive | Only check file existence/loadability, not full validation |

---

## Rollback

Revert: remove `app/routes/health.py`, remove import from `app/main.py`, remove `tests/test_health_ready.py`. Zero impact on existing functionality.
