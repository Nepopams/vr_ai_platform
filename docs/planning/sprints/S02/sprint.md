# Sprint S02: Close Partial Trust Initiative Gaps -- Verification, Regression Tooling, and Rollout Docs

**PI:** standalone (aligns with 2026Q2 NEXT phase)
**Period:** 2026-02-10 -- 2026-02-14 (5 calendar days, ~2-3 working days of Codex effort)
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
| EP-003 epic | `docs/planning/epics/EP-003/epic.md` |
| Initiative (partial-trust) | `docs/planning/initiatives/INIT-2026Q2-partial-trust.md` |
| ADR-004 | `docs/adr/ADR-004-partial-trust-corridor.md` |

---

## Sprint Goal

Deliver the remaining artifacts and hardening needed to close INIT-2026Q2-partial-trust: a formal verification report with edge case tests proving the corridor is safe, a regression metrics analyzer script enabling data-driven sampling decisions, and a rollout runbook enabling operators to safely enable and tune partial trust in production.

---

## Committed Scope

| Story ID | Title | Epic | Estimate | Owner | Notes |
|----------|-------|------|----------|-------|-------|
| ST-005 | Verify and harden partial trust scaffolding + finalize ADR-004 | EP-003 | 1-2 days | Codex | Code + docs (edge case tests + verification report + ADR update). ADR-004 already Accepted; story covers verification report and new tests. |
| ST-006 | Regression metrics analyzer for partial trust risk-log | EP-003 | 1-2 days | Codex | Code (Python script + tests + README) |
| ST-007 | Partial trust rollout runbook and operational documentation | EP-003 | 2-4 hours | Codex | Docs only (runbook at docs/operations/) |

**Total estimated effort:** 2-3 working days of Codex implementation + Claude prompts/review overhead.

Story specs:
- `docs/planning/epics/EP-003/stories/ST-005-verify-harden-scaffolding.md`
- `docs/planning/epics/EP-003/stories/ST-006-regression-metrics-tooling.md`
- `docs/planning/epics/EP-003/stories/ST-007-rollout-documentation.md`

### DoR Readiness Assessment

| Story | DoR Status | Notes |
|-------|------------|-------|
| ST-005 | Ready | Was previously blocked on ADR-004 (Draft). ADR-004 is now Accepted (2026-02-08). All other DoR criteria met: ACs are testable (Given/When/Then), test strategy defined, scope clear, flags assigned. |
| ST-006 | Ready | No blockers. ACs are testable, test strategy defined with 10+ unit tests, scope clear, flags assigned. |
| ST-007 | Ready | Docs-only story. ACs are testable (checklist-verifiable), no code dependencies, flags assigned. Soft dependency on ST-005/ST-006 outputs managed by scheduling order. |

---

## Stretch

| Story ID | Title | Condition |
|----------|-------|-----------|
| (none) | -- | All 3 committed stories are small enough to fit comfortably. If stories complete early, remaining time should be used for review quality, retro, and S03 candidate identification for the next NEXT-phase initiative (multi-entity-extraction or improved-clarify). |

---

## Out of Scope (explicit)

- **Changes to partial trust core implementation** (config, sampling, candidate generation, acceptance rules, types, risk log) -- all are already implemented and working; this sprint verifies and documents, not modifies.
- **Changes to RouterV2 pipeline logic** -- pipeline is stable and tested.
- **Changes to public contracts** (CommandDTO, DecisionDTO) -- no contract changes in EP-003.
- **Changes to feature flag defaults** -- PARTIAL_TRUST_ENABLED stays false; rollout is operator-driven per runbook.
- **CI pipeline integration** for analyzer or tests -- LATER phase (INIT-2026Q3-semver-and-ci).
- **Dashboard or web visualization** of metrics -- not in MVP scope.
- **Extending partial trust to additional intents** -- only add_shopping_item per initiative scope.
- **Multi-entity extraction** (INIT-2026Q2-multi-entity-extraction) -- next initiative, not this sprint.
- **Improved clarify questions** (INIT-2026Q2-improved-clarify) -- next initiative, not this sprint.
- **Automated monitoring/alerting setup** -- runbook documents what to monitor; automation is out of scope.

---

## Capacity Notes

- **Pipeline model:** Claude generates workpacks and prompts, Human gates, Codex implements. Same model as S01.
- **Codex throughput assumption:** ~1 story per day for code stories (ST-005, ST-006), ~0.5 day for docs-only (ST-007). Based on S01 actuals where 4 stories completed in one session.
- **Buffer:** ~30% implicit (5 calendar days for ~2-3 days of estimated work). Slightly larger buffer than S01 since ST-005 involves test code with potential edge case discoveries.
- **Bottleneck risk:** Human gate turnaround. Each story requires prompt-plan gate (Gate C) and post-APPLY review. Budget ~30 min per gate interaction.
- **Parallelism:** ST-005 and ST-006 are independent (can run in parallel). ST-007 has soft dependency on both (should run last). Max parallelism = 2 stories at once (ST-005 + ST-006).
- **S01 retro action items:**
  - Codex pytest in sandbox: if unresolved, verification commands run during Claude review phase (same workaround as S01).
  - Workpack file path accuracy: will verify paths during PLAN phase before APPLY (lesson from ST-003 in S01).

