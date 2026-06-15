# Codex PLAN Prompt — ST-049 HomeTusk Seed Eval Runner

You are in Codex PLAN for ST-049.

## Mode

Read-only only.

Do not edit, create, move, delete, format, install, commit, or mutate files. Do not change runtime, contracts, schemas, existing fixtures, public API, or HomeTusk files.

## Objective

Prepare exact APPLY findings for a privacy-safe Domain Planner v1 seed eval runner that references HomeTusk YAML fixtures read-only and emits redacted provider evidence.

## Required Sources

Read current-state files:

- `AGENTS.md`
- `CODEX.md`
- `docs/CODEX-WORKFLOW.md`
- `docs/planning/strategy/product-goal.md`
- `docs/planning/strategy/roadmap.md`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.md`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.execution.md`
- `docs/planning/epics/EP-016/epic.md`
- `docs/planning/epics/EP-016/stories/ST-049-fixture-import-eval-runner.md`
- `docs/planning/epics/EP-016/domain-planner-v1-provider-mapping.md`
- `docs/guides/domain-planner-v1-privacy-retention.md`
- `docs/adr/ADR-009-domain-planner-v1-narrow-corridor.md`
- `docs/planning/workpacks/ST-049/workpack.md`
- `contracts/schemas/command.schema.json`
- `contracts/schemas/decision.schema.json`
- `scripts/`
- `skills/quality-eval/scripts/evaluate_golden.py`
- `skills/graph-sanity/scripts/run_graph_suite.py`
- `tests/test_quality_eval.py`

Read HomeTusk inputs read-only from:

```text
C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/domain-planner-v1-gate/golden-scenarios-fixtures-v0/
```

Required files:

- `README.md`
- `golden-scenarios-v0.yaml`
- `context-fixtures-v0.yaml`

Do not copy raw scenario text into PLAN output.

## PLAN Output Required

Return a Russian PLAN report with:

- exact files to create/modify;
- files explicitly forbidden;
- fixture strategy: reference-only or copied, with rationale;
- parser/dependency findings, including whether `yaml` import is available;
- eval report schema fields;
- privacy redaction checks;
- risks and stop conditions;
- exact validation commands;
- delegated Gate C recommendation: GO / HOLD / NO-GO for ST-049 APPLY.

## Gate C Criteria

Recommend GO only if:

- planned files stay inside ST-049 allowed paths;
- no runtime/contract/schema/existing-fixture/public API/HomeTusk writes are needed;
- HomeTusk fixtures can be referenced read-only;
- eval output can omit raw text and raw entity names;
- runner can avoid `decision_service.decide()` so validation does not write decision logs;
- dependency assumptions are explicit.

Recommend HOLD if fixture copying, schema changes, runtime planner changes, or HomeTusk edits are required.
