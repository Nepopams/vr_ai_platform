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
