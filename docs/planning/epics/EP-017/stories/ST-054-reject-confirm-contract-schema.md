# ST-054: Contract Schema for First-Class Reject and Non-Executing Confirm

**Status:** Done (Gate D GO for contract schema; runtime acceptance HOLD)
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
| ST-053 posture | `docs/planning/epics/EP-017/domain-planner-v1-contract-posture.md` |
| Workpack | `docs/planning/workpacks/ST-054/workpack.md` |
| ADR-001 | `docs/adr/ADR-001-contract-versioning-compatibility-policy.md` |
| ADR-009 | `docs/adr/ADR-009-domain-planner-v1-narrow-corridor.md` |
| Contract governance | `docs/contracts/CONTRACT-GOVERNANCE-RUNBOOK.md` |
| Current schemas | `contracts/schemas/` |
| Contract fixtures | `skills/contract-checker/fixtures/` |

---

## Description

ST-054 adds contract-level support for first-class provider `reject` and non-executing `confirm` decisions without adding runtime planner behavior. The change is additive and versioned as a MINOR contract bump.

## Acceptance Criteria

```gherkin
Given the current DecisionDTO schema lacks reject and confirm
When ST-054 applies the contract update
Then DecisionDTO validates first-class reject and confirm decisions
And existing start_job/propose/clarify decisions remain valid
And contracts/VERSION is bumped to 2.1.0
And contract fixtures, baseline schemas, API models, and docs are updated
And no runtime planner or HomeTusk files are modified
```

## Scope

### In scope

- Add `reject` and `confirm` to DecisionDTO action enum.
- Add optional `decision_outcome`.
- Add strict `reject_payload` and `confirm_payload` definitions.
- Add `reject` and `confirm` to CommandDTO capabilities.
- Update Pydantic API models to mirror the schema.
- Add contract fixtures and focused API model tests.
- Update `contracts/VERSION`, schema baselines, and `docs/CONTRACTS.md`.

### Out of scope

- Provider `answer`.
- Direct plural `add_shopping_items`.
- Runtime planner changes.
- HomeTusk repository changes.
- Production rollout/config changes.

## Test Strategy

### Unit tests

- `tests/test_contracts.py`
- `tests/test_api_models.py`

### Contract checks

- `python3 skills/contract-checker/scripts/validate_contracts.py`
- `python3 skills/schema-bump/scripts/check_breaking_changes.py`

### Test data

- New valid `reject` and `confirm` DecisionDTO fixtures.
- Invalid `confirm` fixture missing required confirmation id.

## Flags

- contract_impact: yes
- adr_needed: covered-by-ADR-009
- diagrams_needed: none-current-flow
- security_sensitive: yes
- traceability_critical: yes

## Blocked By

- ST-053 Gate D GO.

Runtime planner behavior remains blocked until ST-055.

## Closure Evidence

| Field | Value |
| --- | --- |
| Contract version | `2.1.0` |
| New actions | `reject`, `confirm` |
| New optional field | `decision_outcome` |
| Review report | `docs/planning/workpacks/ST-054/review-report.md` |
| Focused tests | 32 passed |
| Gate D | GO for contract schema; HOLD for runtime acceptance |
