import json
from pathlib import Path

from jsonschema import validate

from graphs.core_graph import process_command, sample_command


BASE_DIR = Path(__file__).resolve().parents[1]
SCHEMA_DIR = BASE_DIR / "contracts" / "schemas"
DECISION_SCHEMA_PATH = SCHEMA_DIR / "decision.schema.json"


def test_process_command_returns_valid_decision():
    decision_schema = json.loads(DECISION_SCHEMA_PATH.read_text(encoding="utf-8"))
    decision = process_command(sample_command())

    assert decision["command_id"] == "cmd-001"
    validate(instance=decision, schema=decision_schema)
