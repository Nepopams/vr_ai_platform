# EP-011: Versioned REST API -- Production-Grade Endpoint for ConsumerApp

**Status:** Ready
**Initiative:** `docs/planning/initiatives/INIT-2026Q1-api-integration.md`
**PI:** `docs/planning/pi/2026Q1-PI02/pi.md`
**Sprint:** S09-S10 candidate
**Owner:** TBD

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/pi/2026Q1-PI02/pi.md` |
| Roadmap | `docs/planning/strategy/roadmap.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q1-api-integration.md` |
| Command schema | `contracts/schemas/command.schema.json` |
| Decision schema | `contracts/schemas/decision.schema.json` |
| Contract VERSION | `contracts/VERSION` (currently `2.0.0`) |
| Current API route | `app/routes/decide.py` |
| Current app factory | `app/main.py` |
| Decision service | `app/services/decision_service.py` |
| ADR-001 (contract versioning) | `docs/adr/ADR-001-contract-versioning.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

Current state of the API layer:

- Single `POST /decide` endpoint at root path (no version prefix)
- Route handler: `app/routes/decide.py` — reads raw JSON via `request.json()`, returns `Dict[str, Any]`
- Validation: `app/services/decision_service.py` — jsonschema validation against `command.schema.json` / `decision.schema.json`
- **No Pydantic models** — all I/O is raw dicts
- **Pydantic is NOT in `pyproject.toml` dependencies** (only fastapi, httpx, jsonschema, openai)
- Error responses are ad-hoc `HTTPException` with `detail` dicts (no standard format)
- No health/readiness endpoints
- No API version in URL path or response headers
- No auto-generated OpenAPI spec beyond FastAPI defaults
- `create_app()` factory includes single router, no prefix
- API sanity test (`scripts/api_sanity.py`) uses TestClient with `POST /decide`
- Test file `tests/test_api_decide.py` has 2 tests (valid decision + invalid command rejection)

## Goal

Transform the API layer into a production-grade, versioned REST API consumable by ConsumerApp:
Pydantic request/response models with validation, versioned path prefix (`/v1/`), health/readiness endpoints, structured error responses with RFC 7807 problem+json format, and auto-generated OpenAPI spec with CI baseline.

## Scope

### In scope

- Pydantic models for CommandDTO input and DecisionDTO output (replacing raw dict I/O)
- Pydantic added to `pyproject.toml` dependencies
- Versioned API path: `POST /v1/decide` (with router prefix)
- API-Version response header
- Backward-compatible unversioned `POST /decide` kept (redirects or delegates to v1)
- Health endpoint: `GET /health` (liveness)
- Readiness endpoint: `GET /ready` (checks decision service availability)
- Structured error responses: RFC 7807 problem+json format with error codes
- Auto-generated OpenAPI spec (`openapi.json`) derived from Pydantic models
- CI step: generate OpenAPI spec + diff against committed baseline
- ADR-007: API versioning strategy (lite)

### Out of scope

- Authentication / authorization
- Rate limiting
- gRPC / GraphQL
- WebSocket / streaming
- Multi-tenant API keys
- Request/response logging middleware
- API gateway / reverse proxy config
- Webhook integration (separate epic EP-012)

## Stories

| Story ID | Title | Status | Flags |
|----------|-------|--------|-------|
| [ST-032](stories/ST-032-pydantic-models.md) | Pydantic models for CommandDTO and DecisionDTO | Ready | contract_impact=yes, adr_needed=none, diagrams_needed=none |
| [ST-033](stories/ST-033-versioned-api-path.md) | Versioned API path `/v1/decide` with router prefix and version header | Ready (dep: ST-032) | contract_impact=yes, adr_needed=lite (ADR-007) |
| [ST-034](stories/ST-034-health-readiness.md) | Health and readiness endpoints | Ready | contract_impact=yes, adr_needed=none, diagrams_needed=none |
| [ST-035](stories/ST-035-structured-errors.md) | Structured error responses with problem+json format | Ready (dep: ST-032) | contract_impact=yes, adr_needed=none, diagrams_needed=none |
| [ST-036](stories/ST-036-openapi-ci-baseline.md) | Auto-generated OpenAPI spec with CI snapshot baseline | Ready (dep: ST-032, ST-033, ST-034, ST-035) | contract_impact=no, adr_needed=none, diagrams_needed=none |

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| FastAPI framework | External | Available (in pyproject.toml) |
| Pydantic library | External | **NOT in pyproject.toml** — must be added by ST-032 |
| Existing route (`app/routes/decide.py`) | Internal | Available |
| Decision service (`app/services/decision_service.py`) | Internal | Available |
| Contract schemas (`contracts/schemas/*.json`) | Internal | Available |
| ADR-001 (contract versioning policy) | Internal | Accepted |
| Existing tests (`tests/test_api_decide.py`) | Internal | Passing (2 tests) |
| API sanity script (`scripts/api_sanity.py`) | Internal | Available |

### Story ordering

```
ST-032 (Pydantic models)          ST-034 (health/readiness)
  |                                      |
  +------+------+                        |
  |             |                        |
  v             v                        |
ST-033        ST-035                     |
(versioned)   (errors)                   |
  |             |                        |
  +------+------+--------+--------------+
         |
         v
      ST-036 (OpenAPI + CI)
```

ST-032 is the foundation (Pydantic models). ST-033 and ST-035 depend on ST-032.
ST-034 (health/readiness) is independent — can run in parallel with ST-032.
ST-036 depends on all four (needs final API shape for OpenAPI baseline).

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Pydantic models break existing TestClient tests | Medium | Medium | Keep unversioned `/decide` backward-compatible; update test fixtures |
| FastAPI already bundles Pydantic | High | Low | Verify: `pip show pydantic` — if bundled, just declare explicitly in pyproject.toml |
| OpenAPI spec drift after future changes | Medium | Low | CI step: generate + diff against committed baseline |
| Backward-compatible path adds maintenance burden | Low | Low | Unversioned path delegates to v1 internally; minimal duplication |
| Error response format breaks existing consumers | Low | Medium | Validation errors return same HTTP 400 status; only body format changes |

## Readiness Report

### Ready
- **ST-032** -- No blockers. Pydantic likely bundled with FastAPI already. (~1 day)
- **ST-033** -- Depends on ST-032 for Pydantic models in route handler. ADR-007 needed (lite). (~1 day)
- **ST-034** -- No blockers. Independent of other stories. (~0.5 day)
- **ST-035** -- Depends on ST-032 for Pydantic error model. (~0.5 day)
- **ST-036** -- Depends on ST-032+ST-033+ST-034+ST-035 for final API shape. (~0.5 day)

### Conditional agents needed
- **contract_impact=yes** on ST-032, ST-033, ST-034, ST-035 -- contract-owner should review API contract changes
- **adr_needed=lite** on ST-033 -- adr-designer for ADR-007 (API versioning strategy)
