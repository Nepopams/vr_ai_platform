# Codex PLAN Prompt — ST-020: Core Pipeline Registry-Aware Gate

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

Story ST-020 adds a flag-gated registry annotation gate to `graphs/core_graph.py`. When `AGENT_REGISTRY_CORE_ENABLED=true`, `process_command()` queries `CapabilitiesLookup` for agents matching the detected intent and logs a snapshot. No decision logic changes.

## Tasks

### Task 1: Inspect core_graph.py process_command()
```bash
cat graphs/core_graph.py
```
Confirm:
- `process_command()` flow: validate → detect_intent → branching → build decision → validate → return
- Where `intent = detect_intent(text)` is called (expected ~line 190)
- Existing imports (json, re, datetime, pathlib, typing, uuid, jsonschema)
- No existing `logging` import

### Task 2: Inspect agent_registry/config.py
```bash
cat agent_registry/config.py
```
Confirm:
- `is_agent_registry_enabled()` exists
- `get_agent_registry_path()` exists
- No `is_agent_registry_core_enabled()` yet

### Task 3: Inspect CapabilitiesLookup from ST-019
```bash
cat agent_registry/capabilities_lookup.py
```
Confirm:
- `CapabilitiesLookup.__init__(registry, catalog)`
- `find_agents(intent, mode)` → `list[AgentSpec]`
- `AgentSpec` has `agent_id`, `mode`, `enabled`

### Task 4: Inspect AgentRegistryV0Loader.load()
```bash
rg "def load" agent_registry/v0_loader.py | head -5
rg "def load_capability_catalog" agent_registry/v0_loader.py
```
Confirm:
- `load(path_override=..., catalog_path_override=...)` → `AgentRegistryV0`
- `load_capability_catalog(catalog_path_override=...)` → `dict[str, dict]`

### Task 5: Check for existing logging in core_graph
```bash
rg "import logging|getLogger|_logger" graphs/core_graph.py
```
Confirm no existing logging setup.

### Task 6: Check for existing test files that test core_graph
```bash
rg "core_graph\|process_command" tests/ --files-with-matches
```
Understand existing test patterns for core_graph.

### Task 7: Inspect how other tests mock registry
```bash
rg "monkeypatch\|mock.*registry\|AgentRegistryV0Loader" tests/ | head -20
```
Understand mocking patterns used in project tests.

### Task 8: Count current tests
```bash
rg "^def test_" tests/ | wc -l
```
Expect: ~50+ test functions, 220 total collected.

---

## Expected findings format

```
## Findings

### core_graph.py
- process_command() line range: [start-end]
- intent = detect_intent(text) at line: [N]
- Existing imports: [list]
- logging: [present/absent]
- Return type: Dict[str, Any]

### agent_registry/config.py
- Functions: [list]
- is_agent_registry_core_enabled: [absent, confirmed]

### CapabilitiesLookup
- Constructor: [params]
- find_agents: [signature]
- AgentSpec accessible fields: [list]

### Loader
- load(): [signature]
- load_capability_catalog(): [signature]

### Existing core_graph tests
- Files: [list]
- Patterns: [monkeypatch / fixture-based / etc.]

### Test count: [N]

### Blockers
- [None expected / list if any]
```

---

## STOP-THE-LINE
If anything is unclear or deviates from expectations, STOP and report instead of guessing.
