# Definition of Done (DoD)

A task is **Done** when it meets ALL criteria below.

## Code Quality

- [ ] Code follows project conventions (Java 21, Spring Boot idioms)
- [ ] Spotless formatting applied (`./gradlew spotlessApply`)
- [ ] No compiler warnings introduced
- [ ] No SonarLint critical issues (if applicable)
- [ ] Code reviewed by at least one peer (PR review)

## Tests Required

- [ ] **Unit tests** written and passing
  - Coverage: New business logic must have unit tests
  - Mocking: External dependencies (AI Platform, DB) mocked appropriately
- [ ] **Integration tests** written and passing
  - Coverage: New endpoints/flows must have integration tests
  - Testcontainers: PostgreSQL container used for DB-dependent tests
- [ ] All tests pass locally: `./scripts/test.sh`
- [ ] Test data cleanup: No test pollution (each test isolated)

## Documentation Updates

- [ ] **API Contract** updated if endpoint/schema changed (`docs/contracts/`)
- [ ] **ADR** created/updated if architectural decision made (`docs/adr/`)
- [ ] **Diagrams** updated if structure/flow changed (`docs/diagrams/`)
- [ ] **Service Catalog** updated if service boundaries changed (`docs/architecture/service-catalog.md`)
- [ ] **CLAUDE.md** updated if development rules changed
- [ ] **Indexes** updated:
  - `docs/_indexes/adr-index.md` if ADR added
  - `docs/_indexes/contracts-index.md` if contract added
  - `docs/_indexes/diagrams-index.md` if diagram added

## Observability (If Applicable)

- [ ] Command traceability verified (correlationId propagated)
- [ ] DecisionLog entry created for command pipeline changes
- [ ] Logs include sufficient context for debugging
- [ ] Metrics/events published if required (TaskCreated, TaskAssigned, etc.)

## Security Basics

- [ ] **No cross-household data leaks** (verified by security-reviewer agent)
- [ ] **No hardcoded secrets** (use environment variables or config)
- [ ] **Input validation** present at API boundary
- [ ] **Auth/authz** enforced if endpoint requires it (JWT validation)

## CI/CD

- [ ] Build passes in CI (if applicable)
- [ ] No breaking changes to stable endpoints without versioning
- [ ] Database migrations tested (if schema changed)

## Definition of "Done"

**Task is Done** = Code merged to main branch + All DoD criteria met.

**NOT Done** if:
- Tests fail
- PR not approved
- DoD checklist incomplete
- Breaking change without migration plan

---

**Responsibility**: Engineer ensures DoD before marking task complete. Reviewer blocks merge if DoD not met.
