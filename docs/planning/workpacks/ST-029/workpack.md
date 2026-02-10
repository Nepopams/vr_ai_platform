# Workpack — ST-029: Unified Fallback and Error Rate Structured Logging

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-010/epic.md` |
| Story | `docs/planning/epics/EP-010/stories/ST-029-unified-fallback-metrics.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q4-production-hardening.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

## Outcome

A unified JSONL log that records, for every command processed by the pipeline, the LLM involvement status: skipped (LLM disabled) or deterministic_only (LLM enabled but core graph uses baseline). The log module also supports recording success/fallback/error outcomes for future integration with shadow/assist/partial-trust paths.

## Architecture Note

`process_command()` runs the deterministic baseline — it does **not** call LLM directly.
Shadow/assist/partial-trust paths run independently. Therefore:
- When `LLM_POLICY_ENABLED=false` → `llm_outcome="skipped"`
- When `LLM_POLICY_ENABLED=true` → `llm_outcome="deterministic_only"` (baseline always used)
- The log module API accepts any outcome (`success`/`fallback`/`error`) for future callers
- Tests verify the logging module handles all outcome types correctly

## Acceptance Criteria Summary

- AC-1: Record emitted for every process_command call (when enabled)
- AC-2: Log module correctly records success outcome
- AC-3: Log module correctly records fallback outcome with reason
- AC-4: Record has `llm_outcome="skipped"` when LLM disabled
- AC-5: No raw user text or LLM output in records
- AC-6: All 245 existing tests pass + 6 new = 251

## Files to Change

| File | Action | Description |
|------|--------|-------------|
| `app/logging/fallback_metrics_log.py` | NEW | Unified fallback logger (follows existing pattern) |
| `graphs/core_graph.py` | UPDATE | Add fallback metrics emission in `process_command()` |
| `tests/test_fallback_metrics.py` | NEW | 6 unit tests |

## Files NOT Modified (invariants)

- `contracts/schemas/command.schema.json` — DO NOT CHANGE
- `contracts/schemas/decision.schema.json` — DO NOT CHANGE
- `app/logging/shadow_router_log.py` — DO NOT CHANGE
- `app/logging/assist_log.py` — DO NOT CHANGE
- `app/logging/partial_trust_risk_log.py` — DO NOT CHANGE
- `app/logging/pipeline_latency_log.py` — DO NOT CHANGE
- `tests/test_pipeline_latency.py` — DO NOT CHANGE
- Decision output of `process_command()` — MUST NOT CHANGE

## Implementation Plan

### Step 1: Create `app/logging/fallback_metrics_log.py`

Follow the exact pattern of existing loggers:

- `DEFAULT_LOG_PATH = Path("logs/fallback_metrics.jsonl")`
- `_ensure_parent(path)` — same as existing
- `is_fallback_metrics_log_enabled()` — reads `FALLBACK_METRICS_LOG_ENABLED`, default `"true"`
- `resolve_log_path()` — reads `FALLBACK_METRICS_LOG_PATH`
- `append_fallback_metrics_log(payload)` — appends JSONL with timestamp, `ensure_ascii=False`
- Privacy comment: `# NO RAW USER OR LLM TEXT — PRIVACY GUARANTEE.`

### Step 2: Update `graphs/core_graph.py` — `process_command()`

Minimal changes to the function:

1. Add fallback_metrics imports alongside existing pipeline_latency imports (lines 231-234)
2. Move `from llm_policy.config import is_llm_policy_enabled` out of the latency `if` block to function-level (avoids duplicate import)
3. Compute `llm_on = is_llm_policy_enabled()` once before both logging blocks
4. Update latency block to use `llm_on` variable
5. Add fallback metrics block after latency block, before `return decision`

### Step 3: Create `tests/test_fallback_metrics.py`

6 unit tests:

1. `test_record_on_llm_success` — directly call `append_fallback_metrics_log` with success payload, verify record structure
2. `test_record_on_llm_timeout` — call with fallback/timeout payload, verify `llm_outcome="fallback"` and `fallback_reason="timeout"`
3. `test_record_on_llm_unavailable` — call with error/unavailable payload, verify structure
4. `test_record_skipped_when_disabled` — call `process_command()` with `LLM_POLICY_ENABLED=false`, verify JSONL has `llm_outcome="skipped"`
5. `test_no_raw_text_in_record` — call `process_command()`, verify record has no `text`/`prompt`/`raw` fields
6. `test_log_written_to_jsonl` — multiple process_command calls, verify valid JSONL lines

## Verification Commands

```bash
# New fallback metrics tests
source .venv/bin/activate && python3 -m pytest tests/test_fallback_metrics.py -v

# Latency tests still pass (both touch process_command)
source .venv/bin/activate && python3 -m pytest tests/test_pipeline_latency.py -v

# Core graph tests still pass
source .venv/bin/activate && python3 -m pytest tests/test_core_graph_registry_gate.py tests/test_graph_execution.py -v

# Full test suite
source .venv/bin/activate && python3 -m pytest --tb=short -q
```

## Risks & Rollback

| Risk | Mitigation |
|------|-----------|
| Touching ST-028's latency section | Only moving import out of `if`, same logic |
| Duplicate import of is_llm_policy_enabled | Refactored to single function-level import |
| Privacy leak | NO raw text/prompt fields, explicit privacy comment |

Rollback: revert `process_command()` latency/fallback blocks, delete new files.
