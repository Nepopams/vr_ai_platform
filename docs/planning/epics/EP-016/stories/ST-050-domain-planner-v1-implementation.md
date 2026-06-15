# ST-050: Domain Planner v1 Narrow Corridor Implementation/Adaptation

**Status:** Done
**Epic:** `docs/planning/epics/EP-016/epic.md`
**Owner:** TBD
**Flags:** contract_impact=tbd-after-ST-048, adr_needed=covered-by-ST-048, diagrams_needed=covered-by-ST-048, security_sensitive=yes, traceability_critical=yes

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Initiative | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.md` |
| Epic | `docs/planning/epics/EP-016/epic.md` |
| ST-048 | `docs/planning/epics/EP-016/stories/ST-048-provider-mapping-artifact-gate.md` |
| ST-049 | `docs/planning/epics/EP-016/stories/ST-049-fixture-import-eval-runner.md` |
| Command schema | `contracts/schemas/command.schema.json` |
| Decision schema | `contracts/schemas/decision.schema.json` |
| Current graph | `graphs/core_graph.py` |
| Current router | `routers/v2.py` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

## Description

Implement or adapt a single provider Domain Planner v1 path for the narrow household command corridor. The implementation must preserve existing flags and fallback behavior, keep `/v1/decide` schema validation, and avoid broad household automation.

## Acceptance Criteria

```gherkin
Given a supported narrow household command with grounded context
When Domain Planner v1 evaluates it
Then the provider returns a schema-valid decision for simple task creation or multi-item shopping addition
And item boundaries are preserved
And missing or ambiguous task/list/member/zone/date context clarifies instead of guessing
And unsupported, unsafe, cross-household, or unverifiable requests do not execute
And ASR remains transcription-only and does not call /v1/decide automatically
```

## Scope

### In scope

- A single planner path for `create_task`, multi-item shopping addition, `clarify`, and safe rejection mapping.
- Version/trace metadata preservation.
- Feature flag or strategy boundary if runtime behavior changes production decisioning.
- Regression tests for schema validity, no unsupported auto-execute, item boundary preservation, and ASR boundary.

### Out of scope

- Direct HomeTusk mutation.
- HomeTusk backend/mobile/API changes.
- Broad multi-agent planner.
- Natural reschedule auto-execute.
- Natural completion auto-execute.
- Read-only answer implementation before HomeTusk answer contract exists.
- Contract/schema changes without dedicated contract workpack approval.

## Test Strategy

### Unit tests

- Planner mapping tests for task, shopping, clarify, and reject-like safe outcomes.

### Integration tests

- `/v1/decide` schema validation and RouterV2/graph regression.
- ASR non-coupling regression.

### Test data

- Provider eval fixtures from ST-049.

## Blocked By

- None for APPLY. ST-048 and ST-049 are complete, and `docs/planning/workpacks/ST-050/plan-report.md` records delegated Gate C GO.

## Delivery Evidence

| Artifact | Path |
|----------|------|
| Workpack | `docs/planning/workpacks/ST-050/workpack.md` |
| PLAN prompt | `docs/planning/workpacks/ST-050/prompt-plan.md` |
| PLAN report | `docs/planning/workpacks/ST-050/plan-report.md` |
| Review report | `docs/planning/workpacks/ST-050/review-report.md` |
| Tests | `tests/test_domain_planner_v1_corridor.py` |
| Regenerated eval report | `docs/planning/workpacks/ST-049/local-seed-eval-report.json` |

## Gate Decisions

| Gate | Decision |
|------|----------|
| Gate C | GO for current-schema runtime APPLY bounded to `graphs/core_graph.py`, `routers/v2.py`, `tests/test_domain_planner_v1_corridor.py`, ST-050 docs, and regenerated ST-049 eval report. |
| Gate D | GO for ST-050 closure; seed eval has zero blocker failures and no contract/schema/public API/HomeTusk edits. |

## Runtime Evidence

| Metric | Value |
|--------|-------|
| Seed scenarios evaluated | 10 |
| Schema-valid decisions | 10 |
| Outcome matches | 10 |
| Unsupported auto-execute | 0 |
| Cross-household references | 0 |
| Blocker failure scenarios | 0 |
