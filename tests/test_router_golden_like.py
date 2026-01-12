import json
from pathlib import Path

from jsonschema import validate

from routers.v1 import RouterV1Adapter
from routers.v2 import RouterV2Pipeline


BASE_DIR = Path(__file__).resolve().parents[1]
FIXTURE_DIR = BASE_DIR / "skills" / "graph-sanity" / "fixtures" / "commands"
DECISION_SCHEMA_PATH = BASE_DIR / "contracts" / "schemas" / "decision.schema.json"


def _load_decision_schema():
    return json.loads(DECISION_SCHEMA_PATH.read_text(encoding="utf-8"))


def _load_fixture_commands(limit: int = 3):
    fixtures = sorted(FIXTURE_DIR.glob("*.json"))
    return [json.loads(path.read_text(encoding="utf-8")) for path in fixtures[:limit]]


def _extract_stable_fields(decision):
    action = decision.get("action")
    payload = decision.get("payload", {})
    stable = {"action": action}

    if action == "start_job":
        stable["job_type"] = payload.get("job_type")
        proposed_actions = payload.get("proposed_actions") or []
        stable["proposed_actions"] = [
            {
                "action": proposed.get("action"),
                "item_name": proposed.get("payload", {}).get("item", {}).get("name"),
                "task_title": proposed.get("payload", {}).get("task", {}).get("title"),
            }
            for proposed in proposed_actions
        ]
    elif action == "clarify":
        stable["missing_fields"] = payload.get("missing_fields")
    return stable


def test_v1_and_v2_match_on_fixtures():
    schema = _load_decision_schema()
    commands = _load_fixture_commands()
    router_v1 = RouterV1Adapter()
    router_v2 = RouterV2Pipeline()

    for command in commands:
        decision_v1 = router_v1.decide(command)
        decision_v2 = router_v2.decide(command)

        validate(instance=decision_v1, schema=schema)
        validate(instance=decision_v2, schema=schema)

        assert _extract_stable_fields(decision_v1) == _extract_stable_fields(decision_v2)
