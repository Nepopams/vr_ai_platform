# INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor — Domain Planner v1: Narrow Household Command Corridor

**Priority:** High
**Period:** 2026Q3 (PI TBD)
**Status:** Draft (to be approved at Gate A)
**Owner:** AI Platform engineering team

## Context

HomeTusk has completed an AI Command Capability Audit and an artifact gate for the next AI-command step.

The HomeTusk-side conclusion is **LIMITED-GO**:

- proceed only toward a narrow AI Platform Domain Planner v1 corridor;
- focus on simple task creation and shopping item addition;
- do not proceed yet to broad natural command execution, HomeTusk `natural_command` runtime implementation, Mobile AI Command Center, mixed task/shopping autonomous planning, or multi-agent production planner.

This initiative is the provider-side follow-up in `vr_ai_platform`.

AI Platform should act as a stateless planner/decision provider. HomeTusk remains the product-service, execution authority, guardrail authority, audit authority, and final acceptance owner.

The target product flow is:

```text
HomeTusk command context
  -> AI Platform Domain Planner v1
  -> schema-valid provider decision
  -> HomeTusk schema validation / guardrails / execution / DecisionLog
```

AI Platform must not mutate HomeTusk state and must not be called directly by mobile/web clients.

## HomeTusk Handoff Inputs

The implementation plan must consume the HomeTusk artifact gate package as consumer acceptance input.

Canonical HomeTusk artifacts:

```text
hometusk/docs/research/ai-command-capabilities/domain-planner-v1-gate/
  README.md
  decision-action-taxonomy-accepted-v0.md
  natural-command-contract-v0-draft.md
  golden-scenarios-fixtures-v0/
  eval-rubric-v0.md
  privacy-and-retention-questions.md
  provider-planner-readiness-checklist.md
  hometusk-ai-platform-integration-doc-drift.md
  provider-initiative-brief.md
```

Expected handoff posture:

- HomeTusk artifacts are acceptance inputs, not provider code changes.
- If fixtures are copied into this repository, the copy must record source repo, source path, source revision or import date, and fixture version.
- Any provider contract/schema change must be explicitly planned and gated.
- Passing provider tests is necessary but not sufficient for HomeTusk acceptance.

## Goal

Implement or adapt a single Domain Planner v1 for the narrow HomeTusk household command corridor.

The planner should support schema-valid provider decisions for:

- simple task creation;
- multi-item shopping addition;
- safe clarification;
- safe rejection;
- optionally non-executing confirmation if the current provider contract can support or cleanly map it.

The initiative must also produce deterministic eval evidence against HomeTusk golden fixtures and document privacy/retention posture for prompt/response data.

## Scope

### In scope

#### Planner capability

- Implement or adapt a single Domain Planner v1 path for narrow household commands.
- Support `create_task` planning.
- Support multi-item `add_shopping_items` planning, represented through provider-supported proposed actions or an explicitly gated schema evolution.
- Preserve item boundaries for shopping commands.
- Support `clarify` when a required slot or entity is missing or ambiguous.
- Support safe `reject` mapping for unsupported, unsafe, cross-household, or unverifiable requests.
- Optionally support non-executing `confirm` for risky but understood plans if contract impact is explicitly gated.
- Propose date/time with timezone when safe, otherwise clarify.
- Prefer clarify over guessing.

#### Contract and schema handling

- Preserve schema validation at request and response boundaries.
- Either:
  1. keep the current provider schema and document accepted mapping into HomeTusk taxonomy, or
  2. propose minimal provider schema changes through contract governance.
- Preserve `/v1/decide` as the provider entrypoint unless an explicit contract gate approves otherwise.
- Provide planner version, decision version, schema version, decision id, and trace id.

#### Evals and fixtures

- Import or reference HomeTusk golden fixtures for the seed scenario set.
- Add deterministic eval runner output suitable for HomeTusk review.
- Report per-scenario result, aggregate metrics, failure buckets, skipped scenarios and reasons, fixture version/source, planner version, decision version, run command, and relevant feature flags.
- Seed fixture pass must include at minimum:
  - schema-valid outputs;
  - no unsupported auto-execute;
  - no cross-household leakage;
  - clarify over guessing;
  - reject unsafe broad assignment;
  - preserve shopping item boundaries;
  - no mutation semantics in provider output.

#### Privacy / retention

- Document provider prompt and response retention posture.
- Document whether raw user text is logged, stored, sampled, or retained.
- Confirm raw audio is not part of `/v1/decide` planner flow.
- Confirm no auth tokens, device tokens, invite tokens, emails, or cross-household data are required.
- Document model/prompt/planner versioning expectations.

#### Compatibility

- Existing ASR endpoint must remain transcription-only.
- Existing `/v1/asr/transcribe` must not call `/v1/decide` automatically.
- Existing shadow, assist, partial-trust, and RouterV2 behavior must remain controlled by flags and not silently broaden production behavior.

### Out of scope

- Direct HomeTusk state mutation.
- Direct mobile/web integration.
- Direct mobile/web calls to AI Platform.
- HomeTusk `natural_command` runtime implementation.
- HomeTusk backend/OpenAPI changes.
- HomeTusk mobile AI UI changes.
- Broad multi-agent production planner.
- Full household workload optimizer.
- Fairness/autonomous assignment optimizer.
- Natural reschedule auto-execute.
- Natural completion auto-execute.
- Read-only `answer_status` runtime behavior until HomeTusk `answered` contract exists.
- Mixed task + shopping autonomous execution without confirmation semantics.
- Prompt-only rollout without schema and eval evidence.
- Production rollout/config change without separate gate.

