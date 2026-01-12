from agent_runner.yandex_client import YandexAIStudioClient


class DummyResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def test_yandex_invalid_json_retry(monkeypatch):
    client = YandexAIStudioClient(
        api_key="key",
        project="folder",
        model="gpt://folder/gpt-oss-120b/latest",
        base_url="https://llm.api.cloud.yandex.net/v1",
        timeout_s=5,
        temperature=0.1,
        max_output_tokens=None,
    )
    calls = {"count": 0}

    def fake_post(url, headers, json_payload):
        calls["count"] += 1
        if calls["count"] == 1:
            return DummyResponse({"choices": [{"message": {"content": "not-json"}}]})
        return DummyResponse({"choices": [{"message": {"content": "{\"items\": []}"}}]})

    monkeypatch.setattr(client, "_post", fake_post)
    payload = {
        "system_prompt": "sys",
        "user_prompt": "user",
        "schema": {"type": "object", "required": ["items"], "properties": {"items": {"type": "array"}}},
    }
    output, _meta = client.extract(payload)
    assert calls["count"] == 2
    assert output["items"] == []
