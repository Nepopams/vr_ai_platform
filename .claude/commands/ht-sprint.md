---
description: Generate Sprint doc + Gate B using templates and strict Sources-of-Truth links.
argument-hint: "<sprint-XX> <ST-001> <ST-002> ..."
---

Use the **sprint-planner** subagent.

Context (read):
- @docs/planning/mvp.md
- @docs/_governance/dor.md
- @docs/_governance/dod.md
- @docs/planning/_templates/sprint.md
- @docs/planning/_templates/gate-b.md
- Relevant epic/story specs for the provided ST-* (find them under docs/planning/epics/**)

Task:
1) Interpret `$ARGUMENTS` as: sprint number + list of story IDs.
2) Create/update:
   - `docs/planning/sprints/sprint-$SPRINT.md`
   - `docs/planning/gates/sprint-$SPRINT-gate-b.md`
3) Fill documents strictly following templates.
4) MUST include:
   - Sources of Truth links (MVP + epic/story + DoR/DoD; ADR/contracts/diagrams only if relevant)
   - committed/stretch/out-of-scope
   - capacity note
   - dependencies + risks
5) If missing inputs → write "Missing inputs" section and stop at Human Gate B.
