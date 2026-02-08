# Sprint S03: Multi-Entity Extraction for Shopping Commands

**PI:** standalone (aligns with 2026Q2 NEXT phase)
**Period:** 2026-02-15 -- 2026-02-21 (5 calendar days, ~3 working days of Codex effort)
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
| EP-004 epic | `docs/planning/epics/EP-004/epic.md` |
| Initiative (multi-entity-extraction) | `docs/planning/initiatives/INIT-2026Q2-multi-entity-extraction.md` |
| ADR-006-P (multi-item model) | `docs/adr/ADR-006-multi-item-internal-model.md` |

---

## Sprint Goal

Deliver end-to-end multi-item shopping extraction so that commands like "Купи молоко, хлеб и бананы" produce multiple `proposed_actions` (one per item) through the entire pipeline -- baseline extraction, LLM/assist enrichment, and V2 planner -- without breaking contract compatibility, partial trust, or existing single-item behavior.

---

## Pre-completed Work

| Story ID | Title | Status | Notes |
|----------|-------|--------|-------|
| ST-008 | ADR-lite: Multi-item internal model and quantity type resolution | Done (pre-sprint) | ADR-006-P created and Accepted on 2026-02-08. Documented model shape, quantity type alignment (string), backward compat strategy. ADR index updated. |

ST-008 was completed before sprint start during EP-004 decomposition. All three code stories (ST-009, ST-010, ST-011) were blocked by ST-008; that blocker is now resolved.

---

## Committed Scope

| Story ID | Title | Epic | Estimate | Owner | Notes |
|----------|-------|------|----------|-------|-------|
| ST-009 | Baseline multi-item extraction and golden dataset expansion | EP-004 | 1-2 days | Codex | Foundation story: new `extract_items()`, normalized dict, agent_runner schema alignment, golden dataset. 9 ACs, 14 tests. |
| ST-010 | LLM extraction and assist mode multi-item support | EP-004 | 1-2 days | Codex | LLM path: multi-item extraction schema, assist mode hint application for all items. 7 ACs, 10 tests. |
| ST-011 | V2 planner multi-action generation and end-to-end integration | EP-004 | 1-2 days | Codex | Integration story: planner generates N proposed_actions, e2e tests, partial trust regression. 8 ACs, 11 tests. |

**Total estimated effort:** 3-4 working days of Codex implementation + Claude prompts/review overhead.

Story specs:
- `docs/planning/epics/EP-004/stories/ST-009-baseline-multi-item-extraction.md`
- `docs/planning/epics/EP-004/stories/ST-010-llm-assist-multi-item.md`
- `docs/planning/epics/EP-004/stories/ST-011-planner-multi-action-e2e.md`

### DoR Readiness Assessment

| Story | DoR Status | Notes |
|-------|------------|-------|
| ST-009 | Ready | Blocker (ST-008/ADR-006-P) is resolved. ACs are testable (Gherkin, 9 ACs), test strategy defined (14 tests), scope clear, flags assigned. Code touchpoints documented. |
| ST-010 | Ready (managed dependency) | Blocked by ST-009 (must complete first). All other DoR criteria met: 7 ACs in Gherkin, 10 tests identified, code touchpoints documented, flags assigned. Dependency managed via execution order. |
| ST-011 | Ready (managed dependency) | Hard dep on ST-009, soft dep on ST-010. All other DoR criteria met: 8 ACs in Gherkin, 11 tests identified (including partial trust regression), code touchpoints documented. Dependency managed via execution order -- scheduled last. |

---

## Stretch

| Story ID | Title | Condition |
|----------|-------|-----------|
| (none) | -- | All 3 committed stories are code-intensive and fill the sprint capacity. If stories complete early, remaining time should be used for review quality, retro, and S04 candidate identification (INIT-2026Q2-improved-clarify). |

---

## Out of Scope (explicit)

- **Attribute hints** (e.g., "обезжиренное молоко") -- deferred; `additionalProperties: false` on `shopping_item_payload` prevents adding without contract schema change (see ADR-006-P Consequences).
- **Multi-intent commands** (e.g., "купи молоко и убери кухню") -- different intent types in one command; not in EP-004 scope.
- **Complex NLP product ontologies** -- no synonym resolution, no category mapping.
- **User preference memory / personalization** -- explicit MVP anti-scope.
- **Contract schema changes** -- existing `proposed_actions: array` and `shopping_item_payload` are sufficient.
- **Agent runner schema changes beyond quantity type alignment** -- only `quantity: number -> string` per ADR-006-P.
- **Partial trust corridor changes** (EP-003) -- partial trust is tested for regression, not modified.
- **Shadow router logging format changes** -- shadow router is stable, not touched.
- **CI integration of contract validation** -- LATER phase (INIT-2026Q3-semver-and-ci).
- **Improved clarify questions** (INIT-2026Q2-improved-clarify) -- next initiative, not this sprint.
- **Changes to feature flag defaults** -- no new feature flags in this epic.

