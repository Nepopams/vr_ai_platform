# ASR Cloud.ru Whisper UAT Rollout Guide

## Purpose

This guide describes the extra configuration and UAT rollout steps for
`POST /v1/asr/transcribe`.

UAT goal: prove that the AI Platform ASR endpoint can call the real Cloud.ru
Whisper model, return a non-empty transcript, and keep logs free of raw audio,
transcript, raw user text, and raw upstream responses.

## Source Anchors

- Runtime setup: `docs/guides/asr-cloudru-whisper.md`
- API contract: `docs/contracts/asr-transcription-api.md`
- Boundary ADR: `docs/adr/ADR-008-asr-cloudru-whisper-mvp.md`
- Workpack review: `docs/planning/workpacks/ST-047/review-report.md`

Cloud.ru docs checked on 2026-06-14 confirm:

- Foundation Models base endpoint: `https://foundation-models.api.cloud.ru/v1/`
- API key authentication for Foundation Models
- `openai/whisper-large-v3` as an internal Audio-to-Text model

The public Cloud.ru OpenAPI spec currently documents only models and chat
completions. Keep `ASR_TRANSCRIBE_PATH` configurable during UAT and record the
confirmed ASR path/response shape before production enablement.

## Preconditions

Before deploying to UAT:

1. UAT has a deployable build that includes ST-047.
2. The UAT operator has a Cloud.ru Foundation Models API key with access to
   `openai/whisper-large-v3`.
3. A short test audio file is available on the UAT host, for example
   `/opt/vr-ai-platform/uat-samples/asr-sample.wav`.
   If the repository sample is available, use `tests/fixtures/asr/uat-sample.wav`.
4. The audio file contains non-sensitive test speech only.
5. UAT ingress can reach `POST /v1/asr/transcribe`.
6. UAT logs are accessible for privacy verification.

Do not use production user recordings for UAT smoke.

## Required UAT Environment

Set these variables in the UAT service environment or secret manager:

```bash
ASR_PROVIDER=cloudru
ASR_BASE_URL=https://foundation-models.api.cloud.ru/v1
ASR_TRANSCRIBE_PATH=/audio/transcriptions
ASR_API_KEY=<secret-from-secret-manager>
ASR_MODEL=openai/whisper-large-v3
ASR_TIMEOUT_MS=30000
ASR_MAX_FILE_SIZE_MB=25
ASR_LOG_ENABLED=true
ASR_LOG_PATH=/var/log/vr-ai-platform/asr_transcriptions.jsonl
LOG_USER_TEXT=false
```

`ASR_API_KEY` must not be stored in git, shell history, screenshots, tickets, or
plain-text runbooks. Placeholder values such as `your-asr-api-key-here` are
rejected at runtime.

If Cloud.ru confirms a different ASR endpoint path during UAT, update only:

```bash
ASR_TRANSCRIBE_PATH=<confirmed-path>
```

Then rerun the UAT smoke and update the ASR contract docs before production.

## Deployment Steps

1. Deploy the ST-047 build to UAT using the normal AI Platform deployment path.
2. Add the `ASR_*` variables to the UAT service environment.
3. Restart the service.

```bash
sudo systemctl restart vr-ai-platform
curl -fsS http://127.0.0.1:8000/health
curl -fsS http://127.0.0.1:8000/ready
```

4. Confirm the ASR route is available through the UAT service endpoint.

```bash
curl -i -X POST http://127.0.0.1:8000/v1/asr/transcribe
```

Expected result for an empty/non-multipart call is a controlled ASR error, not a
service crash. A `400 invalid_multipart` response is acceptable here.

## UAT Smoke via pytest

Run this on the UAT host with the real Cloud.ru key loaded in the environment:

```bash
export ASR_REAL_SMOKE_ENABLED=true
export ASR_API_KEY=<secret-from-secret-manager>
export ASR_BASE_URL=https://foundation-models.api.cloud.ru/v1
export ASR_TRANSCRIBE_PATH=/audio/transcriptions
export ASR_SMOKE_AUDIO_PATH=tests/fixtures/asr/uat-sample.wav
export ASR_LOG_ENABLED=true
export LOG_USER_TEXT=false

python3 -m pytest tests/test_asr_integration_smoke.py -v
```

Expected result:

- `test_real_cloudru_asr_transcription_roundtrip` passes.
- Response status is `200`.
- `transcript` is a non-empty string.
- `provider`, `model`, `trace_id`, `latency_ms`, and `upstream_status` are present.
- The ASR log does not contain the returned transcript.

PowerShell variant for a Windows UAT runner:

```powershell
$env:ASR_REAL_SMOKE_ENABLED = "true"
$env:ASR_API_KEY = "<secret-from-secret-manager>"
$env:ASR_BASE_URL = "https://foundation-models.api.cloud.ru/v1"
$env:ASR_TRANSCRIBE_PATH = "/audio/transcriptions"
$env:ASR_SMOKE_AUDIO_PATH = "C:\uat-samples\asr-sample.wav"
$env:ASR_LOG_ENABLED = "true"
$env:LOG_USER_TEXT = "false"

python3 -m pytest tests/test_asr_integration_smoke.py -v
```

## UAT Smoke via HTTP

After the service is running, call the deployed endpoint:

```bash
curl -fsS -X POST http://127.0.0.1:8000/v1/asr/transcribe \
  -F "file=@tests/fixtures/asr/uat-sample.wav;type=audio/wav"
```

Expected response shape:

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

The platform ASR endpoint does not require a client `Authorization` header in the
MVP. It uses `ASR_API_KEY` only for the upstream Cloud.ru call.

## Privacy Verification

After a successful UAT call:

```bash
tail -n 5 /var/log/vr-ai-platform/asr_transcriptions.jsonl
```

The log may contain only safe metadata:

- `request_id`
- `trace_id`
- `provider`
- `model`
- `status`
- `latency_ms`
- `file_size_bucket`
- `error_type`
- `upstream_status`

The log must not contain:

- raw audio bytes
- transcript text
- raw user text
- prompts
- raw Cloud.ru response bodies
- API keys

If the test audio transcript is known, verify it is absent from logs:

```bash
rg "<known transcript phrase>" /var/log/vr-ai-platform/asr_transcriptions.jsonl
```

Expected result: no matches.

## UAT GO Criteria

Mark ASR UAT as GO only when all items pass:

- `/health` and `/ready` return success after deployment.
- `POST /v1/asr/transcribe` returns `200` for the UAT sample audio.
- Transcript is non-empty and plausibly matches the sample audio.
- ASR metadata log is written.
- ASR metadata log does not contain transcript, raw audio, raw user text, raw
  upstream response, or API key.
- Existing `/v1/decide` smoke still works.
- No changes were required in `contracts/schemas/**`, `contracts/VERSION`,
  `graphs/**`, or RouterV2.
- The confirmed Cloud.ru ASR path and response shape are recorded in
  `docs/contracts/asr-transcription-api.md`.

## NO-GO Conditions

Stop UAT and do not enable ASR for production if any condition is true:

- Cloud.ru returns an unconfirmed endpoint or response shape that the current
  client cannot parse.
- ASR logs contain transcript, raw audio, raw user text, raw upstream response,
  or API keys.
- `/v1/decide` behavior changes after the ASR deployment.
- The ASR endpoint requires CommandDTO/DecisionDTO schema changes.
- UAT requires storing audio files on the AI Platform side.

## Troubleshooting

| Symptom | Likely cause | Action |
|---------|--------------|--------|
| `500 asr_config_error` | Missing env var or placeholder API key | Check `ASR_BASE_URL`, `ASR_API_KEY`, and service restart. |
| `502 auth_error` | Invalid key or no model access | Rotate/check Cloud.ru key and model permissions. |
| `502 upstream_unavailable` | Cloud.ru failure or wrong path | Confirm `ASR_BASE_URL` and `ASR_TRANSCRIBE_PATH`; retry once. |
| `502 bad_upstream_response` | Response JSON shape differs from MVP assumption | Capture sanitized shape, update contract/ADR if needed, then update client in a new workpack. |
| `504 timeout` | Upstream latency exceeds timeout | Increase `ASR_TIMEOUT_MS` for UAT and rerun smoke. |
| `413 file_too_large` | Audio exceeds `ASR_MAX_FILE_SIZE_MB` | Use a smaller UAT sample or raise the limit intentionally. |
| `415 unsupported_media` | Unsupported audio MIME type | Use wav/mp3/webm/ogg/flac or update allowlist through a governed change. |

## Rollback

Preferred rollback:

```bash
sudo systemctl stop vr-ai-platform
# deploy previous known-good artifact
sudo systemctl start vr-ai-platform
curl -fsS http://127.0.0.1:8000/health
curl -fsS http://127.0.0.1:8000/ready
```

If only ASR must be disabled while keeping the build:

1. Remove or unset `ASR_API_KEY` from the UAT service environment.
2. Optionally block `/v1/asr/transcribe` at ingress/API gateway.
3. Restart the service.
4. Confirm `/v1/decide`, `/health`, and `/ready` still work.

With missing ASR credentials, only the ASR endpoint returns a controlled
configuration error; the decision pipeline remains independent.

## UAT Evidence to Record

Record these items in the UAT ticket or release note:

- Deployment artifact/version.
- `ASR_BASE_URL`.
- Confirmed `ASR_TRANSCRIBE_PATH`.
- `ASR_MODEL`.
- Smoke command used.
- HTTP status and `trace_id`.
- Whether transcript matched the sample audio.
- Privacy log check result.
- `/v1/decide` regression smoke result.
- GO/NO-GO decision.
