# Sprint S06: Production Hardening Foundations -- LLM Client, Golden Dataset, Observability

**PI:** standalone (aligns with INIT-2026Q4-production-hardening)
**Period:** 2026-02-10 -- 2026-02-17 (5 calendar days, ~5 working days of Codex effort)
**Status:** Complete

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
| Initiative (production-hardening) | `docs/planning/initiatives/INIT-2026Q4-production-hardening.md` |
| ADR-003 (LLM policy) | `docs/adr/ADR-003-llm-model-policy-registry-and-escalation.md` |
| ADR-004 (partial trust) | `docs/adr/ADR-004-partial-trust-corridor.md` |
| S05 retro (action items) | `docs/planning/sprints/S05/retro.md` |

---

## Sprint Goal

Lay the foundation for production hardening across all three epics by delivering a real HTTP LLM client (EP-008), an expanded golden dataset for quality evaluation (EP-009), and pipeline-wide latency and fallback observability instrumentation (EP-010) -- establishing the first sprint of INIT-2026Q4-production-hardening.

---

## Committed Scope

| Story ID | Title | Epic | Type | Estimate | Owner | Dep | Notes |
|----------|-------|------|------|----------|-------|-----|-------|
| ST-021 | HTTP LLM client implementing LlmCaller interface | EP-008 | Code | 1 day | Codex | None | Foundation for real LLM calls. ~8 new tests. |
| ST-025 | Expand golden dataset to 20+ commands | EP-009 | Code | 0.5 day | Codex | None | Expands from 14 to 20+ entries. ~3 new tests. |
| ST-028 | Pipeline-wide latency instrumentation | EP-010 | Code | 1 day | Codex | None | Adds per-step timing to core pipeline. ~6 new tests. |
| ST-029 | Unified fallback and error rate structured logging | EP-010 | Code | 1 day | Codex | None | Unified LLM outcome tracking. ~6 new tests. |

**Total estimated effort:** 3.5 working days of Codex code implementation.

Story specs:
- `docs/planning/epics/EP-008/stories/ST-021-http-llm-client.md`
- `docs/planning/epics/EP-009/stories/ST-025-expand-golden-dataset.md`
- `docs/planning/epics/EP-010/stories/ST-028-pipeline-latency-instrumentation.md`
- `docs/planning/epics/EP-010/stories/ST-029-unified-fallback-metrics.md`

### DoR Readiness Assessment

| Story | DoR Status | Notes |
|-------|------------|-------|
| ST-021 | Ready | No blockers. LlmCaller interface defined in `llm_policy/models.py`. 5 ACs testable. Test strategy: 8 unit tests. |
| ST-025 | Ready | No blockers. Existing dataset (14 entries) is foundation. 5 ACs testable. Test strategy: 3 unit tests. Backward-compatible additions only. |
| ST-028 | Ready | No blockers. Core pipeline exists. 6 ACs testable. Test strategy: 6 unit tests. Follows existing logging patterns. |
| ST-029 | Ready | No blockers. Reads from existing components. 6 ACs testable. Test strategy: 6 unit tests. Follows existing logging patterns. |

All 4 stories pass DoR. No discovery stories needed. No conditional agents needed (all flags negative: contract_impact=no, adr_needed=none, diagrams_needed=none).

---

## Stretch

| Story ID | Title | Condition |
|----------|-------|-----------|
| (none) | -- | 4 committed stories at 3.5 days fit within 5-day sprint with buffer. If stories complete early, use buffer for review quality, retro, and candidate analysis for S07 (ST-022, ST-026, ST-030). |

---

## Out of Scope (explicit)

- **LLM caller startup registration** (ST-022) -- depends on ST-021, scheduled for S07.
- **.env.example and LLM docs** (ST-023) -- depends on ST-021+ST-022, scheduled for S07.
- **Smoke test with real LLM** (ST-024) -- depends on ST-021+ST-022, scheduled for S08.
- **Quality evaluation script** (ST-026) -- depends on ST-025, scheduled for S07.
- **CI integration for quality report** (ST-027) -- depends on ST-025+ST-026, scheduled for S08.
- **Aggregation script for latency/fallback** (ST-030) -- depends on ST-028+ST-029, scheduled for S07.
- **Observability documentation** (ST-031) -- depends on ST-028+ST-029+ST-030, scheduled for S08.
- **Streaming LLM responses** -- out of EP-008 scope entirely.
- **Token counting / cost tracking** -- out of EP-008 scope.
- **Real-time metrics / Prometheus / Grafana** -- out of EP-010 scope.
- **LLM-specific golden answers** -- out of EP-009 scope.
- **Changes to DecisionDTO or CommandDTO** -- stable boundary.
- **New intents or domains** -- out of initiative scope.
- **Agent invocation from core pipeline** -- Phase 2, separate initiative.

---

## Capacity Notes

