# Codex PLAN Prompt — ST-007: Partial Trust Rollout Runbook

## Role

You are a read-only explorer. You MUST NOT edit, create, or delete any files.

## Allowed commands (whitelist)

- `ls`, `find`
- `cat`, `head`, `tail`
- `rg`, `grep`
- `sed -n`
- `git status`, `git diff`

## Forbidden

- Any file modifications
- Package management, network access
- `git commit`, `git push`

## Environment

- Python binary: `python3` (NOT `python`)

## STOP-THE-LINE

If you discover something that contradicts the workpack assumptions, STOP and report it.

---

## Context

We are implementing ST-007: a rollout runbook for the partial trust corridor.

**Workpack:** `docs/planning/workpacks/ST-007/workpack.md`

**Key files (verified by Claude):**
- `routers/partial_trust_config.py` — all env vars with defaults
- `docs/adr/ADR-004-partial-trust-corridor.md` — rollout plan
- `scripts/README-partial-trust-analyzer.md` — analyzer usage
- `docs/planning/epics/EP-003/verification-report.md` — AC verification

---

## Exploration Tasks

### Task 1: All config env vars

```bash
cat routers/partial_trust_config.py
```

**Report:** List every env var name, default value, type, and valid range.

### Task 2: ADR-004 rollout section

```bash
rg -n "rollout\|0\.01\|0\.05\|0\.10\|kill.switch" docs/adr/ADR-004-partial-trust-corridor.md
```

**Report:** Extract rollout progression and kill-switch details.

### Task 3: Analyzer README (monitoring reference)

```bash
cat scripts/README-partial-trust-analyzer.md
```

**Report:** Extract key metrics for monitoring checklist: acceptance_rate, error_rate, intent_mismatch_rate, latency_p95, sampling progression criteria.

### Task 4: Verification report (prerequisites reference)

```bash
head -20 docs/planning/epics/EP-003/verification-report.md
```

**Report:** Confirm report exists and contains all 4 ACs passed.

### Task 5: LLM policy dependency

```bash
rg -n "LLM_POLICY_ENABLED\|is_llm_policy_enabled" routers/partial_trust_candidate.py | head -5
```

**Report:** Confirm LLM_POLICY_ENABLED is required for candidate generation.

### Task 6: Existing operations docs

```bash
ls docs/operations/ 2>/dev/null || echo "directory does not exist"
```

**Report:** Check if `docs/operations/` exists. If not, note that it needs to be created.

---

## Expected Output

Produce a numbered report (Task 1 through Task 6) with:
- Complete env var inventory
- Rollout progression from ADR-004
- Monitoring metrics from analyzer README
- Any STOP-THE-LINE issues
