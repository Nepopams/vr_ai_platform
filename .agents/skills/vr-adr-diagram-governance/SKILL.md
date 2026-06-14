---
name: vr-adr-diagram-governance
description: Instruction-only workflow skill for ADR and diagram governance in the Codex-only workflow. Use when a change may affect architecture, graph flow, agent boundaries, model policy, public API, diagrams, or ADR/index consistency.
---

# vr-adr-diagram-governance

## Purpose

Decide whether ADRs or diagrams must be created or updated before implementation. Keep architectural documentation aligned without adding speculative architecture.

## Sources / Inputs

- `docs/adr/`
- `docs/_indexes/adr-index.md`
- `docs/diagrams/`
- `docs/_indexes/diagrams-index.md`
- `docs/diagrams/README.md`
- Relevant planning artifacts and workpacks.
- Relevant runtime paths only for read-only inspection.

## Workflow

1. Identify whether the request changes architecture, boundaries, graph flow, agent model, model policy, public API, or external behavior.
2. Check accepted ADRs for conflicts or required updates.
3. Check diagram index for affected diagrams.
4. Decide whether ADR, ADR-lite, diagram update, or no artifact change is required.
5. If required artifacts are missing, stop before APPLY and request or create source-bound drafts.
6. Update indexes only when an approved artifact is created or changed.

## Allowed scope

- Read ADRs, diagrams, indexes, planning docs, and relevant source files.
- Create minimal TODO stubs only when a required governance artifact is missing.
- Produce an ADR/diagram gate decision.

## Forbidden scope

- No runtime implementation.
- No speculative architecture.
- No contracts/schemas/public API changes.
- No APPLY.
- No human gate bypass.

## Output

```markdown
## ADR / Diagram Gate
- Architecture impact:
- ADR impact:
- Diagram impact:
- Required artifacts:
- Index updates:
- Gate result:
```
