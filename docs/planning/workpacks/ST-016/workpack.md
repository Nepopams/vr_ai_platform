# Workpack: ST-016 — Real Schema Breaking-Change Detection

**Status:** Ready
**Story:** `docs/planning/epics/EP-006/stories/ST-016-real-schema-breaking-change-detection.md`

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-006/epic.md` |
| Story | `docs/planning/epics/EP-006/stories/ST-016-real-schema-breaking-change-detection.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q3-semver-and-ci.md` |
| ADR-001 | `docs/adr/ADR-001-contract-versioning-compatibility-policy.md` |
| Schema bump check | `skills/schema-bump/scripts/check_breaking_changes.py` |
| Schema bump module | `skills/schema_bump.py` |
| Contract schemas | `contracts/schemas/command.schema.json`, `contracts/schemas/decision.schema.json` |
| Existing test fixtures | `skills/schema-bump/fixtures/example.schema.json`, `example.schema.next.json` |
| Existing tests | `tests/test_skill_checks.py` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

CI detects actual breaking changes in contract schemas by comparing current schemas against baseline copies. Detection covers: field deletion from properties, type change, new required field (plus existing: removed required field). Backward compat preserved for `--old`/`--new` CLI flags.

## Acceptance Criteria

1. Detect field deletion from properties → "Removed property: X"
2. Detect field type change → "Type changed for property 'X': old_type -> new_type"
3. Detect new required field → "New required field: X"
4. Removed required field still detected (backward compat)
5. Non-breaking change (add optional field) not flagged
6. CI checks real schemas against baseline (when no --old/--new flags)
7. Baseline directory contains copies of current schemas
8. All existing tests pass + new tests pass

---

## Files to Change

| File | Change |
|------|--------|
| `skills/schema-bump/scripts/check_breaking_changes.py` | Extend `find_breaking_changes()` with 3 new detections; add `compare_all_schemas()` for baseline comparison; update `main()` default to use baseline |
| `contracts/schemas/.baseline/command.schema.json` | **New:** exact copy of `contracts/schemas/command.schema.json` |
| `contracts/schemas/.baseline/decision.schema.json` | **New:** exact copy of `contracts/schemas/decision.schema.json` |
| `tests/test_skill_checks.py` | Add ~6 new tests for breaking-change detection |
| `skills/schema-bump/fixtures/example_deleted_field.schema.json` | **New:** test fixture — field removed from properties |
| `skills/schema-bump/fixtures/example_type_change.schema.json` | **New:** test fixture — type changed |
| `skills/schema-bump/fixtures/example_new_required.schema.json` | **New:** test fixture — new required field added |
| `skills/schema-bump/fixtures/example_optional_added.schema.json` | **New:** test fixture — optional field added (non-breaking) |

---

## Implementation Plan

### Step 1: Extend `find_breaking_changes()` in `check_breaking_changes.py`

Current function only detects removed required fields. Extend to detect:

1. **Removed property** — field in old `properties` missing from new `properties`
2. **Type change** — same property has different `type` value
3. **New required field** — field in new `required` not in old `required`

The extended function (exact replacement):

```python
def find_breaking_changes(old_schema_path: Path, new_schema_path: Path) -> list[str]:
    old_schema = json.loads(old_schema_path.read_text(encoding="utf-8"))
    new_schema = json.loads(new_schema_path.read_text(encoding="utf-8"))

    old_required = set(old_schema.get("required", []))
    new_required = set(new_schema.get("required", []))
    old_properties = old_schema.get("properties", {})
    new_properties = new_schema.get("properties", {})

    breaking: list[str] = []

    # Removed required field (existing behavior)
    for field in sorted(old_required - new_required):
        breaking.append(f"Removed required field: {field}")

    # New required field
    for field in sorted(new_required - old_required):
        breaking.append(f"New required field: {field}")

    # Removed property
    for prop in sorted(set(old_properties) - set(new_properties)):
        breaking.append(f"Removed property: {prop}")

    # Type change
    for prop in sorted(set(old_properties) & set(new_properties)):
        old_type = old_properties[prop].get("type")
        new_type = new_properties[prop].get("type")
        if old_type and new_type and old_type != new_type:
            breaking.append(f"Type changed for property '{prop}': {old_type} -> {new_type}")

    return breaking
```

### Step 2: Add `compare_all_schemas()` and update `main()`

Add a function that compares all contract schemas against their baselines:

```python
CONTRACTS_DIR = Path(__file__).resolve().parents[3] / "contracts" / "schemas"
BASELINE_DIR = CONTRACTS_DIR / ".baseline"

SCHEMA_FILES = ["command.schema.json", "decision.schema.json"]


def compare_all_schemas() -> list[str]:
    """Compare current contract schemas against baseline copies."""
    all_breaking: list[str] = []
    for schema_file in SCHEMA_FILES:
        current = CONTRACTS_DIR / schema_file
        baseline = BASELINE_DIR / schema_file
        if not baseline.exists():
            continue
        if not current.exists():
            continue
        issues = find_breaking_changes(baseline, current)
        for issue in issues:
            all_breaking.append(f"[{schema_file}] {issue}")
    return all_breaking
