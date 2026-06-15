# Workpack: ST-048 — Provider Mapping, ADR, Diagram, and Privacy Posture

**Status:** Done (artifact gate closed; runtime HOLD)
**Story:** `docs/planning/epics/EP-016/stories/ST-048-provider-mapping-artifact-gate.md`
**Owner:** Codex PLAN / Codex APPLY / read-only review gate

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Roadmap | `docs/planning/strategy/roadmap.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.md` |
| Execution notes | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.execution.md` |
| Epic | `docs/planning/epics/EP-016/epic.md` |
| Story | `docs/planning/epics/EP-016/stories/ST-048-provider-mapping-artifact-gate.md` |
| Command schema | `contracts/schemas/command.schema.json` |
| Decision schema | `contracts/schemas/decision.schema.json` |
| Contract governance | `docs/contracts/CONTRACT-GOVERNANCE-RUNBOOK.md` |
| ADR index | `docs/_indexes/adr-index.md` |
| Diagrams index | `docs/_indexes/diagrams-index.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

HomeTusk read-only artifact package:

```text
C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/domain-planner-v1-gate/
```

Source revision read during Gate B: `d924c631c80895995c65f22bec6f77dc0a0347b7`.

---

## Outcome

Create the provider-side artifact gate needed before Domain Planner v1 runtime work. The output must document current-schema mapping, gated contract gaps, ADR/diagram decisions, privacy/retention posture, and Gate C stop conditions for later runtime workpacks.

## Artifact Gate Result

**APPROVED and completed for ST-048 artifact scope under delegated user gates. Runtime APPLY remains HOLD.**

| Gate | Result |
|------|--------|
| Gate A | GO: provider-side narrow scope approved in execution notes. |
| Gate B | GO for this docs/artifact workpack; HOLD for runtime APPLY. |
| Contract | No contract edits in ST-048. Any schema/version/public API change requires a later contract workpack. |
| ADR | Required before runtime APPLY; ST-048 may create/update provider ADR artifacts. |
| Diagram | Required before runtime APPLY; ST-048 may create/update provider diagram artifacts. |
| Security/privacy | Required; ST-048 must document prompt/response/eval retention posture or explicit HOLD items. |
| Human Gate C | GO for ST-048 artifact APPLY. PLAN confirmed docs-only scope and no runtime/contract/fixture/HomeTusk writes. |

## Acceptance Criteria

1. Provider mapping note documents current AI Platform schema mapping to HomeTusk outcomes without raw scenario text.
2. First-class `reject`, `confirm`, and `answer` gaps are explicitly gated and not treated as implemented behavior.
3. ADR artifact and ADR index are created or updated for Domain Planner v1 provider boundaries.
4. Diagram artifact and diagram index are created or updated for the provider flow and HomeTusk validation/execution boundary.
5. Privacy/retention posture answers the HomeTusk required questions that AI Platform can answer now, and marks unresolved items as HOLD.
6. Gate C readiness criteria are recorded for later runtime and fixture/eval workpacks.
7. No runtime, contract schema, contract version, fixture, public API, or HomeTusk files are changed.

## Files to Change

### New files

| File | Description |
|------|-------------|
| `docs/planning/epics/EP-016/domain-planner-v1-provider-mapping.md` | Provider mapping and gated outcome semantics. |
| `docs/adr/ADR-009-domain-planner-v1-narrow-corridor.md` | ADR for narrow Domain Planner v1 provider boundary. |
| `docs/diagrams/domain-planner-v1-flow.puml` | Provider flow and execution boundary diagram. |
| `docs/guides/domain-planner-v1-privacy-retention.md` | AI Platform privacy/retention posture for planner data. |

### Modified files

| File | Change |
|------|--------|
| `docs/_indexes/adr-index.md` | Add ADR-009-P entry if ADR is created. |
| `docs/_indexes/diagrams-index.md` | Add Domain Planner v1 flow entry if diagram is created. |
| `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.execution.md` | Update Gate C decision after PLAN/APPLY if needed. |
| `docs/planning/epics/EP-016/epic.md` | Update ST-048 status after completion if needed. |
| `docs/planning/epics/EP-016/stories/ST-048-provider-mapping-artifact-gate.md` | Update status after completion if needed. |
| `docs/planning/workpacks/ST-048/workpack.md` | Update status/checklist after completion if needed. |

