# ST-055 PLAN Report

**Mode:** Read-only PLAN before delegated Gate C
**Date:** 2026-06-15

## Findings

| Area | Finding |
| --- | --- |
| Blocker IDs | `HT-GS-003`, `HT-GS-008`, `HT-GS-015`, `HT-GS-043`, `HT-GS-046`, `HT-GS-048`, `HT-GS-049` |
| Blocker buckets | `wrong_outcome=7`, `unsupported_auto_execute=1`, `item_boundary_loss=5`, `cross_household_reference=0` |
| Contract impact | None for ST-055; ST-054 already added `reject`, `confirm`, and `decision_outcome` under `2.1.0`. |
| Runtime impact | Narrow deterministic planner adaptation in `graphs/core_graph.py`; `routers/v2.py` reuses shared helpers. |
| Eval impact | `scripts/evaluate_domain_planner_seed.py` must recognize first-class `reject` / `confirm` outcomes. |
| Test impact | Focused runtime and eval-runner tests required. |
| ADR impact | No new ADR required; ADR-009 requires contract governance before first-class reject/confirm, satisfied by ST-054. |
| Diagram impact | Flow diagram label should be updated from temporary mapping language to first-class safe reject. |
| HomeTusk impact | Read-only input only; no writes. |

## Proposed Implementation

1. Add a first-class non-executing reject builder in `graphs/core_graph.py`.
2. Route safe-reject categories through first-class `reject`.
3. Add narrow deterministic recognition for the task/shopping blocker categories without broad automation.
4. Update eval outcome mapping and provider outcome classification for first-class `reject` / `confirm`.
5. Add regression tests using non-fixture wording.
6. Regenerate the privacy-safe 50-scenario report.

## Approved Paths

- `graphs/core_graph.py`
- `scripts/evaluate_domain_planner_seed.py`
- `tests/test_domain_planner_v1_corridor.py`
- `tests/test_domain_planner_seed_eval.py`
- `docs/diagrams/domain-planner-v1-flow.puml`
- `docs/planning/epics/EP-017/**`
- `docs/planning/workpacks/ST-055/**`
- `docs/planning/workpacks/ST-052/local-50-scenario-eval-report.json`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.md`

## Forbidden Paths

- HomeTusk repository files.
- `contracts/**`
- `contracts/schemas/**`
- `contracts/VERSION`
- `app/models/api_models.py`
- `app/routes/**`
- `agent_registry/**`
- `agent_runner/**`
- `llm_policy/**`
- production rollout/config files

## Validation Commands

```bash
$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 -m pytest tests/test_domain_planner_v1_corridor.py tests/test_domain_planner_seed_eval.py tests/test_contracts.py tests/test_api_decide.py tests/test_api_models.py -v
$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 scripts/evaluate_domain_planner_seed.py --source-dir C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/provider-domain-planner-v1-acceptance/expanded-golden-scenarios-v1 --check-no-raw-text --output docs/planning/workpacks/ST-052/local-50-scenario-eval-report.json
git diff --check
```

## Readiness

Gate C recommendation: GO for ST-055 APPLY within the approved paths. Initiative acceptance remains HOLD until validation proves zero blocker failure scenarios and review passes.
