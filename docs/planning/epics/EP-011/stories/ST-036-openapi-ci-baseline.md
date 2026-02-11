# ST-036: Auto-Generated OpenAPI Spec with CI Snapshot Baseline

**Epic:** EP-011 (Versioned REST API)
**Status:** Ready
**Flags:** contract_impact=no, adr_needed=none, diagrams_needed=none

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/pi/2026Q1-PI02/pi.md` |
| Epic | `docs/planning/epics/EP-011/epic.md` |
| Current CI | `.github/workflows/ci.yml` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

After ST-032 (Pydantic models), ST-033 (versioned paths), ST-034 (health), and ST-035
(structured errors), the API has a well-defined shape that FastAPI can auto-generate
as an OpenAPI 3.x spec. This story captures the generated spec as a committed baseline
and adds a CI step that regenerates and diffs against it, catching unintended API drift.

## User Value

As a platform maintainer, I want an auto-generated OpenAPI spec committed to the repo
with a CI check that detects drift, so that API changes are always intentional and
documented, and ConsumerApp developers can always trust `openapi.json` as accurate.

## Scope

### In scope

- Script: `scripts/generate_openapi.py` — uses FastAPI `app.openapi()` to dump JSON spec
- Committed baseline: `contracts/openapi.json` — auto-generated, committed to repo
- CI step in `.github/workflows/ci.yml`: regenerate spec + diff against committed baseline
- CI fails if diff is non-empty (forces developer to regenerate and commit updated spec)
- FastAPI app metadata: title, description, version from `contracts/VERSION`

### Out of scope

- OpenAPI spec customization beyond what FastAPI auto-generates
- Swagger UI / ReDoc hosting configuration
- OpenAPI client code generation
- Contract compatibility analysis (breaking change detection)

---

## Acceptance Criteria

### AC-1: OpenAPI spec is auto-generated from app
```
Given the FastAPI app with Pydantic models
When scripts/generate_openapi.py runs
Then contracts/openapi.json is produced
And it contains all endpoints: /v1/decide, /decide, /health, /ready
And request/response schemas match Pydantic models
```

### AC-2: Generated spec is valid OpenAPI 3.x
```
Given the generated openapi.json
When validated against OpenAPI 3.x specification
Then no validation errors are found
```

### AC-3: CI detects spec drift
```
Given contracts/openapi.json is committed
When a code change modifies the API shape (e.g., adding a field)
And developer does not update openapi.json
When CI runs the diff step
Then CI step fails with a clear message showing the diff
```

### AC-4: App metadata in spec matches contracts/VERSION
```
Given contracts/VERSION contains "2.0.0"
When OpenAPI spec is generated
Then info.version matches "2.0.0"
And info.title matches "HomeTask Decision API"
```

### AC-5: All 270+ existing tests pass

---

## Test Strategy

### Unit tests (~3 new in `tests/test_openapi_spec.py`)
- `test_generate_openapi_produces_valid_json`
- `test_openapi_contains_all_endpoints`
- `test_openapi_version_matches_contracts_version`

### CI verification
- CI step: `python3 scripts/generate_openapi.py > /tmp/openapi.json && diff contracts/openapi.json /tmp/openapi.json`

### Regression
- Full test suite: 270+ tests must pass

---

## Code Touchpoints

| File | Change |
|------|--------|
| `scripts/generate_openapi.py` | New: OpenAPI generation script |
| `contracts/openapi.json` | New: committed OpenAPI baseline |
| `.github/workflows/ci.yml` | Modify: add OpenAPI diff step |
| `tests/test_openapi_spec.py` | New: spec validation tests |

---

## Dependencies

- Depends: ST-032 (Pydantic models), ST-033 (versioned paths), ST-034 (health), ST-035 (errors)
- Final story in EP-011 execution order
