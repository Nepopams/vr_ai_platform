# WP / ST-053: Contract Posture Decision for Reject, Confirm, Answer, and Shopping Plurality

**Status:** Done (Gate D GO for contract posture; schema/runtime APPLY HOLD)
**Story:** `docs/planning/epics/EP-017/stories/ST-053-contract-posture.md`
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
| Story | `docs/planning/epics/EP-017/stories/ST-053-contract-posture.md` |
| Contract posture | `docs/planning/epics/EP-017/domain-planner-v1-contract-posture.md` |
| ST-052 eval report | `docs/planning/workpacks/ST-052/local-50-scenario-eval-report.json` |
| ADR-001 | `docs/adr/ADR-001-contract-versioning-compatibility-policy.md` |
| ADR-009 | `docs/adr/ADR-009-domain-planner-v1-narrow-corridor.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

HomeTusk read-only source:

```text
C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/provider-domain-planner-v1-acceptance/reject-confirm-answer-contract-posture.md
```

---

## Outcome

ST-053 delivers a source-bound contract posture gate. It explicitly decides that first-class `reject` and non-executing `confirm` require ST-054 contract-governed schema/version work, `answer` remains blocked, and repeated singular shopping actions remain acceptable for the next provider eval step if item boundaries are preserved.

## Acceptance Criteria

1. Contract posture note exists and records decisions for `reject`, `confirm`, `answer`, and shopping plurality.
2. ST-054 minimum scope is explicit.
3. ST-053 records contract, ADR, and diagram gate decisions.
4. No HomeTusk files, contracts, schemas, public API files, runtime planner files, or rollout/config files are modified.

## Files to Change

### New files (create)

| File | Description |
|------|-------------|
| `docs/planning/epics/EP-017/domain-planner-v1-contract-posture.md` | Provider contract posture artifact. |
| `docs/planning/epics/EP-017/stories/ST-053-contract-posture.md` | ST-053 story. |
| `docs/planning/workpacks/ST-053/workpack.md` | ST-053 implementation authority. |
| `docs/planning/workpacks/ST-053/prompt-plan.md` | ST-053 PLAN prompt. |
| `docs/planning/workpacks/ST-053/plan-report.md` | ST-053 PLAN findings. |
| `docs/planning/workpacks/ST-053/review-report.md` | ST-053 read-only review gate. |

### Modified files (update)

| File | Change |
|------|--------|
| `docs/planning/epics/EP-017/epic.md` | Update ST-053 status and latest posture evidence. |
| `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.md` | Update initiative status. |
| `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md` | Record ST-053 Gate C/D decisions and next step. |

### Deleted files

| File | Reason |
|------|--------|
| None | Not applicable. |

## Implementation Plan

### Step 1: Record posture decisions

Create a contract posture note from current provider schema, ADR-001/ADR-009, ST-052 evidence, and HomeTusk read-only posture.

### Step 2: Define ST-054 scope

Record exact minimum decisions needed before schema/version work for first-class `reject` and non-executing `confirm`.

### Step 3: Review gate

Verify that ST-053 changed only allowed documentation/planning paths and that schema/runtime/HomeTusk files remain untouched.

## Verification Commands

```bash
rg -n "ST-053|first-class `reject`|non-executing `confirm`|answer.*blocked|repeated singular" docs/planning/epics/EP-017 docs/planning/workpacks/ST-053 docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md
git diff --check
git status --short
```

## Tests

| Test | Checks | Expected |
|------|--------|----------|
| `rg` evidence check | ST-053 decisions and gate evidence are present | Pass |
| `git diff --check` | Diff hygiene | Pass |

## DoD Checklist

- [x] Contract posture note exists.
- [x] ST-054 minimum scope is explicit.
- [x] Gate C and Gate D are recorded.
- [x] Contract/schema/runtime/HomeTusk forbidden paths remain untouched.
- [x] Review report exists.

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Contract work starts without semver/fixtures | Medium | High | ST-053 keeps schema work HOLD until ST-054 workpack and Gate C. |
| `answer` sneaks into provider schema too early | Medium | High | Explicitly block `answer` until HomeTusk answer/read-model governance starts. |
| Plural shopping action distracts from planner item-boundary bugs | Medium | Medium | Keep repeated singular actions unless later evidence proves schema insufficiency. |

## Rollback

- Revert ST-053 planning artifacts and status updates.
- No code, contract, runtime, or HomeTusk rollback is needed because ST-053 is docs-only.

## APPLY Boundaries

### Allowed

- `docs/planning/epics/EP-017/domain-planner-v1-contract-posture.md`
- `docs/planning/epics/EP-017/stories/ST-053-contract-posture.md`
- `docs/planning/workpacks/ST-053/**`
- `docs/planning/epics/EP-017/epic.md`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.md`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md`

### Forbidden

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
- Production rollout/config files

## Human Gates

- Gate A: GO, recorded in execution notes.
- Gate B: GO for ST-053 docs-only contract posture; HOLD for schema/runtime mutations.
- Human Gate C: delegated GO for ST-053, recorded in execution notes.
- Human Gate D: GO for ST-053 contract posture; HOLD for schema/runtime APPLY.

## Validation Results

Validation was run on 2026-06-15.

| Command | Result |
|---------|--------|
| `rg -n "ST-053|first-class \`reject\`|non-executing \`confirm\`|answer.*blocked|repeated singular" docs/planning/epics/EP-017 docs/planning/workpacks/ST-053 docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md` | Pass |
| `git diff --check` | Pass with LF-to-CRLF warnings only |
