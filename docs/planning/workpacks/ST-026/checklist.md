# ST-026 Checklist

## Acceptance Criteria

- [ ] AC-1: Deterministic metrics produced (intent_accuracy, entity_precision, entity_recall, clarify_rate, start_job_rate)
- [ ] AC-2: LLM comparison with deterministic + llm_assisted + delta sections
- [ ] AC-3: Report is valid JSON
- [ ] AC-4: All 22 golden dataset entries evaluated without errors
- [ ] AC-5: All 256 existing tests pass + 6 new = 262

## DoD Items

- [ ] `skills/quality-eval/scripts/evaluate_golden.py` created
- [ ] Script loads golden_dataset.json and fixtures from `skills/graph-sanity/fixtures/`
- [ ] Computes 5 metrics: intent_accuracy, entity_precision, entity_recall, clarify_rate, start_job_rate
- [ ] Entity matching uses `extract_items` from core_graph (case-insensitive)
- [ ] LLM comparison: duplicates metrics when LLM enabled, delta section
- [ ] JSON report to stdout
- [ ] `tests/test_quality_eval.py` — 6 new tests
- [ ] Full test suite passes (262 total)
