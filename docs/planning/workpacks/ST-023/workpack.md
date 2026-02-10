# Workpack — ST-023: .env.example and LLM Configuration Documentation

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-008/epic.md` |
| Story | `docs/planning/epics/EP-008/stories/ST-023-env-example-llm-docs.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

Platform operators have a complete `.env.example` reference with all env vars,
a step-by-step LLM setup guide, and `.env` protected from accidental commits.

## Acceptance Criteria

- AC-1: `.env.example` contains all LLM-related env vars (at minimum: LLM_POLICY_ENABLED,
  LLM_API_KEY, LLM_BASE_URL, LLM_PROVIDER, LLM_POLICY_PROFILE, LLM_POLICY_PATH,
  LLM_POLICY_ALLOW_PLACEHOLDERS, SHADOW_ROUTER_ENABLED, PARTIAL_TRUST_ENABLED)
- AC-2: `docs/guides/llm-setup.md` covers enable/disable flow and kill-switch
- AC-3: `.env` is listed in `.gitignore`

---

## Files to Change

| File | Action | Description |
|------|--------|-------------|
| `.env.example` | NEW | Env var template with all platform variables, grouped by section |
| `docs/guides/llm-setup.md` | NEW | LLM setup guide: prerequisites, env var reference, enable/disable, troubleshooting |
| `.gitignore` | UPDATE | Add `.env` entry |

## Files NOT Modified (invariants)

- `llm_policy/*.py` — no code changes
- `routers/*.py` — no code changes
- `app/logging/*.py` — no code changes
- `tests/*` — no tests (docs-only story)

---

## Implementation Plan

### Step 1: Create `.env.example`

Grouped sections with descriptive comments:
1. **LLM Core** — LLM_POLICY_ENABLED, LLM_API_KEY, LLM_BASE_URL, LLM_POLICY_PROFILE,
   LLM_POLICY_PATH, LLM_POLICY_ALLOW_PLACEHOLDERS
2. **Agent Runner** — LLM_PROVIDER, LLM_MODEL, LLM_TEMPERATURE, LLM_TIMEOUT_MS,
   LLM_MAX_OUTPUT_TOKENS, LLM_STORE, LLM_PROJECT, LLM_AGENT_RUNNER_HOST,
   LLM_AGENT_RUNNER_PORT, LLM_AGENT_RUNNER_URL
3. **Shadow Router** — SHADOW_ROUTER_ENABLED, SHADOW_ROUTER_TIMEOUT_MS,
   SHADOW_ROUTER_LOG_PATH, SHADOW_ROUTER_MODE
4. **Assist Mode** — ASSIST_MODE_ENABLED, ASSIST_NORMALIZATION_ENABLED,
   ASSIST_ENTITY_EXTRACTION_ENABLED, ASSIST_CLARIFY_ENABLED, ASSIST_TIMEOUT_MS,
   ASSIST_LOG_PATH
5. **Assist Agent Hints** — ASSIST_AGENT_HINTS_ENABLED, ASSIST_AGENT_HINTS_AGENT_ID,
   ASSIST_AGENT_HINTS_CAPABILITY, ASSIST_AGENT_HINTS_ALLOWLIST,
   ASSIST_AGENT_HINTS_SAMPLE_RATE, ASSIST_AGENT_HINTS_TIMEOUT_MS
6. **Partial Trust** — PARTIAL_TRUST_ENABLED, PARTIAL_TRUST_INTENT,
   PARTIAL_TRUST_SAMPLE_RATE, PARTIAL_TRUST_TIMEOUT_MS, PARTIAL_TRUST_PROFILE_ID,
   PARTIAL_TRUST_RISK_LOG_PATH
7. **Shadow Agent** — SHADOW_AGENT_INVOKER_ENABLED, SHADOW_AGENT_REGISTRY_PATH,
   SHADOW_AGENT_ALLOWLIST, SHADOW_AGENT_SAMPLE_RATE, SHADOW_AGENT_TIMEOUT_MS,
   SHADOW_AGENT_DIFF_LOG_ENABLED, SHADOW_AGENT_DIFF_LOG_PATH
8. **Agent Registry** — AGENT_REGISTRY_ENABLED, AGENT_REGISTRY_PATH,
   AGENT_REGISTRY_CORE_ENABLED
9. **Pipeline Logging** — PIPELINE_LATENCY_LOG_ENABLED, PIPELINE_LATENCY_LOG_PATH,
   FALLBACK_METRICS_LOG_ENABLED, FALLBACK_METRICS_LOG_PATH, DECISION_LOG_PATH,
   DECISION_TEXT_LOG_PATH, LOG_USER_TEXT, AGENT_RUN_LOG_ENABLED, AGENT_RUN_LOG_PATH
10. **Routing** — DECISION_ROUTER_STRATEGY

Default values from codebase. Placeholder for secrets (LLM_API_KEY="your-api-key-here").

### Step 2: Create `docs/guides/llm-setup.md`

Sections:
1. **Prerequisites** — Python 3, venv, API key from LLM provider
2. **Quick Start** — cp .env.example .env, set LLM_API_KEY, set LLM_POLICY_ENABLED=true
3. **Environment Variable Reference** — table with var, default, description (LLM core vars only)
4. **Enable/Disable Flow** — step-by-step enable, disable (kill-switch), what happens on error
5. **Bootstrap Process** — how bootstrap_llm_caller() works (3 guard clauses)
6. **Troubleshooting** — common issues (missing key, placeholders mode, disabled policy)

### Step 3: Update `.gitignore`

Add `.env` entry in a new "Secrets" section before the existing content, or at end.

---

## Verification

Manual review (no automated tests):
1. `.env.example` exists and contains all AC-1 variables
2. `docs/guides/llm-setup.md` exists and covers enable/disable flow
3. `.gitignore` contains `.env` line
4. Full test suite still passes (256 expected — no new tests)

```bash
# Full test suite (no regression)
source .venv/bin/activate && python3 -m pytest --tb=short -q

# Verify .env in .gitignore
grep -n "^\.env$" .gitignore

# Verify .env.example contains required vars
grep -c "LLM_POLICY_ENABLED\|LLM_API_KEY\|LLM_BASE_URL\|LLM_PROVIDER\|LLM_POLICY_PROFILE\|LLM_POLICY_PATH\|LLM_POLICY_ALLOW_PLACEHOLDERS\|SHADOW_ROUTER_ENABLED\|PARTIAL_TRUST_ENABLED" .env.example
```

---

## DoD Checklist

- [ ] `.env.example` created with all platform env vars
- [ ] `docs/guides/llm-setup.md` created with setup guide
- [ ] `.gitignore` updated with `.env`
- [ ] Full test suite passes (256)
- [ ] No code files modified

---

## Risks

| Risk | Mitigation |
|------|-----------|
| Env var missed | Full grep of `os.getenv`/`os.environ` in codebase → comprehensive list |
| Defaults wrong | Each default copied from source code, not guessed |
| .env.example committed with real secrets | Only placeholder values used |

## Rollback

Remove 2 new files + revert 1-line .gitignore change. No code impact.
