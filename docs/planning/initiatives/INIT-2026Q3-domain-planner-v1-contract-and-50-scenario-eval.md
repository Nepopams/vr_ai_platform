# INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval — Domain Planner v1 Contract + 50-Scenario Eval Gate

**Priority:** High
**Period:** 2026Q3 (PI TBD)
**Status:** Done (Gate A GO; Gate B GO; ST-052 Done; ST-053 Done; ST-054 Done; ST-055 Done; ST-056 Done; provider-side Gate D GO)
**Owner:** AI Platform engineering team
**Execution artifact:** `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-contract-and-50-scenario-eval.execution.md`
**Provider epic:** `docs/planning/epics/EP-017/epic.md`

## Context

AI Platform completed `INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor` as a provider-side initiative.

Provider closure delivered a current-schema narrow corridor:

- schema-valid simple `create_task` provider decisions;
- schema-valid multi-item shopping decisions through repeated `propose_add_shopping_item` actions;
- safe `clarify` for missing, ambiguous, contextual, confirm-required, or unsupported requests;
- current-schema safe rejection through `status=error`, `action=clarify` mapping;
- `/v1/decide` unchanged;
- ASR remains transcription-only;
- no HomeTusk state mutation, client integration, or production rollout.

HomeTusk then completed a provider evidence review and kept the result at **LIMITED-GO**.

HomeTusk accepted the provider evidence only as input for a narrower next step. It did **not** accept the provider work as sufficient for HomeTusk `natural_command` runtime, Mobile AI Command UX, production rollout, broad natural command execution, or full product GO.

The next required provider-side step is to consume the HomeTusk expanded 50-scenario suite, run deterministic provider evals, and make an explicit contract posture decision for first-class `reject` and non-executing `confirm`.

## HomeTusk Handoff Inputs

The implementation plan must consume the HomeTusk acceptance package as read-only consumer acceptance input.

Canonical HomeTusk artifacts:

```text
hometusk/docs/research/ai-command-capabilities/provider-domain-planner-v1-acceptance/
  README.md
  provider-evidence-review.md
  provider-eval-evidence-index.md
  expanded-golden-scenarios-v1/
    README.md
    context-fixtures-v1.yaml
    golden-scenarios-v1.yaml
  reject-confirm-answer-contract-posture.md
  natural-command-readiness-decision.md
  recommendation.md
```

Important HomeTusk decisions to preserve:

- final HomeTusk result is **LIMITED-GO**;
- provider evidence must be run against the expanded 50-scenario suite before any HomeTusk runtime acceptance claim;
- `reject_mapped_to_error` is acceptable only as temporary provider evidence, not as a HomeTusk runtime/product contract;
- first-class `reject` is required before HomeTusk runtime integration;
- non-executing `confirm` is required before assignment, reschedule, task-shopping linkage, and batch planning UX;
- `answer` remains blocked until HomeTusk defines a grounded read-only answer contract;
- HomeTusk runtime/mobile/API work remains blocked.

If HomeTusk artifacts are copied or imported into this repository, the import must record:

- source repository;
- source path;
- source revision or import date;
- fixture version;
- whether raw scenario text is present;
- privacy/redaction handling.

## Goal

Prepare AI Platform for HomeTusk's next acceptance decision by:

1. consuming the expanded 50-scenario HomeTusk suite;
2. running deterministic provider evals against all 50 scenarios;
3. preserving 0 blocker failures;
4. deciding provider-side contract posture for first-class `reject`;
5. deciding provider-side contract posture for non-executing `confirm`;
6. keeping `answer` blocked until HomeTusk answer contract governance starts;
7. keeping HomeTusk runtime/mobile/API work blocked.

This initiative may produce provider contract proposals or contract-governed implementation only after explicit gates. It must not silently change `/v1/decide` semantics.

## Scope

### In scope

#### 50-scenario evaluation

- Import or reference HomeTusk `expanded-golden-scenarios-v1` fixtures.
- Extend or reuse `scripts/evaluate_domain_planner_seed.py` for the 50-scenario suite.
- Produce a scenario-by-scenario provider eval report.
- Produce aggregate metrics and failure bucket counts.
- Preserve privacy-safe report output without raw scenario text in planning/review summaries.
- Record source metadata for fixtures.
- Record planner version, decision version, schema version, feature flags, and run command.
- Verify blocker failure count is zero or explicitly stop at HOLD.