---

## Dependencies

| Dependency | Type | Impact | Status |
|------------|------|--------|--------|
| ADR-004 finalized (Accepted) | Internal (prerequisite) | ST-005 AC-2 requires ADR-004 to be Accepted. ST-005 will update the ADR index entry. | Done (2026-02-08) |
| ST-007 soft dependency on ST-005 | Internal (story-to-story) | Runbook references verification report as prerequisite. Can write with placeholder links if needed. | Managed: schedule ST-007 after ST-005 |
| ST-007 soft dependency on ST-006 | Internal (story-to-story) | Runbook references analyzer script for monitoring section. Can write with placeholder links if needed. | Managed: schedule ST-007 after ST-006 |
| Existing test suite passes | Internal (codebase) | Edge case tests in ST-005 depend on baseline tests passing. | Verified: 109 tests pass as of S01 close |
| Human gate availability | Process | Each story needs 2 gate interactions (PLAN approval, APPLY review) | Accepted: PO aware of pipeline model |
| Risk-log JSONL format stability | Internal (codebase) | ST-006 reads risk-log format; changes would require script updates | Stable: format established in partial trust implementation |

**No external dependencies.** All work is self-contained within the repo.

---

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation | ROAM |
|------|-------------|--------|------------|------|
| Edge case tests (ST-005) reveal bugs in acceptance rules | Low | Medium | Any bugs found become must-fix items within ST-005. Scaffolding is well-structured and 9 existing tests pass. If significant bugs found, scope ST-005 to test+fix only, defer verification report to patch story. | Owned |
| Risk-log JSONL records lack fields needed for regression analysis (ST-006) | Low | Medium | Current format includes baseline_summary, llm_summary, diff_summary, latency_ms. Codex PLAN phase will inspect actual JSONL schema before APPLY. | Mitigated |
| Codex cannot run pytest in sandbox (S01 retro carry-forward) | Medium | Low | Workaround established in S01: verification runs during Claude review phase. Does not block delivery, only shifts test verification later in pipeline. | Accepted |
| Workpack contains incorrect file paths (S01 retro lesson) | Low | Medium | PLAN phase will explicitly verify all file paths before APPLY. Workpacks will include path verification step. | Mitigated |
| Human gate turnaround delays sprint | Medium | Medium | Stories are independent (ST-005 + ST-006 parallel); pipeline can process 2 stories simultaneously to reduce idle time. ST-007 is small and can be batched with review of earlier stories. | Accepted |
| Rollout runbook (ST-007) becomes stale if config changes post-sprint | Medium | Low | Runbook references env var names and config file paths. Maintenance note included per ST-007 AC. | Accepted |

---

## Execution Order (recommended)

**Phase 1 (parallel):**
1. **ST-005** (largest story, hardening + verification) -- workpack, prompt-plan, Codex PLAN, prompt-apply, Codex APPLY, review.
2. **ST-006** (independent, can overlap with ST-005) -- workpack, prompt-plan, Codex PLAN, prompt-apply, Codex APPLY, review.

**Phase 2 (after Phase 1 completes):**
3. **ST-007** (depends on ST-005 and ST-006 outputs) -- workpack, prompt-plan, Codex PLAN, prompt-apply, Codex APPLY, review.

Start with workpack generation for ST-005 and ST-006 in parallel after Gate B approval.

---

## Demo Plan

At sprint end, the following should be demonstrable:

1. **Verification report** (`docs/planning/epics/EP-003/verification-report.md`) -- all 4 initiative ACs mapped to code evidence with PASS verdicts.
2. **Edge case test suite** -- new tests passing alongside existing 109 tests (target: ~117+ total tests).
3. **Regression analyzer script** -- run `python3 scripts/analyze_partial_trust.py --risk-log <path>` against synthetic JSONL data and show structured metrics output.
4. **Rollout runbook** (`docs/operations/partial-trust-runbook.md`) -- walkthrough of sampling progression, monitoring checklist, and rollback procedure.
5. **ADR-004 index updated** -- `docs/_indexes/adr-index.md` reflects Accepted status.

**Initiative closure signal:** After all 3 stories pass review, INIT-2026Q2-partial-trust can be marked Done (all 4 initiative ACs verified, all 3 deliverables present).

---

## Gate Ask (Gate B)

**Requesting PO approval for:**

1. **Sprint Goal:** Close all remaining gaps for the Partial Trust initiative by delivering formal verification with edge case tests, a regression metrics analyzer script, and an operational rollout runbook.
2. **Committed scope:** 3 stories (ST-005, ST-006, ST-007) as listed above. All 3 pass DoR.
3. **Out-of-scope list:** As documented above -- no changes to existing partial trust implementation, no CI integration, no other NEXT-phase initiatives.
4. **Risk posture:** All risks are Low-Medium probability, owned/mitigated/accepted. No blockers identified. ADR-004 prerequisite already resolved.
5. **Execution model:** Claude prompts + Codex implementation + Human gates, per the established pipeline. Same model as S01 (which completed 4/4 stories successfully).

**Decision requested:** Approve sprint goal and committed scope to proceed with workpack generation for ST-005 and ST-006.
