# ADR-008: ASR Cloud.ru Whisper Transcription MVP

**Status**: Accepted
**Date**: 2026-06-14
**Initiative**: INIT-2026Q2-asr-cloudru-whisper
**Story**: ST-047
**Related**: ADR-001-P, ADR-007-P

## Context

The current roadmap marks `INIT-2026Q2-asr-cloudru-whisper` as the active initiative.
The platform needs a minimal speech-to-text capability so a client can submit one audio
file and receive a transcript text.

This capability changes the public HTTP API surface, but it must not change the
DecisionDTO pipeline:

- ASR is not an intent router.
- ASR must not call RouterV2 or `/decide` automatically.
- ASR returns text only; the client decides whether to send that text to `/v1/decide`.
- Raw audio and transcript must not be logged by default.

Cloud.ru contract discovery was performed against the public Cloud.ru Foundation Models
documentation on 2026-06-14:

- Model catalog lists `openai/whisper-large-v3` as an internal `Audio-to-Text` model.
- API authentication docs require a Foundation Models API key.
- API reference documents the base endpoint `https://foundation-models.api.cloud.ru/v1/`.
- Downloaded public OpenAPI/Postman specs are OpenAI-compatible but currently list only
  `GET /v1/models` and `POST /v1/chat/completions`.

Therefore the ASR transport must remain configurable. The MVP can use the
OpenAI-compatible audio transcription shape as the default profile, but the actual
Cloud.ru ASR request/response must be verified during manual UAT smoke with a real key
before production enablement.

## Decision

We will add a separate ASR HTTP endpoint:

- `POST /v1/asr/transcribe`
- Request: `multipart/form-data` with exactly one audio file field named `file`.
- Response: typed JSON result with transcript text, provider, model, status, trace_id,
  latency metadata, and upstream status metadata.

We will add an internal Cloud.ru ASR client with these properties:

- Provider defaults to `cloudru`.
- Model defaults to `openai/whisper-large-v3`.
- Base URL, path, API key, timeout, max file size, provider, and model are env-configured.
- The default upstream path is OpenAI-compatible (`/audio/transcriptions`) and is
  configurable via env to avoid hardcoding an unverified Cloud.ru-only path.
- The client accepts success bodies containing a top-level `text` string and rejects
  malformed upstream responses as controlled platform errors.

We will add privacy-safe ASR logging:

- No raw audio bytes.
- No transcript text.
- No raw user text.
- Safe metadata only: request_id/trace_id, provider, model, status, latency_ms,
  file_size_bucket, and error_type.

We will not modify:

- `contracts/schemas/command.schema.json`
- `contracts/schemas/decision.schema.json`
- `contracts/VERSION`
- `graphs/core_graph.py`
- RouterV2 behavior

## Contract Decision

This is an additive HTTP API endpoint under the existing API version prefix `/v1`.
It does not change CommandDTO or DecisionDTO schemas and does not require an ADR-001
schema version bump.

The ASR API contract is documented separately in:

- `docs/contracts/asr-transcription-api.md`

## Consequences

### Positive

- Adds speech-to-text capability without weakening deterministic decision boundaries.
- Keeps ASR isolated from RouterV2 and DecisionDTO.
- Allows Cloud.ru UAT without committing raw audio/transcript to logs.
- Keeps upstream ASR path configurable while public Cloud.ru audio endpoint docs remain
  incomplete.

### Negative

- Manual UAT is required to confirm the real Cloud.ru ASR endpoint and response shape.
- MVP reads one audio file into memory after max-size validation; streaming and chunking
  remain out of scope.
- ASR errors are localized to the ASR endpoint until ST-035 standardizes global
  problem+json responses.

## Alternatives Considered

| Option | Decision | Reason |
|--------|----------|--------|
| Feed ASR transcript directly into `/v1/decide` | Rejected | Violates initiative scope and hides a new RouterV2 input path. |
| Build ASR as an agent | Rejected | Agent orchestration is explicitly out of scope for the ASR MVP. |
| Require `python-multipart` and FastAPI `UploadFile` | Deferred | The current local environment lacks `python-multipart`; MVP can parse one bounded multipart request without adding a runtime dependency. |
| Hardcode Cloud.ru audio endpoint | Rejected | Public Cloud.ru OpenAPI currently does not list audio transcription; endpoint must be configurable. |

## Acceptance Criteria

ADR-008 is satisfied when:

1. `POST /v1/asr/transcribe` exists and accepts one multipart audio file.
2. The endpoint returns a typed transcript response and never calls RouterV2.
3. Cloud.ru ASR client config is controlled through env variables.
4. Unit/integration tests mock Cloud.ru and cover success, timeout, invalid file type,
   file too large, upstream error, and privacy logging.
5. Documentation explains local mock tests and manual Cloud.ru UAT smoke.
