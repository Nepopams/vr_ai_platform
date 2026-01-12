# Contracts Guidelines

## SemVer Policy

- Contract definitions follow semantic versioning.
- Increment MAJOR for breaking changes, MINOR for backward-compatible additions, and PATCH for backward-compatible fixes.

## Backward-Compatibility Rules

- Never remove or rename existing fields without a versioned migration plan.
- Only add optional fields or new variants in a way that older consumers can ignore safely.
- Changes must preserve existing meanings and default behaviors.

## Contract Checks

Run contract validation before merging changes:

- `make validate_contracts`
