"""Tests for Cloud.ru ASR client."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.asr.client import CloudRuAsrClient
from app.asr.config import load_asr_config
from app.asr.errors import (
    AsrAuthError,
    AsrTimeoutError,
    BadUpstreamResponseError,
    UpstreamUnavailableError,
)
from app.asr.multipart import AsrAudioFile


def _config():
    return load_asr_config(
        {
            "ASR_BASE_URL": "https://foundation-models.api.cloud.ru/v1",
            "ASR_API_KEY": "secret-key",
            "ASR_MODEL": "openai/whisper-large-v3",
            "ASR_TIMEOUT_MS": "30000",
        }
    )


def _audio() -> AsrAudioFile:
    return AsrAudioFile(
        filename="sample.wav",
        content_type="audio/wav",
        content=b"fake-audio",
    )


def _response(status_code: int = 200, payload: dict | None = None) -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = payload if payload is not None else {"text": "текст"}
    return response


def test_cloudru_asr_client_sends_openai_compatible_request() -> None:
    caller = CloudRuAsrClient(_config())

    with patch("app.asr.client.httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.post.return_value = _response()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

        result = caller.transcribe(_audio())

    mock_client_cls.assert_called_once_with(timeout=30.0)
    mock_client.post.assert_called_once()
    url = mock_client.post.call_args[0][0]
    kwargs = mock_client.post.call_args[1]
    assert url == "https://foundation-models.api.cloud.ru/v1/audio/transcriptions"
    assert kwargs["headers"]["Authorization"] == "Bearer secret-key"
    assert kwargs["data"]["model"] == "openai/whisper-large-v3"
    assert kwargs["data"]["language"] == "ru"
    assert kwargs["data"]["response_format"] == "json"
    assert kwargs["files"]["file"] == ("sample.wav", b"fake-audio", "audio/wav")
    assert result.transcript == "текст"
    assert result.provider == "cloudru"
    assert result.upstream_status == 200


def test_cloudru_asr_client_timeout_maps_to_controlled_error() -> None:
    caller = CloudRuAsrClient(_config())
    with patch("app.asr.client.httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.post.side_effect = httpx.TimeoutException("timeout")
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

        with pytest.raises(AsrTimeoutError):
            caller.transcribe(_audio())


def test_cloudru_asr_client_auth_error_maps_to_controlled_error() -> None:
    caller = CloudRuAsrClient(_config())
    with patch("app.asr.client.httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.post.return_value = _response(status_code=401)
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

        with pytest.raises(AsrAuthError):
            caller.transcribe(_audio())


def test_cloudru_asr_client_upstream_error_maps_to_unavailable() -> None:
    caller = CloudRuAsrClient(_config())
    with patch("app.asr.client.httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.post.return_value = _response(status_code=503)
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

        with pytest.raises(UpstreamUnavailableError):
            caller.transcribe(_audio())


def test_cloudru_asr_client_rejects_bad_response_shape() -> None:
    caller = CloudRuAsrClient(_config())
    with patch("app.asr.client.httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.post.return_value = _response(payload={"unexpected": "shape"})
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

        with pytest.raises(BadUpstreamResponseError):
            caller.transcribe(_audio())
