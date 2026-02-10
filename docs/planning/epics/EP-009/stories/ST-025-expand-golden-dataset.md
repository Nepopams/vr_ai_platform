# ST-025: Expand Golden Dataset to 20+ Commands

**Epic:** EP-009 (Golden Dataset and Quality Evaluation)
**Status:** Ready
**Flags:** contract_impact=no, adr_needed=none, diagrams_needed=none

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-009/epic.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q4-production-hardening.md` |
| Golden dataset | `skills/graph-sanity/fixtures/golden_dataset.json` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

The golden dataset at `skills/graph-sanity/fixtures/golden_dataset.json` has 14 entries
used by graph-sanity for deterministic validation. For quality evaluation (ST-026),
we need more entries covering all intents, edge cases, and multi-entity scenarios,
with expected outputs documented.

## User Value

As a platform developer, I want a golden dataset of at least 20 commands covering all
supported intents, edge cases, and multi-entity scenarios, so that quality evaluation
has meaningful coverage.

## Scope

### In scope

- Expand `skills/graph-sanity/fixtures/golden_dataset.json` from 14 to 20+ entries
- Add fields: `expected_llm_intent`, `expected_llm_entities`, `expected_action` (start_job/clarify), `difficulty` (easy/medium/hard)
- Add new cases: ambiguous commands, typos, mixed-language, multi-item with quantities
- Backward compatibility: existing fields remain, new fields are additive

### Out of scope

- Evaluation script (ST-026)
- LLM-specific golden answers
- Commands for intents beyond add_shopping_item, create_task, clarify_needed

---

## Acceptance Criteria

### AC-1: Dataset has 20+ entries
```
Given golden_dataset.json
When entries are counted
Then count >= 20
```

### AC-2: All intents represented
```
Given golden_dataset.json
When entries are grouped by expected_intent
Then add_shopping_item, create_task, and clarify_needed each have >= 3 entries
```

### AC-3: Edge cases present
```
Given golden_dataset.json
When entries with difficulty="hard" are filtered
Then count >= 3 (ambiguous, typo, multi-entity)
```

### AC-4: Backward compatible
```
Given existing tests using golden_dataset.json
When ST-025 changes are applied
Then all existing graph-sanity tests pass
```

### AC-5: All 228 existing tests pass

---

## Test Strategy

### Unit tests (~3 new)
- `test_golden_dataset_has_20_plus_entries`
- `test_golden_dataset_all_intents_represented`
- `test_golden_dataset_has_hard_cases`

### Regression
- Full test suite: 228 tests must pass (especially graph-sanity)

---

## Code Touchpoints

| File | Change |
|------|--------|
| `skills/graph-sanity/fixtures/golden_dataset.json` | Update: expand to 20+ entries |
| `tests/test_golden_dataset.py` | New: validation tests |

---

## Dependencies

- None (foundational story)
- Blocks: ST-026, ST-027
