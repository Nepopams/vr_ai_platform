"""Privacy-safe ASR metadata logging."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

DEFAULT_LOG_PATH = Path("logs/asr_transcriptions.jsonl")
ALLOWED_LOG_FIELDS = {
    "request_id",
    "trace_id",
    "provider",
    "model",
    "status",
    "latency_ms",
    "file_size_bucket",
    "error_type",
    "upstream_status",
    "upstream_content_type",
    "upstream_response_keys",
    "upstream_response_type",
    "upstream_text_length",
    "upstream_transcript_length",
    "upstream_data_keys",
    "upstream_result_keys",
    "upstream_error_keys",
    "upstream_error_code",
    "upstream_error_type",
    "upstream_error_status",
}


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def is_asr_log_enabled() -> bool:
    return os.getenv("ASR_LOG_ENABLED", "true").lower() in {"1", "true", "yes"}


def resolve_asr_log_path() -> Path:
    return Path(os.getenv("ASR_LOG_PATH", str(DEFAULT_LOG_PATH)))


def file_size_bucket(size_bytes: int | None) -> str:
    if size_bytes is None:
        return "unknown"
    mib = 1024 * 1024
    if size_bytes <= mib:
        return "0-1MB"
    if size_bytes <= 5 * mib:
        return "1-5MB"
    if size_bytes <= 25 * mib:
        return "5-25MB"
    return ">25MB"


def append_asr_log(payload: Dict[str, Any]) -> Path | None:
    # Privacy guard: ignore any caller-provided fields outside the allowlist.
    if not is_asr_log_enabled():
        return None

    path = resolve_asr_log_path()
    record = {
        key: value
        for key, value in payload.items()
        if key in ALLOWED_LOG_FIELDS
    }
    record.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    try:
        _ensure_parent(path)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"{json.dumps(record, ensure_ascii=False)}\n")
    except OSError:
        return None
    return path