### Deleted files

| File | Reason |
|------|--------|
| None | No deletion authorized. |

## Forbidden Paths

- `contracts/**`
- `contracts/schemas/**`
- `contracts/VERSION`
- `app/**`
- `graphs/**`
- `routers/**`
- `agents/**`
- `agent_registry/**`
- `agent_runner/**`
- `llm_policy/**`
- `tests/**`
- `skills/**`
- `.codex/skills/**`
- Any file outside `C:/Users/user/Documents/projects/VR_AI_Platform`

## Implementation Plan

### Step 1: Codex PLAN

Run the read-only PLAN in `docs/planning/workpacks/ST-048/prompt-plan.md`.

### Step 2: Delegated Gate C

If PLAN confirms no blockers and exact file scope remains within this workpack, record delegated Gate C GO in this workpack or execution notes before APPLY.

### Step 3: Artifact APPLY

Create the mapping note, ADR, diagram, and privacy/retention guide. Update indexes only for artifacts actually created.

### Step 4: Review and closure

Run docs validation and update ST-048 status. Do not mark EP-016 or the initiative Done; this story only closes the provider artifact gate.

## Verification Commands

```bash
git status --short
git diff --check
rg -n "Domain Planner v1|Gate A|Gate B|Gate C|reject|confirm|privacy|retention" docs/planning/initiatives docs/planning/epics/EP-016 docs/planning/workpacks/ST-048
rg -n "ADR-009|domain-planner-v1-flow|Domain Planner v1" docs/_indexes docs/adr docs/diagrams
```

Runtime tests are not required for ST-048 unless forbidden runtime/test/contract paths are changed accidentally.

## Tests

| Test | Checks | Expected |
|------|--------|----------|
| `git diff --check` | Whitespace and patch hygiene | Pass |
| `git status --short` | Only approved docs/planning/ADR/diagram files changed | Pass |
| `rg` artifact checks | Mapping, gate, ADR, diagram, privacy terms present | Pass |

## DoD Checklist

- [x] Read-only PLAN completed.
- [x] Delegated Gate C GO recorded.
- [x] Provider mapping note created.
- [x] ADR created and indexed.
- [x] Diagram created and indexed.
- [x] Privacy/retention posture created.
- [x] No forbidden paths changed.
- [x] Validation commands pass.

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Mapping hides reject/confirm gap | Medium | High | Explicitly mark first-class outcomes as gated and require contract workpack if needed. |
| Privacy posture overclaims retention guarantees | Medium | High | Answer only provider-known items; mark unknowns HOLD. |
| ADR duplicates existing ADRs | Low | Medium | PLAN must compare ADR-000/001/004/006/008 first. |
| Diagram implies AI Platform execution authority | Low | High | Diagram must show HomeTusk validation/execution after provider decision. |

## Rollback

Remove new ST-048 docs/ADR/diagram/privacy artifacts and revert index/status updates. No runtime rollback should be needed because runtime paths are forbidden.

## APPLY Boundaries

### Allowed

- `docs/planning/epics/EP-016/**`
- `docs/planning/workpacks/ST-048/**`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.execution.md`
- `docs/adr/ADR-009-domain-planner-v1-narrow-corridor.md`
- `docs/_indexes/adr-index.md`
- `docs/diagrams/domain-planner-v1-flow.puml`
- `docs/_indexes/diagrams-index.md`
- `docs/guides/domain-planner-v1-privacy-retention.md`

### Forbidden

- Runtime, contracts, schemas, tests, fixtures, public API, and HomeTusk files listed above.

## Human Gates

- Gate A: GO recorded in initiative execution notes.
- Gate B: GO for provider planning and ST-048 workpack; runtime APPLY is HOLD.
- Human Gate C: GO for ST-048 artifact APPLY, recorded after read-only PLAN.
- Human Gate D: GO for ST-048 artifact scope, recorded in `docs/planning/workpacks/ST-048/review-report.md`; runtime APPLY remains HOLD regardless of ST-048 closure.
