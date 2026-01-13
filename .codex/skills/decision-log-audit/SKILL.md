---
name: decision-log-audit
description: Audits Decision JSONL logs for schema compliance, required metadata, and invariants across recorded decisions.
---

# Decision Log Audit Skill

## Purpose
Validates runtime decision logs produced by the Decision API to ensure every recorded decision
conforms to DecisionDTO schema and platform invariants.

## Inputs
- Decision log files in `logs/decision.log.jsonl` (or configured path).
- Decision JSON Schema in `contracts/schemas/decision.schema.json`.

## Outputs
- Audit report printed to stdout.
- Non-zero exit code when violations are detected.

## Checks
- JSON Schema validity for each DecisionDTO entry.
- Presence of required metadata (trace_id, decision_id, schema_version, decision_version).
- Append-only log semantics (no malformed entries).

## Definition of Done (DoD)
- All log entries validate against the schema.
- No missing required fields.
- Script exits with status 0 when logs are valid.

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
