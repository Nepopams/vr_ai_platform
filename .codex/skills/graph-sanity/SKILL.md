---
name: graph-sanity
description: Runs deterministic sanity checks against the decision graph to ensure outputs conform to MVP rules and DecisionDTO schema.
---

# Graph Sanity Skill

## Purpose
Ensures the decision graph produces valid, deterministic DecisionDTO outputs
for a set of predefined command fixtures.

## Inputs
- Command fixtures in `.codex/skills/graph-sanity/fixtures/commands/`.
- Decision graph implementation in `graphs/core_graph.py`.
- Decision JSON Schema in `contracts/schemas/decision.schema.json`.

## Outputs
- Validation report printed to stdout.
- Non-zero exit code on any schema or rule violation.

## Checks
- Output DecisionDTO conforms to schema.
- `action` is limited to MVP enum.
- `schema_version` matches `contracts/VERSION`.
- Deterministic `decision_version`.

## Definition of Done (DoD)
- All fixtures pass validation.
- No unexpected actions or payload shapes.
- Script exits with status 0.
