# INIT-2026Q3 Domain Planner v1 Execution Notes

**Status:** Done; Gate A GO; Gate B GO; ST-048 Gate D GO; ST-049 Gate D GO; ST-050 Gate D GO; ST-051 Gate D GO
**Date:** 2026-06-15
**Initiative:** `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.md`
**Roadmap:** `docs/planning/strategy/roadmap.md`
**Delegation:** Human gates for this initiative are delegated to Codex, but every GO / HOLD / NO-GO decision must be recorded with evidence, risks, and rationale.

---

## Intake Summary

| Field | Decision |
| --- | --- |
| Request type | Mixed delivery initiative: planning, artifact gate, future runtime, future eval, privacy, traceability |
| Scope anchor | `INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor` |
| Current workflow step | `intake -> planning -> artifact gate -> workpack -> PLAN -> Human Gate C -> APPLY -> read-only review gate -> Human Gate D complete` |
| Risk | High, because the initiative touches decision flow, provider/consumer boundaries, eval evidence, and privacy posture |
| Primary boundary | AI Platform remains a stateless provider; HomeTusk remains execution, guardrail, audit, and final acceptance authority |
| Next concrete work | HomeTusk-side review / future provider contract workpack only if requested |

## Sources Read

### Current Repository

| Artifact | Path |
| --- | --- |
| Active rules | `AGENTS.md`, `CODEX.md`, `docs/CODEX-WORKFLOW.md` |
| Product goal | `docs/planning/strategy/product-goal.md` |
| Roadmap | `docs/planning/strategy/roadmap.md` |
| MVP scope | `docs/planning/releases/MVP.md` |
| DoR / DoD | `docs/_governance/dor.md`, `docs/_governance/dod.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.md` |
| Contract schemas | `contracts/schemas/command.schema.json`, `contracts/schemas/decision.schema.json` |
| Contract version | `contracts/VERSION` (`2.0.0`) |
| Contract governance | `docs/contracts/CONTRACT-GOVERNANCE-RUNBOOK.md`, `docs/adr/ADR-001-contract-versioning-compatibility-policy.md` |
| Architecture ADRs | `docs/adr/ADR-000-ai-platform-intent-decision-engine.md`, `docs/adr/ADR-004-partial-trust-corridor.md`, `docs/adr/ADR-006-multi-item-internal-model.md`, `docs/adr/ADR-008-asr-cloudru-whisper-mvp.md` |
| Existing eval/sanity tools | `skills/graph-sanity/scripts/run_graph_suite.py`, `skills/quality-eval/scripts/evaluate_golden.py` |

### HomeTusk Read-Only Inputs

| Artifact | Evidence |
| --- | --- |
| Repository path | `C:/Users/user/Documents/projects/hometusk/hometusk` |
| Source revision read | `d924c631c80895995c65f22bec6f77dc0a0347b7` |
| Worktree note | One unrelated dirty HomeTusk file was present outside the artifact package: `docs/planning/initiatives/INIT-2026Q3-voice-command-chat-mvp.md` |
| Artifact package | `docs/research/ai-command-capabilities/domain-planner-v1-gate/**` |
| Package status | Accepted artifact gate package, recommendation `LIMITED-GO`, dated 2026-06-15 |

Read-only HomeTusk files consumed:

- `domain-planner-v1-gate/README.md`
- `decision-action-taxonomy-accepted-v0.md`
- `natural-command-contract-v0-draft.md`
- `golden-scenarios-fixtures-v0/README.md`
- `golden-scenarios-fixtures-v0/context-fixtures-v0.yaml`
- `golden-scenarios-fixtures-v0/golden-scenarios-v0.yaml`
- `eval-rubric-v0.md`
- `privacy-and-retention-questions.md`
- `provider-planner-readiness-checklist.md`
- `hometusk-ai-platform-integration-doc-drift.md`
- `provider-initiative-brief.md`

## Flags

| Flag | Value | Rationale |
| --- | --- | --- |
| `contract_impact` | `tbd-gated` | First provider slice must prefer current schema mapping; any first-class `reject`, `confirm`, `planner_version`, or new capability shape requires contract governance. |
| `adr_needed` | `yes-before-runtime` | Domain Planner v1 changes decision-flow boundaries and provider planner semantics. |
| `diagrams_needed` | `yes-before-runtime` | The provider flow and HomeTusk boundary must be visible before APPLY. |
| `security_sensitive` | `yes` | The initiative governs prompt/response retention, raw text handling, raw audio exclusion, and cross-household leakage. |
| `traceability_critical` | `yes` | Eval output, trace ids, decision ids, schema/decision/planner versions, and feature flags are acceptance evidence. |
| `cross_repo` | `read-only-inputs` | HomeTusk artifacts are acceptance inputs only; commits stay in the current provider repository. |

