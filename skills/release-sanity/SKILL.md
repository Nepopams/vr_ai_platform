# Release Sanity Skill

## Inputs
- Contract fixtures.
- Decision log fixtures.
- Core graph pipeline.

## Outputs
- Consolidated report of release checks.

## Steps
1. Run contract fixture validation.
2. Audit decision logs.
3. Execute core graph sanity suite.
4. Emit a consolidated pass/fail status.

## Definition of Done (DoD)
- All sub-checks run in order.
- Failures are surfaced with clear messaging.
- Script exits with non-zero status if any sub-check fails.
