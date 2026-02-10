# ST-028: Pipeline-Wide Latency Instrumentation in Core Graph

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
| Core pipeline | `graphs/core_graph.py` |
| Shadow router log | `app/logging/shadow_router_log.py` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

Shadow router and assist runner log per-call `latency_ms`. But there is no pipeline-wide
latency breakdown covering all steps together (normalize, shadow, assist, core_logic,
partial_trust, validation). No p50/p95/p99 aggregation exists.

## User Value

As a platform operator, I want every step of the decision pipeline to be timed with
structured latency records, so that I can identify bottlenecks and compare
"with LLM" vs "without LLM" performance.

## Scope

### In scope

- Add timing wrapper around key pipeline steps
- New module `app/logging/pipeline_latency_log.py` (follows existing pattern)
- Structured JSONL log: `logs/pipeline_latency.jsonl`
- Record per command with breakdown: trace_id, total_ms, step-level times, llm_enabled flag
- Config: `PIPELINE_LATENCY_LOG_ENABLED` env var (default: true)

### Out of scope

- p50/p95/p99 aggregation (ST-030)
- Dashboard or visualization
- Modifying the decision outcome
- Latency alerting

---

## Acceptance Criteria

### AC-1: Latency record emitted for every command
```
Given PIPELINE_LATENCY_LOG_ENABLED=true
When process_command() is called
Then a pipeline_latency record is appended to JSONL log
And it contains total_ms and step-level breakdown
```

### AC-2: Steps are non-negative and sum correctly
```
Given a pipeline_latency record
When step values are summed
Then sum <= total_ms (within rounding tolerance)
And no step value is negative
```

### AC-3: No latency log when disabled
```
Given PIPELINE_LATENCY_LOG_ENABLED=false
When process_command() is called
Then no pipeline_latency record is emitted
```

### AC-4: LLM-enabled flag reflects actual state
```
Given LLM_POLICY_ENABLED=true
When pipeline_latency record is emitted
Then llm_enabled=true
```

### AC-5: No performance regression
```
Given the pipeline without latency logging
When latency logging is enabled
Then overhead is < 1ms per command (time.monotonic() calls only)
```

### AC-6: All 228 existing tests pass

---

## Test Strategy

### Unit tests (~6 new in `tests/test_pipeline_latency.py`)
- `test_latency_record_structure`
- `test_step_breakdown_non_negative`
- `test_total_ms_gte_step_sum`
- `test_disabled_no_log`
- `test_llm_enabled_flag`
- `test_log_written_to_jsonl`

### Regression
- Full test suite: 228 tests must pass

---

## Code Touchpoints

| File | Change |
|------|--------|
| `app/logging/pipeline_latency_log.py` | New: latency logger |
| `graphs/core_graph.py` | Update: add timing around steps |
| `tests/test_pipeline_latency.py` | New: unit tests |

---

## Dependencies

- None (reads existing pipeline, adds instrumentation)
- Blocks: ST-030, ST-031
