# Workpack: ST-018 — ADR-005 Update and Integration Diagram

**Status:** Ready
**Story:** `docs/planning/epics/EP-007/stories/ST-018-adr-005-update-integration-scope.md`

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-007/epic.md` |
| Story | `docs/planning/epics/EP-007/stories/ST-018-adr-005-update-integration-scope.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q3-agent-registry-integration.md` |
| ADR-005 (current) | `docs/adr/ADR-005-internal-agent-contract-v0.md` |
| ADR index | `docs/_indexes/adr-index.md` |
| Diagrams index | `docs/_indexes/diagrams-index.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

ADR-005 updated with integration status, Phase 1 core pipeline gate plan, and feature flag requirements. PlantUML diagram created showing registry in decision flow. Indexes updated.

## Acceptance Criteria

1. ADR-005 has "Integration Status" section (shadow=integrated, assist=integrated, core=not yet)
2. ADR-005 has "Phase 1: Core Pipeline Gate" section (annotation gate, `AGENT_REGISTRY_CORE_ENABLED` flag, no behavior change)
3. `docs/diagrams/agent-registry-integration.puml` exists showing V2 pipeline with registry
4. ADR and diagrams indexes updated
5. No files outside `docs/` modified

---

## Files to Change

| File | Change |
|------|--------|
| `docs/adr/ADR-005-internal-agent-contract-v0.md` | Add 3 new sections (Integration Status, Phase 1, Feature Flags) |
| `docs/diagrams/agent-registry-integration.puml` | New: PlantUML diagram |
| `docs/_indexes/adr-index.md` | Update ADR-005 entry date |
| `docs/_indexes/diagrams-index.md` | Add new diagram row |

---

## Implementation Plan

### Step 1: Add "Integration Status" section to ADR-005

Append after existing "Последствия" section:

```markdown
## Integration Status

| Component | File | Status | Flag |
|-----------|------|--------|------|
| Shadow agent invoker | `routers/agent_invoker_shadow.py` | Integrated | `SHADOW_AGENT_INVOKER_ENABLED` |
| Assist mode hints | `routers/assist/runner.py` | Integrated | `ASSIST_AGENT_HINTS_ENABLED` |
| Core pipeline | `graphs/core_graph.py` | Not yet integrated | `AGENT_REGISTRY_CORE_ENABLED` (planned) |
```

### Step 2: Add "Phase 1: Core Pipeline Gate" section

```markdown
## Phase 1: Core Pipeline Gate

Approach: registry capabilities lookup annotates decisions with agent metadata.
- No behavior change to deterministic baseline
- Flag: `AGENT_REGISTRY_CORE_ENABLED` (default: false)
- Gate queries registry, attaches capability snapshot to trace log
- Deterministic baseline always executes regardless of registry state
```

### Step 3: Add "Feature Flag Requirements" section

Table with all 4 registry-related flags:

| Flag | Component | Default | Purpose |
|------|-----------|---------|---------|
| `AGENT_REGISTRY_ENABLED` | Registry loader | false | Master switch |
| `SHADOW_AGENT_INVOKER_ENABLED` | Shadow invoker | false | Shadow execution |
| `ASSIST_AGENT_HINTS_ENABLED` | Assist runner | false | Entity hints |
| `AGENT_REGISTRY_CORE_ENABLED` | Core pipeline | false | Registry annotation gate |

Rule: all flags default false; any error/timeout → deterministic fallback.

### Step 4: Create PlantUML diagram

`docs/diagrams/agent-registry-integration.puml` showing V2 pipeline:
- CommandDTO → V2 Router → normalize → shadow_router → assist_hints (with registry) → core_graph → shadow_agents (with registry) → partial_trust → DecisionDTO
- Agent Registry as shared component
- Core pipeline gate marked "Phase 1 — planned"

### Step 5: Update indexes

- `docs/_indexes/adr-index.md`: update ADR-005 date to 2026-02-09
- `docs/_indexes/diagrams-index.md`: add row for agent-registry-integration.puml

---

## Verification Commands

```bash
# ADR-005 sections
grep -c "## Integration Status" docs/adr/ADR-005-internal-agent-contract-v0.md        # 1
grep -c "## Phase 1" docs/adr/ADR-005-internal-agent-contract-v0.md                   # 1
grep -c "AGENT_REGISTRY_CORE_ENABLED" docs/adr/ADR-005-internal-agent-contract-v0.md  # >=1

# Existing sections preserved
grep -c "## Контекст" docs/adr/ADR-005-internal-agent-contract-v0.md                  # 1
grep -c "## Решение" docs/adr/ADR-005-internal-agent-contract-v0.md                   # 1

# Diagram
test -f docs/diagrams/agent-registry-integration.puml && echo "OK"
head -1 docs/diagrams/agent-registry-integration.puml | grep "@startuml"
tail -1 docs/diagrams/agent-registry-integration.puml | grep "@enduml"

# Indexes
grep "agent-registry-integration" docs/_indexes/diagrams-index.md
grep "ADR-005" docs/_indexes/adr-index.md | grep "2026-02"

# Docs-only
git diff --name-only | grep -v "^docs/" && echo "FAIL" || echo "OK: docs-only"

# Tests still pass
python3 -m pytest tests/ -q --tb=no
```

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| ADR-005 scope disagreement | Low | Low | Additive update only, Human gate |

## Rollback

- `git revert <commit>` restores ADR-005, removes diagram, reverts indexes
- Zero code/runtime impact

## APPLY Boundaries

**Allowed:** `docs/adr/ADR-005-*.md`, `docs/diagrams/*.puml`, `docs/_indexes/*.md`
**Forbidden:** everything outside `docs/`
