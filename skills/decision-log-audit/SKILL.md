# Decision Log Audit Skill

## Expected log format

Decision logs are stored as JSONL where each line is a single DecisionDTO JSON object validated against `contracts/schemas/decision.schema.json`.

### Example entry

```json
{
  "decision_id": "dec-123",
  "command_id": "cmd-001",
  "status": "ok",
  "action": "start_job",
  "confidence": 0.71,
  "payload": {
    "job_id": "job-001",
    "job_type": "add_shopping_item",
    "proposed_actions": [
      {
        "action": "propose_add_shopping_item",
        "payload": {
          "item": {
            "name": "молоко",
            "list_id": "list-1"
          }
        }
      }
    ]
  },
  "explanation": "Распознан запрос на добавление покупки.",
  "trace_id": "trace-123",
  "schema_version": "2.0.0",
  "decision_version": "mvp1-mock-0.1",
  "created_at": "2024-01-01T00:00:00Z"
}
```
