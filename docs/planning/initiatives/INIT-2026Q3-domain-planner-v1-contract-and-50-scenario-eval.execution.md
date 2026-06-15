# INIT-2026Q3 Domain Planner v1 Contract + 50-Scenario Eval Execution Notes

**Status:** Done; Gate A GO; Gate B GO; ST-052 Gate D GO; ST-053 Gate D GO; ST-054 Gate D GO; ST-055 Gate D GO; ST-056 Gate D GO; provider-side initiative Gate D GO
**Date:** 2026-06-15
**Initiative:** `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.md`
**Roadmap:** `docs/planning/strategy/roadmap.md`
**Delegation:** Human gates for this initiative are delegated to Codex, but every GO / HOLD / NO-GO decision must be recorded with evidence, risks, and rationale.

---

## Intake Summary

| Field | Decision |
| --- | --- |
| Request type | Mixed delivery initiative: roadmap update, planning, artifact gate, eval tooling, future contract posture, future runtime adaptation if proven necessary |
| Scope anchor | `INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval` |
| Current workflow step | `intake -> planning -> artifact gate -> workpack -> PLAN -> delegated Gate C GO -> APPLY -> read-only review -> delegated Gate D GO -> provider handoff complete` |
| Risk | High, because the initiative touches provider/consumer acceptance evidence, contract posture, privacy-safe eval reporting, and future `/v1/decide` semantics |
| Primary boundary | AI Platform remains a stateless provider; HomeTusk remains execution, guardrail, audit, runtime, mobile, API, and final acceptance authority |
| Narrow corridor status | `INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor` is not reopened; it remains provider-side Done and is used as the source baseline |

## Sources Read

