# WP / ST-054: Contract Schema for First-Class Reject and Non-Executing Confirm

**Status:** Done (Gate D GO for contract schema; runtime acceptance HOLD)
**Story:** `docs/planning/epics/EP-017/stories/ST-054-reject-confirm-contract-schema.md`
**Owner:** Codex PLAN / Codex APPLY / read-only review gate

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Roadmap | `docs/planning/strategy/roadmap.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.md` |
| Execution notes | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md` |
| Epic | `docs/planning/epics/EP-017/epic.md` |
| Story | `docs/planning/epics/EP-017/stories/ST-054-reject-confirm-contract-schema.md` |
| ST-053 posture | `docs/planning/epics/EP-017/domain-planner-v1-contract-posture.md` |
| ADR-001 | `docs/adr/ADR-001-contract-versioning-compatibility-policy.md` |
| ADR-009 | `docs/adr/ADR-009-domain-planner-v1-narrow-corridor.md` |
| Contract governance | `docs/contracts/CONTRACT-GOVERNANCE-RUNBOOK.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

ST-054 adds additive, versioned contract support for first-class `reject` and non-executing `confirm` provider decisions. It does not change runtime planner behavior or HomeTusk files.

## Acceptance Criteria

1. `contracts/VERSION` is bumped from `2.0.0` to `2.1.0`.
2. DecisionDTO accepts first-class `reject` and `confirm` actions.
3. DecisionDTO accepts optional `decision_outcome` with action-compatible values.
4. CommandDTO capabilities accept `reject` and `confirm`.
5. Contract fixtures include valid `reject` and `confirm` examples and one invalid confirm example.
6. Pydantic API models mirror the schema changes.
7. `docs/CONTRACTS.md` documents new actions and examples.
8. Baseline schemas are updated after validation.
9. Runtime planner, HomeTusk, production rollout/config, and provider `answer` remain untouched.

## Files to Change

### New files (create)

| File | Description |
|------|-------------|
| `skills/contract-checker/fixtures/valid_decision_reject.json` | Valid first-class reject DecisionDTO fixture. |
| `skills/contract-checker/fixtures/valid_decision_confirm.json` | Valid non-executing confirm DecisionDTO fixture. |
| `skills/contract-checker/fixtures/invalid_decision_confirm_missing_confirmation_id.json` | Invalid confirm payload fixture. |
| `docs/planning/workpacks/ST-054/review-report.md` | Read-only review gate after APPLY. |

### Modified files (update)

| File | Change |
|------|--------|
| `contracts/VERSION` | Bump to `2.1.0`. |
| `contracts/schemas/decision.schema.json` | Add `reject`, `confirm`, optional `decision_outcome`, and payload schemas. |
| `contracts/schemas/command.schema.json` | Add `reject` and `confirm` capabilities. |
| `contracts/schemas/.baseline/decision.schema.json` | Update baseline after schema validation. |
| `contracts/schemas/.baseline/command.schema.json` | Update baseline after schema validation. |
| `skills/contract-checker/fixtures/valid_decision_start_job.json` | Update `schema_version` to `2.1.0`. |
| `skills/contract-checker/fixtures/valid_decision_clarify.json` | Update `schema_version` to `2.1.0`. |
| `app/models/api_models.py` | Mirror new capabilities/actions and optional `decision_outcome`. |
| `app/routes/decide.py` | Omit optional response fields with `None` so API output remains schema-valid. |
| `tests/test_api_models.py` | Add reject/confirm model validation tests. |
| `docs/CONTRACTS.md` | Document new version, actions, compatibility notes, and examples. |
| `docs/planning/epics/EP-017/**` | Update ST-054 status/evidence. |
| `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md` | Record Gate C/D decisions. |

### Deleted files

| File | Reason |
|------|--------|
| None | Not applicable. |

## Implementation Plan

### Step 1: Update schemas and version

Add first-class action and payload definitions, optional `decision_outcome`, capabilities, and bump `contracts/VERSION` to `2.1.0`.

### Step 2: Update fixtures and API models

Add fixtures for `reject` and `confirm`, update schema versions, and mirror the contract in Pydantic models.

### Step 3: Update docs and baselines

Update `docs/CONTRACTS.md` and copy current schemas to `.baseline` after validation.

### Step 4: Validate and review

Run contract checker, schema-bump check, focused tests, diff hygiene, and read-only review gate.

