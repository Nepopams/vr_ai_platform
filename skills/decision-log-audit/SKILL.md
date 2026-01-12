# Decision Log Audit Skill

## Inputs
- JSONL decision log file.
- Decision schema in `contracts/schemas/decision.schema.json`.

## Outputs
- Validation report and exit status.

## Steps
1. Read each JSONL line into a decision payload.
2. Validate the payload against the decision schema.
3. Report malformed JSON or schema violations.

## Definition of Done (DoD)
- All lines in the log file parse as JSON.
- Each entry validates against the decision schema.
- Script exits with non-zero status when issues are found.
