"""Pydantic models for ASR API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AsrTranscriptionResponse(BaseModel):
    """Typed response for `/v1/asr/transcribe`."""

    model_config = ConfigDict(extra="forbid")

    transcript: str
    provider: str
    model: str
    status: Literal["ok"] = "ok"
    trace_id: str
    latency_ms: int = Field(ge=0)
    upstream_status: int
