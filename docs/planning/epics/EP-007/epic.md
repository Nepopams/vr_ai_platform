# EP-007: Agent Registry Integration into Core Pipeline

**Status:** Ready
**Initiative:** `docs/planning/initiatives/INIT-2026Q3-agent-registry-integration.md`
**Sprint:** S05
**Owner:** TBD

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Roadmap | `docs/planning/strategy/roadmap.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q3-agent-registry-integration.md` |
| ADR-005 | `docs/adr/ADR-005-internal-agent-contract-v0.md` |
| ADR-002 | `docs/adr/ADR-002-agent-model-execution-boundaries-mvp.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

The agent registry v0 was scaffolded during earlier sprints and is already used
in two side-channel integrations:

1. **Shadow agent invoker** (`routers/agent_invoker_shadow.py`) -- runs registry agents
   in fire-and-forget shadow mode, logging diffs against baseline decisions.
2. **Assist-mode agent hints** (`routers/assist/runner.py`) -- uses registry to find
   `extract_entities.shopping` agents for entity extraction hints.

Both paths are fully gated by feature flags and have zero impact on the core decision.

**What is missing:**

- `graphs/core_graph.py` does not reference the agent registry at all.
- No capabilities lookup service for the main pipeline to query.
- ADR-005 does not reflect transition from "scaffolded" to "integrated" status.
- No integration diagram shows registry in the decision flow.

## Goal

Lay the groundwork for registry-driven agent routing in the core pipeline by:

1. Updating ADR-005 to document the integration scope and phased rollout plan.
2. Creating a capabilities lookup service that the core pipeline can query.
3. Adding a registry-aware gate to `core_graph.py` (behind a feature flag) that
   annotates decisions with available agent capabilities without changing behavior.

## Scope

### In scope

- ADR-005 update: transition from "scaffolded" to "integration phase 1"
- Integration diagram (PlantUML)
- Capabilities lookup service: thin query layer over the registry
- Core pipeline registry gate: flag-gated annotation (no behavior change)
- Feature flag: `AGENT_REGISTRY_CORE_ENABLED` (default: false)
- Unit and integration tests

### Out of scope

- Marketplace of external agents
- Autonomous multi-step agents
- Replacing baseline decision logic with agent-driven decisions
- Enabling agents by default in production
- Changes to CommandDTO/DecisionDTO external contracts
- Shadow/assist runner changes (already done)

## Stories

| Story ID | Title | Status | Flags |
|----------|-------|--------|-------|
| [ST-018](stories/ST-018-adr-005-update-integration-scope.md) | ADR-005 update and integration diagram | Ready | contract_impact=no, adr_needed=yes, diagrams_needed=yes |
| [ST-019](stories/ST-019-capabilities-lookup-service.md) | Capabilities lookup service for agent registry | Ready | contract_impact=no, adr_needed=none, diagrams_needed=none |
| [ST-020](stories/ST-020-core-graph-registry-gate.md) | Core pipeline registry-aware gate (flag-gated) | Ready (dep: ST-018, ST-019) | contract_impact=no, adr_needed=none, diagrams_needed=none |

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| Agent registry v0 scaffolding | Internal | Done |
| Shadow agent invoker | Internal | Done |
| Assist-mode agent hints | Internal | Done |
| ADR-005 (Accepted) | ADR | Done -- needs update (ST-018) |
| ADR-002 (Agent boundaries) | ADR | Done |
| Existing test suite (202 tests) | Internal | Passing |
| EP-006 (SemVer and CI) | Sprint co-tenant | In parallel -- no code overlap |

### Story ordering

```
ST-018 (ADR + diagram)
  |
  v
ST-019 (capabilities lookup service)
  |
  v
ST-020 (core pipeline gate)
```

- ST-018 first: establishes integration scope and architecture.
- ST-019 depends on ST-018 (architecture approved).
- ST-020 depends on both ST-018 and ST-019.

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Integration gate adds latency to core pipeline | Low | Medium | Flag-gated (default: off). In-memory cached registry. |
| Registry changes break shadow/assist paths | Low | High | New service layer; does not modify existing code. |
| ADR-005 update scope disagreement | Low | Low | Additive update, not replacing existing content. Human gate. |
| Co-tenancy with EP-006 causes merge conflicts | Very Low | Low | No overlapping files. |

## Readiness Report

### Ready
- **ST-018** -- No blockers. Docs-only story (~2h).
- **ST-019** -- All registry infrastructure exists. Clear boundaries (~1 day).
- **ST-020** -- All inputs well-defined. Depends on ST-018 + ST-019 (~1 day).

### Conditional agents needed
- ST-018: `adr_needed=yes` -> adr-designer, `diagrams_needed=yes` -> diagram-steward
