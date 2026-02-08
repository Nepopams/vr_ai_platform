# ST-013: Context-Aware LLM Clarify Prompt and Safety Refinement

**Epic:** EP-005 (Improved Clarify Questions)
**Status:** Ready (dep: ST-012)
**Flags:** contract_impact=no, adr_needed=none, diagrams_needed=none

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-005/epic.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q2-improved-clarify.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

The current LLM clarify prompt in `routers/assist/runner.py` is minimal:

```
"Предложи один уточняющий вопрос и missing_fields. "
"Вопрос должен быть конкретным и релевантным.\n"
f"Интент: {intent_label}\n"
f"Текст: {text}"
```

It doesn't tell the LLM:
- What fields are already extracted (items, task_title, list info)
- What fields are missing (from ST-012 enhanced detection)
- What the acceptable missing_fields vocabulary is

This leads to generic questions like "Что именно нужно сделать?" when a more targeted question like "В какой список добавить молоко?" would be better.

The safety gate `_clarify_question_is_safe` also doesn't check whether the question is relevant to the detected missing_fields.

## User Value

As a user of HomeTusk, I want the clarify question to be specific and relevant to what I forgot to say, so I can answer in one response instead of multiple rounds.

## Scope

### In scope

- Update `_build_clarify_prompt()` to include known/missing field context
- Pass `missing_fields` (from ST-012) into the clarify hint pipeline
- Add relevance check to `_clarify_question_is_safe` -- question should relate to missing_fields
- Update `_CLARIFY_SCHEMA` to constrain `missing_fields` to known vocabulary
- Unit tests for new prompt construction and safety rules
- Logging: include `prompt_context` field count in assist log (no raw text)

### Out of scope

- Changes to `validate_and_build()` (done in ST-012)
- Changes to `clarify_payload` contract schema
- Multi-turn conversation
- New feature flags

---

## Acceptance Criteria

### AC-1: Clarify prompt includes known fields context
```
Given a shopping command where item_name="молоко" but no list is resolvable
When _build_clarify_prompt is called
Then the prompt includes information about what is already known (intent, items)
And the prompt includes what is missing (from missing_fields)
```

### AC-2: Clarify prompt constrains missing_fields vocabulary
```
Given the LLM clarify schema
When LLM returns missing_fields
Then the schema restricts items to known field identifiers: ["text", "intent", "item.name", "item.list_id", "task.title", "capability.start_job"]
```

### AC-3: Safety gate checks question relevance
```
Given a clarify hint with question "Какая погода завтра?" and missing_fields=["item.name"]
When _clarify_question_is_safe evaluates
Then the question is rejected (irrelevant to missing shopping item)
```

### AC-4: Context-aware prompt produces better questions (manual verification)
```
Given command "Купи что-нибудь" (shopping intent, no specific item)
When LLM clarify hint is generated with context-aware prompt
Then the question should reference what's missing (item name)
Rather than asking a generic "Что нужно сделать?"
```

### AC-5: Backward compatibility with assist disabled
```
Given ASSIST_CLARIFY_ENABLED=false
When V2 router processes a clarify-triggering command
Then default baseline questions are used (unchanged)
And all existing tests pass
```

### AC-6: No raw text in logs
```
Given any clarify hint processing
When assist log is written
Then no raw user text or LLM question text appears in log
Only field counts and error types
```

### AC-7: All existing tests pass (176+ from ST-012)
```
Given the test suite after ST-012
When ST-013 changes are applied
Then all tests pass without modification
```

---

## Test Strategy

### Unit tests (~8 new tests)
- `test_clarify_prompt_includes_known_fields` -- AC-1
- `test_clarify_prompt_includes_missing_fields` -- AC-1
- `test_clarify_schema_constrains_vocabulary` -- AC-2
- `test_safety_rejects_irrelevant_question` -- AC-3
- `test_safety_accepts_relevant_question` -- AC-3
- `test_safety_backward_compat_rules` -- existing rules unchanged
- `test_assist_disabled_uses_default` -- AC-5
- `test_clarify_log_no_raw_text` -- AC-6

### Regression
- Full test suite must pass

---

## Code Touchpoints

| File | Change |
|------|--------|
| `routers/assist/runner.py` | `_build_clarify_prompt()` -- add known/missing context; `_clarify_question_is_safe()` -- add relevance check; `_CLARIFY_SCHEMA` -- constrain missing_fields enum; `_run_clarify_hint()` -- accept missing_fields parameter |
| `routers/assist/runner.py` | `_build_assist_hints()` / `apply_assist_hints()` -- pass missing_fields context to clarify hint |
| `tests/test_clarify_prompt.py` | New file: unit tests for prompt construction and safety |

---

## Dependencies

- ST-012 (enhanced missing_fields) must be completed first -- provides the richer field vocabulary
- Blocks: none (ST-014 is independent)
