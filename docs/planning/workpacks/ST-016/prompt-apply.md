# Codex APPLY Prompt — ST-016: Real Schema Breaking-Change Detection

## Role
You are an implementation agent. Apply the changes described below exactly.

## Allowed files (whitelist)
- `skills/schema-bump/scripts/check_breaking_changes.py`
- `skills/schema-bump/fixtures/example_deleted_field.schema.json` (NEW)
- `skills/schema-bump/fixtures/example_type_change.schema.json` (NEW)
- `skills/schema-bump/fixtures/example_new_required.schema.json` (NEW)
- `skills/schema-bump/fixtures/example_optional_added.schema.json` (NEW)
- `contracts/schemas/.baseline/command.schema.json` (NEW)
- `contracts/schemas/.baseline/decision.schema.json` (NEW)
- `tests/test_skill_checks.py`

## Forbidden files
- `skills/schema_bump.py` — do NOT modify
- `contracts/schemas/command.schema.json` — do NOT modify
- `contracts/schemas/decision.schema.json` — do NOT modify
- `contracts/VERSION` — do NOT modify
- `.github/workflows/ci.yml` — do NOT modify
- `routers/**`, `graphs/**`, `agent_registry/**`, `app/**`

## STOP-THE-LINE
If anything deviates from expectations or you need to modify files outside the whitelist, STOP and report.

---

## Step 1: Replace `skills/schema-bump/scripts/check_breaking_changes.py`

**Current file** (full content):

```python
import argparse
import json
from pathlib import Path


DEFAULT_OLD_SCHEMA_PATH = (
    Path(__file__).resolve().parents[1] / "fixtures" / "example.schema.json"
)
DEFAULT_NEW_SCHEMA_PATH = (
    Path(__file__).resolve().parents[1] / "fixtures" / "example.schema.next.json"
)


def _load_required_fields(schema: dict) -> set[str]:
    return set(schema.get("required", []))


def find_breaking_changes(old_schema_path: Path, new_schema_path: Path) -> list[str]:
    old_schema = json.loads(old_schema_path.read_text(encoding="utf-8"))
    new_schema = json.loads(new_schema_path.read_text(encoding="utf-8"))

    old_required = _load_required_fields(old_schema)
    new_required = _load_required_fields(new_schema)

    removed_required = sorted(old_required - new_required)
    return [f"Removed required field: {field}" for field in removed_required]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check schemas for breaking changes.")
    parser.add_argument("--old", type=Path, default=DEFAULT_OLD_SCHEMA_PATH)
    parser.add_argument("--new", type=Path, default=DEFAULT_NEW_SCHEMA_PATH)
    args = parser.parse_args()

    breaking = find_breaking_changes(args.old, args.new)
    if breaking:
        for issue in breaking:
            print(f"BREAKING: {issue}")
        return 1

    print("No breaking changes detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

**Replace with** (exact content):

```python
import argparse
import json
from pathlib import Path


DEFAULT_OLD_SCHEMA_PATH = (
    Path(__file__).resolve().parents[1] / "fixtures" / "example.schema.json"
)
DEFAULT_NEW_SCHEMA_PATH = (
    Path(__file__).resolve().parents[1] / "fixtures" / "example.schema.next.json"
)

CONTRACTS_DIR = Path(__file__).resolve().parents[3] / "contracts" / "schemas"
BASELINE_DIR = CONTRACTS_DIR / ".baseline"

SCHEMA_FILES = ["command.schema.json", "decision.schema.json"]


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


if __name__ == "__main__":
    raise SystemExit(main())
```

---

## Step 2: Create 4 test fixture files

All in `skills/schema-bump/fixtures/`. All compare against `example.schema.json` which has: `properties: {id: string, status: string}`, `required: [id, status]`.

**Create `skills/schema-bump/fixtures/example_deleted_field.schema.json`:**
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

**Create `skills/schema-bump/fixtures/example_type_change.schema.json`:**
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

**Create `skills/schema-bump/fixtures/example_new_required.schema.json`:**
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

**Create `skills/schema-bump/fixtures/example_optional_added.schema.json`:**
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

---

## Step 3: Create baseline directory with exact copies

```bash
mkdir -p contracts/schemas/.baseline
cp contracts/schemas/command.schema.json contracts/schemas/.baseline/command.schema.json
cp contracts/schemas/decision.schema.json contracts/schemas/.baseline/decision.schema.json
```

These must be **byte-identical** to current schemas.

---

## Step 4: Add 6 tests to `tests/test_skill_checks.py`

Append the following 6 tests at the end of the file (after existing `test_release_sanity_includes_decision_log_audit`):

```python


