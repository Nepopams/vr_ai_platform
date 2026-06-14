"""Small single-file multipart parser for ASR MVP."""

from __future__ import annotations

from dataclasses import dataclass
from email.parser import BytesParser
from email.policy import default
from typing import Iterable

from app.asr.errors import (
    FileTooLargeError,
    InvalidMultipartError,
    MissingAudioFileError,
    UnsupportedMediaError,
)


@dataclass(frozen=True)
class AsrAudioFile:
    filename: str
    content_type: str
    content: bytes

    @property
    def size_bytes(self) -> int:
        return len(self.content)


def parse_single_audio_file(
    *,
    body: bytes,
    content_type: str,
    max_file_size_bytes: int,
    allowed_media_types: Iterable[str],
) -> AsrAudioFile:
    if "multipart/form-data" not in content_type.lower():
        raise InvalidMultipartError("ASR request must be multipart/form-data.")
    if "boundary=" not in content_type.lower():
        raise InvalidMultipartError("Multipart boundary is missing.")

    message = BytesParser(policy=default).parsebytes(
        b"Content-Type: "
        + content_type.encode("utf-8")
        + b"\r\nMIME-Version: 1.0\r\n\r\n"
        + body
    )
    if not message.is_multipart():
        raise InvalidMultipartError("Multipart body is malformed.")

    allowed = {item.lower() for item in allowed_media_types}
    file_parts: list[AsrAudioFile] = []
    for part in message.iter_parts():
        if part.get_content_disposition() != "form-data":
            continue
        if part.get_param("name", header="content-disposition") != "file":
            continue

        filename = part.get_filename() or "audio"
        media_type = (part.get_content_type() or "").lower()
        payload = part.get_payload(decode=True) or b""
        if not payload:
            raise InvalidMultipartError("Audio file is empty.")
        if len(payload) > max_file_size_bytes:
            raise FileTooLargeError("Audio file exceeds ASR_MAX_FILE_SIZE_MB.")
        if media_type not in allowed:
            raise UnsupportedMediaError("Unsupported audio media type.")
        file_parts.append(
            AsrAudioFile(
                filename=filename,
                content_type=media_type,
                content=payload,
            )
        )

    if not file_parts:
        raise MissingAudioFileError("Multipart body must include one file field.")
    if len(file_parts) > 1:
        raise InvalidMultipartError("ASR request must include exactly one file field.")
    return file_parts[0]
