# Workpack: ST-013 — Context-Aware LLM Clarify Prompt and Safety Refinement

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Story spec | `docs/planning/epics/EP-005/stories/ST-013-context-aware-clarify-prompt.md` |
| Contract schema | `contracts/schemas/decision.schema.json` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

Make the LLM clarify prompt context-aware (tells LLM what's known and what's missing), constrain `_CLARIFY_SCHEMA` missing_fields to known vocabulary, and add a relevance check to `_clarify_question_is_safe`.

## Current State

### `_build_clarify_prompt()` (runner.py:578-585)
```python
def _build_clarify_prompt(text: str, intent: Optional[str]) -> str:
    intent_label = intent or "unknown"
    return (
        "Предложи один уточняющий вопрос и missing_fields. "
        "Вопрос должен быть конкретным и релевантным.\n"
        f"Интент: {intent_label}\n"
        f"Текст: {text}"
    )
```
- No context about what's already known (items, list, task_title)
- No context about what's missing (missing_fields from baseline)
- No missing_fields vocabulary constraint

### `_run_clarify_hint()` (runner.py:302-326)
- Signature: `_run_clarify_hint(text: str, intent: Optional[str])`
- No `normalized` or `missing_fields` parameter

### `_build_assist_hints()` (runner.py:123-143)
- Calls: `_run_clarify_hint(command.get("text", ""), normalized.get("intent"))`
- Has access to `normalized` but doesn't pass it

### `_CLARIFY_SCHEMA` (runner.py:87-96)
- `missing_fields` is unconstrained `array of string`

### `_clarify_question_is_safe()` (runner.py:628-640)
- Checks: non-empty, length 5-200, no echo, intent whitelist or "?"
- No relevance check against missing_fields

---

## Acceptance Criteria

- AC-1: Clarify prompt includes known/missing context
- AC-2: `_CLARIFY_SCHEMA` constrains missing_fields to known vocabulary
- AC-3: Safety gate adds relevance check
- AC-5: Backward compat with assist disabled
- AC-6: No raw text in logs
- AC-7: All 182 existing tests pass

---

## Files to Change

| File | Action |
|------|--------|
| `routers/assist/runner.py` | Edit `_build_clarify_prompt()`, `_run_clarify_hint()`, `_build_assist_hints()`, `_CLARIFY_SCHEMA`, `_clarify_question_is_safe()` |
| `tests/test_clarify_prompt.py` | Create new test file |

---

## Implementation Plan

### Step 1: Update `_CLARIFY_SCHEMA` to constrain missing_fields vocabulary

### Step 2: Update `_run_clarify_hint()` to accept `normalized` dict

### Step 3: Update `_build_clarify_prompt()` to include known/missing context

### Step 4: Update `_build_assist_hints()` to pass `normalized` to `_run_clarify_hint()`

### Step 5: Add relevance check to `_clarify_question_is_safe()`

### Step 6: Create `tests/test_clarify_prompt.py`

---

## Verification Commands

```bash
# 1. New tests
python3 -m pytest tests/test_clarify_prompt.py -v

# 2. Full test suite
python3 -m pytest tests/ -v

# 3. No secrets
grep -rn 'sk-\|api_key' routers/assist/runner.py tests/test_clarify_prompt.py
```

---

## Invariants (DO NOT break)

- `graphs/core_graph.py` — NOT modified
- `contracts/schemas/decision.schema.json` — NOT modified
- `routers/v2.py` — NOT modified
- Existing `_clarify_question_is_safe` safety rules (non-empty, length, echo-prevention) — NOT removed, only added to
- `apply_assist_hints()` return type — unchanged
- Logging: no raw text in assist.jsonl
