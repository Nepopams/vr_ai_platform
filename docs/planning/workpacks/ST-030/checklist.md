# ST-030 Checklist

## Acceptance Criteria

- [ ] AC-1: p50/p95/p99 for total_ms and per-step
- [ ] AC-2: fallback_rate, error_rate, success_rate as decimals [0..1]
- [ ] AC-3: Separate latency stats for "with_llm" and "without_llm"
- [ ] AC-4: Empty logs → zero counts and null percentiles (no crash)
- [ ] AC-5: All 262 existing tests pass + 6 new = 268

## DoD Items

- [ ] `skills/observability/scripts/aggregate_metrics.py` created
- [ ] Reads pipeline_latency.jsonl and fallback_metrics.jsonl
- [ ] Percentile computation via linear interpolation
- [ ] LLM comparison split by llm_enabled field
- [ ] Outcome-based rate computation (success/fallback/error)
- [ ] JSON report to stdout
- [ ] `tests/test_aggregate_metrics.py` — 6 new tests
- [ ] Full test suite passes (268 total)
