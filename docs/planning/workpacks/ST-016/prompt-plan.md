# Codex PLAN Prompt — ST-016: Real Schema Breaking-Change Detection

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

Story ST-016 extends `check_breaking_changes.py` to detect 3 additional breaking change categories (field deletion, type change, new required field), adds baseline schema comparison, and creates `.baseline/` with current schema copies.

## Tasks

### Task 1: Inspect check_breaking_changes.py
```bash
cat skills/schema-bump/scripts/check_breaking_changes.py
```
Confirm:
- `find_breaking_changes(old_path, new_path)` loads JSON, checks removed required only
- `main()` uses argparse with `--old`/`--new` defaulting to synthetic fixtures
- DEFAULT_OLD_SCHEMA_PATH and DEFAULT_NEW_SCHEMA_PATH point to fixtures

### Task 2: Inspect schema_bump.py module entry point
```bash
cat skills/schema_bump.py
```
Confirm:
- `check` subcommand delegates to `check_breaking_changes.py` with `--old`/`--new`
- CI calls `python -m skills.schema_bump check` (no flags → defaults)

### Task 3: Inspect existing test fixtures
```bash
cat skills/schema-bump/fixtures/example.schema.json
cat skills/schema-bump/fixtures/example.schema.next.json
```
Confirm: both have `id` and `status` properties, required: `[id, status]`.

### Task 4: Inspect real contract schemas (top-level properties and required)
```bash
cat contracts/schemas/command.schema.json | head -10
rg '"required"' contracts/schemas/command.schema.json | head -5
rg '"properties"' contracts/schemas/command.schema.json | head -5
cat contracts/schemas/decision.schema.json | head -20
rg '"required"' contracts/schemas/decision.schema.json | head -5
```
Understand top-level structure for baseline comparison.

### Task 5: Check if .baseline/ already exists
```bash
ls contracts/schemas/.baseline/ 2>/dev/null || echo "does not exist"
```

### Task 6: Inspect existing tests in test_skill_checks.py
```bash
cat tests/test_skill_checks.py
```
Confirm: `load_script()` pattern, current test count (expect 6), naming conventions.

### Task 7: Count current tests
```bash
rg "^def test_" tests/test_skill_checks.py | wc -l
```
Expect: 6 tests.

### Task 8: Verify CONTRACTS_DIR path calculation
```bash
python3 -c "from pathlib import Path; p = Path('skills/schema-bump/scripts/check_breaking_changes.py').resolve(); print(p.parents[3] / 'contracts' / 'schemas')"
```
Confirm the path resolves to `contracts/schemas/`.

---

## Expected findings format

```
## Findings

### check_breaking_changes.py
- find_breaking_changes: [current logic description]
- main() defaults: [paths]
- argparse flags: [--old, --new]

### schema_bump.py
- check subcommand: [delegation pattern]

### Test fixtures
- example.schema.json: [properties, required]
- example.schema.next.json: [properties, required, diff from example]

### Contract schemas (top-level)
- command.schema.json: required=[...], top-level properties=[...]
- decision.schema.json: required=[...], top-level properties=[...]

### Baseline
- .baseline/ exists: [yes/no]

### test_skill_checks.py
- Current test count: [N]
- load_script pattern: [confirmed]

### CONTRACTS_DIR path
- Resolves to: [path]

### Blockers
- [None expected / list if any]
```

---

## STOP-THE-LINE
If anything is unclear or deviates from expectations, STOP and report instead of guessing.
