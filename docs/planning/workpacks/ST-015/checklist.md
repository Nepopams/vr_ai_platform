# ST-015: DoD Checklist

## Acceptance Criteria

- [ ] AC-1: CI runs `decision_log_audit` via release_sanity (`python -m skills.release_sanity` exits 0)
- [ ] AC-2: CI uses release_sanity orchestrator; individual `contract_checker`/`graph_sanity` steps removed; `schema_bump check` remains
- [ ] AC-3: Release sanity failure returns exit 1 with failed check name
- [ ] AC-4: `test_release_sanity_runs` and `test_release_sanity_includes_decision_log_audit` pass
- [ ] AC-5: All 202 existing tests + new tests pass (expect 204)

## Verification

```bash
python3 -m pytest tests/ -v --tb=short                       # 204 passed
python3 -m skills.release_sanity                              # exit 0
grep -c "release_sanity" .github/workflows/ci.yml             # 1
grep -c "skills.contract_checker" .github/workflows/ci.yml    # 0
grep -c "skills.graph_sanity" .github/workflows/ci.yml        # 0
```

## Invariants

- [ ] `contracts/` unchanged
- [ ] `skills/` unchanged
- [ ] `graphs/`, `routers/`, `agent_registry/` unchanged
