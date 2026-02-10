# Codex PLAN Prompt — ST-015: CI Completeness: decision_log_audit + release_sanity Orchestrator

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

Story ST-015 replaces individual CI skill steps (`contract_checker`, `graph_sanity`) with the `release_sanity` orchestrator and adds tests for it.

## Tasks

### Task 1: Inspect CI workflow
```bash
cat .github/workflows/ci.yml
```
Document current steps: names, run commands, order.

### Task 2: Inspect release_sanity script
```bash
cat skills/release-sanity/scripts/release_sanity.py
```
Confirm:
- `CHECKS` list includes `contract-checker`, `decision-log-audit`, `graph-sanity`
- `run_checks()` returns `list[str]` of failures
- `main()` exits 0 on success, 1 on failure

### Task 3: Inspect existing skill check tests
```bash
cat tests/test_skill_checks.py
```
Confirm:
- `load_script()` helper pattern
- Existing test count (expect 4 tests)
- Import style and naming conventions

### Task 4: Check how release_sanity is invoked as module
```bash
cat skills/release-sanity/__init__.py 2>/dev/null || echo "no __init__.py"
ls skills/release-sanity/
cat skills/__init__.py 2>/dev/null || echo "no skills/__init__.py"
```
Determine the correct `python -m` invocation syntax.

### Task 5: Check skills package structure for module invocation
```bash
find skills/ -name "__init__.py" | head -20
find skills/ -name "__main__.py" | head -20
```
Determine if skills have `__main__.py` files or if they use `scripts/` entry points directly.

### Task 6: Verify release_sanity CHECKS list references
```bash
rg "CHECKS" skills/release-sanity/scripts/release_sanity.py
```
Confirm CHECKS list maps to:
- `contract-checker` → `skills/contract-checker/scripts/validate_contracts.py`
- `decision-log-audit` → `skills/decision-log-audit/scripts/audit_decision_logs.py`
- `graph-sanity` → `skills/graph-sanity/scripts/run_graph_suite.py`

### Task 7: Verify all skill scripts exist
```bash
ls -la skills/contract-checker/scripts/validate_contracts.py
ls -la skills/decision-log-audit/scripts/audit_decision_logs.py
ls -la skills/graph-sanity/scripts/run_graph_suite.py
```

### Task 8: Count current tests
```bash
rg "^def test_" tests/test_skill_checks.py | wc -l
python3 -m pytest tests/ --co -q 2>/dev/null | tail -1
```
Expect: 4 tests in test_skill_checks.py, 202 total.

---

## Expected findings format

```
## Findings

### CI Workflow
- Current steps: [list with names and run commands]
- Steps to remove: [list]
- Steps to keep: [list]

### release_sanity
- Module invocation: [python -m command or python3 path]
- CHECKS list: [confirmed contents]
- run_checks() signature: [confirmed]

### test_skill_checks.py
- load_script() pattern: [confirmed]
- Current test count: [N]
- Naming convention: [observed pattern]

### Module structure
- How skills are invoked in CI: [pattern]
- Correct release_sanity invocation: [command]

### Blockers
- [None expected / list if any]
```

---

## STOP-THE-LINE
If anything is unclear or deviates from expectations, STOP and report instead of guessing.
