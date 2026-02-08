---
description: Generate implementation-grade Workpack package for a given story ID (ST-*).
argument-hint: "<ST-001>"
---

Use the **plan-generator** subagent.

Context (read):
- @docs/planning/mvp.md
- @docs/_governance/dod.md
- @docs/planning/_templates/workpack.md

Task:
1) `$ARGUMENTS` contains a single Story ID like `ST-001`.
2) Create/update directory:
   - `docs/planning/workpacks/$STORY_ID/`
3) Create/update:
   - `docs/planning/workpacks/$STORY_ID/workpack.md` (based on template)
   - `docs/planning/workpacks/$STORY_ID/checklist.md` (short checklist derived from AC + DoD)
4) Workpack must contain:
   - Sources of Truth (MVP + epic/story; conditional ADR/contracts/diagrams)
   - explicit Files to change (paths)
   - verification commands + expected results
   - DoD checklist + rollback
5) If you cannot name file paths → write "Missing inputs: file pointers" and stop.
