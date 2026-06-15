# Domain Planner v1 Provider Contract Posture

**Status:** ST-053 contract artifact gate output
**Date:** 2026-06-15
**Initiative:** `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.md`
**Epic:** `docs/planning/epics/EP-017/epic.md`
**Story:** `docs/planning/epics/EP-017/stories/ST-053-contract-posture.md`

---

## Decision Summary

| Area | Provider posture | Next action |
| --- | --- | --- |
| First-class `reject` | Required before HomeTusk runtime acceptance. Current `status=error`, `action=clarify` mapping remains provider evidence only. | Open ST-054 contract-governed schema/version work. |
| Non-executing `confirm` | Required before assignment, reschedule, task-shopping linkage, or batch planning UX acceptance. | Open ST-054 contract-governed schema/version work. |
| `answer` | Blocked. Do not add provider `answer` until HomeTusk read-model and answer contract governance starts. | Keep out of ST-054. |
| `add_shopping_items` | Direct plural provider action is not required for the next provider eval step. Repeated singular `propose_add_shopping_item` remains acceptable if item boundaries are preserved. | Handle item-boundary failures through planner/eval work unless later evidence proves schema insufficiency. |

## Evidence

### Current Provider Contract

- `contracts/VERSION` is `2.0.0`.
- `contracts/schemas/decision.schema.json` supports `start_job`, `propose_create_task`, `propose_add_shopping_item`, and `clarify`.
- The schema does not support first-class `reject`, `confirm`, or `answer`.
- Repeated `propose_add_shopping_item` actions are already supported through `start_job.payload.proposed_actions`.

### HomeTusk Read-Only Posture

Source: `C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/provider-domain-planner-v1-acceptance/reject-confirm-answer-contract-posture.md`

- `reject_mapped_to_error` is not acceptable as a HomeTusk runtime/product contract.
- First-class `reject` is required before runtime integration.
- First-class `confirm` is required before assignment, reschedule, task-shopping linkage, or batch planning UX.
- First-class `answer` is required before answer/status UX, but it depends on grounded HomeTusk read models.
- Direct plural `add_shopping_items` is not required for the next provider eval step.

### ST-052 Eval Evidence

Source: `docs/planning/workpacks/ST-052/local-50-scenario-eval-report.json`

- 50 scenarios evaluated.
- 50 schema-valid decisions.
- 7 blocker failure scenarios.
- 1 unsupported auto-execute.
- 5 item-boundary loss buckets.
- 0 cross-household references.

## Contract Gate

| Field | Decision |
| --- | --- |
| Impact | ST-053 itself has no schema impact; ST-054 will have contract impact. |
| Affected contracts | Future ST-054: `DecisionDTO`, possibly CommandDTO capabilities if new actions are gated by capabilities. |
| ADR-001 classification | Adding optional/non-required first-class actions may be non-breaking only if unknown actions are safely handled by consumers; required fields or changed semantics are breaking. |
| Version decision | ST-053: no version bump. ST-054 must decide semver before schema edits. |
| Fixtures/tests required | ST-054 must update contract fixtures and schema validation tests. |
| Gate result | GO for posture; HOLD for schema mutation until ST-054 workpack and Gate C. |

## ADR / Diagram Gate

| Field | Decision |
| --- | --- |
| Architecture impact | ST-053 docs-only posture has no runtime architecture impact. |
| ADR impact | ADR-009 already says first-class `reject` / `confirm` require later contract governance. ST-054 must decide whether ADR-009 addendum or new ADR is needed. |
| Diagram impact | None for ST-053. ST-054/ST-055 must revisit diagrams if provider flow or action semantics change. |
| Required artifacts | No new ADR/diagram for ST-053. |
| Index updates | None for ST-053. |
| Gate result | NO ARTIFACT CHANGE REQUIRED for ST-053; HOLD for future schema/runtime artifact impact. |

## Required ST-054 Scope

ST-054 must not start APPLY until its own workpack, PLAN, and delegated Gate C are complete.

Minimum ST-054 decisions:

1. Exact `DecisionDTO` representation for first-class `reject`.
2. Exact `DecisionDTO` representation for non-executing `confirm`.
3. Whether new `CommandDTO.capabilities` values are needed.
4. ADR-001 semver classification and `contracts/VERSION` bump.
5. Contract fixture additions under existing contract-checker fixture structure.
6. Schema validation and compatibility checks.
7. Consumer compatibility notes for unknown actions.
8. Rollback and migration notes.

## Explicit Non-Decisions

- No provider `answer` schema in ST-054 unless HomeTusk answer/read-model governance starts first.
- No direct plural `add_shopping_items` action in ST-054 unless a later gate proves repeated singular actions are insufficient.
- No HomeTusk runtime, mobile, backend, OpenAPI, or repository changes.
- No production rollout/config changes.
