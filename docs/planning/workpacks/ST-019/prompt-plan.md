# Codex PLAN Prompt — ST-019: Capabilities Lookup Service for Agent Registry

## Role
You are a read-only explorer. You MUST NOT create, edit, or delete any files.

## Allowed commands (whitelist)
- `ls`, `find`
- `cat`, `head`, `tail`
- `rg`, `grep`, `sed -n`
- `git status`, `git diff`

## Forbidden
- Any file modifications (edit/write/move/delete)
- Any network access
- Package install / system changes
- `git commit`, `git push`, migrations, DB ops

---

## Context

Story ST-019 creates a `CapabilitiesLookup` class in `agent_registry/capabilities_lookup.py` that consolidates agent filtering logic. Given a loaded `AgentRegistryV0`, it answers: "which enabled agents can handle intent X in mode Y?"

## Tasks

### Task 1: Inspect AgentRegistryV0 and AgentSpec models
```bash
cat agent_registry/v0_models.py
```
Confirm:
- `AgentSpec` fields: agent_id, enabled, mode, capabilities, runner, timeouts, privacy, llm_profile_id
- `AgentCapability` fields: capability_id, allowed_intents, risk_level
- `AgentRegistryV0` fields: registry_version, compat_adr, compat_note, agents
- All are frozen dataclasses

### Task 2: Inspect AgentRegistryV0Loader and load_capability_catalog
```bash
cat agent_registry/v0_loader.py
```
Confirm:
- `AgentRegistryV0Loader.load()` returns `AgentRegistryV0`
- `load_capability_catalog()` returns `dict[str, dict[str, Any]]` keyed by capability_id
- What keys each catalog entry has (allowed_modes, payload_allowlist, etc.)

### Task 3: Inspect capability catalog YAML
```bash
cat agent_registry/capabilities-v0.yaml
```
Confirm:
- Number of capabilities (expect 5: normalize_text, extract_entities.shopping, suggest_clarify, propose_plan.executionless, decision_candidate.shopping)
- Each has capability_id, purpose, allowed_modes, risk_level, etc.

### Task 4: Inspect agent registry YAML
```bash
cat agent_registry/agent-registry-v0.yaml
```
Confirm:
- Number of agents (expect 3)
- Each has agent_id, enabled, mode, capabilities with allowed_intents

### Task 5: Inspect existing registry test patterns
```bash
cat tests/test_agent_registry_v0.py
```
Understand:
- How tests create test fixtures (inline vs file-based)
- Import patterns for v0_models
- Naming conventions

### Task 6: Inspect agent_registry __init__.py and config
```bash
cat agent_registry/__init__.py
cat agent_registry/config.py
```
Confirm:
- Current exports (AgentRegistry, AgentRegistryLoader, IntentSpec, RegistryAgent from v1)
- No v0 exports in __init__ (v0 is imported directly from submodules)
- Config: is_agent_registry_enabled(), get_agent_registry_path()

### Task 7: Check for existing capabilities lookup or similar
```bash
rg "capabilities_lookup\|CapabilitiesLookup\|find_agents\|has_capability" agent_registry/ tests/
```
Confirm no existing module conflicts.

### Task 8: Check how shadow invoker and assist hints filter agents
```bash
rg "for.*agent.*in.*registry\|\.agents\|\.mode\|\.enabled\|allowed_intents" routers/agent_invoker_shadow.py routers/assist/runner.py
```
Understand existing ad-hoc filtering patterns that CapabilitiesLookup will consolidate.

### Task 9: Count current tests
```bash
python3 -m pytest tests/ --co -q 2>/dev/null | tail -1
```
Expect: 202 tests.

### Task 10: Verify no naming conflicts
```bash
ls agent_registry/capabilities_lookup.py 2>/dev/null || echo "does not exist"
ls tests/test_capabilities_lookup.py 2>/dev/null || echo "does not exist"
```
Confirm target files don't exist yet.

---

## Expected findings format

```
## Findings

### v0_models.py
- AgentSpec fields: [confirmed list]
- AgentCapability fields: [confirmed list]
- All frozen: [yes/no]

### v0_loader.py
- load() returns: [type]
- load_capability_catalog() returns: [type with key description]
- Catalog entry keys: [list]

### Registry data
- Agents count: [N]
- Capabilities count: [N]
- Agent modes: [list]
- Intents used: [list]

### Test patterns
- Fixture approach: [inline/file-based]
- Import style: [from agent_registry.v0_models import ...]
- Test naming: [test_<thing>_<scenario>]

### Existing filtering (shadow/assist)
- Shadow invoker pattern: [description]
- Assist hints pattern: [description]

### Current test count: [N]

### Blockers
- [None expected / list if any]
```

---

## STOP-THE-LINE
If anything is unclear or deviates from expectations, STOP and report instead of guessing.
