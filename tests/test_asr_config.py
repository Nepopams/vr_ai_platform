"""Tests for ASR env configuration."""

from __future__ import annotations

import pytest

from app.asr.config import (
    DEFAULT_LANGUAGE,
    DEFAULT_MODEL,
    DEFAULT_PROVIDER,
    DEFAULT_TRANSCRIBE_PATH,
    load_asr_config,
)
from app.asr.errors import AsrConfigError


def test_asr_config_defaults_without_credentials() -> None:
    config = load_asr_config({}, require_credentials=False)
    assert config.provider == DEFAULT_PROVIDER
    assert config.model == DEFAULT_MODEL
    assert config.language == DEFAULT_LANGUAGE
    assert config.transcribe_path == DEFAULT_TRANSCRIBE_PATH
    assert config.timeout_ms == 30000
    assert config.max_file_size_mb == 25


def test_asr_config_requires_base_url_and_key() -> None:
    with pytest.raises(AsrConfigError):
        load_asr_config({}, require_credentials=True)

    with pytest.raises(AsrConfigError):
        load_asr_config(
            {"ASR_BASE_URL": "https://foundation-models.api.cloud.ru/v1"},
            require_credentials=True,
        )


def test_asr_config_rejects_placeholder_key() -> None:
    with pytest.raises(AsrConfigError):
        load_asr_config(
            {
                "ASR_BASE_URL": "https://foundation-models.api.cloud.ru/v1",
                "ASR_API_KEY": "your-asr-api-key-here",
            },
            require_credentials=True,
        )


def test_asr_config_env_overrides() -> None:
    config = load_asr_config(
        {
            "ASR_PROVIDER": "cloudru-uat",
            "ASR_BASE_URL": "https://asr.example.test/v1",
            "ASR_TRANSCRIBE_PATH": "audio/transcriptions",
            "ASR_API_KEY": "secret",
            "ASR_MODEL": "openai/whisper-large-v3",
            "ASR_LANGUAGE": "en",
            "ASR_TIMEOUT_MS": "45000",
            "ASR_MAX_FILE_SIZE_MB": "10",
            "ASR_ALLOWED_MEDIA_TYPES": "audio/wav,audio/webm",
        }
    )
    assert config.provider == "cloudru-uat"
    assert config.language == "en"
    assert config.transcribe_url == "https://asr.example.test/v1/audio/transcriptions"
    assert config.timeout_s == 45.0
    assert config.max_file_size_bytes == 10 * 1024 * 1024
    assert config.allowed_media_types == frozenset({"audio/wav", "audio/webm"})


def test_asr_config_rejects_invalid_numbers() -> None:
    with pytest.raises(AsrConfigError):
        load_asr_config(
            {
                "ASR_BASE_URL": "https://asr.example.test/v1",
                "ASR_API_KEY": "secret",
                "ASR_TIMEOUT_MS": "not-int",
            }
        )

    with pytest.raises(AsrConfigError):
        load_asr_config(
            {
                "ASR_BASE_URL": "https://asr.example.test/v1",
                "ASR_API_KEY": "secret",
                "ASR_MAX_FILE_SIZE_MB": "0",
            }
        )

    with pytest.raises(AsrConfigError):
        load_asr_config(
            {
                "ASR_BASE_URL": "https://asr.example.test/v1",
                "ASR_API_KEY": "secret",
                "ASR_LANGUAGE": "russian",
            }
        )
