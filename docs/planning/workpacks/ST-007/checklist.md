# ST-007 — AC / DoD Verification Checklist

## Acceptance Criteria

- [ ] AC-1: All env vars documented (type, default, description, valid range)
- [ ] AC-2: Sampling progression documented (0.01→0.05→0.10 with go/no-go)
- [ ] AC-3: Rollback procedure documented (kill-switch + verification)
- [ ] AC-4: Monitoring checklist with alarm thresholds
- [ ] AC-5: Prerequisites with artifact links
- [ ] AC-6: No sensitive data

## DoD

- [ ] Runbook exists: `test -f docs/operations/partial-trust-runbook.md`
- [ ] Env vars cross-referenced with `routers/partial_trust_config.py`
- [ ] No existing files modified