## Gate A Decision — GO

**Decision:** GO for provider-side initiative scope.

**Evidence:**

- Roadmap initially marked the Domain Planner v1 narrow household corridor as CURRENT; after ST-051 Gate D it is recorded as Completed.
- Initiative states AI Platform must be stateless and must not mutate HomeTusk state.
- HomeTusk package recommendation is `LIMITED-GO`, not broad GO.
- HomeTusk package says provider follow-up may consume taxonomy, seed fixtures, eval rubric, privacy questions, readiness checklist, and provider brief.

**Rationale:**

Gate A criteria are satisfied: the initiative remains provider-side, HomeTusk remains read-only input, the narrow corridor is preserved, and production multi-agent planner remains out of scope.

**Risks accepted:**

- Current provider schema does not have first-class `reject` or `confirm`.
- HomeTusk seed coverage is only 10 scenarios and is not enough for final Domain Planner acceptance.
- Integration drift exists around reject semantics and shopping action boundary.

## Gate B Decision — GO for Provider Planning, HOLD for Runtime APPLY

**Decision:** GO for decomposition, artifact-gate workpack, and read-only PLAN preparation. HOLD for runtime APPLY until ST-048 closes the provider artifact gate and a later workpack passes Gate C.

**Evidence:**

- EP-016 decomposes the initiative into bounded provider-native stories.
- ST-048 is a docs/artifact workpack that records provider mapping, ADR/diagram impact, and privacy posture before runtime work.
- Current `decision.schema.json` supports `start_job`, `propose_create_task`, `propose_add_shopping_item`, and `clarify`, including multiple proposed actions.
- Current `decision.schema.json` does not support first-class `reject`, `confirm`, `answer`, or `add_shopping_items` as a direct action enum.
- HomeTusk readiness checklist requires fixture consumption, taxonomy mapping, deterministic eval output, and privacy/retention answers before Provider Gate C.

**Rationale:**

Gate B can approve planning because the work is decomposed, contract impact is explicitly gated, fixture strategy is explicit, and privacy/retention work is included. Gate B cannot approve runtime APPLY yet because reject/confirm mapping, provider ADR/diagram, and fixture import/eval shape must be documented first.

**Stop conditions before runtime APPLY:**

- Any edit to `contracts/**`, `contracts/schemas/**`, `contracts/VERSION`, public API, or fixtures requires a dedicated contract workpack.
- Any first-class `reject`, `confirm`, or `answer` provider output requires contract governance and ADR/index updates.
- Any runtime work in `graphs/**`, `routers/**`, `app/**`, `agent_registry/**`, `agent_runner/**`, or `llm_policy/**` requires a later workpack, Codex PLAN, delegated Gate C GO, APPLY, read-only review, and Gate D.
- No HomeTusk files may be edited by this initiative.

## Artifact Gate Summary

### Contract Gate

| Field | Decision |
| --- | --- |
| Impact | `tbd-gated`; first slice targets no schema edit |
| Affected contracts | Potentially `CommandDTO`, `DecisionDTO`, and `/v1/decide` semantics if first-class outcomes are introduced |
| ADR-001 classification | Current-schema mapping is no contract impact; optional metadata/action additions are non-breaking only if consumers safely handle them; semantic changes or required fields are breaking |
| Version decision | No version bump for ST-048; later contract workpack must decide semver before schema edits |
| Fixtures/tests required | Contract fixtures only if schemas change; provider eval fixtures required for planner acceptance |
| Gate result | GO for mapping work; HOLD for contract mutation |

### ADR / Diagram Gate

| Field | Decision |
| --- | --- |
| Architecture impact | Yes, Domain Planner v1 affects decision flow and provider/consumer boundaries |
| ADR impact | ADR-lite or full ADR required before runtime APPLY |
| Diagram impact | Provider flow diagram required before runtime APPLY |
| Required artifacts | Provider mapping note, ADR/index update, diagram/index update, privacy/retention posture |
| Gate result | ARTIFACT CHANGE REQUIRED BEFORE RUNTIME WORKPACK |

## Decomposition

| Story | Title | Status | Gate role |
| --- | --- | --- | --- |
| ST-048 | Provider mapping, ADR, diagram, and privacy posture | Done | Provider artifact gate before runtime |
| ST-049 | HomeTusk seed fixture import/reference and deterministic eval runner | Done | Establish eval evidence and fixture source metadata |
| ST-050 | Domain Planner v1 narrow corridor implementation/adaptation | Done | Runtime implementation after ST-048/ST-049 and Gate C |
| ST-051 | Review gate, closure evidence, and HomeTusk handoff | Done | Gate D evidence and initiative closure |

