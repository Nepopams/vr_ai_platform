# Sprint S09: API Foundation -- Pydantic Models, Versioned Path, Health Endpoints

**PI:** 2026Q1-PI02 (INIT-2026Q1-api-integration)
**Period:** TBD (5 calendar days, ~5 working days of Codex effort)
**Status:** Complete

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/pi/2026Q1-PI02/pi.md` |
| Roadmap | `docs/planning/strategy/roadmap.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |
| EP-011 epic | `docs/planning/epics/EP-011/epic.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q1-api-integration.md` |
| ADR-007 | `docs/adr/ADR-007-api-versioning.md` |
| S08 retro | `docs/planning/sprints/S08/retro.md` |

---

## Sprint Goal

Deliver the foundation of a production-grade versioned API: introduce Pydantic request/response models for the `/decide` endpoint (EP-011), add versioned path `/v1/decide` with API-Version header per ADR-007, and create health/readiness endpoints -- progressing INIT-2026Q1-api-integration from 0/5 to 3/5 stories.

---

## Committed Scope

| Story ID | Title | Epic | Type | Estimate | Owner | Dep | Notes |
|----------|-------|------|------|----------|-------|-----|-------|
| ST-032 | Pydantic models for CommandDTO and DecisionDTO | EP-011 | Code | 1 day | Codex | None | Foundation story. Add pydantic to deps, create models, update route. ~8 new tests. |
| ST-033 | Versioned API path `/v1/decide` with router prefix and version header | EP-011 | Code | 1 day | Codex | ST-032 (intra-sprint) | Router prefix, backward-compat, ADR-007 implementation. ~5 new tests. |
| ST-034 | Health and readiness endpoints (`/health`, `/ready`) | EP-011 | Code | 0.5 day | Codex | None (independent) | Liveness + readiness probes. ~5 new tests. |

**Total estimated effort:** 2.5 working days of Codex implementation.

Story specs:
- `docs/planning/epics/EP-011/stories/ST-032-pydantic-models.md`
- `docs/planning/epics/EP-011/stories/ST-033-versioned-api-path.md`
- `docs/planning/epics/EP-011/stories/ST-034-health-readiness.md`

### DoR Readiness Assessment

| Story | DoR Status | Notes |
|-------|------------|-------|
| ST-032 | Ready | No blockers. Pydantic bundled with FastAPI. 6 ACs testable. |
| ST-033 | Ready | Depends on ST-032 (intra-sprint). ADR-007 created. 5 ACs testable. |
| ST-034 | Ready | No blockers. Independent. 4 ACs testable. |

All 3 stories pass DoR. No conditional agents needed beyond ADR-007 (already created).

---

## Stretch

| Story ID | Title | Condition |
|----------|-------|-----------|
| ST-035 | Structured error responses (problem+json) | If ST-032 + ST-033 complete ahead of schedule. Depends on ST-032. |

---

## Out of Scope (explicit)

- **OpenAPI spec generation** -- ST-036 is S10 (needs all endpoints finalized)
- **Webhook integration** -- EP-012, S10-S11
- **Partial trust for create_task** -- EP-013, S11
- **Authentication / authorization** -- future initiative
- **Rate limiting** -- future initiative
- **Error response format changes** -- ST-035 is stretch or S10
- **Breaking changes to existing `/decide` path** -- backward-compat per ADR-007
- **Contract VERSION bump** -- deferred to S10 when API shape is finalized

---

## Capacity Notes

- **Pipeline model:** Same as S01-S08 (30/30 stories, 0 carry-overs).
- **Sprint size:** 3 stories (all code). Consistent with conservative velocity (3 stories/sprint).
- **Buffer:** ~50% implicit (2.5 days estimated in 5 calendar days).
- **Intra-sprint dependency:** ST-033 depends on ST-032. Execute ST-032 first, then ST-033. ST-034 is independent and can run in parallel with ST-032.
- **Gate interactions:** ~9 (3 per story x 3).
- **Test suite baseline:** 270 tests (270 passed, 3 conditional skipped). Expected growth: ~18 new tests (target: ~288).
- **S08 retro action items:**
  - Action #2 (update golden-dataset guide baseline metrics): Open, cosmetic, non-blocking for S09.
- **New dependency for ST-032:** Pydantic must be added to `pyproject.toml`. FastAPI already bundles Pydantic as a transitive dependency, so `pip show pydantic` should confirm it's available. Explicit declaration ensures it's not silently lost.

---

## Dependencies

