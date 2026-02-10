# Workpack: ST-021 — HTTP LLM Client Implementing LlmCaller Interface

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Story spec | `docs/planning/epics/EP-008/stories/ST-021-http-llm-client.md` |
| Epic | `docs/planning/epics/EP-008/epic.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q4-production-hardening.md` |
| Sprint | `docs/planning/sprints/S06/sprint.md` |
| ADR-003 | `docs/adr/ADR-003-llm-model-policy-registry-and-escalation.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

A new module `llm_policy/http_caller.py` that implements the `LlmCaller` callable
signature (`Callable[[CallSpec, str], str]`) using `httpx` to make real HTTP calls to
LLM providers. Supports `yandex_ai_studio` and `openai_compatible` provider formats.

---

## Acceptance Criteria Summary

1. Caller sends correct HTTP POST to `{base_url}/chat/completions` with model/temperature/max_tokens
2. Caller raises `TimeoutError` on HTTP timeout
3. Caller raises `LlmUnavailableError` on connection/HTTP errors
4. No API key value appears in any log output
5. All 228 existing tests pass; ~8 new tests pass

---

## Key Design Decisions

### Use httpx (already a project dependency)
`httpx` 0.28.1 is already used by `agent_runner/yandex_client.py`. No new dependency.

### Follow existing YandexAIStudioClient pattern
`agent_runner/yandex_client.py` shows the exact HTTP pattern:
- POST to `{base_url}/chat/completions`
- OpenAI-compatible format: `{"model": ..., "messages": [...], "temperature": ..., "max_tokens": ...}`
- `Authorization: Bearer {api_key}` header
- Yandex: also `OpenAI-Project: {project}` header

### LlmCaller signature contract
```python
LlmCaller = Callable[[CallSpec, str], str]
```
- Input: `CallSpec` (provider, model, temperature, max_tokens, timeout_ms, base_url, project) + prompt string
- Output: response text (the LLM's completion content)
- Errors: `TimeoutError` on timeout, `LlmUnavailableError` on connection/HTTP errors

### Error mapping
| httpx error | Maps to |
|-------------|---------|
| `httpx.TimeoutException` | `TimeoutError` |
| `httpx.ConnectError` | `LlmUnavailableError` |
| `httpx.HTTPStatusError` (4xx/5xx) | `LlmUnavailableError` |
| JSON parse failure (no choices) | `LlmUnavailableError` |

### API key source
Read from env var `LLM_API_KEY`. Passed to caller via factory function (not read inside caller itself — allows testing without env).

---

## Files to Change

| File | Action | Description |
|------|--------|-------------|
| `llm_policy/http_caller.py` | **New** | HTTP client implementing LlmCaller |
| `tests/test_http_llm_client.py` | **New** | ~8 unit tests |

### Files NOT changed (invariants)
- `llm_policy/models.py` — LlmCaller type unchanged
- `llm_policy/runtime.py` — caller injection unchanged
- `llm_policy/errors.py` — LlmUnavailableError unchanged
- `llm_policy/config.py` — no new config functions (ST-022 scope)
- `agent_runner/yandex_client.py` — reference only, not modified
- All existing test files — no modifications

---

## Implementation Plan

### Step 1: Create `llm_policy/http_caller.py`

```python
# llm_policy/http_caller.py
"""HTTP LLM client implementing LlmCaller interface."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict

import httpx

from llm_policy.errors import LlmUnavailableError
from llm_policy.models import CallSpec

_LOGGER = logging.getLogger("llm_policy.http_caller")


def create_http_caller(*, api_key: str | None = None) -> "HttpLlmCaller":
    """Factory function. Reads LLM_API_KEY from env if not provided."""
    key = api_key or os.getenv("LLM_API_KEY", "")
    if not key:
        raise ValueError("LLM_API_KEY is required")
    return HttpLlmCaller(api_key=key)


class HttpLlmCaller:
    """Callable implementing LlmCaller = Callable[[CallSpec, str], str]."""

    def __init__(self, *, api_key: str) -> None:
        self._api_key = api_key

    def __call__(self, spec: CallSpec, prompt: str) -> str:
        url = self._build_url(spec)
        headers = self._build_headers(spec)
        body = self._build_body(spec, prompt)
        timeout_s = (spec.timeout_ms / 1000) if spec.timeout_ms else 30.0

        # Log request metadata (NEVER the API key or prompt content)
        _LOGGER.info(
            "llm_http_request provider=%s model=%s url=%s timeout_s=%.1f",
            spec.provider,
            spec.model,
            url,
            timeout_s,
        )

        try:
            with httpx.Client(timeout=timeout_s) as client:
                response = client.post(url, headers=headers, json=body)
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise TimeoutError(f"LLM request timed out after {timeout_s}s") from exc
        except httpx.ConnectError as exc:
            raise LlmUnavailableError(f"LLM connection failed: {exc}") from exc
        except httpx.HTTPStatusError as exc:
            raise LlmUnavailableError(
                f"LLM HTTP error {exc.response.status_code}"
            ) from exc
        except httpx.HTTPError as exc:
            raise LlmUnavailableError(f"LLM HTTP error: {exc}") from exc

        return self._extract_content(response)

    def _build_url(self, spec: CallSpec) -> str:
        base = spec.base_url or os.getenv("LLM_BASE_URL", "")
        if not base:
            raise LlmUnavailableError("No base_url in CallSpec and LLM_BASE_URL not set")
        return f"{base.rstrip('/')}/chat/completions"

    def _build_headers(self, spec: CallSpec) -> Dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        # Yandex AI Studio uses OpenAI-Project header
        if spec.provider == "yandex_ai_studio" and spec.project:
            headers["OpenAI-Project"] = spec.project
        return headers

    def _build_body(self, spec: CallSpec, prompt: str) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "model": spec.model,
            "messages": [
                {"role": "user", "content": prompt},
            ],
        }
        if spec.temperature is not None:
            body["temperature"] = spec.temperature
        if spec.max_tokens is not None:
            body["max_tokens"] = spec.max_tokens
        return body

    def _extract_content(self, response: httpx.Response) -> str:
        try:
            data = response.json()
        except ValueError as exc:
            raise LlmUnavailableError("LLM response is not valid JSON") from exc
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LlmUnavailableError("Cannot extract content from LLM response") from exc
```

### Step 2: Create `tests/test_http_llm_client.py`

~8 tests using `unittest.mock.patch` to mock `httpx.Client`:

1. `test_sends_correct_request_yandex` — verify POST URL, headers (incl. OpenAI-Project), body
2. `test_sends_correct_request_openai_compatible` — verify no OpenAI-Project header
3. `test_returns_response_text` — mock successful response, check content extracted
4. `test_timeout_raises_timeout_error` — mock `httpx.TimeoutException`, verify `TimeoutError` raised
5. `test_connection_failure_raises_unavailable` — mock `httpx.ConnectError`, verify `LlmUnavailableError`
6. `test_http_error_raises_unavailable` — mock `httpx.HTTPStatusError`, verify `LlmUnavailableError`
7. `test_no_api_key_in_logs` — capture log output, assert API key string not present
8. `test_respects_callspec_parameters` — verify temperature, max_tokens, timeout_ms correctly mapped

Test pattern: use `unittest.mock.patch("httpx.Client")` to return a mock client
that returns controlled responses. Create `CallSpec` instances directly.

---

## Verification Commands

```bash
# Run new tests only
source .venv/bin/activate && python3 -m pytest tests/test_http_llm_client.py -v

# Run full test suite (must pass 228 + ~8 new)
source .venv/bin/activate && python3 -m pytest --tb=short -q

# Verify module imports cleanly
source .venv/bin/activate && python3 -c "from llm_policy.http_caller import create_http_caller, HttpLlmCaller; print('OK')"

# Verify no secrets in source
grep -r "LLM_API_KEY" llm_policy/http_caller.py | grep -v 'getenv\|environ\|LLM_API_KEY' || echo "No hardcoded keys"
```

---

## Tests

### New tests (~8)
| Test | Validates |
|------|-----------|
| `test_sends_correct_request_yandex` | AC-1: correct URL, headers, body for yandex_ai_studio |
| `test_sends_correct_request_openai_compatible` | AC-1: correct headers for openai_compatible (no project header) |
| `test_returns_response_text` | AC-1: extracts content from OpenAI-format response |
| `test_timeout_raises_timeout_error` | AC-2: httpx.TimeoutException → TimeoutError |
| `test_connection_failure_raises_unavailable` | AC-3: httpx.ConnectError → LlmUnavailableError |
| `test_http_error_raises_unavailable` | AC-3: HTTP 500 → LlmUnavailableError |
| `test_no_api_key_in_logs` | AC-4: log output does not contain API key value |
| `test_respects_callspec_parameters` | AC-1: temperature, max_tokens, timeout_ms correctly used |

### Regression
- All 228 existing tests must pass (AC-5)

---

## DoD Checklist

- [ ] `llm_policy/http_caller.py` created with `HttpLlmCaller` class and `create_http_caller` factory
- [ ] Implements `LlmCaller = Callable[[CallSpec, str], str]` signature exactly
- [ ] Supports `yandex_ai_studio` provider (with project header)
- [ ] Supports `openai_compatible` provider (generic)
- [ ] Raises `TimeoutError` on timeout (mapped from `httpx.TimeoutException`)
- [ ] Raises `LlmUnavailableError` on connection/HTTP errors
- [ ] No API key in logs (verified by test)
- [ ] No raw user text or LLM output in logs
- [ ] 8 new tests in `tests/test_http_llm_client.py` pass
- [ ] All 228 existing tests pass
- [ ] No new dependencies (httpx already in project)

---

## Risks

| Risk | Mitigation |
|------|------------|
| httpx mock complexity | Follow pattern from `test_llm_policy_runtime.py` (StubCaller). Mock at `httpx.Client` level. |
| API key leakage in error messages | `LlmUnavailableError` messages use generic text, never include key. Test verifies. |
| CallSpec.base_url is None in existing routes | Fallback to `LLM_BASE_URL` env var. Factory validates presence. |
| Response format varies by provider | Both yandex and openai use same `choices[0].message.content` format. |

---

## Rollback

- Delete `llm_policy/http_caller.py` and `tests/test_http_llm_client.py`
- No other files modified. Zero impact on existing behavior.
