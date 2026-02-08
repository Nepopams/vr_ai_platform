# Vibe Status Command

**Command**: `/vibe-status`

**Purpose**: Show artifact map and completion status for VIBE Kit documentation.

---

## What This Command Does

Displays a **read-only status report** of VIBE Kit artifacts:
- Which documentation files exist vs missing
- Which indexes are populated vs empty
- Which agents are available
- TODO list for human to complete

**This command does NOT**:
- Modify any files
- Run tests or linters
- Execute code

---

## Usage

```
/vibe-status
```

---

## Expected Output

```
VIBE Kit Status Report
======================

📁 Documentation Structure
  ✅ docs/_governance/
    ✅ dor.md (Definition of Ready)
    ✅ dod.md (Definition of Done)
  ✅ docs/_indexes/
    ✅ adr-index.md
    ✅ contracts-index.md
    ✅ diagrams-index.md
  ✅ docs/planning/
    ✅ mvp.md
    ✅ epics/ (README present)
    ✅ workpacks/ (README present)
    ✅ pi/ (README present)
  ✅ docs/contracts/ (README present)
  ✅ docs/adr/ (README present)
  ✅ docs/diagrams/ (README present)

🤖 Agents Available
  Existing (Quality Gates):
    ✅ arch-reviewer
    ✅ contract-writer
    ✅ observability-reviewer
    ✅ security-reviewer
    ✅ test-writer

  New (Planning & Orchestration):
    ✅ triage-manager
    ✅ pi-planner
    ✅ sprint-planner
    ✅ epic-decomposer
    ✅ adr-designer
    ✅ diagram-steward
    ✅ plan-generator
    ✅ dev-prompt-engineer
    ✅ codex-review-gate

📋 Indexes Status
  ✅ ADR Index: 5 entries (ADR-001 to ADR-009)
  ✅ Contracts Index: 4 entries
  ✅ Diagrams Index: 4 entries

🚧 TODO for Human
  [ ] Fill MVP scope details in docs/planning/mvp.md
  [ ] Customize DoR/DoD for HomeTusk tech stack
  [ ] Migrate existing ADRs from docs/architecture/decisions/ to docs/adr/
  [ ] Migrate existing diagrams from docs/architecture/diagrams/ to docs/diagrams/
  [ ] Define test/lint commands in docs/_governance/ or scripts/
  [ ] Create first epic in docs/planning/epics/
  [ ] (Optional) Create PI-1 artifacts if using PI planning
```

---

## Implementation Notes

This command should:
1. Use `Read` tool to check file existence
2. Use `Glob` to list directories
3. Count entries in index files
4. Output formatted status report
5. NOT modify any files

---

See also: `CLAUDE.md` for VIBE Kit overview and pipeline.
