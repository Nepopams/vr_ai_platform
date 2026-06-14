"""Controlled ASR errors."""

from __future__ import annotations


class AsrError(Exception):
    """Base class for controlled ASR platform errors."""

    error_type = "asr_error"
    status_code = 500

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class AsrConfigError(AsrError):
    error_type = "asr_config_error"
    status_code = 500


class InvalidMultipartError(AsrError):
    error_type = "invalid_multipart"
    status_code = 400


class MissingAudioFileError(AsrError):
    error_type = "missing_audio_file"
    status_code = 400


class FileTooLargeError(AsrError):
    error_type = "file_too_large"
    status_code = 413


class UnsupportedMediaError(AsrError):
    error_type = "unsupported_media"
    status_code = 415


class AsrTimeoutError(AsrError):
    error_type = "timeout"
    status_code = 504


class AsrAuthError(AsrError):
    error_type = "auth_error"
    status_code = 502


class UpstreamUnavailableError(AsrError):
    error_type = "upstream_unavailable"
    status_code = 502


class BadUpstreamResponseError(AsrError):
    error_type = "bad_upstream_response"
    status_code = 502
