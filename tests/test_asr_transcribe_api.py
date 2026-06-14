"""Endpoint tests for ASR transcription API."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.asr.client import AsrTranscriptionResult
from app.asr.errors import AsrTimeoutError, UpstreamUnavailableError
from app.main import create_app


def _client(monkeypatch, tmp_path) -> TestClient:
    monkeypatch.setenv("ASR_BASE_URL", "https://foundation-models.api.cloud.ru/v1")
    monkeypatch.setenv("ASR_API_KEY", "secret")
    monkeypatch.setenv("ASR_LOG_PATH", str(tmp_path / "asr.jsonl"))
    return TestClient(create_app())


def _success_result() -> AsrTranscriptionResult:
    return AsrTranscriptionResult(
        transcript="Добавь молоко",
        provider="cloudru",
        model="openai/whisper-large-v3",
        latency_ms=123,
        upstream_status=200,
    )


def test_asr_transcribe_success(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    with patch("app.routes.asr.CloudRuAsrClient") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.transcribe.return_value = _success_result()
        mock_client_cls.return_value = mock_client

        response = client.post(
            "/v1/asr/transcribe",
            files={"file": ("sample.wav", b"fake-audio", "audio/wav")},
        )

    assert response.status_code == 200
    assert response.headers.get("API-Version") == "v1"
    data = response.json()
    assert data["transcript"] == "Добавь молоко"
    assert data["provider"] == "cloudru"
    assert data["status"] == "ok"
    assert data["trace_id"].startswith("trace-asr-")
    mock_client.transcribe.assert_called_once()


def test_asr_transcribe_rejects_invalid_media_type(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    with patch("app.routes.asr.CloudRuAsrClient") as mock_client_cls:
        response = client.post(
            "/v1/asr/transcribe",
            files={"file": ("note.txt", b"not-audio", "text/plain")},
        )

    assert response.status_code == 415
    assert response.json()["error"] == "unsupported_media"
    mock_client_cls.assert_not_called()


def test_asr_transcribe_rejects_file_too_large(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("ASR_MAX_FILE_SIZE_MB", "1")
    client = _client(monkeypatch, tmp_path)
    oversized = b"x" * (1024 * 1024 + 1)
    with patch("app.routes.asr.CloudRuAsrClient") as mock_client_cls:
        response = client.post(
            "/v1/asr/transcribe",
            files={"file": ("large.wav", oversized, "audio/wav")},
        )

    assert response.status_code == 413
    assert response.json()["error"] == "file_too_large"
    mock_client_cls.assert_not_called()


def test_asr_transcribe_timeout_returns_504(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    with patch("app.routes.asr.CloudRuAsrClient") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.transcribe.side_effect = AsrTimeoutError("ASR timed out.")
        mock_client_cls.return_value = mock_client

        response = client.post(
            "/v1/asr/transcribe",
            files={"file": ("sample.wav", b"fake-audio", "audio/wav")},
        )

    assert response.status_code == 504
    assert response.json()["error"] == "timeout"


def test_asr_transcribe_upstream_error_returns_502(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    with patch("app.routes.asr.CloudRuAsrClient") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.transcribe.side_effect = UpstreamUnavailableError("upstream down")
        mock_client_cls.return_value = mock_client

        response = client.post(
            "/v1/asr/transcribe",
            files={"file": ("sample.wav", b"fake-audio", "audio/wav")},
        )

    assert response.status_code == 502
    assert response.json()["error"] == "upstream_unavailable"


def test_asr_transcribe_is_versioned_only(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    response = client.post(
        "/asr/transcribe",
        files={"file": ("sample.wav", b"fake-audio", "audio/wav")},
    )
    assert response.status_code == 404
