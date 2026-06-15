# Domain Planner v1 Provider Closure and HomeTusk Handoff

**Date:** 2026-06-15
**Initiative:** `INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor`
**Epic:** `EP-016`
**Status:** Provider-side GO for closure; HomeTusk acceptance remains separate

## Provider Result

AI Platform completed the provider-side Domain Planner v1 narrow household command corridor under current-schema mapping.

The provider result is limited to:

- schema-valid simple `create_task` provider decisions;
- schema-valid multi-item shopping provider decisions using repeated `propose_add_shopping_item` actions;
- safe `clarify` for missing, ambiguous, contextual, confirm-required, or unsupported requests;
- current-schema safe rejection for unsafe or impossible requests using `status=error`, `action=clarify`;
- `/v1/decide` as the unchanged provider entrypoint;
- ASR remaining transcription-only.

## Evidence Package

| Area | Evidence |
|------|----------|
| Artifact gate | `docs/planning/workpacks/ST-048/review-report.md` |
| Provider mapping | `docs/planning/epics/EP-016/domain-planner-v1-provider-mapping.md` |
| ADR | `docs/adr/ADR-009-domain-planner-v1-narrow-corridor.md` |
| Diagram | `docs/diagrams/domain-planner-v1-flow.puml` |
| Privacy posture | `docs/guides/domain-planner-v1-privacy-retention.md` |
| Eval runner | `scripts/evaluate_domain_planner_seed.py` |
| Eval report | `docs/planning/workpacks/ST-049/local-seed-eval-report.json` |
| Runtime review | `docs/planning/workpacks/ST-050/review-report.md` |
| Final review | `docs/planning/workpacks/ST-051/review-report.md` |

## Seed Eval Summary

| Metric | Value |
|--------|-------|
| Fixture versions | `golden-scenarios-v0`, `golden-context-v0` |
| Source revision | `d924c631c80895995c65f22bec6f77dc0a0347b7` |
| Total scenarios | 10 |
| Evaluated scenarios | 10 |
| Schema-valid decisions | 10 |
| Outcome matches | 10 |
| Unsupported auto-execute | 0 |
| Cross-household references | 0 |
| Blocker failure scenarios | 0 |

Remaining non-blocker buckets:

| Bucket | Count |
|--------|-------|
| `wrong_intent` | 7 |
| `item_boundary_loss` | 2 |

These remaining buckets are not Gate D blockers because the affected rows are non-executing clarify/reject-mapping outcomes, but they should remain visible to HomeTusk reviewers.

## Contract Status

No `contracts/**`, schema, version, or public API change was made.

Current-schema limitations remain:

- no first-class `reject`;
- no first-class `confirm`;
- no first-class `answer`;
- no direct plural `add_shopping_items` action enum.

If HomeTusk requires first-class versions of those outcomes, open a dedicated provider contract workpack before implementation.

## Privacy / Retention Status

- No raw fixture text is included in provider planning, review, or eval reports.
- Raw audio is not part of `/v1/decide`.
- ASR does not call `/v1/decide` automatically.
- `LOG_USER_TEXT` remains opt-in and was not enabled for validation.
- Production prompt/response retention policy remains a separate HOLD item if an external LLM is introduced or raw text retention is requested.

## HomeTusk Review Notes

HomeTusk should treat this as provider evidence, not product acceptance.

Recommended HomeTusk-side next steps:

1. Review the provider evidence package listed above.
2. Expand product-owned scenarios toward the 50-scenario acceptance threshold.
3. Decide whether current-schema safe rejection is sufficient or a first-class `reject` contract workpack is required.
4. Decide whether non-executing `confirm` is required before mixed task/shopping or assignment-inference flows.
5. Keep HomeTusk execution, guardrails, audit, and final acceptance outside AI Platform.

## Non-Goals Preserved

- No HomeTusk runtime, backend, mobile, OpenAPI, or integration file was changed.
- No direct HomeTusk state mutation was introduced.
- No direct mobile/web call path to AI Platform was introduced.
- No broad multi-agent production planner was introduced.
- No production rollout/config change was made.
