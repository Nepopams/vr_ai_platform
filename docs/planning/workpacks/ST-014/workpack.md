# Workpack: ST-014 — Clarify Golden Dataset Ground Truth and Quality Measurement

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Story spec | `docs/planning/epics/EP-005/stories/ST-014-clarify-golden-dataset-measurement.md` |
| Contract schema | `contracts/schemas/decision.schema.json` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

Add ground truth annotations to clarify-triggering golden fixtures, create 2 new clarify edge-case fixtures, and build a measurement script that computes missing_fields match rate across the golden dataset.

## Current State

### Golden dataset (`skills/graph-sanity/fixtures/commands/`)
14 fixtures total. Clarify-triggering fixtures (no `expected` annotations):
- `empty_text.json` — whitespace text, should clarify with `missing_fields=["text"]`
- `unknown_intent.json` — "Что-то непонятное про погоду", should clarify with `missing_fields=["intent"]`
- `minimal_context.json` — "Сделай что-нибудь полезное", should clarify with `missing_fields` depending on intent detection

### Existing analyzer scripts
- `scripts/analyze_shadow_router.py` — shadow router JSONL analyzer
- `scripts/analyze_partial_trust.py` — partial trust risk-log analyzer (pattern reference)

---

## Acceptance Criteria

- AC-1: Clarify fixtures have `expected` ground truth annotations
- AC-2: Measurement script computes missing_fields match rate
- AC-3: At least 2 new clarify-specific fixtures added
- AC-4: Script handles both V1 and V2 routers
- AC-5: Script has unit tests
- AC-6: All 192 existing tests pass

---

## Files to Change

| File | Action |
|------|--------|
| `skills/graph-sanity/fixtures/commands/empty_text.json` | Add `expected` annotation |
| `skills/graph-sanity/fixtures/commands/unknown_intent.json` | Add `expected` annotation |
| `skills/graph-sanity/fixtures/commands/minimal_context.json` | Add `expected` annotation |
| `skills/graph-sanity/fixtures/commands/clarify_partial_shopping.json` | New fixture |
| `skills/graph-sanity/fixtures/commands/clarify_ambiguous_intent.json` | New fixture |
| `scripts/analyze_clarify_quality.py` | New script |
| `tests/test_clarify_measurement.py` | New test file |

---

## Invariants (DO NOT break)

- `routers/v2.py` — NOT modified
- `routers/assist/runner.py` — NOT modified
- `graphs/core_graph.py` — NOT modified
- `contracts/schemas/` — NOT modified
- Existing fixture JSON structure (command fields) — NOT changed, only `expected` key added
- Existing tests — NOT modified
