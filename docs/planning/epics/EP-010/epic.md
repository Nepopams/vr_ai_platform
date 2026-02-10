# EP-010: Pipeline Observability -- Latency Breakdown and Fallback Metrics

**Status:** Ready
**Initiative:** `docs/planning/initiatives/INIT-2026Q4-production-hardening.md`
**Sprint:** TBD (S06-S08 candidate)
**Owner:** TBD

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Roadmap | `docs/planning/strategy/roadmap.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q4-production-hardening.md` |
| Shadow router log | `app/logging/shadow_router_log.py` |
| Partial trust risk log | `app/logging/partial_trust_risk_log.py` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

Current state of observability:

- Shadow router logs per-call `latency_ms` in `logs/shadow_router.jsonl`
- Assist runner logs per-step `latency_ms` (normalizer, entities, clarify)
- Partial trust risk log captures accepted_llm / fallback / error
- Core pipeline (`process_command`) has no timing instrumentation
- No aggregate view of pipeline-wide latency (p50/p95/p99)
- No unified fallback rate counter across all LLM paths

## Goal

Add pipeline-wide latency breakdown (every step timed), unify fallback/error metrics
into a structured format, create an aggregation script for dashboard-ready summaries,
and document all observability outputs.

## Scope

### In scope

- Pipeline-wide latency instrumentation in core pipeline
- Structured latency log with per-step breakdown (JSONL)
- Unified fallback/error rate structured logging (JSONL)
- Aggregation script: p50/p95/p99 latency, fallback/error/success rates
- Observability documentation and runbook
- Config via env vars (`PIPELINE_LATENCY_LOG_ENABLED`, `FALLBACK_METRICS_LOG_ENABLED`)

### Out of scope

- Real-time metrics / streaming aggregation
- Grafana / Prometheus integration
- Alerting thresholds or SLA definitions
- Dashboard UI
- Modifying any decision logic

## Stories

| Story ID | Title | Status | Flags |
|----------|-------|--------|-------|
| [ST-028](stories/ST-028-pipeline-latency-instrumentation.md) | Pipeline-wide latency instrumentation | Ready | contract_impact=no, adr_needed=none, diagrams_needed=none |
| [ST-029](stories/ST-029-unified-fallback-metrics.md) | Unified fallback and error rate structured logging | Ready | contract_impact=no, adr_needed=none, diagrams_needed=none |
| [ST-030](stories/ST-030-aggregation-script.md) | Latency and fallback summary aggregation script | Ready (dep: ST-028, ST-029) | contract_impact=no, adr_needed=none, diagrams_needed=none |
| [ST-031](stories/ST-031-observability-docs.md) | Observability documentation and runbook | Ready (dep: ST-028, ST-029, ST-030) | contract_impact=no, adr_needed=none, diagrams_needed=none |

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| Shadow router logging | Internal | Done |
| Assist mode logging | Internal | Done |
| Partial trust risk log | Internal | Done |
| Core pipeline (core_graph.py) | Internal | Done |
| Existing test suite (228 tests) | Internal | Passing |

### Story ordering

```
ST-028 (pipeline latency)    ST-029 (fallback metrics)
  |                             |
  +--------+--------+----------+
           |
           v
        ST-030 (aggregation script)
           |
           v
        ST-031 (docs)
```

ST-028 and ST-029 are independent and can run in parallel. ST-030 depends on both.
ST-031 depends on all three.

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Latency instrumentation overhead | Very Low | Low | time.monotonic() only, no external deps |
| JSONL log files grow large | Low | Low | Log rotation is ops concern, not in scope |
| Privacy leak in fallback logs | Low | High | No raw user text / LLM output; privacy AC in ST-029 |
| Aggregation math errors (percentiles) | Low | Low | Well-tested with synthetic data |

## Readiness Report

### Ready
- **ST-028** -- No blockers. Adds instrumentation to existing pipeline. (~1 day)
- **ST-029** -- No blockers. Reads status from existing components. (~1 day)
- **ST-030** -- Depends on ST-028+ST-029 log formats. (~1 day)
- **ST-031** -- Docs-only. Depends on all code stories. (~0.5 day)

### Conditional agents needed
- None (all flags negative)