| Artifact | Path / Evidence |
| --- | --- |
| Active rules | `AGENTS.md`, `CODEX.md`, `docs/CODEX-WORKFLOW.md` |
| Product goal | `docs/planning/strategy/product-goal.md` |
| Roadmap | `docs/planning/strategy/roadmap.md` |
| MVP scope | `docs/planning/releases/MVP.md` |
| DoR / DoD | `docs/_governance/dor.md`, `docs/_governance/dod.md` |
| Closed baseline initiative | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.md` |
| Closed baseline execution notes | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.execution.md` |
| Current initiative | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.md` |
| ADR baseline | `docs/adr/ADR-001-contract-versioning-compatibility-policy.md`, `docs/adr/ADR-009-domain-planner-v1-narrow-corridor.md` |
| Contract runbook | `docs/contracts/CONTRACT-GOVERNANCE-RUNBOOK.md` |
| Privacy posture | `docs/guides/domain-planner-v1-privacy-retention.md` |
| Existing eval runner | `scripts/evaluate_domain_planner_seed.py` |
| Existing eval tests | `tests/test_domain_planner_seed_eval.py` |

## HomeTusk Read-Only Inputs

| Artifact | Evidence |
| --- | --- |
| Repository path | `C:/Users/user/Documents/projects/hometusk/hometusk` |
| Source revision read | `b18bfdb6f0bdbf6044ad5b986aee837dca7bf5b3` |
| Acceptance package | `docs/research/ai-command-capabilities/provider-domain-planner-v1-acceptance/**` |
| Expanded fixture suite | `expanded-golden-scenarios-v1/` |
| Fixture metadata | 50 scenarios, 6 contexts, fixture version `v1`; raw scenario text must not be copied into planning/review summaries |

## Flags

| Flag | Value | Rationale |
| --- | --- | --- |
| `contract_impact` | `tbd-gated`; ST-052 is `none` | ST-052 only generalizes eval fixture loading. First-class `reject` / `confirm` requires a later contract workpack. |
| `adr_needed` | `none` for ST-052; `possible` later | ADR-009 covers current-schema narrow corridor. Contract semantics or public behavior changes may need new ADR/ADR update. |
| `diagrams_needed` | `none` for ST-052; `possible` later | Eval tooling does not change provider flow. Contract/runtime behavior changes may require diagram review. |
| `security_sensitive` | `yes` | Fixture reports must not leak raw scenario text or household names. |
| `traceability_critical` | `yes` | Eval reports must record source revision, fixture version, run command, schema/decision versions, metrics, and failure buckets. |
| `cross_repo` | `read-only-inputs` | HomeTusk artifacts are acceptance inputs only; commits stay in this repository. |

## Gate A Decision — GO

**Decision:** GO for the current roadmap initiative `INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval`.

**Evidence:**

- Roadmap had no active initiative selected, while the 50-scenario successor initiative already existed as a source-bound draft.
- The requested `narrow-household-command-corridor` initiative is already Done with ST-051 Gate D GO and should not be reopened without a new scope rationale.
- The successor initiative preserves the closed narrow corridor as baseline and keeps HomeTusk runtime/mobile/API work blocked.
- HomeTusk acceptance package exists read-only with expanded v1 fixtures and LIMITED-GO posture.

**Rationale:**

Gate A criteria are satisfied for the successor initiative: provider-side scope is preserved, HomeTusk remains read-only input, expanded 50 scenarios are the eval target, HomeTusk runtime/mobile/API remains blocked, and production rollout remains out of scope.

**Risks accepted:**

- The 50-scenario eval may expose blocker failures; the initiative must record HOLD/NO-GO rather than force acceptance.
- Current-schema `reject` and missing `confirm` remain product-contract gaps until explicit contract posture work.
- External HomeTusk fixtures are read-only inputs; this repository must avoid copying raw scenario text into reports or planning notes.

## Gate B Decision — GO for ST-052, HOLD for Contract/Runtime Mutations

**Decision:** GO for decomposition and the first implementation workpack `ST-052`; HOLD for contract/schema/public API/runtime changes until separate PLAN/Gate C evidence.

**Evidence:**

- ST-052 is bounded to fixture reference, eval runner generalization, privacy-safe report generation, and tests.
- ST-052 has no contract/schema/version/public API impact.
- The initiative already defines later decisions for first-class `reject`, non-executing `confirm`, blocked `answer`, and plural shopping posture.
- Contract governance and ADR-001 require a dedicated workpack before any schema/version mutation.

**Rationale:**

Gate B can approve the first implementation slice because fixture strategy, privacy/report redaction strategy, allowed paths, validation commands, and stop conditions are explicit. It cannot approve contract or runtime behavior changes yet.

**Stop conditions before broader APPLY:**

- Any edit to `contracts/**`, `contracts/schemas/**`, `contracts/VERSION`, public API, existing fixtures, or HomeTusk files stops ST-052.
- Any first-class `reject`, `confirm`, `answer`, or changed `/v1/decide` semantics requires contract governance and a separate workpack.
- Any runtime edit in `graphs/**`, `routers/**`, `app/**`, `agent_registry/**`, `agent_runner/**`, or `llm_policy/**` requires a later PLAN/Gate C decision.

## Artifact Gate Summary

### Contract Gate

| Field | Decision |
| --- | --- |
| Impact | ST-052: none |
| Affected contracts | None for ST-052 |
| ADR-001 classification | No schema, version, public API, or DecisionDTO semantic change |
| Version decision | No version bump |
| Fixtures/tests required | Eval runner unit tests only; no contract fixtures |
| Gate result | GO for ST-052 eval tooling; HOLD for contract mutation |

### ADR / Diagram Gate

| Field | Decision |
| --- | --- |
| Architecture impact | None for ST-052 |
| ADR impact | None for ST-052; ADR-009 remains baseline |
| Diagram impact | None for ST-052 |
| Required artifacts | No new ADR/diagram for ST-052 |
| Index updates | None |
| Gate result | NO ARTIFACT CHANGE REQUIRED for ST-052 |

## Decomposition

| Story | Title | Status | Gate role |
| --- | --- | --- | --- |
| ST-052 | Expanded 50-scenario fixture reference and eval runner | Done | First implementation slice; no contract/runtime changes |
| ST-053 | Contract posture decision for `reject`, `confirm`, `answer`, and shopping plurality | Done | Contract artifact gate before schema work |
| ST-054 | Contract-governed schema implementation for first-class `reject` and non-executing `confirm` | Done | Contract/schema work after ST-053 Gate D and Gate C |
| ST-055 | Narrow planner runtime adaptation from 50-scenario blockers | Done | Gate D GO after zero-blocker eval |
| ST-056 | Review, closure evidence, and HomeTusk handoff | Done | Final Gate D evidence for the initiative |

## ST-052 Gate C Decision — GO

**Decision:** GO for ST-052 APPLY.

**Evidence:**

- Workpack exists at `docs/planning/workpacks/ST-052/workpack.md`.
- PLAN report exists at `docs/planning/workpacks/ST-052/plan-report.md`.
- HomeTusk expanded v1 fixture suite exists read-only at `C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/provider-domain-planner-v1-acceptance/expanded-golden-scenarios-v1`.
- PLAN confirms that ST-052 can proceed by changing only eval tooling, eval tests, and ST-052 planning/evidence artifacts.
- PLAN confirms no contract/schema/version/public API/runtime/HomeTusk changes are required.

**Rationale:**

ST-052 creates the evidence mechanism needed before any contract or runtime decisions. It preserves initiative scope, keeps HomeTusk read-only, and records blocker counts instead of treating eval confidence as runtime permission.

**Approved paths:**

- `scripts/evaluate_domain_planner_seed.py`
- `tests/test_domain_planner_seed_eval.py`
- `docs/planning/workpacks/ST-052/**`
- `docs/planning/epics/EP-017/**`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md`

**Forbidden paths:**

- `contracts/**`
- `contracts/schemas/**`
- `contracts/VERSION`
- `graphs/**`
- `routers/**`
- `app/**`
- `agent_registry/**`
- `agent_runner/**`
- `llm_policy/**`
- HomeTusk repository files

## Next Step

ST-054 must create a dedicated contract-governed schema/version workpack for first-class `reject` and non-executing `confirm`. ST-055 should remain HOLD until ST-054 and a dedicated runtime PLAN decide whether current-schema or updated-contract planner behavior should address the observed 50-scenario blockers.

## ST-052 Gate D Decision — GO for Eval Tooling; HOLD for Initiative Acceptance

**Decision:** GO for ST-052 closure. HOLD for initiative acceptance and runtime/product readiness.

**Evidence:**

- Workpack exists at `docs/planning/workpacks/ST-052/workpack.md`.
- PLAN report exists at `docs/planning/workpacks/ST-052/plan-report.md`.
- Review report exists at `docs/planning/workpacks/ST-052/review-report.md`.
- 50-scenario eval report exists at `docs/planning/workpacks/ST-052/local-50-scenario-eval-report.json`.
- Validation passed:
  - `$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 -m pytest tests/test_domain_planner_seed_eval.py -v`: 5 passed.
  - `$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 scripts/evaluate_domain_planner_seed.py --source-dir C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/provider-domain-planner-v1-acceptance/expanded-golden-scenarios-v1 --check-no-raw-text --output docs/planning/workpacks/ST-052/local-50-scenario-eval-report.json`: pass.
  - `git diff --check`: pass with LF-to-CRLF warnings only.
- Local 50-scenario eval metrics: 50 evaluated, 50 schema-valid, 43 outcome matches, 11 intent matches, 1 unsupported auto-execute, 0 cross-household references, 7 blocker failure scenarios.
- Failure bucket counts: `wrong_outcome=7`, `wrong_intent=39`, `item_boundary_loss=5`, `unsupported_auto_execute=1`.
- No HomeTusk files were edited or copied.
- No contract, schema, contract version, public API, runtime planner, rollout/config, or existing fixture files were changed.
- `--check-no-raw-text` passed for the generated report.

**Rationale:**

ST-052 delivered the evidence mechanism required by the current initiative and removed a hidden `PyYAML` dependency by adding an in-runner fallback parser for the fixture YAML subset. The generated evidence does not satisfy initiative acceptance because blocker failure tolerance is zero and the current provider has 7 blocker failure scenarios.

**Residual risks:**

- First-class `reject` and non-executing `confirm` remain contract posture decisions.
- At least one unsupported scenario currently auto-executes and must be addressed before any acceptance claim.
- Multi-item boundary behavior still has failure buckets in the expanded suite.
- Intent match quality is low in the 50-scenario suite and needs triage before runtime acceptance.

**Next required gate:**

ST-053 contract posture workpack, followed by a dedicated ST-055 runtime PLAN only if contract posture permits current-schema adaptation.

## ST-053 Gate C Decision — GO

**Decision:** GO for docs-only ST-053 APPLY.

**Evidence:**

- HomeTusk contract posture states first-class `reject` is required before runtime integration.
- HomeTusk contract posture states first-class non-executing `confirm` is required before assignment, reschedule, task-shopping linkage, and batch planning UX.
- HomeTusk contract posture states `answer` is required before status/query UX, but answer must be grounded in HomeTusk read models.
- HomeTusk contract posture states direct plural `add_shopping_items` is not required for the next provider eval step if repeated singular actions preserve item boundaries.
- Current provider `DecisionDTO` schema has no first-class `reject`, `confirm`, or `answer` actions.
- ADR-001 requires contract governance, semver, fixtures, and validation for schema/action changes.

**Rationale:**

ST-053 can make the contract posture explicit without mutating schemas. This is the required artifact gate before any ST-054 contract/schema APPLY.

**Approved paths:**

- `docs/planning/epics/EP-017/domain-planner-v1-contract-posture.md`
- `docs/planning/epics/EP-017/stories/ST-053-contract-posture.md`
- `docs/planning/workpacks/ST-053/**`
- `docs/planning/epics/EP-017/epic.md`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md`

**Forbidden paths:**

- `contracts/**`
- `contracts/schemas/**`
- `contracts/VERSION`
- `graphs/**`
- `routers/**`
- `app/**`
- `agent_registry/**`
- `agent_runner/**`
- `llm_policy/**`
- HomeTusk repository files

## ST-053 Gate D Decision — GO for Contract Posture; HOLD for Schema/Runtime APPLY

**Decision:** GO for ST-053 closure. HOLD for contract schema mutation and runtime adaptation until separate ST-054/ST-055 workpacks.

**Evidence:**

- Contract posture note exists at `docs/planning/epics/EP-017/domain-planner-v1-contract-posture.md`.
- Workpack exists at `docs/planning/workpacks/ST-053/workpack.md`.
- PLAN report exists at `docs/planning/workpacks/ST-053/plan-report.md`.
- Review report exists at `docs/planning/workpacks/ST-053/review-report.md`.
- Validation passed:
  - `rg -n "ST-053|first-class reject|non-executing confirm|answer remains blocked|repeated singular" docs/planning/epics/EP-017 docs/planning/workpacks/ST-053 docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md`: pass.
  - `git diff --check`: pass with LF-to-CRLF warnings only.
- No HomeTusk files were edited or copied.
- No contract, schema, contract version, public API, runtime planner, rollout/config, or existing fixture files were changed.

**Posture decisions:**

| Area | Decision |
| --- | --- |
| `reject` | Implement first-class provider `reject` through dedicated ST-054 contract-governed schema/version work before HomeTusk runtime acceptance. |
| `confirm` | Implement first-class non-executing provider `confirm` through dedicated ST-054 contract-governed schema/version work before assignment/linkage/reschedule/batch UX acceptance. |
| `answer` | Keep blocked until HomeTusk answer/read-model contract governance starts; do not include in ST-054. |
| `add_shopping_items` | Keep repeated singular `propose_add_shopping_item` actions for the next provider eval step; item-boundary failures should be handled as planner/eval behavior, not as immediate plural action schema work. |

**Rationale:**

ST-053 resolves the ambiguity that blocked broader APPLY. The next implementation authority must be a contract workpack for `reject` and `confirm`; runtime adaptation remains HOLD until the contract path is decided and approved.

**Next required gate:**

ST-054 contract/schema workpack with ADR-001 semver classification, schema edits, fixtures, version decision, validation commands, rollback, and Gate C before APPLY.

## ST-054 Gate C Decision — GO

**Decision:** GO for ST-054 contract/schema APPLY.

**Evidence:**

- ST-053 Gate D is GO and explicitly opens ST-054 contract-governed work for first-class `reject` and non-executing `confirm`.
- Current `DecisionDTO` has no first-class `reject` or `confirm`.
- ADR-001 allows adding new optional fields or action values as MINOR only when consumers safely handle unknown actions.
- ADR-009 requires contract governance before first-class `reject` or `confirm`.
- Current HomeTusk posture requires first-class `reject` before runtime integration and non-executing `confirm` before assignment/linkage/reschedule/batch UX.
- PLAN confirms ST-054 can avoid `status` enum changes by adding first-class actions and optional `decision_outcome`.

**Approved contract design:**

| Area | Decision |
| --- | --- |
| Semver | MINOR: `2.0.0 -> 2.1.0` |
| `DecisionDTO.action` | Add `reject` and `confirm` |
| `DecisionDTO.decision_outcome` | Add optional enum: `execute`, `clarify`, `reject`, `confirm` |
| `DecisionDTO.status` | Keep existing enum unchanged: `ok`, `clarify`, `error` |
| `reject` payload | Non-mutating payload with stable code and user-safe reason |
| `confirm` payload | Non-mutating pending confirmation payload with summary, reasons, proposed actions, expiry, and confirmation id |
| `answer` | Remains blocked; no schema field/action in ST-054 |
| Plural shopping | No direct plural action in ST-054 |

**Approved paths:**

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
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.md`

**Forbidden paths:**

- `graphs/**`
- `routers/**`
- `app/services/**`
- `agent_registry/**`
- `agent_runner/**`
- `llm_policy/**`
- HomeTusk repository files
- Production rollout/config files

**Stop conditions:**

- Need to add provider `answer`.
- Need to change or remove existing required fields.
- Need to alter `start_job`, `propose_*`, or `clarify` semantics.
- Need runtime planner behavior changes.

## ST-054 Gate D Decision — GO for Contract Schema; HOLD for Runtime Acceptance

**Decision:** GO for ST-054 closure. HOLD for runtime acceptance and 50-scenario initiative acceptance until ST-055.

**Evidence:**

- Workpack exists at `docs/planning/workpacks/ST-054/workpack.md`.
- PLAN report exists at `docs/planning/workpacks/ST-054/plan-report.md`.
- Review report exists at `docs/planning/workpacks/ST-054/review-report.md`.
- `contracts/VERSION` is `2.1.0`.
- `DecisionDTO` schema supports first-class `reject`, first-class non-executing `confirm`, and optional `decision_outcome`.
- `CommandDTO.capabilities` accepts `reject` and `confirm`.
- Contract fixtures include valid `reject`, valid `confirm`, and invalid confirm-without-confirmation-id cases.
- Baseline schemas under `contracts/schemas/.baseline/` were updated.
- API boundary omits optional `None` response fields via `response_model_exclude_none=True`.
- Validation passed:
  - `$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 skills/contract-checker/scripts/validate_contracts.py`: pass.
  - `$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 skills/schema-bump/scripts/check_breaking_changes.py`: pass.
  - Explicit HEAD-vs-current breaking checks for `decision.schema.json` and `command.schema.json`: pass.
  - `$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 -m pytest tests/test_contracts.py tests/test_api_models.py tests/test_api_decide.py tests/test_api_versioned.py tests/test_health_ready.py tests/test_domain_planner_v1_corridor.py -v`: 32 passed, 1 warning.
  - `$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 scripts/evaluate_domain_planner_seed.py --source-dir C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/provider-domain-planner-v1-acceptance/expanded-golden-scenarios-v1 --check-no-raw-text --output docs/planning/workpacks/ST-052/local-50-scenario-eval-report.json`: pass.
  - `git diff --check`: pass with LF-to-CRLF warnings only.
- Regenerated 50-scenario eval metrics under schema `2.1.0`: 50 evaluated, 50 schema-valid, 43 outcome matches, 11 intent matches, 1 unsupported auto-execute, 0 cross-household references, 7 blocker failure scenarios.
- No HomeTusk files were edited or copied.
- No runtime planner, rollout/config, provider `answer`, or direct plural shopping action was added.

**Rationale:**

ST-054 satisfies the contract governance slice needed before runtime adaptation. The schema change is additive and preserves existing status values; new runtime behavior still requires ST-055 because schema support alone does not change planner decisions.

**Residual risks:**

- Runtime still emits current behavior and does not yet use first-class `reject` / `confirm`.
- The 50-scenario suite still has 7 blocker failure scenarios.
- One unsupported scenario still auto-executes in current runtime behavior.
- Item-boundary failures remain planner/eval behavior risks.

**Next required gate:**

ST-055 runtime planner adaptation workpack and PLAN, bounded to the 50-scenario blocker evidence and the new `2.1.0` contract.

## ST-055 Gate C Decision — GO

**Decision:** GO for ST-055 runtime APPLY.

**Evidence:**

- Workpack exists at `docs/planning/workpacks/ST-055/workpack.md`.
- PLAN report exists at `docs/planning/workpacks/ST-055/plan-report.md`.
- ST-054 Gate D is GO and `contracts/VERSION` is `2.1.0`.
- The 50-scenario eval report identifies 7 blocker scenario IDs: `HT-GS-003`, `HT-GS-008`, `HT-GS-015`, `HT-GS-043`, `HT-GS-046`, `HT-GS-048`, `HT-GS-049`.
- Current blocker buckets are `wrong_outcome=7`, `unsupported_auto_execute=1`, `item_boundary_loss=5`, `cross_household_reference=0`.
- PLAN confirms the blockers can be addressed without new contract/schema/version changes.
- PLAN confirms HomeTusk remains read-only and raw scenario text must not be copied into planning/review artifacts.

**Rationale:**

Runtime adaptation is now required because initiative acceptance requires zero blocker failure scenarios and schema support alone does not change planner behavior. The approved APPLY is bounded to first-class non-executing `reject`, simple task recognition, grounded shopping item-boundary preservation, and eval classification alignment.

**Approved paths:**

- `graphs/core_graph.py`
- `scripts/evaluate_domain_planner_seed.py`
- `tests/test_domain_planner_v1_corridor.py`
- `tests/test_domain_planner_seed_eval.py`
- `docs/diagrams/domain-planner-v1-flow.puml`
- `docs/planning/epics/EP-017/**`
- `docs/planning/workpacks/ST-055/**`
- `docs/planning/workpacks/ST-052/local-50-scenario-eval-report.json`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.md`

**Forbidden paths:**

- HomeTusk repository files
- `contracts/**`
- `contracts/schemas/**`
- `contracts/VERSION`
- `app/models/api_models.py`
- `app/routes/**`
- `agent_registry/**`
- `agent_runner/**`
- `llm_policy/**`
- production rollout/config files

**Risks accepted:**

- First-class `reject` becomes runtime-visible for unsupported/cross-household commands, relying on ST-054 schema/API compatibility.
- Some non-blocker intent mismatch buckets may remain after ST-055 if outcomes are safe and non-executing.
- Diagram update is limited to stale label correction; no structural flow change is introduced.

**Stop conditions:**

- Need to add provider `answer`, new schema fields, direct plural shopping action, or a contract version bump.
- Need to mutate HomeTusk files or implement HomeTusk backend/mobile/runtime.
- Need to execute assignment, reschedule, completion, payment, device control, or external order actions.

## ST-055 Gate D Decision — GO for Runtime Adaptation

**Decision:** GO for ST-055 closure. GO for zero-blocker provider eval evidence.

**Evidence:**

- Workpack exists at `docs/planning/workpacks/ST-055/workpack.md`.
- PLAN report exists at `docs/planning/workpacks/ST-055/plan-report.md`.
- Review report exists at `docs/planning/workpacks/ST-055/review-report.md`.
- Runtime changes are bounded to deterministic helpers in `graphs/core_graph.py`.
- Eval alignment is bounded to `scripts/evaluate_domain_planner_seed.py`.
- Diagram label update exists at `docs/diagrams/domain-planner-v1-flow.puml`.
- Validation passed:
  - `$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 -m pytest tests/test_domain_planner_v1_corridor.py tests/test_domain_planner_seed_eval.py tests/test_contracts.py tests/test_api_decide.py tests/test_api_models.py -v`: 33 passed, 1 warning.
  - `$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 -m pytest tests/ -v`: 346 passed, 4 skipped, 1 warning.
  - `$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 skills/contract-checker/scripts/validate_contracts.py`: pass.
  - `$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 skills/schema-bump/scripts/check_breaking_changes.py`: pass.
  - `$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 -m skills.release_sanity`: pass.
  - `$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 scripts/evaluate_domain_planner_seed.py --source-dir C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/provider-domain-planner-v1-acceptance/expanded-golden-scenarios-v1 --check-no-raw-text --output docs/planning/workpacks/ST-052/local-50-scenario-eval-report.json`: pass.
  - `git diff --check`: pass with LF-to-CRLF warnings only.
- Final 50-scenario eval metrics: 50 evaluated, 50 schema-valid, 50 outcome matches, 20 intent matches, 0 unsupported auto-execute, 0 cross-household references, 0 blocker failure scenarios.
- Remaining failure buckets are non-blockers: `wrong_intent=30`, `item_boundary_loss=2`.
- No HomeTusk files were edited or copied.
- No contract/schema/version files were changed by ST-055.
- No provider `answer`, direct plural shopping action, HomeTusk runtime, mobile/backend/API integration, production rollout, or broad planner execution was added.

**Rationale:**

ST-055 satisfies the initiative acceptance requirement that blocker failure count be zero before final Gate D. The runtime adaptation remains inside the narrow provider corridor: clear simple task creation and grounded shopping may execute as provider proposals, unsupported/cross-household categories reject without mutation, and confirm/answer/broad automation categories remain non-executing.

**Residual risks:**

- Non-blocker intent mismatch remains visible for HomeTusk review.
- Runtime `confirm` emission remains future work; ST-054 only provides schema support and ST-055 keeps confirm-required categories non-executing.
- Provider `answer` remains blocked until HomeTusk read-model contract governance starts.

## ST-056 Gate C/D Decision — GO for Closure and Handoff

**Decision:** GO for docs-only ST-056 closure. GO for provider-side initiative handoff.

**Evidence:**

- ST-056 story exists at `docs/planning/epics/EP-017/stories/ST-056-review-closure-hometusk-handoff.md`.
- Workpack exists at `docs/planning/workpacks/ST-056/workpack.md`.
- Review report exists at `docs/planning/workpacks/ST-056/review-report.md`.
- HomeTusk handoff exists at `docs/planning/workpacks/ST-056/hometusk-handoff.md`.
- ST-055 review is GO.
- The regenerated eval report is privacy-safe and has zero blocker failures.
- Handoff summarizes 50-scenario results, contract decisions, privacy posture, residual risks, and next recommended HomeTusk action without raw scenario text.

**Rationale:**

The initiative requires a provider-side evidence package suitable for HomeTusk review. ST-056 makes the closure explicit and preserves the boundary that HomeTusk runtime/mobile/backend/API implementation remains out of scope.

**Residual risks:**

- HomeTusk must still decide whether to accept the provider evidence.
- Any runtime integration, confirmation UX, guardrail/audit behavior, and product rollout must be governed by a separate HomeTusk-owned initiative.

## Final Initiative Gate D Decision — GO for Provider-Side Closure

**Decision:** GO. The provider-side initiative `INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval` is Done.

**Acceptance evidence:**

| Criterion | Result |
| --- | --- |
| Expanded 50-scenario suite consumed/referenced | GO |
| Deterministic eval runner evaluates all 50 scenarios | GO |
| Per-scenario and aggregate report exists | GO |
| Failure bucket counts and blocker count recorded | GO |
| Planner/schema/decision versions, flags, source, command recorded | GO |
| No raw scenario text in planning/review summaries | GO |
| Blocker failure count is zero | GO |
| First-class `reject` posture explicit | GO; schema and runtime support |
| Non-executing `confirm` posture explicit | GO; schema support, runtime emission deferred |
| `answer` status explicit | GO; blocked |
| ASR boundary preserved | GO |
| No HomeTusk files modified | GO |
| No production rollout/config change | GO |
| Existing provider tests pass | GO |
| HomeTusk handoff note produced | GO |

**Final metrics:**

| Metric | Value |
| --- | --- |
| Total scenarios | 50 |
| Evaluated scenarios | 50 |
| Schema-valid decisions | 50 |
| Outcome matches | 50 |
| Intent matches | 20 |
| Unsupported auto-execute | 0 |
| Cross-household references | 0 |
| Blocker failure scenarios | 0 |
| Remaining non-blocker buckets | `wrong_intent=30`, `item_boundary_loss=2` |

**Recommendation:**

HomeTusk should review `docs/planning/workpacks/ST-056/hometusk-handoff.md` and decide whether to open a separate runtime integration initiative. AI Platform should not start HomeTusk runtime/mobile/backend/API work from this provider initiative.
