# ST-051: Review Gate, Closure Evidence, and HomeTusk Handoff

**Status:** Done
**Epic:** `docs/planning/epics/EP-016/epic.md`
**Owner:** TBD
**Flags:** contract_impact=tbd, adr_needed=tbd, diagrams_needed=tbd, security_sensitive=yes, traceability_critical=yes

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Initiative | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.md` |
| Epic | `docs/planning/epics/EP-016/epic.md` |
| ST-048 | `docs/planning/epics/EP-016/stories/ST-048-provider-mapping-artifact-gate.md` |
| ST-049 | `docs/planning/epics/EP-016/stories/ST-049-fixture-import-eval-runner.md` |
| ST-050 | `docs/planning/epics/EP-016/stories/ST-050-domain-planner-v1-implementation.md` |
| Workflow | `docs/CODEX-WORKFLOW.md` |
| DoD | `docs/_governance/dod.md` |

## Description

Run the read-only review gate after implementation, collect closure evidence, and produce HomeTusk handoff notes. This story does not approve HomeTusk runtime work; it packages provider evidence for separate HomeTusk acceptance.

## Acceptance Criteria

```gherkin
Given Domain Planner v1 implementation and eval evidence exist
When the read-only review gate runs
Then the review result is GO or NO-GO with must-fix, should-fix, evidence, and recommendation
And contract/ADR/diagram drift is explicitly checked
And seed fixtures have zero blocker failures before Gate D
And privacy/retention posture is documented
And HomeTusk handoff notes are clear and source-bound
```

## Scope

### In scope

- Read-only review gate report.
- Gate D decision evidence.
- Closure/handoff summary for HomeTusk review.
- Initiative status recommendation.

### Out of scope

- Production code edits during review.
- HomeTusk file edits.
- Merge/ship decision outside delegated provider gate.

## Test Strategy

### Unit tests

- None for review artifact creation.

### Integration tests

- Re-run required validation commands from implementation workpack before Gate D.

### Test data

- ST-049 eval output and ST-050 validation output.

## Blocked By

- None. ST-051 has Gate D GO for provider initiative closure.

## Delivery Evidence

| Artifact | Path |
|----------|------|
| Workpack | `docs/planning/workpacks/ST-051/workpack.md` |
| PLAN report | `docs/planning/workpacks/ST-051/plan-report.md` |
| Closure handoff | `docs/planning/epics/EP-016/domain-planner-v1-closure-handoff.md` |
| Review report | `docs/planning/workpacks/ST-051/review-report.md` |

## Gate Decisions

| Gate | Decision |
|------|----------|
| Gate C | GO for docs-only closure APPLY. |
| Gate D | GO for provider initiative closure; HomeTusk acceptance remains separate. |
