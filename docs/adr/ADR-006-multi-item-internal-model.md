# ADR-006-P: Multi-Item Internal Model and Quantity Type Alignment

**Status**: Accepted
**Date**: 2026-02-08
**Epic**: EP-004 (Multi-Entity Extraction for Shopping Commands)

## Context

The platform needs to support multi-item shopping commands like "Купи молоко, хлеб и бананы".
Currently the internal pipeline is single-item oriented:

- `extract_item_name()` returns a single `Optional[str]`
- `normalized` dict carries `item_name: str | None`
- V2 planner builds exactly 1 `proposed_action`

The contract schema (`decision.schema.json`) already supports multiple `proposed_actions` in
`start_job_payload` and `shopping_item_payload` with `name`, `quantity` (string), `unit`, `list_id`.

However, there is a type discrepancy:
- **Contract** (`decision.schema.json:93`): `quantity: {"type": "string"}`
- **Agent runner** (`agent_runner/schemas.py:22`): `quantity: {"type": ["number", "null"]}`

We need to decide:
1. The internal model shape for multi-item in the `normalized` dict
2. Which type wins for `quantity`
3. How to maintain backward compatibility during migration

## Decision

### 1. Internal model shape

The `normalized` dict will carry a new field `items: List[dict]` where each dict has:

```python
{
    "name": str,           # required, item name
    "quantity": str | None, # optional, e.g. "2", "пару"
    "unit": str | None,     # optional, e.g. "литра", "kg"
}
```

The existing `item_name: str | None` field is kept as a computed backward-compatibility property:
`item_name = items[0]["name"] if items else None`.

### 2. Quantity type: `string`

**Decision:** Align on `string` everywhere, matching the contract schema.

**Rationale:**
- The contract is the external boundary and must not change (ADR-001-P policy).
- Quantities can be non-numeric ("пару", "немного", "several") -- `string` is the safer type.
- Numeric parsing is the consumer's responsibility, not the platform's.
- `agent_runner/schemas.py` will be updated: `quantity: ["number", "null"]` -> `["string", "null"]`.
  This is a non-breaking change for the agent runner (internal boundary, no external consumers).

### 3. Backward compatibility

| Component | Strategy |
|-----------|----------|
| `normalized["item_name"]` | Kept as first item's name. Computed from `items[0]["name"]`. |
| `extract_item_name()` | Kept. Delegates to `extract_items()[0]["name"]` internally. |
| Partial trust candidate generation | Uses `item_name` (single-item path unchanged). |
| Shadow router | Uses `item_name` (single-item path unchanged). |
| V2 planner | Reads `items` list, generates N `proposed_actions`. Falls back to `item_name` if `items` absent. |
| Assist mode `_apply_entity_hints` | Populates `items` list (all matching items, not just first). |

## Consequences

### Positive

- Multi-item commands produce per-item `proposed_actions` -- directly improves `start_job` rate.
- No contract schema changes required (existing `proposed_actions: array` is sufficient).
- Quantity type aligned across all layers (string everywhere).
- Backward compatibility preserved -- single-item commands behave identically.

### Negative

- `agent_runner/schemas.py` `quantity` type must change from `number` to `string` (ST-009).
  Any agent that relied on numeric quantity will need to parse strings.
  Mitigation: No external agents exist; only `baseline_shopping` agent is affected.
- `item_name` kept as redundant field until all consumers migrate to `items`.
  Mitigation: Acceptable tech debt; removal can be a cleanup story later.
- `additionalProperties: false` on `shopping_item_payload` means attribute hints
  (e.g., "обезжиренное") cannot be added without a contract schema change.
  Mitigation: Attribute hints deferred; not in EP-004 scope.

## Alternatives Considered

### A. Quantity as `number` (align agent_runner direction)

Rejected: Would require contract schema change (`quantity: string` -> `number`), which is a
breaking change per ADR-001-P. Non-numeric quantities ("пару") would need a separate field.

### B. Quantity as `oneOf [string, number]`

Rejected: Adds complexity to validation. Consumers would need to handle both types.
Better to pick one canonical type.

### C. Replace `item_name` with `items` (no backward compat)

Rejected: Would break partial trust, shadow router, and any code reading `item_name`.
Migration cost too high for no user benefit.
