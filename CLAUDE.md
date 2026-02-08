# CLAUDE.md — Hometusk + AI Platform delivery pipeline (Claude=Arch/BA, Codex=Dev)

## Mission
This repo is developed via a controlled “vibe-coding” pipeline:
- **Claude Code = Analysis & Architecture department** (triage → planning → decomposition → artifacts).
- **Codex = Development department** (implementation + tests + docs-as-code).
- **Human = Product owner & final gate** (approve decisions, plans, scope, and merges).

Primary objective: **deliver in small batches with strong governance**:
- explicit scope boundaries,
- contract-first for integrations,
- decision log (ADR) only when architecture-significant,
- diagrams as code only when structural/flow changes matter,
- pre-merge review gate.

---

## Source of truth (always anchor)
Project truth lives in repo artifacts. Claude must reference files, not “memory”.

### Planning anchors (always)
- Product goal (target state): `docs/planning/strategy/product-goal.md`
- Roadmap (Now/Next/Later): `docs/planning/strategy/roadmap.md`
- Scope anchor (choose exactly one per planning cycle):
  - Release scope: `docs/planning/releases/<RELEASE>.md` (e.g., `docs/planning/releases/MVP.md`)
  - Initiative scope: `docs/planning/initiatives/INIT-*.md`

> Note: `docs/planning/mvp.md` is legacy/redirect only. Use `docs/planning/releases/MVP.md` as canonical.

### Planning (delivery hierarchy)
- PI plans (optional): `docs/planning/pi/<PI_ID>/`
- Epics & stories: `docs/planning/epics/<EPIC_ID>/`
- Work packages (delivery plans): `docs/planning/workpacks/<STORY_ID>/`

### Governance
- DoR (Definition of Ready): `docs/_governance/dor.md`
- DoD (Definition of Done): `docs/_governance/dod.md`

### Contracts / Decisions / Diagrams
- Contracts (API/DTO/events): `docs/contracts/**`
- ADR decision log (canonical): `docs/adr/**`
  - legacy (if not migrated): `docs/architecture/decisions/**`
- Diagrams as code (PlantUML) (canonical): `docs/diagrams/**`
  - legacy (if not migrated): `docs/architecture/diagrams/**`

### Indexes (navigation)
- ADR index: `docs/_indexes/adr-index.md`
- Contracts index: `docs/_indexes/contracts-index.md`
- Diagrams index: `docs/_indexes/diagrams-index.md`

---

## Imports (keep this file slim)
When helpful, Claude should pull exact docs into context via imports (fast + stable):
- Product goal: @docs/planning/strategy/product-goal.md
- Roadmap: @docs/planning/strategy/roadmap.md
- Current scope anchor: @docs/planning/releases/MVP.md
- DoR: @docs/_governance/dor.md
- DoD: @docs/_governance/dod.md

(Claude Code supports `@path` imports in CLAUDE.md.) 

---

## Artifact map & naming conventions

### IDs
- PI: `YYYYQn-PI##`  (e.g., `2026Q1-PI01`)
- Sprint: `S##`      (e.g., `S01`)
- Epic: `EP-###`
- Story: `ST-###`
- Initiative: `INIT-YYYYQn-<slug>` (e.g., `INIT-2026Q2-reliability`)

### Standard folders

#### Strategy / Portfolio (long-lived anchors)
- `docs/planning/strategy/`
  - `product-goal.md` — target state (always referenced)
  - `roadmap.md` — Now/Next/Later or quarter map
- `docs/planning/releases/`
  - `<RELEASE>.md` — release scope, exit criteria, non-goals (e.g., `MVP.md`)
- `docs/planning/initiatives/`
  - `INIT-*.md` — initiative scope (alternative to release scope)

#### PI planning (optional)
- `docs/planning/pi/<PI_ID>/`
  - `pi.md` — PI charter (goals/non-goals/exit criteria)
  - `objectives.md` — PI objectives (measurable)
  - `backlog.md` — initiatives/epics list (links)
  - `roadmap.md` — rough mapping Sprints → Epics
  - `risks.md` — risk register (ROAM-lite)
  - `capacity.md` — capacity assumptions + buffers
  - `decisions.md` — links to ADR/contracts/diagrams relevant to PI
  - `sprints/Sxx/`
    - `sprint.md` — sprint goal + committed scope + deps + risks + anchors
    - `scope.md` — in/out + readiness notes
    - `demo.md` — demo plan
    - `retro.md` — retro template

