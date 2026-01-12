import json
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import validate


BASE_DIR = Path(__file__).resolve().parents[1]
SCHEMA_DIR = BASE_DIR / "contracts" / "schemas"
CONTRACTS_VERSION_PATH = BASE_DIR / "contracts" / "VERSION"


def load_schema(name: str) -> dict:
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


def test_command_schema_allows_example_payload():
    command_schema = load_schema("command.schema.json")
    example_command = {
        "command_id": "cmd-001",
        "user_id": "user-123",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task": {
            "title": "Plan weekly chores",
            "description": "Generate a mock plan for household chores.",
            "priority": "medium",
        },
        "context": {"locale": "en-US"},
    }

    validate(instance=example_command, schema=command_schema)


def test_decision_schema_allows_example_payload():
    decision_schema = load_schema("decision.schema.json")
    schema_version = CONTRACTS_VERSION_PATH.read_text(encoding="utf-8").strip()
    example_decision = {
        "decision_id": "dec-123",
        "command_id": "cmd-001",
        "status": "accepted",
        "actions": [
            {
                "type": "plan",
                "description": "Provide a mock weekly chores plan.",
            }
        ],
        "reasoning_log": {
            "command_id": "cmd-001",
            "steps": [
                "Validate command payload against schema.",
                "Simulate agent reasoning in mock mode.",
                "Assemble decision output and attach reasoning log.",
            ],
            "model_version": "mock-model-0.1",
            "prompt_version": "prompt-v0",
            "trace_id": "trace-123",
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "version": "v0",
        "schema_version": schema_version,
    }

    validate(instance=example_decision, schema=decision_schema)