| Dependency | Type | Impact | Status |
|------------|------|--------|--------|
| FastAPI framework (`pyproject.toml`) | External | ST-032 builds on FastAPI's Pydantic integration | Available |
| Pydantic library (transitive via FastAPI) | External | ST-032 needs explicit declaration + import | Available (implicit), needs pyproject.toml update |
| ADR-007 (API versioning strategy) | Internal | ST-033 implements this ADR | Created (Proposed) |
| Existing `app/routes/decide.py` | Internal | ST-032 modifies route handler | Available |
| Existing `app/services/decision_service.py` | Internal | ST-032 modifies service to accept Pydantic model | Available |
| Existing `app/main.py` | Internal | ST-033 modifies app factory for router prefix; ST-034 adds health router | Available |
| Contract schemas (`contracts/schemas/*.json`) | Internal | ST-032 models mirror these schemas | Available (2.0.0) |
| Existing tests (`tests/test_api_decide.py`) | Internal | ST-032/ST-033 must update these | Available (2 tests) |
| Human gate availability | Process | ~9 gate interactions | Accepted |

**No new external dependencies beyond Pydantic explicit declaration.**

---

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation | ROAM |
|------|-------------|--------|------------|------|
| Pydantic models diverge from jsonschema definitions | Medium | Medium | Dual validation (Pydantic + jsonschema) during migration; test both paths | Mitigate |
| FastAPI Pydantic version mismatch (v1 vs v2) | Low | Medium | PLAN phase: verify `pip show pydantic` version; use v2 API if available | Mitigate |
| Backward-compat `/decide` path adds complexity | Low | Low | Thin delegate to v1; single test verifies parity | Accept |
| Existing tests break from route signature change | Medium | Low | ST-032 updates all affected tests in same commit | Mitigate |
| ST-033 blocked if ST-032 takes longer than expected | Low | Medium | ST-034 (independent) can run in parallel; stretch ST-035 deferred | Accept |

---

## Execution Order (recommended)

**Recommended sequence:**

1. **ST-034** -- Health and readiness endpoints (independent, 0.5 day).
   *Rationale:* No dependencies. Quick win. Validates FastAPI setup works.

2. **ST-032** -- Pydantic models for CommandDTO / DecisionDTO (1 day).
   *Rationale:* Foundation story. Blocks ST-033. Largest effort.

3. **ST-033** -- Versioned API path `/v1/decide` (1 day).
   *Rationale:* Depends on ST-032. Implements ADR-007. Completes sprint goal.

**Timeline estimate:**

```
Day 1:  ST-034 (health/readiness) + ST-032 start (Pydantic models)
Day 2:  ST-032 complete
Day 3:  ST-033 (versioned path)
Day 4:  Buffer / stretch ST-035 / review
Day 5:  Buffer / retro
```

---

## Demo Plan

### EP-011: Versioned REST API (initiative progress: 0/5 → 3/5)

1. **Pydantic models (ST-032)** -- Show `app/models/api_models.py`: CommandRequest, DecisionResponse with full nested structure. Demonstrate auto-validation on invalid input (422 response).

2. **Versioned path (ST-033)** -- Show `POST /v1/decide` returning valid response with `API-Version: v1` header. Show backward-compat `POST /decide` still works.

3. **Health endpoints (ST-034)** -- Show `GET /health` → `{"status": "ok", "version": "..."}`. Show `GET /ready` → `{"status": "ready", "checks": {"decision_service": "ok"}}`.

### Cross-cutting

4. **Test suite growth** -- All tests passing (target: ~288 tests, up from 270).
5. **ADR-007** -- API versioning strategy documented and implemented.
6. **Initiative progress** -- INIT-2026Q1-api-integration: 3/5 EP-011 stories done. EP-012 pending (S10-S11).

---

## Gate Ask (Gate B)

**Requesting PO approval for:**

1. **Sprint Goal:** Deliver the API foundation: Pydantic models, versioned path `/v1/decide`, health/readiness endpoints.
2. **Committed scope:** 3 stories (all code) from EP-011. All pass DoR. One intra-sprint dependency (ST-033 → ST-032).
3. **Out-of-scope list:** As documented above. No error format changes (S10), no OpenAPI (S10), no webhooks (S10-S11).
4. **Risk posture:** All risks Low-Medium. Pydantic version mismatch mitigated via PLAN phase check.
5. **Execution model:** Same pipeline as S01-S08 (30/30 stories, 0 carry-overs). Conservative velocity (3 stories). 50% buffer.
6. **Significance:** First sprint of PI02. Establishes the versioned API foundation that all subsequent EP-011/EP-012 stories build on.

**Decision requested:** Approve sprint goal and committed scope to proceed with workpack generation for ST-034 (first in execution order).
