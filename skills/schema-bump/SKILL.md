# Schema Bump Skill

## Inputs
- Old and new JSON schema files.
- Optional version override.

## Outputs
- Updated schema file with bumped version metadata.
- Report of any detected breaking changes.

## Steps
1. Read the schema file targeted for version updates.
2. Bump the schema version metadata.
3. Compare old/new schemas to detect breaking changes.
4. Emit a report and exit with a non-zero status if breaking changes exist.

## Definition of Done (DoD)
- Version bump updates the intended schema file.
- Breaking change checks correctly detect required-field removals.
- Scripts exit with clear messaging and appropriate status codes.
