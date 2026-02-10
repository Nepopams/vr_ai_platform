# Workpack — ST-028: Pipeline-Wide Latency Instrumentation

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-010/epic.md` |
| Story | `docs/planning/epics/EP-010/stories/ST-028-pipeline-latency-instrumentation.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q4-production-hardening.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

## Outcome

Every `process_command()` call emits a structured JSONL latency record with total_ms and per-step breakdown. Record includes `llm_enabled` flag. Disabled via env var.

## Acceptance Criteria Summary

- AC-1: Latency record emitted for every command (when enabled)
- AC-2: Steps non-negative, sum <= total_ms
- AC-3: No record when disabled
- AC-4: `llm_enabled` reflects `LLM_POLICY_ENABLED`
- AC-5: Overhead < 1ms (time.monotonic only)
- AC-6: All 239 existing tests pass + 6 new = 245

## Files to Change

| File | Action | Description |
|------|--------|-------------|
| `app/logging/pipeline_latency_log.py` | NEW | Latency logger (follows shadow_router_log.py pattern) |
| `graphs/core_graph.py` | UPDATE | Add timing around 5 steps in `process_command()` |
| `tests/test_pipeline_latency.py` | NEW | 6 unit tests |

## Files NOT Modified (invariants)

- `contracts/schemas/command.schema.json` — DO NOT CHANGE
- `contracts/schemas/decision.schema.json` — DO NOT CHANGE
- `app/logging/shadow_router_log.py` — DO NOT CHANGE
- `app/logging/assist_log.py` — DO NOT CHANGE
- Decision output of `process_command()` — MUST NOT CHANGE

## Implementation Plan

### Step 1: Create `app/logging/pipeline_latency_log.py`

Follow the exact pattern of `app/logging/shadow_router_log.py`:

- `DEFAULT_LOG_PATH = Path("logs/pipeline_latency.jsonl")`
- `_ensure_parent(path)` — same as existing
- `is_pipeline_latency_log_enabled()` — reads `PIPELINE_LATENCY_LOG_ENABLED` env var, default `"true"`
- `resolve_log_path()` — reads `PIPELINE_LATENCY_LOG_PATH` env var
- `append_pipeline_latency_log(payload)` — appends JSONL record with timestamp

### Step 2: Update `graphs/core_graph.py` — `process_command()`

Add `import time` and import the new logging module. Wrap 5 steps with `time.monotonic()` timing:

Current `process_command()` structure (lines 227-318):
```
Line 228-229: load command schema + validate         → "validate_command_ms"
Line 231-232: text + detect_intent                    → "detect_intent_ms"
Line 233:     _annotate_registry_capabilities         → "registry_ms"
Line 234-313: capabilities check + core if/elif/else  → "core_logic_ms"
Line 315-316: load decision schema + validate         → "validate_decision_ms"
Line 318:     return decision
```

Insert timing wrapper:
```python
def process_command(command: Dict[str, Any]) -> Dict[str, Any]:
    import time
    from app.logging.pipeline_latency_log import (
        is_pipeline_latency_log_enabled,
        append_pipeline_latency_log,
    )

    t_start = time.monotonic()

    # Step 1: validate command
    t0 = time.monotonic()
    command_schema = load_schema(COMMAND_SCHEMA_PATH)
    validate(instance=command, schema=command_schema)
    validate_command_ms = (time.monotonic() - t0) * 1000

    # Step 2: detect intent
    t0 = time.monotonic()
    text = command.get("text", "").strip()
    intent = detect_intent(text)
    detect_intent_ms = (time.monotonic() - t0) * 1000

    # Step 3: registry annotation
    t0 = time.monotonic()
    registry_snapshot = _annotate_registry_capabilities(intent)
    registry_ms = (time.monotonic() - t0) * 1000

    # Step 4: core logic (unchanged)
    t0 = time.monotonic()
    capabilities = set(command.get("capabilities", []))
    # ... entire if/elif/else block unchanged ...
    core_logic_ms = (time.monotonic() - t0) * 1000

    # Step 5: validate decision
    t0 = time.monotonic()
    decision_schema = load_schema(DECISION_SCHEMA_PATH)
    validate(instance=decision, schema=decision_schema)
    validate_decision_ms = (time.monotonic() - t0) * 1000

    total_ms = (time.monotonic() - t_start) * 1000

    # Emit latency record
    if is_pipeline_latency_log_enabled():
        from llm_policy.config import is_llm_policy_enabled
        append_pipeline_latency_log({
            "command_id": command.get("command_id"),
            "trace_id": decision.get("trace_id"),
            "total_ms": round(total_ms, 3),
            "steps": {
                "validate_command_ms": round(validate_command_ms, 3),
                "detect_intent_ms": round(detect_intent_ms, 3),
                "registry_ms": round(registry_ms, 3),
                "core_logic_ms": round(core_logic_ms, 3),
                "validate_decision_ms": round(validate_decision_ms, 3),
            },
            "llm_enabled": is_llm_policy_enabled(),
        })

    return decision
```

Key constraints:
- The if/elif/else core logic block is **NOT changed** — only wrapped with timing
- Decision output is identical
- Imports inside function to avoid circular import risk
- `round(..., 3)` for clean JSONL

### Step 3: Create `tests/test_pipeline_latency.py`

6 unit tests:

1. `test_latency_record_structure` — call process_command, read JSONL, verify keys
2. `test_step_breakdown_non_negative` — all step values >= 0
3. `test_total_ms_gte_step_sum` — total_ms >= sum of steps
4. `test_disabled_no_log` — set `PIPELINE_LATENCY_LOG_ENABLED=false`, no JSONL written
5. `test_llm_enabled_flag` — monkeypatch `LLM_POLICY_ENABLED=true`, verify flag
6. `test_log_written_to_jsonl` — verify file exists and is parseable JSON per line

Test pattern:
- Use `tmp_path` fixture for log isolation
- Monkeypatch `PIPELINE_LATENCY_LOG_PATH` to `tmp_path / "latency.jsonl"`
- Use `sample_command()` from `graphs.core_graph`
- Monkeypatch `PIPELINE_LATENCY_LOG_ENABLED` as needed

## Verification Commands

```bash
# New latency tests
source .venv/bin/activate && python3 -m pytest tests/test_pipeline_latency.py -v

# Core graph tests (must still pass)
source .venv/bin/activate && python3 -m pytest tests/test_core_graph_registry_gate.py tests/test_graph_execution.py -v

# Full test suite
source .venv/bin/activate && python3 -m pytest --tb=short -q
```

## Risks & Rollback

| Risk | Mitigation |
|------|-----------|
| Circular import from app.logging in graphs/ | Import inside function body |
| Timing overhead | Only `time.monotonic()` calls — sub-microsecond |
| File I/O in hot path | Gated by `is_pipeline_latency_log_enabled()` |

Rollback: revert `process_command()` to pre-timing version, delete new files.
