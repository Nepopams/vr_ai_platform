"""Tests for health and readiness endpoints (ST-034)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import create_app

BASE_DIR = Path(__file__).resolve().parents[1]
VERSION_PATH = BASE_DIR / "contracts" / "VERSION"


def _client() -> TestClient:
    return TestClient(create_app())


def test_health_returns_ok() -> None:
    client = _client()
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_health_contains_version() -> None:
    expected_version = VERSION_PATH.read_text(encoding="utf-8").strip()
    client = _client()
    response = client.get("/health")
    data = response.json()
    assert data["version"] == expected_version


def test_ready_returns_ok_when_service_available() -> None:
    client = _client()
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


def test_ready_returns_503_when_service_unavailable() -> None:
    fake_path = Path("/nonexistent/command.schema.json")
    with patch("app.routes.health.COMMAND_SCHEMA_PATH", fake_path):
        client = _client()
        response = client.get("/ready")
    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "not_ready"
    assert "error" in data["checks"]["decision_service"]


def test_ready_checks_dict_structure() -> None:
    client = _client()
    response = client.get("/ready")
    data = response.json()
    assert "checks" in data
    assert "decision_service" in data["checks"]
