# ST-047 Review and Hardening Summary

**Date:** 2026-06-14
**Scope:** `INIT-2026Q2-asr-cloudru-whisper`
**Result:** GO. Local ASR MVP is implemented and Cloud.ru UAT smoke passed.

## Summary

ST-047 adds a versioned ASR transcription endpoint, an env-driven Cloud.ru Whisper client,
controlled ASR errors, privacy-safe metadata logging, planning artifacts, and tests.

The ASR capability is intentionally isolated from RouterV2 and DecisionDTO. The endpoint
returns transcript text to the client and does not automatically submit it to `/v1/decide`.

## Evidence

| Requirement | Evidence | Result |
|-------------|----------|--------|
| Roadmap current initiative updated | `docs/planning/strategy/roadmap.md` | Pass |
| ADR accepted and indexed | `docs/adr/ADR-008-asr-cloudru-whisper-mvp.md`, `docs/_indexes/adr-index.md` | Pass |
| ASR API contract recorded | `docs/contracts/asr-transcription-api.md`, `docs/_indexes/contracts-index.md` | Pass |
| Diagram added and indexed | `docs/diagrams/asr-cloudru-whisper-flow.puml`, `docs/_indexes/diagrams-index.md` | Pass |
| Endpoint implemented | `app/routes/asr.py`, `app/main.py` | Pass |
| Configurable Cloud.ru client implemented | `app/asr/config.py`, `app/asr/client.py` | Pass |
| Controlled errors implemented | `app/asr/errors.py`, endpoint tests | Pass |
| Privacy-safe ASR logs implemented | `app/logging/asr_log.py`, `tests/test_asr_privacy.py` | Pass |
| RouterV2/DecisionDTO unchanged | forbidden-path diff check and ASR boundary grep | Pass |
| Local and UAT docs added | `docs/guides/asr-cloudru-whisper.md`, `docs/guides/asr-cloudru-whisper-uat-rollout.md` | Pass |
| Manual Cloud.ru smoke ready | `tests/test_asr_integration_smoke.py` | Pass |
| Real Cloud.ru ASR smoke | VPS curl smoke, trace `trace-asr-d198bf85f3724b1ab9348d038de8829e` | Pass |

## Validation

Latest local validation:

```bash
python3 -m pytest tests/test_asr_config.py tests/test_asr_client.py tests/test_asr_transcribe_api.py tests/test_asr_privacy.py tests/test_asr_integration_smoke.py -v
python3 -m pytest tests/ -v
python3 skills/contract-checker/scripts/validate_contracts.py
python3 skills/release_sanity.py
git diff --check
```

Observed result:

- ASR focused suite: 18 passed, 1 skipped.
- Full suite: 325 passed, 4 skipped.
- Contract checker: passed.
- Release sanity: passed.
- Whitespace check: passed.

## UAT Evidence

Manual Cloud.ru UAT smoke passed on 2026-06-14 against the VPS deployment.

Observed response:

- HTTP status: `200`
- provider: `cloudru`
- model: `openai/whisper-large-v3`
- upstream_status: `200`
- trace_id: `trace-asr-d198bf85f3724b1ab9348d038de8829e`
- latency_ms: `1509`
- transcript language: Russian after `ASR_LANGUAGE=ru`

Confirmed endpoint/config:

- `ASR_BASE_URL=https://foundation-models.api.cloud.ru/v1`
- `ASR_TRANSCRIBE_PATH=/audio/transcriptions`
- `ASR_MODEL=openai/whisper-large-v3`
- `ASR_LANGUAGE=ru`

Public Cloud.ru docs checked on 2026-06-14 confirm the Foundation Models base endpoint
and the `openai/whisper-large-v3` Audio-to-Text model. The downloadable public API
specification does not currently publish an audio transcription method, but the UAT
smoke confirms the OpenAI-compatible `/audio/transcriptions` path works for the current
Cloud.ru deployment.

## UAT Finding: Language Hint

Initial Cloud.ru smoke with Russian audio returned English text, which indicates that
the upstream Whisper profile may translate when no language hint is provided. The ASR
client now sends `ASR_LANGUAGE=ru` by default as the upstream `language` form field.
Set `ASR_LANGUAGE=` only when provider-side auto language detection is intentionally
required.

## Recommendation

Approve ST-047 for Human Gate D. The local MVP and real Cloud.ru UAT smoke are complete.
