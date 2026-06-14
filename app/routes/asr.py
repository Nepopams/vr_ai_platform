"""ASR transcription API route."""

from __future__ import annotations

import time
from uuid import uuid4

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.asr.client import CloudRuAsrClient
from app.asr.config import DEFAULT_MODEL, DEFAULT_PROVIDER, AsrConfig, load_asr_config
from app.asr.errors import AsrError, FileTooLargeError
from app.asr.multipart import AsrAudioFile, parse_single_audio_file
from app.logging.asr_log import append_asr_log, file_size_bucket
from app.models.asr_models import AsrTranscriptionResponse

MULTIPART_OVERHEAD_BYTES = 64 * 1024

router = APIRouter()


@router.post("/asr/transcribe", response_model=AsrTranscriptionResponse)
async def transcribe_asr(request: Request):
    started = time.monotonic()
    trace_id = f"trace-asr-{uuid4().hex}"
    config: AsrConfig | None = None
    audio: AsrAudioFile | None = None

    try:
        config = load_asr_config()
        _reject_large_content_length(request, config.max_file_size_bytes)
        audio = parse_single_audio_file(
            body=await request.body(),
            content_type=request.headers.get("content-type", ""),
            max_file_size_bytes=config.max_file_size_bytes,
            allowed_media_types=config.allowed_media_types,
        )
        result = CloudRuAsrClient(config).transcribe(audio)
    except AsrError as exc:
        log_payload = {
            "request_id": trace_id,
            "trace_id": trace_id,
            "provider": config.provider if config else DEFAULT_PROVIDER,
            "model": config.model if config else DEFAULT_MODEL,
            "status": "error",
            "latency_ms": int((time.monotonic() - started) * 1000),
            "file_size_bucket": file_size_bucket(audio.size_bytes if audio else None),
            "error_type": exc.error_type,
        }
        log_payload.update(exc.log_details)
        append_asr_log(log_payload)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_type,
                "message": exc.message,
                "trace_id": trace_id,
            },
        )

    append_asr_log(
        {
            "request_id": trace_id,
            "trace_id": trace_id,
            "provider": result.provider,
            "model": result.model,
            "status": "ok",
            "latency_ms": int((time.monotonic() - started) * 1000),
            "file_size_bucket": file_size_bucket(audio.size_bytes),
            "upstream_status": result.upstream_status,
        }
    )
    return AsrTranscriptionResponse(
        transcript=result.transcript,
        provider=result.provider,
        model=result.model,
        trace_id=trace_id,
        latency_ms=result.latency_ms,
        upstream_status=result.upstream_status,
    )


def _reject_large_content_length(request: Request, max_file_size_bytes: int) -> None:
    raw = request.headers.get("content-length")
    if not raw:
        return
    try:
        content_length = int(raw)
    except ValueError:
        return
    if content_length > max_file_size_bytes + MULTIPART_OVERHEAD_BYTES:
        raise FileTooLargeError("Audio file exceeds ASR_MAX_FILE_SIZE_MB.")
