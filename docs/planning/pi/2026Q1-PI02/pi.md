# PI Plan: 2026Q1-PI02 — API & Integration + Deepen LLM Trust

## Sources of Truth

- Product goal: `docs/planning/strategy/product-goal.md`
- Scope anchor: `docs/planning/releases/MVP.md`
- Roadmap: `docs/planning/strategy/roadmap.md`
- DoR: `docs/_governance/dor.md`
- DoD: `docs/_governance/dod.md`
- ADR index: `docs/adr/README.md`
- Contracts: `contracts/schemas/command.schema.json`, `contracts/schemas/decision.schema.json`
- Contract version: `contracts/VERSION` (currently `2.0.0`)
- Prior velocity: `docs/planning/sprints/S08/retro.md`

---

## 1. PI Charter

### Period

2026Q1-PI02: 8 weeks (4 development sprints S09-S12 + buffer/IP at end of S12)

### Context

MVP is complete: 30/30 stories, 270 tests (270 passed, 3 conditional skipped), 9/9 initiatives closed, all 4 product pillars addressed. The platform has a working FastAPI server with a single `POST /decide` endpoint, shadow LLM routing, assist mode, partial trust for `add_shopping_item`, golden dataset evaluation, CI pipeline, and full observability.

The PO has approved two strategic directions for this PI:

1. **API & Integration** — make the platform consumable by real clients (ConsumerApp, third-party systems) via a production-grade REST API with versioning, health checks, error contracts, and webhook/SDK foundations.
2. **Deepen LLM Trust** — expand partial trust to `create_task` intent, introduce configurable confidence thresholds, and build A/B comparison tooling (shadow vs production).

### PI Goal

**Make the AI Platform externally consumable and measurably smarter: a versioned API for consumers and expanded partial trust for a second intent, all without breaking MVP guarantees.**

### Non-Goals (Explicit)

- No new intents beyond `add_shopping_item` and `create_task`
- No new consumers beyond HomeTusk (multi-tenant support is future)
- No persistent user memory or personalization
- No autonomous agents or agent orchestration
- No UI/UX work
- No fine-tuning or model training
- No breaking changes to existing stable contracts without ADR + major version bump
- No WebSocket/streaming API (webhook is event-push only)

### MVP Exit Criteria (Maintained)

All MVP exit criteria remain enforced as invariants throughout PI02:

1. Platform does not break HomeTusk on any LLM error
2. All LLM integrations are fully disableable via feature flags
3. All decisions are traceable (trace_id, decision_log, structured JSONL)
4. Contracts remain stable (or versioned via ADR-001 SemVer policy)

---

## 2. PI Objectives

| # | Objective | Measurable Outcome | Pillar |
|---|-----------|-------------------|--------|
| OBJ-1 | Production-grade API for ConsumerApp | `POST /v1/decide` with versioned path, Pydantic request/response models, OpenAPI spec auto-generated, health endpoint, structured error responses. Integration test suite passes. | P1: Contract-first |
| OBJ-2 | API versioning and compatibility guard | API version in URL path (`/v1/`), version header in responses, contract diff CI check extended to cover API layer. ADR documenting versioning strategy. | P1: Contract-first |
| OBJ-3 | Webhook notification foundation | Webhook config model (URL, secret, events), `POST` callback on decision events, retry with backoff, kill-switch flag. At least 1 event type (`decision_completed`). | P4: Safe extensibility |
| OBJ-4 | Partial trust for `create_task` intent | Partial trust corridor extended to `create_task` with acceptance rules, shape validation, confidence threshold, sampling, risk logging. Flag-gated, deterministic fallback on any error. | P2: Deterministic by default |
| OBJ-5 | Configurable confidence thresholds | Per-corridor confidence thresholds configurable in `llm-policy.yaml` or env vars, with different defaults per intent. Observable in risk logs. | P3: Explainability & observability |
| OBJ-6 | A/B shadow vs production comparison tooling | Script/report that compares partial-trust accepted decisions vs baseline deterministic decisions using golden dataset + risk logs. Outputs match rate, entity diff, confidence distribution. | P3: Explainability & observability |

---

## 3. Initiatives

### INIT-2026Q1-api-integration (Priority: High)

**Goal:** Make AI Platform consumable by external clients through a versioned, production-grade REST API.

**Scope:**
- Versioned API path (`/v1/decide`)
- Pydantic request/response models (replacing raw dict validation)
- Auto-generated OpenAPI spec
- Health/readiness endpoints (`/health`, `/ready`)
- Structured error responses with error codes
- API versioning strategy (ADR)
- Webhook foundation (config, dispatch, retry, kill-switch)

**Out of scope:**
- Authentication/authorization (future initiative)
- Rate limiting (future initiative)
- gRPC or GraphQL
- WebSocket/streaming
- Multi-tenant API keys

**Product Pillars:** P1 (Contract-first decisioning), P4 (Safe extensibility)

