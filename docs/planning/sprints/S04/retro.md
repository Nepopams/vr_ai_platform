# Sprint S04 -- Retrospective

**Date:** 2026-02-09
**Facilitator:** Claude (Arch/BA)
**Attendees:** Human (PO), Claude (Arch/BA), Codex (Dev)

---

## Sprint Summary

| Metric | Value |
|--------|-------|
| Sprint Goal | Improve clarify question quality (missing_fields, LLM prompt, measurement) |
| Stories committed | 3 |
| Stories completed | 3/3 |
| Stories carried over | 0 |
| Sprint Goal met? | **Yes** |

Initiative status:
- INIT-2026Q2-improved-clarify -> **Done** (closes entire 2026Q2 NEXT phase)

---

## What Went Well

- **13/13 stories across 4 sprints** — zero carry-overs, zero scope changes
- **ST-012 and ST-013 clean first-pass** — no must-fix issues, all tests passed on first review
- **S03 retro lesson applied** — proactively included mock update in ST-013 prompt-apply (line 105 of test_assist_mode.py), avoiding the pattern that caused issues in S03
- **PLAN findings useful despite sandbox limits** — Codex code inference (e.g., minimal_context.json = start_job not clarify) was accurate even without running the code
- **Pipeline maturity** — 4th sprint in a row with same model, predictable throughput

---

## What Did Not Go Well

- **ST-014 required patch cycle** — inline `expected` in fixture JSON broke `test_graph_execution.py` because `command.schema.json` has `additionalProperties: false`. Not caught in workpack design or PLAN.
- **Second issue in patch** — manifest in `commands/` picked up by `run_graph_suite.py`'s `glob("*.json")`. Required moving manifest to parent directory. Two-phase fix for what should have been caught once.
- **Test count target missed** — sprint plan targeted ~196, actual is 202 (exceeded, not a problem, but estimate was off by +3%)

---

## Action Items

| Action | Owner | Due |
|--------|-------|-----|
| When adding data to existing fixture/schema directories, always check what globbers/validators consume those files | Claude | S05+ |
| Add to workpack risk analysis: "Does this file format change break schema validation (additionalProperties)?" | Claude | S05+ |
| Consider two-file pattern (data + metadata) as default for test annotations | Claude | S05+ |

---

## Pipeline Observations

### Claude (Arch/BA) effectiveness
- **Workpack quality:** Good for ST-012/013. ST-014 had a design gap (inline expected vs schema validation).
- **Prompt quality (plan/apply):** Excellent for ST-012/013 (zero must-fix). ST-014 needed patch.
- **Review thoroughness:** Caught the schema issue on first review. Caught manifest glob issue on second review. Fixed directly for second issue.
- **Bottlenecks:** ST-014 two-cycle review added ~30min overhead.

### Codex (Dev) effectiveness
- **PLAN phase accuracy:** All PLAN findings confirmed. Code inference correct even without running tests.
- **APPLY phase quality:** ST-012 and ST-013 perfect. ST-014 faithfully implemented the (flawed) prompt.
- **Deviation from workpack:** None. Codex followed instructions exactly.
- **Bottlenecks:** Sandbox limitation (no pytest/jsonschema) — accepted, permanent.

### Human (PO) gate flow
- **Gate turnaround time:** Fast — all gates same-session.
- **Blocking issues:** None.
- **Communication clarity:** Good.

---

## Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| Stories completed | 3 | 3 |
| Tests passing | All (~196) | 202 |
| DoD compliance | 100% | 100% |
| Gate interactions per story | ~3 | ST-012: 3, ST-013: 3, ST-014: 5 (patch) |
| Codex APPLY attempts | 3 | 4 (ST-014 patch) |
| Must-fix issues on review | 0 | 1 (ST-014 schema break, fixed) |
| Initiatives closed | 1 (improved-clarify) | 1 |

---

## Carry-Forward Items

- Secrets-check grep pattern refinement (carry from S03 — not urgent, no false positives in S04)

---

## Phase Completion Note

With INIT-2026Q2-improved-clarify Done, the entire **2026Q2 NEXT phase** is complete:
- INIT-2026Q2-partial-trust -> Done (S02)
- INIT-2026Q2-multi-entity-extraction -> Done (S03)
- INIT-2026Q2-improved-clarify -> Done (S04)

Next phase: **LATER (2026Q3)** — SemVer/CI, Codex integration, Agent registry.

---

## Next Sprint Candidates

| Initiative | Priority | Comment |
|------------|----------|---------|
| INIT-2026Q3-semver-and-ci | Low | SemVer and CI contract validation. |
| INIT-2026Q3-codex-integration | Low | Codex pipeline integration. |
| INIT-2026Q3-agent-registry-integration | Low | Agent registry and runner for internal agents. |
