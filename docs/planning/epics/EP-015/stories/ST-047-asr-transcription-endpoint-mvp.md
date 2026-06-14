# ST-047: ASR Transcription Endpoint MVP

**Epic:** EP-015 (ASR Cloud.ru Whisper Transcription MVP)
**Status:** Implemented (manual Cloud.ru UAT pending)
**Flags:** contract_impact=additive-public-api, adr_needed=yes, diagrams_needed=yes, security_sensitive=yes, traceability_critical=yes

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Roadmap | `docs/planning/strategy/roadmap.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q2-asr-cloudru-whisper.md` |
| Epic | `docs/planning/epics/EP-015/epic.md` |
| ADR | `docs/adr/ADR-008-asr-cloudru-whisper-mvp.md` |
| ASR API contract | `docs/contracts/asr-transcription-api.md` |
| Existing app factory | `app/main.py` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## User Value

As a client developer, I want to upload one audio file and receive transcript text,
so that voice input can be converted to text before an explicit `/v1/decide` call.

## Acceptance Criteria

1. `POST /v1/asr/transcribe` accepts `multipart/form-data` with exactly one `file` part.
2. Supported media types are allowlisted; unsupported media returns a controlled 415 error.
3. File size is bounded by `ASR_MAX_FILE_SIZE_MB`; oversized files return 413.
4. Cloud.ru ASR config is env-driven: base URL, path, API key, provider, model, timeout, max file size.
5. Cloud.ru ASR client returns a typed internal result: transcript, provider, model, latency/status metadata.
6. Cloud.ru/upstream errors are normalized: timeout, auth error, unsupported media, file too large, upstream unavailable, bad upstream response.
7. Raw audio is not stored by the platform.
8. Raw audio and transcript are not logged by default.
9. Logs contain only safe metadata: request_id/trace_id, provider, model, status, latency_ms, file_size_bucket, error_type.
10. Existing `/decide`, `/v1/decide`, RouterV2, Assist Mode, and Partial Trust behavior are unchanged.
11. Unit/integration tests mock Cloud.ru; no real Cloud.ru call is required in CI.
12. Tests cover success, timeout, invalid file type, file too large, upstream error, and privacy logging.
13. Documentation covers env, local mock tests, and manual UAT smoke.

## Out of Scope

- Streaming, diarization, chunking, audio storage, queues, UI upload, ASR agent, multi-provider orchestration.
- Automatic transcript submission into `/v1/decide`.
- CommandDTO/DecisionDTO schema changes.

## Test Strategy

- `tests/test_asr_config.py`: env defaults and validation.
- `tests/test_asr_client.py`: mocked `httpx` success/error/timeout/bad response.
- `tests/test_asr_transcribe_api.py`: endpoint success and controlled errors.
- `tests/test_asr_privacy.py`: ASR logs exclude transcript, raw audio, and raw user text.
- Regression: existing decide/versioned API tests continue to pass.