## Next Step

Provider-side initiative closure is complete. HomeTusk product acceptance, scenario expansion, production rollout, or first-class outcome contract work remain separate future initiatives/workpacks.

## ST-048 Gate D Decision — GO

**Decision:** GO for ST-048 artifact scope only.

**Evidence:**

- Provider mapping note exists at `docs/planning/epics/EP-016/domain-planner-v1-provider-mapping.md`.
- ADR exists and is indexed: `docs/adr/ADR-009-domain-planner-v1-narrow-corridor.md`, `docs/_indexes/adr-index.md`.
- Diagram exists and is indexed: `docs/diagrams/domain-planner-v1-flow.puml`, `docs/_indexes/diagrams-index.md`.
- Privacy/retention posture exists at `docs/guides/domain-planner-v1-privacy-retention.md`.
- ST-048 review report is `docs/planning/workpacks/ST-048/review-report.md`.
- Validation found no raw HomeTusk scenario text in ST-048 reports/artifacts.
- No runtime, contract, schema, fixture, test, public API, or HomeTusk file was changed.

**Rationale:**

ST-048 closes the provider artifact gate required before runtime planning. It does not complete the initiative and does not approve ST-050 runtime APPLY.

**Next required gate:**

ST-049 must define fixture import/reference and deterministic eval evidence before any runtime workpack can reach Gate C.

## ST-049 Gate C Decision — GO

**Decision:** GO for ST-049 eval runner APPLY only.

**Evidence:**

- Workpack exists at `docs/planning/workpacks/ST-049/workpack.md`.
- PLAN report exists at `docs/planning/workpacks/ST-049/plan-report.md`.
- PLAN confirmed reference-only HomeTusk fixture access and no raw fixture copying.
- PLAN confirmed no runtime, contract, schema, public API, existing fixture, or HomeTusk edits are required for ST-049.
- `yaml` import is available in the current validation environment.

**Rationale:**

ST-049 can establish provider eval evidence without broadening scope or mutating runtime behavior. This GO does not approve ST-050 runtime APPLY.

## ST-049 Gate D Decision — GO

**Decision:** GO for ST-049 closure.

**Evidence:**

- Eval runner exists at `scripts/evaluate_domain_planner_seed.py`.
- Unit tests exist at `tests/test_domain_planner_seed_eval.py`.
- Review report exists at `docs/planning/workpacks/ST-049/review-report.md`.
- Local seed eval report exists at `docs/planning/workpacks/ST-049/local-seed-eval-report.json`.
- Validation passed:
  - `python3 -m pytest tests/test_domain_planner_seed_eval.py -v`: 4 passed.
  - `python3 scripts/evaluate_domain_planner_seed.py --source-dir C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/domain-planner-v1-gate/golden-scenarios-fixtures-v0 --check-no-raw-text --output docs/planning/workpacks/ST-049/local-seed-eval-report.json`: pass.
  - `python3 -m pytest tests/test_quality_eval.py -v`: 6 passed.
  - `git diff --check`: pass with LF-to-CRLF warnings only.
- Local seed eval metrics: 10 evaluated, 10 schema-valid, 8 outcome matches, 3 intent matches, 1 unsupported auto-execute, 0 cross-household references, 2 blocker failure scenarios.
- No HomeTusk files were edited or copied.
- No runtime, contract, schema, public API, or existing fixture files were changed.

**Rationale:**

ST-049 delivered the evaluation mechanism and privacy-safe evidence boundary. The current provider behavior is not yet runtime-accepted; the blocker failures are scoped to ST-050/ST-051.

**Next required gate:**

ST-050 must receive a dedicated runtime workpack, read-only PLAN, delegated Gate C decision, APPLY, and read-only review before any runtime acceptance claim.

## ST-050 Gate C Decision — GO

**Decision:** GO for current-schema ST-050 runtime APPLY only.

**Evidence:**

- Workpack exists at `docs/planning/workpacks/ST-050/workpack.md`.
- PLAN report exists at `docs/planning/workpacks/ST-050/plan-report.md`.
- ST-048 closed provider mapping, ADR, diagram, and privacy posture before runtime work.
- ST-049 closed reference-only seed eval runner and baseline evidence.
- PLAN confirmed ST-050 can proceed without contract/schema/version/public API changes.
- Approved runtime paths are limited to `graphs/core_graph.py` and `routers/v2.py`; approved test path is `tests/test_domain_planner_v1_corridor.py`.
- Validation commands and rollback are recorded in the ST-050 workpack.

**Rationale:**

