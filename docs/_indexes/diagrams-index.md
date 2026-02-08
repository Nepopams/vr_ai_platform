# Diagrams Index

This index tracks all architecture and flow diagrams in the project.

## How to Use

- **Diagram**: Descriptive name
- **Type**: C4 (context/container/component), sequence, flow, ERD, etc.
- **Purpose**: What does this diagram explain?
- **Link**: Relative path from repo root

## Index

| Diagram | Type | Purpose | Link |
|---------|------|---------|------|
| System Context (MVP) | C4 Level 1 | High-level system boundaries | [Link](../architecture/decisions/mvp/01-system-context.md) |
| Container Diagram (MVP) | C4 Level 2 | Services and data stores | [Link](../architecture/decisions/mvp/02-container.md) |
| Component Diagram (Backend) | C4 Level 3 | Backend internal structure | [Link](../architecture/decisions/mvp/03-component-backend.md) |
| Command Processing Flow | Sequence | NL command → task creation | [Link](../architecture/diagrams/command-processing-flow.md) |

## Diagram Lifecycle

- **Current**: Reflects implemented architecture
- **Proposed**: Design for upcoming changes
- **Superseded**: Archived, replaced by newer diagram

## When to Update

Run `diagram-steward` agent when:
- New service/component added
- Service boundaries change
- Integration points change
- Command/data flow changes

**Note**: Not every code change requires a diagram update. Diagram updates are needed only for **structural or flow changes**.

---

**Maintenance**: Update this index when running diagram-steward agent or manually adding diagrams.
