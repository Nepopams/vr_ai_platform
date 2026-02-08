# Definition of Ready (DoR)

A story/task is **Ready** when it meets ALL criteria below.

## Story Fields Required

- [ ] **Title**: Clear, user-centric (e.g., "User can submit task via natural language")
- [ ] **Description**: Includes context, user value, and expected behavior
- [ ] **Acceptance Criteria**: Testable conditions (Given/When/Then format preferred)
- [ ] **Related ADR**: Link if architecture decision required (see `adr_needed` flag)
- [ ] **Related Contracts**: Link if new API/schema introduced (see `contract_impact` flag)

## Acceptance Criteria Rules

- Must be **testable** (not subjective like "good UX")
- Must specify **happy path** and at least one **edge case**
- Must include **error conditions** if applicable
- Example:
  ```
  Given user submits command "Clean kitchen tonight"
  When AI Platform is available
  Then task is created with zone=kitchen, deadline=today 18:00-22:00
  And DecisionLog entry is created with confidence >= 0.7
  ```

## Test Strategy Required

- [ ] Unit tests identified (which classes/methods)
- [ ] Integration tests identified (which endpoints/flows)
- [ ] Test data/fixtures defined (household, users, zones)

## Flags (Check if Applicable)

- [ ] **contract_impact**: New endpoint, schema, or breaking change → requires contract-writer agent
- [ ] **adr_needed**: Architectural decision → requires ADR (see adr-designer agent)
- [ ] **diagrams_needed**: Structural or flow change → requires diagram update (see diagram-steward agent)
- [ ] **security_sensitive**: Auth/authz change or cross-household data → requires security-reviewer agent
- [ ] **traceability_critical**: Command pipeline change → requires observability-reviewer agent

## Blocked States (Not Ready If...)

- Depends on unfinished work (link blocker)
- External dependency not available (e.g., AI Platform contract not finalized)
- Domain model unclear (needs refinement session)

---

**Responsibility**: BA/Product Owner ensures DoR before Sprint Planning. Engineer can reject story if DoR not met.
