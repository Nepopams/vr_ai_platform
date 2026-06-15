# Codex PLAN — ST-054 Reject / Confirm Contract Schema

## Mode

Read-only PLAN. Do not edit files, install packages, mutate runtime state, commit, or touch HomeTusk files.

## Sources

- `docs/planning/workpacks/ST-054/workpack.md`
- `docs/planning/epics/EP-017/stories/ST-054-reject-confirm-contract-schema.md`
- `docs/planning/epics/EP-017/domain-planner-v1-contract-posture.md`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md`
- `contracts/schemas/decision.schema.json`
- `contracts/schemas/command.schema.json`
- `contracts/schemas/.baseline/*.schema.json`
- `contracts/VERSION`
- `skills/contract-checker/fixtures/`
- `app/models/api_models.py`
- `docs/CONTRACTS.md`
- `docs/adr/ADR-001-contract-versioning-compatibility-policy.md`
- `docs/adr/ADR-009-domain-planner-v1-narrow-corridor.md`

## Required Findings

- Confirm exact schema edits.
- Confirm semver decision.
- Confirm fixture and test updates.
- Confirm validation commands.
- Confirm forbidden runtime/HomeTusk paths stay untouched.

## Stop Conditions

- Need to change `status` enum.
- Need to add provider `answer`.
- Need to change runtime planner behavior.
- Need to edit HomeTusk files.
