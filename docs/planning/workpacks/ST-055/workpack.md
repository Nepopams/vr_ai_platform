# WP / ST-055: Narrow Planner Runtime Adaptation from 50-Scenario Blockers

**Status:** Done (Gate D GO)
**Story:** `docs/planning/epics/EP-017/stories/ST-055-narrow-planner-runtime-adaptation.md`
**Initiative:** `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.md`
**Date:** 2026-06-15

---

## Outcome

Adapt the deterministic Domain Planner v1 narrow corridor so the provider returns schema-valid, non-executing first-class `reject` decisions for unsupported/cross-household commands and executes only the simple task / grounded shopping cases needed to clear the 50-scenario blocker buckets.

## Sources of Truth

| Artifact | Path |
| --- | --- |
| Current initiative | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.md` |
| Execution notes | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md` |
| Epic | `docs/planning/epics/EP-017/epic.md` |
| ST-052 eval report | `docs/planning/workpacks/ST-052/local-50-scenario-eval-report.json` |
| ST-053 posture | `docs/planning/epics/EP-017/domain-planner-v1-contract-posture.md` |
| ST-054 contract schema | `contracts/schemas/decision.schema.json`, `contracts/schemas/command.schema.json`, `contracts/VERSION` |
| ADR baseline | `docs/adr/ADR-009-domain-planner-v1-narrow-corridor.md` |
| Flow diagram | `docs/diagrams/domain-planner-v1-flow.puml` |

HomeTusk read-only source package:

```text
C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/provider-domain-planner-v1-acceptance/
```

Source revision read: `b18bfdb6f0bdbf6044ad5b986aee837dca7bf5b3`.

## Scope

### In Scope

- `DecisionDTO.action=reject` runtime output using the ST-054 `2.1.0` schema.
- Narrow deterministic task and shopping recognition improvements proven by blocker IDs.
- Shopping extraction fixes that preserve repeated singular `propose_add_shopping_item` boundaries.
- Eval-runner classification of first-class `reject` / `confirm`.
- Focused tests and regenerated 50-scenario eval report.
- Planning/review artifacts for Gate D.

### Out of Scope

- Contract/schema/version changes.
- Provider `answer`.
- Direct plural shopping action.
- First-class runtime `confirm` implementation beyond eval classification.
- HomeTusk repo edits.
- HomeTusk runtime/backend/mobile/OpenAPI work.
- Production rollout/config changes.
- Broad household automation, assignment execution, reschedule execution, completion execution, device control, payment, or external ordering execution.

## Allowed Paths

| Path | Purpose |
| --- | --- |
| `graphs/core_graph.py` | Shared deterministic planner helpers and first-class safe reject builder. |
| `scripts/evaluate_domain_planner_seed.py` | Eval classification for first-class `reject` / `confirm`. |
| `tests/test_domain_planner_v1_corridor.py` | Runtime regression tests for ST-055 behavior. |
| `tests/test_domain_planner_seed_eval.py` | Eval-runner tests for first-class reject classification. |
| `docs/diagrams/domain-planner-v1-flow.puml` | Prevent stale safe-reject mapping label if needed. |
| `docs/planning/epics/EP-017/**` | Story/epic status and evidence. |
| `docs/planning/workpacks/ST-055/**` | Workpack, PLAN, review, and closure artifacts. |
| `docs/planning/workpacks/ST-052/local-50-scenario-eval-report.json` | Regenerated privacy-safe 50-scenario eval evidence. |
| `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md` | Gate C/D decisions and evidence. |
| `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.md` | Initiative status update only. |

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

## Implementation Plan

1. Add a first-class `reject` decision builder that uses ST-054 schema fields and remains non-executing.
2. Change safe-reject runtime routing to use first-class `reject` after the `2.1.0` contract.
3. Add narrow unsupported/cross-household rejection classifiers for blocker evidence categories.
4. Add narrow deterministic task/shopping recognition and extraction support for blocker evidence categories.
5. Update eval classification to recognize `reject` and `confirm` outcomes.
6. Update focused tests.
7. Regenerate the 50-scenario eval report with `--check-no-raw-text`.
8. Run review gate and record Gate D.

## Acceptance Criteria

- [x] 50-scenario blocker failure count is zero.
- [x] Unsupported auto-execute count is zero.
- [x] Cross-household references remain zero.
- [x] `reject` decisions are schema-valid and non-executing.
- [x] Simple task and grounded shopping blocker IDs no longer have `wrong_outcome`.
- [x] No raw HomeTusk scenario text appears in planning/review artifacts.
- [x] No HomeTusk files are modified.
- [x] No contract/schema/version files are changed by ST-055.

## Validation Commands

```bash
$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 -m pytest tests/test_domain_planner_v1_corridor.py tests/test_domain_planner_seed_eval.py tests/test_contracts.py tests/test_api_decide.py tests/test_api_models.py -v
$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 scripts/evaluate_domain_planner_seed.py --source-dir C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/provider-domain-planner-v1-acceptance/expanded-golden-scenarios-v1 --check-no-raw-text --output docs/planning/workpacks/ST-052/local-50-scenario-eval-report.json
git diff --check
```

## Rollback

- Revert ST-055 edits in `graphs/core_graph.py`, eval runner/tests, diagram label, and ST-055 planning artifacts.
- Regenerate the 50-scenario eval report from the previous runtime state if rollback evidence is needed.
- Do not touch ST-054 contract/schema changes unless a separate rollback workpack is approved.

## Risks

| Risk | Probability | Impact | Mitigation |
| --- | --- | --- | --- |
| Overfitting to fixture text | Medium | High | Implement semantic keyword families and test with non-fixture wording. |
| First-class `reject` surprises consumers | Medium | High | ST-054 already added schema/API model support; keep `/v1/decide` shape schema-valid. |
| Broad unsupported commands become reject instead of clarify | Medium | Medium | Keep reject classifiers narrow to unsupported/cross-household categories from blocker evidence. |
| Diagram/ADR drift | Low | Medium | Update flow diagram label; no new ADR because ST-054 contract governance already approved first-class `reject`. |

## Gate Decisions

- Gate A: inherited GO for current initiative.
- Gate B: inherited GO for decomposition; runtime mutation was HOLD until ST-055.
- Gate C: delegated GO for ST-055 runtime APPLY within allowed paths above.
- Gate D: delegated GO after review.

## Validation Results

Validation was run on 2026-06-15.

| Check | Result |
| --- | --- |
| Focused tests | 33 passed, 1 warning |
| Full tests | 346 passed, 4 skipped, 1 warning |
| Contract checker | Pass |
| Schema-bump check | Pass |
| Release sanity | Pass through `python3 -m skills.release_sanity` |
| 50-scenario eval | 50 evaluated, 50 schema-valid, 50 outcome matches, 0 blocker failures |
| Unsupported auto-execute | 0 |
| Cross-household references | 0 |
| Diff hygiene | Pass with LF-to-CRLF warnings only |

`make release-sanity` was not run because `make` is unavailable in this Windows environment; the direct `python3` entrypoint passed.
