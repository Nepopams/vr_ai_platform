# ST-055: Narrow Planner Runtime Adaptation from 50-Scenario Blockers

**Status:** Done (Gate D GO)
**Epic:** `docs/planning/epics/EP-017/epic.md`
**Initiative:** `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.md`
**Workpack:** `docs/planning/workpacks/ST-055/workpack.md`

---

## User Story

As the AI Platform provider,
I need the deterministic Domain Planner v1 narrow corridor to use the approved `2.1.0` contract and address the 50-scenario blocker buckets,
so that HomeTusk can review provider evidence with zero blocker failure scenarios before any runtime or mobile integration.

## Scope

In scope:

- First-class non-executing `reject` runtime output for unsupported, unsafe, or cross-household commands already covered by ST-054.
- Narrow deterministic recognition improvements for simple task creation and grounded multi-item shopping commands.
- Eval-runner alignment so first-class `reject` / `confirm` outcomes are classified correctly.
- Focused regression tests and regenerated privacy-safe 50-scenario eval report.
- Diagram label update if needed to avoid stale safe-reject mapping language.

Out of scope:

- New contracts, schema fields, or contract version bump.
- First-class `answer`.
- Direct plural `add_shopping_items` action.
- HomeTusk repository edits.
- HomeTusk runtime, backend, OpenAPI, mobile, or production rollout.
- Broad multi-agent planning, reschedule execution, completion execution, assignment execution, or payment/device execution.

## Acceptance Criteria

1. The 50-scenario eval has zero blocker failure scenarios.
2. Unsupported auto-execute count is zero.
3. Cross-household reference count remains zero.
4. `reject` scenarios return non-executing schema-valid decisions.
5. Simple task and multi-item shopping blocker scenarios are handled inside the narrow corridor.
6. No raw HomeTusk scenario text is copied into planning/review summaries.
7. Existing provider/API/contract tests remain passing.
8. No HomeTusk files are modified.
9. No contract/schema/version change is made in ST-055.

## Evidence Inputs

The ST-052 50-scenario eval report identifies blocker scenario IDs:

- `HT-GS-003`
- `HT-GS-008`
- `HT-GS-015`
- `HT-GS-043`
- `HT-GS-046`
- `HT-GS-048`
- `HT-GS-049`

Failure buckets before ST-055:

- `wrong_outcome=7`
- `unsupported_auto_execute=1`
- `item_boundary_loss=5`
- `cross_household_reference=0`

## Gate Status

Gate C was delegated GO for ST-055 only within `docs/planning/workpacks/ST-055/workpack.md`.

Gate D is GO. Review report: `docs/planning/workpacks/ST-055/review-report.md`.
