# ST-012: Enhanced missing_fields Detection in Baseline

**Epic:** EP-005 (Improved Clarify Questions)
**Status:** Ready
**Flags:** contract_impact=no, adr_needed=none, diagrams_needed=none

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-005/epic.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q2-improved-clarify.md` |
| Contract schema | `contracts/schemas/decision.schema.json` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

Currently `validate_and_build()` in `routers/v2.py` sets `missing_fields` in only 3 coarse cases:

| Trigger | missing_fields | Gap |
|---------|---------------|-----|
| Empty text | `["text"]` | OK |
| Shopping intent, no item | `["item.name"]` | Doesn't distinguish "no items at all" from "has list but no item name" |
| Task intent, no title | `["task.title"]` | Doesn't distinguish partial info |
| No start_job capability | None | Could indicate `["capability.start_job"]` |
| Intent not detected | None | Could indicate `["intent"]` |

Richer `missing_fields` would let:
1. The LLM prompt (ST-013) know what's already known
2. The product layer render smarter follow-up UI
3. Measurement (ST-014) compare actual vs expected fields

## User Value

As a product developer using the AI Platform, I want clarify decisions to include specific `missing_fields` that tell me exactly what information is missing, so I can build targeted follow-up UX instead of generic "please clarify" dialogs.

## Scope

### In scope

- Enrich `missing_fields` in `validate_and_build()` for all 5 clarify triggers
- Add context-aware field detection: if shopping intent is detected but items list is empty, include `["item.name"]`; if items exist but no list_id resolvable, include `["item.list_id"]`
- Pass `missing_fields` to `_clarify_question()` for all clarify paths (already done for 3/5)
- Unit tests for each enriched trigger
- Backward compatibility: existing clarify behavior unchanged for existing triggers

### Out of scope

- LLM prompt changes (ST-013)
- Golden dataset ground truth (ST-014)
- Changes to `clarify_payload` contract schema
- New feature flags

---

## Acceptance Criteria

### AC-1: Intent not detected -> missing_fields includes "intent"
```
Given a command with unrecognized intent (e.g., "Что-то про погоду")
When V2 router processes the command
Then the clarify decision includes missing_fields=["intent"]
And the question is the default "Уточните, что нужно сделать: задача или покупка?"
```

### AC-2: No start_job capability -> missing_fields includes "capability.start_job"
```
Given a command without "start_job" in capabilities
When V2 router processes the command
Then the clarify decision includes missing_fields=["capability.start_job"]
```

### AC-3: Shopping intent, items present but no list_id resolvable -> missing_fields includes "item.list_id"
```
Given a command "Купи молоко" with context that has NO shopping_lists
When V2 router processes the command
Then the decision is start_job (item extraction still works)
But if no default_list_id is available, the proposed_action item has no list_id field
```

Note: This AC is informational -- we detect the gap but don't block start_job. The `missing_fields` enrichment applies only to actual clarify triggers.

### AC-4: Empty text -> missing_fields still ["text"] (backward compat)
```
Given a command with empty text
When V2 router processes the command
Then the clarify decision includes missing_fields=["text"]
(unchanged from current behavior)
```

### AC-5: Shopping intent, no items AND no item_name -> missing_fields=["item.name"]
```
Given a command detected as add_shopping_item but extraction returns no items
When V2 router processes the command
Then the clarify decision includes missing_fields=["item.name"]
(unchanged from current behavior)
```

### AC-6: Task intent, no title -> missing_fields=["task.title"] (backward compat)
```
Given a command detected as create_task but no title extracted
When V2 router processes the command
Then the clarify decision includes missing_fields=["task.title"]
(unchanged from current behavior)
```

### AC-7: All 176 existing tests pass
```
Given the current test suite of 176 tests
When ST-012 changes are applied
Then all 176 tests pass without modification
```

---

## Test Strategy

### Unit tests (~6 new tests)
- `test_clarify_missing_fields_intent_unknown` -- AC-1
- `test_clarify_missing_fields_no_capability` -- AC-2
- `test_clarify_missing_fields_empty_text_backward_compat` -- AC-4
- `test_clarify_missing_fields_no_item_backward_compat` -- AC-5
- `test_clarify_missing_fields_no_task_title_backward_compat` -- AC-6
- `test_clarify_missing_fields_all_present_start_job` -- verify start_job path doesn't include missing_fields

### Regression
- Full test suite: 176 tests must pass

---

## Code Touchpoints

| File | Change |
|------|--------|
| `routers/v2.py` | `validate_and_build()` -- enrich `missing_fields` for 2 triggers that currently pass None |
| `tests/test_clarify_missing_fields.py` | New file: unit tests for enriched missing_fields |

---

## Dependencies

- None (foundation story)
- Blocks: ST-013, ST-014