### INIT-2026Q1-deepen-llm-trust (Priority: High)

**Goal:** Expand partial trust to a second intent (`create_task`), make confidence thresholds configurable, and build comparison tooling to measure LLM quality against baseline.

**Scope:**
- Extend `ALLOWED_CORRIDOR_INTENTS` to include `create_task`
- Create acceptance rules for `create_task` corridor (shape validation, field allowlist, confidence gate)
- Configurable per-intent confidence thresholds
- A/B comparison script (shadow/partial-trust logs vs baseline vs golden dataset)
- Extended golden dataset with `create_task` entries (10+ new entries)
- Updated observability guide

**Out of scope:**
- Partial trust for any intent beyond `create_task`
- LLM-first for clarify decisions
- Automatic threshold tuning
- Online A/B testing infrastructure (this is offline comparison)

**Product Pillars:** P2 (Deterministic by default), P3 (Explainability & observability)

---

## 4. Epic Candidates

### EP-011: Versioned REST API (INIT-2026Q1-api-integration)

**Goal:** Production-grade versioned API endpoint for ConsumerApp.

| # | Story Candidate | Flags |
|---|----------------|-------|
| ST-032 | Pydantic models for CommandDTO / DecisionDTO (replace raw dict I/O) | contract_impact=yes |
| ST-033 | Versioned API path `/v1/decide` with router prefix and version header | contract_impact=yes, adr_needed=lite |
| ST-034 | Health and readiness endpoints (`/health`, `/ready`) | contract_impact=yes |
| ST-035 | Structured error responses with error codes and problem+json format | contract_impact=yes |
| ST-036 | Auto-generated OpenAPI spec + CI snapshot baseline | contract_impact=no |

### EP-012: Webhook Notification Foundation (INIT-2026Q1-api-integration)

**Goal:** Event-push mechanism for consumers to receive decision notifications.

| # | Story Candidate | Flags |
|---|----------------|-------|
| ST-037 | Webhook config model (URL, secret, event types, enabled flag) | contract_impact=yes, adr_needed=lite |
| ST-038 | Webhook dispatch on `decision_completed` event (async, retry with backoff) | contract_impact=yes |
| ST-039 | Webhook kill-switch flag + observability logging | contract_impact=no |

### EP-013: Partial Trust for create_task (INIT-2026Q1-deepen-llm-trust)

**Goal:** Extend partial trust corridor to the `create_task` intent with full acceptance rules.

| # | Story Candidate | Flags |
|---|----------------|-------|
| ST-040 | Extend ALLOWED_CORRIDOR_INTENTS + create_task acceptance rules | adr_needed=amendment (ADR-004) |
| ST-041 | create_task LLM candidate generation (llm-policy task + profile) | contract_impact=no |
| ST-042 | create_task partial trust E2E test + risk log verification | contract_impact=no |

### EP-014: Confidence Thresholds & A/B Comparison (INIT-2026Q1-deepen-llm-trust)

**Goal:** Configurable confidence thresholds per intent and offline comparison tooling.

| # | Story Candidate | Flags |
|---|----------------|-------|
| ST-043 | Configurable per-intent confidence thresholds in llm-policy.yaml | contract_impact=no |
| ST-044 | A/B comparison script (risk logs vs golden dataset, match rate + diffs) | contract_impact=no |
| ST-045 | Extended golden dataset with create_task entries (10+ commands) | contract_impact=no |
| ST-046 | Updated observability guide for new corridors and comparison tooling | contract_impact=no |

---

## 5. Iteration Roadmap

### Sprint S09 (Week 1-2): API Foundation

**Sprint Goal:** Deliver versioned API endpoint with Pydantic models and structured errors.

| Epic | Stories | Dependencies |
|------|---------|-------------|
| EP-011 | ST-032, ST-033, ST-034 | None (builds on existing FastAPI app) |

**ADR needed:** ADR-007 API versioning strategy (lite)
**Contract impact:** Yes — new Pydantic models, versioned path, health endpoints

### Sprint S10 (Week 3-4): API Completion + Webhook Start

**Sprint Goal:** Complete API error handling, OpenAPI spec, and begin webhook foundation.

| Epic | Stories | Dependencies |
|------|---------|-------------|
| EP-011 | ST-035, ST-036 | S09: Pydantic models exist |
| EP-012 | ST-037 | S09: versioned API exists |

### Sprint S11 (Week 5-6): Webhook Completion + Partial Trust create_task

**Sprint Goal:** Complete webhook dispatch and extend partial trust to create_task.

| Epic | Stories | Dependencies |
|------|---------|-------------|
| EP-012 | ST-038, ST-039 | S10: webhook config model |
| EP-013 | ST-040 | None (builds on existing partial trust) |

**ADR needed:** ADR-004 amendment (create_task corridor)

### Sprint S12 (Week 7-8): LLM Trust Deepening + Integration Polish

