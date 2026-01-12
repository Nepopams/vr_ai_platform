import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from graphs.core_graph import process_command


BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURE = BASE_DIR / "skills" / "contract-checker" / "fixtures" / "valid_command.json"
SCHEMA_PATH = BASE_DIR / "contracts" / "schemas" / "decision.schema.json"


def run_graph_suite(fixtures: list[Path]) -> list[str]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    failures: list[str] = []

    for fixture in fixtures:
        payload = json.loads(fixture.read_text(encoding="utf-8"))
        decision = process_command(payload)
        errors = sorted(validator.iter_errors(decision), key=lambda err: err.path)
        if errors:
            message = ", ".join(error.message for error in errors)
            failures.append(f"{fixture.name} produced invalid decision: {message}")

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Run core graph sanity suite.")
    parser.add_argument(
        "fixtures",
        nargs="*",
        type=Path,
        default=[DEFAULT_FIXTURE],
        help="Command fixture JSON files.",
    )
    args = parser.parse_args()

    failures = run_graph_suite(args.fixtures)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Graph sanity suite passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