- **Pipeline model:** Claude generates workpacks and prompts, Human gates, Codex implements. Same proven model as S01-S05 (19/19 stories, 0 carry-overs).
- **Sprint history:** 19 stories across 5 sprints, zero carry-overs, zero scope changes.
- **Codex throughput assumption:** ~1 code story per day (S01-S05 actuals). ST-025 is sub-day (data expansion, not complex logic).
- **This sprint:** 4 code stories = standard sprint size (consistent with S01-S04). All code, no docs stories this sprint.
- **Buffer:** ~30% implicit (3.5 days estimated effort in 5 calendar days). Conservative compared to S05 (6 stories / 5 days).
- **Bottleneck risk:** Human gate turnaround. Each code story requires 3 gate interactions (workpack approval, PLAN output relay, APPLY output relay + review). Total: ~12 gate interactions.
- **Parallelism opportunity:** All 4 stories are independent (no inter-story deps, no shared files). Maximum parallelism is architecturally possible but sequential execution is pragmatic per S05 retro learnings.
- **S05 retro action items applied:**
  - Secrets-check grep pattern refinement (carry from S03) -- relevant for ST-021 (API keys). Will verify in workpack.
  - Pipeline automation for parallel Codex execution -- not yet automated; sequential execution continues.
  - Check globber/validator consumption when adding data (carry from S04) -- relevant for ST-025 (golden dataset expansion). Will verify in workpack.
- **Test suite baseline:** 228 tests passing. Expected growth: ~23 new tests across 4 code stories (target: ~251 tests).
- **Three-epic spread:** Work spans EP-008, EP-009, EP-010 with zero code overlap. Each story touches distinct modules.

---

## Dependencies

| Dependency | Type | Impact | Status |
|------------|------|--------|--------|
| LlmCaller type definition (`llm_policy/models.py`) | Internal | ST-021 implements this interface. | Done |
| LLM policy runtime (`llm_policy/runtime.py`) | Internal | ST-021 must be compatible with `set_llm_caller()`. | Done |
| ADR-003 (LLM model policy) | Internal | ST-021 follows provider routing policy. | Accepted |
| Golden dataset v1 (14 entries) | Internal | ST-025 expands this. | Done |
| Graph-sanity skill tests | Internal | ST-025 must not break existing 14-entry validation. | Passing |
| Core pipeline (`graphs/core_graph.py`) | Internal | ST-028 adds timing instrumentation. | Done |
| Shadow router log (`app/logging/shadow_router_log.py`) | Internal | ST-028, ST-029 follow same logging pattern. | Done |
| Partial trust risk log (`app/logging/partial_trust_risk_log.py`) | Internal | ST-029 reads status from existing components. | Done |
| Existing test suite (228 tests) | Internal | All changes must preserve. | Passing |
| Human gate availability | Process | ~12 gate interactions across 4 stories. | Accepted |
| No code overlap between stories | Internal | All 4 stories touch distinct files. | Verified |

**No external dependencies.** All work is self-contained within the repo.

---

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation | ROAM |
|------|-------------|--------|------------|------|
| HTTP caller adds dependency (httpx/urllib) not currently in project | Low | Low | Use stdlib `urllib.request` or check existing deps first. Workpack will specify. | Mitigated |
| Secrets (LLM_API_KEY) accidentally logged in ST-021 | Low | High | Privacy AC mandates no API key in logs. Dedicated test `test_no_api_key_in_logs`. ADR-003 policy. | Mitigated |
| Golden dataset expansion breaks graph-sanity tests (ST-025) | Low | Medium | Backward-compatible additions only. AC-4 mandates all existing tests pass. S04 retro lesson: check globbers. | Mitigated |
| Core pipeline instrumentation (ST-028) changes behavior | Very Low | High | Instrumentation is read-only timing. No decision logic modified. Flag-gated. | Mitigated |
| Two stories touch `graphs/core_graph.py` (ST-028, ST-029) | Low | Medium | ST-028 adds timing wrapper; ST-029 adds fallback record emission. Different code locations. Execution order ST-028 before ST-029 avoids merge conflict. | Owned |
| Codex sandbox lacks pytest (permanent) | -- | Low | Accepted permanent limitation. Verification during Claude review. | Accepted |
| Adding data to fixture directories breaks globbers (S04 retro) | Low | Medium | Workpack for ST-025 will check glob patterns before placing new entries. | Mitigated |
| Three epics in one sprint increases context switching | Low | Low | Stories are independent. No inter-story deps. Sequential execution avoids context mixing. | Accepted |

---

## Execution Order (recommended)

All 4 stories are independent with no inter-story dependencies. However, two stories (ST-028 and ST-029) both touch `graphs/core_graph.py`, so ordering them sequentially avoids merge conflicts.

**Recommended sequence:**

