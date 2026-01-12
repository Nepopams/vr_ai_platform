# Contracts

This document describes the JSON payload formats for HomeTask commands and decisions.

## Schema Versioning

The current contract schema version is tracked in [`contracts/VERSION`](../contracts/VERSION). Update this file whenever the JSON schemas change so downstream tooling can detect schema bumps.
DecisionDTO must expose `schema_version` equal to `contracts/VERSION`, and contract extensions must remain non-breaking within a MAJOR version.

## Command Payload

**Schema:** `contracts/schemas/command.schema.json`

### Fields

- `command_id` (string, required): Unique ID for the command.
- `user_id` (string, required): Unique ID for the user.
- `timestamp` (string, date-time, required): ISO-8601 timestamp for when the command was issued.
- `task` (object, required): Task details.
  - `title` (string, required): Short task title.
  - `description` (string, required): Full task description.
  - `priority` (string, required): One of `low`, `medium`, or `high`.
- `context` (object, optional): Additional metadata for the command.

### Example

```json
{
  "command_id": "cmd-001",
  "user_id": "user-123",
  "timestamp": "2024-01-01T12:00:00Z",
  "task": {
    "title": "Plan weekly chores",
    "description": "Generate a mock plan for household chores.",
    "priority": "medium"
  },
  "context": {
    "locale": "en-US"
  }
}
```

## Decision Payload

**Schema:** `contracts/schemas/decision.schema.json`

### Fields

- `decision_id` (string, required): Unique ID for the decision.
- `command_id` (string, required): Reference to the originating command.
- `status` (string, required): `accepted`, `rejected`, or `needs_input`.
- `actions` (array, required): Actions produced by the pipeline.
  - `type` (string, required): Action type.
  - `description` (string, required): Action description.
- `reasoning_log` (object, required): Structured reasoning trace.
  - `command_id` (string, required): Command ID for trace linkage.
  - `steps` (array, required): Ordered list of reasoning steps.
  - `model_version` (string, required): Model version identifier.
  - `prompt_version` (string, required): Prompt version identifier.
- `created_at` (string, date-time, required): Decision creation timestamp.
- `version` (string, required): Decision schema or pipeline version.

### Example

```json
{
  "decision_id": "dec-123",
  "command_id": "cmd-001",
  "status": "accepted",
  "actions": [
    {
      "type": "plan",
      "description": "Provide a mock weekly chores plan."
    }
  ],
  "reasoning_log": {
    "command_id": "cmd-001",
    "steps": [
      "Validate command payload against schema.",
      "Simulate agent reasoning in mock mode.",
      "Assemble decision output and attach reasoning log."
    ],
    "model_version": "mock-model-0.1",
    "prompt_version": "prompt-v0"
  },
  "created_at": "2024-01-01T12:00:05Z",
  "version": "v0"
}
```

## Generated Examples

The examples below are generated from `skills/fixtures-generator/scripts/generate_fixtures.py`.

<!-- BEGIN GENERATED EXAMPLES -->
### create_task

Create a new household task.

```json
{
  "command_id": "cmd-create-001",
  "context": {
    "source": "mobile-app"
  },
  "task": {
    "description": "Book a plumber to fix the kitchen sink leak.",
    "priority": "high",
    "title": "Schedule plumber visit"
  },
  "timestamp": "2024-01-02T09:30:00Z",
  "user_id": "user-100"
}
```

### assign_task

Assign an existing task to a household member.

```json
{
  "command_id": "cmd-assign-002",
  "context": {
    "assignee": "Sam",
    "due_date": "2024-01-05"
  },
  "task": {
    "description": "Assign the recycling pickup to Sam.",
    "priority": "medium",
    "title": "Take out recycling"
  },
  "timestamp": "2024-01-02T09:30:00Z",
  "user_id": "user-101"
}
```

### add_shopping_item

Add an item to the shared shopping list.

```json
{
  "command_id": "cmd-shop-003",
  "context": {
    "list": "groceries",
    "quantity": "2 cartons"
  },
  "task": {
    "description": "Add oat milk to the grocery list for this week.",
    "priority": "low",
    "title": "Buy oat milk"
  },
  "timestamp": "2024-01-02T09:30:00Z",
  "user_id": "user-102"
}
```

### clarify

Ask a clarifying question for missing task details.

```json
{
  "command_id": "cmd-clarify-004",
  "context": {
    "needs_clarification": [
      "store list",
      "time window"
    ]
  },
  "task": {
    "description": "Need confirmation on which stores to visit.",
    "priority": "medium",
    "title": "Plan weekend errands"
  },
  "timestamp": "2024-01-02T09:30:00Z",
  "user_id": "user-103"
}
```
<!-- END GENERATED EXAMPLES -->
