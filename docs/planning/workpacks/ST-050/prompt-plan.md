# ST-050 Codex PLAN Prompt

**Mode:** Read-only PLAN
**Workpack:** `docs/planning/workpacks/ST-050/workpack.md`

## Objective

Plan the bounded runtime adaptation for Domain Planner v1 narrow household command corridor without changing contracts, schemas, public API, HomeTusk files, or production rollout config.

## Required Sources

- `AGENTS.md`
- `CODEX.md`
- `docs/CODEX-WORKFLOW.md`
- `docs/planning/strategy/product-goal.md`
- `docs/planning/strategy/roadmap.md`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.md`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.execution.md`
- `docs/planning/epics/EP-016/epic.md`
- `docs/planning/epics/EP-016/stories/ST-050-domain-planner-v1-implementation.md`
- `docs/planning/epics/EP-016/domain-planner-v1-provider-mapping.md`
- `docs/adr/ADR-009-domain-planner-v1-narrow-corridor.md`
- `docs/guides/domain-planner-v1-privacy-retention.md`
- `docs/planning/workpacks/ST-049/local-seed-eval-report.json`
- `contracts/schemas/command.schema.json`
- `contracts/schemas/decision.schema.json`
- `graphs/core_graph.py`
- `routers/v2.py`
- `app/routes/asr.py`
- `app/routes/decide.py`
- `app/services/decision_service.py`
- Relevant tests under `tests/`

## PLAN Questions

1. Which exact runtime files need changes?
2. Can ST-050 satisfy the seed blocker failures using current `DecisionDTO` schema?
3. Does the plan require contract/schema/version/public API changes?
4. Which tests and eval commands prove narrow corridor behavior?
5. What stop conditions should block APPLY?

## Required PLAN Output

- affected files;
- no-schema-impact or contract-impact decision;
- proposed implementation steps;
- exact validation commands;
- risks and stop conditions;
- Gate C recommendation: GO, HOLD, or NO-GO.

## Forbidden During PLAN

- file writes or edits;
- package installs;
- network;
- runtime mutation;
- commits;
- HomeTusk writes.
