# ST-034 Checklist

## Acceptance Criteria

- [ ] AC-1: `GET /health` → 200 + `{"status": "ok", "version": "2.0.0"}`
- [ ] AC-2: `GET /ready` → 200 + `{"status": "ready", "checks": {"decision_service": "ok"}}`
- [ ] AC-3: `GET /ready` with broken service → 503 + `{"status": "not_ready", ...}`
- [ ] AC-4: All 270 existing tests pass

## DoD

- [ ] `app/routes/health.py` created
- [ ] `app/main.py` updated (include health router)
- [ ] `tests/test_health_ready.py` created (5 tests)
- [ ] 5 new tests pass
- [ ] 270 existing tests pass (275 total, 3 skipped)
- [ ] No modifications to forbidden paths
- [ ] No new dependencies added
