"""Smoke test for Decision API using FastAPI TestClient."""

from __future__ import annotations

import json
import os
import tempfile
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


def main() -> int:
    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ["DECISION_LOG_PATH"] = str(Path(temp_dir) / "decisions.jsonl")
        command = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        schema = json.loads(DECISION_SCHEMA_PATH.read_text(encoding="utf-8"))
        client = TestClient(create_app())

        response = client.post("/v1/decide", json=command)
        if response.status_code != 200:
            print(f"API sanity failed: {response.status_code} {response.text}")
            return 1

        decision = response.json()
        validate(instance=decision, schema=schema)
        print("API sanity passed.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
