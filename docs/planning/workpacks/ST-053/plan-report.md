# ST-053 PLAN Report

**Mode:** Read-only PLAN
**Date:** 2026-06-15
**Result:** Ready for delegated Gate C GO

## Findings

| Area | Finding |
| --- | --- |
| Current contract version | `contracts/VERSION` is `2.0.0`. |
| Current DecisionDTO actions | `start_job`, `propose_create_task`, `propose_add_shopping_item`, `clarify`. |
| Missing first-class outcomes | No provider `reject`, `confirm`, or `answer` action exists. |
| Shopping action shape | `start_job.payload.proposed_actions` supports repeated singular `propose_add_shopping_item`. |
| HomeTusk `reject` posture | First-class `reject` is required before runtime integration; current mapped error/clarify is evidence only. |
| HomeTusk `confirm` posture | First-class non-executing `confirm` is required before assignment/linkage/reschedule/batch UX. |
| HomeTusk `answer` posture | `answer` is blocked until grounded HomeTusk answer/read-model governance starts. |
| HomeTusk shopping posture | Direct plural `add_shopping_items` is not required for the next provider eval step. |
| Contract impact | None for ST-053. ST-054 will have contract impact if it edits schemas. |
| ADR / diagram impact | None for ST-053. ST-054/ST-055 must revisit if action semantics or flow change. |
| Runtime impact | None for ST-053. |

## Files To Modify

- `docs/planning/epics/EP-017/domain-planner-v1-contract-posture.md`
- `docs/planning/epics/EP-017/stories/ST-053-contract-posture.md`
- `docs/planning/workpacks/ST-053/**`
- `docs/planning/epics/EP-017/epic.md`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.md`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md`

## Files To Avoid

- `contracts/**`
- `contracts/schemas/**`
- `contracts/VERSION`
- `graphs/**`
- `routers/**`
- `app/**`
- `agent_registry/**`
- `agent_runner/**`
- `llm_policy/**`
- HomeTusk repository files

## Implementation Steps

1. Create provider contract posture artifact.
2. Record ST-054 minimum contract workpack scope.
3. Update EP-017 and execution notes with Gate C/D decisions.
4. Run docs/evidence checks and diff hygiene checks.

## Validation Commands

```bash
rg -n "ST-053|first-class `reject`|non-executing `confirm`|answer.*blocked|repeated singular" docs/planning/epics/EP-017 docs/planning/workpacks/ST-053 docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md
git diff --check
git status --short
```

## Blockers

None for ST-053. Schema/runtime work remains HOLD pending ST-054/ST-055 workpacks.

## Gate C Readiness

GO. The APPLY is bounded to planning and contract posture documentation only.
