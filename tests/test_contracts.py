import json
from pathlib import Path

from jsonschema import Draft202012Validator


BASE_DIR = Path(__file__).resolve().parents[1]
SCHEMA_DIR = BASE_DIR / "contracts" / "schemas"
FIXTURE_DIR = BASE_DIR / "skills" / "contract-checker" / "fixtures"


def load_schema(name: str) -> dict:
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


def _schema_for_fixture(path: Path) -> dict:
    if "command" in path.name:
        return load_schema("command.schema.json")
    if "decision" in path.name:
        return load_schema("decision.schema.json")
    raise ValueError(f"Unsupported fixture name: {path.name}")


def test_contract_fixtures_validate_against_schemas():
    fixtures = sorted(FIXTURE_DIR.glob("*.json"))
    assert fixtures, "Fixtures directory is empty"

    for fixture in fixtures:
        schema = _schema_for_fixture(fixture)
        payload = json.loads(fixture.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(payload), key=lambda err: err.path)
        is_invalid = fixture.name.startswith("invalid_")

        if is_invalid:
            assert errors, f"Expected {fixture.name} to fail validation"
        else:
            assert not errors, f"{fixture.name} failed validation"
