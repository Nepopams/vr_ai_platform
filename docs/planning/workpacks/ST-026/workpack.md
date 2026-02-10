# Workpack — ST-026: Quality Evaluation Script with Metrics

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-009/epic.md` |
| Story | `docs/planning/epics/EP-009/stories/ST-026-quality-evaluation-script.md` |
| Golden dataset | `skills/graph-sanity/fixtures/golden_dataset.json` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

A reproducible evaluation script that runs all golden dataset entries through the
deterministic pipeline, computes quality metrics (intent accuracy, entity precision/recall,
clarify rate, start_job rate), and outputs a valid JSON report.

## Acceptance Criteria

- AC-1: Script produces deterministic metrics (intent_accuracy, entity_precision,
  entity_recall, clarify_rate, start_job_rate) when LLM disabled
- AC-2: Script produces comparison with "deterministic" and "llm_assisted" columns
  when LLM enabled, plus "delta" section
- AC-3: Report is valid JSON
- AC-4: All 22 golden dataset entries evaluated without errors in stub mode
- AC-5: All 256 existing tests pass + 6 new = 262

---

## Architecture Decisions

### Entity evaluation approach

`process_command` uses `extract_item_name` (returns single string for all items).
Golden dataset has `expected_item_names` as a list of individual items.

**Decision**: Use `extract_items` from `core_graph` for entity evaluation — it splits
items properly and exists in the codebase. This measures the entity extraction
CAPABILITY, not just what process_command currently returns as a single string.

### LLM-assisted evaluation

`process_command` is currently always deterministic. When `LLM_POLICY_ENABLED=true`,
the script runs the same pipeline but reports results in both "deterministic" and
"llm_assisted" columns (identical for now), with delta=0. This structures the output
for future LLM integration without requiring actual LLM calls.

---

## Files to Change

| File | Action | Description |
|------|--------|-------------|
| `skills/quality-eval/scripts/evaluate_golden.py` | NEW | Evaluation script |
| `tests/test_quality_eval.py` | NEW | 6 unit tests |

## Files NOT Modified (invariants)

- `graphs/core_graph.py` — DO NOT CHANGE
- `skills/graph-sanity/**` — DO NOT CHANGE
- `llm_policy/**` — DO NOT CHANGE
- `tests/test_golden_dataset_validation.py` — DO NOT CHANGE
- `tests/test_core_graph_registry_gate.py` — DO NOT CHANGE

---

## Implementation Plan

### Step 1: Create `skills/quality-eval/scripts/evaluate_golden.py`

Functions:

1. **`load_golden_dataset(path)`** — load and return list from JSON
2. **`load_fixture_command(fixture_dir, filename)`** — load single command fixture
3. **`evaluate_entry(entry, fixture_dir)`** — run one golden entry:
   - Load fixture command
   - Run `process_command(command)` → decision
   - Call `detect_intent(text)` for actual intent
   - Determine actual_action from decision:
     - If `decision["action"] == "clarify"` → `"clarify"`
     - Else: `decision["payload"]["proposed_actions"][0]["action"]`
   - Call `extract_items(text)` for actual item names
   - Return result dict
4. **`compute_metrics(results)`** — aggregate:
   - `intent_accuracy`: fraction of `intent_match == True`
   - `entity_precision`: TP / (TP + FP) across entries with `expected_item_names`
   - `entity_recall`: TP / (TP + FN) across entries with `expected_item_names`
   - `clarify_rate`: fraction of `actual_action == "clarify"`
   - `start_job_rate`: fraction of `actual_action != "clarify"`
   - Entity matching: case-insensitive exact match on item name strings
5. **`build_report(deterministic_metrics, llm_metrics=None)`** — build report dict:
   - Always includes `"deterministic"` key
   - If `llm_metrics` provided: add `"llm_assisted"` and `"delta"` keys
6. **`main()`** — CLI entrypoint:
   - Load golden dataset
   - Run evaluate_entry for each
   - Compute metrics
   - If `LLM_POLICY_ENABLED=true`: duplicate as llm_assisted
   - Output JSON to stdout

### Step 2: Create `tests/test_quality_eval.py`

6 tests using synthetic result dicts (no process_command dependency):

1. `test_compute_metrics_deterministic` — 3 synthetic results → check all 5 metrics
2. `test_intent_accuracy_computation` — 4 results with known matches → verify fraction
3. `test_entity_precision_recall` — results with item names → verify TP/FP/FN
4. `test_clarify_rate_computation` — results with mix of clarify/start_job
5. `test_report_valid_json` — build_report output is json-serializable
6. `test_empty_dataset_no_crash` — empty list → all metrics 0.0, total_entries 0

---

## Verification Commands

```bash
# New evaluation tests
source .venv/bin/activate && python3 -m pytest tests/test_quality_eval.py -v

# Run evaluation script in stub mode
source .venv/bin/activate && python3 skills/quality-eval/scripts/evaluate_golden.py

# Full test suite
source .venv/bin/activate && python3 -m pytest --tb=short -q
```

---

## DoD Checklist

- [ ] `evaluate_golden.py` created with metric computation
- [ ] Script runs all 22 golden entries without errors
- [ ] Report is valid JSON with correct metric keys
- [ ] `test_quality_eval.py` — 6 new tests
- [ ] Full test suite passes (262 total)
- [ ] No code files modified outside touchpoints

---

## Risks

| Risk | Mitigation |
|------|-----------|
| process_command side effects (log files) | Tests use tmp_path + monkeypatch for log paths |
| Import path for skills script in tests | Add script dir to sys.path in test module |
| Entity matching edge cases (typos, etc.) | Case-insensitive exact match, document as limitation |

## Rollback

Remove 2 new files. No impact on existing code.