#### Contract posture

- Evaluate whether current schema can remain sufficient for provider evidence only.
- Decide whether to open or execute a contract workpack for first-class `reject`.
- Decide whether to open or execute a contract workpack for non-executing `confirm`.
- Keep `answer` blocked unless HomeTusk answer contract governance has started.
- Document compatibility with repeated singular `propose_add_shopping_item` actions.
- Document whether plural `add_shopping_items` is needed in provider schema or can remain a HomeTusk taxonomy mapping.

#### Provider implementation / adaptation

Allowed only after Gate C, and only if PLAN proves the scope is required by the 50-scenario eval:

- improve deterministic planner behavior inside the narrow corridor;
- improve `clarify`/safe reject routing;
- preserve shopping item boundaries;
- improve current-schema mapping without breaking consumers;
- add first-class `reject` or non-executing `confirm` only through explicit contract governance.

#### Privacy and retention

- Update provider privacy/retention posture for the 50-scenario eval and any contract work.
- Confirm raw audio remains outside `/v1/decide`.
- Confirm ASR does not call `/v1/decide` automatically.
- Confirm `LOG_USER_TEXT=false` remains the default for validation and production-like runs.
- Keep prompt/response retention HOLD if external LLM or raw text retention is introduced without policy approval.

#### Documentation and handoff

- Produce provider-side evidence suitable for HomeTusk review.
- Produce a HomeTusk handoff note summarizing:
  - 50-scenario results;
  - blocker/non-blocker buckets;
  - contract decisions;
  - privacy posture;
  - remaining HOLD items;
  - recommended next HomeTusk action.

### Out of scope

- HomeTusk repository edits.
- HomeTusk `natural_command` runtime implementation.
- HomeTusk backend/OpenAPI/mobile changes.
- Direct HomeTusk state mutation.
- Direct mobile/web integration.
- Direct mobile/web calls to AI Platform.
- Production rollout/config changes.
- Broad multi-agent production planner.
- Full household workload optimizer.
- Natural reschedule auto-execute.
- Natural completion auto-execute.
- Read-only `answer_status` runtime behavior unless HomeTusk answer contract governance starts.
- Mixed task + shopping autonomous execution without non-executing confirmation semantics.
- Prompt-only behavior with no schema/eval evidence.

## Required Contract Decisions

### `reject`

Current state:

```text
reject_mapped_to_error = status=error, action=clarify
```

This is acceptable only as temporary provider evidence.

This initiative must decide one of:

```text
A. Keep current-schema mapping for eval only; open separate contract workpack before HomeTusk runtime.
B. Implement first-class provider reject now through contract-governed schema/version work.
C. HOLD because HomeTusk acceptance needs first-class reject before any further provider work.
```

### `confirm`

Current state:

```text
confirm = missing / not first-class
```

This initiative must decide one of:

```text
A. Defer confirm, keep confirm-required scenarios as clarify/no-execute.
B. Implement non-executing confirm now through contract-governed schema/version work.
C. HOLD because HomeTusk requires confirm before evaluating assignment/linkage/reschedule scenarios.
```

### `answer`

Current state:

```text
answer = missing / blocked
```

Default decision:

```text
Keep answer/status blocked until HomeTusk answer contract governance starts.
```

Any deviation requires explicit Gate B/Gate C rationale.

### `add_shopping_items`

Current state:

```text
Repeated singular propose_add_shopping_item actions preserve item boundaries.
```

This initiative must decide whether repeated singular actions remain sufficient for provider v1 eval, or whether a direct plural action should be proposed later.

## Acceptance Criteria

1. HomeTusk expanded 50-scenario suite is consumed or referenced with source metadata.
2. Deterministic eval runner can evaluate all 50 scenarios.
3. Eval report includes per-scenario and aggregate results.
4. Eval report includes failure bucket counts and blocker failure count.
5. Eval report records planner version, decision version, schema version, feature flags, fixture source, and run command.
6. Eval report does not leak raw scenario text into planning/review summaries.
7. Blocker failure count is 0 before Gate D, or initiative closes as HOLD/NO-GO.
8. Provider contract posture for first-class `reject` is explicit.
9. Provider contract posture for non-executing `confirm` is explicit.
10. `answer` remains blocked unless HomeTusk answer contract governance exists.
11. ASR remains transcription-only and does not call `/v1/decide`.
12. No HomeTusk files are modified.
13. No production rollout/config change is made.
14. Existing provider tests continue to pass.
15. HomeTusk handoff note is produced.

