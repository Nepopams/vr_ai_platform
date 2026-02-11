# ST-032: Pydantic Models for CommandDTO and DecisionDTO

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
| Command schema | `contracts/schemas/command.schema.json` |
| Decision schema | `contracts/schemas/decision.schema.json` |
| Current route | `app/routes/decide.py` |
| Decision service | `app/services/decision_service.py` |
| pyproject.toml | `pyproject.toml` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

The API currently uses raw `Dict[str, Any]` for both input and output. Validation is done
via jsonschema against `command.schema.json` and `decision.schema.json`. There are no
Pydantic models, and Pydantic is not explicitly declared in `pyproject.toml` (though FastAPI
bundles it as a dependency).

This story introduces Pydantic models that mirror the existing JSON schemas, replaces
raw dict I/O in the route handler, and explicitly adds Pydantic to dependencies.

## User Value

As a ConsumerApp developer, I want typed request/response models for the `/decide` endpoint,
so that I get auto-validation, IDE auto-completion, and auto-generated OpenAPI documentation.

## Scope

### In scope

- Pydantic model: `CommandRequest` — mirrors `command.schema.json` (6 required fields + nested context)
- Pydantic model: `DecisionResponse` — mirrors `decision.schema.json` (11 required fields + action-specific payloads)
- Pydantic sub-models for nested structures (HouseholdMember, Zone, ShoppingList, Context, etc.)
- Pydantic sub-models for payload variants (TaskPayload, ShoppingItemPayload, ClarifyPayload, StartJobPayload, etc.)
- New module: `app/models/api_models.py` (all models in one file)
- Update `app/routes/decide.py` to use `CommandRequest` as input and `DecisionResponse` as return type
- Add `pydantic` to `pyproject.toml` dependencies (explicit declaration)
- Update `app/services/decision_service.py`: accept `CommandRequest`, return `DecisionResponse`
  - **Retain** jsonschema validation internally as a safety net (dual validation during migration)
- Update `tests/test_api_decide.py` to work with new typed I/O
- Update `scripts/api_sanity.py` to work with new route signature

### Out of scope

- Versioned path prefix (ST-033)
- Error response models (ST-035)
- Health endpoints (ST-034)
- Removing jsonschema validation (keep as safety net during migration)
- OpenAPI spec generation/CI (ST-036)

---

## Acceptance Criteria

### AC-1: CommandRequest model matches command.schema.json
```
Given the CommandRequest Pydantic model
When compared to command.schema.json
Then all 6 required fields are present (command_id, user_id, timestamp, text, capabilities, context)
And nested context structure matches (household with members, zones, shopping_lists; defaults; policies)
And capabilities is a list of enum values matching the schema
```

### AC-2: DecisionResponse model matches decision.schema.json
```
Given the DecisionResponse Pydantic model
When compared to decision.schema.json
Then all 11 required fields are present
And action-specific payload variants are discriminated by action field
And confidence is bounded [0, 1]
```

### AC-3: Route handler uses Pydantic models
```
Given a valid JSON command matching CommandRequest
When POST /decide is called
Then FastAPI auto-validates via Pydantic (no manual request.json() parsing)
And response is serialized from DecisionResponse model
And response body matches decision.schema.json
```

### AC-4: Invalid input returns 422 with Pydantic validation errors
```
Given a JSON command with missing required field "text"
When POST /decide is called
Then HTTP 422 is returned (FastAPI default for Pydantic validation failure)
And response body contains validation error details
```

### AC-5: Jsonschema validation remains as safety net
```
Given valid Pydantic input that somehow produces an invalid decision dict
When decision_service validates output
Then jsonschema still catches violations (belt-and-suspenders)
```

### AC-6: All 270 existing tests pass

---

## Test Strategy

### Unit tests (~8 new in `tests/test_api_models.py`)
- `test_command_request_valid` — construct from valid dict
- `test_command_request_missing_field` — raises ValidationError
- `test_command_request_invalid_capability` — rejects unknown capability
- `test_decision_response_valid_start_job` — construct from valid start_job dict
- `test_decision_response_valid_clarify` — construct from valid clarify dict
- `test_decision_response_confidence_bounds` — rejects confidence > 1 or < 0
- `test_decision_response_roundtrip` — model → dict → model
- `test_command_context_nested_validation` — validates household.members structure

### Updated tests
- `tests/test_api_decide.py` — update to match new response shape (should still pass with Pydantic typed output)

### Regression
- Full test suite: 270 tests must pass

---

## Code Touchpoints

| File | Change |
|------|--------|
| `app/models/__init__.py` | New: empty init |
| `app/models/api_models.py` | New: CommandRequest, DecisionResponse, nested models |
| `app/routes/decide.py` | Modify: use CommandRequest as parameter, DecisionResponse as return |
| `app/services/decision_service.py` | Modify: accept CommandRequest.model_dump(), keep jsonschema |
| `pyproject.toml` | Modify: add "pydantic" to dependencies |
| `tests/test_api_models.py` | New: unit tests for models |
| `tests/test_api_decide.py` | Modify: update for Pydantic-typed route |
| `scripts/api_sanity.py` | Modify: update for Pydantic-typed route |

---

## Dependencies

- Blocks: ST-033 (versioned path needs Pydantic models)
- Blocks: ST-035 (error models build on Pydantic)
- Blocks: ST-036 (OpenAPI needs Pydantic models)
