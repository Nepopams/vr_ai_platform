# ST-018: ADR-005 Update and Integration Diagram

**Epic:** EP-007 (Agent Registry Integration)
**Status:** Ready
**Flags:** contract_impact=no, adr_needed=yes, diagrams_needed=yes

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-007/epic.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q3-agent-registry-integration.md` |
| ADR-005 (current) | `docs/adr/ADR-005-internal-agent-contract-v0.md` |
| ADR-002 | `docs/adr/ADR-002-agent-model-execution-boundaries-mvp.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

ADR-005 was accepted on 2026-01-13 and documents the Internal Agent Contract v0.
Since then, shadow invoker and assist hints were built and integrated. ADR-005
does not document:

1. The phased integration plan (shadow -> assist -> core pipeline)
2. Integration status of existing consumers
3. Boundaries for core pipeline integration
4. Feature flag requirements for integration phase
5. A diagram showing registry in the decision flow

## User Value

As a platform developer, I want ADR-005 to reflect actual integration status and
next steps, so I understand boundaries and risks of registry-aware core pipeline routing.

## Scope

### In scope

- Add "Integration Status" section to ADR-005
- Add "Phase 1: Core Pipeline Gate" section
- Add "Feature Flag Requirements" section
- Create PlantUML integration diagram (`docs/diagrams/agent-registry-integration.puml`)
- Update `docs/_indexes/adr-index.md` and `docs/_indexes/diagrams-index.md`

### Out of scope

- Changes to ADR-005 "Decision" section (v0 contract rules unchanged)
- New ADR (this is an update to existing)
- Any code changes
- Changes to external contracts

---

## Acceptance Criteria

### AC-1: ADR-005 includes integration status section
```
Given ADR-005
When the update is applied
Then "## Integration Status" exists
And lists shadow invoker as "integrated, flag-gated"
And lists assist hints as "integrated, flag-gated"
And lists core pipeline as "not yet integrated"
```

### AC-2: ADR-005 includes Phase 1 integration plan
```
Given the updated ADR-005
Then "## Phase 1: Core Pipeline Gate" exists
And describes: registry capabilities lookup annotates decisions
And states: no behavior change to deterministic baseline
And lists flag AGENT_REGISTRY_CORE_ENABLED (default: false)
```

### AC-3: Integration diagram exists and is accurate
```
Given docs/diagrams/agent-registry-integration.puml
When rendered
Then shows CommandDTO -> V2 Router -> core_graph with registry gate -> DecisionDTO
And shadow invoker and assist hints as side channels
```

### AC-4: Indexes updated
```
Given docs/_indexes/diagrams-index.md and adr-index.md
When ST-018 is complete
Then both are updated with new/modified entries
```

### AC-5: No code changes
```
Given this story
Then no files outside docs/ are modified
```

---

## Test Strategy

### No automated tests (docs-only story)

### Verification
- ADR-005 well-formed with required sections
- PlantUML renders without errors
- Indexes consistent

---

## Code Touchpoints

| File | Change |
|------|--------|
| `docs/adr/ADR-005-internal-agent-contract-v0.md` | Add Integration Status, Phase 1, Feature Flags sections |
| `docs/diagrams/agent-registry-integration.puml` | New: PlantUML integration diagram |
| `docs/_indexes/adr-index.md` | Update ADR-005 entry |
| `docs/_indexes/diagrams-index.md` | Add diagram entry |

---

## Dependencies

- None (foundation story, docs-only)
- Blocks: ST-019, ST-020
