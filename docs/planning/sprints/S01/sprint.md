# Sprint S01: Close NOW-Phase Gaps for Shadow Router and Assist-Mode Initiatives

**PI:** standalone (pre-PI, aligns with 2026Q1 NOW phase)
**Period:** 2026-02-10 -- 2026-02-14 (5 calendar days, ~3-4 working days of Codex effort)
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
| EP-001 epic | `docs/planning/epics/EP-001/epic.md` |
| EP-002 epic | `docs/planning/epics/EP-002/epic.md` |
| Initiative (shadow-router) | `docs/planning/initiatives/INIT-2026Q1-shadow-router.md` |
| Initiative (assist-mode) | `docs/planning/initiatives/INIT-2026Q1-assist-mode.md` |

---

## Sprint Goal

Close the remaining gaps in both NOW-phase initiatives (Shadow Router and Assist-Mode) by delivering the golden-dataset analyzer script with ground truth, documenting assist-mode acceptance rules, and producing formal verification reports for both initiatives -- enabling initiative closure and measurable LLM quality assessment.

---

## Committed Scope

| Story ID | Title | Epic | Estimate | Owner | Notes |
|----------|-------|------|----------|-------|-------|
| ST-001 | Golden-dataset analyzer script + ground truth manifest + README | EP-001 | 1-2 days | Codex | Code + tests (Python script, golden dataset, README) |
| ST-002 | Retroactive verification of shadow-router AC1-AC3 | EP-001 | 1-2 hours | Codex | Docs only (verification report) |
| ST-003 | Document acceptance rules for assist-mode hints | EP-002 | 2-4 hours | Codex | Docs only (acceptance rules at docs/contracts/) |
| ST-004 | Retroactive verification of assist-mode initiative ACs | EP-002 | 1-2 hours | Codex | Docs only (verification report, depends on ST-003) |

**Total estimated effort:** 2-3 working days of Codex implementation + Claude prompts/review overhead.

Story specs:
- `docs/planning/epics/EP-001/stories/ST-001-golden-dataset-analyzer.md`
- `docs/planning/epics/EP-001/stories/ST-002-retroactive-verification.md`
- `docs/planning/epics/EP-002/stories/ST-003-acceptance-rules-documentation.md`
- `docs/planning/epics/EP-002/stories/ST-004-retroactive-verification.md`

---

## Stretch

| Story ID | Title | Condition |
|----------|-------|-----------|
| (none) | -- | All 4 committed stories are small; no stretch items identified. If stories complete early, the remaining time should be used for review quality and retro. |

---

## Out of Scope (explicit)

- **Code changes to shadow router or assist-mode implementation** -- this sprint is about measurement and documentation, not behavior changes.
- **CI pipeline integration for the analyzer script** -- follow-up work (LATER phase, INIT-2026Q3-semver-and-ci).
- **Dashboard or web visualization of metrics** -- not in MVP scope.
- **Partial Trust implementation** -- NEXT phase (INIT-2026Q2-partial-trust).
- **Multi-entity extraction improvements** -- NEXT phase (INIT-2026Q2-multi-entity-extraction).
- **Improved clarify questions** -- NEXT phase (INIT-2026Q2-improved-clarify).
- **New tests for existing code** -- verification stories use existing tests only.
- **Baseline comparison in analyzer script** -- potential future enhancement, not in ST-001 scope.

---

## Capacity Notes

- **Pipeline model:** Claude generates workpacks and prompts, Human gates, Codex implements.
- **Codex throughput assumption:** ~1 story per day for code stories (ST-001), ~2-3 doc stories per day (ST-002, ST-003, ST-004).
- **Buffer:** ~20% implicit (5 calendar days for ~3 days of estimated work).
- **Bottleneck risk:** Human gate turnaround. Each story requires prompt-plan gate (Gate C) and post-APPLY review. Budget ~30 min per gate interaction.
- **Parallelism:** ST-001 and ST-002 are independent. ST-003 is independent. ST-004 depends on ST-003. Max parallelism = 3 stories at once (ST-001 + ST-002 + ST-003).

---

## Dependencies

| Dependency | Type | Impact | Status |
|------------|------|--------|--------|
| ST-004 depends on ST-003 | Internal (story-to-story) | ST-003 creates `docs/contracts/assist-mode-acceptance-rules.md` which ST-004 references for AC2 verification | Managed: schedule ST-003 before ST-004 |
| Existing test suite passes | Internal (codebase) | Verification stories depend on 99 existing tests passing | Verified: tests pass as of sprint planning |
| Human gate availability | Process | Each story needs 2 gate interactions (PLAN approval, APPLY review) | Accepted: PO aware of pipeline model |

**No external dependencies.** All work is self-contained within the repo.

---

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation | ROAM |
|------|-------------|--------|------------|------|
| Existing tests break before verification stories run | Low | Medium | Run full test suite before starting ST-002/ST-004. If failures found, fix first (hotfix exception). | Mitigated |
| Golden dataset ground truth labels are ambiguous for some fixture commands | Medium | Low | ST-001 includes explicit schema with expected_intent and expected_entity_keys; review ground truth in PLAN phase before APPLY. | Owned |
| Human gate turnaround delays sprint | Medium | Medium | Stories are independent (except ST-004); pipeline can process 2-3 stories in parallel to reduce idle time. | Accepted |
| Acceptance rules doc (ST-003) requires deep code reading | Low | Low | Code is well-structured with clear function names; Codex PLAN phase will map all rules before APPLY. | Mitigated |
| Shadow router JSONL format underdocumented | Low | Medium | ST-001 PLAN phase will inspect actual JSONL structure in code/tests before building analyzer. | Mitigated |

---

## Execution Order (recommended)

1. **ST-001** (largest story, start first) -- workpack, then prompt-plan, Codex PLAN, prompt-apply, Codex APPLY, review.
2. **ST-002** (independent, can overlap with ST-001) -- workpack, prompt-plan, Codex PLAN, prompt-apply, Codex APPLY, review.
3. **ST-003** (independent, can overlap) -- workpack, prompt-plan, Codex PLAN, prompt-apply, Codex APPLY, review.
4. **ST-004** (depends on ST-003) -- start after ST-003 review passes.

---

## Gate Ask (Gate B)

**Requesting PO approval for:**

1. **Sprint Goal:** Close NOW-phase gaps for both initiatives by delivering the golden-dataset analyzer and formal verification artifacts.
2. **Committed scope:** 4 stories (ST-001 through ST-004) as listed above.
3. **Out-of-scope list:** As documented above -- no code changes to existing implementation, no CI integration, no NEXT-phase features.
4. **Risk posture:** All risks are Low-Medium probability, mitigated or accepted. No blockers identified.
5. **Execution model:** Claude prompts + Codex implementation + Human gates, per the established pipeline.

**Decision requested:** Approve sprint goal and committed scope to proceed with workpack generation for ST-001.
