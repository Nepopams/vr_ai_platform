# ST-026: Quality Evaluation Script with Metrics

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

ST-025 expands the golden dataset. This story creates the evaluation script that
runs commands through the pipeline and computes quality metrics.

## User Value

As a platform developer, I want a script that runs all golden dataset commands through
the pipeline (deterministic and LLM-assisted), compares results against expected answers,
and outputs quality metrics, so that I have a reproducible quality assessment.

## Scope

### In scope

- New script: `skills/quality-eval/scripts/evaluate_golden.py`
- Runs each golden dataset command through:
  1. Deterministic pipeline only (`process_command`)
  2. LLM-assisted pipeline (if `LLM_POLICY_ENABLED`)
- Computes metrics:
  - Intent accuracy (deterministic vs LLM vs expected)
  - Entity precision and recall (item names)
  - Clarify rate (% of commands resulting in clarify)
  - Overall start_job rate
- Output: JSON report to stdout and/or file
- Works in stub mode (LLM disabled): evaluates deterministic-only
- Works in real mode (LLM enabled): evaluates both and shows comparison

### Out of scope

- CI integration (ST-027)
- Automated pass/fail thresholds
- LLM performance benchmarks (latency is EP-010)

---

## Acceptance Criteria

### AC-1: Script produces metrics for deterministic pipeline
```
Given LLM_POLICY_ENABLED=false
When evaluate_golden.py runs
Then report contains: intent_accuracy_deterministic, entity_precision_deterministic,
     entity_recall_deterministic, clarify_rate_deterministic, start_job_rate_deterministic
```

### AC-2: Script produces comparison when LLM enabled
```
Given LLM_POLICY_ENABLED=true, LLM_API_KEY set
When evaluate_golden.py runs
Then report contains metrics for both "deterministic" and "llm_assisted" columns
And a "delta" section showing improvement/regression per metric
```

### AC-3: Report is valid JSON
```
Given evaluate_golden.py output
When parsed
Then it is valid JSON
```

### AC-4: Works with expanded golden dataset
```
Given 20+ entries in golden_dataset.json
When evaluate_golden.py runs (stub mode)
Then all entries are evaluated without errors
```

### AC-5: All 228 existing tests pass

---

## Test Strategy

### Unit tests (~6 new in `tests/test_quality_eval.py`)
- `test_evaluate_deterministic_only`
- `test_intent_accuracy_computation`
- `test_entity_precision_recall`
- `test_clarify_rate_computation`
- `test_report_valid_json`
- `test_empty_dataset_no_crash`

### Regression
- Full test suite: 228 tests must pass

---

## Code Touchpoints

| File | Change |
|------|--------|
| `skills/quality-eval/scripts/evaluate_golden.py` | New: evaluation script |
| `tests/test_quality_eval.py` | New: unit tests |

---

## Dependencies

- ST-025 (golden dataset must be expanded)
- Blocks: ST-027
