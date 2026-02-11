# Workpack: ST-032 — Pydantic Models for CommandDTO and DecisionDTO

**Status:** Ready
**Story:** `docs/planning/epics/EP-011/stories/ST-032-pydantic-models.md`

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/pi/2026Q1-PI02/pi.md` |
| Epic | `docs/planning/epics/EP-011/epic.md` |
| Story spec | `docs/planning/epics/EP-011/stories/ST-032-pydantic-models.md` |
| Command schema | `contracts/schemas/command.schema.json` |
| Decision schema | `contracts/schemas/decision.schema.json` |
| Current route | `app/routes/decide.py` |
| Decision service | `app/services/decision_service.py` |
| pyproject.toml | `pyproject.toml` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

Pydantic models for CommandDTO input and DecisionDTO output, integrated into the FastAPI route handler. FastAPI auto-validates input via Pydantic (replacing manual `request.json()` + jsonschema for input). Jsonschema validation retained as safety net for output. Pydantic explicitly added to `pyproject.toml`.

---

## Acceptance Criteria (from story spec)

1. **AC-1:** CommandRequest Pydantic model matches command.schema.json (6 required fields, nested context)
2. **AC-2:** DecisionResponse Pydantic model matches decision.schema.json (11 required fields)
3. **AC-3:** Route handler uses Pydantic models (auto-validation input, typed output)
4. **AC-4:** Invalid input returns 422 with Pydantic validation errors
5. **AC-5:** Jsonschema validation retained as safety net for output
6. **AC-6:** All 275 existing tests pass

---

## Key Design Decisions

### Input: CommandRequest — full Pydantic model
- Mirrors `command.schema.json` exactly: 6 required fields + nested context
- `model_config = ConfigDict(extra="forbid")` to match `additionalProperties: false`
- Nested models: `HouseholdMember`, `Zone`, `ShoppingList`, `Household`, `Defaults`, `Policies`, `Context`
- `capabilities`: `List[Literal["start_job", "propose_create_task", "propose_add_shopping_item", "clarify"]]` with `min_length=1`
- FastAPI auto-validates on input — replaces manual `request.json()` + jsonschema

### Output: DecisionResponse — Pydantic model, payload as Dict
- 11 required fields with proper types
- `payload: Dict[str, Any]` — kept as dict because the entire internal pipeline produces dicts, and jsonschema validates the exact action-specific shape in `decision_service.py`
- `confidence: float` with `ge=0, le=1`
- `status: Literal["ok", "clarify", "error"]`
- `action: Literal["start_job", "propose_create_task", "propose_add_shopping_item", "clarify"]`

### Conversion flow
```
JSON body → FastAPI auto-parses → CommandRequest (Pydantic validates)
         → command.model_dump() → decide(dict) → dict
         → DecisionResponse.model_validate(dict) → FastAPI serializes
