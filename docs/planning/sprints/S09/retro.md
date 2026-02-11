# Sprint S09 -- Retrospective

**Date:** 2026-02-11
**Facilitator:** Claude (Arch/BA)
**Attendees:** Human (PO), Claude (Arch/BA), Codex (Dev)

---

## Sprint Summary

| Metric | Value |
|--------|-------|
| Sprint Goal | Deliver API foundation: Pydantic models, versioned path, health endpoints |
| Stories committed | 3 |
| Stories completed | 3/3 |
| Stories carried over | 0 |
| Sprint Goal met? | Yes |
| Tests: start → end | 270 → 288 (+18 new) |
| Must-fix issues | 0 |
| Should-fix issues | 0 |

Initiative status:
- INIT-2026Q1-api-integration: **3/5 EP-011 stories done** (ST-032, ST-033, ST-034)

---

## Evidence

### ST-034: Health and Readiness Endpoints (EP-011)
- Commit: `493069f`
- Files: `app/routes/health.py` (new), `app/main.py` (modified), `tests/test_health_ready.py` (new, 5 tests)
- `GET /health` → 200 + `{"status": "ok", "version": "2.0.0"}`
- `GET /ready` → 200/503 with decision service check
- Independent of other stories, executed first.

### ST-032: Pydantic Models for CommandDTO and DecisionDTO (EP-011)
- Commit: `4761bb6`
- Files: `app/models/api_models.py` (new), `app/routes/decide.py` (modified), `pyproject.toml` (modified), `tests/test_api_models.py` (new, 8 tests), `tests/test_api_decide.py` (modified)
- CommandRequest: 6 required fields + nested Context with all sub-models
- DecisionResponse: 11 required fields, payload as Dict[str, Any]
- **Review fix:** `model_dump()` → `model_dump(exclude_none=True)` — Pydantic v2 serializes Optional fields as `null`, jsonschema rejects `null` for `"type": "array"/"object"`. One-line fix during review.
- STOP-THE-LINE in PLAN: Pydantic not in Codex sandbox (resolved — available in real .venv as FastAPI transitive dep).

### ST-033: Versioned API Path /v1/decide (EP-011)
- Commit: `d84c95a`
- Files: `app/main.py` (modified), `tests/test_api_versioned.py` (new, 5 tests), `tests/test_api_decide.py` (modified), `scripts/api_sanity.py` (modified)
- `POST /v1/decide` canonical, `POST /decide` backward compat (same handler, double-mount)
- `APIVersionMiddleware` adds `API-Version: v1` header on `/v1/*` responses
- STOP-THE-LINE in PLAN: starlette not in Codex sandbox (resolved — available in real .venv).

### Verification
```
288 passed, 3 skipped in 11.84s
```

---

## What Went Well

- **3/3 stories, 0 must-fix.** Streak: 33/33 stories across 9 sprints, zero carry-overs.
- **First PI02 sprint complete.** EP-011 at 3/5.
- **Review caught real bug.** ST-032 `model_dump()` → `model_dump(exclude_none=True)` — would have broken existing jsonschema validation. Caught by running `test_decide_returns_valid_decision`.
- **Codex sandbox STOP-THE-LINE pattern well-established.** Both ST-032 and ST-033 PLAN phases triggered STOP-THE-LINE for missing transitive deps (pydantic, starlette). Quick resolution: verify in real .venv, proceed.
- **Double-mount pattern elegant.** Same router mounted with and without prefix — zero code duplication for backward compat.
- **ADR-007 created before sprint.** No ambiguity during implementation.

---

## What Could Be Improved

- **Codex sandbox false STOP-THE-LINE.** Both stories hit it for transitive deps. Consider noting in PLAN prompts that sandbox lacks `.venv` and transitive deps should be verified separately.
- **ST-032 `exclude_none=True` not anticipated in workpack.** The Pydantic v2 behavior of serializing `None` as `null` is well-known. Should have been in the workpack's risk section and prompt-apply.

---

## Action Items

| # | Action | Owner | Status |
|---|--------|-------|--------|
| 1 | Carry from S08: Update golden-dataset guide baseline metrics | Claude | Open (cosmetic) |
| 2 | Add note to PLAN prompt template: Codex sandbox lacks transitive deps (pydantic, starlette, etc.) — verify in real .venv | Claude | Open |
| 3 | Add `exclude_none=True` pattern to MEMORY as Pydantic v2 lesson | Claude | Closed (applied below) |

---

## Sprint Velocity

| Sprint | Stories | Tests Added | Duration | Notes |
|--------|---------|-------------|----------|-------|
| S01 | 4/4 | 0 → 109 | ~1 day | NOW phase |
| S02 | 3/3 | 109 → 131 | ~1 day | Partial trust |
| S03 | 3/3 | 131 → 176 | ~1 day | Multi-entity |
| S04 | 3/3 | 176 → 202 | ~1 day | Improved clarify |
| S05 | 6/6 | 202 → 228 | ~1 day | CI + registry |
| S06 | 4/4 | 228 → 251 | ~1 day | Production hardening L1 |
| S07 | 4/4 | 251 → 268 | ~1 day | Production hardening L2 |
| S08 | 3/3 | 268 → 270 | ~1 day | Production hardening L3 |
| **S09** | **3/3** | **270 → 288** | **~1 day** | **API foundation (PI02 sprint 1)** |
| **Total** | **33/33** | **288 tests** | **9 sprints** | **0 carry-overs** |

---

## Platform Status (Post-S09)

### API Layer (new)
- `POST /v1/decide` — canonical versioned endpoint with Pydantic models
- `POST /decide` — backward-compatible (delegates to v1)
- `GET /health` — liveness probe
- `GET /ready` — readiness probe
- `API-Version: v1` header on all `/v1/*` responses
- ADR-007: API versioning strategy documented

### EP-011 Progress
| Story | Title | Status |
|-------|-------|--------|
| ST-032 | Pydantic models | Done |
| ST-033 | Versioned path /v1/decide | Done |
| ST-034 | Health/readiness endpoints | Done |
| ST-035 | Structured errors (problem+json) | Pending (S10) |
| ST-036 | OpenAPI spec + CI baseline | Pending (S10) |
