import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator


BASE_DIR = Path(__file__).resolve().parents[3]
SCHEMA_PATH = BASE_DIR / "contracts" / "schemas" / "decision.schema.json"
DEFAULT_LOG_PATH = (
    BASE_DIR / "skills" / "decision-log-audit" / "fixtures" / "sample_decision_log.jsonl"
)


def audit_log(path: Path) -> list[str]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors: list[str] = []

    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        errors.append("Decision log is empty.")
        return errors

    for index, line in enumerate(lines, start=1):
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"Line {index}: invalid JSON ({exc})")
            continue

        violations = sorted(validator.iter_errors(payload), key=lambda err: err.path)
        if violations:
            message = ", ".join(error.message for error in violations)
            errors.append(f"Line {index}: schema violation ({message})")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit decision log JSONL files.")
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG_PATH)
    args = parser.parse_args()

    errors = audit_log(args.log)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Decision log audit passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
