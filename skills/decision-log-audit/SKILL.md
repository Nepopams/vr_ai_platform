# Decision Log Audit Skill

## Expected log format

Decision logs are stored as JSONL where each line is a single JSON object with two top-level keys:

- `decision`: The decision payload that must validate against `contracts/schemas/decision.schema.json`.
- `metadata`: Required runtime metadata used for auditing and traceability.

### Required metadata fields

| Field | Type | Description |
| --- | --- | --- |
| `command_id` | string | Identifier for the command that produced the decision. Must match `decision.command_id`. |
| `trace_id` | string | Distributed tracing identifier for the decision run. |
| `prompt_version` | string | Prompt version used for the decision. Must match `decision.reasoning_log.prompt_version`. |
| `schema_version` | string | Decision schema or pipeline version. Must match `decision.version`. |
| `latency_ms` | integer | End-to-end latency in milliseconds. |

### Example entry

```json
{
  "decision": {
    "decision_id": "dec-123",
    "command_id": "cmd-001",
    "status": "accepted",
    "actions": [
      {"type": "plan", "description": "Provide a mock weekly chores plan."}
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
    "created_at": "2024-01-01T00:00:00Z",
    "version": "v0"
  },
  "metadata": {
    "command_id": "cmd-001",
    "trace_id": "trace-123",
    "prompt_version": "prompt-v0",
    "schema_version": "v0",
    "latency_ms": 185
  }
}
```
