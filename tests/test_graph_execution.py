import json
from pathlib import Path

from jsonschema import validate

from graphs.core_graph import process_command, sample_command


BASE_DIR = Path(__file__).resolve().parents[1]
SCHEMA_DIR = BASE_DIR / "contracts" / "schemas"
DECISION_SCHEMA_PATH = SCHEMA_DIR / "decision.schema.json"
CONTRACTS_VERSION_PATH = BASE_DIR / "contracts" / "VERSION"


def test_process_command_returns_valid_decision():
    decision_schema = json.loads(DECISION_SCHEMA_PATH.read_text(encoding="utf-8"))
    schema_version = CONTRACTS_VERSION_PATH.read_text(encoding="utf-8").strip()
    decision = process_command(sample_command())

    assert decision["command_id"] == "cmd-001"
    assert decision["schema_version"] == schema_version
    assert decision["reasoning_log"]["trace_id"]
    validate(instance=decision, schema=decision_schema)
