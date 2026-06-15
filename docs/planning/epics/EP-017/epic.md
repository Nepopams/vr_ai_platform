# EP-017: Domain Planner v1 Contract + 50-Scenario Eval Gate

**Status:** Done (Gate D GO; HomeTusk runtime integration remains separate)
**Initiative:** `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.md`
**Roadmap:** `docs/planning/strategy/roadmap.md`
**Owner:** Codex / AI Platform engineering team

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Roadmap | `docs/planning/strategy/roadmap.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.md` |
| Execution notes | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md` |
| Baseline initiative | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.md` |
| Baseline closure notes | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.execution.md` |
| MVP scope | `docs/planning/releases/MVP.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |
| Contract governance | `docs/contracts/CONTRACT-GOVERNANCE-RUNBOOK.md` |
| ADR-001 | `docs/adr/ADR-001-contract-versioning-compatibility-policy.md` |
| ADR-009 | `docs/adr/ADR-009-domain-planner-v1-narrow-corridor.md` |
| Privacy posture | `docs/guides/domain-planner-v1-privacy-retention.md` |

HomeTusk read-only source package:

```text
C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/provider-domain-planner-v1-acceptance/
```

Source revision read: `b18bfdb6f0bdbf6044ad5b986aee837dca7bf5b3`.

---

## Context

EP-016 closed the provider-side narrow Domain Planner v1 corridor. HomeTusk then kept the acceptance posture at LIMITED-GO and required deterministic provider evidence against an expanded 50-scenario suite before runtime acceptance. This epic handles that provider-side evidence and contract posture work without changing HomeTusk runtime, mobile, API, or repository files.

## Goal

Produce privacy-safe provider eval evidence for the expanded HomeTusk 50-scenario suite and make explicit contract posture decisions for `reject`, non-executing `confirm`, blocked `answer`, and shopping action plurality before any contract or runtime APPLY.

## Scope

### In scope

- Reference the expanded HomeTusk v1 fixtures with source metadata.
- Generalize the provider eval runner so it can evaluate the 50-scenario suite.
- Produce scenario-by-scenario and aggregate eval evidence without raw scenario text in planning/review summaries.
- Record blocker failure counts, failure buckets, source revision, fixture version, run command, schema versions, decision versions, and feature flags.
- Decide contract posture for first-class `reject`, non-executing `confirm`, blocked `answer`, and plural shopping actions in a later gated story.
- Optionally perform narrow planner adaptation only if eval evidence proves blockers and a later workpack approves runtime paths.

### Out of scope

- HomeTusk repository edits.
- HomeTusk `natural_command` runtime implementation.
- HomeTusk backend/OpenAPI/mobile changes.
- Direct HomeTusk state mutation.
- Direct mobile/web calls to AI Platform.
- Production rollout/config changes.
- Broad multi-agent production planner.
- Contract/schema/public API changes without a dedicated contract workpack.
- Runtime planner changes before a dedicated PLAN/Gate C decision.

## Stories

| Story ID | Title | Status | Flags |
|----------|-------|--------|-------|
| [ST-052](stories/ST-052-expanded-50-scenario-eval-runner.md) | Expanded 50-scenario fixture reference and eval runner | Done | contract_impact=no, adr_needed=none, diagrams_needed=none, security_sensitive=yes, traceability_critical=yes |
| [ST-053](stories/ST-053-contract-posture.md) | Contract posture decision for `reject`, `confirm`, `answer`, and shopping plurality | Done | contract_impact=no-edit; opens ST-054, adr_needed=none, diagrams_needed=none, security_sensitive=yes, traceability_critical=yes |
| [ST-054](stories/ST-054-reject-confirm-contract-schema.md) | Contract-governed schema implementation for first-class `reject` and non-executing `confirm` | Done | contract_impact=yes, adr_needed=covered-by-ADR-009, diagrams_needed=none-current-flow |
| [ST-055](stories/ST-055-narrow-planner-runtime-adaptation.md) | Narrow planner runtime adaptation from 50-scenario blockers | Done | contract_impact=no-new-contract, adr_needed=none, diagrams_needed=label-update, security_sensitive=yes, traceability_critical=yes |
| [ST-056](stories/ST-056-review-closure-hometusk-handoff.md) | Review, closure evidence, and HomeTusk handoff | Done | contract_impact=no, adr_needed=none, diagrams_needed=none, security_sensitive=yes, traceability_critical=yes |

## Dependencies

