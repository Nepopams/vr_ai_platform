# ADR-000: AI Platform — Contract-first Intent → Decision Engine (LangGraph)

- Status: Accepted
- Date: 2026-01-12
- Owners: Platform Team (Codex) + Product Team (Claude)
- Consumer: HomeTask MVP (домашние задачи/покупки, NL-интерфейс)

## 1) Контекст и проблема

Нужно разделить ответственность между продуктом HomeTask и AI-платформой так, чтобы:

- команды могли развиваться параллельно;
- ИИ был предсказуемым, управляемым и трассируемым;
- UX не превращался в “ответ через полчаса” из-за долгих агентных действий.

## 2) Решение (Decision)

Мы принимаем архитектурный принцип:

AI Platform = stateless decision engine, который:

1. принимает CommandDTO (текст команды + контекст + capabilities)
2. возвращает DecisionDTO (action + payload + confidence + explanation + trace_id)
3. не хранит и не мутирует продуктовые сущности напрямую
4. логирует reasoning/trace и версии (schema_version / prompt_version / model_id)
5. оркестрируется через LangGraph (узлы/агенты как компоненты pipeline)

### 2.1 Границы ответственности

AI Platform:

- intent extraction / классификация интентов
- нормализация времени/сущностей в пределах DTO
- выбор действия из whitelist capabilities
- формирование DecisionDTO
- schema validation входов/выходов
- трассировка + аудит (decision logs)

HomeTask:

- доменные правила и авторизация (membership, права, лимиты, политики)
- финальная доменная валидация и исполнение (ActionExecutor)
- хранение состояния/событий (TaskActivity и т.п.)
- UX и диалоги, включая clarify-loop

Политика: ИИ предлагает — продукт решает и исполняет.

### 2.2 Двухфазная реакция (Short/Long Path Execution)

Платформа обязана поддерживать двухфазное поведение:

- Short-path: платформа быстро возвращает подтверждение и запуск выполнения:
  - action = start_job (или ack)
  - минимальный payload для job (job_id, job_type, trace_id, опц. ui_message)
  - ответ в рамках интерактивного SLA (секунды)
- Long-path: дальнейшие действия выполняются асинхронно.

В MVP исполнителем job является продукт HomeTask, который применяет доменные действия, управляет прогрессом и уведомлениями. Платформа остаётся stateless относительно домена.

### 2.3 Протокол интеграции

- Контрактный метод: POST /decide (или эквивалент)
- Вход: CommandDTO (JSON Schema)
- Выход: DecisionDTO (JSON Schema)
- Любой вход/выход валидируется схемой.

### 2.4 Оркестрация в LangGraph (концепт)

MVP-граф:

1. Validator — schema validation + trace_id
2. Planner — intent + сущности (NL → structured)
3. Decider — action/payload + confidence
4. Clarifier — если низкая уверенность → action=clarify
5. Finalize — сбор DecisionDTO + reasoning log

## 3) Non-goals

- “универсальный ассистент” и покрытие всех бытовых сценариев
- прямой доступ платформы к БД продукта
- обучение/finetune в MVP
- сложная мультитенантность/marketplace инструментов на старте
- выполнение долгих операций внутри платформы в MVP (допускается позже)

## 4) MVP-объём платформы (пересечение с MVP HomeTask)

Платформа MVP поддерживает:

- интенты: create_task, add_shopping_item, create_list (опц.), clarify
- консервативный decisioning: при неуверенности → clarify, не “догадываться”
- start_job/ack как стандартный short-path для долгих действий
- 100% трассируемость: command_id ↔ trace_id ↔ decision_id/job_id
- contract-tests + graph-sanity + decision-log audit + release-sanity

## 5) Consequences

Плюсы

- команды независимы (контракт = handshake)
- быстрый UX (ack сразу) без ожидания долгих агентов
- управляемость качества (schema + logs + версии)
- переиспользуемость на другие продукты

Минусы

- продукт обязан готовить качественный контекст (DTO projection)
- требуется дисциплина версионирования контрактов
- часть “магии” будет появляться итеративно

## 6) Альтернативы (отклонены)

1. встроить ИИ внутрь продукта — теряем платформенность/параллельность
2. дать платформе право мутировать домен — ломаем безопасность/инварианты
3. сразу marketplace агентов — тонем до MVP

## 7) Риски и контроль

- расползание ответственности → capabilities whitelist + product-side validator
- “плавающие” контракты → semver + schema diff + CI gates
- потеря доверия → clarify по умолчанию + conservative decisions
- “job hell” → TTL, лимиты шагов, идемпотентность

## 8) Operational rules

- contracts/ = source of truth; изменения через PR + semver bump
- релизный гейт: validate_contracts, graph_sanity, decision_log_audit, release_sanity
- интерактивный SLA для short-path: ответ ≤ N секунд (фиксируем позже, ориентир 2–5s)

## 9) Acceptance Criteria

- границы platform vs product зафиксированы
- short/long path утверждён и не ломает stateless-принцип
- контрактный протокол и MVP-объём согласованы
- LangGraph принят как базовый механизм оркестрации

## Links

- MVP v1: `docs/mvp/AI_PLATFORM_MVP_v1.md`
- Diagrams index: `docs/diagrams/README.md`