## Verification Commands

```bash
$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 skills/contract-checker/scripts/validate_contracts.py
$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 skills/schema-bump/scripts/check_breaking_changes.py
$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 -m pytest tests/test_contracts.py tests/test_api_models.py -v
git diff --check
git status --short
```

## Tests

| Test | Checks | Expected |
|------|--------|----------|
| contract checker | Contract fixtures match schemas | Pass |
| schema-bump check | No breaking required/property/type change vs baseline | Pass |
| `tests/test_contracts.py` | Fixtures and schema version alignment | Pass |
| `tests/test_api_models.py` | Pydantic model support for new contract shape | Pass |

## DoD Checklist

- [x] Version bumped.
- [x] Schemas updated.
- [x] Fixtures updated.
- [x] Baselines updated.
- [x] Docs updated.
- [x] Focused validations pass.
- [x] Review report and Gate D are recorded.

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| New status values break consumers | Medium | High | Do not change `status` enum in ST-054. Use first-class actions and optional `decision_outcome`. |
| Contract docs diverge from schema | Medium | Medium | Update `docs/CONTRACTS.md` and fixtures in the same workpack. |
| Runtime starts emitting new actions without planner work | Low | High | ST-054 does not edit runtime planner; ST-055 remains required. |
| `answer` is added too early | Low | High | Explicitly out of scope and absent from schema. |

## Rollback

- Revert schema, fixture, version, docs, API model, and ST-054 planning updates.
- Restore `.baseline` schemas from the prior revision.
- No runtime or HomeTusk rollback is required.

## APPLY Boundaries

### Allowed

- `contracts/VERSION`
- `contracts/schemas/decision.schema.json`
- `contracts/schemas/command.schema.json`
- `contracts/schemas/.baseline/decision.schema.json`
- `contracts/schemas/.baseline/command.schema.json`
- `skills/contract-checker/fixtures/**`
- `app/models/api_models.py`
- `app/routes/decide.py`
- `tests/test_api_models.py`
- `docs/CONTRACTS.md`
- `docs/planning/epics/EP-017/**`
- `docs/planning/workpacks/ST-054/**`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.md`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md`

### Forbidden

- `graphs/**`
- `routers/**`
- `app/services/**`
- `agent_registry/**`
- `agent_runner/**`
- `llm_policy/**`
- HomeTusk repository files
- Production rollout/config files
- Provider `answer` contract/action
- Direct plural `add_shopping_items` action

## Human Gates

- Gate A: GO, recorded in execution notes.
- Gate B: GO for ST-054 after ST-053 posture; HOLD for runtime mutations.
- Human Gate C: delegated GO for ST-054, recorded in execution notes.
- Human Gate D: GO for contract schema; HOLD for runtime acceptance.

## Validation Results

Validation was run on 2026-06-15.

| Command | Result |
|---------|--------|
| `$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 skills/contract-checker/scripts/validate_contracts.py` | Pass |
| `$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 skills/schema-bump/scripts/check_breaking_changes.py` | Pass |
| Explicit HEAD-vs-current schema-bump check for `decision.schema.json` | Pass |
| Explicit HEAD-vs-current schema-bump check for `command.schema.json` | Pass |
| `$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 -m pytest tests/test_contracts.py tests/test_api_models.py tests/test_api_decide.py tests/test_api_versioned.py tests/test_health_ready.py tests/test_domain_planner_v1_corridor.py -v` | Pass: 32 passed, 1 warning |
| `$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 scripts/evaluate_domain_planner_seed.py --source-dir C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/provider-domain-planner-v1-acceptance/expanded-golden-scenarios-v1 --check-no-raw-text --output docs/planning/workpacks/ST-052/local-50-scenario-eval-report.json` | Pass |
| `git diff --check` | Pass with LF-to-CRLF warnings only |

## Post-Contract Eval Metrics

| Metric | Value |
|--------|-------|
| Schema versions | `2.1.0` |
| Total scenarios | 50 |
| Evaluated scenarios | 50 |
| Schema-valid decisions | 50 |
| Outcome matches | 43 |
| Intent matches | 11 |
| Unsupported auto-execute | 1 |
| Cross-household references | 0 |
| Blocker failure scenarios | 7 |
| Failure buckets | `wrong_outcome=7`, `wrong_intent=39`, `item_boundary_loss=5`, `unsupported_auto_execute=1` |
