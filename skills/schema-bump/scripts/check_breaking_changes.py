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