1. **ST-021** -- HTTP LLM client (EP-008 foundation, standalone module).
   Workpack -> prompt-plan -> Codex PLAN -> prompt-apply -> Codex APPLY -> review -> merge.
   *Rationale:* Highest complexity (HTTP client + error handling + privacy). Fresh start.

2. **ST-025** -- Expand golden dataset (EP-009 foundation, data expansion).
   Workpack -> prompt-plan -> Codex PLAN -> prompt-apply -> Codex APPLY -> review -> merge.
   *Rationale:* Sub-day effort, quick win. Provides context switch from HTTP work.

3. **ST-028** -- Pipeline latency instrumentation (EP-010 foundation, touches core_graph.py).
   Workpack -> prompt-plan -> Codex PLAN -> prompt-apply -> Codex APPLY -> review -> merge.
   *Rationale:* Must merge before ST-029 to avoid core_graph.py conflicts.

4. **ST-029** -- Unified fallback metrics (EP-010 companion, also touches core_graph.py).
   Workpack -> prompt-plan -> Codex PLAN -> prompt-apply -> Codex APPLY -> review -> merge.
   *Rationale:* After ST-028 merge, core_graph.py has timing; ST-029 adds fallback record cleanly.

**Timeline estimate:**

```
Day 1:  ST-021 (HTTP LLM client)
Day 2:  ST-025 (golden dataset) + ST-028 start (latency instrumentation)
Day 3:  ST-028 complete + ST-029 (fallback metrics)
Day 4:  ST-029 complete + buffer
Day 5:  Buffer / retro / S07 candidate analysis
```

**Parallelism notes:**
- ST-021 and ST-025 could run in parallel (zero shared files).
- ST-028 and ST-029 should run sequentially (both touch `graphs/core_graph.py`).
- Sequential execution remains default per S05 retro (pragmatic for human gate flow).

---

## Demo Plan

At sprint end, the following should be demonstrable:

### EP-008: Real LLM Client
1. **HTTP caller module** -- Show `llm_policy/http_caller.py` implementing `LlmCaller` callable. Demonstrate: correct request construction for `yandex_ai_studio` and `openai_compatible` providers via unit tests.
2. **Error handling** -- Show `TimeoutError` raised on timeout, `LlmUnavailableError` on connection failure.
3. **Privacy guarantee** -- Show test confirming no API key appears in logs.

### EP-009: Golden Dataset Expansion
4. **Expanded dataset** -- Show `golden_dataset.json` with 20+ entries (up from 14). Show coverage: all 3 intents represented, hard cases (ambiguous, typo, multi-entity) present.
5. **Backward compatibility** -- Show all existing graph-sanity tests still pass.

### EP-010: Pipeline Observability
6. **Latency instrumentation** -- Show pipeline_latency record structure: trace_id, total_ms, step-level breakdown, llm_enabled flag. Show flag-gated disable.
7. **Fallback metrics** -- Show fallback_metrics record: trace_id, llm_outcome (success/fallback/error/skipped), per-component status. Show privacy guarantee (no raw text).

### Cross-cutting
8. **Test suite growth** -- All tests passing (target: ~251 tests, up from 228).
9. **Zero behavior regression** -- All existing pipeline behavior unchanged. All new instrumentation is additive and flag-gated.

**Initiative progress signal:** After S06 completion:
- INIT-2026Q4-production-hardening: 4 of 11 stories done (foundation layer for all 3 epics).
- All 3 epics have their foundation story completed, unblocking S07 stories (ST-022, ST-026, ST-030).

---

## Gate Ask (Gate B)

**Requesting PO approval for:**

1. **Sprint Goal:** Lay production hardening foundations across three epics -- real HTTP LLM client (EP-008), expanded golden dataset (EP-009), and pipeline latency + fallback observability (EP-010) -- as the first sprint of INIT-2026Q4-production-hardening.
2. **Committed scope:** 4 code stories (ST-021, ST-025, ST-028, ST-029) across 3 epics (EP-008, EP-009, EP-010). All 4 pass DoR. No conditional agents needed.
3. **Out-of-scope list:** As documented above -- no bootstrap/registration, no evaluation script, no aggregation, no docs stories, no streaming, no real-time metrics, no schema changes.
4. **Risk posture:** All risks Low or Very Low. Highest concern is `core_graph.py` contention between ST-028 and ST-029, mitigated by sequential execution (ST-028 first). Privacy risk in ST-021 mitigated by dedicated test and ADR-003 policy.
5. **Execution model:** Same pipeline as S01-S05 (19/19 stories, 0 carry-overs). Back to standard 4-story sprint (vs S05's ambitious 6). Conservative 30% buffer.
6. **Significance:** First sprint of a new initiative (INIT-2026Q4-production-hardening) after completing all 8 previous roadmap initiatives. Lays the groundwork for all 3 epics simultaneously, maximizing S07-S08 throughput.

**Decision requested:** Approve sprint goal and committed scope to proceed with workpack generation for ST-021 (first in execution order).