**Sprint Goal:** Complete partial trust for create_task, build A/B comparison.

| Epic | Stories | Dependencies |
|------|---------|-------------|
| EP-013 | ST-041, ST-042 | S11: acceptance rules |
| EP-014 | ST-043 | S11: create_task corridor |

**Stretch:**

| EP-014 | ST-044, ST-045, ST-046 | S12: thresholds exist |

---

## 6. Capacity Assumptions

### Velocity Reference (S01-S08)

| Metric | Value |
|--------|-------|
| Average stories/sprint | 3.75 |
| Range | 3-6 |
| Carry-overs | 0 (across all 8 sprints) |
| Must-fix rate | 0 |

### PI02 Capacity Plan

- **Conservative velocity:** 3 stories/sprint
- **4 sprints x 3 stories = 12 stories committed**
- **Stretch:** 3 stories (ST-044, ST-045, ST-046) — only if capacity allows
- **Total backlog:** 15 stories (12 committed + 3 stretch)
- **Test growth target:** 270 → ~340-350 (estimated +70-80 new tests)

---

## 7. Risks (ROAM-lite)

| # | Risk | Impact | Probability | ROAM | Mitigation |
|---|------|--------|------------|------|------------|
| R1 | Pydantic models break existing `/decide` clients | High | Medium | Mitigate | Maintain backward-compatible unversioned path alongside `/v1/decide` |
| R2 | Webhook dispatch adds latency to decision pipeline | Medium | Medium | Mitigate | Async fire-and-forget dispatch, never block response |
| R3 | create_task acceptance rules more complex than shopping | Medium | High | Own | Start with strict allowlist (title + assignee_id only), expand iteratively |
| R4 | ADR-004 amendment scope creep toward generic corridor | Medium | Medium | Mitigate | PO gate on amendment, strict scope: only add `create_task` |
| R5 | OpenAPI spec drift from actual behavior | Low | Medium | Mitigate | CI step: generate + diff against baseline |
| R6 | Contract VERSION bump required (currently 2.0.0) | Medium | Low | Accept | Additive changes = minor bump 2.1.0, no breaking changes |
| R7 | Golden dataset insufficient for create_task evaluation | Low | Medium | Mitigate | Add 10+ create_task entries covering edge cases |
| R8 | A/B comparison script scope ambiguity | Low | Medium | Resolve | Define spec before S12 |

---

## 8. Dependencies

### Internal

| Dependency | Required By | Status |
|-----------|------------|--------|
| Existing FastAPI app (`app/main.py`, `app/routes/decide.py`) | EP-011 | Available |
| Existing JSON schemas (`contracts/schemas/`) | EP-011 | Available |
| ADR-001 (contract versioning policy) | EP-011 | Accepted |
| Existing partial trust corridor (`routers/partial_trust_*`) | EP-013 | Available |
| ADR-004 (partial trust corridor) | EP-013 | Accepted (needs amendment) |
| `llm-policy.yaml` task/profile structure | EP-013, EP-014 | Available |
| Golden dataset + evaluation script | EP-014 | Available (22 entries) |
| Observability JSONL logging framework | EP-012, EP-013 | Available |

### External

| Dependency | Required By | Risk |
|-----------|------------|------|
| Yandex AI Studio / OpenAI-compatible API | EP-013 | Medium (API stability) |
| FastAPI / Pydantic library | EP-011 | Low (already in pyproject.toml) |
| httpx library | EP-012 | Low (already in pyproject.toml) |

---

## 9. Decisions Required

| Decision | Type | Sprint | Status |
|----------|------|--------|--------|
| API versioning strategy (URL path vs header vs both) | ADR-007 (new) | S09 | To be created |
| Webhook payload contract (event envelope schema) | Contract | S10-S11 | To be created |
| ADR-004 amendment: extend corridor to create_task | ADR amendment | S11 | To be created |
| Contract VERSION bump 2.0.0 → 2.1.0 | Governance | S09 or S10 | TBD |

---

## 10. Gate Ask (Gate A — PI Scope)

**Requesting PO approval for:**

1. **PI Goal:** Make the AI Platform externally consumable and measurably smarter.
2. **Two initiatives:** INIT-2026Q1-api-integration + INIT-2026Q1-deepen-llm-trust.
3. **Four epics:** EP-011 (Versioned API), EP-012 (Webhook), EP-013 (Partial Trust create_task), EP-014 (Thresholds & A/B).
4. **12 committed + 3 stretch stories** across 4 sprints (S09-S12).
5. **Risk posture:** R3 (create_task complexity) owned, R1 (Pydantic migration) mitigated via backward compatibility.
6. **Contract VERSION bump:** minor 2.1.0 for additive changes.

**Next step after approval:** Epic decomposition for EP-011 (epic-decomposer), then conditional artifact agents (contract-owner for API contracts, adr-designer for ADR-007), then sprint planning for S09.
