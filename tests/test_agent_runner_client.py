import json

import app.llm.agent_runner_client as client


class DummyResponse:
    def __init__(self, payload):
        self._payload = payload

    def read(self):
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_shadow_invoke_disabled(monkeypatch):
    monkeypatch.setenv("LLM_SHOPPING_EXTRACTOR_ENABLED", "false")
    called = {"value": False}

    def fake_log(_payload):
        called["value"] = True

    monkeypatch.setattr(client, "append_llm_runner_log", fake_log)
    client.shadow_invoke(text="Купи молоко", context={}, trace_id="trace-1")
    assert called["value"] is False


def test_invoke_runner_builds_envelope(monkeypatch):
    monkeypatch.setenv("LLM_AGENT_RUNNER_URL", "http://localhost:8089")
    monkeypatch.setenv("LLM_SHOPPING_EXTRACTOR_TIMEOUT_S", "1")
    captured = {}

    def fake_urlopen(req, timeout):
        captured["url"] = req.full_url
        captured["data"] = req.data
        return DummyResponse({"ok": True, "meta": {}})

    monkeypatch.setattr(client.urlrequest, "urlopen", fake_urlopen)
    payload = client.invoke_runner(text="Купи молоко", context={}, trace_id="trace-1")
    assert payload["ok"] is True
    body = json.loads(captured["data"].decode("utf-8"))
    assert body["agent_id"] == client.AGENT_ID
    assert body["intent"] == client.INTENT
