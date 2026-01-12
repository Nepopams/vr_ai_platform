# Contracts

Документ описывает форматы JSON для команд (CommandDTO) и решений (DecisionDTO) HomeTask AI Platform.

## Версионирование схем

Текущая версия схемы контрактов хранится в [`contracts/VERSION`](../contracts/VERSION). Любые изменения схем должны сопровождаться корректным semver-бампом согласно ADR-001.
DecisionDTO всегда содержит `schema_version`, равный значению `contracts/VERSION`.

## MVP v1

### Intents

- `create_task`
- `add_shopping_item`
- `clarify_needed`

### Actions

- `start_job`
- `propose_create_task`
- `propose_add_shopping_item`
- `clarify`

### Примечание о совместимости

Если продукт получает неизвестный `action`, он обязан обработать его безопасно (например, игнорировать или переводить в `clarify`) согласно ADR-001.

## CommandDTO

**Schema:** `contracts/schemas/command.schema.json`

### Поля

- `command_id` (string, required)
- `user_id` (string, required)
- `timestamp` (string, date-time, required)
- `text` (string, required)
- `capabilities` (string[], required) — whitelist действий
- `context` (object, required)
  - `context.household.members[]` (required)
  - `context.household.zones[]` (optional)
  - `context.household.shopping_lists[]` (optional)
  - `context.defaults` (optional)
  - `context.policies` (optional)

### Пример

```json
{
  "command_id": "cmd-001",
  "user_id": "user-123",
  "timestamp": "2024-01-01T12:00:00Z",
  "text": "Добавь молоко в список покупок",
  "capabilities": [
    "start_job",
    "propose_create_task",
    "propose_add_shopping_item",
    "clarify"
  ],
  "context": {
    "household": {
      "household_id": "house-1",
      "members": [
        {"user_id": "user-123", "display_name": "Аня"}
      ],
      "shopping_lists": [
        {"list_id": "list-1", "name": "Продукты"}
      ]
    }
  }
}
```

## DecisionDTO

**Schema:** `contracts/schemas/decision.schema.json`

### Поля

- `decision_id` (string, required)
- `command_id` (string, required)
- `status` (`ok` | `clarify` | `error`, required)
- `action` (string, required)
- `confidence` (number 0..1, required)
- `payload` (object, required)
- `explanation` (string, required)
- `trace_id` (string, required)
- `schema_version` (string, required)
- `decision_version` (string, required)
- `created_at` (string, date-time, required)

### Пример: `start_job` + `proposed_actions`

```json
{
  "decision_id": "dec-123",
  "command_id": "cmd-001",
  "status": "ok",
  "action": "start_job",
  "confidence": 0.72,
  "payload": {
    "job_id": "job-001",
    "job_type": "add_shopping_item",
    "proposed_actions": [
      {
        "action": "propose_add_shopping_item",
        "payload": {
          "item": {
            "name": "молоко",
            "quantity": "2",
            "unit": "л",
            "list_id": "list-1"
          },
          "idempotency_key": "cmd-001:item:milk"
        }
      }
    ],
    "ui_message": "Понял, запускаю выполнение."
  },
  "explanation": "Распознан запрос на добавление покупки.",
  "trace_id": "trace-001",
  "schema_version": "2.0.0",
  "decision_version": "mvp1-mock-0.1",
  "created_at": "2024-01-01T12:00:05Z"
}
```
