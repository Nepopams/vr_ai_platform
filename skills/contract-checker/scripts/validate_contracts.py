import json
from pathlib import Path

from jsonschema import Draft202012Validator


BASE_DIR = Path(__file__).resolve().parents[2]
SCHEMA_DIR = BASE_DIR / "contracts" / "schemas"
FIXTURE_DIR = BASE_DIR / "skills" / "contract-checker" / "fixtures"


def _load_schema(name: str) -> dict:
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


def _schema_for_fixture(path: Path) -> dict:
    if "command" in path.name:
        return _load_schema("command.schema.json")
    if "decision" in path.name:
        return _load_schema("decision.schema.json")
    raise ValueError(f"Unsupported fixture name: {path.name}")


def validate_fixtures() -> list[str]:
    failures: list[str] = []
    fixtures = sorted(FIXTURE_DIR.glob("*.json"))
    if not fixtures:
        failures.append("No fixtures found to validate.")
        return failures

    for fixture in fixtures:
        schema = _schema_for_fixture(fixture)
        payload = json.loads(fixture.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(payload), key=lambda err: err.path)
        is_invalid = fixture.name.startswith("invalid_")

        if is_invalid and not errors:
            failures.append(f"Expected {fixture.name} to fail validation.")
        if not is_invalid and errors:
            message = ", ".join(error.message for error in errors)
            failures.append(f"{fixture.name} failed validation: {message}")

    return failures


def main() -> int:
    failures = validate_fixtures()
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("All contract fixtures validated successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
