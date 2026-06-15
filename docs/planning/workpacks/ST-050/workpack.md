# Workpack: ST-050 — Domain Planner v1 Narrow Corridor Runtime Adaptation

**Status:** Done (Gate D GO for runtime adaptation scope)
**Story:** `docs/planning/epics/EP-016/stories/ST-050-domain-planner-v1-implementation.md`
**Owner:** Codex PLAN / Codex APPLY / read-only review gate

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Roadmap | `docs/planning/strategy/roadmap.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.md` |
| Execution notes | `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.execution.md` |
| Epic | `docs/planning/epics/EP-016/epic.md` |
| Story | `docs/planning/epics/EP-016/stories/ST-050-domain-planner-v1-implementation.md` |
| Provider mapping | `docs/planning/epics/EP-016/domain-planner-v1-provider-mapping.md` |
| ADR-009 | `docs/adr/ADR-009-domain-planner-v1-narrow-corridor.md` |
| Privacy posture | `docs/guides/domain-planner-v1-privacy-retention.md` |
| ST-049 eval runner | `scripts/evaluate_domain_planner_seed.py` |
| ST-049 local eval report | `docs/planning/workpacks/ST-049/local-seed-eval-report.json` |
| Command schema | `contracts/schemas/command.schema.json` |
| Decision schema | `contracts/schemas/decision.schema.json` |
| Current graph | `graphs/core_graph.py` |
| Current router | `routers/v2.py` |
| ASR route | `app/routes/asr.py` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

HomeTusk read-only fixture source:

```text
C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/domain-planner-v1-gate/golden-scenarios-fixtures-v0/
```

Source revision read during ST-048/ST-049/ST-050 planning: `d924c631c80895995c65f22bec6f77dc0a0347b7`.

---

## Outcome

Adapt the current deterministic provider planner to the Domain Planner v1 narrow corridor using the existing `DecisionDTO` schema. The implementation must improve current blocker evidence without adding first-class `reject`, `confirm`, `answer`, public API changes, HomeTusk writes, or broad planner behavior.

## Artifact Gate Result

**APPROVED for ST-050 runtime APPLY under delegated Gate C.**

| Area | Decision |
|------|----------|
| Gate A | GO: provider-side narrow initiative scope already recorded. |
| Gate B | GO: EP-016 decomposition complete. |
| ST-048 Gate D | GO: provider mapping, ADR, diagram, and privacy posture complete. |
| ST-049 Gate D | GO: eval runner and baseline seed evidence complete. |
| Contract | No contract/schema/version/public API change approved. Current-schema mapping only. |
| ADR/Diagram | Covered by ADR-009 and `docs/diagrams/domain-planner-v1-flow.puml`; no new ADR/diagram expected unless PLAN discovers drift. |
| Security/privacy | No raw HomeTusk fixture text in reports. Runtime must not enable raw text logging or raw LLM output logging. |
| Human Gate C | GO for ST-050 runtime APPLY. PLAN confirmed current-schema implementation, exact runtime files, validation commands, rollback, and no HomeTusk writes. |
| Human Gate D | GO for ST-050 runtime adaptation closure. Seed eval has zero blocker failures; ST-051 closure and handoff remain pending. |

## Acceptance Criteria

1. Current v1 provider path returns schema-valid decisions for simple `create_task` and multi-item `add_shopping_items`.
2. Shopping item boundaries are preserved with one `propose_add_shopping_item` per parsed item.
3. Mixed task/shopping, confirmation-like, reschedule, batch, answer, ambiguous, unsupported, unsafe, cross-household, or unverifiable requests do not produce execute semantics.
4. Safe rejection is represented with current schema as `status=error`, `action=clarify`, and a clarify payload when the planner can identify unsafe or impossible requests.
5. `/v1/decide` continues request/response schema validation.
6. ASR remains transcription-only and does not call `/v1/decide`.
7. ST-049 seed eval report is regenerated and shows zero blocker failure scenarios.
8. No HomeTusk files, contract schemas, contract version, public API files, existing fixtures, `.codex/skills/**`, or production rollout config are changed.

## Files to Change

### New files

