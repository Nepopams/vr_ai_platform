# Workpack: ST-033 — Versioned API Path `/v1/decide` with Router Prefix and Version Header

**Status:** Ready
**Story:** `docs/planning/epics/EP-011/stories/ST-033-versioned-api-path.md`

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/pi/2026Q1-PI02/pi.md` |
| Epic | `docs/planning/epics/EP-011/epic.md` |
| Story spec | `docs/planning/epics/EP-011/stories/ST-033-versioned-api-path.md` |
| ADR-007 | `docs/adr/ADR-007-api-versioning.md` |
| Current app factory | `app/main.py` |
| Current route | `app/routes/decide.py` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

`POST /v1/decide` as the canonical versioned endpoint. `API-Version: v1` response header on all `/v1/*` responses. Backward-compatible unversioned `POST /decide` retained, delegating to v1 implementation. Per ADR-007.

---

## Acceptance Criteria (from story spec)

1. **AC-1:** `POST /v1/decide` → 200 + valid DecisionResponse + `API-Version: v1` header
2. **AC-2:** `POST /decide` (unversioned) → 200 + same DecisionResponse (backward compat)
3. **AC-3:** `API-Version: v1` header on all `/v1/*` responses (including errors)
4. **AC-4:** ADR-007 documents versioning strategy (already created)
5. **AC-5:** All 283 existing tests pass (+ new tests)

---

## Key Design

Per ADR-007 and current codebase state (post-ST-032):

- `app/routes/decide.py` defines `router = APIRouter()` with `POST /decide`
- `app/main.py` includes it as `app.include_router(decide_router)` (no prefix)

**Approach:**
1. Mount decide_router under `/v1` prefix in `app/main.py`
2. Add a second mount of the same router at root (no prefix) for backward compat
3. Add middleware to inject `API-Version: v1` header on all `/v1/*` responses
4. The route in `decide.py` stays as `@router.post("/decide")` — the prefix is added by `include_router`

This means:
- `/v1/decide` → hits decide_router via prefixed mount
- `/decide` → hits decide_router via unprefixed mount
- Both call the exact same handler — zero duplication

---

## Files to Change

| File | Action | Description |
|------|--------|-------------|
| `app/main.py` | **Modify** | Mount decide_router twice (with /v1 prefix + root), add middleware |
| `tests/test_api_versioned.py` | **Create** | ~5 new tests for versioned path + header |
| `tests/test_api_decide.py` | **Modify** | Update path to `/v1/decide`, add backward compat test |
| `scripts/api_sanity.py` | **Modify** | Update path to `/v1/decide` |

### Forbidden paths (do not modify)

- `app/routes/decide.py` — route handler unchanged, prefix via main.py
- `app/routes/health.py` — health stays at root (not versioned)
- `app/services/decision_service.py` — internal
- `contracts/schemas/*.json` — stable boundary

---

## Implementation Plan

### Step 1: Modify `app/main.py`

- Mount decide_router with `/v1` prefix (canonical)
- Mount decide_router again at root (backward compat)
- Add middleware that sets `API-Version: v1` header on responses to `/v1/*` paths
- Health router stays at root (infrastructure, not versioned per ADR-007)

### Step 2: Create `tests/test_api_versioned.py`

5 tests:
1. `test_v1_decide_returns_valid_decision` — `POST /v1/decide` → 200
2. `test_v1_decide_returns_version_header` — response has `API-Version: v1`
3. `test_unversioned_decide_still_works` — `POST /decide` → 200 (backward compat)
4. `test_v1_invalid_command_returns_error_with_version_header` — 422 response also has `API-Version: v1`
5. `test_health_no_version_header` — `GET /health` does NOT have `API-Version` header

### Step 3: Update `tests/test_api_decide.py`

Update both tests to use `/v1/decide` as primary path.

### Step 4: Update `scripts/api_sanity.py`

Update `client.post("/decide", ...)` to `client.post("/v1/decide", ...)`.

---

## Verification Commands

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

---

## DoD Checklist

- [ ] `app/main.py` updated (v1 prefix + backward compat + middleware)
- [ ] `tests/test_api_versioned.py` created (5 tests)
- [ ] `tests/test_api_decide.py` updated (v1 path)
- [ ] `scripts/api_sanity.py` updated (v1 path)
- [ ] 5 new tests pass
- [ ] 283 existing tests pass (288 total, 3 skipped)
- [ ] `API-Version: v1` header present on /v1 responses
- [ ] `/decide` backward compat works
- [ ] ADR-007 already created (AC-4 satisfied)
- [ ] No modifications to forbidden paths

---

## Risks

| Risk | Mitigation |
|------|------------|
| Double-mounting router causes route conflicts | FastAPI supports this — routes are matched first-come |
| Middleware overhead | Lightweight string check on path, negligible |
| Existing tests break from path change | Update in same commit |

---

## Rollback

Revert `app/main.py` to single mount without prefix, revert test/script path changes. Zero impact.
