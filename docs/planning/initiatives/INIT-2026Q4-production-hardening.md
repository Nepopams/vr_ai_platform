# INIT-2026Q4-production-hardening — Production Hardening: LLM, метрики, качество

**Приоритет:** Высокий
**Период:** 2026Q4
**Статус:** Proposed
**Owner:** TBD

## Контекст

MVP платформы построен: контрактная архитектура, детерминистический пайплайн,
shadow/assist LLM-слой (scaffolding), partial trust (1 intent), agent registry,
CI governance. 19 историй, 228 тестов, 8 инициатив закрыты.

Однако LLM-интеграция работает на заглушках — реальные вызовы не проверены в бою.
Нет автоматизированной оценки качества (golden dataset). Нет мониторинга latency.
Для выхода в прод нужно закрыть эти пробелы.

## Цель

Подготовить платформу к реальной эксплуатации с живым LLM:
- Реальные LLM-вызовы через shadow/assist с замерами
- Автоматизированная оценка качества на golden dataset
- Метрики latency и quality как CI/observability артефакты

## Scope

### 1. Real LLM integration
- Подключение реального LLM-клиента (Yandex GPT / OpenAI-compatible) в shadow router
- Конфигурация через env vars (модель, endpoint, timeout)
- Retain: deterministic fallback на любую ошибку/таймаут
- Retain: feature flag kill-switch

### 2. Golden dataset и quality metrics
- Формализация golden dataset (набор команд → ожидаемые intent/entities/action)
- Скрипт оценки: прогон команд через pipeline, сравнение с golden answers
- Метрики: intent accuracy, entity precision/recall, clarify rate
- CI-интеграция (optional gate или report)

### 3. Latency observability
- Замеры p50/p95/p99 latency на каждом шаге pipeline (normalize, shadow, assist, core, partial trust)
- Structured logging с latency breakdown
- Baseline latency без LLM vs с LLM

### 4. Error budget и fallback metrics
- Подсчёт: сколько раз LLM fallback сработал vs LLM ответил успешно
- Risk log: accepted_llm / fallback / error + причина (расширение partial trust логики)
- Dashboard-ready формат (JSONL или structured log)

## Out of scope

- Второй consumer (отдельная инициатива)
- Новые интенты / домены
- Расширение partial trust на другие интенты (может быть следующей инициативой)
- Agent invocation из core pipeline (Phase 2 — отдельно)
- UI/UX
- Персональные профили / долгая память
- Автоматический retrain / fine-tuning

## Acceptance criteria

1. Shadow router вызывает реальный LLM (под флагом), fallback работает при ошибке/таймауте
2. Golden dataset из ≥20 команд с ожидаемыми ответами; скрипт оценки выдаёт intent accuracy ≥ baseline
3. Latency breakdown логируется для каждого шага pipeline
4. Fallback rate измерим и логируется в structured формате
5. Все существующие 228 тестов проходят; новые тесты для LLM integration (mocked)
6. Документация: как запустить с реальным LLM, как прогнать golden dataset

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM API нестабилен / медленный | Medium | Timeout + fallback + kill-switch (уже есть scaffolding) |
| Golden dataset субъективен | Low | Начать с очевидных кейсов, расширять итеративно |
| Latency instrumentation замедляет pipeline | Low | Lightweight structured logging, no external deps |
| Secrets management для LLM API keys | Medium | env vars only, .env в .gitignore, CI secrets |

## Dependencies

- Shadow router scaffolding (INIT-2026Q1-shadow-router) — Done
- Assist mode scaffolding (INIT-2026Q1-assist-mode) — Done
- Partial trust (INIT-2026Q2-partial-trust) — Done
- CI governance (INIT-2026Q3-semver-and-ci) — Done

## Deliverables

- Рабочий LLM-клиент в shadow router (flag-gated)
- Golden dataset + evaluation script
- Latency breakdown logging
- Fallback/error metrics logging
- Документация по запуску и оценке
