# INIT-2026Q1-shadow-router — Shadow LLM-router и метрики

**Приоритет:** Высокий  
**Период:** 2026Q1  
**Статус:** Proposed  
**Owner:** TBD

## Контекст
Нужно безопасно измерять пользу LLM в роутинге/извлечении сущностей без влияния на продуктовые решения.
Цель — получить сравнение baseline vs LLM (shadow) и метрики качества на golden-dataset.

## Цель
- Добавить параллельный (shadow) LLM-вызов для каждого `CommandDTO`
- Собрать структурированный JSONL-лог для анализа качества/латентности/ошибок
- Не влиять на `DecisionDTO` и не менять публичные контракты

## Scope (входит)
- Введение структуры `RouterSuggestion` (внутренняя модель, не контракт)
- Shadow LLM-call в pipeline router на каждый запрос (под флагом)
- JSONL логирование:
  - `intent` (suggested)
  - `entities_summary` (без raw user text/LLM output)
  - `clarify_question` (summary/short form)
  - `latency_ms`
  - `error_type`
  - `trace_id` / `request_id`
- Скрипт анализа golden-dataset:
  - intent match rate
  - entity extraction hit rate (по summary/labels)
  - latency p50/p95
  - error breakdown

## Out of scope (не входит)
- Любое влияние на `DecisionDTO`
- Авто-исполнение задач
- Хранение raw текста пользователя или raw LLM output

## Acceptance criteria
1. Shadow режим выключен по умолчанию и включается флагом
2. При ошибке/таймауте LLM baseline работает как раньше
3. JSONL-лог не содержит raw user text и raw LLM output
4. Есть воспроизводимый скрипт анализа golden-dataset и README как запускать

## Метрики успеха
- Intent match rate (LLM vs baseline)
- Entity hit rate (по набору тест-кейсов)
- p95 latency и доля таймаутов
- Доля ошибок по типам

## Риски и контрмеры
- Рост латентности → строгий таймаут, асинхронный shadow, отключаемый флаг
- Утечка чувствительных данных в лог → только summaries/counters, audit

## Зависимости
- Наличие feature-flag механизма
- Golden dataset (минимальный набор кейсов)

## Deliverables
- `RouterSuggestion` (internal)
- Shadow call + JSONL logger
- Analyzer script + краткий гайд
