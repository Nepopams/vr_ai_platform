# Codex PLAN Prompt — ST-048 Provider Mapping Artifact Gate

You are in Codex PLAN for ST-048.

## Mode

Read-only only.

Do not edit, create, move, delete, format, install, commit, or mutate files. Do not change runtime, contracts, schemas, fixtures, tests, public API, or HomeTusk files.

## Objective

Prepare exact APPLY findings for the provider-side artifact gate before Domain Planner v1 runtime work.

## Required Sources

Read current-state files:

- `AGENTS.md`
- `CODEX.md`
- `docs/CODEX-WORKFLOW.md`
- `docs/planning/strategy/product-goal.md`
- `docs/planning/strategy/roadmap.md`
- `docs/planning/releases/MVP.md`
- `docs/_governance/dor.md`
- `docs/_governance/dod.md`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.md`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.execution.md`
- `docs/planning/epics/EP-016/epic.md`
- `docs/planning/epics/EP-016/stories/ST-048-provider-mapping-artifact-gate.md`
- `docs/planning/workpacks/ST-048/workpack.md`
- `contracts/schemas/command.schema.json`
- `contracts/schemas/decision.schema.json`
- `contracts/VERSION`
- `docs/contracts/CONTRACT-GOVERNANCE-RUNBOOK.md`
- `docs/adr/ADR-000-ai-platform-intent-decision-engine.md`
- `docs/adr/ADR-001-contract-versioning-compatibility-policy.md`
- `docs/adr/ADR-004-partial-trust-corridor.md`
- `docs/adr/ADR-006-multi-item-internal-model.md`
- `docs/adr/ADR-008-asr-cloudru-whisper-mvp.md`
- `docs/_indexes/adr-index.md`
- `docs/_indexes/diagrams-index.md`
- `docs/diagrams/README.md`

Read HomeTusk inputs read-only from:

```text
C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/domain-planner-v1-gate/
```

Required files:

- `README.md`
- `decision-action-taxonomy-accepted-v0.md`
- `natural-command-contract-v0-draft.md`
- `golden-scenarios-fixtures-v0/README.md`
- `eval-rubric-v0.md`
- `privacy-and-retention-questions.md`
- `provider-planner-readiness-checklist.md`
- `hometusk-ai-platform-integration-doc-drift.md`
- `provider-initiative-brief.md`

Do not copy raw scenario text into PLAN output.

## PLAN Output Required

Return a Russian PLAN report with:

- affected files to create/modify;
- files explicitly forbidden;
- contract impact decision and stop conditions;
- ADR/diagram decision;
- privacy/retention questions that can be answered now vs HOLD;
- risks;
- exact validation commands;
- delegated Gate C recommendation: GO / HOLD / NO-GO for ST-048 APPLY.

## Gate C Criteria

Recommend GO only if:

- planned files stay inside ST-048 allowed paths;
- no runtime/contract/schema/fixture/test/HomeTusk writes are needed;
- current-schema mapping can be documented without pretending first-class `reject` or `confirm` exists;
- ADR and diagram artifacts can be source-bound to existing evidence;
- privacy posture can avoid raw text and raw audio leakage.

Recommend HOLD if any runtime, contract, schema, fixture, public API, or HomeTusk mutation is required.
