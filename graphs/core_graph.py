"""Mock decision-making pipeline for HomeTask AI System."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from jsonschema import validate

from codex.reasoning_log import build_reasoning_log

BASE_DIR = Path(__file__).resolve().parents[1]
SCHEMA_DIR = BASE_DIR / "contracts" / "schemas"

COMMAND_SCHEMA_PATH = SCHEMA_DIR / "command.schema.json"
DECISION_SCHEMA_PATH = SCHEMA_DIR / "decision.schema.json"


def load_schema(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sample_command() -> Dict[str, Any]:
    return {
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


def process_command(command: Dict[str, Any]) -> Dict[str, Any]:
    command_schema = load_schema(COMMAND_SCHEMA_PATH)
    validate(instance=command, schema=command_schema)

    steps = [
        "Validate command payload against schema.",
        "Simulate agent reasoning in mock mode.",
        "Assemble decision output and attach reasoning log.",
    ]
    reasoning_log = build_reasoning_log(
        command_id=command["command_id"],
        steps=steps,
        model_version="mock-model-0.1",
        prompt_version="prompt-v0",
    )

    decision = {
        "decision_id": f"dec-{uuid4().hex}",
        "command_id": command["command_id"],
        "status": "accepted",
        "actions": [
            {
                "type": "plan",
                "description": "Provide a mock weekly chores plan.",
            }
        ],
        "reasoning_log": reasoning_log,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "version": "v0",
    }

    decision_schema = load_schema(DECISION_SCHEMA_PATH)
    validate(instance=decision, schema=decision_schema)

    return decision


def main() -> None:
    command = sample_command()
    decision = process_command(command)
    print(json.dumps(decision, indent=2))


if __name__ == "__main__":
    main()
