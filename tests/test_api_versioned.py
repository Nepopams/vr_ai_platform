"""Tests for versioned API paths (ST-033)."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app

BASE_DIR = Path(__file__).resolve().parents[1]
FIXTURE_PATH = (
    BASE_DIR
    / "skills"
    / "contract-checker"
    / "fixtures"
    / "valid_command_create_task.json"
)


def _client() -> TestClient:
    return TestClient(create_app())


def _valid_command() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_v1_decide_returns_valid_decision(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DECISION_LOG_PATH", str(tmp_path / "decisions.jsonl"))
    client = _client()
    response = client.post("/v1/decide", json=_valid_command())
    assert response.status_code == 200
    data = response.json()
    assert "decision_id" in data
    assert "action" in data


def test_v1_decide_returns_version_header(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DECISION_LOG_PATH", str(tmp_path / "decisions.jsonl"))
    client = _client()
    response = client.post("/v1/decide", json=_valid_command())
    assert response.headers.get("API-Version") == "v1"


def test_unversioned_decide_still_works(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DECISION_LOG_PATH", str(tmp_path / "decisions.jsonl"))
    client = _client()
    response = client.post("/decide", json=_valid_command())
    assert response.status_code == 200
    data = response.json()
    assert "decision_id" in data


def test_v1_invalid_command_returns_error_with_version_header(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DECISION_LOG_PATH", str(tmp_path / "decisions.jsonl"))
    client = _client()
    response = client.post("/v1/decide", json={"command_id": "cmd-1"})
    assert response.status_code == 422
    assert response.headers.get("API-Version") == "v1"


def test_health_no_version_header() -> None:
    client = _client()
    response = client.get("/health")
    assert response.status_code == 200
    assert "API-Version" not in response.headers
