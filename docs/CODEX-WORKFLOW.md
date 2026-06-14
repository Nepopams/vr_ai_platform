# Codex-Only Delivery Workflow

## Purpose

This document defines the active operating model for this repository after migration from the legacy Claude/Codex split. It describes how Codex performs delivery end to end while preserving human gates, contract-first governance, ADR/diagram discipline, and read-only review boundaries.

The active model is:

`intake -> planning -> artifact gate -> workpack -> Codex PLAN -> Human Gate C -> Codex APPLY -> read-only review gate -> Human Gate D`

## Active Authority Chain

1. `AGENTS.md` - short normative rules for Codex.
2. `CODEX.md` - short operational entrypoint for Codex-only workflow.
3. `docs/CODEX-WORKFLOW.md` - detailed workflow model.
4. `.agents/skills/**/SKILL.md` - reusable workflow instructions.
5. `.codex/agents/**` - read-only review agents.
6. `.codex/skills/**` - existing deterministic / implementation-oriented project skills.

Legacy Claude files are not active workflow authority. See "Legacy Status" below.

## Sources of Truth

| Area | Source |
| --- | --- |
| Product goal | `docs/planning/strategy/product-goal.md` |
| Roadmap | `docs/planning/strategy/roadmap.md` |
| Release scope | `docs/planning/releases/MVP.md` |
| DoR / DoD | `docs/_governance/dor.md`, `docs/_governance/dod.md` |
| ADRs | `docs/adr/`, `docs/_indexes/adr-index.md` |
| Contracts | `contracts/schemas/`, `contracts/VERSION`, `docs/contracts/CONTRACT-GOVERNANCE-RUNBOOK.md` |
| Diagrams | `docs/diagrams/`, `docs/_indexes/diagrams-index.md` |
| Planning templates | `docs/planning/_templates/` |
| Workpacks | `docs/planning/workpacks/<STORY_ID>/` |

If a source is missing, create only a minimal TODO stub and do not invent product content.

## Operating Model

### 1. Intake

Capture the user request, goal, constraints, success criteria, scope anchor, urgency, risks, and known forbidden paths. Do not assume domain meaning from repository names or folder names.

Expected output:

- request type and risk level;
- candidate scope anchor;
- missing inputs;
- whether artifact gate is needed before workpack.

Use skill: `.agents/skills/vr-intake-triage/SKILL.md`.

### 2. Planning

Turn intake into a planning artifact aligned with product goal, roadmap, MVP scope, DoR, DoD, ADRs, contracts, and diagrams. Planning must stay source-bound and must not add product strategy that is not already present in repository files.

Expected output:

- scoped plan;
- in-scope and out-of-scope boundaries;
- risks and dependencies;
- readiness status;
- flags: `contract_impact`, `adr_needed`, `diagrams_needed`, `security_sensitive`, `traceability_critical`.

Use skill: `.agents/skills/vr-planning/SKILL.md`.

### 3. Artifact Gate

Run before implementation when the change might affect contracts, schemas, public API, graph behavior, model policy, agent behavior, observability, ADRs, or diagrams.

Gate result must say one of:

- `NO ARTIFACT CHANGE REQUIRED`;
- `ARTIFACT CHANGE REQUIRED BEFORE WORKPACK`;
- `BLOCKED - HUMAN DECISION REQUIRED`.

Contract work uses `.agents/skills/vr-contract-governance/SKILL.md`.

ADR and diagram work uses `.agents/skills/vr-adr-diagram-governance/SKILL.md`.

### 4. Workpack

The workpack is the authority for APPLY. It must include:

- sources of truth;
- outcome;
- acceptance criteria;
- files to change;
- allowed and forbidden paths;
- implementation plan;
- validation commands;
- tests;
- rollback;
- risks;
- artifact gate result.

Use `docs/planning/_templates/workpack.md` and `.agents/skills/vr-workpack-prompts/SKILL.md`.

### 5. Codex PLAN

PLAN is read-only exploration. It may inspect the repository and prepare implementation findings, but it must not mutate the working tree.

Allowed:

- read files;
- inspect git status and diffs;
- inspect schemas, tests, scripts, logs, planning docs;
- propose exact implementation steps.

Forbidden:

- file writes, edits, moves, deletes;
- package installs;
- network;
- commits and pushes;
- migrations or runtime mutations;
- APPLY work.

