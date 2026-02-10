# EP-008: Real LLM Client Integration

**Status:** Ready
**Initiative:** `docs/planning/initiatives/INIT-2026Q4-production-hardening.md`
**Sprint:** TBD (S06 candidate)
**Owner:** TBD

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Roadmap | `docs/planning/strategy/roadmap.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q4-production-hardening.md` |
| ADR-003 | `docs/adr/ADR-003-llm-model-policy-registry-and-escalation.md` |
| ADR-004 | `docs/adr/ADR-004-partial-trust-corridor.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

The entire LLM pipeline (shadow router, assist mode, partial trust) is wired through
`llm_policy/runtime.py` which calls `get_llm_caller()`. Currently no real HTTP caller
is registered -- all LLM paths use stubs or return placeholders. The policy YAML
(`llm_policy/llm-policy.yaml`) already has routing for `yandex_ai_studio` with
`${YANDEX_FOLDER_ID}` placeholders. The `LlmCaller` type (`Callable[[CallSpec, str], str]`)
is defined in `llm_policy/models.py`.

To connect a real LLM, we need: (a) an HTTP client implementing `LlmCaller`,
(b) a startup hook that registers the caller, (c) env-var configuration and docs,
and (d) a smoke test to verify the end-to-end path.

## Goal

Enable real LLM calls through the existing scaffolding with zero behavior change
when the feature flag is off, full deterministic fallback on any error, and secrets
handled exclusively through environment variables.

## Scope

### In scope

- HTTP client implementing `LlmCaller` callable signature
- Support for `yandex_ai_studio` and `openai_compatible` providers
- Startup registration via bootstrap module
- Environment variable configuration (`LLM_API_KEY`, `LLM_BASE_URL`, `LLM_PROVIDER`)
- `.env.example` and LLM setup documentation
- Smoke test with real LLM (skipped in CI without credentials)
- Privacy: no secrets, raw user text, or raw LLM output in logs

### Out of scope

- Streaming responses
- Token counting / cost tracking
- Retry logic (handled by `llm_policy/runtime.py`)
- Multiple simultaneous callers
- Provider-specific account setup guides
- Production deployment infrastructure

## Stories

| Story ID | Title | Status | Flags |
|----------|-------|--------|-------|
| [ST-021](stories/ST-021-http-llm-client.md) | HTTP LLM client implementing LlmCaller interface | Ready | contract_impact=no, adr_needed=none, diagrams_needed=none |
| [ST-022](stories/ST-022-llm-caller-bootstrap.md) | LLM caller startup registration and env-var config | Ready (dep: ST-021) | contract_impact=no, adr_needed=none, diagrams_needed=none |
| [ST-023](stories/ST-023-env-example-llm-docs.md) | .env.example and LLM configuration documentation | Ready (dep: ST-021, ST-022) | contract_impact=no, adr_needed=none, diagrams_needed=none |
| [ST-024](stories/ST-024-smoke-test-real-llm.md) | Smoke test: real LLM round-trip through shadow router | Ready (dep: ST-021, ST-022) | contract_impact=no, adr_needed=none, diagrams_needed=none |

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| LlmCaller abstraction (ADR-003) | Internal | Done |
| Shadow router scaffolding | Internal | Done |
| Assist mode scaffolding | Internal | Done |
| llm_policy runtime/models | Internal | Done |
| Existing test suite (228 tests) | Internal | Passing |

### Story ordering

```
ST-021 (HTTP caller)
  |
  v
ST-022 (bootstrap/registration)
  |
  +---> ST-023 (docs)
  |
  +---> ST-024 (smoke test)
```

ST-021 first (foundation). ST-022 depends on ST-021. ST-023 and ST-024 depend on
ST-021+ST-022 but are independent of each other.

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| LLM API provider changes interface | Low | Medium | OpenAI-compatible generic format as fallback |
| Secrets leak into logs | Low | High | Privacy tests in ST-021; ADR-003 mandates no raw text |
| Real LLM tests flaky in CI | Low | Low | Conditional skip when no credentials |
| HTTP client dependency bloat | Low | Low | Use stdlib `urllib` or single dep (`httpx`) |

## Readiness Report

### Ready
- **ST-021** -- No blockers. All LlmCaller interface is defined. (~1 day)
- **ST-022** -- Depends on ST-021. Clear bootstrap pattern. (~0.5 day)
- **ST-023** -- Docs-only. Depends on ST-021+ST-022 for content. (~0.5 day)
- **ST-024** -- Depends on ST-021+ST-022. Conditional test. (~1 day)

### Conditional agents needed
- None (all flags negative)
