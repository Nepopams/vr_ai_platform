"""Shared pytest fixtures for HomeTask AI Platform tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
SCHEMA_DIR = BASE_DIR / "contracts" / "schemas"


@pytest.fixture()
def command_schema() -> Dict[str, Any]:
    """Load CommandDTO JSON schema."""
    return json.loads(
        (SCHEMA_DIR / "command.schema.json").read_text(encoding="utf-8")
    )


@pytest.fixture()
def decision_schema() -> Dict[str, Any]:
    """Load DecisionDTO JSON schema."""
    return json.loads(
        (SCHEMA_DIR / "decision.schema.json").read_text(encoding="utf-8")
    )


@pytest.fixture()
def household_context() -> Dict[str, Any]:
    """Full household context with members, zones, and shopping lists."""
    return {
        "household": {
            "household_id": "house-test-001",
            "members": [
                {"user_id": "user-test-001", "display_name": "Тест Юзер"}
            ],
            "zones": [
                {"zone_id": "zone-kitchen", "name": "Кухня"},
                {"zone_id": "zone-bath", "name": "Ванная"},
            ],
            "shopping_lists": [
                {"list_id": "list-test-001", "name": "Продукты"}
            ],
        },
        "defaults": {
            "default_assignee_id": "user-test-001",
            "default_list_id": "list-test-001",
        },
    }


@pytest.fixture()
def minimal_context() -> Dict[str, Any]:
    """Minimal valid context — only required fields."""
    return {
        "household": {
            "members": [{"user_id": "user-test-min"}]
        }
    }


@pytest.fixture()
def valid_command(household_context: Dict[str, Any]) -> Dict[str, Any]:
    """Minimal valid CommandDTO with full context."""
    return {
        "command_id": "cmd-test-001",
        "user_id": "user-test-001",
        "timestamp": "2026-01-01T12:00:00+00:00",
        "text": "Тестовая команда",
        "capabilities": [
            "start_job",
            "propose_create_task",
            "propose_add_shopping_item",
            "clarify",
        ],
        "context": household_context,
    }


@pytest.fixture()
def valid_command_shopping(household_context: Dict[str, Any]) -> Dict[str, Any]:
    """CommandDTO that triggers add_shopping_item intent."""
    return {
        "command_id": "cmd-test-shop-001",
        "user_id": "user-test-001",
        "timestamp": "2026-01-01T12:00:00+00:00",
        "text": "Купи молоко",
        "capabilities": [
            "start_job",
            "propose_create_task",
            "propose_add_shopping_item",
            "clarify",
        ],
        "context": household_context,
    }


@pytest.fixture()
def valid_command_task(household_context: Dict[str, Any]) -> Dict[str, Any]:
    """CommandDTO that triggers create_task intent."""
    return {
        "command_id": "cmd-test-task-001",
        "user_id": "user-test-001",
        "timestamp": "2026-01-01T12:00:00+00:00",
        "text": "Убери кухню",
        "capabilities": [
            "start_job",
            "propose_create_task",
            "propose_add_shopping_item",
            "clarify",
        ],
        "context": household_context,
    }
