"""Cloud.ru/OpenAI-compatible ASR transcription client."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import httpx

from app.asr.config import AsrConfig
from app.asr.errors import (
    AsrAuthError,
    AsrTimeoutError,
    BadUpstreamResponseError,
    FileTooLargeError,
    UnsupportedMediaError,
    UpstreamUnavailableError,
)
from app.asr.multipart import AsrAudioFile


@dataclass(frozen=True)
class AsrTranscriptionResult:
    transcript: str
    provider: str
    model: str
    latency_ms: int
    upstream_status: int


class CloudRuAsrClient:
    """ASR client using a configurable OpenAI-compatible transcription path."""

    def __init__(self, config: AsrConfig) -> None:
        self._config = config

    def transcribe(self, audio: AsrAudioFile) -> AsrTranscriptionResult:
        started = time.monotonic()
        response = self._post_audio(audio)
        latency_ms = int((time.monotonic() - started) * 1000)
        transcript = self._extract_transcript(response)
        return AsrTranscriptionResult(
            transcript=transcript,
            provider=self._config.provider,
            model=self._config.model,
            latency_ms=latency_ms,
            upstream_status=response.status_code,
        )

    def _post_audio(self, audio: AsrAudioFile) -> httpx.Response:
        headers = {"Authorization": f"Bearer {self._config.api_key}"}
        data = {
            "model": self._config.model,
            "response_format": "json",
        }
        if self._config.language:
            data["language"] = self._config.language
        files = {
            "file": (audio.filename, audio.content, audio.content_type),
        }

        try:
            with httpx.Client(timeout=self._config.timeout_s) as client:
                response = client.post(
                    self._config.transcribe_url,
                    headers=headers,
                    data=data,
                    files=files,
                )
        except httpx.TimeoutException as exc:
            raise AsrTimeoutError("ASR upstream request timed out.") from exc
        except httpx.ConnectError as exc:
            raise UpstreamUnavailableError("ASR upstream connection failed.") from exc
        except httpx.HTTPError as exc:
            raise UpstreamUnavailableError("ASR upstream request failed.") from exc

        self._raise_for_status(response)
        return response

    def _raise_for_status(self, response: httpx.Response) -> None:
        status = response.status_code
        if status < 400:
            return
        if status in {401, 403}:
            raise AsrAuthError("ASR upstream authentication failed.")
        if status == 413:
            raise FileTooLargeError("ASR upstream rejected file as too large.")
        if status == 415:
            raise UnsupportedMediaError("ASR upstream rejected media type.")
        raise UpstreamUnavailableError("ASR upstream returned an error.")

    def _extract_transcript(self, response: httpx.Response) -> str:
        try:
            data = response.json()
        except ValueError as exc:
            raise BadUpstreamResponseError(
                "ASR upstream response is not JSON.",
                log_details=self._response_shape(response, None),
            ) from exc

        transcript = self._first_non_blank_text(data)
        if not isinstance(transcript, str) or not transcript.strip():
            raise BadUpstreamResponseError(
                "ASR upstream response has no text or transcript field.",
                log_details=self._response_shape(response, data),
            )
        return transcript

    def _first_non_blank_text(self, data: Any) -> str | None:
        if not isinstance(data, dict):
            return None

        for key in ("text", "transcript"):
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return value

        for container_key in ("data", "result"):
            nested = data.get(container_key)
            if isinstance(nested, dict):
                for key in ("text", "transcript"):
                    value = nested.get(key)
                    if isinstance(value, str) and value.strip():
                        return value

        return None

    def _response_shape(self, response: httpx.Response, data: Any) -> dict[str, Any]:
        details: dict[str, Any] = {
            "upstream_status": response.status_code,
            "upstream_content_type": response.headers.get("content-type"),
        }
        if isinstance(data, dict):
            details["upstream_response_keys"] = sorted(str(key) for key in data.keys())
            details["upstream_text_length"] = self._string_length(data.get("text"))
            details["upstream_transcript_length"] = self._string_length(data.get("transcript"))
            details["upstream_data_keys"] = self._nested_keys(data.get("data"))
            details["upstream_result_keys"] = self._nested_keys(data.get("result"))
        else:
            details["upstream_response_type"] = type(data).__name__ if data is not None else "non_json"
        return details

    def _string_length(self, value: Any) -> int | None:
        return len(value) if isinstance(value, str) else None

    def _nested_keys(self, value: Any) -> list[str] | None:
        if not isinstance(value, dict):
            return None
        return sorted(str(key) for key in value.keys())