---

## Capacity Notes

- **Pipeline model:** Claude generates workpacks and prompts, Human gates, Codex implements. Same proven model as S01 (4/4) and S02 (3/3).
- **Codex throughput assumption:** ~1 story per day for code stories (S01/S02 actuals). All 3 stories are code stories with significant test coverage.
- **Buffer:** ~25% implicit (5 calendar days for ~3-4 days of estimated work). Slightly tighter than S02 because all stories are code-intensive (no docs-only stories).
- **Bottleneck risk:** Human gate turnaround. Each story requires 3 gate interactions (prompt-plan gate, prompt-apply gate, review). Budget ~30 min per gate interaction. ST-010 and ST-011 cannot start until ST-009 completes.
- **Parallelism:** ST-009 must run first (foundation). After ST-009 completes, ST-010 and ST-011 are independent and could theoretically run in parallel. However, ST-011 e2e tests cover ST-010 changes, so ST-011 should be reviewed last.
- **S02 retro action items:**
  - Codex pytest in sandbox: if unresolved, verification commands run during Claude review phase (same workaround as S01/S02).
  - Batching gate approvals: consider presenting ST-010 and ST-011 prompt-plans together after ST-009 completes.
  - Secrets-check grep pattern: will refine in workpack verification commands.
- **Test suite baseline:** 131 tests passing (~3.6s). Expected growth: ~35 new tests across 3 stories (target: ~166 tests).

---

## Dependencies

| Dependency | Type | Impact | Status |
|------------|------|--------|--------|
| ADR-006-P accepted | Internal (prerequisite) | ST-009 model decisions depend on ADR. All 3 stories reference ADR-006-P for internal model shape and quantity type. | Done (2026-02-08) |
| ST-009 must complete before ST-010 and ST-011 | Internal (story-to-story) | ST-009 creates `extract_items()` and `normalized["items"]` that ST-010 and ST-011 build upon. | Managed: execution order |
| ST-010 soft dep on ST-011 (review order) | Internal (story-to-story) | ST-011 e2e tests validate the complete pipeline including ST-010 changes. ST-011 should be reviewed after ST-010 is merged. | Managed: execution order |
| Existing test suite passes (131 tests) | Internal (codebase) | New tests depend on baseline tests passing. | Verified: 131 tests pass as of S02 close |
| Partial trust implementation stable | Internal (codebase) | ST-011 regression tests verify partial trust is not broken by multi-item changes. Partial trust code must not change during sprint. | Stable: EP-003 Done, no changes planned |
| `decision.schema.json` supports multi-item | Contract | `proposed_actions: array` and `shopping_item_payload` already support multiple items. | Verified: schema already sufficient |
| Human gate availability | Process | Each story needs 3 gate interactions (PLAN approval, APPLY approval, review) | Accepted: PO aware of pipeline model |

**No external dependencies.** All work is self-contained within the repo.

---

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation | ROAM |
|------|-------------|--------|------------|------|
| Baseline item splitting produces false splits (e.g., "хлеб и масло" as one product vs two) | Medium | Medium | Conservative splitting: only split on explicit list patterns (comma, " и "/ " and " between items). Golden dataset must include edge cases. PLAN phase will inspect existing text patterns. | Owned |
| LLM multi-item extraction may return duplicates or hallucinated items | Low | Medium | Assist mode acceptance rules filter LLM output against original text tokens (existing pattern from EP-002). | Mitigated |
| Changes to `normalized` dict break partial trust candidate generation | Medium | High | ST-011 includes explicit regression test (AC-6). `item_name` backward compat maintained per ADR-006-P. PLAN phase will verify partial trust code paths. | Mitigated |
| ST-009 takes longer than 1 day, blocking ST-010 and ST-011 | Medium | High | ST-009 is the critical path. If delayed, ST-010 and ST-011 cannot start. Buffer allows for 1 extra day. If ST-009 exceeds 2 days, descope ST-011 to stretch. | Owned |
| `quantity: number -> string` in agent_runner breaks existing tests | Low | Low | Only `baseline_shopping` agent uses this field internally. PLAN phase will identify all consumers before APPLY. | Mitigated |
| Golden dataset expansion reveals existing bugs in baseline | Low | Low | Any bugs found are documented and fixed within ST-009 scope (see epic risk register). | Accepted |
| Codex cannot run pytest in sandbox (S01/S02 carry-forward) | Medium | Low | Workaround established: verification runs during Claude review phase. Does not block delivery. | Accepted |
| Human gate turnaround delays sprint (sequential stories) | Medium | Medium | ST-009 is the bottleneck; after that, consider batching ST-010 and ST-011 prompt-plans per S02 retro action item. | Accepted |

