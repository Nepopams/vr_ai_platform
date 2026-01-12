from agent_runner.envelope import (
    SUPPORTED_AGENT_ID,
    SUPPORTED_INTENT,
    AgentRequest,
    build_response,
    parse_request,
    unsupported_response,
)


def test_parse_request_ok():
    payload = {
        "a2a_version": "a2a.v1",
        "message_id": "msg-1",
        "trace_id": "trace-1",
        "agent_id": SUPPORTED_AGENT_ID,
        "intent": SUPPORTED_INTENT,
        "input": {"text": "Купи молоко", "context": {"household": {}}},
    }
    request = parse_request(payload)
    assert isinstance(request, AgentRequest)
    assert request.input_text == "Купи молоко"


def test_parse_request_missing_fields():
    payload = {"a2a_version": "a2a.v1"}
    try:
        parse_request(payload)
    except ValueError as exc:
        assert "Missing fields" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing fields")


def test_unsupported_response():
    request = AgentRequest(
        a2a_version="a2a.v1",
        message_id="msg-1",
        trace_id="trace-1",
        agent_id="other",
        intent="other",
        input_text="test",
        input_context={},
    )
    response = unsupported_response(request)
    assert response["ok"] is False
    assert response["error"]["type"] == "unsupported_agent_or_intent"


def test_build_response_ok():
    request = AgentRequest(
        a2a_version="a2a.v1",
        message_id="msg-1",
        trace_id="trace-1",
        agent_id=SUPPORTED_AGENT_ID,
        intent=SUPPORTED_INTENT,
        input_text="test",
        input_context={},
    )
    response = build_response(request=request, ok=True, output={"items": []})
    assert response["ok"] is True
    assert response["output"]["items"] == []
