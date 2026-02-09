# Codex PLAN Prompt — ST-013: Context-Aware LLM Clarify Prompt

## Role

You are a read-only exploration agent. Do NOT create or edit any files.

## Environment

- Python binary: `python3` (NOT `python`)

## STOP-THE-LINE

If any finding contradicts the workpack assumptions, STOP and report.

---

## Context

Implementing ST-013: Context-aware LLM clarify prompt and safety refinement in `routers/assist/runner.py`.

**Changes planned:**
1. `_CLARIFY_SCHEMA` — add enum constraint on `missing_fields` items
2. `_run_clarify_hint()` — add `normalized` parameter
3. `_build_clarify_prompt()` — include known/missing context
4. `_build_assist_hints()` — pass `normalized` to `_run_clarify_hint()`
5. `_clarify_question_is_safe()` — add optional relevance check

---

## Exploration Tasks

### Task 1: Verify _CLARIFY_SCHEMA current structure
```bash
sed -n '87,96p' routers/assist/runner.py
```
Confirm: missing_fields has no enum constraint, just `{"type": "array", "items": {"type": "string"}}`.

### Task 2: Verify _run_clarify_hint signature and body
```bash
sed -n '302,326p' routers/assist/runner.py
```
Confirm: takes `(text, intent)`, no `normalized` param. Returns ClarifyHint.

### Task 3: Verify _build_clarify_prompt signature and body
```bash
sed -n '578,585p' routers/assist/runner.py
```
Confirm: takes `(text, intent)`, no context about known/missing fields.

### Task 4: Verify _build_assist_hints call to _run_clarify_hint
```bash
sed -n '123,143p' routers/assist/runner.py
```
Confirm: calls `_run_clarify_hint(command.get("text", ""), normalized.get("intent"))`. Has access to `normalized` dict.

### Task 5: Verify _clarify_question_is_safe full body
```bash
sed -n '628,641p' routers/assist/runner.py
```
Confirm: 5 checks (non-empty, len<5, len>200, echo, intent/question-mark). No relevance check.

### Task 6: Check _select_clarify_hint for any missing_fields usage
```bash
sed -n '505,524p' routers/assist/runner.py
```
Confirm: calls `_clarify_question_is_safe(question, intent, original_text)` — no missing_fields param passed.

### Task 7: Verify ClarifyHint type in types.py
```bash
rg "class ClarifyHint" routers/assist/types.py -A 10
```
Confirm: fields are `question, missing_fields, confidence, error_type, latency_ms`.

### Task 8: Check existing test_assist_mode clarify tests
```bash
sed -n '88,115p' tests/test_assist_mode.py
```
Confirm: `test_assist_clarify_rejects_mismatched_missing_fields` mocks `_run_clarify_hint` with `lambda _text, _intent:`. After our change, signature becomes `(text, intent, normalized)` — this mock needs updating.

### Task 9: Check all callers of _run_clarify_hint
```bash
rg "_run_clarify_hint" routers/assist/runner.py tests/ --no-heading
```
Confirm: called only in `_build_assist_hints` and mocked in test files. List all mocks.

### Task 10: Check all callers of _clarify_question_is_safe
```bash
rg "_clarify_question_is_safe" routers/assist/runner.py tests/ --no-heading
```
Confirm: called only in `_select_clarify_hint`. List any test mocks.

### Task 11: Verify _log_step for clarify
```bash
rg "_log_step.*clarify" routers/assist/runner.py --no-heading
```
Confirm: what data is logged for clarify step. Ensure we know where NOT to put raw text.

### Task 12: Check the known missing_fields vocabulary (from ST-012)
```bash
rg "missing_fields=" routers/v2.py --no-heading
```
Confirm: complete list of field identifiers used: `["text"]`, `["item.name"]`, `["task.title"]`, `["capability.start_job"]`, `["intent"]`.

---

## Expected Findings

1. `_CLARIFY_SCHEMA` missing_fields is unconstrained — will add enum
2. `_run_clarify_hint(text, intent)` — will add `normalized` param
3. `_build_clarify_prompt(text, intent)` — will add `normalized` and build context string
4. `_build_assist_hints` has `normalized` in scope — just pass it through
5. `_clarify_question_is_safe(question, intent, original_text)` — will add optional `missing_fields` param for relevance
6. Mock in `test_assist_mode.py` line ~102 uses `lambda _text, _intent:` — MUST be updated to `lambda _text, _intent, _normalized=None:`
7. Known vocabulary: `text`, `item.name`, `item.list_id`, `task.title`, `capability.start_job`, `intent`

## Deliverable

Report findings for all 12 tasks. Highlight STOP-THE-LINE issues, especially about mocks in existing tests.
