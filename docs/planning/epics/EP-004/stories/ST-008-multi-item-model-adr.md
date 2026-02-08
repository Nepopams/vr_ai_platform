# ST-008: ADR-lite: Multi-Item Internal Model and Quantity Type Resolution

**Status:** Ready
**Epic:** `docs/planning/epics/EP-004/epic.md`
**Owner:** TBD

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-004/epic.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q2-multi-entity-extraction.md` |
| Contract schema (decision) | `contracts/schemas/decision.schema.json` |
| Agent runner schema | `agent_runner/schemas.py` |
| ADR-001 (contract versioning) | `docs/adr/ADR-001-contract-versioning-compatibility-policy.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Description

As a platform architect, I need a documented decision on the internal multi-item data model
and the resolution of the quantity type discrepancy, so that all subsequent stories (ST-009
through ST-011) have a clear, agreed-upon model to implement against.

### Current state

- The `normalized` dict uses `item_name: str | None` (singular).
- `agent_runner/schemas.py` defines `quantity` as `number | null`.
- `contracts/schemas/decision.schema.json` defines `quantity` as `string`.
- Both schemas support the same fields (name, quantity, unit) but differ on quantity type.

### Decisions to make

1. **Internal model shape**: What replaces `item_name: str` in the normalized dict?
   Proposed: `items: List[dict]` where each dict has `{name: str, quantity: str|None, unit: str|None}`.
2. **Quantity type**: Align on `string` (matching contract) or `number` (matching agent_runner)?
   Proposed: Keep contract as `string` (no breaking change). Align `agent_runner/schemas.py`
   quantity to `string | null` to match. Rationale: quantities like "пару", "немного" are
   better as strings; numeric parsing is the consumer's responsibility.
3. **Backward compatibility**: How does `item_name` coexist during migration?
   Proposed: Keep `item_name` as computed property (first item's name) for backward compat
   with partial trust and shadow router. Add `items` as the primary field.

## Acceptance Criteria

```gherkin
AC-1: ADR-lite document exists and covers required decisions
  Given a file at docs/adr/ADR-006-multi-item-internal-model.md
  When a reviewer reads it
  Then it documents:
    - the internal model shape (items list with name/quantity/unit)
    - the quantity type resolution (string, aligned with contract)
    - the backward compatibility strategy (item_name kept for compat)
  And the Status is "Accepted"

AC-2: ADR index is updated
  Given docs/_indexes/adr-index.md
  When a reviewer reads it
  Then ADR-006 is listed with status "accepted"

AC-3: Agent runner schema quantity type is documented as needing alignment
  Given the ADR-006 document
  When a reviewer reads the "Consequences" section
  Then it states that agent_runner/schemas.py quantity type must change
    from number to string in ST-009 implementation
  And it references ADR-001 non-breaking change rules as justification
```

## Scope

### In scope

- Create `docs/adr/ADR-006-multi-item-internal-model.md` (ADR-lite format)
- Document the three decisions: model shape, quantity type, backward compat
- Update `docs/_indexes/adr-index.md`

### Out of scope

- Any code changes (this is documentation only)
- Contract schema changes (confirmed: existing schema suffices)
- Changes to agent_runner/schemas.py (deferred to ST-009)
- Attribute hints (e.g., "обезжиренное") -- deferred, not in contract schema

## Test Strategy

- None (documentation-only story)

## Flags

- contract_impact: review (confirms existing schema suffices, no changes needed)
- adr_needed: lite (this story IS the ADR)
- diagrams_needed: none
- security_sensitive: no
- traceability_critical: no

## Blocked By

- None
