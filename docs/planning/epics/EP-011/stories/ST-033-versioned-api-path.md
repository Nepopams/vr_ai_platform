# ST-033: Versioned API Path `/v1/decide` with Router Prefix and Version Header

**Epic:** EP-011 (Versioned REST API)
**Status:** Ready
**Flags:** contract_impact=yes, adr_needed=lite (ADR-007)

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/pi/2026Q1-PI02/pi.md` |
| Epic | `docs/planning/epics/EP-011/epic.md` |
| ADR-001 (contract versioning) | `docs/adr/ADR-001-contract-versioning.md` |
| Current app factory | `app/main.py` |
| Current route | `app/routes/decide.py` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

The API currently exposes `POST /decide` at root level with no version prefix. Existing
consumers (api_sanity.py, test_api_decide.py) use this path directly. The PI plan calls
for versioned paths (`/v1/decide`) to allow future API evolution without breaking consumers.

ADR-007 (API versioning strategy) must be created as part of this story to document the
chosen approach (URL path prefix).

## User Value

As a ConsumerApp developer, I want a versioned API path (`/v1/decide`) with an explicit
API-Version response header, so that I can depend on a stable API contract and migrate
at my own pace when new versions are released.

## Scope

### In scope

- Router prefix: `POST /v1/decide` as the canonical endpoint
- `API-Version: v1` response header on all `/v1/*` responses (via middleware or response hook)
- Backward-compatible unversioned `POST /decide` — delegates to v1 implementation internally
- Update `app/main.py` to mount versioned router with `/v1` prefix
- ADR-007 (lite): document URL-path versioning strategy, backward-compatibility policy
- Update existing tests and api_sanity.py to use `/v1/decide` (and verify `/decide` still works)

### Out of scope

- Header-only versioning (URL path is primary)
- V2 API endpoint
- Content negotiation
- Deprecation headers/warnings for unversioned path
- Authentication/authorization

---

## Acceptance Criteria

### AC-1: Versioned path responds correctly
```
Given a valid CommandRequest
When POST /v1/decide is called
Then HTTP 200 is returned with a valid DecisionResponse
And response header contains "API-Version: v1"
```

### AC-2: Backward-compatible unversioned path works
```
Given a valid CommandRequest
When POST /decide is called (unversioned)
Then HTTP 200 is returned with the same DecisionResponse as /v1/decide
```

### AC-3: Version header present on all v1 responses
```
Given any request to /v1/* (including error responses)
When response is returned
Then "API-Version: v1" header is present
```

### AC-4: ADR-007 documents versioning strategy
```
Given ADR-007 is written
Then it documents: URL-path versioning strategy, backward-compatibility guarantee,
  deprecation policy for unversioned path, and criteria for introducing /v2
```

### AC-5: All 270+ existing tests pass (+ new tests for versioned path)

---

## Test Strategy

### Unit tests (~5 new in `tests/test_api_versioned.py`)
- `test_v1_decide_returns_valid_decision`
- `test_v1_decide_returns_version_header`
- `test_unversioned_decide_still_works`
- `test_v1_invalid_command_returns_error_with_version_header`
- `test_v1_route_registered`

### Updated tests
- `tests/test_api_decide.py` — update paths to `/v1/decide` (keep backward compat tests)
- `scripts/api_sanity.py` — update to use `/v1/decide`

### Regression
- Full test suite: 270+ tests must pass

---

## Code Touchpoints

| File | Change |
|------|--------|
| `app/main.py` | Modify: mount router with `/v1` prefix, add unversioned backward-compat route |
| `app/routes/decide.py` | Modify: add middleware/hook for API-Version header |
| `docs/adr/ADR-007-api-versioning.md` | New: API versioning strategy ADR |
| `docs/adr/README.md` | Modify: add ADR-007 entry |
| `tests/test_api_versioned.py` | New: versioned path tests |
| `tests/test_api_decide.py` | Modify: update paths |
| `scripts/api_sanity.py` | Modify: update path to `/v1/decide` |

---

## Dependencies

- Depends: ST-032 (Pydantic models must exist)
- Blocks: ST-036 (OpenAPI needs final path structure)
- ADR-007 is produced as part of this story
