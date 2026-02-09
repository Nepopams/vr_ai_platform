# ST-020: Core Pipeline Registry-Aware Gate (Flag-Gated)

**Epic:** EP-007 (Agent Registry Integration)
**Status:** Ready (dep: ST-018, ST-019)
**Flags:** contract_impact=no, adr_needed=none, diagrams_needed=none

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-007/epic.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q3-agent-registry-integration.md` |
| ADR-005 (updated) | `docs/adr/ADR-005-internal-agent-contract-v0.md` |
| Core pipeline | `graphs/core_graph.py` |
| Capabilities lookup | `agent_registry/capabilities_lookup.py` (from ST-019) |
| Agent registry config | `agent_registry/config.py` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

After ST-018 (ADR) and ST-019 (capabilities lookup), the platform has a documented
integration plan and a query service. The core pipeline (`graphs/core_graph.py`)
currently uses pure deterministic logic with no awareness of the agent registry.

This story adds a **registry-aware gate** that:
- Queries capabilities lookup for agents matching the detected intent
- Annotates the decision trace with agent capability metadata
- Logs the snapshot for observability
- **Does NOT change any decision logic** -- deterministic baseline unaffected
- Entirely gated behind `AGENT_REGISTRY_CORE_ENABLED` (default: false)

This is a "read-only probe" pattern: pipeline becomes aware of what agents COULD
contribute, without actually invoking them.

## User Value

As a platform operator, I want the core pipeline to be aware of registered agent
capabilities, so I can observe which agents would be available for each intent
and prepare for future registry-driven routing without any behavior change.

## Scope

### In scope

- New flag: `AGENT_REGISTRY_CORE_ENABLED` in `agent_registry/config.py` (default: false)
- New function `_annotate_registry_capabilities(decision, intent)` in `graphs/core_graph.py`
- Call annotation from `process_command()` when flag enabled
- `registry_snapshot` logged (not added to DecisionDTO response)
- Unit and integration tests

### Out of scope

- Invoking registry agents from core pipeline
- Changing DecisionDTO schema or payload
- Modifying V2 router
- Modifying shadow invoker or assist hints
- Agent-driven routing decisions (future epic)
- Flag management UI

---

## Acceptance Criteria

### AC-1: Flag defaults to disabled
```
Given no AGENT_REGISTRY_CORE_ENABLED env var
When core pipeline processes a command
Then registry gate is not invoked
And decision is identical to current behavior
```

### AC-2: Flag enabled triggers capability annotation
```
Given AGENT_REGISTRY_CORE_ENABLED=true
When core pipeline processes command "Купи молоко"
Then agent run log contains registry_snapshot with:
  intent, available_agents, any_enabled
```

### AC-3: Decision payload unchanged regardless of flag
```
Given AGENT_REGISTRY_CORE_ENABLED=true
When core pipeline processes any command
Then returned DecisionDTO is identical to flag-disabled behavior
```

### AC-4: Registry load failure does not break pipeline
```
Given AGENT_REGISTRY_CORE_ENABLED=true
And agent registry YAML is missing or malformed
When core pipeline processes a command
Then decision is produced normally (deterministic fallback)
And log contains registry_snapshot with error status
```

### AC-5: Annotation works for all intents
```
Given AGENT_REGISTRY_CORE_ENABLED=true
When core pipeline processes commands for each intent
Then each log entry includes registry_snapshot with correct intent
```

### AC-6: No raw user text in registry log entries
```
Given AGENT_REGISTRY_CORE_ENABLED=true
When registry gate logs a snapshot
Then log contains only: intent, agent_ids, modes, enabled flags, capability_ids
And does NOT contain user text or PII
```

### AC-7: All 202+ existing tests pass
```
Given the test suite
When ST-020 changes are applied
Then all existing tests pass and new tests also pass
```

---

## Test Strategy

### Unit tests (~9 new in `tests/test_core_graph_registry_gate.py`)
- `test_gate_disabled_by_default`
- `test_gate_enabled_annotates_log`
- `test_decision_unchanged_with_flag_on`
- `test_decision_unchanged_with_flag_off`
- `test_registry_load_failure_graceful`
- `test_annotation_shopping_intent`
- `test_annotation_task_intent`
- `test_annotation_clarify_intent`
- `test_no_raw_text_in_log`

### Integration test (~1)
- `test_full_pipeline_with_registry_gate` -- command in, decision out, verify log

### Regression
- Full test suite must pass

---

## Code Touchpoints

| File | Change |
|------|--------|
| `agent_registry/config.py` | Add `is_agent_registry_core_enabled()` |
| `graphs/core_graph.py` | Add `_annotate_registry_capabilities()`; call from `process_command()` when flag enabled |
| `tests/test_core_graph_registry_gate.py` | New: unit + integration tests |

---

## Dependencies

- ST-018 (ADR): architecture documented and approved
- ST-019 (capabilities lookup): `CapabilitiesLookup` class must exist
