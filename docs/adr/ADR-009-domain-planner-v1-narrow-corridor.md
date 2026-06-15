# ADR-009: Domain Planner v1 Narrow Household Corridor

**Status**: accepted
**Date**: 2026-06-15
**Initiative**: `INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor`
**Epic**: `EP-016`

## Context

HomeTusk accepted a `LIMITED-GO` artifact package for a narrow provider-side Domain Planner v1. AI Platform must remain a stateless, contract-driven decision provider. HomeTusk remains execution, guardrail, audit, and final acceptance authority.

The current provider contract version is `2.0.0`. The existing DecisionDTO schema supports `start_job`, `propose_create_task`, `propose_add_shopping_item`, and `clarify`, including multiple proposed actions under `start_job`. It does not provide first-class `reject`, `confirm`, or `answer` outcomes.

## Decision

AI Platform may proceed toward Domain Planner v1 only inside a narrow household command corridor:

- clear simple task creation;
- clear multi-item shopping addition;
- safe clarification;
- safe rejection mapping;
- optional confirmation only after contract governance if a first-class non-executing confirm outcome is needed.

The first runtime implementation should prefer current-schema mapping and must not change `contracts/**`, public API, or DecisionDTO semantics unless a dedicated contract workpack approves it.

### Current-Schema Mapping

| Domain Planner outcome | Provider representation |
| --- | --- |
| `execute/create_task` | `status=ok`, `action=start_job`, `job_type=create_task`, proposed `propose_create_task` action |
| `execute/add_shopping_items` | `status=ok`, `action=start_job`, `job_type=add_shopping_item`, repeated proposed `propose_add_shopping_item` actions |
| `clarify` | `status=clarify`, `action=clarify` |
| `reject` | Temporary non-executing safe rejection using current schema; classify in eval as `reject_mapped_to_error` |
| `confirm` | Not implemented in current schema; clarify/no-op or contract HOLD |
| `answer` | Not implemented; clarify/block until HomeTusk answer contract exists |

### Runtime Guardrails

Any future runtime work must:

- preserve `/v1/decide` request and response schema validation;
- preserve ASR as transcription-only and never auto-call `/v1/decide`;
- avoid direct HomeTusk mutation;
- avoid direct mobile/web calls to AI Platform;
- keep broad planning, reschedule, completion, status answer, workload optimization, and production multi-agent planning out of scope;
- provide deterministic eval evidence before Gate D;
- avoid raw user text or raw LLM output in logs, reports, review notes, and generated artifacts.

## Contract Implications

No contract change is approved by this ADR.

Per ADR-001, a later contract workpack is required before:

- adding first-class `reject`, `confirm`, `answer`, or plural shopping actions;
- adding required planner/model/prompt provenance fields to DecisionDTO;
- changing capability enums or `/v1/decide` request shape;
- changing the meaning of `start_job`, `propose_*`, or `clarify`.

## Diagram Implications

A provider flow diagram is required before runtime APPLY. It must show that AI Platform returns a provider decision only; HomeTusk validates, guards, logs, and executes.

## Privacy Implications

Domain Planner v1 may process reviewed text and minimal household context only. Raw audio is outside the planner flow. Raw text logging remains disabled by default and must not be enabled for production planner flows without a separate privacy/security decision.

## Consequences

### Positive

- Keeps the initiative aligned with the HomeTusk `LIMITED-GO` posture.
- Reuses current multi-item proposed action shape where possible.
- Prevents accidental broad planner or direct execution behavior.
- Makes reject/confirm gaps explicit before implementation.

### Negative

- Current-schema reject mapping is semantically rough.
- Confirmation scenarios cannot be represented first-class without contract work.
- Final acceptance remains blocked until deterministic eval evidence exists.

## Alternatives Considered

### Add first-class outcomes immediately

Rejected for ST-048. This requires contract governance, versioning, fixtures, and consumer alignment.

### Treat all unsupported scenarios as clarify

Rejected as a complete solution. Clarify is safe but does not fully satisfy HomeTusk reject semantics; reject-like scenarios must be explicitly classified in eval and may require a contract follow-up.

### Build a broad multi-agent planner

Rejected. It conflicts with the initiative scope and HomeTusk `LIMITED-GO` recommendation.
