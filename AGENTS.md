# AGENTS.md

## Base Rules

- Всегда отвечай на русском. Код, имена API, схем и команд остаются на языке исходных файлов.
- Работай только с файлами текущего репозитория, если пользователь явно не разрешил внешний источник.
- Не выводи домен из названия репозитория. Назначение платформы бери из `docs/planning/strategy/product-goal.md`, ADR и контрактов.
- Не меняй runtime-код, `contracts/**`, schemas, public API, тестовые фикстуры и существующие `.codex/skills/**` без утвержденного workpack и human gate.
- Для Python используй `python3`, `.venv/bin/python3`, `.venv/bin/pytest` или `python3 -m pytest`. Команды с `python` запрещены.

## Active Workflow Authority

1. `AGENTS.md` - главный краткий instruction-файл для Codex.
2. `CODEX.md` - короткий операционный вход в Codex-only workflow.
3. `docs/CODEX-WORKFLOW.md` - подробная operating model.
4. `.agents/skills/**/SKILL.md` - reusable workflow instructions.
5. `.codex/agents/**` - read-only review agents.
6. `.codex/skills/**` - project-specific deterministic / implementation-oriented skills, сохраняются как есть.

`CLAUDE.md` и `.claude/**` являются legacy reference only и не являются active workflow authority.

## Sources of Truth

| Artifact | Canonical path |
| --- | --- |
| Product goal | `docs/planning/strategy/product-goal.md` |
| Roadmap | `docs/planning/strategy/roadmap.md` |
| MVP scope | `docs/planning/releases/MVP.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |
| ADR archive | `docs/adr/` |
| ADR index | `docs/_indexes/adr-index.md` |
| Contract schemas | `contracts/schemas/` |
| Contract version | `contracts/VERSION` |
| Contract governance | `docs/contracts/CONTRACT-GOVERNANCE-RUNBOOK.md` |
| Diagrams index | `docs/_indexes/diagrams-index.md` |
| Planning templates | `docs/planning/_templates/` |
| Workpacks | `docs/planning/workpacks/<STORY_ID>/` |

## Architectural Invariants

- AI Platform is a stateless, contract-driven decision engine that returns `DecisionDTO`.
- `graphs/core_graph.py` orchestrates the graph pipeline; deterministic behavior is the baseline.
- LLM, assist, shadow, partial trust, and agent-hints may enhance decisions only within ADR-approved guardrails and feature flags.
- All inputs and outputs must conform to `contracts/schemas/`.
- Contract changes follow ADR-001 semver and require fixture/test updates.
- New intents, actions, externally visible fields, model policy changes, runtime agent behavior, or public API changes require artifact gate before APPLY.
- No raw user text or raw LLM output in logs, reports, review notes, or generated artifacts.

## Codex-Only Delivery Pipeline

Active delivery flow:

`intake -> planning -> artifact gate -> workpack -> Codex PLAN -> Human Gate C -> Codex APPLY -> read-only review gate -> Human Gate D`

- Intake and planning collect goal, constraints, sources of truth, scope anchor, risks, and readiness.
- Artifact gate decides whether contracts, ADR, diagrams, model policy, public API, or planning anchors must change before implementation.
- Workpack is the implementation authority for APPLY: files, boundaries, acceptance criteria, commands, rollback.
- Human Gate C is mandatory between PLAN and APPLY.
- Human Gate D is mandatory after the read-only review gate before merge, ship, or rollback.

## PLAN / APPLY / REVIEW

### Codex PLAN

- Read-only only: inspect files, schemas, tests, logs, and git state.
- No edits, no file writes, no package installs, no network, no commits, no migrations, no runtime mutation.
- Output exact findings: affected files, risks, missing inputs, proposed implementation steps, validation commands.
- If sources conflict or required inputs are missing, stop and report the blocked list.

### Codex APPLY

- Allowed only after Human Gate C.
- Follow the approved workpack and PLAN findings.
- Touch only allowed paths. Do not broaden scope opportunistically.
- Stop before changing contracts, schemas, public API, ADR-significant architecture, or diagrams unless artifact gate already approved it.
- Preserve existing `.codex/skills/**` unless the workpack explicitly authorizes a skill change.

### Read-Only REVIEW

- Review agents and review passes are read-only.
- No production code writes, no document mutation, no parallel document mutation, no APPLY, no human gate bypass.
- Output must be GO/NO-GO with Must-fix, Should-fix, Evidence, and Recommendation.

## Change Management

- Changes to `contracts/`, `graphs/`, `agents/`, `agent_registry/`, `agent_runner/`, `llm_policy/`, `routers/`, `app/`, or public API require explicit source-of-truth references and relevant checks.
- Contract changes require ADR-001 classification, semver decision, fixtures, schema validation, graph sanity, and changelog entry.
- ADR or diagram drift must be resolved before implementation if the work changes architecture, flow, boundaries, or external behavior.
- If a requested change conflicts with an accepted ADR, stop and create or request a Draft ADR instead of pushing implementation.

## Local Commands

```bash
python3 -m pytest tests/ -v
make validate_contracts
make run_graph
make run_graph_suite
make audit_decisions
make release-sanity
```

`make release-sanity` is offline-friendly and may skip API sanity when optional API dependencies are unavailable. Full API sanity uses `RUN_API_SANITY=1 make release-sanity`.

## Worktree Safety

- Read current git status before broad edits.
- Never revert or delete user changes unless the user explicitly asks.
- Ignore unrelated dirty files. If they affect the task, work with them and explain the constraint.
- Prefer `rg` / `rg --files` for discovery.
- Use focused patches and avoid unrelated refactors.

## Output Expectations

- Explain decisions, summaries, validation, risks, and follow-up in Russian.
- Reference local files with exact paths when useful.
- For delivery work, final reports should include Summary, Files changed, Active workflow authority, Legacy status, Validation, Risks / Follow-up.
