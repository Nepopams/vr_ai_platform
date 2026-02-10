# ST-029: Unified Fallback and Error Rate Structured Logging

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
| Partial trust risk log | `app/logging/partial_trust_risk_log.py` |
| Shadow router log | `app/logging/shadow_router_log.py` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

Partial trust risk log and shadow router log each capture LLM outcomes for their
respective paths. But there is no unified view: "for this command, did the LLM
contribute, fall back, or error across all paths?"

## User Value

As a platform operator, I want a unified log that records, for every LLM-involved
decision, whether the LLM succeeded, fell back to deterministic, or errored,
so that I can track the fallback rate and error budget.

## Scope

### In scope

- New module `app/logging/fallback_metrics_log.py`
- One record per command involving any LLM path (shadow/assist/partial trust)
- Fields: trace_id, timestamp, llm_outcome (success/fallback/error/skipped),
  fallback_reason, per-component status, llm_latency_ms, deterministic_used
- Logged to `logs/fallback_metrics.jsonl`
- Config: `FALLBACK_METRICS_LOG_ENABLED` env var (default: true)
- No raw user text or raw LLM output (privacy)

### Out of scope

- Aggregation/dashboard (ST-030)
- Alerting on error budget
- Modifying any decision logic
- Changes to existing per-component logs

---

## Acceptance Criteria

### AC-1: Record emitted for LLM-involved commands
```
Given LLM_POLICY_ENABLED=true, SHADOW_ROUTER_ENABLED=true
When process_command() is called
Then a fallback_metrics record is emitted
```

### AC-2: Correct outcome -- success
```
Given LLM returns successfully
When fallback_metrics record is emitted
Then llm_outcome="success" and fallback_reason=null
```

### AC-3: Correct outcome -- fallback
```
Given LLM times out
When fallback_metrics record is emitted
Then llm_outcome="fallback" and fallback_reason="timeout" and deterministic_used=true
```

### AC-4: Skipped when LLM disabled
```
Given LLM_POLICY_ENABLED=false
When process_command() is called
Then either no record emitted, or llm_outcome="skipped"
```

### AC-5: Privacy guarantee
```
Given any fallback_metrics record
When inspected
Then no field contains raw user text or raw LLM output
```

### AC-6: All 228 existing tests pass

---

## Test Strategy

### Unit tests (~6 new in `tests/test_fallback_metrics.py`)
- `test_record_on_llm_success`
- `test_record_on_llm_timeout`
- `test_record_on_llm_unavailable`
- `test_record_skipped_when_disabled`
- `test_no_raw_text_in_record`
- `test_log_written_to_jsonl`

### Regression
- Full test suite: 228 tests must pass

---

## Code Touchpoints

| File | Change |
|------|--------|
| `app/logging/fallback_metrics_log.py` | New: unified fallback logger |
| `graphs/core_graph.py` or integration point | Update: emit fallback record |
| `tests/test_fallback_metrics.py` | New: unit tests |

---

## Dependencies

- None (reads status from existing components)
- Blocks: ST-030, ST-031
