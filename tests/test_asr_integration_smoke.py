"""Manual Cloud.ru ASR smoke tests (skipped unless explicitly enabled)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

_ASR_REAL_SMOKE_ENABLED = os.getenv("ASR_REAL_SMOKE_ENABLED", "").lower() in {
    "1",
    "true",
    "yes",
}
_ASR_API_KEY = os.getenv("ASR_API_KEY", "")
_ASR_BASE_URL = os.getenv("ASR_BASE_URL", "")
_ASR_SMOKE_AUDIO_PATH = os.getenv("ASR_SMOKE_AUDIO_PATH", "")

HAS_ASR_SMOKE_INPUTS = bool(
    _ASR_REAL_SMOKE_ENABLED
    and _ASR_API_KEY
    and _ASR_BASE_URL
    and _ASR_SMOKE_AUDIO_PATH
    and Path(_ASR_SMOKE_AUDIO_PATH).exists()
)

requires_asr_smoke = pytest.mark.skipif(
    not HAS_ASR_SMOKE_INPUTS,
    reason=(
        "ASR_REAL_SMOKE_ENABLED=true, ASR_API_KEY, ASR_BASE_URL, "
        "and existing ASR_SMOKE_AUDIO_PATH required"
    ),
)


@requires_asr_smoke
def test_real_cloudru_asr_transcription_roundtrip(monkeypatch, tmp_path) -> None:
    """Manual UAT smoke: local ASR endpoint calls real Cloud.ru ASR."""
    monkeypatch.setenv("ASR_LOG_PATH", str(tmp_path / "asr_smoke.jsonl"))
    monkeypatch.setenv("ASR_LOG_ENABLED", "true")

    audio_path = Path(_ASR_SMOKE_AUDIO_PATH)
    media_type = _guess_media_type(audio_path)
    client = TestClient(create_app())

    with audio_path.open("rb") as handle:
        response = client.post(
            "/v1/asr/transcribe",
            files={"file": (audio_path.name, handle, media_type)},
        )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "ok"
    assert data["provider"]
    assert data["model"]
    assert data["trace_id"].startswith("trace-asr-")
    assert isinstance(data["latency_ms"], int)
    assert data["latency_ms"] >= 0
    assert isinstance(data["transcript"], str)
    assert data["transcript"].strip()

    log_text = (tmp_path / "asr_smoke.jsonl").read_text(encoding="utf-8")
    assert data["transcript"] not in log_text


def _guess_media_type(path: Path) -> str:
    suffix = path.suffix.lower()
    return {
        ".mp3": "audio/mpeg",
        ".mp4": "audio/mp4",
        ".m4a": "audio/m4a",
        ".wav": "audio/wav",
        ".webm": "audio/webm",
        ".ogg": "audio/ogg",
        ".flac": "audio/flac",
    }.get(suffix, "audio/wav")