## Accepted Narrow Corridor

### Auto-execute candidate decisions

AI Platform may propose provider decisions that map to HomeTusk `execute` only for:

```text
create_task
add_shopping_items
```

Actual execution is still performed only by HomeTusk after validation and guardrails.

### Clarify

Planner should clarify when:

- task title is missing or vague;
- shopping item boundary is unclear;
- default/list/source cannot be grounded;
- member, zone, task, or date is ambiguous;
- household context is incomplete;
- capability is missing.

### Reject

Planner should reject or map to safe rejection when:

- action type is unsupported;
- request is unsafe or impossible;
- request references unverifiable or cross-household entities;
- request would require direct AI execution;
- provider cannot produce schema-valid output.

### Confirm

`confirm` is optional for this initiative and must be non-executing if introduced.

If supported, use confirm for:

- inferred assignment to someone other than requester;
- task plus shopping linkage;
- reschedule;
- batch planning;
- broad workload redistribution;
- any action outside the narrow auto-execute corridor but still inside the household domain.

## Acceptance Criteria

1. Domain Planner v1 is implemented or adapted for the narrow corridor without broadening production behavior outside flags/gates.
2. `/v1/decide` continues to validate request and response schemas.
3. Planner supports simple `create_task` decision output.
4. Planner supports multi-item shopping addition while preserving item boundaries.
5. Planner clarifies missing/ambiguous task, list, member, zone, or date context.
6. Planner rejects unsupported, unsafe, cross-household, or unverifiable requests.
7. Planner output includes trace id and versioning metadata required for audit.
8. Provider eval runner consumes or imports HomeTusk seed fixtures with source metadata.
9. Provider eval output reports per-scenario and aggregate results.
10. Seed scenarios have zero blocker failures before Gate D.
11. Privacy/retention posture is documented for prompt/response data.
12. ASR endpoint remains transcription-only and does not call `/v1/decide`.
13. Existing tests continue to pass.
14. No HomeTusk repository files are modified.
15. No broad multi-agent production planner is introduced.

## Suggested Execution Shape

Codex should decompose this initiative after Gate A into provider-native epics/stories/workpacks.

Expected work areas may include:

- contract review and mapping decision;
- fixture import/eval harness;
- Domain Planner v1 implementation/adaptation;
- privacy/retention documentation;
- regression tests;
- review and closure evidence.

No implementation should start before Gate C.

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Planner becomes broad household automation | High | Keep narrow corridor and reject/clarify outside it |
| Prompt-only behavior without evals | High | Require deterministic eval output and seed scenario pass |
| Schema drift with HomeTusk | High | Explicit contract gate and mapping docs |
| Multi-agent complexity enters too early | Medium | Single planner only; multi-agent out of scope |
| Date/time normalization guesses | High | Clarify when timezone/window is ambiguous |
| Non-requester assignment causes social/policy issues | High | Confirm or clarify; no auto-execute assignment inference |
| Provider logs sensitive data | High | Privacy/retention doc and safe logging review |
| HomeTusk acceptance assumes provider tests are enough | Medium | Provider tests necessary but not sufficient; HomeTusk review remains separate |

## Dependencies

- HomeTusk artifact gate package, especially:
  - accepted decision/action taxonomy;
  - golden scenario fixtures;
  - eval rubric;
  - provider readiness checklist;
  - privacy/retention questions;
  - provider initiative brief.
- Existing AI Platform `/v1/decide` route.
- Existing provider schemas under `contracts/schemas/**`.
- Existing RouterV2 / assist / partial trust code paths.
- Existing pytest setup.
- Current development rules: `AGENTS.md`, `CLAUDE.md`, `CODEX.md` if present.

## Gates

### Gate A — Initiative scope

Approve only if:

- initiative remains provider-side;
- HomeTusk remains read-only input;
- narrow corridor is preserved;
- production multi-agent planner remains out of scope.

### Gate B — Execution commitment

Approve only if:

- work is decomposed into bounded provider tasks;
- contract impact is explicitly identified;
- eval fixture strategy is explicit;
- privacy/retention doc is included.

### Gate C — APPLY approval

Approve only if PLAN lists:

- exact provider files to change;
- exact tests/eval commands;
- schema impact or no-schema-impact decision;
- fixture import/source path;
- rollback strategy;
- no HomeTusk write operations.

### Gate D — Closure

Approve only if:

- implementation matches narrow corridor;
- seed fixtures pass with zero blocker failures;
- unsafe/broad/cross-household scenarios do not execute;
- privacy/retention posture is documented;
- provider contract changes, if any, are documented and versioned;
- HomeTusk handoff notes are clear.

## Success Signals

- Domain Planner v1 can reliably handle simple task and shopping seed scenarios.
- Planner clarifies instead of guessing when context is ambiguous.
- Planner rejects unsafe or unsupported scenarios.
- Eval output is reviewable by HomeTusk.
- Provider implementation remains isolated from HomeTusk runtime.
- The next HomeTusk-side decision can be based on evidence, not demo behavior.

## Non-Goals Reminder

This initiative does not approve:

- HomeTusk `natural_command` implementation;
- Mobile AI Command Center;
- direct mobile to AI Platform;
- broad autonomous household planning;
- production multi-agent orchestration.
