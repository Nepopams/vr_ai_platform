# Codex APPLY Prompt — ST-047: ASR Transcription Endpoint MVP

## Role

You are a senior Python/FastAPI developer implementing ASR transcription MVP.

## Rules

- Follow `docs/planning/workpacks/ST-047/workpack.md`.
- Modify only allowed files.
- Do not edit `contracts/schemas/**`, `contracts/VERSION`, `graphs/**`, or `routers/**`.
- Do not call RouterV2 or `/v1/decide` from the ASR endpoint.
- Do not log transcript, raw audio, raw user text, prompt, or raw upstream body.
- Real Cloud.ru calls must not run in unit tests.

## PLAN Findings Summary

- Use a separate `app.routes.asr` router and mount it only under `/v1`.
- Use `httpx.Client` for upstream calls.
- Avoid `UploadFile` because `python-multipart` is not present locally.
- Use env-driven `ASR_*` config and safe defaults.
- Keep Cloud.ru path configurable via `ASR_TRANSCRIBE_PATH`.

## Verification

```bash
python3 -m pytest tests/test_asr_config.py tests/test_asr_client.py tests/test_asr_transcribe_api.py tests/test_asr_privacy.py -v
python3 -m pytest tests/test_api_decide.py tests/test_api_versioned.py -v
make validate_contracts
```
