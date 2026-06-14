"""Privacy tests for ASR logs."""

from __future__ import annotations

from pathlib import Path

from app.logging.asr_log import append_asr_log


def test_asr_log_filters_transcript_audio_and_user_text(monkeypatch, tmp_path) -> None:
    log_path = tmp_path / "asr.jsonl"
    monkeypatch.setenv("ASR_LOG_PATH", str(log_path))
    monkeypatch.setenv("ASR_LOG_ENABLED", "true")

    append_asr_log(
        {
            "request_id": "trace-asr-1",
            "trace_id": "trace-asr-1",
            "provider": "cloudru",
            "model": "openai/whisper-large-v3",
            "status": "ok",
            "latency_ms": 42,
            "file_size_bucket": "0-1MB",
            "upstream_status": 200,
            "transcript": "секретная расшифровка",
            "raw_audio": "RIFF-secret-audio",
            "text": "raw user text",
            "raw_upstream_response": {"text": "секретная расшифровка"},
        }
    )

    contents = Path(log_path).read_text(encoding="utf-8")
    assert "trace-asr-1" in contents
    assert "cloudru" in contents
    assert "секретная расшифровка" not in contents
    assert "RIFF-secret-audio" not in contents
    assert "raw user text" not in contents
    assert "raw_upstream_response" not in contents


def test_asr_log_can_be_disabled(monkeypatch, tmp_path) -> None:
    log_path = tmp_path / "asr.jsonl"
    monkeypatch.setenv("ASR_LOG_PATH", str(log_path))
    monkeypatch.setenv("ASR_LOG_ENABLED", "false")

    result = append_asr_log({"trace_id": "trace-asr-disabled"})

    assert result is None
    assert not log_path.exists()


def test_asr_log_write_errors_do_not_raise(monkeypatch, tmp_path) -> None:
    log_path = tmp_path / "asr.jsonl"
    monkeypatch.setenv("ASR_LOG_PATH", str(log_path))
    monkeypatch.setenv("ASR_LOG_ENABLED", "true")

    def _raise_permission_error(*args, **kwargs):
        raise PermissionError("log path is not writable")

    monkeypatch.setattr(Path, "open", _raise_permission_error)

    result = append_asr_log({"trace_id": "trace-asr-permission"})

    assert result is None