```

Update `main()` to run baseline comparison when no `--old`/`--new` flags:

```python
def main() -> int:
    parser = argparse.ArgumentParser(description="Check schemas for breaking changes.")
    parser.add_argument("--old", type=Path, default=None)
    parser.add_argument("--new", type=Path, default=None)
    args = parser.parse_args()

    if args.old and args.new:
        # Explicit comparison (backward compat)
        breaking = find_breaking_changes(args.old, args.new)
    else:
        # Default: compare real schemas against baseline
        breaking = compare_all_schemas()

    if breaking:
        for issue in breaking:
            print(f"BREAKING: {issue}")
        return 1

    print("No breaking changes detected.")
    return 0
```

### Step 3: Create baseline directory with current schemas

Copy `contracts/schemas/command.schema.json` → `contracts/schemas/.baseline/command.schema.json`
Copy `contracts/schemas/decision.schema.json` → `contracts/schemas/.baseline/decision.schema.json`

These must be **byte-identical** to current schemas.

### Step 4: Create test fixtures

4 small JSON schemas in `skills/schema-bump/fixtures/`:

**example_deleted_field.schema.json** — `status` property removed:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Example",
  "type": "object",
  "required": ["id"],
  "properties": {
    "id": {"type": "string"}
  },
  "additionalProperties": false
}
```

**example_type_change.schema.json** — `status` type changed to object:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Example",
  "type": "object",
  "required": ["id", "status"],
  "properties": {
    "id": {"type": "string"},
    "status": {"type": "object"}
  },
  "additionalProperties": false
}
```

**example_new_required.schema.json** — `name` added as required:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Example",
  "type": "object",
  "required": ["id", "status", "name"],
  "properties": {
    "id": {"type": "string"},
    "status": {"type": "string"},
    "name": {"type": "string"}
  },
  "additionalProperties": false
}
```

**example_optional_added.schema.json** — `description` added as optional (non-breaking):
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Example",
  "type": "object",
  "required": ["id", "status"],
  "properties": {
    "id": {"type": "string"},
    "status": {"type": "string"},
    "description": {"type": "string"}
  },
  "additionalProperties": false
}
```

All test against `example.schema.json` as the "old" baseline (has `id: string`, `status: string`, required: `[id, status]`).

### Step 5: Add tests to `tests/test_skill_checks.py`

6 new tests appended:

1. `test_detect_field_deletion` — old=example.schema.json, new=example_deleted_field.schema.json → contains "Removed property: status"
2. `test_detect_type_change` — old=example.schema.json, new=example_type_change.schema.json → contains "Type changed for property 'status': string -> object"
3. `test_detect_new_required_field` — old=example.schema.json, new=example_new_required.schema.json → contains "New required field: name"
4. `test_detect_removed_required_backward_compat` — old with required [id, status], new with required [id] → contains "Removed required field: status" (existing behavior)
5. `test_non_breaking_optional_addition` — old=example.schema.json, new=example_optional_added.schema.json → returns []
6. `test_real_schemas_against_baseline_no_breaking` — loads script, calls `compare_all_schemas()`, asserts `== []`

---

## Verification Commands

```bash
# Full test suite (expect 220 passed)
python3 -m pytest tests/ -v --tb=short

# Just skill checks (expect 12 tests)
python3 -m pytest tests/test_skill_checks.py -v --tb=short

# Schema bump check via module (expect "No breaking changes detected.")
python3 -m skills.schema_bump check

# Direct script (expect "No breaking changes detected.")
python3 skills/schema-bump/scripts/check_breaking_changes.py

# Explicit old/new (backward compat, expect exit 0)
python3 skills/schema-bump/scripts/check_breaking_changes.py --old skills/schema-bump/fixtures/example.schema.json --new skills/schema-bump/fixtures/example.schema.next.json

# Baseline files exist
ls contracts/schemas/.baseline/command.schema.json contracts/schemas/.baseline/decision.schema.json

# Baseline matches current
diff contracts/schemas/command.schema.json contracts/schemas/.baseline/command.schema.json
diff contracts/schemas/decision.schema.json contracts/schemas/.baseline/decision.schema.json
```

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Existing `test_schema_bump_breaking_changes` test breaks (uses explicit --old/--new) | Low | Low | Backward compat preserved — explicit paths still work |
| `compare_all_schemas()` fails if .baseline missing | Low | Low | `continue` on missing baseline |
| Nested property changes not detected | Medium | Low | Out of scope (top-level only per story) |

## Rollback

- `git revert <commit>` removes detection changes and baseline
- No contract/schema content changes (baseline is a copy)

## APPLY Boundaries

**Allowed:** `skills/schema-bump/scripts/check_breaking_changes.py`, `skills/schema-bump/fixtures/*`, `contracts/schemas/.baseline/*`, `tests/test_skill_checks.py`
**Forbidden:** `skills/schema_bump.py`, `contracts/schemas/command.schema.json`, `contracts/schemas/decision.schema.json`, `contracts/VERSION`, `.github/workflows/ci.yml`, `graphs/`, `routers/`, `agent_registry/`
