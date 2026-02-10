# Codex APPLY — ST-018: ADR-005 Update and Integration Diagram

## Role
You are an implementation agent. Modify/create exactly the files specified below.

## Allowed files (whitelist)
- `docs/adr/ADR-005-internal-agent-contract-v0.md` (MODIFY — append sections)
- `docs/diagrams/agent-registry-integration.puml` (CREATE)
- `docs/_indexes/adr-index.md` (MODIFY — update row)
- `docs/_indexes/diagrams-index.md` (MODIFY — add row)

## Forbidden
- Any file outside `docs/`
- Any code changes
- Network access
- `git commit/push`

## STOP-THE-LINE
If anything is unclear — STOP and ask, do not guess.

---

## Step 1: Append "Integration Status" section to ADR-005

Open `docs/adr/ADR-005-internal-agent-contract-v0.md`.

**DO NOT modify** the existing sections (Контекст, Решение, Последствия, Связанные документы).

Append the following **after** the "## Связанные документы" section:

```markdown

## Integration Status

| Component | File | Status | Feature Flag |
|-----------|------|--------|-------------|
| Shadow agent invoker | `routers/agent_invoker_shadow.py` | Integrated, flag-gated | `shadow_agent_invoker_enabled` (from `routers.shadow_agent_config`) |
| Assist mode hints | `routers/assist/runner.py` | Integrated, flag-gated | `assist_agent_hints_enabled()` (from `routers/assist/config.py`) |
| Core pipeline | `graphs/core_graph.py` | Not yet integrated | `AGENT_REGISTRY_CORE_ENABLED` (planned, Phase 1) |

Notes:
- Shadow invoker: loads registry via `AgentRegistryV0Loader.load(path_override=...)`, filters by mode="shadow" and allowlist, fire-and-forget execution.
- Assist hints: loads registry via `AgentRegistryV0Loader.load()`, filters by mode="assist" and capability `extract_entities.shopping`, applies best candidate if matching.
- Core pipeline: no registry references as of S04. Phase 1 will add a read-only annotation gate.
```

## Step 2: Append "Phase 1: Core Pipeline Gate" section

Continue appending to ADR-005:

```markdown

## Phase 1: Core Pipeline Gate

**Approach:** Registry capabilities lookup annotates decisions with agent metadata (read-only probe).

- The core pipeline (`graphs/core_graph.py`) will query `CapabilitiesLookup` for agents matching the detected intent.
- A `registry_snapshot` will be attached to the decision trace log (NOT to DecisionDTO response).
- **No behavior change** to the deterministic baseline — baseline always executes regardless of registry state.
- Feature flag: `AGENT_REGISTRY_CORE_ENABLED` (env var, default: `false`).
- Any error or timeout in registry lookup → silently skipped, decision produced normally.

**V2 pipeline flow** (from `routers/v2.py`):
1. `normalize()`
2. `start_shadow_router()`
3. `apply_assist_hints()` ← uses registry (assist mode)
4. `plan()`
5. `validate_and_build()`
6. `invoke_shadow_agents()` ← uses registry (shadow mode)
7. `_maybe_apply_partial_trust()`
8. return decision

Phase 1 adds a registry annotation step inside `core_graph.process_command()`, gated by `AGENT_REGISTRY_CORE_ENABLED`.
```

## Step 3: Append "Feature Flag Requirements" section

Continue appending to ADR-005:

```markdown

## Feature Flag Requirements

All registry-related flags default to `false`. Any error or timeout in registry falls back to deterministic baseline.

| Flag | Component | Default | Source | Purpose |
|------|-----------|---------|--------|---------|
| `AGENT_REGISTRY_ENABLED` | Registry loader | `false` | `agent_registry/config.py` | Master switch for registry loading |
| `AGENT_REGISTRY_PATH` | Registry loader | `None` | `agent_registry/config.py` | Optional path override for registry YAML |
| `shadow_agent_invoker_enabled` | Shadow invoker | `false` | `routers/shadow_agent_config.py` | Enable shadow agent execution |
| `assist_agent_hints_enabled` | Assist runner | `false` | `routers/assist/config.py` | Enable agent entity hints |
| `AGENT_REGISTRY_CORE_ENABLED` | Core pipeline | `false` | `agent_registry/config.py` (planned) | Enable registry annotation gate (Phase 1) |
```

## Step 4: Create PlantUML diagram

Create `docs/diagrams/agent-registry-integration.puml` with the following content:

```plantuml
@startuml agent-registry-integration
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

title Agent Registry Integration in V2 Pipeline

Person(user, "User", "Sends natural language command")

System_Boundary(platform, "AI Platform") {
    Component(v2router, "V2 Router", "routers/v2.py", "Pipeline orchestrator")
    Component(normalize, "Normalize", "routers/v2.py", "Text normalization")
    Component(shadow_router, "Shadow Router", "routers/shadow_router.py", "LLM shadow suggestions")
    Component(assist_hints, "Assist Hints", "routers/assist/runner.py", "Entity extraction hints")
    Component(core_graph, "Core Graph", "graphs/core_graph.py", "Deterministic decision pipeline")
    Component(shadow_agents, "Shadow Agents", "routers/agent_invoker_shadow.py", "Shadow agent execution")
    Component(partial_trust, "Partial Trust", "routers/v2.py", "Controlled LLM trust")

    ComponentDb(registry, "Agent Registry", "agent_registry/", "File-based agent registry (YAML)")

    Component(registry_gate, "Registry Gate", "graphs/core_graph.py", "Phase 1: read-only annotation\n(AGENT_REGISTRY_CORE_ENABLED)")
}

System_Ext(consumer, "HomeTusk", "Product consumer")

Rel(user, v2router, "CommandDTO")
Rel(v2router, normalize, "1. normalize()")
Rel(v2router, shadow_router, "2. start_shadow_router()", "async")
Rel(v2router, assist_hints, "3. apply_assist_hints()")
Rel(v2router, core_graph, "4-5. plan() + validate_and_build()")
Rel(v2router, shadow_agents, "6. invoke_shadow_agents()", "fire-and-forget")
Rel(v2router, partial_trust, "7. _maybe_apply_partial_trust()")
Rel(v2router, consumer, "DecisionDTO")

Rel(assist_hints, registry, "lookup agents\n(mode=assist)", "flag-gated")
Rel(shadow_agents, registry, "lookup agents\n(mode=shadow)", "flag-gated")
Rel_D(registry_gate, registry, "lookup capabilities\n(Phase 1 — planned)", "flag-gated")
Rel(core_graph, registry_gate, "annotate trace", "if AGENT_REGISTRY_CORE_ENABLED")

SHOW_LEGEND()
@enduml
```

## Step 5: Update ADR index

In `docs/_indexes/adr-index.md`, find the line:

```
| ADR-005-P | Internal Agent Contract v0 (ABI) | accepted | 2026-01-XX | [Link](../adr/ADR-005-internal-agent-contract-v0.md) |
```

Replace it with:

```
| ADR-005-P | Internal Agent Contract v0 (ABI) | accepted | 2026-02-09 | [Link](../adr/ADR-005-internal-agent-contract-v0.md) |
```

(Only the date changes: `2026-01-XX` → `2026-02-09`)

## Step 6: Update diagrams index

In `docs/_indexes/diagrams-index.md`, add a new row to the table (after the last existing row):

```
| Agent Registry Integration | Component / Flow | Registry integration points in V2 pipeline | [Link](../diagrams/agent-registry-integration.puml) |
```

---

## Verification

After all changes, run:

```bash
# ADR-005 new sections
grep -c "## Integration Status" docs/adr/ADR-005-internal-agent-contract-v0.md        # expect: 1
grep -c "## Phase 1: Core Pipeline Gate" docs/adr/ADR-005-internal-agent-contract-v0.md # expect: 1
grep -c "## Feature Flag Requirements" docs/adr/ADR-005-internal-agent-contract-v0.md   # expect: 1
grep -c "AGENT_REGISTRY_CORE_ENABLED" docs/adr/ADR-005-internal-agent-contract-v0.md    # expect: >=2

# Existing sections preserved
grep -c "## Контекст" docs/adr/ADR-005-internal-agent-contract-v0.md                   # expect: 1
grep -c "## Решение" docs/adr/ADR-005-internal-agent-contract-v0.md                    # expect: 1
grep -c "## Последствия" docs/adr/ADR-005-internal-agent-contract-v0.md                # expect: 1

# Diagram exists and valid
test -f docs/diagrams/agent-registry-integration.puml && echo "OK"
head -1 docs/diagrams/agent-registry-integration.puml | grep "@startuml"
tail -1 docs/diagrams/agent-registry-integration.puml | grep "@enduml"

# Indexes updated
grep "ADR-005" docs/_indexes/adr-index.md | grep "2026-02-09"
grep "agent-registry-integration" docs/_indexes/diagrams-index.md

# Only docs modified
git diff --name-only | grep -v "^docs/" && echo "FAIL: non-docs" || echo "OK: docs-only"

# No secrets
grep -rn 'sk-\|api_key\|secret' docs/adr/ADR-005-internal-agent-contract-v0.md docs/diagrams/agent-registry-integration.puml; echo "Secrets check done"
```

Expected: all checks pass, docs-only changes, no secrets.