PLAN output must include:

- confirmed files to create, modify, or avoid;
- assumptions;
- risks;
- exact validation commands;
- blockers;
- readiness for Human Gate C.

### 6. Human Gate C

Human Gate C is mandatory. Codex cannot move from PLAN to APPLY until the human approves the plan or supplies corrections.

Gate C approval should identify:

- approved scope;
- approved files and forbidden paths;
- accepted risks;
- required validation commands;
- whether any artifact work must happen first.

### 7. Codex APPLY

APPLY performs implementation only after Human Gate C. APPLY must stay inside the approved workpack and PLAN findings.

APPLY must stop if it discovers:

- contract/schema/public API change not approved by artifact gate;
- ADR conflict;
- missing source of truth;
- need to change runtime behavior beyond approved scope;
- unexpected dirty files that make the work unsafe.

### 8. Read-Only Review Gate

Review is a separate read-only step after APPLY. It may inspect diffs, files, and verification results. It must not edit files or run APPLY.

Use `.codex/agents/**` read-only review agents as needed:

| Agent | Purpose |
| --- | --- |
| `architecture-review` | Check architectural scope, boundaries, and ADR alignment. |
| `contract-drift-review` | Check contract/schema/version drift. |
| `adr-diagram-drift-review` | Check ADR and diagram drift. |
| `security-review` | Check security and privacy risks. |
| `observability-review` | Check logs, metrics, traceability, and raw-data policy. |
| `test-gap-review` | Check missing tests and validation gaps. |
| `planning-audit` | Check workpack, DoR/DoD, and scope alignment. |
| `final-review-gate` | Aggregate GO/NO-GO for Human Gate D. |

All read-only agents must explicitly enforce:

- no production code writes;
- no document mutation;
- no parallel document mutation;
- no APPLY;
- no human gate bypass.

### 9. Human Gate D

Human Gate D decides merge, ship, rework, rollback, or defer after the read-only review gate. Codex may recommend but cannot replace this decision.

## Review Gate Format

Use this format for the final review gate:

```markdown
## Review Result: GO | NO-GO

### Must-Fix Issues
- None

### Should-Fix Issues
- None

### Evidence
- Files reviewed:
- Commands run:
- Command results:
- Sources checked:

### Contract / ADR / Diagram Drift
- Contract drift:
- ADR drift:
- Diagram drift:

### Recommendation
Approve for Human Gate D | Block until fixes are complete
```

## Skills

Workflow skills live in `.agents/skills/**`. They are instruction-only and contain no runtime code.

- `vr-intake-triage` - classify request, risk, missing inputs, and next workflow step.
- `vr-planning` - create source-bound planning artifacts.
- `vr-contract-governance` - classify contract changes and required semver/fixture checks.
- `vr-adr-diagram-governance` - decide whether ADRs or diagrams must change.
- `vr-workpack-prompts` - create workpack, PLAN prompt, and APPLY prompt boundaries.
- `vr-review-gate` - run read-only review gate and GO/NO-GO report.

Existing `.codex/skills/**` stay in place as project-specific deterministic / implementation-oriented skills. Do not move, delete, or rewrite them as part of workflow migration.

## Legacy Status

The legacy pipeline was:

`Claude = analysis / architecture / prompts, Codex = implementation`

That pipeline is now historical reference only. Active workflow now lives in:

- `AGENTS.md`;
- `CODEX.md`;
- `docs/CODEX-WORKFLOW.md`;
- `.agents/skills/**`;
- `.codex/agents/**`.

`CLAUDE.md` and `.claude/**` must not be used as active workflow authority. They may be read only to understand historical decisions or migration context.

## Migration Note

This repository has been migrated to Codex-only delivery workflow documentation. The migration is limited to workflow instructions, read-only review agents, reusable workflow skills, and legacy notices. It does not change runtime code, contracts, schemas, public API, fixtures, or existing `.codex/skills/**`.

## Local Validation

For workflow-only changes, validation should normally include:

```bash
git status --short
rg -n "active workflow authority|legacy reference only|no APPLY|Human Gate C|Human Gate D" AGENTS.md CODEX.md docs/CODEX-WORKFLOW.md .agents .codex/agents .claude CLAUDE.md
rg --files .codex/skills
```

Runtime checks are not required for documentation-only workflow migration unless runtime files, contracts, schemas, tests, fixtures, or public API files are changed.
