# ST-048: Provider Mapping, ADR, Diagram, and Privacy Posture

**Status:** Done
**Epic:** `docs/planning/epics/EP-016/epic.md`
**Owner:** Codex PLAN / Codex APPLY / read-only review gate
**Flags:** contract_impact=tbd-gated, adr_needed=yes, diagrams_needed=yes, security_sensitive=yes, traceability_critical=yes

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Roadmap | `docs/planning/strategy/roadmap.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.md` |
| Execution notes | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.execution.md` |
| Epic | `docs/planning/epics/EP-016/epic.md` |
| Command schema | `contracts/schemas/command.schema.json` |
| Decision schema | `contracts/schemas/decision.schema.json` |
| Contract governance | `docs/contracts/CONTRACT-GOVERNANCE-RUNBOOK.md` |
| ADR index | `docs/_indexes/adr-index.md` |
| Diagrams index | `docs/_indexes/diagrams-index.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

HomeTusk read-only package:

```text
C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/domain-planner-v1-gate/
```

## Description

Create the provider-side artifact gate needed before Domain Planner v1 runtime work. This story records how the current AI Platform schema maps to HomeTusk accepted taxonomy, what remains gated, what ADR/diagram artifacts are required, and what privacy/retention posture applies before planner APPLY.

## Acceptance Criteria

```gherkin
Given the HomeTusk artifact package and current provider schemas
When the provider artifact gate is prepared
Then the mapping from current provider actions to HomeTusk outcomes is documented
And unsupported first-class outcomes are marked as gated, not silently implemented
And ADR and diagram requirements are captured before runtime APPLY
And privacy/retention questions are answered or explicitly marked HOLD
And no runtime, contract, schema, fixture, or HomeTusk files are changed
```

## Scope

### In scope

- Provider mapping note for current-schema Domain Planner v1 corridor.
- ADR draft/accepted artifact for narrow Domain Planner v1 boundaries.
- Provider flow diagram and diagram index update.
- Privacy/retention posture for prompt/response/eval data.
- Gate C readiness criteria for later runtime workpacks.

### Out of scope

- Runtime planner implementation.
- Contract/schema/version changes.
- Fixture import or fixture transformation.
- Eval runner implementation.
- HomeTusk file edits.
- Public API changes.

## Test Strategy

### Unit tests

- None. This is a docs/artifact-gate story.

### Integration tests

- None. Runtime behavior is out of scope.

### Documentation validation

- `git diff --check`
- `rg -n "Domain Planner v1|Gate A|Gate B|Gate C|reject|confirm|privacy|retention" docs/planning/initiatives docs/planning/epics/EP-016 docs/planning/workpacks/ST-048`
- Verify that no forbidden runtime/contract paths changed with `git status --short`.

## Blocked By

- Closed by `docs/planning/workpacks/ST-048/workpack.md`; runtime work remains blocked by later workpacks.
