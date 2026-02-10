# Checklist — ST-031: Observability Documentation and Runbook

## Acceptance Criteria

- [ ] AC-1: Guide covers all 5 log types (pipeline_latency, fallback_metrics, shadow_router, assist, partial_trust_risk)
- [ ] AC-2: Guide includes aggregation instructions (run command + output interpretation)
- [ ] AC-3: All logging-related env vars documented

## DoD

- [ ] `docs/guides/observability.md` created
- [ ] All 5 primary log types documented with schemas
- [ ] Additional logs (decision, agent_run, shadow_agent_diff) mentioned
- [ ] Aggregation script section complete
- [ ] Privacy notes included (LOG_USER_TEXT, no raw text in fallback/partial trust logs)
- [ ] No invariant files modified
- [ ] No regression in existing tests (270 passed, 3 skipped)

## Verification

```bash
test -f docs/guides/observability.md && wc -l docs/guides/observability.md
source .venv/bin/activate && python3 -m pytest --tb=short -q
```
