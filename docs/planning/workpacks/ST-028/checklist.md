# ST-028 Checklist

## Acceptance Criteria

- [ ] AC-1: Latency record emitted for every command (when enabled)
- [ ] AC-2: Steps non-negative, sum <= total_ms
- [ ] AC-3: No record when PIPELINE_LATENCY_LOG_ENABLED=false
- [ ] AC-4: llm_enabled reflects LLM_POLICY_ENABLED
- [ ] AC-5: Overhead < 1ms (time.monotonic only)
- [ ] AC-6: All 239 existing tests pass + 6 new = 245

## DoD Items

- [ ] `app/logging/pipeline_latency_log.py` created (follows existing pattern)
- [ ] `graphs/core_graph.py` updated with timing in `process_command()`
- [ ] Decision output unchanged (no behavioral change)
- [ ] `tests/test_pipeline_latency.py` — 6 new tests
- [ ] Core graph and graph execution tests still pass
- [ ] Full test suite passes (245 total)
