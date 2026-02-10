# ST-021 Checklist

## Acceptance Criteria

- [ ] AC-1: Caller sends correct HTTP POST with model/temperature/max_tokens
- [ ] AC-2: TimeoutError raised on timeout
- [ ] AC-3: LlmUnavailableError raised on connection/HTTP error
- [ ] AC-4: No API key value in any log output
- [ ] AC-5: All 228 existing tests pass + ~8 new tests pass

## DoD Items

- [ ] `llm_policy/http_caller.py` — HttpLlmCaller + create_http_caller factory
- [ ] Implements `Callable[[CallSpec, str], str]` signature
- [ ] yandex_ai_studio provider (with OpenAI-Project header)
- [ ] openai_compatible provider (generic)
- [ ] Error mapping: httpx.TimeoutException → TimeoutError
- [ ] Error mapping: httpx.ConnectError/HTTPStatusError → LlmUnavailableError
- [ ] Privacy: no API key in logs (test verifies)
- [ ] Privacy: no raw user text / LLM output in logs
- [ ] `tests/test_http_llm_client.py` — 8 unit tests
- [ ] Full test suite passes (228 existing + 8 new = 236)
- [ ] No new dependencies added
- [ ] No existing files modified
