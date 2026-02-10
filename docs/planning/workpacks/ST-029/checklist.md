# ST-029 Checklist

## Acceptance Criteria

- [ ] AC-1: Record emitted for every process_command call (when enabled)
- [ ] AC-2: Log module records success outcome correctly
- [ ] AC-3: Log module records fallback outcome with reason
- [ ] AC-4: llm_outcome="skipped" when LLM disabled
- [ ] AC-5: No raw user text or LLM output in records
- [ ] AC-6: All 245 existing tests pass + 6 new = 251

## DoD Items

- [ ] `app/logging/fallback_metrics_log.py` created (follows existing pattern)
- [ ] `graphs/core_graph.py` updated — fallback metrics emission added
- [ ] Privacy guarantee: no raw text/prompt/LLM output fields
- [ ] Decision output unchanged
- [ ] `tests/test_fallback_metrics.py` — 6 new tests
- [ ] Latency tests (ST-028) still pass
- [ ] Full test suite passes (251 total)
