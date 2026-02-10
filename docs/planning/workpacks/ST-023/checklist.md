# ST-023 Checklist

## Acceptance Criteria

- [ ] AC-1: `.env.example` contains LLM_POLICY_ENABLED, LLM_API_KEY, LLM_BASE_URL, LLM_PROVIDER, LLM_POLICY_PROFILE, LLM_POLICY_PATH, LLM_POLICY_ALLOW_PLACEHOLDERS, SHADOW_ROUTER_ENABLED, PARTIAL_TRUST_ENABLED
- [ ] AC-2: `docs/guides/llm-setup.md` covers enable/disable flow and kill-switch
- [ ] AC-3: `.env` listed in `.gitignore`

## DoD Items

- [ ] `.env.example` created with grouped sections and placeholder values
- [ ] `docs/guides/llm-setup.md` created with prerequisites, env reference, enable/disable, troubleshooting
- [ ] `.gitignore` updated with `.env` entry
- [ ] Full test suite passes (256 total, 0 new)
- [ ] No code files modified
