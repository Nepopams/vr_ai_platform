# ASR Transcription API

**Status:** draft MVP
**Provider:** AI Platform
**Consumer:** Client / ConsumerApp
**Initiative:** `docs/planning/initiatives/INIT-2026Q2-asr-cloudru-whisper.md`
**ADR:** `docs/adr/ADR-008-asr-cloudru-whisper-mvp.md`

## Endpoint

`POST /v1/asr/transcribe`

The endpoint accepts one audio file and returns transcript text. It does not call
`/v1/decide`, RouterV2, Assist Mode, or Partial Trust.

## Request

Content type: `multipart/form-data`

Required fields:

| Field | Type | Description |
|-------|------|-------------|
| `file` | binary file | One audio file. |

Supported media types for MVP:

- `audio/mpeg`
- `audio/mp3`
- `audio/mp4`
- `audio/m4a`
- `audio/wav`
- `audio/x-wav`
- `audio/webm`
- `audio/ogg`
- `audio/flac`

## Response: 200

```json
{
  "transcript": "Добавь молоко в список покупок",
  "provider": "cloudru",
  "model": "openai/whisper-large-v3",
  "status": "ok",
  "trace_id": "trace-asr-...",
  "latency_ms": 1234,
  "upstream_status": 200
}
```

## Error Responses

The ASR endpoint returns controlled JSON errors:

```json
{
  "error": "unsupported_media",
  "message": "Unsupported audio media type.",
  "trace_id": "trace-asr-..."
}
```

| HTTP | `error` | Meaning |
|------|---------|---------|
| 400 | `invalid_multipart` | Request is not a valid single-file multipart body. |
| 400 | `missing_audio_file` | No `file` part was provided. |
| 413 | `file_too_large` | File exceeds configured max size. |
| 415 | `unsupported_media` | File media type is not in the MVP allowlist. |
| 500 | `asr_config_error` | Required ASR provider config is missing or invalid. |
| 502 | `auth_error` | Upstream Cloud.ru authentication failed. |
| 502 | `bad_upstream_response` | Upstream response is malformed or unsupported. |
| 502 | `upstream_unavailable` | Upstream returned a retryable/non-auth failure. |
| 504 | `timeout` | Upstream ASR call timed out. |

## Environment

| Env var | Default | Description |
|---------|---------|-------------|
| `ASR_PROVIDER` | `cloudru` | Provider label in responses/logs. |
| `ASR_BASE_URL` | empty | Required upstream base URL, e.g. `https://foundation-models.api.cloud.ru/v1`. |
| `ASR_TRANSCRIBE_PATH` | `/audio/transcriptions` | Configurable OpenAI-compatible transcription path. |
| `ASR_API_KEY` | empty | Required Cloud.ru Foundation Models API key. |
| `ASR_MODEL` | `openai/whisper-large-v3` | ASR model id. |
| `ASR_TIMEOUT_MS` | `30000` | Upstream timeout. |
| `ASR_MAX_FILE_SIZE_MB` | `25` | Max accepted file size. |
| `ASR_LOG_ENABLED` | `true` | Enable safe ASR metadata logs. |
| `ASR_LOG_PATH` | `logs/asr_transcriptions.jsonl` | JSONL log path. |

## Privacy

The platform must not store raw audio. Logs must not include raw audio, transcript,
raw user text, prompt, or raw upstream output. Logs may include only safe metadata:
request_id/trace_id, provider, model, status, latency_ms, file_size_bucket, and error_type.

`ASR_API_KEY` placeholder values such as `your-asr-api-key-here` are rejected at runtime.

## Cloud.ru Contract Discovery

Public Cloud.ru docs checked on 2026-06-14 confirm:

- Foundation Models API base endpoint: `https://foundation-models.api.cloud.ru/v1/`
- API key authentication for Foundation Models
- `openai/whisper-large-v3` is available as an internal Audio-to-Text model

The downloadable public OpenAPI/Postman specs currently list only models and chat
completion methods. Because the audio transcription method is not listed there, this
MVP keeps `ASR_TRANSCRIBE_PATH` configurable and requires manual UAT smoke before
production enablement.
