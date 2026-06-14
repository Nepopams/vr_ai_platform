# ASR Cloud.ru Whisper Setup

## Purpose

`POST /v1/asr/transcribe` accepts one audio file and returns transcript text.
The endpoint does not call `/v1/decide` automatically. A client that wants a
DecisionDTO must submit the returned transcript to `/v1/decide` in a separate request.

## Environment

```bash
ASR_PROVIDER=cloudru
ASR_BASE_URL=https://foundation-models.api.cloud.ru/v1
ASR_TRANSCRIBE_PATH=/audio/transcriptions
ASR_API_KEY=<secret>
ASR_MODEL=openai/whisper-large-v3
ASR_LANGUAGE=ru
ASR_TIMEOUT_MS=30000
ASR_MAX_FILE_SIZE_MB=25
ASR_LOG_ENABLED=true
ASR_LOG_PATH=logs/asr_transcriptions.jsonl
```

Replace the placeholder `ASR_API_KEY` value before UAT. Placeholder values are rejected
as ASR configuration errors.

`ASR_TRANSCRIBE_PATH` is intentionally configurable. Public Cloud.ru docs checked
on 2026-06-14 confirm the Foundation Models base URL and the
`openai/whisper-large-v3` Audio-to-Text model, but the downloadable public OpenAPI
spec currently lists only models and chat completions.

`ASR_LANGUAGE=ru` is sent to the upstream transcription call to keep Russian UAT
audio as Russian text instead of an English translation. Set `ASR_LANGUAGE=` only
if auto language detection is required.

## Local Tests

Real Cloud.ru is not called by unit/integration tests.

```bash
python3 -m pytest tests/test_asr_config.py tests/test_asr_client.py tests/test_asr_transcribe_api.py tests/test_asr_privacy.py -v
```

## Manual UAT Smoke

Use a real Cloud.ru Foundation Models API key and a small audio file.

For the full UAT rollout checklist, service restart flow, GO/NO-GO criteria,
privacy verification, and rollback steps, see
`docs/guides/asr-cloudru-whisper-uat-rollout.md`.

### Via pytest

The real Cloud.ru smoke test is skipped by default. Enable it explicitly:

```bash
ASR_REAL_SMOKE_ENABLED=true \
ASR_API_KEY=<secret> \
ASR_BASE_URL=https://foundation-models.api.cloud.ru/v1 \
ASR_TRANSCRIBE_PATH=/audio/transcriptions \
ASR_LANGUAGE=ru \
ASR_SMOKE_AUDIO_PATH=/path/to/sample.wav \
python3 -m pytest tests/test_asr_integration_smoke.py -v
```

### Via curl

```bash
curl -X POST http://127.0.0.1:8000/v1/asr/transcribe \
  -F "file=@sample.wav;type=audio/wav"
```

The platform ASR endpoint does not require the client `Authorization` header in MVP.
It uses `ASR_API_KEY` only for the upstream Cloud.ru call.

Expected response:

```json
{
  "transcript": "...",
  "provider": "cloudru",
  "model": "openai/whisper-large-v3",
  "status": "ok",
  "trace_id": "trace-asr-...",
  "latency_ms": 1234,
  "upstream_status": 200
}
```

## Privacy

`logs/asr_transcriptions.jsonl` contains safe metadata only:

- request_id / trace_id
- provider
- model
- status
- latency_ms
- file_size_bucket
- error_type
- upstream_status

It must not contain raw audio, transcript, raw user text, prompts, or raw upstream
responses.
