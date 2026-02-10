# ST-023: .env.example and LLM Configuration Documentation

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
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

ST-021 and ST-022 create the HTTP caller and bootstrap mechanism. Platform operators
need clear documentation on how to configure and run with a real LLM.

## User Value

As a platform operator, I want clear documentation on how to configure and run the
platform with a real LLM, so that I can set up the environment without guessing.

## Scope

### In scope

- `.env.example` file with all LLM-related env vars (placeholder values, not real secrets)
- `docs/guides/llm-setup.md`: prerequisites, env var reference, enable/disable, troubleshooting
- Update `.gitignore` to include `.env` if not already present
- Kill-switch documentation (`LLM_POLICY_ENABLED=false`)

### Out of scope

- Provider-specific setup guides (Yandex account creation)
- Cost estimates
- Production deployment guides

---

## Acceptance Criteria

### AC-1: .env.example contains all required vars
```
Given .env.example
When reviewed
Then it contains: LLM_POLICY_ENABLED, LLM_API_KEY, LLM_BASE_URL, LLM_PROVIDER,
     LLM_POLICY_PROFILE, LLM_POLICY_PATH, LLM_POLICY_ALLOW_PLACEHOLDERS,
     SHADOW_ROUTER_ENABLED, PARTIAL_TRUST_ENABLED
```

### AC-2: Guide covers enable/disable flow
```
Given docs/guides/llm-setup.md
When reviewed
Then it describes: how to enable LLM, how to disable (kill-switch), what happens on error
```

### AC-3: .env is in .gitignore
```
Given .gitignore
When reviewed
Then .env is listed
```

---

## Test Strategy

- Manual review
- No automated tests (docs-only)

---

## Code Touchpoints

| File | Change |
|------|--------|
| `.env.example` | New: env var template |
| `docs/guides/llm-setup.md` | New: LLM setup guide |
| `.gitignore` | Update: add .env if missing |

---

## Dependencies

- ST-021, ST-022 (needs to document what they created)
