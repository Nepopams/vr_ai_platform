# Codex APPLY Prompt — ST-015: CI Completeness: decision_log_audit + release_sanity Orchestrator

## Role
You are an implementation agent. Apply the changes described below exactly.

## Allowed files (whitelist)
- `.github/workflows/ci.yml`
- `tests/test_skill_checks.py`

## Forbidden files
- `skills/**` — do NOT modify any skill scripts
- `contracts/**`, `graphs/**`, `routers/**`, `agent_registry/**`, `app/**`

## STOP-THE-LINE
If anything deviates from expectations or you need to modify files outside the whitelist, STOP and report.

---

## Context

Story ST-015 replaces individual CI skill steps (`Validate contracts`, `Graph sanity`) with the `release_sanity` orchestrator, which already includes contract-checker + decision-log-audit + graph-sanity. The `Check schema version` step remains separate.

### Key finding from PLAN phase
- `skills/release-sanity/` has a **hyphen** in directory name and **no `__init__.py`** — cannot be invoked as `python -m skills.release_sanity`
- Correct invocation: `python3 skills/release-sanity/scripts/release_sanity.py`

---

## Step 1: Update `.github/workflows/ci.yml`

**Current file** (full content to replace):

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: Run tests
        run: python -m pytest tests/ -v --tb=short

      - name: Validate contracts
        run: python -m skills.contract_checker

      - name: Check schema version
        run: python -m skills.schema_bump check

      - name: Graph sanity
        run: python -m skills.graph_sanity
```

**Replace with** (exact content):

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: Run tests
        run: python -m pytest tests/ -v --tb=short

      - name: Check schema version
        run: python -m skills.schema_bump check

      - name: Release sanity
        run: python3 skills/release-sanity/scripts/release_sanity.py
```

Changes:
- **Removed** "Validate contracts" step (`python -m skills.contract_checker`)
- **Removed** "Graph sanity" step (`python -m skills.graph_sanity`)
- **Added** "Release sanity" step (`python3 skills/release-sanity/scripts/release_sanity.py`)
- **Kept** "Check schema version" step (moved before Release sanity for logical ordering)
- **Kept** "Run tests" step unchanged

---

## Step 2: Add 2 tests to `tests/test_skill_checks.py`

**Current file** (full content):

```python
import runpy
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


def load_script(path: Path) -> dict:
    return runpy.run_path(str(path), run_name="__test__")


def test_contract_checker_fixtures():
    script = load_script(
        BASE_DIR / "skills" / "contract-checker" / "scripts" / "validate_contracts.py"
    )
    failures = script["validate_fixtures"]()
    assert failures == []


def test_decision_log_audit_fixture():
    script = load_script(
        BASE_DIR
        / "skills"
        / "decision-log-audit"
        / "scripts"
        / "audit_decision_logs.py"
    )
    log_path = (
        BASE_DIR
        / "skills"
        / "decision-log-audit"
        / "fixtures"
        / "sample_decision_log.jsonl"
    )
    errors = script["audit_log"](log_path)
    assert errors == []


def test_graph_sanity_runs():
    script = load_script(
        BASE_DIR / "skills" / "graph-sanity" / "scripts" / "run_graph_suite.py"
    )
    fixture_path = (
        BASE_DIR
        / "skills"
        / "contract-checker"
        / "fixtures"
        / "valid_command_create_task.json"
    )
    failures = script["run_graph_suite"]([fixture_path])
    assert failures == []


def test_schema_bump_breaking_changes():
    script = load_script(
        BASE_DIR
        / "skills"
        / "schema-bump"
        / "scripts"
        / "check_breaking_changes.py"
    )
    old_schema = BASE_DIR / "skills" / "schema-bump" / "fixtures" / "example.schema.json"
    new_schema = (
        BASE_DIR / "skills" / "schema-bump" / "fixtures" / "example.schema.next.json"
    )
    breaking = script["find_breaking_changes"](old_schema, new_schema)
    assert breaking == []
```

**Replace with** (exact content — adds 2 new tests at the end):

```python
import runpy
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


def load_script(path: Path) -> dict:
    return runpy.run_path(str(path), run_name="__test__")


def test_contract_checker_fixtures():
    script = load_script(
        BASE_DIR / "skills" / "contract-checker" / "scripts" / "validate_contracts.py"
    )
    failures = script["validate_fixtures"]()
    assert failures == []


def test_decision_log_audit_fixture():
    script = load_script(
        BASE_DIR
        / "skills"
        / "decision-log-audit"
        / "scripts"
        / "audit_decision_logs.py"
    )
    log_path = (
        BASE_DIR
        / "skills"
        / "decision-log-audit"
        / "fixtures"
        / "sample_decision_log.jsonl"
    )
    errors = script["audit_log"](log_path)
    assert errors == []


def test_graph_sanity_runs():
    script = load_script(
        BASE_DIR / "skills" / "graph-sanity" / "scripts" / "run_graph_suite.py"
    )
    fixture_path = (
        BASE_DIR
        / "skills"
        / "contract-checker"
        / "fixtures"
        / "valid_command_create_task.json"
    )
    failures = script["run_graph_suite"]([fixture_path])
    assert failures == []


def test_schema_bump_breaking_changes():
    script = load_script(
        BASE_DIR
        / "skills"
        / "schema-bump"
        / "scripts"
        / "check_breaking_changes.py"
    )
    old_schema = BASE_DIR / "skills" / "schema-bump" / "fixtures" / "example.schema.json"
    new_schema = (
        BASE_DIR / "skills" / "schema-bump" / "fixtures" / "example.schema.next.json"
    )
    breaking = script["find_breaking_changes"](old_schema, new_schema)
    assert breaking == []


def test_release_sanity_runs():
    script = load_script(
        BASE_DIR / "skills" / "release-sanity" / "scripts" / "release_sanity.py"
    )
    failures = script["run_checks"]()
    assert failures == []


def test_release_sanity_includes_decision_log_audit():
    script = load_script(
        BASE_DIR / "skills" / "release-sanity" / "scripts" / "release_sanity.py"
    )
    checks = script["CHECKS"]
    check_names = [name for name, _ in checks]
    assert "contract-checker" in check_names
    assert "decision-log-audit" in check_names
    assert "graph-sanity" in check_names
```

Changes:
- **Added** `test_release_sanity_runs()` — loads release_sanity.py, calls `run_checks()`, asserts no failures
- **Added** `test_release_sanity_includes_decision_log_audit()` — loads script, reads `CHECKS` list (list of tuples `(name, path)`), asserts all 3 check names present

---

## Verification

After applying changes, run:

```bash
# Full test suite (expect 204 passed)
python3 -m pytest tests/ -v --tb=short

# Just skill checks (expect 6 tests)
python3 -m pytest tests/test_skill_checks.py -v --tb=short

# CI file checks
grep -c "release_sanity" .github/workflows/ci.yml        # expect 1
grep -c "skills.contract_checker" .github/workflows/ci.yml  # expect 0
grep -c "skills.graph_sanity" .github/workflows/ci.yml      # expect 0
grep -c "skills.schema_bump" .github/workflows/ci.yml       # expect 1
```
