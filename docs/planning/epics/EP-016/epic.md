# EP-016: Domain Planner v1 — Narrow Household Command Corridor

**Status:** Done
**Initiative:** `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.md`
**Roadmap:** `docs/planning/strategy/roadmap.md`
**Owner:** Codex / AI Platform engineering team

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Roadmap | `docs/planning/strategy/roadmap.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.md` |
| Execution notes | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.execution.md` |
| MVP scope | `docs/planning/releases/MVP.md` |
| Command schema | `contracts/schemas/command.schema.json` |
| Decision schema | `contracts/schemas/decision.schema.json` |
| Contract version | `contracts/VERSION` |
| Contract governance | `docs/contracts/CONTRACT-GOVERNANCE-RUNBOOK.md` |
| ADR-000 | `docs/adr/ADR-000-ai-platform-intent-decision-engine.md` |
| ADR-001 | `docs/adr/ADR-001-contract-versioning-compatibility-policy.md` |
| ADR-004 | `docs/adr/ADR-004-partial-trust-corridor.md` |
| ADR-006 | `docs/adr/ADR-006-multi-item-internal-model.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

HomeTusk read-only source package:

```text
C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/domain-planner-v1-gate/
```

Source revision read: `d924c631c80895995c65f22bec6f77dc0a0347b7`.

---

## Context

HomeTusk closed an artifact gate with a `LIMITED-GO` recommendation. The provider-side follow-up is a narrow AI Platform Domain Planner v1 corridor for simple task creation and shopping item addition. HomeTusk remains execution, guardrail, audit, and final acceptance authority.

Current provider contracts already support schema-valid `start_job` decisions, `propose_create_task`, `propose_add_shopping_item`, `clarify`, and multi-item output through repeated proposed actions. They do not provide first-class `reject`, `confirm`, or `answer` outcomes.

## Goal

Deliver a source-bound provider path toward Domain Planner v1 that preserves the narrow corridor, records contract/ADR/diagram/privacy gates, consumes or references HomeTusk seed fixtures with source metadata, and eventually produces deterministic eval evidence before closure.

## Scope

### In scope

- Provider-side artifact gate for current-schema mapping, reject/confirm limitations, ADR/diagram impact, and privacy posture.
- Fixture import/reference strategy for HomeTusk seed scenarios.
- Deterministic eval runner output with per-scenario and aggregate results.
- Narrow planner support for simple `create_task`, multi-item `add_shopping_items` mapping, safe `clarify`, and safe `reject` mapping.
- Regression checks proving ASR remains transcription-only and `/v1/decide` schema validation continues.

### Out of scope

- HomeTusk runtime, mobile, backend, OpenAPI, or integration doc edits.
- Direct HomeTusk state mutation.
- Direct mobile/web calls to AI Platform.
- Broad multi-agent production planner.
- Full household workload optimizer.
- First-class `answer` behavior before HomeTusk answer contract exists.
- Contract/schema/public API changes without a dedicated contract workpack.
- Production rollout/config changes without a separate gate.

## Stories

| Story ID | Title | Status | Flags |
|----------|-------|--------|-------|
| [ST-048](stories/ST-048-provider-mapping-artifact-gate.md) | Provider mapping, ADR, diagram, and privacy posture | Done | contract_impact=no-edit, adr_needed=done, diagrams_needed=done, security_sensitive=yes, traceability_critical=yes |
| [ST-049](stories/ST-049-fixture-import-eval-runner.md) | HomeTusk seed fixture import/reference and deterministic eval runner | Done | contract_impact=no, adr_needed=none, diagrams_needed=none, security_sensitive=yes, traceability_critical=yes |
| [ST-050](stories/ST-050-domain-planner-v1-implementation.md) | Domain Planner v1 narrow corridor implementation/adaptation | Done | contract_impact=none-current-schema, adr_needed=covered-by-ST-048, diagrams_needed=covered-by-ST-048, security_sensitive=yes, traceability_critical=yes |
| [ST-051](stories/ST-051-review-closure-handoff.md) | Review gate, closure evidence, and HomeTusk handoff | Done | contract_impact=no, adr_needed=none, diagrams_needed=none, security_sensitive=yes, traceability_critical=yes |

## Artifact Gate

| Area | Decision |
|------|----------|
| Gate A | GO. Provider-side scope is narrow and HomeTusk remains read-only input. |
| Gate B | GO for decomposition and ST-048 artifact workpack. Runtime APPLY remains HOLD. |
| Contract | Start with current-schema mapping. Any schema edit, version bump, first-class `reject`/`confirm`, or public API change requires a dedicated contract workpack. |
| ADR | Required before runtime APPLY because Domain Planner v1 affects decision flow and provider boundaries. |
| Diagram | Required before runtime APPLY to show HomeTusk -> AI Platform -> HomeTusk validation/execution boundary. |
| Security/privacy | Required before runtime APPLY; prompt/response retention and raw text/audio boundaries must be documented. |

## Dependencies

- HomeTusk artifact package under the read-only path listed above.
- Existing `/v1/decide` route and request/response schema validation.
- Existing `RouterV2` / graph behavior, assist, shadow, and partial-trust flags.
- Existing graph sanity and quality-eval tooling.
- Future contract workpack if ST-048 proves current schema mapping is insufficient.

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| `reject` semantics remain rough in current schema | High | High | ST-048 must document current-schema mapping or HOLD for contract workpack. |
| `confirm` is required by consumer taxonomy but not provider schema | Medium | High | Treat confirm as optional/non-executing and gated; do not fake execution semantics. |
| Seed fixture set is too small for final acceptance | High | Medium | Use seed gate now; record need for 50 product-owned scenarios before acceptance. |
| Planner broadens into household automation | Medium | High | Keep ST-050 bounded to create_task/add_shopping_items/clarify/reject only. |
| Raw text leaks into reports/logs | Medium | High | Store source metadata and scenario IDs in reports; keep privacy review mandatory. |
| Contract drift with HomeTusk wrapper docs | Medium | High | ST-048 must address documented drift D-004 and D-005 before runtime work. |

## Readiness

ST-048 is Done and closes the provider artifact gate for mapping, ADR, diagram, and privacy posture. ST-049 is Done and provides the reference-only seed eval runner plus local evidence. ST-050 is Done for current-schema runtime adaptation and has Gate D GO. ST-051 is Done and closes the provider initiative with handoff evidence.

## Latest ST-049 Evidence

| Metric | Value |
|--------|-------|
| Total seed scenarios | 10 |
| Schema-valid decisions | 10 |
| Outcome matches | 10 |
| Intent matches | 3 |
| Unsupported auto-execute | 0 |
| Cross-household references | 0 |
| Blocker failure scenarios | 0 |

ST-051 Gate D is GO for provider initiative closure. HomeTusk product acceptance remains separate.