def test_detect_field_deletion():
    script = load_script(
        BASE_DIR / "skills" / "schema-bump" / "scripts" / "check_breaking_changes.py"
    )
    old = BASE_DIR / "skills" / "schema-bump" / "fixtures" / "example.schema.json"
    new = BASE_DIR / "skills" / "schema-bump" / "fixtures" / "example_deleted_field.schema.json"
    breaking = script["find_breaking_changes"](old, new)
    assert any("Removed property: status" in b for b in breaking)


def test_detect_type_change():
    script = load_script(
        BASE_DIR / "skills" / "schema-bump" / "scripts" / "check_breaking_changes.py"
    )
    old = BASE_DIR / "skills" / "schema-bump" / "fixtures" / "example.schema.json"
    new = BASE_DIR / "skills" / "schema-bump" / "fixtures" / "example_type_change.schema.json"
    breaking = script["find_breaking_changes"](old, new)
    assert any("Type changed for property 'status': string -> object" in b for b in breaking)


def test_detect_new_required_field():
    script = load_script(
        BASE_DIR / "skills" / "schema-bump" / "scripts" / "check_breaking_changes.py"
    )
    old = BASE_DIR / "skills" / "schema-bump" / "fixtures" / "example.schema.json"
    new = BASE_DIR / "skills" / "schema-bump" / "fixtures" / "example_new_required.schema.json"
    breaking = script["find_breaking_changes"](old, new)
    assert any("New required field: name" in b for b in breaking)


def test_detect_removed_required_backward_compat():
    script = load_script(
        BASE_DIR / "skills" / "schema-bump" / "scripts" / "check_breaking_changes.py"
    )
    old = BASE_DIR / "skills" / "schema-bump" / "fixtures" / "example.schema.json"
    new = BASE_DIR / "skills" / "schema-bump" / "fixtures" / "example_deleted_field.schema.json"
    breaking = script["find_breaking_changes"](old, new)
    assert any("Removed required field: status" in b for b in breaking)


def test_non_breaking_optional_addition():
    script = load_script(
        BASE_DIR / "skills" / "schema-bump" / "scripts" / "check_breaking_changes.py"
    )
    old = BASE_DIR / "skills" / "schema-bump" / "fixtures" / "example.schema.json"
    new = BASE_DIR / "skills" / "schema-bump" / "fixtures" / "example_optional_added.schema.json"
    breaking = script["find_breaking_changes"](old, new)
    assert breaking == []


def test_real_schemas_against_baseline_no_breaking():
    script = load_script(
        BASE_DIR / "skills" / "schema-bump" / "scripts" / "check_breaking_changes.py"
    )
    breaking = script["compare_all_schemas"]()
    assert breaking == []
```

---

## Verification

After applying all changes, run:

```bash
# Full test suite (expect 220 passed)
python3 -m pytest tests/ -v --tb=short

# Just skill checks (expect 12 tests)
python3 -m pytest tests/test_skill_checks.py -v --tb=short

# Schema bump check via module (expect "No breaking changes detected.")
python3 -m skills.schema_bump check

# Explicit old/new backward compat (expect exit 0)
python3 skills/schema-bump/scripts/check_breaking_changes.py --old skills/schema-bump/fixtures/example.schema.json --new skills/schema-bump/fixtures/example.schema.next.json

# Baseline files exist and match
ls contracts/schemas/.baseline/command.schema.json contracts/schemas/.baseline/decision.schema.json
diff contracts/schemas/command.schema.json contracts/schemas/.baseline/command.schema.json
diff contracts/schemas/decision.schema.json contracts/schemas/.baseline/decision.schema.json
```
