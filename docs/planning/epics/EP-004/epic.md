# EP-004: Multi-Entity Extraction for Shopping Commands

**Status:** Ready
**Initiative:** `docs/planning/initiatives/INIT-2026Q2-multi-entity-extraction.md`
**Owner:** TBD

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q2-multi-entity-extraction.md` |
| Contract schema (decision) | `contracts/schemas/decision.schema.json` |
| Contract schema (command) | `contracts/schemas/command.schema.json` |
| ADR-001 (contract versioning) | `docs/adr/ADR-001-contract-versioning-compatibility-policy.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

Shopping commands frequently contain lists: "молоко, хлеб и бананы", plus quantities and simple
attributes. The current extraction pipeline is entirely single-item oriented:

- `extract_item_name()` returns a single `Optional[str]` -- "хлеб и яйца" becomes one string.
- LLM extraction schema (`SHOPPING_EXTRACTION_SCHEMA`) has a single `item_name` field.
- V2 planner builds exactly 1 `proposed_action` from a single `item_name`.
- Assist mode entity hints pick only the FIRST item from LLM arrays.
- Agent runner schema already supports multi-item (`items: array`), but this is not wired through.

The existing contract schema (`decision.schema.json`) already supports `proposed_actions: array`
and `shopping_item_payload` with name/quantity/unit/list_id -- so multi-item is contract-compatible.

There is one discrepancy to resolve: `quantity` is `string` in the contract schema but `number`
in `agent_runner/schemas.py`.

## Goal

Deliver multi-item shopping extraction so that commands like "Купи молоко, хлеб и бананы"
produce multiple `proposed_actions`, one per item, without breaking contract compatibility.

1. Resolve the quantity type discrepancy (ADR-lite)
2. Update baseline extraction to split and return multiple items
3. Update LLM extraction and assist mode to work with multiple items
4. Update V2 planner to generate multiple proposed_actions and prove end-to-end

## Scope

### In scope

- ADR-lite documenting internal multi-item model and quantity type resolution
- Baseline extraction: split comma/conjunction-separated items
- LLM extraction schema: multi-item support
- Assist mode: use all items (not just first)
- V2 planner: generate N proposed_actions for N items
- Golden dataset expansion with multi-item expectations
- Quantity/unit parsing (basic: "2 литра молока", "3 eggs")
- Unit tests and integration tests for all changes

### Out of scope

- Complex NLP product ontologies
- User preference memory / personalization
- Task execution
- Attribute hints in contract schema (requires `additionalProperties` change -- deferred)
- Changes to partial trust corridor (EP-003)
- Changes to shadow router logging format
- Multi-intent support (e.g., "купи молоко и убери кухню" -- still picks first intent)
- Agent runner schema changes beyond quantity type alignment
- CI integration of contract validation

## Stories

| Story ID | Title | Status | Flags |
|----------|-------|--------|-------|
| [ST-008](stories/ST-008-multi-item-model-adr.md) | ADR-lite: Multi-item internal model and quantity type resolution | Done (ADR-006-P Accepted) | contract_impact=review, adr_needed=lite |
| [ST-009](stories/ST-009-baseline-multi-item-extraction.md) | Baseline multi-item extraction and golden dataset expansion | Ready (unblocked) | contract_impact=no |
| [ST-010](stories/ST-010-llm-assist-multi-item.md) | LLM extraction and assist mode multi-item support | Ready (dep: ST-009) | contract_impact=no |
| [ST-011](stories/ST-011-planner-multi-action-e2e.md) | V2 planner multi-action generation and end-to-end integration | Ready (dep: ST-009, soft: ST-010) | contract_impact=review |

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| EP-003 (Partial Trust) | Internal | Done -- no hard dependency, but ST-011 must not break partial trust |
| `contracts/schemas/decision.schema.json` supports multi-item | Contract | Done (proposed_actions is already array) |
| `agent_runner/schemas.py` multi-item schema | Internal | Done (already returns items array) |
| Quantity type discrepancy resolution | Internal | Done -- resolved in ADR-006-P (align on string) |

### Story ordering

```
ST-008 (ADR-lite, no code)
  |
  v
ST-009 (baseline extraction + golden dataset)
  |
  +-------+-------+
  v               v
ST-010          ST-011
(LLM/assist)   (planner/e2e)
```

- ST-008 must be completed first (establishes model decisions).
- ST-009 depends on ST-008 (implements the model).
- ST-010 and ST-011 can run in parallel after ST-009.
- ST-011 includes end-to-end tests that validate the complete pipeline including ST-010 changes,
  so if run in parallel, ST-011 should be completed/reviewed last.

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Baseline item splitting produces false splits (e.g., "хлеб и масло" as one product vs two) | Medium | Medium | Conservative splitting: only split on explicit list patterns (comma, "и"/"and" between items). Golden dataset must include edge cases. |
| LLM multi-item extraction may return duplicates or hallucinated items | Low | Medium | Assist mode acceptance rules filter LLM output against original text tokens. |
| Quantity type discrepancy may require contract schema change | Low | Low | ADR-lite (ST-008) will determine alignment direction. Contract `quantity: string` can represent "2" as string. |
| Changes to `normalized` dict may break partial trust candidate generation | Medium | High | ST-011 integration tests must verify partial trust still works. `item_name` backward compat maintained. |
| Golden dataset expansion may reveal existing bugs in baseline | Low | Low | Any bugs found are documented and fixed within ST-009. |

## Readiness Report

### Done
- **ST-008** -- ADR-006-P created and Accepted (2026-02-08). All decisions documented.

### Ready
- **ST-009** -- Unblocked (ST-008 Done). All DoR criteria met. Sprint S03 committed.
- **ST-010** -- DoR met. Managed dependency on ST-009 (execution order). Sprint S03 committed.
- **ST-011** -- DoR met. Hard dep on ST-009, soft dep on ST-010 (execution order). Sprint S03 committed.