| File | Description |
|------|-------------|
| `tests/test_domain_planner_v1_corridor.py` | Regression tests for narrow corridor behavior, schema validity, safe rejection mapping, item boundary preservation, and ASR non-coupling. |
| `docs/planning/workpacks/ST-050/plan-report.md` | Read-only PLAN findings and Gate C recommendation. |
| `docs/planning/workpacks/ST-050/review-report.md` | Read-only review and Gate D recommendation after APPLY. |

### Modified files

| File | Change |
|------|--------|
| `graphs/core_graph.py` | Adapt current deterministic graph to preserve multi-item boundaries and map unsafe/impossible requests to safe current-schema rejection. |
| `routers/v2.py` | Keep RouterV2 behavior aligned with the narrow corridor guardrails. |
| `docs/planning/workpacks/ST-050/workpack.md` | Record Gate C, validation, DoD, and Gate D status. |
| `docs/planning/epics/EP-016/epic.md` | Update ST-050 status after PLAN/APPLY/REVIEW. |
| `docs/planning/epics/EP-016/stories/ST-050-domain-planner-v1-implementation.md` | Update status, evidence, and gate decisions. |
| `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.execution.md` | Record ST-050 Gate C/D decisions and next step. |
| `docs/planning/workpacks/ST-049/local-seed-eval-report.json` | Regenerate eval evidence after runtime adaptation. |

### Deleted files

| File | Reason |
|------|--------|
| None | No deletion authorized. |

## Forbidden Paths

- `contracts/**`
- `contracts/schemas/**`
- `contracts/VERSION`
- `app/**` except read-only inspection of `app/routes/asr.py`, `app/routes/decide.py`, and `app/services/decision_service.py`
- `agents/**`
- `agent_registry/**`
- `agent_runner/**`
- `llm_policy/**`
- `skills/**`
- `.codex/skills/**`
- Existing fixture directories
- HomeTusk repository files
- Production rollout/config files

## Implementation Plan

### Step 1: Codex PLAN

Run the read-only PLAN in `docs/planning/workpacks/ST-050/prompt-plan.md`.

### Step 2: Delegated Gate C

Record GO/HOLD/NO-GO after PLAN. GO is allowed only if the implementation stays current-schema and bounded to the allowed runtime/test/docs paths.

### Step 3: Runtime adaptation

Implement minimal deterministic guardrails:

- preserve multi-item shopping boundaries in the v1 graph path;
- clarify mixed task/shopping or confirm-required requests rather than executing;
- map unsafe/impossible current-schema rejection candidates to `status=error`, `action=clarify`;
- keep version/trace metadata complete;
- keep RouterV2 aligned with the same guardrails.

### Step 4: Tests and eval

Add focused tests and regenerate the ST-049 seed eval report with the same privacy-safe runner.

### Step 5: Read-only review

Run the validation commands and record Gate D. Do not mark the initiative complete until ST-051 closure evidence and HomeTusk handoff notes are complete.

## Verification Commands

```bash
python3 -m pytest tests/test_domain_planner_v1_corridor.py -v
python3 -m pytest tests/test_multi_item_e2e.py tests/test_planner_multi_item.py tests/test_graph_execution.py tests/test_api_decide.py -v
python3 scripts/evaluate_domain_planner_seed.py --source-dir C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/domain-planner-v1-gate/golden-scenarios-fixtures-v0 --check-no-raw-text --output docs/planning/workpacks/ST-049/local-seed-eval-report.json
python3 -m pytest tests/test_domain_planner_seed_eval.py -v
git diff --check
```

On this Windows workspace, validation may need:

```bash
PYTHONPATH=.venv/Lib/site-packages
```

with `python3`, because the system `python3` may not expose repository test dependencies.

## Validation Results

Validation was run on 2026-06-15. The Windows shell used `PYTHONPATH=.;.venv/Lib/site-packages` with `python3` for the full test suite because subprocess checks need both the repository root and bundled site packages.