ST-050 can address seed blocker failures and item boundary loss through current-schema deterministic guardrails. This preserves the narrow corridor and does not approve first-class `reject`, `confirm`, `answer`, direct plural shopping actions, HomeTusk writes, or production rollout changes.

**Stop conditions:**

- Any need to edit `contracts/**`, `contracts/schemas/**`, `contracts/VERSION`, public API, HomeTusk files, existing fixtures, or production rollout config stops APPLY.
- Any need for first-class `reject`, `confirm`, `answer`, or changed `/v1/decide` semantics stops APPLY and requires a contract workpack.

## ST-050 Gate D Decision — GO

**Decision:** GO for ST-050 runtime adaptation closure.

**Evidence:**

- Runtime changes stayed inside `graphs/core_graph.py` and `routers/v2.py`.
- Test coverage was added at `tests/test_domain_planner_v1_corridor.py`.
- Review report exists at `docs/planning/workpacks/ST-050/review-report.md`.
- Regenerated seed eval report exists at `docs/planning/workpacks/ST-049/local-seed-eval-report.json`.
- Validation passed:
  - `python3 -m pytest tests/test_domain_planner_v1_corridor.py -v`: 7 passed.
  - `python3 -m pytest tests/test_multi_item_e2e.py tests/test_planner_multi_item.py tests/test_graph_execution.py tests/test_api_decide.py -v`: 14 passed.
  - `python3 scripts/evaluate_domain_planner_seed.py --source-dir C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/domain-planner-v1-gate/golden-scenarios-fixtures-v0 --check-no-raw-text --output docs/planning/workpacks/ST-049/local-seed-eval-report.json`: pass.
  - `python3 -m pytest tests/test_domain_planner_seed_eval.py -v`: 4 passed.
  - `python3 -m pytest tests/ -v`: 336 passed, 4 skipped.
  - `git diff --check`: pass with LF-to-CRLF warnings only.
- Local seed eval metrics after ST-050: 10 evaluated, 10 schema-valid, 10 outcome matches, 0 unsupported auto-execute, 0 cross-household references, 0 blocker failure scenarios.
- Privacy scan over ST-050/ST-049 planning and eval artifacts found 0 raw fixture text matches.
- No HomeTusk files were edited or copied.
- No contract, schema, contract version, public API, or existing fixture files were changed.

**Rationale:**

ST-050 satisfies the runtime adaptation scope under current-schema mapping. The initiative is not closed yet because ST-051 must still aggregate final evidence, document residual non-blocker buckets, and prepare handoff notes.

**Next required gate:**

ST-051 must receive a dedicated closure/handoff workpack, PLAN, delegated Gate C decision, APPLY, read-only review, and Gate D before the roadmap initiative can be marked complete.

## ST-051 Gate C Decision — GO

**Decision:** GO for docs-only ST-051 closure APPLY.

**Evidence:**

- ST-048, ST-049, and ST-050 each have Gate D GO.
- Seed eval after ST-050 has 0 blocker failure scenarios.
- No contract/schema/public API/HomeTusk changes are required for closure.
- Approved paths are limited to ST-051 planning docs, the EP-016 handoff note, and roadmap/initiative/epic/story status updates.

**Rationale:**

ST-051 can close the provider-side initiative by aggregating evidence and making HomeTusk handoff boundaries explicit.

## ST-051 Gate D Decision — GO

**Decision:** GO for provider-side initiative closure.

**Evidence:**

- Workpack exists at `docs/planning/workpacks/ST-051/workpack.md`.
- Closure handoff exists at `docs/planning/epics/EP-016/domain-planner-v1-closure-handoff.md`.
- Review report exists at `docs/planning/workpacks/ST-051/review-report.md`.
- Validation passed:
  - `python3 -m pytest tests/ -v`: 336 passed, 4 skipped.
  - `python3 scripts/evaluate_domain_planner_seed.py --source-dir C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/domain-planner-v1-gate/golden-scenarios-fixtures-v0 --check-no-raw-text --output docs/planning/workpacks/ST-049/local-seed-eval-report.json`: pass.
  - `git diff --check`: pass with LF-to-CRLF warnings only.
  - Privacy scan over ST-049/ST-050/ST-051 planning and eval artifacts: 0 raw fixture text matches.
- Seed eval has 10 evaluated, 10 schema-valid, 10 outcome matches, 0 unsupported auto-execute, 0 cross-household references, and 0 blocker failure scenarios.
- No HomeTusk files were edited or copied.
- No contract, schema, contract version, public API, or existing fixture files were changed.

**Rationale:**

The provider-side initiative satisfies its acceptance criteria and gate requirements. HomeTusk product acceptance, scenario expansion to 50 cases, first-class `reject`/`confirm`/`answer` contracts, and production rollout remain separate future work.
