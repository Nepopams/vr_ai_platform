# ADR-001: Contract versioning & compatibility policy (CommandDTO/DecisionDTO)

- Status: Accepted
- Date: 2026-01-12
- Owners: Platform Team (Codex) + Product Team (Claude)
- Scope: AI Platform ↔ HomeTask (и будущие продукты)
- Goal: зафиксировать правила изменения контрактов так, чтобы команды могли развиваться параллельно без “сломали прод”.

## 1) Контекст и проблема

Контракт (CommandDTO/DecisionDTO) — единственный стабильный интерфейс между продуктом и AI-платформой. Контракты будут эволюционировать: появятся новые интенты, новые поля контекста, новые типы действий, версии промптов и т.п.

Без чёткой политики версионирования получаем:

- неожиданные breaking изменения,
- невозможность воспроизвести поведение по trace,
- хаос в документации и тестах.

## 2) Решение (Decision)

Мы принимаем contract-first подход и семантическое версионирование (semver) для контрактов.

Версии:

- MAJOR.MINOR.PATCH

Хранение версии: contracts/VERSION (source of truth)

В каждом DecisionDTO возвращаем:

- schema_version (из contracts/VERSION)
- decision_version (версия пайплайна/промптов, отдельно от schema)

Принцип совместимости:

- MINOR/PATCH изменения должны быть backward compatible для потребителей текущей major-версии.
- MAJOR — допускает breaking изменения, требует периода миграции.

## 3) Определения: что считается breaking / non-breaking

### 3.1 Non-breaking (разрешено в MINOR/PATCH)

- Добавление необязательного поля (optional) в CommandDTO или DecisionDTO
- Добавление нового значения в “расширяемые” enums/union при соблюдении правил обработки неизвестного (см. ниже)
- Добавление нового типа action если продукт обязан обрабатывать unknown actions безопасно (fallback)
- Расширение объекта context новыми optional подсекциями
- Добавление новых metadata полей (trace, latency_ms, prompt_version) как optional

### 3.2 Breaking (требует MAJOR)

- Удаление поля
- Переименование поля
- Изменение типа поля (string → object, number → string, и т.п.)
- Изменение семантики поля так, что старый потребитель будет работать неверно
- Перевод optional → required
- Сужение допустимых значений (например, раньше принимали любой string, теперь enum)

## 4) Правила обработки неизвестного (ключ к non-breaking расширениям)

Чтобы мы могли добавлять новые action/интенты без постоянных major-версий, фиксируем обязательное поведение:

HomeTask (consumer) обязан:

- Если DecisionDTO.action неизвестен:
  - не выполнять ничего, логировать событие, показать пользователю нейтральное сообщение, и/или запросить clarify через повторный вызов, если предусмотрено.
- Если DecisionDTO.payload содержит неизвестные поля:
  - игнорировать их.
- Если в CommandDTO.context есть неизвестные поля:
  - AI Platform обязана игнорировать их.

AI Platform обязана:

- Не полагаться на поля, которых нет в CommandDTO (всё optional может отсутствовать)
- Не считать отсутствие нового поля ошибкой, пока оно не required в major версии

Это делает расширение контрактов безопасным.

## 5) Версионирование endpoint/API

Для MVP достаточно одного endpoint POST /decide.

Но политика на будущее фиксируется:

- Major версия отражается либо в URL (/v1/decide), либо в заголовке (X-Contract-Version: 1), либо оба.

В MVP можно оставить один путь, но major должен быть явно различим на уровне маршрутизации, чтобы можно было держать /v1 и /v2 параллельно при миграции.

## 6) Миграция и депрекейшн

При breaking изменениях:

- Выпускаем vNext (MAJOR+1) параллельно
- Поддерживаем N недель/релизов dual-run (конкретику определим позже)
- В DecisionDTO добавляем deprecations (опционально) с перечнем полей/действий, уходящих в будущем
- Документация в docs/CONTRACTS.md ведётся по версиям (v1, v2…)

## 7) CI gates (как не допускать “сломали контракт”)

Любой PR, меняющий contracts/, обязан пройти:

- validate_contracts (fixtures against schemas)
- schema diff check:
  - Если изменились required поля / типы / удаление — блокируем MINOR/PATCH и требуем MAJOR
- graph_sanity (пайплайн выдаёт DecisionDTO валидный по новой схеме)
- Обновление docs/CONTRACTS.md и CHANGELOG.md (если менялся контракт)

## 8) Правило фикстур и примеров

Fixtures в репозитории — это “контрактные примеры” и они версионируются вместе со схемой.

Для каждой major версии есть набор fixtures минимум:

- valid_command_*
- valid_decision_*
- несколько invalid_* для negative tests

## 9) Consequences

Плюсы

- параллельная разработка без сюрпризов
- стабильная интеграция и воспроизводимость по trace
- расширяемость без бесконечных major

Минусы

- дисциплина: обновлять docs и fixtures
- нужно строго придерживаться “unknown action/payload safe handling”

## 10) Decision / Acceptance Criteria

ADR-001 считается принятым, если согласовано:

- semver для контрактов (contracts/VERSION + schema_version в решениях)
- список breaking/non-breaking правил
- правило обработки неизвестного для action и полей
- CI gates на изменения контрактов

## Links

- MVP v1: `docs/mvp/AI_PLATFORM_MVP_v1.md`
- Diagrams index: `docs/diagrams/README.md`
