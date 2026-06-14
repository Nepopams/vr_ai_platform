# INIT-2026Q2-asr-cloudru-whisper — ASR Capability: Cloud.ru Whisper Transcription MVP

**Приоритет:** Высокий
**Период:** 2026Q2 (PI TBD)
**Статус:** Implemented (manual Cloud.ru UAT pending)
**Owner:** TBD

## Контекст

AI Platform готова к нормальной разработке через Codex pipeline и уже поддерживает управляемое развитие LLM-функций через shadow / assist / partial trust подход.

Следующий необходимый capability для продукта — ASR: преобразование голосовой команды пользователя в текст. В MVP используется Cloud.ru Foundation Models и модель `openai/whisper-large-v3`.

Текущая задача — реализовать минимальный production-like ASR pipeline:

- принять один аудиофайл;
- отправить его в Cloud.ru Whisper;
- получить расшифровку;
- вернуть текст клиенту;
- не подключать результат автоматически к RouterV2;
- проверить на этой инициативе новый pipeline разработки Codex AI Platform от постановки до завершения.

Важно: Cloud.ru ASR API contract должен быть проверен отдельно перед реализацией клиента. Нельзя хардкодить endpoint/response shape без подтверждения.

## Цель

Добавить в AI Platform MVP-capability для speech-to-text:

- ASR endpoint для передачи одного аудиофайла;
- внутренний Cloud.ru ASR client;
- конфигурацию через env;
- безопасную обработку ошибок Cloud.ru;
- privacy-safe логирование без raw audio и transcript по умолчанию;
- unit/integration тесты с mock Cloud.ru;
- документацию для локального и UAT smoke-теста.

## Scope

### Epics

- **EP-TBD**: ASR API Contract Discovery & Cloud.ru Client
- **EP-TBD**: ASR Transcription Endpoint MVP
- **EP-TBD**: ASR Observability, Privacy & Test Readiness

### Out of scope

- Streaming ASR
- Диаризация / speaker separation
- Chunking длинных аудиофайлов
- Хранение аудио на стороне платформы
- Очереди и async job processing
- Автоматическая отправка transcript в `/decide`
- ASR Agent / agent orchestration
- Multi-provider ASR abstraction
- UI для загрузки аудио
- Rate limiting
- Billing / quota accounting
- Human review / correction workflow

## Acceptance criteria

1. Добавлен ASR endpoint для одного аудиофайла, например `POST /v1/asr/transcribe`.
2. Endpoint принимает `multipart/form-data` с одним audio file.
3. Поддерживается Cloud.ru provider с моделью по умолчанию `openai/whisper-large-v3`.
4. Cloud.ru base URL, API key, model, timeout и max file size задаются через env.
5. Перед реализацией/финализацией клиента зафиксирован фактический Cloud.ru ASR API contract: endpoint, auth, request format, response format.
6. ASR client возвращает typed internal result: transcript text, provider, model, latency/status metadata.
7. Ошибки Cloud.ru нормализованы в контролируемые platform errors: timeout, auth error, unsupported media, file too large, upstream unavailable, bad upstream response.
8. Raw audio не сохраняется платформой.
9. Raw audio и transcript не логируются по умолчанию.
10. Логи содержат только safe metadata: request_id/trace_id, provider, model, status, latency_ms, file_size_bucket, error_type.
11. Реальный Cloud.ru вызов не требуется для unit tests; Cloud.ru мокается.
12. Добавлены endpoint tests: success, timeout, invalid file type, file too large, upstream error.
13. Добавлен privacy test: логи не содержат transcript/raw audio/user text.
14. Существующий `/decide`, RouterV2, Assist Mode и Partial Trust не меняют поведение.
15. Обновлена integration/dev документация: env, локальный запуск, mock-тесты, manual UAT smoke.
16. Добавлен ADR или planning note по ASR MVP Capability и его границам.
17. Codex pipeline проходит полный цикл: PLAN → APPLY phases → tests/docs → hardening summary.

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Cloud.ru ASR endpoint/format отличается от OpenAI Audio API | High | Phase 0 API contract discovery; endpoint/base URL configurable; не хардкодить неподтверждённый контракт |
| Утечка transcript/audio в логи | High | Privacy-safe logger, запрет raw fields, отдельный privacy test |
| Большие файлы перегружают API/platform | Medium | `ASR_MAX_FILE_SIZE_MB`, content-length validation, controlled 413 |
| Cloud.ru latency ухудшает UX | Medium | timeout config, structured timeout error, no retry loop in MVP |
| ASR начнут использовать как скрытый вход в RouterV2 | Medium | Явно out of scope; endpoint только возвращает text |
| Реальные Cloud.ru тесты нестабильны в CI | Low | Unit tests через mock; real API только manual smoke/UAT |
| Неверная модель/профиль Cloud.ru в env | Medium | readiness/manual smoke docs, clear config errors |

## Dependencies

- Cloud.ru Foundation Models API access
- Cloud.ru API key/service account for Foundation Models
- Model availability: `openai/whisper-large-v3`
- Existing API framework in AI Platform
- Existing logging conventions
- Existing test framework / pytest setup
- ADR-001 contract compatibility policy
- Current Codex development rules: `CODEX.md`, `AGENTS.md`, `skills/`
