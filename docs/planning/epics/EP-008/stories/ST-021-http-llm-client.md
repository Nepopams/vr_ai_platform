# ST-021: HTTP LLM Client Implementing LlmCaller Interface

**Epic:** EP-008 (Real LLM Client Integration)
**Status:** Ready
**Flags:** contract_impact=no, adr_needed=none, diagrams_needed=none

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-008/epic.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q4-production-hardening.md` |
| ADR-003 | `docs/adr/ADR-003-llm-model-policy-registry-and-escalation.md` |
| LlmCaller type | `llm_policy/models.py` |
| LLM policy runtime | `llm_policy/runtime.py` |
| LLM policy YAML | `llm_policy/llm-policy.yaml` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

The `LlmCaller` type is defined as `Callable[[CallSpec, str], str]` in `llm_policy/models.py`.
The runtime (`llm_policy/runtime.py`) supports caller injection via `set_llm_caller()` /
`get_llm_caller()`. Currently no real HTTP caller is registered. The policy YAML has
routing for `yandex_ai_studio` provider with placeholder env vars.

## User Value

As a platform developer, I want a real HTTP client that implements the `LlmCaller`
callable signature, so that the existing `run_task_with_policy` can call a real LLM
provider without any changes to the runtime.

## Scope

### In scope

- New module `llm_policy/http_caller.py` with a function/class implementing `LlmCaller`
- Supports `provider="yandex_ai_studio"` (primary) and `provider="openai_compatible"` (secondary)
- Reads `base_url` from `CallSpec` or env var `LLM_BASE_URL`
- Reads API key from env var `LLM_API_KEY` (never hardcoded, never logged)
- Respects `CallSpec.timeout_ms`, `CallSpec.temperature`, `CallSpec.max_tokens`, `CallSpec.model`
- Raises `TimeoutError` on timeout, `LlmUnavailableError` on connection failure
- No raw user text or raw LLM output in logs (privacy guarantee)

### Out of scope

- Streaming responses
- Token counting / cost tracking
- Multiple provider implementations beyond yandex_ai_studio and openai_compatible
- Retry logic (handled by `llm_policy/runtime.py`)
- Registration/startup hook (ST-022)

---

## Acceptance Criteria

### AC-1: Caller sends correct HTTP request
```
Given a CallSpec with provider="yandex_ai_studio", model="gpt-oss-20b", temperature=0.2
When the caller is invoked with prompt "test"
Then it sends a POST to the configured base_url with correct model/temperature/max_tokens
And returns the response text
```

### AC-2: Caller raises TimeoutError on timeout
```
Given a CallSpec with timeout_ms=100
When the LLM does not respond within 100ms
Then TimeoutError is raised
```

### AC-3: Caller raises LlmUnavailableError on connection failure
```
Given an unreachable base_url
When the caller is invoked
Then LlmUnavailableError is raised
```

### AC-4: No secrets in logs
```
Given LLM_API_KEY is set
When the caller executes (success or failure)
Then no log line contains the API key value
```

### AC-5: All 228 existing tests pass
```
Given the test suite
When ST-021 changes are applied
Then all 228 tests pass and new tests also pass
```

---

## Test Strategy

### Unit tests (~8 new in `tests/test_http_llm_client.py`)
- `test_sends_correct_request_yandex`
- `test_sends_correct_request_openai_compatible`
- `test_returns_response_text`
- `test_timeout_raises_timeout_error`
- `test_connection_failure_raises_unavailable`
- `test_http_error_raises_unavailable`
- `test_no_api_key_in_logs`
- `test_respects_callspec_parameters`

### Regression
- Full test suite: 228 tests must pass

---

## Code Touchpoints

| File | Change |
|------|--------|
| `llm_policy/http_caller.py` | New: HTTP client implementing LlmCaller |
| `tests/test_http_llm_client.py` | New: unit tests |

---

## Dependencies

- None (foundational story)
- Blocks: ST-022, ST-023, ST-024
