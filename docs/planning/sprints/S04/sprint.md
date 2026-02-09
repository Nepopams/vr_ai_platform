# Sprint S04: Improved Clarify Questions

**PI:** standalone (aligns with 2026Q2 NEXT phase)
**Period:** 2026-02-08 -- 2026-02-14 (5 calendar days, ~3 working days of Codex effort)
**Status:** Done

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Roadmap | `docs/planning/strategy/roadmap.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |
| EP-005 epic | `docs/planning/epics/EP-005/epic.md` |
| Initiative (improved-clarify) | `docs/planning/initiatives/INIT-2026Q2-improved-clarify.md` |

---

## Sprint Goal

Improve clarify question quality so that clarify decisions include specific `missing_fields`, LLM generates context-aware questions, and improvement is measurable via golden dataset ground truth -- completing the last NEXT-phase initiative (INIT-2026Q2-improved-clarify) and closing the 2026Q2 NEXT phase.

---

## Committed Scope

| Story ID | Title | Epic | Estimate | Owner | Notes |
|----------|-------|------|----------|-------|-------|
| ST-012 | Enhanced missing_fields detection in baseline | EP-005 | 1 day | Codex | Foundation: enrich missing_fields for all 5 clarify triggers. 6 new tests. |
| ST-013 | Context-aware LLM clarify prompt and safety refinement | EP-005 | 1-2 days | Codex | LLM prompt improvement + safety gate refinement. 8 new tests. |
| ST-014 | Clarify golden dataset ground truth and quality measurement | EP-005 | 1 day | Codex | Measurement script + fixture annotations + 2 new fixtures. 6 new tests. |

**Total estimated effort:** 3-4 working days of Codex implementation + Claude prompts/review overhead.

Story specs:
- `docs/planning/epics/EP-005/stories/ST-012-enhanced-missing-fields.md`
- `docs/planning/epics/EP-005/stories/ST-013-context-aware-clarify-prompt.md`
- `docs/planning/epics/EP-005/stories/ST-014-clarify-golden-dataset-measurement.md`

### DoR Readiness Assessment

| Story | DoR Status | Notes |
|-------|------------|-------|
| ST-012 | Ready | No blockers. ACs are testable (6 ACs), test strategy defined (6 tests), code touchpoints documented. |
| ST-013 | Ready (managed dependency) | Blocked by ST-012 (must complete first). All other DoR criteria met: 7 ACs, 8 tests identified, code touchpoints documented. |
| ST-014 | Ready (managed dependency) | Blocked by ST-012 (ground truth must align with enriched fields). 6 ACs, 6 tests identified. Independent of ST-013. |

---

## Stretch

| Story ID | Title | Condition |
|----------|-------|-----------|
| (none) | -- | All 3 committed stories fill sprint capacity. If stories complete early, use time for review quality, retro, and 2026Q3 LATER phase candidate identification. |

---

## Out of Scope (explicit)

- **UI dialog manager** -- product-layer responsibility, not platform.
- **Multi-turn conversation state** -- no memory between requests (MVP anti-scope).
- **Changes to clarify_payload contract schema** -- already sufficient (has question, missing_fields, options).
- **Subjective question quality scoring** -- too complex; use objective missing_fields match rate instead.
- **CI integration of measurement** -- LATER phase (INIT-2026Q3-semver-and-ci).
- **Partial trust corridor changes** -- EP-003 done, not touched.
- **Multi-item extraction changes** -- EP-004 done, not touched.
- **Shadow router changes** -- stable, not touched.
- **New feature flags** -- existing `ASSIST_CLARIFY_ENABLED` is sufficient.

---

## Capacity Notes

- **Pipeline model:** Claude generates workpacks and prompts, Human gates, Codex implements. Same proven model as S01 (4/4), S02 (3/3), S03 (3/3).
- **Codex throughput assumption:** ~1 story per day for code stories (S01-S03 actuals).
- **Buffer:** ~25% implicit (5 calendar days for ~3-4 days of estimated work).
- **Bottleneck risk:** Human gate turnaround. Each story requires 3 gate interactions.
- **Parallelism:** ST-012 must run first (foundation). After ST-012 completes, ST-013 and ST-014 are independent and can run in parallel.
- **S03 retro action items:**
  - Include ALL existing test stubs when changing schemas in prompt-apply.
  - Anticipate V1/V2 divergence in workpack risk analysis.
  - Secrets-check: use stricter grep pattern.
- **Test suite baseline:** 176 tests passing (~4s). Expected growth: ~20 new tests across 3 stories (target: ~196 tests).

---

## Dependencies

| Dependency | Type | Impact | Status |
|------------|------|--------|--------|
| EP-004 (Multi-Entity Extraction) | Internal | ST-012 builds on stable normalized["items"] pipeline. | Done |
| EP-002 (Assist Mode) | Internal | ST-013 modifies assist clarify pipeline. | Done |
| Existing test suite passes (176 tests) | Internal | New tests depend on baseline tests passing. | Verified |
| `decision.schema.json` clarify_payload | Contract | Already has question + missing_fields + options. No changes needed. | Verified |
| Human gate availability | Process | Each story needs 3 gate interactions | Accepted |

**No external dependencies.** All work is self-contained within the repo.

---

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation | ROAM |
|------|-------------|--------|------------|------|
| Enhanced missing_fields break existing clarify tests | Low | Medium | ST-012 changes are additive (new fields for currently-None triggers). Existing 3 triggers unchanged. All 176 tests must pass. | Mitigated |
| LLM prompt changes degrade question quality | Low | Medium | Safety gate remains. Feature flag gating. Fallback to default question always available. | Mitigated |
| Golden dataset ground truth is subjective | Medium | Low | Use objective criteria: missing_fields match rate (mechanical), not question text quality. | Accepted |
| Changes to _clarify_question_is_safe allow unsafe questions | Low | High | Echo-prevention and length limits remain non-negotiable. Only add relevance checks, don't relax safety. | Owned |
| Codex cannot run pytest in sandbox (carry-forward) | -- | Low | Accepted as permanent limitation. Verification during Claude review. | Accepted |
| ST-012 scope creep into validate_and_build refactoring | Low | Medium | Strict scope: only add missing_fields values, don't restructure the method. | Owned |

---

## Execution Order (recommended)

**Phase 1 (sequential, critical path):**
1. **ST-012** -- Enhanced missing_fields detection. Foundation story.
   - Workpack -> prompt-plan -> Codex PLAN -> prompt-apply -> Codex APPLY -> review -> merge.

**Phase 2 (parallel after ST-012 merged):**
2. **ST-013** -- Context-aware LLM clarify prompt.
   - Workpack -> prompt-plan -> Codex PLAN -> prompt-apply -> Codex APPLY -> review -> merge.

3. **ST-014** -- Clarify golden dataset and measurement.
   - Can run in parallel with ST-013.
   - Should be reviewed last (measures combined effect).
   - Workpack -> prompt-plan -> Codex PLAN -> prompt-apply -> Codex APPLY -> review -> merge.

Start with workpack generation for ST-012 immediately after Gate B approval.

---

## Demo Plan

At sprint end, the following should be demonstrable:

1. **Enhanced missing_fields** -- Run a command with unknown intent and show `missing_fields=["intent"]` in clarify decision.
2. **Context-aware question** -- Compare LLM-generated clarify question before/after: should reference what's known.
3. **Safety gate** -- Show that irrelevant LLM questions are rejected.
4. **Measurement script** -- Run `python3 scripts/analyze_clarify_quality.py` against golden dataset and show missing_fields match rate.
5. **New fixtures** -- Show 2 new clarify-specific golden fixtures with ground truth.
6. **Test suite growth** -- All tests passing (target: ~196 tests, up from 176).

**Initiative closure signal:** After all 3 stories pass review, INIT-2026Q2-improved-clarify can be marked Done. This also completes the entire 2026Q2 NEXT phase.

---

## Gate Ask (Gate B)

**Requesting PO approval for:**

1. **Sprint Goal:** Improve clarify question quality with enhanced missing_fields, context-aware LLM prompts, and measurable golden dataset ground truth -- closing the last NEXT-phase initiative.
2. **Committed scope:** 3 stories (ST-012, ST-013, ST-014) as listed above. All 3 pass DoR.
3. **Out-of-scope list:** As documented above -- no UI dialog manager, no contract changes, no multi-turn, no CI integration.
4. **Risk posture:** All risks Low-Medium. One High-impact risk (safety gate relaxation) is owned with strict rule: only add checks, don't remove existing safety.
5. **Execution model:** Same pipeline as S01-S03 (10/10 stories delivered, 0 carry-overs).
6. **Significance:** Closing this initiative completes the entire 2026Q2 NEXT phase. Next phase would be LATER (2026Q3).

**Decision requested:** Approve sprint goal and committed scope to proceed with workpack generation for ST-012.
