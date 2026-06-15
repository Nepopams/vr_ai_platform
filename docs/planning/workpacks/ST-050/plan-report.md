# ST-050 Codex PLAN Report

**Date:** 2026-06-15
**Mode:** Read-only PLAN
**Result:** GO for ST-050 runtime APPLY under current-schema mapping

## Findings

- ST-048 and ST-049 are complete and provide the required artifact gate, mapping, ADR, privacy posture, and seed eval baseline.
- Current `DecisionDTO` can represent the ST-050 implementation without schema edits:
  - execute task/shopping through `status=ok`, `action=start_job`;
  - multi-item shopping through repeated `propose_add_shopping_item`;
  - clarify through `status=clarify`, `action=clarify`;
  - safe rejection through current-schema `status=error`, `action=clarify`.
- The current router strategy is `v1`, which uses `graphs/core_graph.py`; the ST-049 seed report therefore measures `graphs/core_graph.py` behavior unless `DECISION_ROUTER_STRATEGY` is set.
- `RouterV2Pipeline` already preserves multi-item shopping boundaries, but it should share the same unsafe/mixed guardrails as the v1 graph path.
- ST-049 baseline evidence shows 2 blocker failure scenarios:
  - one unsupported auto-execute case;
  - one reject-like case that maps to ordinary clarify instead of current-schema safe rejection.
- ST-049 baseline also shows item boundary loss in the v1 graph path because `process_command()` uses single-item extraction for shopping.
- ASR route `app/routes/asr.py` is transcription-only and does not import or call the decision route/service. ST-050 should add a regression test, not modify ASR runtime.

## Files Approved For ST-050 APPLY

### Modify

- `graphs/core_graph.py`
- `routers/v2.py`
- `docs/planning/workpacks/ST-050/workpack.md`
- `docs/planning/epics/EP-016/epic.md`
- `docs/planning/epics/EP-016/stories/ST-050-domain-planner-v1-implementation.md`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.execution.md`
- `docs/planning/workpacks/ST-049/local-seed-eval-report.json`

### Create

- `tests/test_domain_planner_v1_corridor.py`
- `docs/planning/workpacks/ST-050/review-report.md`

## Contract Gate

| Field | Decision |
|-------|----------|
| Impact | none |
| Affected contracts | None |
| ADR-001 classification | No schema shape, enum, required field, version, or public API change |
| Version decision | No contract version bump |
| Fixtures/tests required | Runtime tests and ST-049 eval report only; no contract fixtures |
| Gate result | GO for current-schema runtime mapping; HOLD if first-class `reject`, `confirm`, `answer`, or plural action is required |

## Proposed Implementation Steps

1. Add a current-schema safe rejection builder in `graphs/core_graph.py`.
2. Add narrow-corridor guard helpers for unsupported/risky/mixed requests without storing raw scenario text in planning artifacts.
3. Update v1 graph shopping branch to use `extract_items()` and repeated proposed actions.
4. Update v1 graph and RouterV2 validation to clarify or safe-reject outside the allowed execute corridor.
5. Add focused tests for schema-valid task/shopping, item boundaries, safe rejection mapping, unsupported auto-execute prevention, `/v1/decide` validation, and ASR non-coupling.
6. Regenerate the ST-049 local seed eval report and verify zero blocker failures.

## Validation Commands

```bash
python3 -m pytest tests/test_domain_planner_v1_corridor.py -v
python3 -m pytest tests/test_multi_item_e2e.py tests/test_planner_multi_item.py tests/test_graph_execution.py tests/test_api_decide.py -v
python3 scripts/evaluate_domain_planner_seed.py --source-dir C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/domain-planner-v1-gate/golden-scenarios-fixtures-v0 --check-no-raw-text --output docs/planning/workpacks/ST-049/local-seed-eval-report.json
python3 -m pytest tests/test_domain_planner_seed_eval.py -v
git diff --check
```

## Stop Conditions

Stop and create a separate contract workpack if implementation requires:

- editing `contracts/**`, `contracts/schemas/**`, or `contracts/VERSION`;
- adding first-class `reject`, `confirm`, `answer`, or direct plural shopping actions;
- changing `/v1/decide` public request/response shape;
- editing HomeTusk files;
- enabling raw user text or raw LLM output logging;
- adding broad planner, reschedule execute, completion execute, answer runtime, workload optimizer, or production multi-agent behavior.

## Gate C Recommendation

GO for ST-050 runtime APPLY within the approved current-schema boundaries.

This GO does not approve contract changes, public API changes, HomeTusk writes, production rollout/config changes, or initiative closure.