#### Epics & Stories
- `docs/planning/epics/<EPIC_ID>/`
  - `epic.md` — epic charter + boundaries + story list
  - `stories/ST-###-*.md` — story specs (AC, scope, flags)

#### Workpacks (implementation packets for Codex)
- `docs/planning/workpacks/<STORY_ID>/`
  - `workpack.md` — executable delivery plan (steps/files/checks/rollout)
  - `checklist.md` — AC/DoD verification checklist
  - `risks.md` — optional per-story risks (ROAM-lite)
  - `prompt-plan.md` — Codex PLAN prompt (generated after workpack approval)
  - `prompt-apply.md` — Codex APPLY prompt (generated after plan approval)
  - (review conducted by Claude Code directly, no prompt file)

---

## Pipeline (end-to-end operating model)
> Principle: **minimal process that preserves correctness**, with explicit gates.

### 0) Intake (Human → Claude)
Human provides:
- goal & constraints,
- success criteria (DoD expectations),
- urgency & risk tolerance,
- identifies current scope anchor (Release or Initiative).

### 1) Triage (Claude: triage-manager)
Output: **Triage Summary** (type/level/risk/impacts) + next step.
If out-of-scope → propose defer/swap/next-PI candidate.

### 2) Portfolio/PI Planning (Claude: pi-planner) — optional for quarter-sized work
Use when the ask spans multiple epics/sprints.
Output: PI charter + objectives + backlog + roadmap + risks + capacity.
**Human Gate A:** approve PI scope/objectives/roadmap/risk posture.

### 3) Sprint Planning (Claude: sprint-planner)
Output: sprint goal + committed scope (DoR-ready only) + out-of-scope + deps/risks.
Must include Planning anchors:
- Product goal
- Scope anchor (Release/Initiative)
**Human Gate B:** approve sprint goal + committed scope.

### 4) Decomposition (Claude: epic-decomposer)
Epic → sprint-sized stories with:
- In/Out of scope,
- Acceptance Criteria,
- test strategy,
- flags: contract_impact / adr_needed / diagrams_needed,
- readiness report (ready vs blocked).

### 5) Conditional artifact “workhorses” (Claude)
Triggered by story flags:
- contract_impact=yes → **contract-owner** (contract-first pack)
- adr_needed!=none → **adr-designer** (decision log)
- diagrams_needed!=none → **diagram-steward** (minimal valuable diagrams)

Each artifact requires a quick **Human Gate** when it changes external behavior:
- contract changes must be approved before implementation.

### 6) Work package (Claude: plan-generator)
For each **DoR-ready story in committed scope**:
- produce `workpack.md` + `checklist.md` (and risks if needed).
Output is the authoritative “implementation packet” for Codex.

### 7) Codex prompts (Claude Code) — iterative generation
Prompts are generated **one at a time**, not as a bundle:

**Stage 1: PLAN prompt**
- **When:** Workpack status = Ready
- **Action:** Generate only `prompt-plan.md`
- **DO NOT generate:** prompt-apply.md

**Stage 2: APPLY prompt**
- **When:** Human shows Codex PLAN output
- **Action:** Generate `prompt-apply.md` incorporating PLAN findings (actual paths, signatures, migration versions)
- **DO NOT:** guess or invent details — use facts from Codex PLAN response

**Stage 3: Review (no prompt needed)**
- **When:** Human shows Codex APPLY output
- **Action:** Claude Code conducts review directly (run verification commands, check key files, produce GO/NO-GO)

Anti-patterns:
- ❌ Generating all prompts at once
- ❌ Guessing in APPLY without PLAN results
- ❌ Running Codex directly (Human runs Codex)
- ❌ Writing implementation code (Claude Code = prompts + review only)

PLAN prompt rules:
- NO edits, NO file writes.
- Allow only read-only commands (whitelist below).
- If required input is missing → stop and request it.

Allowed read-only commands (PLAN):
- `ls`, `find`
- `cat`
- `rg` / `grep`
- `sed -n`, `head`, `tail`
- `git status`, `git diff` (read-only inspection)

Forbidden in PLAN:
- any file modifications (edit/write/move/delete)
- any network access
- package install / system changes
- `git commit/push`, migrations, DB ops

