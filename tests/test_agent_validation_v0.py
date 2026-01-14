from agent_registry.validation import validate_agent_input, validate_agent_output_payload
from agent_registry.v0_reason_codes import (
    REASON_CAPABILITY_NOT_ALLOWED,
    REASON_INVALID_INPUT,
    REASON_INVALID_OUTPUT,
)


def _catalog():
    return {
        "extract_entities.shopping": {
            "payload_allowlist": {"items", "confidence"},
        }
    }


def test_validate_input_not_dict():
    ok, reason, normalized = validate_agent_input("bad")

    assert ok is False
    assert reason == REASON_INVALID_INPUT
    assert normalized is None


def test_validate_output_unknown_capability():
    ok, reason = validate_agent_output_payload({}, "unknown", _catalog())

    assert ok is False
    assert reason == REASON_CAPABILITY_NOT_ALLOWED


def test_validate_output_extra_keys():
    ok, reason = validate_agent_output_payload({"items": [], "extra": 1}, "extract_entities.shopping", _catalog())

    assert ok is False
    assert reason == REASON_INVALID_OUTPUT


def test_validate_output_ok():
    ok, reason = validate_agent_output_payload({"items": [], "confidence": 0.7}, "extract_entities.shopping", _catalog())

    assert ok is True
    assert reason is None
