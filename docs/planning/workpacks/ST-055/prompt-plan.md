# Codex PLAN — ST-055 Narrow Planner Runtime Adaptation

## Mode

Read-only PLAN completed before delegated Gate C.

## Required Sources

- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.md`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md`
- `docs/planning/workpacks/ST-052/local-50-scenario-eval-report.json`
- `docs/planning/workpacks/ST-054/workpack.md`
- `contracts/schemas/decision.schema.json`
- `graphs/core_graph.py`
- `routers/v2.py`
- `scripts/evaluate_domain_planner_seed.py`
- `tests/test_domain_planner_v1_corridor.py`
- `tests/test_domain_planner_seed_eval.py`

## PLAN Questions

1. Which blocker IDs remain after ST-054 regeneration?
2. Can the blockers be resolved without contract/schema/version changes?
3. Which runtime files need edits?
4. Which eval/test files need edits?
5. Do ADRs or diagrams drift?
6. What validation proves Gate D readiness?

## Stop Conditions

- Any need for `answer`, new contract fields, schema version bump, HomeTusk edits, backend/mobile/API rollout, or broad planner semantics.
- Any need to log/copy raw HomeTusk scenario text into planning/review artifacts.