| Command | Result |
|---------|--------|
| `python3 -m pytest tests/test_domain_planner_v1_corridor.py -v` | Pass: 7 passed |
| `python3 -m pytest tests/test_multi_item_e2e.py tests/test_planner_multi_item.py tests/test_graph_execution.py tests/test_api_decide.py -v` | Pass: 14 passed |
| `python3 scripts/evaluate_domain_planner_seed.py --source-dir C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/domain-planner-v1-gate/golden-scenarios-fixtures-v0 --check-no-raw-text --output docs/planning/workpacks/ST-049/local-seed-eval-report.json` | Pass |
| `python3 -m pytest tests/test_domain_planner_seed_eval.py -v` | Pass: 4 passed |
| `python3 -m pytest tests/ -v` | Pass: 336 passed, 4 skipped |
| `git diff --check` | Pass with LF-to-CRLF warnings only |

Local seed eval metrics after ST-050:

| Metric | Value |
|--------|-------|
| Total scenarios | 10 |
| Evaluated scenarios | 10 |
| Schema-valid decisions | 10 |
| Outcome matches | 10 |
| Intent matches | 3 |
| Unsupported auto-execute | 0 |
| Cross-household references | 0 |
| Blocker failure scenarios | 0 |

Remaining non-blocker failure buckets:

| Bucket | Count |
|--------|-------|
| `wrong_intent` | 7 |
| `item_boundary_loss` | 2 |

## Tests

| Test | Checks | Expected |
|------|--------|----------|
| `tests/test_domain_planner_v1_corridor.py` | Narrow corridor guardrails and schema validity | Pass |
| `tests/test_multi_item_e2e.py` | Existing RouterV2 multi-item behavior | Pass |
| `tests/test_planner_multi_item.py` | Existing RouterV2 planning units | Pass |
| `tests/test_graph_execution.py` | Existing graph suite validity | Pass |
| `tests/test_api_decide.py` | `/v1/decide` request/response schema validation | Pass |
| `scripts/evaluate_domain_planner_seed.py --check-no-raw-text` | HomeTusk seed eval with no raw report output | Pass with zero blocker failures |

## DoD Checklist

- [x] Read-only PLAN completed.
- [x] Delegated Gate C GO/HOLD/NO-GO recorded.
- [x] Contract no-impact decision recorded.
- [x] Runtime edits stay inside allowed paths.
- [x] Seed eval regenerated with zero blocker failures.
- [x] ASR non-coupling regression covered.
- [x] No HomeTusk files changed.
- [x] No contract/schema/version/public API files changed.
- [x] Review report records Gate D recommendation.

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Heuristics become broad planner behavior | Medium | High | Keep rules limited to explicit narrow corridor guardrails and clarify/reject outside scope. |
| Current-schema reject mapping is semantically rough | High | Medium | Use documented `status=error` + `action=clarify`; defer first-class reject to a contract workpack. |
| Seed eval still reports non-blocker quality gaps | Medium | Medium | Gate D requires zero blocker failures; ST-051 can document remaining non-blocker evidence. |
| Existing RouterV2 tests expect execution for broad shopping text | Low | Medium | Preserve simple shopping behavior; only mixed/unsafe/unsupported cases clarify/reject. |
| Raw text leaks into generated planning artifacts | Low | High | Use scenario IDs, metrics, and failure buckets only in docs. |

## Rollback

Revert `graphs/core_graph.py`, `routers/v2.py`, `tests/test_domain_planner_v1_corridor.py`, ST-050 docs, and regenerated eval report. No schema or public API rollback should be needed.

## APPLY Boundaries

### Allowed

- `graphs/core_graph.py`
- `routers/v2.py`
- `tests/test_domain_planner_v1_corridor.py`
- `docs/planning/workpacks/ST-050/**`
- `docs/planning/workpacks/ST-049/local-seed-eval-report.json`
- `docs/planning/epics/EP-016/epic.md`
- `docs/planning/epics/EP-016/stories/ST-050-domain-planner-v1-implementation.md`
- `docs/planning/initiatives/INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor.execution.md`

### Forbidden

- Contracts, schemas, public API, existing fixtures, HomeTusk files, `.codex/skills/**`, and production rollout/config files listed above.

## Human Gates

- Gate A: GO recorded in initiative execution notes.
- Gate B: GO for provider planning and EP-016 decomposition.
- ST-048 Gate D: GO.
- ST-049 Gate D: GO.
- Human Gate C: GO for ST-050 runtime APPLY.
- Human Gate D: GO for ST-050 runtime adaptation scope.
