import argparse
import runpy
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
BUMP_SCRIPT = BASE_DIR / "schema-bump" / "scripts" / "bump_version.py"
CHECK_SCRIPT = BASE_DIR / "schema-bump" / "scripts" / "check_breaking_changes.py"


def main() -> None:
    parser = argparse.ArgumentParser(description="Schema bump utilities.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    bump_parser = subparsers.add_parser("bump", help="Bump schema metadata version.")
    bump_parser.add_argument("--schema")
    bump_parser.add_argument("--part", choices=["major", "minor", "patch"])

    check_parser = subparsers.add_parser("check", help="Check for breaking changes.")
    check_parser.add_argument("--old")
    check_parser.add_argument("--new")

    args = parser.parse_args()
    remaining = sys.argv[2:]

    if args.command == "bump":
        sys.argv = [str(BUMP_SCRIPT), *remaining]
        runpy.run_path(str(BUMP_SCRIPT), run_name="__main__")
    elif args.command == "check":
        sys.argv = [str(CHECK_SCRIPT), *remaining]
        runpy.run_path(str(CHECK_SCRIPT), run_name="__main__")


if __name__ == "__main__":
    main()
