# Sprint S06 -- Retrospective

**Date:** 2026-02-10
**Facilitator:** Claude (Arch/BA)
**Attendees:** Human (PO), Claude (Arch/BA), Codex (Dev)

---

## Sprint Summary

| Metric | Value |
|--------|-------|
| Sprint Goal | Lay production hardening foundations across three epics |
| Stories committed | 4 |
| Stories completed | 4/4 |
| Stories carried over | 0 |
| Sprint Goal met? | Yes |
| Tests: start → end | 228 → 251 (+23) |
| Must-fix issues | 0 |
| Should-fix issues | 0 |

Initiative status:
- INIT-2026Q4-production-hardening: **4/11 stories done** (foundation layer for all 3 epics)

---

## Evidence

### ST-021: HTTP LLM Client (EP-008)
- Commit: `e660908`
- Files: `llm_policy/http_caller.py` (new), `tests/test_http_llm_client.py` (new, 8 tests)
- Implements `LlmCaller` interface via httpx. Supports `yandex_ai_studio` and `openai_compatible` providers.
- Error mapping: timeout→TimeoutError, connect/HTTP→LlmUnavailableError.
- Privacy: no API key in logs (dedicated test).

### ST-025: Golden Dataset Expansion (EP-009)
- Commit: `0d31a7a`
- Files: `golden_dataset.json` (14→22 entries), 6 new command fixtures, `tests/test_golden_dataset_validation.py` (new, 3 tests), `tests/test_analyze_shadow_router.py` (assertion update)
- Distribution: add_shopping_item 10, create_task 7, clarify_needed 5.
- New fields: `expected_action`, `difficulty` on all 22 entries.
- Note: Codex PLAN raised false STOP-THE-LINE on `additionalProperties:false` — clarified in APPLY that it applies to command fixtures, not golden_dataset.json.

### ST-028: Pipeline Latency Instrumentation (EP-010)
- Commit: `500ffab`
- Files: `app/logging/pipeline_latency_log.py` (new), `graphs/core_graph.py` (updated), `tests/test_pipeline_latency.py` (new, 6 tests)
- 5 timed steps: validate_command, detect_intent, registry, core_logic, validate_decision.
- JSONL log, flag-gated (`PIPELINE_LATENCY_LOG_ENABLED`, default true).

### ST-029: Unified Fallback Metrics (EP-010)
- Commit: `17cd4c9`
- Files: `app/logging/fallback_metrics_log.py` (new), `graphs/core_graph.py` (updated), `tests/test_fallback_metrics.py` (new, 6 tests)
- Records llm_outcome: skipped/deterministic_only (+ success/fallback/error for future integrations).
- Privacy guarantee: no raw text/prompt/LLM output fields.
- Refactored `is_llm_policy_enabled` import to function-level (shared by latency + fallback blocks).

### Verification
```
251 passed in 11.64s
```

---

## What Went Well

- **4/4 stories, 0 must-fix, all first-attempt passes.** Continues the streak: 23/23 stories across 6 sprints with zero carry-overs.
- **Three-epic coverage in one sprint.** All 3 epics (EP-008, EP-009, EP-010) got their foundation story, unblocking S07 across all tracks.
- **core_graph.py contention handled cleanly.** ST-028 before ST-029 as planned — ST-029 built on ST-028's timing infrastructure, reused `llm_on` variable.
- **STOP-THE-LINE worked correctly.** Codex PLAN for ST-025 raised a false alarm on `additionalProperties:false` — the process caught it, Claude clarified in APPLY prompt, and Codex proceeded cleanly.
- **Prompt-apply with exact code remains the winning pattern.** All 4 stories had exact file contents in prompt-apply; Codex reproduced 1:1.

---

## What Could Be Improved

- **STOP-THE-LINE false alarm overhead.** ST-025 had a false alarm that required an extra round-trip. PLAN prompt could be more explicit about which schema applies where.
- **Story spec test count drift.** Story specs (written during decomposition) estimated 228 existing tests, but by the time ST-029 ran, the base was 245. Not a real problem, but sprint test targets should reference "current count" not "baseline at planning time".
- **All-code sprint.** No docs stories this sprint. Works fine when all stories are well-scoped, but adding 1 docs story as warm-up (S05 pattern) can help with context.

---

## Action Items

| # | Action | Owner | Status |
|---|--------|-------|--------|
| 1 | In PLAN prompts, explicitly state which schema applies to which file (prevent false STOP-THE-LINE) | Claude | Open |
| 2 | Sprint test baseline: use "current count at sprint start" not story-spec count | Claude | Open |
| 3 | Carry: secrets-check grep pattern refinement (from S03/S05) — verified for ST-021, no issues found | -- | Closed |
| 4 | Carry: check globber consumption for new data files (from S04/S05) — verified for ST-025, no issues | -- | Closed |

---

## Sprint Velocity

| Sprint | Stories | Tests Added | Duration | Notes |
|--------|---------|-------------|----------|-------|
| S01 | 4/4 | 0 → 109 | ~1 day | NOW phase |
| S02 | 3/3 | 109 → 131 | ~1 day | Partial trust |
| S03 | 3/3 | 131 → 176 | ~1 day | Multi-entity |
| S04 | 3/3 | 176 → 202 | ~1 day | Improved clarify |
| S05 | 6/6 | 202 → 228 | ~1 day | CI + registry |
| **S06** | **4/4** | **228 → 251** | **~1 day** | **Production hardening foundations** |
| **Total** | **23/23** | **251 tests** | **6 sprints** | **0 carry-overs** |

---

## Next Sprint Candidates (S07)

Unblocked by S06 completions:
- **ST-022** (EP-008): LLM caller startup registration — depends on ST-021 ✅
- **ST-026** (EP-009): Quality evaluation script — depends on ST-025 ✅
- **ST-030** (EP-010): Aggregation script for latency/fallback — depends on ST-028+ST-029 ✅

These 3 stories are the natural "second layer" across all 3 epics.