---

## Execution Order (recommended)

**Phase 1 (sequential, critical path):**
1. **ST-009** -- Baseline multi-item extraction. Foundation story that all others depend on.
   - Workpack -> prompt-plan -> Codex PLAN -> prompt-apply -> Codex APPLY -> review -> merge.

**Phase 2 (sequential, after ST-009 merged):**
2. **ST-010** -- LLM extraction and assist mode multi-item.
   - Can start immediately after ST-009 is merged.
   - Workpack -> prompt-plan -> Codex PLAN -> prompt-apply -> Codex APPLY -> review -> merge.

3. **ST-011** -- V2 planner multi-action and e2e integration.
   - Should start after ST-010 is merged (soft dependency: e2e tests cover ST-010 changes).
   - If time pressure, can start in parallel with ST-010 but must be reviewed/merged last.
   - Workpack -> prompt-plan -> Codex PLAN -> prompt-apply -> Codex APPLY -> review -> merge.

**Optimization opportunity:** After ST-009 completes, present ST-010 and ST-011 workpacks together. If Human can batch gate approvals (S02 retro action item), both PLAN phases could run closer together.

Start with workpack generation for ST-009 immediately after Gate B approval.

---

## Demo Plan

At sprint end, the following should be demonstrable:

1. **Multi-item baseline extraction** -- Run `extract_items("Купи молоко, хлеб и бананы")` and show it returns 3 separate items with correct names.
2. **Quantity/unit parsing** -- Run `extract_items("Купи 2 литра молока")` and show `{name: "молока", quantity: "2", unit: "литра"}`.
3. **LLM extraction schema** -- Show `SHOPPING_EXTRACTION_SCHEMA` defines `items: array` of structured objects.
4. **Assist mode all-items** -- Show that `_apply_entity_hints()` populates `normalized["items"]` with all matching items (not just first).
5. **V2 planner multi-action** -- Run the full pipeline with "Купи молоко, хлеб и бананы" and show `proposed_actions` contains 3 entries, each with `action="propose_add_shopping_item"`.
6. **Schema compliance** -- Show that the multi-item decision output validates against `contracts/schemas/decision.schema.json`.
7. **Partial trust regression** -- Show that single-item partial trust path still works (ST-011 AC-6).
8. **Test suite growth** -- All tests passing (target: ~166 tests, up from 131).

**Initiative closure signal:** After all 3 code stories pass review, INIT-2026Q2-multi-entity-extraction can be marked Done if all initiative ACs are verified. (Note: may need a brief verification pass similar to S01 ST-002/ST-004 pattern, but the e2e tests in ST-011 should cover this.)

---

## Gate Ask (Gate B)

**Requesting PO approval for:**

1. **Sprint Goal:** Deliver end-to-end multi-item shopping extraction (baseline, LLM/assist, planner) so that multi-item commands produce per-item `proposed_actions` without breaking compatibility or existing behavior.
2. **Pre-completed work:** ST-008 (ADR-006-P) is already done and accepted. No sprint effort required.
3. **Committed scope:** 3 code stories (ST-009, ST-010, ST-011) as listed above. All 3 pass DoR (ST-010 and ST-011 have managed dependencies on ST-009, resolved via execution order).
4. **Out-of-scope list:** As documented above -- no attribute hints, no multi-intent, no contract schema changes, no partial trust modifications, no other NEXT-phase initiatives.
5. **Risk posture:** One High-impact risk (partial trust regression) is actively mitigated via dedicated regression test in ST-011. Critical path risk (ST-009 duration) is owned with buffer. All other risks are Low-Medium.
6. **Execution model:** Claude prompts + Codex implementation + Human gates, per the established pipeline. Same model as S01 (4/4) and S02 (3/3). Sequential execution with ST-009 as critical path.

**Decision requested:** Approve sprint goal and committed scope to proceed with workpack generation for ST-009.
