# Codex PLAN — ST-053 Contract Posture

## Mode

Read-only PLAN. Do not edit files, install packages, mutate runtime state, commit, or touch HomeTusk files.

## Sources

- `docs/planning/workpacks/ST-053/workpack.md`
- `docs/planning/epics/EP-017/stories/ST-053-contract-posture.md`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.md`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md`
- `contracts/schemas/decision.schema.json`
- `contracts/schemas/command.schema.json`
- `contracts/VERSION`
- `docs/adr/ADR-001-contract-versioning-compatibility-policy.md`
- `docs/adr/ADR-009-domain-planner-v1-narrow-corridor.md`
- HomeTusk read-only source: `C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/provider-domain-planner-v1-acceptance/reject-confirm-answer-contract-posture.md`

## Required Findings

- Confirm current provider schema support for `reject`, `confirm`, `answer`, and repeated shopping actions.
- Confirm HomeTusk posture for each outcome.
- Confirm whether ST-053 itself requires schema/runtime changes.
- Confirm ST-054 minimum scope and stop conditions.

## Stop Conditions

- Need to edit `contracts/**`, `contracts/schemas/**`, `contracts/VERSION`, runtime planner files, public API, or HomeTusk files.
- Need to add `answer` without HomeTusk answer/read-model governance.
- Need to infer product semantics not present in sources.
