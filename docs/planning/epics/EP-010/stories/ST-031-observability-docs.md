# ST-031: Observability Documentation and Runbook

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

ST-028, ST-029, ST-030 create the instrumentation and aggregation. Platform operators
need documentation describing all observability outputs and how to use them.

## User Value

As a platform operator, I want documentation describing all observability outputs
(log files, their schemas, how to run aggregation), so that I can monitor the
platform in production.

## Scope

### In scope

- `docs/guides/observability.md` covering:
  - List of all JSONL log files and their locations
  - Schema for each log type (pipeline_latency, fallback_metrics, shadow_router, assist, partial_trust_risk)
  - How to run `aggregate_metrics.py`
  - Interpretation guide: healthy fallback rate, expected latency values
  - Env vars for enabling/disabling each log

### Out of scope

- Dashboard setup guides
- Alerting configuration
- SLA definitions

---

## Acceptance Criteria

### AC-1: Guide covers all log types
```
Given docs/guides/observability.md
When reviewed
Then it documents all 5 log file types with their schemas
```

### AC-2: Guide includes aggregation instructions
```
Given docs/guides/observability.md
When reviewed
Then it explains how to run aggregate_metrics.py and interpret results
```

### AC-3: Env var reference complete
```
Given docs/guides/observability.md
When reviewed
Then all logging-related env vars are documented
```

---

## Test Strategy

- Manual review
- No automated tests (docs-only)

---

## Code Touchpoints

| File | Change |
|------|--------|
| `docs/guides/observability.md` | New: observability runbook |

---

## Dependencies

- ST-028, ST-029, ST-030 (needs to document what they created)
