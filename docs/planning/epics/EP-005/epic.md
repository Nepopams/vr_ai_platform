# EP-005: Improved Clarify Questions

**Status:** Done
**Initiative:** `docs/planning/initiatives/INIT-2026Q2-improved-clarify.md`
**Owner:** TBD

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q2-improved-clarify.md` |
| Contract schema (decision) | `contracts/schemas/decision.schema.json` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

The clarify pipeline currently works but has quality gaps:

1. **Baseline `missing_fields` are coarse** -- only 3 values: `text`, `item.name`, `task.title`. Real commands may have partial info (e.g., "купи что-нибудь в Ашане" -- has list hint but no item name). Richer field detection would enable smarter questions.

2. **LLM clarify prompt is minimal** -- `"Предложи один уточняющий вопрос и missing_fields"` gives no context about what's already known. A context-aware prompt would produce more relevant questions.

3. **No clarify quality measurement** -- no ground truth in golden dataset for what the "right" clarify question is. Cannot measure improvement without a baseline metric.

4. **Safety rules are basic** -- `_clarify_question_is_safe` checks length, echo-prevention, and intent match. Could add more nuanced filtering (e.g., question relevance to detected missing_fields).

**What already works (from S01 assist-mode delivery):**
- LLM clarify hint generation (`_run_clarify_hint`)
- Safety gate (`_clarify_question_is_safe`)
- Subset validation in `_clarify_question()` (LLM can't introduce new missing_fields)
- Logging to `assist.jsonl` (step=clarify, accepted/rejected, latency)
- Feature flag gating (`ASSIST_CLARIFY_ENABLED`)

**Contract compatibility:** `clarify_payload` already has `question`, `missing_fields`, `options` fields. No schema changes needed.

## Goal

Improve clarify question quality so that:
1. Baseline detects more nuanced missing_fields based on what IS and ISN'T present
2. LLM generates context-aware questions that reference what's known
3. Improvement is measurable via golden dataset ground truth
4. All improvements are safe (deterministic fallback, no raw text leaks)

## Scope

### In scope

- Enhanced `missing_fields` detection in `validate_and_build()` -- detect partial info (list known but not item, item known but not list, intent unclear, etc.)
- Context-aware LLM clarify prompt -- pass already-known fields so LLM asks about what's MISSING, not everything
- Golden dataset clarify ground truth -- expected `missing_fields` and question quality annotations for clarify fixtures
- Clarify quality measurement script -- compare actual vs expected missing_fields, count match rate
- Refined safety rules -- align `_clarify_question_is_safe` with richer missing_fields

### Out of scope

- UI dialog manager (product-layer responsibility)
- Multi-turn conversation state (no memory between requests)
- Changes to `clarify_payload` contract schema (already sufficient)
- Partial trust corridor changes (EP-003 done, not touched)
- Multi-item extraction changes (EP-004 done, not touched)
- Changes to shadow router
- New feature flags beyond existing `ASSIST_CLARIFY_ENABLED`

## Stories

| Story ID | Title | Status | Flags |
|----------|-------|--------|-------|
| [ST-012](stories/ST-012-enhanced-missing-fields.md) | Enhanced missing_fields detection in baseline | Done (7668eed) | contract_impact=no, adr_needed=none |
| [ST-013](stories/ST-013-context-aware-clarify-prompt.md) | Context-aware LLM clarify prompt and safety refinement | Done (13a6438) | contract_impact=no, adr_needed=none |
| [ST-014](stories/ST-014-clarify-golden-dataset-measurement.md) | Clarify golden dataset ground truth and quality measurement | Done (ad156b8) | contract_impact=no, adr_needed=none |

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| EP-004 (Multi-Entity Extraction) | Internal | Done -- multi-item `missing_fields` are stable |
| EP-002 (Assist Mode) | Internal | Done -- clarify hint pipeline is stable |
| `contracts/schemas/decision.schema.json` supports clarify | Contract | Done (clarify_payload already has question + missing_fields + options) |
| Existing test suite passes (176 tests) | Internal | Verified |

### Story ordering

```
ST-012 (enhanced missing_fields)
  |
  +-------+-------+
  v               v
ST-013          ST-014
(LLM prompt)   (measurement)
```

- ST-012 must be completed first (enriches the missing_fields that ST-013 and ST-014 consume).
- ST-013 and ST-014 are independent and can run in parallel after ST-012.
- ST-014 should be reviewed last (measures the combined effect of ST-012 + ST-013).

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Enhanced missing_fields break existing clarify tests | Low | Medium | ST-012 must pass all 176 existing tests. New fields are additive -- existing triggers unchanged. |
| LLM clarify prompt changes degrade question quality | Low | Medium | Safety gate (`_clarify_question_is_safe`) remains. Fallback to default question always available. Feature flag gating. |
| Golden dataset ground truth is subjective | Medium | Low | Use objective criteria: missing_fields match rate (mechanical), not question text quality (subjective). |
| Changes to `_clarify_question_is_safe` allow unsafe questions | Low | High | Echo-prevention and length limits remain non-negotiable. Only add relevance checks, don't relax safety. |

## Readiness Report

### Ready
- **ST-012** -- No blockers. All DoR criteria met. Foundation story.
- **ST-013** -- DoR met. Managed dependency on ST-012 (execution order).
- **ST-014** -- DoR met. Managed dependency on ST-012 (execution order).
