# Codex PLAN — ST-018: ADR-005 Update and Integration Diagram

## Role
You are a read-only explorer. NO edits, NO file writes, NO network access.

## Allowed commands (whitelist)
- `ls`, `find`
- `cat`, `head`, `tail`
- `rg`, `grep`
- `sed -n`

## Forbidden
- Any file modifications
- Any network access
- `git commit/push`
- Package installs

## STOP-THE-LINE
If anything below is unclear or missing — STOP and report, do not guess.

---

## Context

Story ST-018 updates ADR-005 with integration status, Phase 1 core pipeline gate plan,
and feature flags. Also creates a PlantUML integration diagram.

This is a **docs-only story** (no code changes). The PLAN phase captures exact current
state of ADR-005 and codebase integration points.

## Exploration Tasks

### Task 1: Read current ADR-005 in full
```bash
cat docs/adr/ADR-005-internal-agent-contract-v0.md
```
**Report:** Full content. Note the section headers (we must preserve them unchanged).

### Task 2: Verify shadow agent invoker integration
```bash
rg "SHADOW_AGENT_INVOKER_ENABLED" routers/agent_invoker_shadow.py
rg "AgentRegistryV0Loader" routers/agent_invoker_shadow.py
head -30 routers/agent_invoker_shadow.py
```
**Report:** Exact flag name, how registry is loaded, file structure.

### Task 3: Verify assist mode agent hints integration
```bash
rg "ASSIST_AGENT_HINTS_ENABLED" routers/assist/runner.py
rg "AgentRegistryV0Loader" routers/assist/runner.py
```
**Report:** Exact flag name, how registry is used.

### Task 4: Verify core_graph.py has NO registry references
```bash
rg "agent_registry\|AgentRegistry\|AGENT_REGISTRY" graphs/core_graph.py
```
**Report:** Confirm no matches (core pipeline not yet integrated).

### Task 5: Check agent_registry/config.py for existing flags
```bash
cat agent_registry/config.py
```
**Report:** List all env var flags and their defaults.

### Task 6: Check V2 pipeline flow in routers/v2.py
```bash
cat routers/v2.py
```
**Report:** The `decide()` method flow — list the steps in order (normalize, shadow_router,
assist_hints, plan, validate_and_build, shadow_agents, partial_trust, etc.)

### Task 7: Check existing PlantUML diagrams for style reference
```bash
ls docs/diagrams/ 2>/dev/null || echo "No docs/diagrams/"
ls docs/plantuml/ 2>/dev/null
cat docs/plantuml/c4-lvl3.puml 2>/dev/null | head -30
```
**Report:** Existing diagram style, includes, naming conventions.

### Task 8: Check ADR index — current ADR-005 entry
```bash
grep "ADR-005" docs/_indexes/adr-index.md
```
**Report:** Current row content (ID, title, status, date, link).

### Task 9: Check diagrams index structure
```bash
cat docs/_indexes/diagrams-index.md
```
**Report:** Table header format for adding new row.

### Task 10: Check docs/diagrams/README.md if exists
```bash
cat docs/diagrams/README.md 2>/dev/null || echo "No README"
```
**Report:** Any guidelines for diagram placement/naming.

---

## Expected output format

For each task, report:
1. Task number and description
2. Findings (exact content, flag names, code paths)
3. Any issues or missing items

End with a summary: "All prerequisites verified" or list of blockers.
