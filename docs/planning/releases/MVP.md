# MVP — AI Platform v1

## Hypothesis

Если AI Platform будет:
- строго контрактной,
- детерминированной по умолчанию,
- и будет использовать LLM только под контролем,

то она сможет:
- улучшить понимание пользовательских команд,
- снизить число clarify-итераций,
- не сломать UX и безопасность продукта.

## In Scope (MVP)

### Functional

- Приём текстовой команды (CommandDTO)
- Intent detection (deterministic + assisted)
- Entity extraction (shopping / basic tasks)
- Clarify vs start_job decisioning
- Shadow LLM Router
- LLM Assist Mode (normalization, entities, clarify)
- Partial Trust для **одного** интента

### Non-functional

- Contract compatibility
- Zero-impact fallback
- Observability (logs, trace_id)
- Feature-flag driven rollout

## Out of Scope (Explicit)

- Исполнение задач
- Пользовательская память
- Автономные агенты
- Свободное планирование без правил
- UI-логика диалогов

## Exit criteria

### Must-have

1. Платформа не ломает HomeTusk при любых LLM-ошибках
2. LLM-интеграции полностью отключаемы флагами
3. Все решения трассируемы
4. Контракты стабильны

### Quality signals

- ↓ среднее число clarify
- ↑ доля `start_job`
- Нет роста p95 latency
