"""Run the core graph suite against fixture commands."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from jsonschema import validate

from graphs.core_graph import process_command


SUITE_DIR = Path(__file__).resolve().parent
FIXTURE_DIR = SUITE_DIR.parent / "fixtures" / "commands"
REPO_ROOT = SUITE_DIR.parents[3]
DECISION_SCHEMA_PATH = REPO_ROOT / "contracts" / "schemas" / "decision.schema.json"


def load_fixture_commands() -> List[Dict[str, Any]]:
    if not FIXTURE_DIR.exists():
        raise FileNotFoundError(f"Fixture directory not found: {FIXTURE_DIR}")

    fixture_paths = sorted(FIXTURE_DIR.glob("*.json"))
    if not fixture_paths:
        raise FileNotFoundError(f"No fixture command files found in {FIXTURE_DIR}")

    return [json.loads(path.read_text(encoding="utf-8")) for path in fixture_paths]


def load_decision_schema() -> Dict[str, Any]:
    return json.loads(DECISION_SCHEMA_PATH.read_text(encoding="utf-8"))


def assert_reasoning_trace_metadata(decision: Dict[str, Any]) -> None:
    reasoning_log = decision.get("reasoning_log")
    assert isinstance(reasoning_log, dict), "reasoning_log must be present"

    for key in ("command_id", "steps", "model_version", "prompt_version"):
        assert reasoning_log.get(key), f"reasoning_log.{key} must be present"

    steps = reasoning_log.get("steps")
    assert isinstance(steps, list) and steps, "reasoning_log.steps must be non-empty"

    assert decision.get("decision_id"), "decision_id must be present"
    assert decision.get("created_at"), "created_at must be present"
    assert decision.get("version"), "version must be present"

    assert (
        reasoning_log.get("command_id") == decision.get("command_id")
    ), "reasoning_log.command_id must match decision.command_id"


def validate_decision(decision: Dict[str, Any], schema: Dict[str, Any]) -> None:
    validate(instance=decision, schema=schema)
    assert_reasoning_trace_metadata(decision)


def run_graph_suite() -> List[Dict[str, Any]]:
    fixture_commands = load_fixture_commands()
    decision_schema = load_decision_schema()

    decisions = []
    for command in fixture_commands:
        decision = process_command(command)
        validate_decision(decision, decision_schema)
        decisions.append(decision)

    return decisions


def main() -> None:
    decisions = run_graph_suite()
    print(json.dumps(decisions, indent=2))


if __name__ == "__main__":
    main()
