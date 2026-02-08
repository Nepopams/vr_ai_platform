# Planning Guardrails (Project) — Source-of-Truth First

Цель: сделать planning-артефакты (Sprint / Workpack / Gate / Review) обсуждаемыми и исполняемыми,
без импровизаций и “ощущений”.

## STOP-THE-LINE (не обсуждается)
1) Любой документ в:
   - `docs/planning/sprints/`
   - `docs/planning/gates/`
   - `docs/planning/reviews/`
   - `docs/planning/workpacks/*/workpack.md`
   ОБЯЗАН содержать секцию **"## Sources of Truth"**.
   Если секции нет — документ считается **Draft/Needs inputs**, scope не утверждаем.

2) Нельзя заявлять “готово / реализовано / уже есть” без секции **Evidence**:
   - ссылка на файл(ы) в репо, или
   - ссылка на PR/коммит, или
   - список команд верификации (tests) + ожидаемый результат.
   Иначе — помечаем как **Assumption**.

3) Workpack “Ready” только если заполнены:
   - Files to change (пути)
   - Verification commands
   - DoD checklist
   - Risks + Rollback
   Иначе статус **Draft / Needs inputs**.

## Required sections (минимум)
### Sprint / Gate / Review
- Sources of Truth
- Goal
- Scope: Committed / Stretch / Out of scope (explicit)
- Assumptions (если есть)
- Dependencies
- Risks & mitigations
- Gate ask / Decision (что именно утверждаем)

### Workpack
- Sources of Truth
- Outcome
- Acceptance Criteria
- Files to change
- Implementation plan (commit-sized)
- Verification commands
- Tests
- DoD checklist
- Risks
- Rollback
- (опционально) Prompt Pack placeholder

## Sources of Truth — обязательный минимум
Всегда (в каждом planning doc):
- MVP: `docs/planning/mvp.md`
- Story/Epic: соответствующий файл в `docs/planning/epics/**` (или story-spec файл, если вы их выделяете)
- Governance: `docs/_governance/dor.md` и `docs/_governance/dod.md`

Условно (только если релевантно):
- Contract / OpenAPI: релевантные файлы в `docs/contracts/**` (только если `contract_impact=yes`)
- ADR: релевантные файлы в `docs/adr/**` или `docs/architecture/decisions/**` (только если `adr_needed=yes`)
- Diagrams: `docs/diagrams/**` или `docs/architecture/diagrams/**` (только если `diagrams_needed=yes`)

## Story hygiene (чтобы не ломать приоритеты)
- Сторис для “MVP closure” в первую очередь должны закрывать:
  - reproducible build / тест-прогоны / устойчивость / идемпотентность
  - clarification loop / NEEDS_INPUT цикл
  - contract governance / выходные артефакты
  UX-улучшения и ресёрч-валидации допустимы, но обычно идут в Stretch или следующую PI.

## Gate definitions (коротко)
- Gate A: Scope clarification (in/out, assumptions, deps/risks)
- Gate B: Sprint commitment (goal + committed/stretch/out-of-scope + capacity note + risks)
- Exit Review: факты + evidence + решение “закрыто/не закрыто”

## If missing inputs
Если не хватает источников истины/контекста:
- не выдумывай
- выведи список “Missing inputs” и остановись на Human Gate
