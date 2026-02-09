# Codex PLAN Prompt — ST-012: Enhanced missing_fields Detection

## Role

You are a read-only exploration agent. Do NOT create or edit any files.

## Environment

- Python binary: `python3` (NOT `python`)
- All tests: `python3 -m pytest tests/ -v`

## STOP-THE-LINE

If any finding contradicts the workpack assumptions, STOP and report the discrepancy.

---

## Context

Implementing ST-012: Enhanced missing_fields detection in baseline `validate_and_build()`.

**Goal:** Add `missing_fields` to 2 clarify triggers that currently pass `missing_fields=None`:
1. No `start_job` capability -> add `missing_fields=["capability.start_job"]`
2. Intent not detected -> add `missing_fields=["intent"]`

---

## Exploration Tasks

### Task 1: Verify validate_and_build() structure
```bash
sed -n '135,215p' routers/v2.py
```
Confirm: 5 clarify triggers, triggers #1 (line ~146) and #5 (line ~207) pass `missing_fields=None`.

### Task 2: Verify _clarify_question() behavior with None missing_fields
```bash
sed -n '217,225p' routers/v2.py
```
Confirm: when `missing_fields=None`, the subset check on line ~221-223 is skipped (because `if missing_fields and assist.clarify_missing_fields` is falsy). So adding `missing_fields` to these triggers will NOW activate the subset check for LLM hints.

### Task 3: Verify build_clarify_decision() in core_graph.py
```bash
sed -n '131,153p' graphs/core_graph.py
```
Confirm: `missing_fields` is optional param, added to payload only `if missing_fields` is truthy.

### Task 4: Verify decision schema clarify_payload
```bash
sed -n '162,178p' contracts/schemas/decision.schema.json
```
Confirm: `missing_fields` is optional array of strings. No enum constraint on values (any string allowed).

### Task 5: Check existing clarify tests
```bash
rg "missing_fields" tests/ --no-heading
```
Confirm: which tests assert on missing_fields and what values they expect.

### Task 6: Check test_assist_mode clarify test
```bash
sed -n '88,115p' tests/test_assist_mode.py
```
Confirm: `test_assist_clarify_rejects_mismatched_missing_fields` — this test sends empty text, so it triggers the "empty text" clarify (trigger #2 with `missing_fields=["text"]`). It should NOT be affected by our changes to triggers #1 and #5.

### Task 7: Verify conftest.py command fixtures
```bash
rg "capabilities" tests/conftest.py --no-heading
```
Confirm: all test fixtures include `"start_job"` in capabilities (so trigger #1 is not hit by existing tests).

### Task 8: Check if any test triggers "intent not detected" path
```bash
rg "Интент не распознан\|intent.*clarify\|unknown.*intent" tests/ --no-heading
```
Confirm: whether any existing test hits trigger #5.

### Task 9: Check test_graph_execution.py for clarify assertions
```bash
cat tests/test_graph_execution.py
```
Confirm: what clarify assertions exist and whether they check missing_fields.

### Task 10: Verify no other files reference missing_fields values
```bash
rg "capability\.start_job\|\"intent\".*missing" routers/ tests/ --no-heading
```
Confirm: our new field names don't collide with existing code.

---

## Expected Findings

1. Triggers #1 and #5 currently pass `missing_fields=None` — confirmed
2. Adding `missing_fields` to these triggers activates the `_clarify_question` subset gate for LLM hints — this is DESIRED behavior (LLM should only suggest fields that baseline identified)
3. No existing tests are broken because:
   - No existing test triggers #1 (all fixtures have `start_job` in capabilities)
   - No existing test triggers #5 and checks `missing_fields`
4. Schema allows any string in `missing_fields` array — no constraint violation

## Deliverable

Report findings for all 10 tasks. Highlight any STOP-THE-LINE issues.
