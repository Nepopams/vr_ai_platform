"""Decision service integrating graph execution and validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from jsonschema import ValidationError, validate

from app.logging.decision_log import append_decision_log, append_decision_text
from routers.factory import decide as router_decide

BASE_DIR = Path(__file__).resolve().parents[2]
SCHEMA_DIR = BASE_DIR / "contracts" / "schemas"
COMMAND_SCHEMA_PATH = SCHEMA_DIR / "command.schema.json"
DECISION_SCHEMA_PATH = SCHEMA_DIR / "decision.schema.json"


def _load_schema(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


class CommandValidationError(Exception):
    def __init__(self, error: ValidationError) -> None:
        super().__init__(error.message)
        self.error = error


def validate_command(command: Dict[str, Any]) -> None:
    schema = _load_schema(COMMAND_SCHEMA_PATH)
    try:
        validate(instance=command, schema=schema)
    except ValidationError as exc:
        raise CommandValidationError(exc) from exc


def validate_decision(decision: Dict[str, Any]) -> None:
    schema = _load_schema(DECISION_SCHEMA_PATH)
    validate(instance=decision, schema=schema)


def decide(command: Dict[str, Any]) -> Dict[str, Any]:
    validate_command(command)
    decision = router_decide(command)
    validate_decision(decision)
    append_decision_log(decision)
    append_decision_text(command, decision.get("trace_id"))
    return decision


def format_validation_error(error: ValidationError) -> Dict[str, Any]:
    path = "/".join(str(item) for item in error.path)
    return {
        "message": error.message,
        "path": path,
    }
