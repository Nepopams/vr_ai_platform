# ST-049 Codex PLAN Report

**Date:** 2026-06-15
**Mode:** Read-only PLAN
**Result:** GO for ST-049 eval runner APPLY

## Findings

- ST-049 can be executed without copying HomeTusk raw fixture YAML into this repository.
- Fixture strategy is reference-only: runner reads the HomeTusk fixture directory from a caller-supplied path or documented default path.
- HomeTusk source revision remains `d924c631c80895995c65f22bec6f77dc0a0347b7`.
- Seed fixture versions are `golden-scenarios-v0` and `golden-context-v0`.
- Seed scenario IDs are `GS-001` through `GS-010`; context fixture IDs are `ctx-home-1-default`, `ctx-home-1-no-default-list`, and `ctx-home-1-ambiguous-petr`.
- `yaml` import is available in the current environment.
- `routers.factory.decide()` can run provider decisions without calling `app.services.decision_service.decide()`, avoiding default decision/text log writes.
- Default router strategy is `v1` unless `DECISION_ROUTER_STRATEGY` is set.

## Files Approved For ST-049 APPLY

### Create

- `scripts/evaluate_domain_planner_seed.py`
- `tests/test_domain_planner_seed_eval.py`
- `docs/planning/workpacks/ST-049/review-report.md`

### Modify

- `docs/planning/workpacks/ST-049/workpack.md`
- `docs/planning/epics/EP-016/epic.md`
- `docs/planning/epics/EP-016/stories/ST-049-fixture-import-eval-runner.md`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.execution.md`

## Forbidden Files

- `contracts/**`
- `contracts/schemas/**`
- `contracts/VERSION`
- `app/**`
- `graphs/**`
- `routers/**`
- `agents/**`
- `agent_registry/**`
- `agent_runner/**`
- `llm_policy/**`
- `skills/**`
- `.codex/skills/**`
- existing fixture directories
- HomeTusk repository files

## Eval Report Schema

The runner output must include:

- `source`: repo/path/revision/fixture versions/scenario count/context count;
- `run`: run command, planner label, schema version, decision versions, selected feature flags;
- `results[]`: scenario ID, schema validity, expected/actual outcome family, intent/action family, failure buckets, trace completeness, skipped status;
- `metrics`: aggregate counts, blocker failures, schema-valid count, outcome matches, unsupported auto-execute count, cross-household reference count;
- `failure_buckets`: aggregate bucket counts.

The output must not include:

- raw command text;
- item names;
- member, zone, or list display names;
- raw prompts;
- raw LLM output.

## Stop Conditions

Stop and create a different workpack if implementation requires:

- copying raw HomeTusk fixtures into this repository;
- changing provider runtime behavior;
- changing contracts, schemas, public API, or contract version;
- modifying existing project fixtures;
- editing HomeTusk files.

## Gate C Recommendation

GO for ST-049 eval runner APPLY.

This GO does not approve ST-050 runtime planner APPLY.
