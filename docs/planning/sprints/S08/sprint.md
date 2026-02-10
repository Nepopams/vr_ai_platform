# Sprint S08: Production Hardening Layer 3 -- Initiative Closure

**PI:** standalone (aligns with INIT-2026Q4-production-hardening)
**Period:** 2026-02-24 -- 2026-02-28 (5 calendar days, ~5 working days of Codex effort)
**Status:** Planning

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Roadmap | `docs/planning/strategy/roadmap.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |
| EP-008 epic | `docs/planning/epics/EP-008/epic.md` |
| EP-009 epic | `docs/planning/epics/EP-009/epic.md` |
| EP-010 epic | `docs/planning/epics/EP-010/epic.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q4-production-hardening.md` |
| S07 retro | `docs/planning/sprints/S07/retro.md` |

---

## Sprint Goal

Close INIT-2026Q4-production-hardening by completing the final 3 stories: smoke-test the real LLM path (EP-008), integrate quality evaluation into CI (EP-009), and document all observability outputs (EP-010) -- progressing the initiative from 8/11 to 11/11 stories.

---

## Committed Scope

| Story ID | Title | Epic | Type | Estimate | Owner | Dep | Notes |
|----------|-------|------|------|----------|-------|-----|-------|
| ST-024 | Smoke test: real LLM round-trip through shadow router | EP-008 | Code | 1 day | Codex | ST-021+ST-022 ✅ | Conditional tests (skipped without LLM key). ~5 new tests. |
| ST-027 | CI integration for golden dataset quality report | EP-009 | CI+Docs | 0.5 day | Codex | ST-025+ST-026 ✅ | CI step + golden-dataset guide. ~0 new unit tests (CI verification). |
| ST-031 | Observability documentation and runbook | EP-010 | Docs | 0.5 day | Codex | ST-028+ST-029+ST-030 ✅ | Docs-only, fast pipeline. ~0 tests. |

**Total estimated effort:** 2 working days of Codex implementation.

Story specs:
- `docs/planning/epics/EP-008/stories/ST-024-smoke-test-real-llm.md`
- `docs/planning/epics/EP-009/stories/ST-027-ci-golden-dataset.md`
- `docs/planning/epics/EP-010/stories/ST-031-observability-docs.md`

### DoR Readiness Assessment

| Story | DoR Status | Notes |
|-------|------------|-------|
| ST-024 | Ready | ST-021+ST-022 done. Conditional integration tests. 4 ACs testable. |
| ST-027 | Ready | ST-025+ST-026 done. CI step + docs. 3 ACs testable. |
| ST-031 | Ready | ST-028+ST-029+ST-030 done. Docs-only. 3 ACs testable. |

All 3 stories pass DoR. No conditional agents needed (all flags negative).

---

## Stretch

| Story ID | Title | Condition |
|----------|-------|-----------|
| (none) | -- | 3 committed stories at 2 days fit within 5-day sprint. Significant buffer used for initiative closure review, MEMORY update, and next-quarter candidate analysis. |

---

## Out of Scope (explicit)

- **Performance benchmarks with real LLM** -- out of EP-008 scope.
- **Automated pass/fail thresholds for quality** -- out of EP-009 scope.
- **Dashboard setup / Grafana / Prometheus** -- out of EP-010 scope.
- **CI with real LLM credentials** -- ST-024 tests skip in CI; real LLM testing is manual.
- **New intents or domains** -- out of initiative scope.
- **Changes to DecisionDTO or CommandDTO** -- stable boundary.
- **Hot-reloading of LLM config** -- out of scope.
- **Second consumer integration** -- separate initiative.

---

## Capacity Notes

- **Pipeline model:** Same as S01-S07 (27/27 stories, 0 carry-overs).
- **Sprint size:** 3 stories (1 code + 1 CI/docs + 1 docs). Smallest sprint, consistent with closure pattern.
- **Buffer:** ~60% implicit (2 days estimated in 5 calendar days). Extra buffer is intentional: initiative closure sprint, time for final review and documentation.
- **Bottleneck risk:** Human gate turnaround. No intra-sprint dependencies -- all 3 stories are independent.
- **Gate interactions:** ~9 (3 per story × 3).
- **S07 retro action items applied:**
  - Action #3 (story spec test counts drift): Story specs reference "228 tests" but actual baseline is 268. Sprint uses current count (268) per S06/S07 established practice.
- **Test suite baseline:** 268 tests passing. Expected growth: ~5 new tests (target: ~273). ST-024 adds conditional tests; ST-027 and ST-031 are docs/CI (0 tests).
- **Initiative closure:** Completing all 3 stories closes INIT-2026Q4-production-hardening (11/11) and all 3 epics (EP-008: 4/4, EP-009: 3/3, EP-010: 4/4).

---

## Dependencies

| Dependency | Type | Impact | Status |
|------------|------|--------|--------|
| ST-021 HTTP caller (`llm_policy/http_caller.py`) | Internal | ST-024 uses real HTTP caller. | Done (S06) |
| ST-022 Bootstrap (`llm_policy/bootstrap.py`) | Internal | ST-024 uses bootstrap to register caller. | Done (S07) |
| ST-025+ST-026 golden dataset + eval script | Internal | ST-027 integrates eval into CI. | Done (S06+S07) |
| ST-028+ST-029+ST-030 observability stack | Internal | ST-031 documents these. | Done (S06+S07) |
| `.github/workflows/ci.yml` | Internal | ST-027 adds step. | Exists |
| Human gate availability | Process | ~9 gate interactions. | Accepted |

**No external dependencies.** All work is self-contained within the repo.

---

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation | ROAM |
|------|-------------|--------|------------|------|
| ST-024 smoke tests need real LLM credentials | -- | Low | Tests skip without credentials. Development uses mocks; manual testing with real key is optional. | Accepted |
| ST-027 CI step interferes with existing CI steps | Low | Medium | Add as separate job/step, not modify existing ones. | Mitigated |
| ST-031 docs miss some log types | Low | Low | Grep all JSONL log paths during PLAN phase for completeness. | Mitigated |
| Story spec test counts drift ("228" vs actual 268) | Low | Low | Established practice: use current count (268). Action #3 from S07 retro. | Accepted |
| Codex sandbox lacks pytest (permanent) | -- | Low | Accepted. Verification during Claude review. | Accepted |

---

## Execution Order (recommended)

**Recommended sequence:**

1. **ST-024** -- Smoke test with real LLM (EP-008, code).
   *Rationale:* Only code story. Largest effort (1 day). Foundation verification.

2. **ST-027** -- CI integration for quality report (EP-009, CI+docs).
   *Rationale:* Independent. CI modification + docs guide. Medium effort (0.5 day).

3. **ST-031** -- Observability docs and runbook (EP-010, docs).
   *Rationale:* Independent. Pure docs. Fastest story (0.5 day). Natural closure.

**Timeline estimate:**

```
Day 1:  ST-024 (smoke test)
Day 2:  ST-027 (CI + golden-dataset guide) + ST-031 (observability docs)
Day 3:  Buffer / initiative closure review
Day 4:  Buffer / next-quarter candidate analysis
Day 5:  Buffer / retro
```

---

## Demo Plan

### EP-008: Real LLM Client Integration (initiative complete: 4/4)
1. **Smoke test module** -- Show `tests/test_llm_integration_smoke.py`: tests skip gracefully without credentials. Demonstrate with mock.
2. **Kill-switch verification** -- Show test proving `LLM_POLICY_ENABLED=false` prevents any LLM call.

### EP-009: Golden Dataset Quality Evaluation (initiative complete: 3/3)
3. **CI step** -- Show updated `.github/workflows/ci.yml` with quality-eval step.
4. **Golden dataset guide** -- Show `docs/guides/golden-dataset.md`: run locally, add entries, interpret report.

### EP-010: Pipeline Observability (initiative complete: 4/4)
5. **Observability runbook** -- Show `docs/guides/observability.md`: all 5 log types, schemas, aggregation instructions.
6. **Env var reference** -- All logging env vars documented.

### Cross-cutting
7. **Test suite growth** -- All tests passing (target: ~273 tests, up from 268).
8. **Initiative closure** -- INIT-2026Q4: 11/11 stories done. All 3 epics closed (EP-008: 4/4, EP-009: 3/3, EP-010: 4/4).
9. **Platform status** -- 9 initiatives closed, 30/30 stories across 8 sprints, 0 carry-overs.

---

## Gate Ask (Gate B)

**Requesting PO approval for:**

1. **Sprint Goal:** Close INIT-2026Q4-production-hardening by completing the final 3 stories across 3 epics.
2. **Committed scope:** 3 stories (1 code + 1 CI/docs + 1 docs) across 3 epics. All pass DoR. No intra-sprint dependencies.
3. **Out-of-scope list:** As documented above.
4. **Risk posture:** All risks Low. No real LLM credentials required for CI. Story spec drift handled by established practice.
5. **Execution model:** Same pipeline as S01-S07 (27/27 stories, 0 carry-overs). Smallest sprint (3 stories, 2 days effort) with 60% buffer for initiative closure.
6. **Significance:** Closes INIT-2026Q4-production-hardening (11/11 stories), completing all 3 epics. After S08, **all 9 initiatives are closed** across the full roadmap (NOW + NEXT + LATER + CURRENT phases). Platform reaches production-ready state.

**Decision requested:** Approve sprint goal and committed scope to proceed with workpack generation for ST-024 (first in execution order).
