# ST-035: Structured Error Responses with Problem+JSON Format

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
| Current route | `app/routes/decide.py` |
| Current decision service | `app/services/decision_service.py` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

Current error responses are ad-hoc `HTTPException` with varying `detail` dicts:
- Invalid JSON: `{"error": "Invalid JSON body."}`
- Validation error: `{"error": "CommandDTO validation failed.", "violations": [...]}`
- Internal error: `{"error": "Internal error.", "trace_id": "trace-..."}`

These are inconsistent and not machine-parseable. RFC 7807 (Problem Details for HTTP APIs)
provides a standard format that consumers can reliably parse.

## User Value

As a ConsumerApp developer, I want structured, machine-readable error responses following
RFC 7807, so that my client can programmatically handle different error types without
parsing free-text error messages.

## Scope

### In scope

- Pydantic model: `ProblemDetail` — RFC 7807 fields (type, title, status, detail, instance, trace_id)
- Error codes enum: `INVALID_JSON`, `VALIDATION_FAILED`, `INTERNAL_ERROR`
- Custom exception handler for `CommandValidationError` → ProblemDetail response
- Custom exception handler for generic `Exception` → ProblemDetail response
- Content-Type header: `application/problem+json` on error responses
- Update `app/routes/decide.py` error handling to use ProblemDetail
- Pydantic ValidationError (422) handler → ProblemDetail format

### Out of scope

- Custom error codes for specific business logic errors
- Error logging changes (existing logging stays)
- Error response rate limiting
- Error response localization/i18n

---

## Acceptance Criteria

### AC-1: Validation error returns problem+json
```
Given an invalid command (missing required field)
When POST /v1/decide is called
Then HTTP 400 is returned
And Content-Type is "application/problem+json"
And body matches: {"type": "validation_error", "title": "Command Validation Failed",
  "status": 400, "detail": "...", "violations": [...]}
```

### AC-2: Invalid JSON returns problem+json
```
Given malformed JSON body
When POST /v1/decide is called
Then HTTP 400 is returned
And Content-Type is "application/problem+json"
And body matches: {"type": "invalid_json", "title": "Invalid JSON", "status": 400, ...}
```

### AC-3: Internal error returns problem+json with trace_id
```
Given an unexpected internal error
When POST /v1/decide is called
Then HTTP 500 is returned
And Content-Type is "application/problem+json"
And body matches: {"type": "internal_error", "title": "Internal Server Error",
  "status": 500, "trace_id": "trace-...", ...}
And actual error details are NOT leaked to client
```

### AC-4: Pydantic validation error (422) returns problem+json
```
Given input that fails Pydantic validation (e.g., wrong type for field)
When POST /v1/decide is called
Then HTTP 422 is returned
And Content-Type is "application/problem+json"
And body contains structured validation errors
```

### AC-5: All 270+ existing tests pass (+ new error tests)

---

## Test Strategy

### Unit tests (~6 new in `tests/test_structured_errors.py`)
- `test_validation_error_problem_json_format`
- `test_invalid_json_problem_json_format`
- `test_internal_error_problem_json_format`
- `test_internal_error_contains_trace_id`
- `test_pydantic_422_problem_json_format`
- `test_error_content_type_header`

### Updated tests
- `tests/test_api_decide.py` — update error assertions to match new ProblemDetail format

### Regression
- Full test suite: 270+ tests must pass

---

## Code Touchpoints

| File | Change |
|------|--------|
| `app/models/error_models.py` | New: ProblemDetail model, error code enum |
| `app/routes/decide.py` | Modify: replace HTTPException with ProblemDetail responses |
| `app/main.py` | Modify: register custom exception handlers |
| `tests/test_structured_errors.py` | New: error format tests |
| `tests/test_api_decide.py` | Modify: update error assertions |

---

## Dependencies

- Depends: ST-032 (Pydantic models and typed route handler)
- Blocks: ST-036 (OpenAPI needs error models)