```

### Internal pipeline untouched
`decision_service.decide()` still accepts `Dict[str, Any]` and returns `Dict[str, Any]`. Jsonschema validation stays. Only the API boundary changes.

---

## Files to Change

| File | Action | Description |
|------|--------|-------------|
| `app/models/api_models.py` | **Create** | CommandRequest, DecisionResponse, nested models |
| `app/routes/decide.py` | **Modify** | Use CommandRequest param, DecisionResponse return |
| `pyproject.toml` | **Modify** | Add "pydantic" to dependencies |
| `tests/test_api_models.py` | **Create** | ~8 unit tests for models |
| `tests/test_api_decide.py` | **Modify** | Update error test (400→422, new error format) |
| `scripts/api_sanity.py` | **Modify** | Update to work with Pydantic-typed route |

### Forbidden paths (do not modify)

- `app/services/decision_service.py` — internal, stays Dict-based
- `routers/**` — internal pipeline
- `graphs/**` — internal pipeline
- `contracts/schemas/*.json` — stable boundary
- `app/routes/health.py` — unrelated (ST-034)

---

## Implementation Plan

### Step 1: Add pydantic to `pyproject.toml`

Add `"pydantic"` to the `dependencies` list. FastAPI already bundles it as a transitive dependency, but explicit declaration ensures it's not silently lost.

### Step 2: Create `app/models/api_models.py`

New module with all Pydantic models. Must create `app/models/__init__.py` (empty) first since the directory doesn't exist (confirmed in ST-034 PLAN).

**Models to create (matching schemas exactly):**

From `command.schema.json`:
- `HouseholdMember` — user_id (req), display_name (opt), role (opt), workload_score (opt)
- `Zone` — zone_id (req), name (req)
- `ShoppingList` — list_id (req), name (req)
- `Household` — household_id (opt), members (req, min 1), zones (opt), shopping_lists (opt)
- `Defaults` — default_assignee_id (opt), default_list_id (opt)
- `Policies` — quiet_hours (opt), max_open_tasks_per_user (opt, ge=0)
- `Context` — household (req), defaults (opt), policies (opt)
- `CommandRequest` — command_id, user_id, timestamp, text, capabilities (min 1), context

All with `model_config = ConfigDict(extra="forbid")`.

From `decision.schema.json`:
- `DecisionResponse` — 11 required fields, payload as `Dict[str, Any]`

### Step 3: Modify `app/routes/decide.py`

Current:
```python
async def decide_route(request: Request) -> Dict[str, Any]:
    payload = await request.json()
    decision = decide(payload)
    return decision
```

New:
```python
async def decide_route(command: CommandRequest) -> DecisionResponse:
    decision = decide(command.model_dump())
    return DecisionResponse.model_validate(decision)
```

Error handling changes:
- Remove manual `request.json()` try/except (FastAPI handles invalid JSON → 422)
- Remove `CommandValidationError` catch (Pydantic validates instead → 422)
- Keep internal error handler (500 with trace_id)
- Note: `CommandValidationError` from `decision_service` is still raised by jsonschema inside `decide()`, but since Pydantic already validated the input, it shouldn't fire. Keep the catch as safety net.

### Step 4: Update `tests/test_api_decide.py`

`test_decide_rejects_invalid_command`:
- Currently asserts: `status_code == 400`, `detail.error == "CommandDTO validation failed."`
- After: assert `status_code == 422` (Pydantic validation error)
- Body format: `{"detail": [{"type": "...", "loc": [...], "msg": "..."}]}` (FastAPI standard)

`test_decide_returns_valid_decision`:
- Should still pass as-is (valid input → 200 → valid decision JSON)

### Step 5: Update `scripts/api_sanity.py`

Should still work as-is because:
- Sends valid JSON fixture → 200
- Validates response against jsonschema
- If route return type changes to `DecisionResponse`, FastAPI serializes it the same way

PLAN phase should confirm this.

### Step 6: Create `tests/test_api_models.py`

8 unit tests:
1. `test_command_request_valid` — construct from valid dict
2. `test_command_request_missing_field` — raises ValidationError on missing `text`
3. `test_command_request_invalid_capability` — rejects unknown capability string
4. `test_command_request_extra_field_rejected` — extra fields rejected (additionalProperties: false)
5. `test_decision_response_valid` — construct from valid decision dict
6. `test_decision_response_confidence_bounds` — rejects confidence > 1 or < 0
7. `test_decision_response_roundtrip` — model → dict → model is stable
8. `test_command_context_nested_validation` — validates household.members min_length=1

---

## Verification Commands

```bash
# New model tests
python3 -m pytest tests/test_api_models.py -v

# Updated API tests
python3 -m pytest tests/test_api_decide.py -v

# API sanity script
python3 scripts/api_sanity.py

# Full regression
python3 -m pytest --tb=short -q
```

**Expected outcomes:**
- `tests/test_api_models.py`: 8 passed
- `tests/test_api_decide.py`: 2 passed
- `scripts/api_sanity.py`: "API sanity passed."
- Full suite: 283 passed, 3 skipped

---

## Tests

| Test | File | Validates |
|------|------|-----------|
| `test_command_request_valid` | `tests/test_api_models.py` | AC-1 |
| `test_command_request_missing_field` | `tests/test_api_models.py` | AC-1 |
| `test_command_request_invalid_capability` | `tests/test_api_models.py` | AC-1 |
| `test_command_request_extra_field_rejected` | `tests/test_api_models.py` | AC-1 |
| `test_decision_response_valid` | `tests/test_api_models.py` | AC-2 |
| `test_decision_response_confidence_bounds` | `tests/test_api_models.py` | AC-2 |
| `test_decision_response_roundtrip` | `tests/test_api_models.py` | AC-2 |
| `test_command_context_nested_validation` | `tests/test_api_models.py` | AC-1 |
| `test_decide_rejects_invalid_command` (updated) | `tests/test_api_decide.py` | AC-4 |
| `test_decide_returns_valid_decision` | `tests/test_api_decide.py` | AC-3, AC-5 |
| Full regression (275 existing) | all test files | AC-6 |

---

## DoD Checklist

- [ ] `pydantic` added to `pyproject.toml` dependencies
- [ ] `app/models/__init__.py` created (empty)
- [ ] `app/models/api_models.py` created with all models
- [ ] `app/routes/decide.py` updated to use Pydantic models
- [ ] `tests/test_api_models.py` created with 8 tests
- [ ] `tests/test_api_decide.py` updated (422 error format)
- [ ] `scripts/api_sanity.py` still works
- [ ] All 8 new tests pass
- [ ] All 275 existing tests pass (283 total, 3 skipped)
- [ ] No modifications to forbidden paths

---

## Risks

| Risk | Mitigation |
|------|------------|
| Pydantic v1 vs v2 API differences | PLAN phase: check `pip show pydantic` version, use v2 API (`model_dump`, `model_validate`, `ConfigDict`) |
| Jsonschema validation fires on Pydantic-validated input | Keep as safety net; should never fire but doesn't hurt |
| DecisionResponse.model_validate rejects valid pipeline output | PLAN phase: test with real pipeline output dict; use `model_config = ConfigDict(extra="forbid")` only if schema has `additionalProperties: false` |
| datetime serialization format differs between Pydantic and manual | Use `str` for timestamp/created_at (not `datetime`) to avoid format mismatch |

---

## Rollback

Revert: restore `app/routes/decide.py` to raw dict version, remove `app/models/`, revert `pyproject.toml`, revert `tests/test_api_decide.py`, remove `tests/test_api_models.py`. Zero impact on internal pipeline.
