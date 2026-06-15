# Domain Planner v1 Provider Mapping

**Status:** ST-048 artifact gate output
**Date:** 2026-06-15
**Initiative:** `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.md`
**Epic:** `docs/planning/epics/EP-016/epic.md`
**Workpack:** `docs/planning/workpacks/ST-048/workpack.md`

---

## Purpose

This note maps the HomeTusk accepted Domain Planner v1 taxonomy to the current AI Platform provider schema. It is an artifact-gate document, not runtime implementation approval.

## Source Inputs

| Source | Evidence |
| --- | --- |
| AI Platform contract version | `contracts/VERSION` = `2.0.0` |
| Provider request schema | `contracts/schemas/command.schema.json` |
| Provider response schema | `contracts/schemas/decision.schema.json` |
| HomeTusk artifact package | `C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/domain-planner-v1-gate/` |
| HomeTusk source revision read | `d924c631c80895995c65f22bec6f77dc0a0347b7` |
| Fixture version | `golden-scenarios-v0`, `golden-context-v0` |

## Current Provider Schema Facts

- `CommandDTO.capabilities` currently allows `start_job`, `propose_create_task`, `propose_add_shopping_item`, and `clarify`.
- `DecisionDTO.action` currently allows `start_job`, `propose_create_task`, `propose_add_shopping_item`, and `clarify`.
- `DecisionDTO.status` currently allows `ok`, `clarify`, and `error`.
- `start_job.payload.proposed_actions[]` can contain repeated `propose_add_shopping_item` actions, which supports multi-item shopping boundaries without a schema edit.
- There is no first-class provider action for `reject`, `confirm`, `answer`, or direct plural `add_shopping_items`.

## Outcome Mapping

| HomeTusk canonical outcome | Current provider mapping | Gate decision |
| --- | --- | --- |
| `execute` for `create_task` | `status=ok`, `action=start_job`, `payload.job_type=create_task`, with `propose_create_task` in `proposed_actions` when capability allows | Allowed only for clear, grounded task creation in the narrow corridor. |
| `execute` for `add_shopping_items` | `status=ok`, `action=start_job`, `payload.job_type=add_shopping_item`, with one `propose_add_shopping_item` per item in `proposed_actions` | Allowed only when list/default grounding and item boundaries are clear. |
| `clarify` | `status=clarify`, `action=clarify`, `payload.missing_fields[]` identifies missing or ambiguous fields | Preferred when context is missing, ambiguous, unsupported, or outside the safe corridor. |
| `reject` | Temporary current-schema safe rejection: non-executing `DecisionDTO` using `status=error` with `action=clarify` and a clarify payload; evals classify this as `reject_mapped_to_error` | Semantically rough. If HomeTusk requires first-class reject before acceptance, HOLD and create a contract workpack. |
| `confirm` | Not first-class. Current-schema behavior must not execute; use clarify/no-op for risky understood plans or HOLD for contract workpack | Optional in the initiative; not approved as execution semantics. |
| `answer` | Not first-class. Current-schema behavior must not mutate; clarify or block until HomeTusk answer contract exists | Out of scope for Domain Planner v1 runtime. |

## Narrow Corridor Rules

Provider auto-execute candidates are limited to:

- `create_task`;
- `add_shopping_items` represented as repeated current-schema shopping proposed actions.

Provider must clarify or safe-reject when:

- required task/list/member/zone/date context is missing or ambiguous;
- a request is unsupported, unsafe, cross-household, or unverifiable;
- a request would require direct AI execution or HomeTusk state mutation;
- a request requires `confirm`, `answer`, reschedule, completion, linkage, batch planning, or workload redistribution semantics not approved by contract governance.

## Seed Scenario Mapping Without Raw Text

| Scenario IDs | Expected outcome family | Current-schema provider posture |
| --- | --- | --- |
| `GS-001` | `execute_or_clarify` | Execute only if date/time window is safely normalized; otherwise clarify. |
| `GS-002`, `GS-003` | `execute` / `execute_or_clarify` | Use repeated shopping proposed actions; clarify if list/source cannot be grounded. |
| `GS-004`, `GS-005`, `GS-006`, `GS-007` | `confirm_or_clarify` / `confirm` / `clarify_or_confirm` | Do not execute under current schema; clarify/no-op unless a future contract workpack adds confirm. |
| `GS-008`, `GS-010` | `clarify` / `answer_blocked_or_clarify` | Clarify or block; never mutate. |
| `GS-009` | `reject` | Use current-schema safe rejection or HOLD for first-class reject contract work. |

Reports and review artifacts should reference scenario IDs and failure buckets, not raw scenario text.

## Contract Gate Decision

ST-048 approves no schema or public API change.

Later work must stop for contract governance if it needs:

- a first-class `reject`, `confirm`, or `answer` action;
- a direct plural `add_shopping_items` action enum;
- required `planner_version` or prompt/model provenance fields in DecisionDTO;
- new CommandDTO fields for locale, timezone, reference instant, or audit metadata;
- any changed semantics for `start_job`, `propose_*`, `clarify`, schema validation, or `/v1/decide`.

## Eval Strategy Boundary

ST-049 should decide whether to import HomeTusk seed fixtures into this repository or reference them read-only. If copied, each fixture copy must record:

- source repository;
- source path;
- source revision or import date;
- fixture version;
- transformation notes;
- privacy classification.

Provider eval output should include:

- scenario ID;
- schema validity;
- mapped outcome;
- intent/action family;
- failure buckets;
- trace/version completeness;
- aggregate metrics;
- skipped scenarios with explicit reasons.

## Gate C Requirements For Runtime Work

A later runtime workpack must not receive Gate C GO until it lists:

- exact runtime files to change;
- exact schema impact or no-schema-impact decision;
- fixture import/reference path;
- eval command and expected report path;
- rollback plan;
- tests for no unsupported auto-execute, no cross-household execution, clarify over guessing, item boundary preservation, ASR non-coupling, and schema validation.
