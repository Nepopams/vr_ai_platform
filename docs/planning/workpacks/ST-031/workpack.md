# Workpack — ST-031: Observability Documentation and Runbook

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-010/epic.md` |
| Story spec | `docs/planning/epics/EP-010/stories/ST-031-observability-docs.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q4-production-hardening.md` |
| Sprint | `docs/planning/sprints/S08/sprint.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

A single new file `docs/guides/observability.md` — an operator-facing guide that documents all JSONL log types, their schemas, env vars, how to run the aggregation script, and how to interpret results.

---

## Acceptance Criteria (from story spec)

| AC | Description | How to verify |
|----|-------------|---------------|
| AC-1 | Guide covers all 5 log types with schemas | Manual review of docs/guides/observability.md |
| AC-2 | Guide includes aggregation instructions | Section on `aggregate_metrics.py` with run command and output interpretation |
| AC-3 | Env var reference complete | All logging-related env vars documented in a table |

---

## Architecture and Design Decisions

### 5 primary log types (from story spec)

| # | Log type | File | Module | Env path var | Enable var |
|---|----------|------|--------|-------------|------------|
| 1 | Pipeline latency | `logs/pipeline_latency.jsonl` | `app/logging/pipeline_latency_log.py` | `PIPELINE_LATENCY_LOG_PATH` | `PIPELINE_LATENCY_LOG_ENABLED` (default: true) |
| 2 | Fallback metrics | `logs/fallback_metrics.jsonl` | `app/logging/fallback_metrics_log.py` | `FALLBACK_METRICS_LOG_PATH` | `FALLBACK_METRICS_LOG_ENABLED` (default: true) |
| 3 | Shadow router | `logs/shadow_router.jsonl` | `app/logging/shadow_router_log.py` | `SHADOW_ROUTER_LOG_PATH` | `SHADOW_ROUTER_ENABLED` (feature flag) |
| 4 | Assist | `logs/assist.jsonl` | `app/logging/assist_log.py` | `ASSIST_LOG_PATH` | `ASSIST_MODE_ENABLED` (feature flag) |
| 5 | Partial trust risk | `logs/partial_trust_risk.jsonl` | `app/logging/partial_trust_risk_log.py` | `PARTIAL_TRUST_RISK_LOG_PATH` | `PARTIAL_TRUST_ENABLED` (feature flag) |

### Additional log types (document briefly)

| Log type | File | Enable var |
|----------|------|------------|
| Decision | `logs/decisions.jsonl` | Always on |
| Decision text | `logs/decision_text.jsonl` | `LOG_USER_TEXT` (default: false, privacy) |
| Agent run | `logs/agent_run.jsonl` | `AGENT_RUN_LOG_ENABLED` (default: false) |
| Shadow agent diff | `logs/shadow_agent_diff.jsonl` | `SHADOW_AGENT_DIFF_LOG_ENABLED` (default: false) |

### Aggregation script

`skills/observability/scripts/aggregate_metrics.py`:
- Reads `pipeline_latency.jsonl` and `fallback_metrics.jsonl`.
- Computes: p50/p95/p99 latency (total + per-step), fallback/error/success rates.
- Comparison: with-LLM vs without-LLM groups.
- Output: JSON report to stdout.
- Handles missing files and invalid lines gracefully.

### Log record schemas (from PLAN exploration)

**Pipeline latency record** keys: `timestamp`, `trace_id`, `command_id`, `total_ms`, `steps` (dict of step→ms), `llm_enabled`.

**Fallback metrics record** keys: `timestamp`, `trace_id`, `command_id`, `llm_outcome` ("success"/"fallback"/"error").

**Shadow router record** keys (17): `timestamp`, `trace_id`, `command_id`, `router_version`, `router_strategy`, `status`, `latency_ms`, `error_type`, `suggested_intent`, `missing_fields`, `clarify_question`, `entities_summary`, `confidence`, `model_meta`, `baseline_intent`, `baseline_action`, `baseline_job_type`.

**Assist record**: flexible payload with `timestamp` auto-added. Typical keys include step name, latency, result summary.

**Partial trust risk record**: flexible payload with `timestamp` auto-added. Typical keys include `outcome` (accepted_llm/fallback/error), `intent`, `reason`.

### Guide style

Follow `docs/guides/llm-setup.md` and `docs/guides/golden-dataset.md` patterns: clear headings, code blocks, env var tables, step-by-step instructions.

### Privacy notes

The guide must document:
- `LOG_USER_TEXT` defaults to `false` — only enable for debugging.
- Partial trust and fallback logs contain NO raw user text or LLM output.
- Shadow agent diff uses privacy-safe summarization (structure only, no values).

---

## Files to Change

| File | Change | New/Modify |
|------|--------|------------|
| `docs/guides/observability.md` | New: observability guide and runbook | New |

### Invariants (DO NOT CHANGE)

- `app/logging/*.py` — all logging modules
- `skills/observability/scripts/aggregate_metrics.py`
- `graphs/core_graph.py`
- `.env.example`
- All test files

---

## Implementation Plan

### Step 1: Create `docs/guides/observability.md`

Sections:
1. Overview — what observability is available, JSONL format
2. Log Types — each of the 5 primary types with schema, env vars, example record
3. Additional Logs — decision, agent run, shadow agent diff (brief)
4. Environment Variables Reference — complete table
5. Running Aggregation — command, output format, interpretation
6. Interpreting Results — healthy values, what to look for
7. Privacy — what is/isn't logged, `LOG_USER_TEXT` flag

---

## Verification Commands

```bash
# Verify guide exists and has content
test -f docs/guides/observability.md && wc -l docs/guides/observability.md

# Full test suite unchanged (expect 270 passed, 3 skipped)
source .venv/bin/activate && python3 -m pytest --tb=short -q
```

---

## Tests

No new tests. Docs-only story.

---

## DoD Checklist

- [ ] `docs/guides/observability.md` created
- [ ] Covers all 5 primary log types with schemas
- [ ] Covers aggregation script (run command + output interpretation)
- [ ] All logging env vars documented
- [ ] Privacy notes included
- [ ] No invariant files modified
- [ ] No regression in existing tests (270 passed, 3 skipped)

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Log record schemas drift from code | Low | Low | PLAN phase confirms schemas from source code |
| Missing some env vars | Low | Low | PLAN phase greps all logging env vars |

---

## Rollback

Delete `docs/guides/observability.md`. No other files modified.