### 8) Implementation (Codex)
- Human runs PLAN prompt in Codex (read-only)
- **Human Gate C:** approve plan, show output to Claude Code
- Human runs APPLY prompt in Codex (workspace-write)
- Human shows output to Claude Code for review

### 9) Review gate (Claude Code)
Claude Code conducts review directly:
1. Run verification commands from workpack
2. Check key files for correctness
3. Produce GO/NO-GO report:
   ```
   ## Review Result: [GO / NO-GO]
   ### Must-Fix Issues
   - [list or "None"]
   ### Should-Fix Issues
   - [list or "None"]
   ### Evidence
   - Backend tests: [PASS/FAIL]
   - Web build: [PASS/FAIL]
   - [other checks as needed]
   ### Recommendation
   [Approve for merge / Block with required fixes]
   ```
**Human Gate D:** merge / ship / rollback decision.

---

## Subagents (Claude Code)
Project subagents live in: `.claude/agents/*.md` (YAML frontmatter + prompt).

### Mandatory sequence (happy path)
1. `triage-manager` → Triage Summary (identifies flags)
2. `pi-planner` (only for PI-sized asks)
3. `epic-decomposer` → Epic + Stories (with flags per story)
4. **ARTIFACTS GATE** → Run conditional agents (see below), then Human Gate
5. `sprint-planner` → Sprint commitment (only after artifacts approved)
6. `plan-generator` → Workpacks
7. `codex-review-gate`

### Conditional agents (run at step 4, BEFORE sprint-planner)
Check epic/story flags and run applicable agents:

| Flag | Agent | Output |
|------|-------|--------|
| `contract_impact=yes` | `contract-owner` | OpenAPI/contract pack |
| `adr_needed!=none` | `adr-designer` | ADR/ADR-lite document |
| `diagrams_needed!=none` | `diagram-steward` | PlantUML/C4 diagram |

**Human Gate:** Approve artifacts before sprint planning.

**Checklist reminder:**
```
After epic-decomposer, check flags:
[ ] Any contract_impact? → contract-owner
[ ] Any adr_needed? → adr-designer
[ ] Any diagrams_needed? → diagram-steward
Then proceed to sprint-planner.
```

### Invocation rules
- Claude MUST proactively pick the right subagent when a trigger matches.
- If ambiguity exists, Claude outputs a **blocked list** and requests the minimal missing info.

---

## Planning guardrails
Все planning-артефакты должны соответствовать правилам: `.claude/rules/planning.md`.
Шаблоны: `docs/planning/_templates/`.

### Anchor non-negotiable
Every Sprint/Workpack/Gate/Review MUST include "## Sources of Truth" with:
- Product goal: `docs/planning/strategy/product-goal.md`
- Scope anchor: `docs/planning/releases/<...>.md` OR `docs/planning/initiatives/INIT-*.md`

---

## Codex handoff policy (non-negotiables)
Codex is fast but must be constrained.

### For every story prompt:
Dev prompts MUST include:
- allowed files/paths,
- forbidden paths,
- invariants (contracts/schemas/public behaviors),
- acceptance criteria summary,
- test commands + expected outcome,
- “STOP-THE-LINE” rule: if deviation needed → stop and ask.

### Plan-only enforcement (practical)
Codex planning requires reading repo sources-of-truth.
Therefore PLAN prompts must:
- forbid edits/writes,
- allow strictly whitelisted read-only commands,
- and (optionally) recommend running PLAN under read-only sandbox/approvals.

---

## Automation (optional but recommended)

### Custom slash commands
Store reusable prompts in `.claude/commands/` (project scope). 
Candidates:
- `/project:triage`
- `/project:pi_plan`
- `/project:sprint_plan`
- `/project:workpack`
- `/project:codex_prompt_plan`
- `/project:codex_prompt_apply`
- `/project:codex_prompt_review`

(Claude Code supports custom slash commands defined as Markdown in `.claude/commands/`.) 

### Hooks (guardrails)
If/when needed, enforce gates via `.claude/settings.json` hooks (PreToolUse/UserPromptSubmit etc.). 

---

## Working agreement
- Prefer small batches, keep docs close to code, avoid speculative refactors.
- ADR only when the decision is architecture-significant.
- Diagrams only when they reduce risk or improve shared understanding.
- Every merge must have a clear GO/NO-GO decision backed by artifacts.
