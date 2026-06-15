# ST-053: Contract Posture Decision for Reject, Confirm, Answer, and Shopping Plurality

**Status:** Done (Gate D GO for contract posture; schema/runtime APPLY HOLD)
**Epic:** `docs/planning/epics/EP-017/epic.md`
**Owner:** Codex / AI Platform engineering team

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.md` |
| Execution notes | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md` |
| Epic | `docs/planning/epics/EP-017/epic.md` |
| Contract posture | `docs/planning/epics/EP-017/domain-planner-v1-contract-posture.md` |
| Workpack | `docs/planning/workpacks/ST-053/workpack.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |
| ADR-001 | `docs/adr/ADR-001-contract-versioning-compatibility-policy.md` |
| ADR-009 | `docs/adr/ADR-009-domain-planner-v1-narrow-corridor.md` |
| Current DecisionDTO schema | `contracts/schemas/decision.schema.json` |

HomeTusk read-only source:

```text
C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/provider-domain-planner-v1-acceptance/reject-confirm-answer-contract-posture.md
```

---

## Description

ST-053 records the provider-side contract posture required before schema or runtime work. It decides which outcomes need contract-governed implementation, which remain blocked, and which current-schema mappings remain acceptable for the next provider eval step.

## Acceptance Criteria

```gherkin
Given the current DecisionDTO schema lacks first-class reject, confirm, and answer
When ST-053 completes the contract posture gate
Then the provider decision for reject, confirm, answer, and shopping plurality is explicit
And the next contract workpack scope is bounded
And no schema, public API, runtime, or HomeTusk files are modified
```

## Scope

### In scope

- Decide provider posture for first-class `reject`.
- Decide provider posture for non-executing `confirm`.
- Decide provider posture for blocked `answer`.
- Decide whether repeated singular shopping actions remain sufficient for the next provider eval step.
- Define the minimum ST-054 contract workpack scope.

### Out of scope

- Editing `contracts/**`, schemas, or `contracts/VERSION`.
- Runtime planner changes.
- HomeTusk repository edits.
- Adding provider `answer` without HomeTusk answer/read-model governance.
- Production rollout/config changes.

## Test Strategy

### Unit tests

- Not applicable; docs-only contract posture.

### Validation

- `rg` evidence checks over ST-053 artifacts.
- `git diff --check`.

### Test data

- ST-052 eval report metrics.
- HomeTusk contract posture doc, read-only.

## Flags

- contract_impact: no-edit in ST-053; yes in ST-054 if approved
- adr_needed: none for ST-053; possible for ST-054
- diagrams_needed: none for ST-053; possible for ST-054/ST-055
- security_sensitive: yes
- traceability_critical: yes

## Blocked By

- None for ST-053.

Schema/runtime work remains blocked until ST-054/ST-055 workpacks, PLAN, Gate C, APPLY, review, and Gate D.
