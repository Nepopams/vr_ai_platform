# Workpack — ST-007: Partial Trust Rollout Runbook

**Status:** Ready
**Story:** `docs/planning/epics/EP-003/stories/ST-007-rollout-documentation.md`
**Epic:** `docs/planning/epics/EP-003/epic.md`
**Initiative:** `docs/planning/initiatives/INIT-2026Q2-partial-trust.md`

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q2-partial-trust.md` |
| ADR-004 | `docs/adr/ADR-004-partial-trust-corridor.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

A rollout runbook enabling operators to safely enable, tune, and disable the partial trust corridor in production.

---

## Files to Change

### New files (CREATE)

| File | Description |
|------|-------------|
| `docs/operations/partial-trust-runbook.md` | Rollout runbook |

### Key files to READ (context, not modify)

| File | Why |
|------|-----|
| `routers/partial_trust_config.py` | All env vars with defaults |
| `docs/adr/ADR-004-partial-trust-corridor.md` | Rollout plan (0.01→0.05→0.10) |
| `scripts/README-partial-trust-analyzer.md` | Analyzer usage for monitoring |
| `docs/planning/epics/EP-003/verification-report.md` | AC verification reference |

---

## Verification Commands

```bash
# 1. Runbook exists
test -f docs/operations/partial-trust-runbook.md && echo "OK" || echo "MISSING"

# 2. All env vars documented (cross-reference with config)
grep "PARTIAL_TRUST_ENABLED" docs/operations/partial-trust-runbook.md
grep "PARTIAL_TRUST_SAMPLE_RATE" docs/operations/partial-trust-runbook.md
grep "PARTIAL_TRUST_TIMEOUT_MS" docs/operations/partial-trust-runbook.md
grep "PARTIAL_TRUST_RISK_LOG_PATH" docs/operations/partial-trust-runbook.md

# 3. Full test suite (no regressions)
python3 -m pytest tests/ -v
```

---

## DoD Checklist

- [ ] Runbook documents all environment variables with types, defaults, valid ranges
- [ ] Runbook documents sampling progression (0.01→0.05→0.10) with go/no-go criteria
- [ ] Runbook documents rollback procedure (kill-switch + verification)
- [ ] Runbook documents monitoring checklist with alarm thresholds
- [ ] Runbook documents prerequisites with artifact links
- [ ] No sensitive data in runbook (no API keys, secrets)
- [ ] No existing files modified

---

## Rollback

Delete `docs/operations/partial-trust-runbook.md`. No existing files modified.
