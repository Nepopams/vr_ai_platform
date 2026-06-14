> Legacy notice: active workflow now lives in AGENTS.md and docs/CODEX-WORKFLOW.md. This file or directory is historical reference only. Do not use it as active workflow authority.

---
description: Generate Gate B or Exit Review artifact from templates.
argument-hint: "gate-b <sprint-XX> | exit-review <sprint-XX>"
---

Context (read):
- @docs/planning/mvp.md
- @docs/_governance/dod.md
- @docs/planning/_templates/gate-b.md
- @docs/planning/_templates/exit-review.md

Task:
- If `$ARGUMENTS` starts with `gate-b`:
  - create/update `docs/planning/gates/sprint-$SPRINT-gate-b.md`
- If `$ARGUMENTS` starts with `exit-review`:
  - create/update `docs/planning/reviews/sprint-$SPRINT-exit-review.md`

Hard rules:
- Always include Sources of Truth.
- Do not invent evidence; if missing, list Missing inputs.
