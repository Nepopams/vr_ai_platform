# Sprint S07: Production Hardening Layer 2 -- Bootstrap, Evaluation, Aggregation

**PI:** standalone (aligns with INIT-2026Q4-production-hardening)
**Period:** 2026-02-17 -- 2026-02-24 (5 calendar days, ~5 working days of Codex effort)
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
| Initiative | `docs/planning/initiatives/INIT-2026Q4-production-hardening.md` |
| S06 retro | `docs/planning/sprints/S06/retro.md` |

---

## Sprint Goal

Complete the second layer of production hardening: wire the real LLM caller into the platform bootstrap (EP-008), create the quality evaluation script (EP-009), and build the latency/fallback aggregation script (EP-010) -- progressing INIT-2026Q4 from 4/11 to 8/11 stories.

---

## Committed Scope

| Story ID | Title | Epic | Type | Estimate | Owner | Dep | Notes |
|----------|-------|------|------|----------|-------|-----|-------|
| ST-022 | LLM caller startup registration and env-var configuration | EP-008 | Code | 1 day | Codex | ST-021 ✅ | Bootstrap module. ~5 new tests. |
| ST-023 | .env.example and LLM configuration documentation | EP-008 | Docs | 0.5 day | Codex | ST-022 (intra-sprint) | Docs story, fast pipeline. ~0 tests (docs only). |
| ST-026 | Quality evaluation script with metrics | EP-009 | Code | 1 day | Codex | ST-025 ✅ | Runs golden dataset through pipeline. ~6 new tests. |
| ST-030 | Latency and fallback summary aggregation script | EP-010 | Code | 1 day | Codex | ST-028+ST-029 ✅ | p50/p95/p99 + fallback rates. ~6 new tests. |

**Total estimated effort:** 3.5 working days of Codex implementation.

Story specs:
- `docs/planning/epics/EP-008/stories/ST-022-llm-caller-bootstrap.md`
- `docs/planning/epics/EP-008/stories/ST-023-env-example-llm-docs.md`
- `docs/planning/epics/EP-009/stories/ST-026-quality-evaluation-script.md`
- `docs/planning/epics/EP-010/stories/ST-030-aggregation-script.md`

### DoR Readiness Assessment

| Story | DoR Status | Notes |
|-------|------------|-------|
| ST-022 | Ready | ST-021 done. Reads env vars, creates HttpLlmCaller, calls set_llm_caller(). 4 ACs testable. |
| ST-023 | Ready | Docs-only. ST-022 must complete first (intra-sprint dep). .env.example + guide. |
| ST-026 | Ready | ST-025 done. Script reads golden_dataset.json, runs process_command(). 5 ACs testable. |
| ST-030 | Ready | ST-028+ST-029 done. Reads JSONL logs, computes percentiles. 5 ACs testable. |

All 4 stories pass DoR. No conditional agents needed (all flags negative).

---

## Stretch

| Story ID | Title | Condition |
|----------|-------|-----------|
| (none) | -- | 4 committed stories at 3.5 days fit within 5-day sprint. Buffer used for review quality and S08 candidate analysis. |

---

## Out of Scope (explicit)

- **Smoke test with real LLM** (ST-024) -- depends on ST-022, but requires real LLM key; scheduled for S08.
- **CI integration for quality report** (ST-027) -- depends on ST-026, scheduled for S08.
- **Observability documentation** (ST-031) -- depends on ST-030, scheduled for S08.
- **Hot-reloading of LLM config** -- out of EP-008 scope.
- **Automated pass/fail thresholds for quality** -- out of EP-009 scope.
- **Real-time metrics / Prometheus / Grafana** -- out of EP-010 scope.
- **Changes to DecisionDTO or CommandDTO** -- stable boundary.
- **New intents or domains** -- out of initiative scope.

---

## Capacity Notes

