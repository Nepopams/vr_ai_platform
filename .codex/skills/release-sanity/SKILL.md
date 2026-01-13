---
name: release-sanity
description: Aggregates all critical sanity checks required before a release, ensuring contracts, graphs, and logs are consistent.
---

# Release Sanity Skill

## Purpose
Acts as a release gate by executing a predefined set of validation skills
required for a safe platform release.

## Inputs
- Contract schemas and fixtures.
- Decision graph fixtures.
- Optional decision logs (if present).

## Outputs
- Combined report of all executed checks.
- Non-zero exit code if any included check fails.

## Includes
- contract-checker
- graph-sanity
- decision-log-audit (if logs are present)
- api-sanity (optional, environment-dependent)

## Definition of Done (DoD)
- All included sanity checks pass.
- Script exits with status 0 indicating release readiness.
