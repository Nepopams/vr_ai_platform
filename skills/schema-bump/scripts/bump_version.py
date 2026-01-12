import argparse
import json
from pathlib import Path


DEFAULT_SCHEMA_PATH = (
    Path(__file__).resolve().parents[1] / "fixtures" / "example.schema.json"
)


def _parse_version(version: str) -> tuple[int, int, int]:
    parts = version.split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        raise ValueError(f"Invalid version format: {version}")
    return tuple(int(part) for part in parts)


def _format_version(parts: tuple[int, int, int]) -> str:
    return ".".join(str(part) for part in parts)


def bump_schema_version(schema_path: Path, part: str) -> str:
    data = json.loads(schema_path.read_text(encoding="utf-8"))
    current_version = data.get("x-version", "0.0.0")
    major, minor, patch = _parse_version(current_version)

    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "patch":
        patch += 1
    else:
        raise ValueError(f"Unknown bump part: {part}")

    new_version = _format_version((major, minor, patch))
    data["x-version"] = new_version
    schema_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return new_version


def main() -> int:
    parser = argparse.ArgumentParser(description="Bump schema metadata version.")
    parser.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_SCHEMA_PATH,
        help="Path to the schema JSON file.",
    )
    parser.add_argument(
        "--part",
        choices=["major", "minor", "patch"],
        default="patch",
        help="Which part of the version to bump.",
    )
    args = parser.parse_args()

    new_version = bump_schema_version(args.schema, args.part)
    print(f"Bumped schema version to {new_version} in {args.schema}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
