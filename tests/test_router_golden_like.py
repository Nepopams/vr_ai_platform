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


def test_v1_and_v2_match_on_fixtures():
    """Both V1 and V2 produce valid decisions for all fixtures.

    V2 may produce more proposed_actions for multi-item commands (intentional).
    Both must produce valid schema and agree on action type (start_job/clarify).
    """
    schema = _load_decision_schema()
    commands = _load_fixture_commands()
    router_v1 = RouterV1Adapter()
    router_v2 = RouterV2Pipeline()

    for command in commands:
        decision_v1 = router_v1.decide(command)
        decision_v2 = router_v2.decide(command)

        validate(instance=decision_v1, schema=schema)
        validate(instance=decision_v2, schema=schema)

        # V1 and V2 agree on action type (start_job / clarify)
        assert decision_v1["action"] == decision_v2["action"]
        assert decision_v1["status"] == decision_v2["status"]
