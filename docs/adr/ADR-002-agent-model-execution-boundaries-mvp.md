# ADR-002: Agent model & execution boundaries (MVP)

- Status: Accepted
- Date: 2026-01-12
- Owners: Platform Team (Codex) + Product Team (Claude)
- Scope: AI Platform MVP (LangGraph), HomeTask MVP интеграция

## 1) Контекст и проблема

В MVP платформа уже реализует минимальный decisioning-пайплайн (router + propose_* + clarify + start_job) и должна оставаться stateless. При этом команда планирует дальнейшее развитие (включая file-based registry агентов и реальные executors), не меняя текущего поведения.

Нужна явная фиксация «агентной модели» MVP как источника правды для разработки и расширений, чтобы:

- не ломать поведение MVP;
- сохранить контрактные гарантии (ADR-001);
- избежать скрытых side-effects и “магических” агентов;
- обеспечить воспроизводимость через trace/decision версии.

## 2) Решение (Decision)

Мы фиксируем агентную модель MVP и границы исполнения. В MVP все агенты являются **моками** (decision-time) и не выполняют реальных доменных действий. Реальный execution остаётся на стороне продукта HomeTask.

### 2.1 MVP агенты (5) и их роли

#### A) Decision/Router (реальный)

**Responsibilities**
- Классифицировать intent (`create_task`, `add_shopping_item`, `clarify_needed`).
- Определять ветку пайплайна (clarify или start_job с propose_*).
- Соблюдать whitelist capabilities и unknown-handling (ADR-001).

**Non-responsibilities**
- Не выполняет доменные действия.
- Не пишет в БД, не вызывает внешние сервисы.
- Не ведёт state между вызовами.

#### B) ShoppingList executor (мок через `propose_add_shopping_item`)

**Responsibilities**
- Формировать `propose_add_shopping_item` payload в рамках DecisionDTO.
- Нормализовать поля item (name/quantity/unit/list_id) в пределах контракта.

**Non-responsibilities**
- Не добавляет покупки в реальные списки.
- Не выполняет внешние вызовы.

#### C) Task executor (мок через `propose_create_task`)

**Responsibilities**
- Формировать `propose_create_task` payload в рамках DecisionDTO.
- Заполнять минимально возможные поля задачи (title/assignee_id/zone_id/due).

**Non-responsibilities**
- Не создаёт реальные задачи.
- Не изменяет доменную модель.

#### D) Clarifier (ветка `clarify`)

**Responsibilities**
- Формировать `clarify` payload (question/options/missing_fields) при недостатке данных.
- Возвращать status=`clarify` и обоснование.

**Non-responsibilities**
- Не ведёт multi-turn диалоги.
- Не хранит историю и контекст между вызовами.

#### E) Job manager (мок `start_job`)

**Responsibilities**
- Формировать `start_job` payload (job_id, job_type, proposed_actions, ui_message).
- Обеспечивать short-path ответ (SLA в секундах).

**Non-responsibilities**
- Не выполняет jobs.
- Не управляет прогрессом и уведомлениями.

### 2.2 Operational model

- Каждое решение должно содержать `trace_id`, `decision_version`, `schema_version`.
- `schema_version` берётся из `contracts/VERSION`.
- Поведение MVP детерминировано (mock mode) и не зависит от внешних сервисов.
- Версии агентов должны фиксироваться в reasoning/trace (подготовка к registry).

### 2.3 Contract implications (что нельзя менять без ADR + версии)

Без нового ADR и semver-bump (ADR-001) **нельзя**:

- менять список intents/actions MVP;
- менять обязательные поля CommandDTO/DecisionDTO;
- менять смысл `start_job`, `propose_*`, `clarify` payload;
- изменять правила unknown-handling и требования к `schema_version`/`decision_version`.

Источник правды: `docs/mvp/AI_PLATFORM_MVP_v1.md` и `contracts/VERSION`.

### 2.4 Non-goals (MVP)

- Любые реальные side-effects (DB writes, доменные мутации).
- Внешние интеграции и LLM-вызовы.
- Multi-turn диалоги и хранение состояния.
- Асинхронное исполнение внутри платформы.

## 3) Consequences

Плюсы:

- Ясные границы ответственности агентов и отсутствие “скрытого” выполнения.
- Стабильность контрактов и воспроизводимость решений.
- Готовность к будущему file-based registry без изменения текущего поведения.

Минусы:

- Ограниченная «интеллектуальность» MVP и отсутствие реального исполнения.
- Нужна дисциплина обновления ADR/диаграмм при расширении.

## Links

- ADR-000: `docs/adr/ADR-000-ai-platform-intent-decision-engine.md`
- ADR-001: `docs/adr/ADR-001-contract-versioning-compatibility-policy.md`
- MVP v1: `docs/mvp/AI_PLATFORM_MVP_v1.md`
- Diagrams index: `docs/diagrams/README.md`
- Integration docs: `docs/integration/`