## Suggested Execution Shape

Codex should decompose this initiative after Gate A into provider-native epics/stories/workpacks.

Expected work areas may include:

- ST-A: fixture import/reference + 50-scenario eval runner plan;
- ST-B: provider contract posture decision for `reject` / `confirm` / `answer`;
- ST-C: optional contract-governed schema work if approved;
- ST-D: optional narrow planner adaptation if 50-scenario blockers require it;
- ST-E: privacy/retention update and HomeTusk handoff evidence.

No APPLY should start before Gate C.

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Provider overfits the original 10 scenarios | High | Evaluate against expanded 50-scenario suite |
| `reject_mapped_to_error` becomes product contract by accident | High | Explicit contract posture decision |
| Missing `confirm` blocks usable assignment/linkage UX | High | Contract posture decision before HomeTusk runtime work |
| Scenario eval leaks raw household text into reports | High | Privacy-safe report mode and redaction checks |
| Contract changes happen without versioning | High | Contract governance gate and ADR-001 compliance |
| HomeTusk runtime starts too early | High | HomeTusk remains blocked until separate acceptance/gate |
| Multi-agent expansion sneaks into provider work | Medium | Single narrow planner only; broad multi-agent out of scope |
| 50-scenario eval exposes broad failure | Medium | Close as HOLD/NO-GO rather than forcing runtime acceptance |

## Dependencies

- HomeTusk provider acceptance package with expanded 50 scenarios.
- Existing provider Domain Planner v1 narrow corridor closure.
- Existing `/v1/decide` route and schemas.
- Existing eval runner `scripts/evaluate_domain_planner_seed.py`.
- Existing tests, including `tests/test_domain_planner_v1_corridor.py`.
- Contract governance docs and ADR-001.
- Privacy/retention posture from Domain Planner v1 closure.

## Gates

### Gate A — Initiative scope

Approve only if:

- initiative remains provider-side;
- HomeTusk remains read-only input;
- expanded 50 scenarios are the eval target;
- HomeTusk runtime/mobile/API remains blocked;
- production rollout remains out of scope.

### Gate B — Execution commitment

Approve only if:

- fixture import/reference strategy is explicit;
- contract impact is explicitly classified;
- `reject` and `confirm` decision path is explicit;
- privacy/report redaction strategy is explicit;
- exact provider workpacks are defined.

### Gate C — APPLY approval

Approve only if PLAN lists:

- exact provider files to change;
- exact tests/eval commands;
- contract/schema/version impact or no-impact rationale;
- HomeTusk source revision/path;
- rollback strategy;
- no HomeTusk write operations;
- stop conditions for contract/runtime scope creep.

### Gate D — Closure

Approve only if:

- 50 scenarios are evaluated;
- blocker failure count is 0 or final decision is HOLD/NO-GO;
- contract posture for `reject` and `confirm` is explicit;
- `answer` status is explicit;
- privacy/retention posture is updated;
- ASR boundary is preserved;
- HomeTusk handoff notes are complete;
- no HomeTusk files are modified.

## Success Signals

- AI Platform can report deterministic results against 50 HomeTusk product scenarios.
- Unsafe, unsupported, cross-household, answer-style, and confirm-required scenarios do not execute.
- Contract decisions for `reject` and `confirm` are no longer ambiguous.
- HomeTusk can make the next decision from evidence rather than seed-demo confidence.

## Closure Summary

Closed on 2026-06-15 with provider-side Gate D GO.

Final provider evidence:

- 50 scenarios evaluated;
- 50 schema-valid decisions;
- 50 outcome matches;
- 0 blocker failure scenarios;
- 0 unsupported auto-execute;
- 0 cross-household references;
- first-class `reject` supported in schema and runtime;
- non-executing `confirm` supported in schema, with runtime UX deferred to a future HomeTusk integration initiative;
- `answer` remains blocked;
- HomeTusk handoff produced at `docs/planning/workpacks/ST-056/hometusk-handoff.md`.

## Non-Goals Reminder

This initiative does not approve:

- HomeTusk `natural_command` runtime;
- Mobile AI Command Center;
- direct mobile/web to AI Platform;
- broad household automation;
- production multi-agent orchestration;
- production rollout.
