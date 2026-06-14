"""Environment-driven ASR configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping

from app.asr.errors import AsrConfigError

DEFAULT_PROVIDER = "cloudru"
DEFAULT_MODEL = "openai/whisper-large-v3"
DEFAULT_TRANSCRIBE_PATH = "/audio/transcriptions"
DEFAULT_TIMEOUT_MS = 30000
DEFAULT_MAX_FILE_SIZE_MB = 25
PLACEHOLDER_API_KEYS = frozenset(
    {
        "your-asr-api-key-here",
        "<secret>",
        "<set-in-env-or-secret-manager>",
    }
)
DEFAULT_ALLOWED_MEDIA_TYPES = frozenset(
    {
        "audio/mpeg",
        "audio/mp3",
        "audio/mp4",
        "audio/m4a",
        "audio/wav",
        "audio/x-wav",
        "audio/webm",
        "audio/ogg",
        "audio/flac",
    }
)


@dataclass(frozen=True)
class AsrConfig:
    provider: str
    base_url: str
    transcribe_path: str
    api_key: str
    model: str
    timeout_ms: int
    max_file_size_mb: int
    allowed_media_types: frozenset[str]

    @property
    def timeout_s(self) -> float:
        return self.timeout_ms / 1000

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    @property
    def transcribe_url(self) -> str:
        path = self.transcribe_path
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.base_url.rstrip('/')}{path}"


def _positive_int(env: Mapping[str, str], key: str, default: int) -> int:
    raw = env.get(key, str(default)).strip()
    try:
        value = int(raw)
    except ValueError as exc:
        raise AsrConfigError(f"{key} must be an integer") from exc
    if value <= 0:
        raise AsrConfigError(f"{key} must be positive")
    return value


def _media_types(env: Mapping[str, str]) -> frozenset[str]:
    raw = env.get("ASR_ALLOWED_MEDIA_TYPES", "").strip()
    if not raw:
        return DEFAULT_ALLOWED_MEDIA_TYPES
    values = frozenset(item.strip().lower() for item in raw.split(",") if item.strip())
    if not values:
        raise AsrConfigError("ASR_ALLOWED_MEDIA_TYPES must not be empty")
    return values


def load_asr_config(
    env: Mapping[str, str] | None = None,
    *,
    require_credentials: bool = True,
) -> AsrConfig:
    source = env or os.environ
    provider = source.get("ASR_PROVIDER", DEFAULT_PROVIDER).strip() or DEFAULT_PROVIDER
    base_url = source.get("ASR_BASE_URL", "").strip()
    api_key = source.get("ASR_API_KEY", "").strip()
    transcribe_path = (
        source.get("ASR_TRANSCRIBE_PATH", DEFAULT_TRANSCRIBE_PATH).strip()
        or DEFAULT_TRANSCRIBE_PATH
    )
    model = source.get("ASR_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    timeout_ms = _positive_int(source, "ASR_TIMEOUT_MS", DEFAULT_TIMEOUT_MS)
    max_file_size_mb = _positive_int(
        source,
        "ASR_MAX_FILE_SIZE_MB",
        DEFAULT_MAX_FILE_SIZE_MB,
    )

    if require_credentials and not base_url:
        raise AsrConfigError("ASR_BASE_URL is required")
    if require_credentials and not api_key:
        raise AsrConfigError("ASR_API_KEY is required")
    if require_credentials and api_key.lower() in PLACEHOLDER_API_KEYS:
        raise AsrConfigError("ASR_API_KEY must not be a placeholder")

    return AsrConfig(
        provider=provider,
        base_url=base_url,
        transcribe_path=transcribe_path,
        api_key=api_key,
        model=model,
        timeout_ms=timeout_ms,
        max_file_size_mb=max_file_size_mb,
        allowed_media_types=_media_types(source),
    )
