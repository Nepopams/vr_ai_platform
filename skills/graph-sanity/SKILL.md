# Graph Sanity Skill

## Inputs
- Command fixtures (default: `skills/contract-checker/fixtures/valid_command_create_task.json`).
- Core graph pipeline.

## Outputs
- Decision payloads validated against the decision schema.

## Steps
1. Load command fixtures.
2. Run each command through the core graph.
3. Validate generated decisions against the decision schema.
4. Report any failures.

## Definition of Done (DoD)
- All command fixtures execute through the core graph.
- Each decision validates against the decision schema.
- Script exits with non-zero status if any command fails.
