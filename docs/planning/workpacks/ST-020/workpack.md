# Workpack: ST-020 — Core Pipeline Registry-Aware Gate (Flag-Gated)

**Status:** Ready
**Story:** `docs/planning/epics/EP-007/stories/ST-020-core-graph-registry-gate.md`

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-007/epic.md` |
| Story | `docs/planning/epics/EP-007/stories/ST-020-core-graph-registry-gate.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q3-agent-registry-integration.md` |
| ADR-005 | `docs/adr/ADR-005-internal-agent-contract-v0.md` |
| Core pipeline | `graphs/core_graph.py` |
| Capabilities lookup | `agent_registry/capabilities_lookup.py` (ST-019) |
| Agent registry loader | `agent_registry/v0_loader.py` |
| Agent registry config | `agent_registry/config.py` |
| Agent registry YAML | `agent_registry/agent-registry-v0.yaml` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

Core pipeline (`graphs/core_graph.py`) becomes registry-aware via a read-only annotation gate. When `AGENT_REGISTRY_CORE_ENABLED=true`, `process_command()` queries `CapabilitiesLookup` for agents matching the detected intent, logs a `registry_snapshot`, but **does not change any decision logic**. Any registry error → silently skipped.

## Acceptance Criteria

1. Flag `AGENT_REGISTRY_CORE_ENABLED` defaults to false; no registry code runs when disabled
2. Flag enabled → `registry_snapshot` logged with: intent, available agent_ids, any_enabled boolean
3. DecisionDTO payload unchanged regardless of flag state
4. Registry load/lookup failure → graceful fallback, decision produced normally, error logged
5. No raw user text or PII in registry log entries
6. All 220 existing tests pass + new tests pass

---

## Files to Change

| File | Change |
|------|--------|
| `agent_registry/config.py` | Add `is_agent_registry_core_enabled()` function |
| `graphs/core_graph.py` | Add `_annotate_registry_capabilities()`; call from `process_command()` when flag enabled |
| `tests/test_core_graph_registry_gate.py` | **New:** ~8 unit tests |

---

## Implementation Plan

### Step 1: Add flag to `agent_registry/config.py`

Append one function:

```python
def is_agent_registry_core_enabled() -> bool:
    return os.getenv("AGENT_REGISTRY_CORE_ENABLED", "false").lower() in {"1", "true", "yes"}
```

### Step 2: Add annotation function to `graphs/core_graph.py`

Add imports at top (after existing imports):

```python
import logging

_logger = logging.getLogger(__name__)
```

Add annotation function (before `process_command`):

```python
def _annotate_registry_capabilities(intent: str) -> Dict[str, Any]:
    """Read-only probe: query registry for agents matching intent.

    Returns a registry_snapshot dict for logging. Never raises.
    """
    try:
        from agent_registry.config import is_agent_registry_core_enabled

        if not is_agent_registry_core_enabled():
            return {}

        from agent_registry.v0_loader import AgentRegistryV0Loader, load_capability_catalog
        from agent_registry.capabilities_lookup import CapabilitiesLookup

        registry = AgentRegistryV0Loader.load()
        catalog = load_capability_catalog()
        lookup = CapabilitiesLookup(registry, catalog)

        # Check all modes
        agents_shadow = lookup.find_agents(intent, "shadow")
        agents_assist = lookup.find_agents(intent, "assist")
        all_agents = agents_shadow + agents_assist

        snapshot = {
            "intent": intent,
            "available_agents": [
                {"agent_id": a.agent_id, "mode": a.mode}
                for a in all_agents
            ],
            "any_enabled": len(all_agents) > 0,
        }

        _logger.info("registry_snapshot: %s", snapshot)
        return snapshot

    except Exception as exc:
        _logger.warning("registry annotation failed: %s", exc)
        return {"intent": intent, "error": str(exc), "any_enabled": False}
```

Key design decisions:
- Lazy imports inside function — avoids import errors when registry not available
- Flag check first — zero overhead when disabled (returns `{}`)
- All exceptions caught — deterministic fallback guaranteed
- Only agent_id and mode in log — no user text, no PII
- Returns dict for testability

### Step 3: Call annotation from `process_command()`

In `process_command()`, after `intent = detect_intent(text)` (line ~190), add:

```python
    registry_snapshot = _annotate_registry_capabilities(intent)
```

This line goes right after `intent = detect_intent(text)` and before the capability checks. The `registry_snapshot` variable is computed but not added to the decision — it's only logged inside the annotation function.

### Step 4: Create `tests/test_core_graph_registry_gate.py`

~8 unit tests:

1. `test_gate_disabled_by_default` — no env var set, call `_annotate_registry_capabilities("add_shopping_item")` → returns `{}`
2. `test_gate_enabled_returns_snapshot` — set env var, mock loader to return test registry → returns snapshot with intent, available_agents, any_enabled
3. `test_decision_unchanged_with_flag_off` — call `process_command()` without flag → decision produced normally
4. `test_decision_unchanged_with_flag_on` — set env var, mock loader → decision identical to flag-off (same action, same payload structure)
5. `test_registry_load_failure_graceful` — set env var, mock loader to raise → returns snapshot with error, pipeline produces decision normally
6. `test_annotation_returns_agent_ids` — set env var, mock registry with 2 agents → snapshot.available_agents has 2 entries with correct agent_ids
7. `test_no_raw_text_in_snapshot` — set env var, mock registry → snapshot contains only intent/agent_id/mode/any_enabled, no "text" key
8. `test_gate_empty_registry_returns_none_enabled` — set env var, mock empty registry → any_enabled=False, available_agents=[]

Test pattern: use `monkeypatch.setenv` for flag, `monkeypatch.setattr` or mock for registry loader. Use `sample_command()` from core_graph for integration-style tests.

---

## Verification Commands

```bash
# Full test suite (expect 228 passed)
python3 -m pytest tests/ -v --tb=short

# Just registry gate tests (expect 8 tests)
python3 -m pytest tests/test_core_graph_registry_gate.py -v --tb=short

# Import check
python3 -c "from graphs.core_graph import _annotate_registry_capabilities; print('OK')"

# Flag check
python3 -c "from agent_registry.config import is_agent_registry_core_enabled; print(is_agent_registry_core_enabled())"
# expect: False
```

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Lazy imports slow down hot path | Low | Low | Only when flag=true; registry load is fast (file-based) |
| Mock complexity in tests | Medium | Low | Use monkeypatch for env vars and loader |
| Circular import agent_registry ↔ graphs | Low | Medium | Lazy imports inside function prevent circular deps |

## Rollback

- Revert `graphs/core_graph.py` changes (remove annotation call + function)
- Revert `agent_registry/config.py` (remove one function)
- Delete `tests/test_core_graph_registry_gate.py`
- No schema/contract/flag-file changes

## APPLY Boundaries

**Allowed:** `agent_registry/config.py`, `graphs/core_graph.py`, `tests/test_core_graph_registry_gate.py`
**Forbidden:** `agent_registry/v0_models.py`, `agent_registry/v0_loader.py`, `agent_registry/capabilities_lookup.py`, `agent_registry/*.yaml`, `routers/**`, `contracts/**`, `.github/workflows/ci.yml`
