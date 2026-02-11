# Codex PLAN Prompt — ST-032: Pydantic Models for CommandDTO and DecisionDTO

## Role

You are a senior Python/FastAPI developer performing a **read-only exploration** of the codebase to gather facts needed for implementing Pydantic request/response models.

## Rules

- **NO file edits, NO file creation, NO writes of any kind.**
- Only use: `ls`, `find`, `cat`, `rg`/`grep`, `sed -n`, `head`, `tail`, `git status`, `git diff`
- If you discover something that contradicts the plan below → **STOP and report it** (STOP-THE-LINE)

## Context

We are introducing Pydantic models for the API boundary. Currently `app/routes/decide.py` uses raw `request.json()` + `Dict[str, Any]`. We need Pydantic models that mirror `command.schema.json` and `decision.schema.json`, then update the route handler to use them. Internal pipeline stays dict-based.

## Tasks

### Task 1: Confirm Pydantic version available
```bash
pip show pydantic 2>/dev/null || python3 -c "import pydantic; print(pydantic.__version__)"
```
We need to know if it's v1 or v2 (affects API: `model_dump` vs `dict`, `model_validate` vs `parse_obj`, `ConfigDict` vs `class Config`).

### Task 2: Read command.schema.json in full
```bash
cat contracts/schemas/command.schema.json
```
Map every field, nested type, required/optional, enum values, and constraints (minItems, additionalProperties).

### Task 3: Read decision.schema.json in full
```bash
cat contracts/schemas/decision.schema.json
```
Map all 11 required fields, payload definitions, allOf/oneOf structure. Focus on whether payload sub-models are needed at the Pydantic level or if `Dict[str, Any]` is sufficient.

### Task 4: Read current decide route handler
```bash
cat app/routes/decide.py
```
Confirm exact error handling flow. Map which exceptions are caught and what HTTP codes are returned.

### Task 5: Read decision_service.py
```bash
cat app/services/decision_service.py
```
Confirm: `decide()` accepts `Dict[str, Any]`, returns `Dict[str, Any]`. The jsonschema validation calls. The `CommandValidationError` class.

### Task 6: Test what a real pipeline output dict looks like
```bash
rg "decision_id" tests/ --files-with-matches
```
Then read a test that creates/asserts a decision dict to see all actual fields returned by the pipeline. This tells us if `DecisionResponse.model_validate(decision_dict)` will work.

### Task 7: Check test_api_decide.py error assertion
```bash
cat tests/test_api_decide.py
```
Confirm: `test_decide_rejects_invalid_command` asserts status 400 and specific error body. We need to update this to 422 + Pydantic format.

### Task 8: Check if app/models/ directory exists
```bash
ls -la app/models/ 2>/dev/null || echo "DOES NOT EXIST"
ls -la app/__init__.py 2>/dev/null || echo "NO APP INIT"
```

### Task 9: Check scripts/api_sanity.py
```bash
cat scripts/api_sanity.py
```
Confirm it sends valid JSON and only checks status 200 + jsonschema validation on response. Should still work after Pydantic migration.

### Task 10: Check pyproject.toml packages.find
```bash
cat pyproject.toml
```
Confirm `app*` is in `packages.find.include` (so `app.models` will be discovered).

## Expected Output

For each task, report:
1. What you found (exact values, versions, patterns)
2. Any deviations from expectations
3. Any STOP-THE-LINE issues

## STOP-THE-LINE Triggers

- Pydantic version is v1 only (no v2 available) — would need different API
- `decide()` returns something other than `Dict[str, Any]`
- Decision dict has fields NOT in `decision.schema.json` (model_validate would fail with `extra="forbid"`)
- `app/` is not a proper package (no `__init__.py` anywhere in chain)
