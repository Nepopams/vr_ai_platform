# AI Platform MVP v1

Статус: Accepted

Документ фиксирует минимальный, строго ограниченный объём MVP v1 для AI Platform. Любые изменения вне этого объёма требуют либо отдельного ADR (Draft), либо явного документа "MVP v2" с последующим соблюдением ADR-001.

## Ссылки на ADR

- ADR-000: AI Platform — Contract-first Intent → Decision Engine (LangGraph)
- ADR-001: Contract versioning & compatibility policy (CommandDTO/DecisionDTO)

## Scope MVP v1

### Intents

- `create_task`
- `add_shopping_item`
- `clarify_needed`

### Actions

- `start_job`
- `propose_create_task`
- `propose_add_shopping_item`
- `clarify`

### Default behavior

- Для доменных изменений (создание задач и добавление покупок) возвращать `start_job` и, если возможно, прикладывать `proposed_actions`.
- В остальных случаях — `clarify`.

## Обязательные поля (CommandDTO v1)

- `command_id` (string)
- `user_id` (string)
- `timestamp` (ISO-8601 string)
- `text` (string)
- `capabilities` (string[], whitelist действий)
- `context` (object)

### Context v1

Минимально обязательное:

- `context.household.members[]` (минимум `user_id`, `display_name` опционально)

Опционально:

- `context.household.household_id`
- `context.household.zones[]` (`zone_id`, `name`)
- `context.household.shopping_lists[]` (`list_id`, `name`)
- `context.defaults` (`default_assignee_id`, `default_list_id`)
- `context.policies` (`quiet_hours`, `max_open_tasks_per_user`)

## Обязательные поля (DecisionDTO v1)

- `decision_id` (string)
- `command_id` (string)
- `status` (`ok` | `clarify` | `error`)
- `action` (строка из MVP v1)
- `confidence` (number 0..1)
- `payload` (object)
- `explanation` (string)
- `trace_id` (string)
- `schema_version` (string = `contracts/VERSION`)
- `decision_version` (string)
- `created_at` (ISO-8601 string)

## Payload правила

### `start_job`

- `job_id` (string)
- `job_type` (`create_task` | `add_shopping_item` | `unknown`)
- `proposed_actions` (опц.) — список проектируемых действий
- `ui_message` (опц.)

### `propose_create_task`

- `task`:
  - `title` (string)
  - `description` (опц.)
  - `assignee_id` (опц.)
  - `zone_id` (опц.)
  - `due` (опц.)
- `idempotency_key` (опц.)
- `job_hint` (опц.)

### `propose_add_shopping_item`

- `item`:
  - `name` (string)
  - `quantity` (опц.)
  - `unit` (опц.)
  - `list_id` (опц.)
- `idempotency_key` (опц.)

### `clarify`

- `question` (string)
- `options` (опц.)
- `missing_fields` (опц.)
- `job_id` (опц.)

## Acceptance Criteria MVP v1

- Команды классифицируются на `create_task`, `add_shopping_item` или `clarify_needed` на фикстурах.
- Для каждого входного примера возвращается либо:
  - `start_job` + `proposed_actions`,
  - либо `clarify` с понятным вопросом.
- Все решения валидируются JSON Schema.
- В каждом ответе присутствуют `trace_id`, `schema_version`, `decision_version`.
- Проверки `make validate_contracts`, `make graph-sanity`, `make release-sanity` должны быть зелёными.
