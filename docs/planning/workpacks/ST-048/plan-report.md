# ST-048 Codex PLAN Report

**Date:** 2026-06-15
**Mode:** Read-only PLAN
**Result:** GO for ST-048 artifact APPLY

## Findings

- ST-048 can be executed as a docs-only artifact workpack.
- Current `decision.schema.json` supports `start_job`, `propose_create_task`, `propose_add_shopping_item`, `clarify`, and multi-item output through `start_job.payload.proposed_actions`.
- Current provider schema does not provide first-class `reject`, `confirm`, `answer`, or direct `add_shopping_items` actions.
- ADR-000 and ADR-002 preserve the stateless provider boundary and prohibit domain mutation in AI Platform.
- ADR-001 requires contract governance and semver for any schema, action enum, required field, or semantic contract change.
- ADR-006 confirms multi-item shopping can use repeated proposed actions without schema changes.
- ADR-008 keeps ASR transcription-only and outside `/v1/decide` automatic routing.
- `app/services/decision_service.py` calls `append_decision_text`, but `app/logging/decision_log.py` writes raw command text only when `LOG_USER_TEXT` is explicitly enabled; default is `false`.

## Files Approved For ST-048 APPLY

### Create

- `docs/planning/epics/EP-016/domain-planner-v1-provider-mapping.md`
- `docs/adr/ADR-009-domain-planner-v1-narrow-corridor.md`
- `docs/diagrams/domain-planner-v1-flow.puml`
- `docs/guides/domain-planner-v1-privacy-retention.md`

### Modify

- `docs/_indexes/adr-index.md`
- `docs/_indexes/diagrams-index.md`
- `docs/planning/workpacks/ST-048/workpack.md`
- `docs/planning/workpacks/ST-048/plan-report.md`

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
- `tests/**`
- `skills/**`
- `.codex/skills/**`
- Any HomeTusk file

## Contract Impact

No contract edit is approved for ST-048.

Stop and create a dedicated contract workpack if later work needs:

- first-class `reject`, `confirm`, or `answer` actions;
- direct `add_shopping_items` action enum;
- required `planner_version` in DecisionDTO;
- new `/v1/decide` request fields or public API changes;
- semantic changes to `start_job`, `propose_*`, or `clarify`.

## ADR / Diagram Decision

ADR and diagram artifacts are required before runtime APPLY. ST-048 may create them because they are source-bound documentation artifacts and do not mutate runtime behavior.

## Privacy / Retention Decision

ST-048 must document:

- raw audio is outside `/v1/decide` planner flow;
- raw command text logging is opt-in through `LOG_USER_TEXT`, defaults to `false`, and is HOLD for production enablement unless separately approved;
- eval/review reports should use scenario IDs, source metadata, metrics, and failure buckets, not raw scenario text;
- retention period, storage region, access policy, deletion process, and external model training policy remain HOLD unless a source exists.

## Gate C Recommendation

GO for ST-048 APPLY only.

Runtime APPLY remains HOLD until a later workpack passes its own PLAN and Gate C.
