# ST-052 PLAN Report

**Mode:** Read-only PLAN
**Date:** 2026-06-15
**Result:** Ready for delegated Gate C GO

## Findings

| Area | Finding |
| --- | --- |
| Source package | HomeTusk expanded v1 fixture directory exists read-only under `provider-domain-planner-v1-acceptance/expanded-golden-scenarios-v1/`. |
| Source revision | `b18bfdb6f0bdbf6044ad5b986aee837dca7bf5b3`. |
| Fixture structure | v1 suite has 50 scenarios and 6 contexts. |
| Existing runner | `scripts/evaluate_domain_planner_seed.py` hard-codes v0 fixture filenames and can be generalized without runtime or contract edits. |
| Existing tests | `tests/test_domain_planner_seed_eval.py` already verifies source metadata, scenario IDs, privacy-safe output, and failure buckets for v0. |
| Contract impact | None for ST-052. |
| ADR / diagram impact | None for ST-052. |
| Runtime impact | None for ST-052. |
| Privacy | Reports must continue to omit raw fixture text and household/user-facing strings. |

## Files To Modify

- `scripts/evaluate_domain_planner_seed.py`
- `tests/test_domain_planner_seed_eval.py`
- `docs/planning/workpacks/ST-052/local-50-scenario-eval-report.json`
- `docs/planning/workpacks/ST-052/review-report.md`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md`
- `docs/planning/epics/EP-017/epic.md`
- `docs/planning/epics/EP-017/stories/ST-052-expanded-50-scenario-eval-runner.md`

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

1. Add fixture filename discovery for v0 and v1 scenario/context files.
2. Include fixture filenames and suite policy metadata in the report.
3. Add safe expected-outcome mapping for `reject_or_clarify`.
4. Extend privacy sensitive-key scan for v1 user-facing fields.
5. Add unit tests for v1 fixture loading and report privacy.
6. Run the expanded 50-scenario eval and record review/Gate D.

## Validation Commands

```bash
$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 -m pytest tests/test_domain_planner_seed_eval.py -v
$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 scripts/evaluate_domain_planner_seed.py --source-dir C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/provider-domain-planner-v1-acceptance/expanded-golden-scenarios-v1 --check-no-raw-text --output docs/planning/workpacks/ST-052/local-50-scenario-eval-report.json
git diff --check
git status --short
```

## Blockers

None for ST-052. Broader contract/runtime work remains HOLD pending later stories.

## Gate C Readiness

GO. The APPLY is bounded to eval tooling, tests, and ST-052 planning/evidence artifacts.