- HomeTusk provider acceptance package under the read-only path listed above.
- Existing `/v1/decide` route and schemas.
- Existing Domain Planner v1 narrow corridor closure from EP-016.
- Existing eval runner `scripts/evaluate_domain_planner_seed.py`.
- Contract governance docs and ADR-001.
- Privacy/retention posture from Domain Planner v1 closure.

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| 50-scenario eval exposes blocker failures | High | High | Record blocker counts and HOLD/NO-GO rather than forcing acceptance. |
| `reject_mapped_to_error` becomes product contract by accident | High | High | Keep ST-052 evidence-only; require ST-053 contract posture decision. |
| Missing `confirm` blocks assignment/linkage UX | High | High | Decide posture before runtime acceptance or schema work. |
| Raw scenario text leaks into reports | Medium | High | Use IDs, metadata, metrics, buckets; run `--check-no-raw-text`. |
| Contract changes happen without versioning | Medium | High | Stop before `contracts/**`; require dedicated contract workpack. |
| Runtime scope expands during eval work | Medium | High | ST-052 forbids `graphs/**`, `routers/**`, `app/**`, rollout/config changes. |

## Flags

- contract_impact: `no` for ST-052, `tbd-gated` for later posture/schema stories
- adr_needed: `none` for ST-052, `possible` for later contract/runtime changes
- diagrams_needed: `none` for ST-052, `possible` for later behavior/flow changes
- security_sensitive: `yes`
- traceability_critical: `yes`

## Readiness

Gate A, Gate B, and final Gate D are GO for the current provider-side initiative. ST-052 through ST-056 are Done. HomeTusk runtime/mobile/backend/API integration remains out of scope and requires a separate HomeTusk-owned initiative.

## Latest 50-Scenario Evidence

| Metric | Value |
|--------|-------|
| Total 50-scenario suite | 50 |
| Evaluated scenarios | 50 |
| Schema-valid decisions | 50 |
| Outcome matches | 50 |
| Intent matches | 20 |
| Unsupported auto-execute | 0 |
| Cross-household references | 0 |
| Blocker failure scenarios | 0 |
| Failure buckets | `wrong_intent=30`, `item_boundary_loss=2` |

The latest report is `docs/planning/workpacks/ST-052/local-50-scenario-eval-report.json`. It is privacy-safe and passed `--check-no-raw-text`.

## Latest ST-053 Contract Posture

| Area | Decision |
|------|----------|
| First-class `reject` | Required before HomeTusk runtime acceptance; open ST-054 contract workpack. |
| Non-executing `confirm` | Required before assignment/linkage/reschedule/batch UX acceptance; open ST-054 contract workpack. |
| `answer` | Blocked until HomeTusk grounded read-model contract governance starts. |
| Shopping plurality | Repeated singular `propose_add_shopping_item` remains sufficient for the next provider eval step if item boundaries are preserved. |

ST-053 Gate D is GO for contract posture. It does not approve schema, version, public API, or runtime changes.

## Latest ST-054 Contract Evidence

| Area | Value |
|------|-------|
| Contract version | `2.1.0` |
| New DecisionDTO actions | `reject`, `confirm` |
| New optional DecisionDTO field | `decision_outcome` |
| Status enum | Unchanged: `ok`, `clarify`, `error` |
| CommandDTO capabilities | Added `reject`, `confirm` |
| Provider `answer` | Not added |
| Direct plural shopping action | Not added |
| Focused tests | 32 passed |
| 50-scenario blocker count after regeneration | 7 before ST-055; 0 after ST-055 |

ST-054 Gate D is GO for contract schema. Runtime adaptation is now authorized only through ST-055.

## Latest ST-055 Runtime Evidence

| Area | Value |
|------|-------|
| Gate C | GO for ST-055 APPLY |
| Gate D | GO for ST-055 closure |
| Workpack | `docs/planning/workpacks/ST-055/workpack.md` |
| PLAN report | `docs/planning/workpacks/ST-055/plan-report.md` |
| Review report | `docs/planning/workpacks/ST-055/review-report.md` |
| Original blocker scenario IDs | `HT-GS-003`, `HT-GS-008`, `HT-GS-015`, `HT-GS-043`, `HT-GS-046`, `HT-GS-048`, `HT-GS-049` |
| Contract impact | None; use `2.1.0` first-class `reject` already approved in ST-054 |
| Runtime paths | `graphs/core_graph.py` only for shared deterministic helpers |
| Eval/test paths | `scripts/evaluate_domain_planner_seed.py`, focused tests, regenerated ST-052 eval report |
| Diagram path | `docs/diagrams/domain-planner-v1-flow.puml` label update only |
| Focused tests | 33 passed |
| Full tests | 346 passed, 4 skipped |
| Release sanity | Pass through `python3 -m skills.release_sanity` |

ST-055 Gate D is GO.

## ST-056 Closure / Handoff

| Area | Value |
|------|-------|
| Gate D | GO for provider-side initiative closure |
| Workpack | `docs/planning/workpacks/ST-056/workpack.md` |
| Story | `docs/planning/epics/EP-017/stories/ST-056-review-closure-hometusk-handoff.md` |
| Handoff note | `docs/planning/workpacks/ST-056/hometusk-handoff.md` |
| HomeTusk files | Not modified |
| Remaining blocked areas | HomeTusk runtime/mobile/backend/API, provider `answer`, production rollout |

EP-017 is Done for provider evidence and handoff. The recommended next action is HomeTusk review and, if accepted, a separate HomeTusk-owned runtime integration initiative.
