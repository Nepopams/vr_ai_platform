# ST-030: Latency and Fallback Summary Aggregation Script

**Epic:** EP-010 (Pipeline Observability)
**Status:** Ready
**Flags:** contract_impact=no, adr_needed=none, diagrams_needed=none

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-010/epic.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q4-production-hardening.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

ST-028 produces `pipeline_latency.jsonl`, ST-029 produces `fallback_metrics.jsonl`.
This story creates a script that reads both and produces aggregate statistics.

## User Value

As a platform operator, I want a script that reads latency and fallback JSONL logs
and produces aggregate statistics (p50/p95/p99 latency, fallback rate, error rate),
so that I have dashboard-ready metrics for production readiness assessment.

## Scope

### In scope

- New script: `skills/observability/scripts/aggregate_metrics.py`
- Reads `logs/pipeline_latency.jsonl` and `logs/fallback_metrics.jsonl`
- Outputs:
  - Latency: p50, p95, p99 for total_ms and each step
  - Latency comparison: with_llm vs without_llm (grouped by `llm_enabled`)
  - Fallback rate, error rate, success rate (as decimals [0..1])
  - Command count, time range
- Output format: JSON report to stdout and/or file
- Works on empty logs (produces zeros, no crash)

### Out of scope

- Real-time metrics / streaming aggregation
- Grafana / Prometheus integration
- CI integration for this script
- Alerting thresholds

---

## Acceptance Criteria

### AC-1: Script produces latency percentiles
```
Given pipeline_latency.jsonl with 50+ records
When aggregate_metrics.py runs
Then report contains p50, p95, p99 for total_ms and per-step
```

### AC-2: Script produces fallback rate
```
Given fallback_metrics.jsonl with mixed outcomes
When aggregate_metrics.py runs
Then report contains fallback_rate, error_rate, success_rate as decimals [0..1]
```

### AC-3: Comparison output
```
Given pipeline_latency records with both llm_enabled=true and llm_enabled=false
When aggregate_metrics.py runs
Then report contains separate latency stats for "with_llm" and "without_llm"
```

### AC-4: Empty log handling
```
Given empty JSONL files
When aggregate_metrics.py runs
Then report is produced with zero counts and null percentiles (no crash)
```

### AC-5: All 228 existing tests pass

---

## Test Strategy

### Unit tests (~6 new in `tests/test_aggregate_metrics.py`)
- `test_latency_percentiles_computation`
- `test_fallback_rate_computation`
- `test_llm_comparison_split`
- `test_empty_logs_no_crash`
- `test_single_record`
- `test_report_valid_json`

### Regression
- Full test suite: 228 tests must pass

---

## Code Touchpoints

| File | Change |
|------|--------|
| `skills/observability/scripts/aggregate_metrics.py` | New: aggregation script |
| `tests/test_aggregate_metrics.py` | New: unit tests |

---

## Dependencies

- ST-028, ST-029 (needs the log formats they define)
- Blocks: ST-031
