# ST-047 Review and Hardening Summary

**Date:** 2026-06-14
**Scope:** `INIT-2026Q2-asr-cloudru-whisper`
**Result:** GO for local ASR MVP; production enablement remains gated by manual Cloud.ru UAT.

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
| Manual Cloud.ru smoke ready | `tests/test_asr_integration_smoke.py` | Pass with external inputs pending |

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

## Open External Gate

Manual Cloud.ru UAT is still pending because the current environment does not provide:

- `ASR_REAL_SMOKE_ENABLED=true`
- `ASR_API_KEY`
- `ASR_BASE_URL`
- `ASR_SMOKE_AUDIO_PATH`

Public Cloud.ru docs checked on 2026-06-14 confirm the Foundation Models base endpoint
and the `openai/whisper-large-v3` Audio-to-Text model, but the downloadable public API
specification does not currently publish an audio transcription method. The implementation
therefore keeps `ASR_TRANSCRIBE_PATH` configurable and requires manual UAT before
production enablement.

## UAT Finding: Language Hint

Initial Cloud.ru smoke with Russian audio returned English text, which indicates that
the upstream Whisper profile may translate when no language hint is provided. The ASR
client now sends `ASR_LANGUAGE=ru` by default as the upstream `language` form field.
Set `ASR_LANGUAGE=` only when provider-side auto language detection is intentionally
required.

## Recommendation

Approve the local MVP for Human Gate D with one explicit follow-up: run the real Cloud.ru
ASR smoke test before enabling this capability in production.
