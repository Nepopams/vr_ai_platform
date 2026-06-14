# EP-015: ASR Cloud.ru Whisper Transcription MVP

**Status:** Implemented (manual Cloud.ru UAT pending)
**Initiative:** `docs/planning/initiatives/INIT-2026Q2-asr-cloudru-whisper.md`
**Roadmap:** `docs/planning/strategy/roadmap.md`
**Owner:** Codex

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Roadmap | `docs/planning/strategy/roadmap.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q2-asr-cloudru-whisper.md` |
| ADR | `docs/adr/ADR-008-asr-cloudru-whisper-mvp.md` |
| ASR API contract | `docs/contracts/asr-transcription-api.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Goal

Deliver a minimal production-like ASR capability for one audio file:

- client sends audio to `/v1/asr/transcribe`;
- AI Platform sends audio to Cloud.ru Whisper through a configurable client;
- client receives transcript text;
- transcript is not automatically routed into `/v1/decide`;
- logs stay privacy-safe.

## Scope

### In scope

- Add ASR endpoint under `/v1`.
- Add internal Cloud.ru ASR client.
- Add env-driven configuration.
- Add controlled ASR error mapping.
- Add safe ASR metadata logging.
- Add unit/integration tests with mocked Cloud.ru.
- Add local/UAT documentation.

### Out of scope

- Streaming ASR.
- Diarization / speaker separation.
- Chunking long audio files.
- Audio storage.
- Async jobs / queues.
- Automatic transcript submission to `/v1/decide`.
- ASR Agent / agent orchestration.
- Multi-provider abstraction beyond a provider label/config.
- UI upload flow.
- Rate limiting.
- Billing / quota accounting.

## Stories

| Story ID | Title | Status | Flags |
|----------|-------|--------|-------|
| [ST-047](stories/ST-047-asr-transcription-endpoint-mvp.md) | ASR transcription endpoint MVP | Ready | contract_impact=additive-public-api, adr_needed=yes, diagrams_needed=yes, security_sensitive=yes, traceability_critical=yes |

## Artifact Gate

| Area | Decision |
|------|----------|
| Contract | Additive HTTP API contract only; no CommandDTO/DecisionDTO schema change; no `contracts/VERSION` bump. |
| ADR | ADR-008 accepted for ASR boundary, Cloud.ru contract ambiguity, and privacy constraints. |
| Diagram | `docs/diagrams/asr-cloudru-whisper-flow.puml` documents the new flow and non-call into RouterV2. |
| Security/privacy | Requires tests proving logs exclude audio/transcript/raw user text. |