- **Pipeline model:** Same as S01-S06 (23/23 stories, 0 carry-overs).
- **Sprint size:** 4 stories (3 code + 1 docs). Standard size, consistent with S01/S02/S03/S04/S06.
- **Buffer:** ~30% implicit (3.5 days estimated in 5 calendar days).
- **Bottleneck risk:** Human gate turnaround. ST-022 must complete before ST-023 (intra-sprint dep). Other 2 stories are independent.
- **Gate interactions:** ~12 (3 per code story × 3 + 3 for docs story).
- **S06 retro action items applied:**
  - PLAN prompts explicitly state which schema applies to which file (action #1).
  - Sprint test baseline uses current count (251), not story-spec count (action #2).
- **Test suite baseline:** 251 tests passing. Expected growth: ~17 new tests (target: ~268).
- **Mixed sprint:** 3 code + 1 docs. S05 retro showed docs-first ordering builds context. Here ST-023 (docs) follows ST-022 (its dependency), but could also provide warm context for ST-026/ST-030.

---

## Dependencies

| Dependency | Type | Impact | Status |
|------------|------|--------|--------|
| ST-021 HTTP caller (`llm_policy/http_caller.py`) | Internal | ST-022 uses `create_http_caller()`. | Done (S06) |
| ST-025 expanded golden dataset | Internal | ST-026 reads `golden_dataset.json`. | Done (S06) |
| ST-028 pipeline latency log | Internal | ST-030 reads `pipeline_latency.jsonl`. | Done (S06) |
| ST-029 fallback metrics log | Internal | ST-030 reads `fallback_metrics.jsonl`. | Done (S06) |
| `llm_policy/runtime.py` (set_llm_caller/get_llm_caller) | Internal | ST-022 uses these. | Done |
| `graphs/core_graph.py` (process_command) | Internal | ST-026 calls this for evaluation. | Done |
| Human gate availability | Process | ~12 gate interactions. | Accepted |
| ST-022 → ST-023 intra-sprint dep | Internal | ST-023 must wait for ST-022 completion. | Managed by execution order |

**No external dependencies.** All work is self-contained within the repo.

---

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation | ROAM |
|------|-------------|--------|------------|------|
| ST-022 bootstrap registers caller in production without real key | Low | Medium | Validation: skip registration when env vars missing. AC-2 mandates this. | Mitigated |
| ST-023 intra-sprint dep blocks if ST-022 takes longer | Low | Low | ST-023 is docs-only (0.5 day). Even if delayed, doesn't block ST-026/ST-030. | Accepted |
| ST-026 evaluation script differences from actual golden entries | Low | Medium | Script reads golden_dataset.json directly, no hardcoded expectations. | Mitigated |
| ST-030 percentile computation with few records | Low | Low | AC-4: empty logs produce zeros, no crash. AC-1 requires 50+ records for percentiles in test. | Mitigated |
| skills/ directory naming (hyphen vs underscore) | Low | Low | S05 lesson: dir names use hyphens (`quality-eval`, `observability`), module files use underscores. | Mitigated |
| Codex sandbox lacks pytest (permanent) | -- | Low | Accepted. Verification during Claude review. | Accepted |

---

## Execution Order (recommended)

**Recommended sequence:**

1. **ST-022** -- LLM caller bootstrap (EP-008, code).
   *Rationale:* Must complete before ST-023. Foundation for real LLM integration.

2. **ST-023** -- .env.example and LLM docs (EP-008, docs).
   *Rationale:* Depends on ST-022. Quick docs story, provides warm-up context switch.

3. **ST-026** -- Quality evaluation script (EP-009, code).
   *Rationale:* Independent. Builds on golden dataset (ST-025).

4. **ST-030** -- Aggregation script (EP-010, code).
   *Rationale:* Independent. Builds on latency/fallback logs (ST-028+ST-029).

**Timeline estimate:**

```
Day 1:  ST-022 (LLM bootstrap)
Day 2:  ST-023 (docs, quick) + ST-026 start
Day 3:  ST-026 complete + ST-030 start
Day 4:  ST-030 complete + buffer
Day 5:  Buffer / retro / S08 candidate analysis
```

---

## Demo Plan

### EP-008: Real LLM Client Integration
1. **Bootstrap module** -- Show `llm_policy/bootstrap.py`: auto-registers caller when env vars set. Show skip when vars missing.
2. **Configuration docs** -- Show `.env.example` with all LLM env vars, `docs/guides/llm-setup.md`.

### EP-009: Golden Dataset Quality Evaluation
3. **Evaluation script** -- Run `evaluate_golden.py` in stub mode, show JSON report with intent accuracy, entity precision/recall, clarify rate.
4. **All 22 golden entries evaluated** -- Show report covers all entries without errors.

### EP-010: Pipeline Observability
5. **Aggregation script** -- Show `aggregate_metrics.py` output: p50/p95/p99 latency, fallback/error rates, LLM vs non-LLM comparison.
6. **Empty log handling** -- Show script works on empty logs (zeros, no crash).

### Cross-cutting
7. **Test suite growth** -- All tests passing (target: ~268 tests, up from 251).
8. **Initiative progress** -- INIT-2026Q4: 8/11 stories done after S07. Only 3 stories remain (ST-024, ST-027, ST-031).

---

## Gate Ask (Gate B)

**Requesting PO approval for:**

1. **Sprint Goal:** Complete the second layer of production hardening: bootstrap (EP-008), quality evaluation (EP-009), and aggregation (EP-010).
2. **Committed scope:** 4 stories (3 code + 1 docs) across 3 epics. All pass DoR. One intra-sprint dep (ST-023 after ST-022).
3. **Out-of-scope list:** As documented above.
4. **Risk posture:** All risks Low. Skills directory naming (S05 lesson) mitigated. Intra-sprint dep is docs story, minimal impact.
5. **Execution model:** Same pipeline as S01-S06 (23/23 stories, 0 carry-overs). Standard 4-story sprint with 30% buffer.
6. **Significance:** Progresses initiative from 4/11 to 8/11 stories. After S07, only 3 stories remain for INIT-2026Q4 closure (ST-024, ST-027, ST-031 — all third-layer).

**Decision requested:** Approve sprint goal and committed scope to proceed with workpack generation for ST-022 (first in execution order).
