# Workpack — ST-030: Latency and Fallback Summary Aggregation Script

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-010/epic.md` |
| Story | `docs/planning/epics/EP-010/stories/ST-030-aggregation-script.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

A standalone aggregation script that reads pipeline_latency.jsonl and
fallback_metrics.jsonl, computes percentile latencies (p50/p95/p99), fallback/error/success
rates, LLM comparison split, and outputs a JSON report.

## Acceptance Criteria

- AC-1: Report contains p50, p95, p99 for total_ms and per-step
- AC-2: Report contains fallback_rate, error_rate, success_rate as decimals [0..1]
- AC-3: Report contains separate latency stats for "with_llm" and "without_llm"
- AC-4: Empty logs produce zero counts and null percentiles (no crash)
- AC-5: All 262 existing tests pass + 6 new = 268

---

## JSONL Record Formats (from ST-028/ST-029)

### pipeline_latency.jsonl
```json
{
  "command_id": "...", "trace_id": "...",
  "total_ms": 12.345,
  "steps": {
    "validate_command_ms": 1.23, "detect_intent_ms": 0.45,
    "registry_ms": 0.12, "core_logic_ms": 8.67, "validate_decision_ms": 1.89
  },
  "llm_enabled": false,
  "timestamp": "2026-02-01T10:00:00+00:00"
}
```

### fallback_metrics.jsonl
```json
{
  "command_id": "...", "trace_id": "...",
  "intent": "add_shopping_item", "decision_action": "start_job",
  "llm_outcome": "skipped",
  "fallback_reason": "policy_disabled",
  "deterministic_used": true, "llm_latency_ms": null,
  "components": {},
  "timestamp": "2026-02-01T10:00:00+00:00"
}
```

Possible `llm_outcome` values: "success", "fallback", "error", "skipped", "deterministic_only".

---

## Files to Change

| File | Action | Description |
|------|--------|-------------|
| `skills/observability/scripts/aggregate_metrics.py` | NEW | Aggregation script |
| `tests/test_aggregate_metrics.py` | NEW | 6 unit tests |

## Files NOT Modified (invariants)

- `app/logging/pipeline_latency_log.py` — DO NOT CHANGE
- `app/logging/fallback_metrics_log.py` — DO NOT CHANGE
- `graphs/core_graph.py` — DO NOT CHANGE
- `tests/test_pipeline_latency.py` — DO NOT CHANGE
- `tests/test_fallback_metrics.py` — DO NOT CHANGE

---

## Implementation Plan

### Step 1: Create `skills/observability/scripts/aggregate_metrics.py`

Functions:

1. **`load_jsonl(path)`** — load JSONL file, return list of dicts. Empty list if file missing.
2. **`_percentile(values, p)`** — compute p-th percentile via linear interpolation. None for empty.
3. **`_percentile_set(values)`** — returns `{p50, p95, p99}` dict.
4. **`compute_latency_stats(records)`** — compute percentiles for total_ms and each step.
   Returns `{count, total_ms: {p50, p95, p99}, steps: {name: {p50, p95, p99}}}`.
5. **`compute_latency_comparison(records)`** — split by `llm_enabled`, return
   `{all, with_llm, without_llm}` each with latency stats.
6. **`compute_fallback_rates(records)`** — count outcomes, compute rates.
   Returns `{count, fallback_rate, error_rate, success_rate, outcome_counts}`.
7. **`_time_range(latency_records, fallback_records)`** — extract first/last timestamps.
8. **`build_report(latency_records, fallback_records)`** — combines all into
   `{latency, fallback, time_range}`.
9. **`main()`** — load from default paths, print JSON.

### Step 2: Create `tests/test_aggregate_metrics.py`

6 pure-function tests with synthetic records:

1. `test_latency_percentiles_computation` — 5 records [10,20,30,40,50], verify p50=30, p95=48, p99=49.6
2. `test_fallback_rate_computation` — 5 records (2 success, 1 fallback, 1 error, 1 skipped)
3. `test_llm_comparison_split` — 4 records (2 with_llm, 2 without), verify split
4. `test_empty_logs_no_crash` — build_report([], []) → zeros and nulls
5. `test_single_record` — 1 record each, verify percentiles equal the value
6. `test_report_valid_json` — json.dumps/loads round-trip

---

## Verification Commands

```bash
# New aggregation tests
source .venv/bin/activate && python3 -m pytest tests/test_aggregate_metrics.py -v

# Latency and fallback tests still pass
source .venv/bin/activate && python3 -m pytest tests/test_pipeline_latency.py tests/test_fallback_metrics.py -v

# Full test suite
source .venv/bin/activate && python3 -m pytest --tb=short -q
```

---

## DoD Checklist

- [ ] `aggregate_metrics.py` created with percentile + rate computation
- [ ] Latency: p50/p95/p99 for total_ms and per-step
- [ ] Fallback: fallback_rate, error_rate, success_rate as decimals
- [ ] LLM comparison: with_llm vs without_llm split
- [ ] Empty logs: no crash, zero counts, null percentiles
- [ ] JSON report to stdout
- [ ] `tests/test_aggregate_metrics.py` — 6 new tests
- [ ] Full test suite passes (268 total)

---

## Risks

| Risk | Mitigation |
|------|-----------|
| Percentile edge cases (1 record, all same) | Tests cover single-record and empty cases |
| JSONL format mismatch | Record formats confirmed from ST-028/ST-029 source code |
| Large log files | load_jsonl reads line-by-line, no full-file buffering needed for MVP |

## Rollback

Remove 2 new files. No impact on existing code.
