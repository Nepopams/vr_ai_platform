# ST-054 PLAN Report

**Mode:** Read-only PLAN
**Date:** 2026-06-15
**Result:** Ready for delegated Gate C GO

## Findings

| Area | Finding |
| --- | --- |
| Current version | `contracts/VERSION` is `2.0.0`. |
| Semver decision | MINOR bump to `2.1.0`; additive action/capability values and optional top-level field. |
| DecisionDTO action edits | Add `reject` and `confirm`. |
| DecisionDTO status edits | None; keep `ok`, `clarify`, `error`. |
| Optional field | Add `decision_outcome` with `execute`, `clarify`, `reject`, `confirm`. |
| Payloads | Add strict `reject_payload` and `confirm_payload`. |
| CommandDTO | Add `reject` and `confirm` capabilities. |
| Pydantic models | Update `CapabilityType`, `ActionType`, and optional `decision_outcome`. |
| API serialization | Omit optional `None` fields from decision responses to preserve JSON Schema validity. |
| Fixtures | Add valid reject/confirm and invalid confirm fixtures; update valid fixture schema versions. |
| Docs | Update `docs/CONTRACTS.md`. |
| Baseline | Update `.baseline` schemas after validation. |
| ADR / diagram | ADR-009 covers contract governance need; no diagram change because provider flow remains AI Platform decision -> HomeTusk validation/execution. |

## Files To Modify

- `contracts/VERSION`
- `contracts/schemas/decision.schema.json`
- `contracts/schemas/command.schema.json`
- `contracts/schemas/.baseline/decision.schema.json`
- `contracts/schemas/.baseline/command.schema.json`
- `skills/contract-checker/fixtures/**`
- `app/models/api_models.py`
- `app/routes/decide.py`
- `tests/test_api_models.py`
- `docs/CONTRACTS.md`
- `docs/planning/epics/EP-017/**`
- `docs/planning/workpacks/ST-054/**`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md`

## Files To Avoid

- `graphs/**`
- `routers/**`
- `app/services/**`
- `agent_registry/**`
- `agent_runner/**`
- `llm_policy/**`
- HomeTusk repository files
- Production rollout/config files

## Validation Commands

```bash
$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 skills/contract-checker/scripts/validate_contracts.py
$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 skills/schema-bump/scripts/check_breaking_changes.py
$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 -m pytest tests/test_contracts.py tests/test_api_models.py -v
git diff --check
git status --short
```

## Blockers

None for ST-054 contract APPLY. Runtime behavior remains blocked until ST-055.

## Gate C Readiness

GO. The APPLY is bounded to contract/schema/fixture/API-model/docs updates only.
