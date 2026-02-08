# Sprint S03 -- Retrospective

**Date:** 2026-02-08
**Facilitator:** Claude (Arch/BA)
**Attendees:** Human (PO), Claude (Arch/BA), Codex (Dev)

---

## Sprint Summary

| Metric | Value |
|--------|-------|
| Sprint Goal | Deliver end-to-end multi-item shopping extraction (baseline, LLM/assist, planner) |
| Stories committed | 3 (+ 1 pre-completed) |
| Stories completed | 3/3 |
| Stories carried over | 0 |
| Sprint Goal met? | **Yes** |

Initiative status:
- INIT-2026Q2-multi-entity-extraction -> Done (all 3 ACs PASS, all deliverables present)

---

## What Went Well

- **3/3 code stories closed in a single session** -- pipeline throughput maintained at S01/S02 level. All stories required significant code changes (not docs-only), yet delivered without delays.
- **Zero must-fix on ST-011 review** -- Codex produced exact content from prompt-apply, 176/176 tests passed on first run without fixes.
- **ST-010 review had 1 must-fix, resolved in <5 min** -- test stub mismatch (`item_name` -> `items` format) was caught by Claude review and fixed immediately.
- **Test suite grew +45 tests (131 -> 176) with zero regressions** -- significant coverage increase for multi-item pipeline across all 3 extraction layers.
- **ADR-006-P (ST-008) pre-completed before sprint** -- decisions on internal model (items: List[dict], quantity: string) resolved before coding started. No ambiguity during implementation.
- **Contract schema required zero changes** -- `decision.schema.json` already supported `proposed_actions: array` with quantity/unit/list_id. Validated in planning, confirmed in implementation.
- **Backward compatibility proven end-to-end** -- `item_name` property maintained via `ExtractionResult.item_name`, partial trust not broken (ST-011 AC-6), single-item path works unchanged.
- **Sequential execution order worked** -- ST-009 -> ST-010 -> ST-011 was the right order. Each story built cleanly on the previous one.

---

## What Did Not Go Well

- **Codex sandbox still lacks pytest** -- carry-forward from S01/S02. Verification always shifts to Claude review phase. Accepted as permanent limitation.
- **ST-010 test stub mismatch** -- `test_llm_policy_tasks.py::test_policy_enabled_uses_llm` had old stub format. Caught on review, fixed in 1 line. Root cause: prompt-apply didn't include this test file in changes because it wasn't a "new" test. Lesson: when changing a schema/contract, always check existing test stubs that mock the old format.
- **Golden-like test required rethinking** -- V1/V2 divergence on multi-item commands meant `_extract_stable_fields` comparison broke. Resolved by comparing only action type + schema validity. Could have been anticipated better in workpack.
- **Secrets-check grep still uses broad pattern** -- S02 action item to refine was partially addressed (narrower file list) but pattern itself not changed.

---

## Action Items

| Action | Owner | Due |
|--------|-------|-----|
| When changing extraction/LLM schemas, include ALL existing test stubs in prompt-apply | Claude | Next code story |
| Anticipate V1/V2 divergence in workpack risk analysis when adding new pipeline features | Claude | Next EP |
| Secrets-check: consider `--fixed-strings` or stricter pattern for next workpack | Claude | S04 |

---

## Pipeline Observations

### Claude (Arch/BA) effectiveness
- **Workpack quality:** High -- all 3 workpacks had correct paths, accurate file contents. ST-011 prompt-apply was 100% exact.
- **Prompt quality (plan/apply):** High -- ST-011: zero deviations. ST-010: 1 test stub missed (existing file not included). ST-009: clean.
- **Review thoroughness:** Good -- caught ST-010 stub issue, ran full test suite, verified schema, checked invariants, verified backward compat.
- **Improvement:** Include "existing test stubs that mock changed schemas" in prompt-apply file list.

### Codex (Dev) effectiveness
- **PLAN phase accuracy:** 100% -- all exploration tasks (19 for ST-010, 13 for ST-011) confirmed correctly. No STOP-THE-LINE across entire sprint.
- **APPLY phase quality:** 100% -- exact content reproduction for all 3 stories. No deviations from prompts.
- **Deviation from workpack:** None -- Codex followed STOP-THE-LINE rules perfectly across all 3 stories.
- **Bottlenecks:** pytest unavailable in sandbox (known, accepted).

### Human (PO) gate flow
- **Gate turnaround time:** Fast -- same-session approvals for all gates.
- **Blocking issues:** None.
- **Communication clarity:** Good -- clear "GO -> merge -> next" pattern.

---

## Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| Stories completed | 3 | 3 |
| Tests passing | All (~166+) | **176** (all pass) |
| DoD compliance | 100% | 100% |
| Gate interactions per story | ~3 | 3 (plan gate, apply gate, review) |
| Codex APPLY attempts | 3 | 3 (1 per story, zero retries) |
| Must-fix issues on review | 0 | 1 (ST-010 test stub, fixed immediately) |
| Initiatives closed | 1 (multi-entity-extraction) | 1 (Done) |

---

## Carry-Forward Items

- Codex pytest in sandbox: **Closed** (accepted as permanent limitation)
- S02 batching gate approvals: **Not tested** (sequential story deps made batching impractical for S03)
- Secrets-check grep pattern: **Open** (minor, refine in S04)

---

## Sprint History

| Sprint | Goal | Stories | Tests | Initiatives Closed |
|--------|------|---------|-------|--------------------|
| S01 | Close NOW-phase gaps (Shadow Router + Assist-Mode) | 4/4 | 109 | 2 (shadow-router, assist-mode) |
| S02 | Close Partial Trust initiative gaps | 3/3 | 131 | 1 (partial-trust) |
| **S03** | **Multi-entity extraction end-to-end** | **3/3** | **176** | **1 (multi-entity-extraction)** |
| **Total** | | **10/10 + 3 pre-completed** | **176** | **4 initiatives** |

---

## Next Sprint Candidates

Remaining NEXT-phase (2026Q2) initiatives per roadmap:

| Initiative | Priority | Comment |
|------------|----------|---------|
| INIT-2026Q2-improved-clarify | Medium | missing_fields, LLM-assist for clarify questions. Builds on assist-mode and multi-entity extraction foundations. Last remaining NEXT-phase initiative. |

After improved-clarify, the NEXT phase (2026Q2) would be complete. LATER phase (2026Q3) initiatives:

| Initiative | Priority | Comment |
|------------|----------|---------|
| INIT-2026Q3-semver-and-ci | Low | SemVer and CI contract validation. |
| INIT-2026Q3-codex-integration | Low | Codex pipeline integration. |
| INIT-2026Q3-agent-registry-integration | Low | Agent registry and runner for internal agents. |

Recommendation: **INIT-2026Q2-improved-clarify** is the natural next target -- last remaining NEXT-phase initiative, builds on assist-mode + multi-entity foundation delivered in S01-S03.
