"""Tests for Pydantic API models (ST-032)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.models.api_models import CommandRequest, DecisionResponse


def _valid_command_dict() -> dict:
    return {
        "command_id": "cmd-test-001",
        "user_id": "user-test-001",
        "timestamp": "2026-01-01T12:00:00+00:00",
        "text": "Тестовая команда",
        "capabilities": ["start_job", "clarify"],
        "context": {
            "household": {
                "members": [{"user_id": "user-test-001"}]
            }
        },
    }


def _valid_decision_dict() -> dict:
    return {
        "decision_id": "dec-001",
        "command_id": "cmd-001",
        "status": "ok",
        "action": "start_job",
        "confidence": 0.78,
        "payload": {
            "job_id": "job-001",
            "job_type": "create_task",
            "proposed_actions": [],
        },
        "explanation": "Тестовое решение.",
        "trace_id": "trace-001",
        "schema_version": "2.0.0",
        "decision_version": "mvp1-graph-0.1",
        "created_at": "2026-01-01T12:00:00+00:00",
    }


def test_command_request_valid() -> None:
    cmd = CommandRequest.model_validate(_valid_command_dict())
    assert cmd.command_id == "cmd-test-001"
    assert cmd.context.household.members[0].user_id == "user-test-001"


def test_command_request_missing_field() -> None:
    data = _valid_command_dict()
    del data["text"]
    with pytest.raises(ValidationError):
        CommandRequest.model_validate(data)


def test_command_request_invalid_capability() -> None:
    data = _valid_command_dict()
    data["capabilities"] = ["start_job", "unknown_cap"]
    with pytest.raises(ValidationError):
        CommandRequest.model_validate(data)


def test_command_request_extra_field_rejected() -> None:
    data = _valid_command_dict()
    data["extra_field"] = "should fail"
    with pytest.raises(ValidationError):
        CommandRequest.model_validate(data)


def test_decision_response_valid() -> None:
    dec = DecisionResponse.model_validate(_valid_decision_dict())
    assert dec.decision_id == "dec-001"
    assert dec.action == "start_job"


def test_decision_response_confidence_bounds() -> None:
    data = _valid_decision_dict()
    data["confidence"] = 1.5
    with pytest.raises(ValidationError):
        DecisionResponse.model_validate(data)

    data["confidence"] = -0.1
    with pytest.raises(ValidationError):
        DecisionResponse.model_validate(data)


def test_decision_response_roundtrip() -> None:
    data = _valid_decision_dict()
    dec = DecisionResponse.model_validate(data)
    dumped = dec.model_dump()
    dec2 = DecisionResponse.model_validate(dumped)
    assert dec == dec2


def test_command_context_nested_validation() -> None:
    data = _valid_command_dict()
    data["context"]["household"]["members"] = []
    with pytest.raises(ValidationError):
        CommandRequest.model_validate(data)
