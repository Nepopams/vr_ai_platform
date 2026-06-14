# Roadmap (Now / Next / Later) — aligned with Initiatives

Этот roadmap построен вокруг списка инициатив `docs/planning/initiatives/` и отражает
их порядок приоритетности: **High → Medium → Low**.

---

## Completed

| Phase | Period | Sprints | Stories | Tests | Initiatives |
|-------|--------|---------|---------|-------|-------------|
| 2026Q1 | S01 | 1 | 4/4 | 0→109 | shadow-router, assist-mode |
| 2026Q2 | S02-S04 | 3 | 9/9 | 109→202 | partial-trust, multi-entity-extraction, improved-clarify |
| 2026Q3 | S05 | 1 | 6/6 | 202→228 | semver-and-ci, agent-registry-integration, codex-integration (organically) |
| 2026Q4 | S06-S08 | 3 | 11/11 | 228→270 | production-hardening |
| **Total** | | **8** | **30/30** | **270** | **9 done** |

Детали закрытых инициатив: `docs/planning/initiatives/INIT-*.md`.
Ретроспективы: `docs/planning/sprints/S01..S08/retro.md`.

---

## CURRENT (2026Q2 / PI TBD) — ASR Capability: Cloud.ru Whisper Transcription MVP

Цель фазы: добавить MVP-capability для speech-to-text через Cloud.ru Foundation Models и модель `openai/whisper-large-v3`.

1) **INIT-2026Q2-asr-cloudru-whisper** — ASR Capability: Cloud.ru Whisper Transcription MVP (**Высокий**)
- ASR endpoint для одного аудиофайла, например `POST /v1/asr/transcribe`
- Внутренний Cloud.ru ASR client с моделью по умолчанию `openai/whisper-large-v3`
- Конфигурация через env: base URL, API key, model, timeout, max file size
- Privacy-safe logging без raw audio и transcript по умолчанию
- Unit/integration тесты с mock Cloud.ru и документация для локального/UAT smoke

**Gates:**
- Перед финализацией клиента зафиксирован фактический Cloud.ru ASR API contract: endpoint, auth, request format, response format
- Endpoint не отправляет transcript автоматически в RouterV2 или `/decide`
- Raw audio не сохраняется платформой; raw audio и transcript не логируются по умолчанию
- Существующий `/decide`, RouterV2, Assist Mode и Partial Trust не меняют поведение
- Реальный Cloud.ru вызов не требуется для unit tests; real API остается manual smoke/UAT

**Success signals:**
- `POST /v1/asr/transcribe` принимает `multipart/form-data` с одним audio file и возвращает typed transcript result
- Ошибки Cloud.ru нормализованы в platform errors: timeout, auth error, unsupported media, file too large, upstream unavailable, bad upstream response
- Логи содержат только safe metadata: request_id/trace_id, provider, model, status, latency_ms, file_size_bucket, error_type
- Добавлены endpoint/privacy tests и ASR MVP planning note или ADR по границам capability

---

## NEXT — TBD

Кандидаты определяются PO.

---

## LATER — TBD

---

## Prioritization principles

- Сначала измеримость и безопасность, потом "умность"
- Любая LLM-фича должна иметь deterministic fallback и kill-switch
- Контракты и DecisionDTO — стабильная граница ответственности
- Расширяемость = через инициативы, ADR и совместимость, а не через "быстрые хаки"
