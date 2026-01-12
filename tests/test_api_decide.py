import json
from pathlib import Path

from fastapi.testclient import TestClient
from jsonschema import validate

from app.main import create_app


BASE_DIR = Path(__file__).resolve().parents[1]
FIXTURE_PATH = (
    BASE_DIR
    / "skills"
    / "contract-checker"
    / "fixtures"
    / "valid_command_create_task.json"
)
DECISION_SCHEMA_PATH = BASE_DIR / "contracts" / "schemas" / "decision.schema.json"


def test_decide_returns_valid_decision(monkeypatch, tmp_path):
    monkeypatch.setenv("DECISION_LOG_PATH", str(tmp_path / "decisions.jsonl"))
    command = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    schema = json.loads(DECISION_SCHEMA_PATH.read_text(encoding="utf-8"))
    client = TestClient(create_app())

    response = client.post("/decide", json=command)
    assert response.status_code == 200
    decision = response.json()
    validate(instance=decision, schema=schema)


def test_decide_rejects_invalid_command(monkeypatch, tmp_path):
    monkeypatch.setenv("DECISION_LOG_PATH", str(tmp_path / "decisions.jsonl"))
    client = TestClient(create_app())
    response = client.post("/decide", json={"command_id": "cmd-1"})
    assert response.status_code == 400
    payload = response.json()
    assert payload.get("detail", {}).get("error") == "CommandDTO validation failed."
