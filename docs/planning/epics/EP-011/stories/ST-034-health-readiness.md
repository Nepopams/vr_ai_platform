# ST-034: Health and Readiness Endpoints

**Epic:** EP-011 (Versioned REST API)
**Status:** Ready
**Flags:** contract_impact=yes, adr_needed=none, diagrams_needed=none

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/pi/2026Q1-PI02/pi.md` |
| Epic | `docs/planning/epics/EP-011/epic.md` |
| Current app factory | `app/main.py` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

The platform has no health or readiness endpoints. For production deployment behind a
load balancer or orchestrator (Kubernetes, Docker Compose), liveness and readiness probes
are essential. These endpoints are lightweight and independent of the Pydantic model story.

## User Value

As a platform operator, I want `/health` and `/ready` endpoints so that I can configure
liveness and readiness probes in my deployment orchestrator, ensuring automatic restarts
on failure and traffic routing only to ready instances.

## Scope

### In scope

- `GET /health` — liveness probe (always returns 200 if process is alive)
- `GET /ready` — readiness probe (checks that decision service can be called)
- Response models: `HealthResponse` (status, version), `ReadyResponse` (status, checks dict)
- Both endpoints at root level (not versioned — infrastructure concern, not API version)
- version field from `contracts/VERSION` or app metadata

### Out of scope

- Deep health checks (database, external LLM API)
- Metrics endpoint (/metrics for Prometheus)
- Startup probe (separate from liveness)
- Authentication on health endpoints

---

## Acceptance Criteria

### AC-1: Health endpoint returns liveness
```
Given the application is running
When GET /health is called
Then HTTP 200 is returned
And response body contains {"status": "ok", "version": "<app_version>"}
```

### AC-2: Ready endpoint checks decision service
```
Given the application is running and decision service is available
When GET /ready is called
Then HTTP 200 is returned
And response body contains {"status": "ready", "checks": {"decision_service": "ok"}}
```

### AC-3: Ready endpoint reports not-ready on failure
```
Given the decision service is unavailable (e.g., schema file missing)
When GET /ready is called
Then HTTP 503 is returned
And response body contains {"status": "not_ready", "checks": {"decision_service": "error: ..."}}
```

### AC-4: All 270 existing tests pass

---

## Test Strategy

### Unit tests (~5 new in `tests/test_health_ready.py`)
- `test_health_returns_ok`
- `test_health_contains_version`
- `test_ready_returns_ok_when_service_available`
- `test_ready_returns_503_when_service_unavailable`
- `test_ready_checks_dict_structure`

### Regression
- Full test suite: 270 tests must pass

---

## Code Touchpoints

| File | Change |
|------|--------|
| `app/routes/health.py` | New: /health and /ready route handlers |
| `app/models/health_models.py` | New: HealthResponse, ReadyResponse Pydantic models |
| `app/main.py` | Modify: include health router |
| `tests/test_health_ready.py` | New: endpoint tests |

---

## Dependencies

- No dependencies on other EP-011 stories (independent)
- Blocks: ST-036 (OpenAPI needs all endpoints)
