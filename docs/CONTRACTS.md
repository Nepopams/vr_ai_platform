# Contracts

This document describes the JSON payload formats for HomeTask commands and decisions.

## Schema Versioning

The current contract schema version is tracked in [`contracts/VERSION`](../contracts/VERSION). Update this file whenever the JSON schemas change so downstream tooling can detect schema bumps.

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
