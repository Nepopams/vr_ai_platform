---
name: schema-bump
description: Safely bumps contract schema versions following compatibility rules and updates related metadata.
---

# Schema Bump Skill

## Purpose
Automates controlled version increments for contract schemas while enforcing
compatibility and versioning policies defined in ADR-001.

## Inputs
- Current schema version in `contracts/VERSION`.
- Contract schemas in `contracts/schemas/`.

## Outputs
- Updated version files and schemas.
- Summary of version changes.

## Rules
- Breaking changes require major version bump.
- Backward-compatible changes require minor version bump.
- Patch versions are reserved for documentation or metadata-only changes.

## Definition of Done (DoD)
- Version updated according to change type.
- Schemas remain valid.
- No unintentional breaking changes introduced.
