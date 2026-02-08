# WP-000: Bootstrap Pipeline Readiness

**Status:** Ready
**Type:** Infrastructure / Governance
**Priority:** Critical (блокирует все остальные WP)
**Owner:** Codex (implementation) / Claude (prompts + review)

---

## Sources of Truth

| Артефакт | Путь |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Roadmap | `docs/planning/strategy/roadmap.md` |
| Release scope (MVP) | `docs/planning/releases/MVP.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |
| ADR-000 (core arch) | `docs/adr/ADR-000-ai-platform-intent-decision-engine.md` |
| ADR-001 (contract versioning) | `docs/adr/ADR-001-contract-versioning-compatibility-policy.md` |
| ADR-003 (LLM policy) | `docs/adr/ADR-003-llm-model-policy-registry-and-escalation.md` |
| Readiness Audit | Conversation artifact (2026-02-08) |

---

## Outcome

Репозиторий полностью готов к управляемой разработке через пайплайн Claude (planning/arch) + Codex (implementation):
- CI автоматически валидирует контракты и тесты на каждый push/PR
- Dev environment воспроизводим за одну команду
- Golden dataset достаточен для измерения intent match rate
- Planning templates позволяют создавать epics/stories/workpacks единообразно
- Индексы и ADR в консистентном состоянии

---

## Acceptance Criteria

1. **CI зелёный на main:** `python -m pytest tests/ -v` + `python -m skills.contract_checker` + `python -m skills.schema_bump check` + `python -m skills.graph_sanity` проходят в GitHub Actions
2. **Dev setup за 1 команду:** `make setup-dev && make test` работает на чистом клоне (Python 3.11+)
3. **Golden dataset >= 12 fixtures:** Покрыты все intents (`add_shopping_item`, `create_task`, `clarify_needed`) + edge cases (пустой text, unknown intent, minimal context)
4. **Planning templates существуют:** 4 шаблона в `docs/planning/_templates/` (epic, story, workpack, sprint)
5. **Initiatives index:** `docs/_indexes/initiatives-index.md` ссылается на все 8 инициатив
6. **Shared test fixtures:** `tests/conftest.py` с базовыми pytest fixtures
7. **ADR cleanup:** Дубликат ADR-005 удалён, ADR index для AI Platform ADRs (000-005) добавлен в `docs/_indexes/adr-index.md`

---

## Files to Change

### New files (create)

| Файл | Описание |
|------|----------|
| `.github/workflows/ci.yml` | CI pipeline: pytest + contract validation + schema bump + graph sanity |
| `docs/planning/_templates/epic.md` | Шаблон epic charter |
| `docs/planning/_templates/story.md` | Шаблон story spec |
| `docs/planning/_templates/workpack.md` | Шаблон workpack |
| `docs/planning/_templates/sprint.md` | Шаблон sprint plan |
| `docs/_indexes/initiatives-index.md` | Индекс всех инициатив |
| `tests/conftest.py` | Shared pytest fixtures |
| `skills/graph-sanity/fixtures/commands/buy_milk.json` | Fixture: simple shopping, single item |
| `skills/graph-sanity/fixtures/commands/buy_bread_and_eggs.json` | Fixture: shopping, multi-item text |
| `skills/graph-sanity/fixtures/commands/clean_bathroom.json` | Fixture: task, explicit zone |
| `skills/graph-sanity/fixtures/commands/fix_faucet.json` | Fixture: task, repair type |
| `skills/graph-sanity/fixtures/commands/empty_text.json` | Fixture: edge case, empty/whitespace text |
| `skills/graph-sanity/fixtures/commands/unknown_intent.json` | Fixture: edge case, ambiguous command |
| `skills/graph-sanity/fixtures/commands/minimal_context.json` | Fixture: edge case, minimal household |
| `skills/graph-sanity/fixtures/commands/shopping_no_list.json` | Fixture: shopping, no shopping_lists in context |
| `skills/graph-sanity/fixtures/commands/task_no_zones.json` | Fixture: task, no zones in context |
| `skills/graph-sanity/fixtures/commands/buy_apples_en.json` | Fixture: shopping, English text |
| `skills/graph-sanity/fixtures/commands/multiple_tasks.json` | Fixture: complex, multi-intent text |

### Modified files (update)

| Файл | Изменение |
|------|-----------|
| `Makefile` | Добавить target `setup-dev` |
| `README.md` | Обновить Quick Start секцию (setup-dev + test) |
| `docs/_indexes/adr-index.md` | Добавить AI Platform ADRs (000-005) в таблицу |

### Deleted files

| Файл | Причина |
|------|---------|
| `docs/adr/ADR-005: Внутренний контракт агента v0 как ABI платформы.md` | Дубликат `ADR-005-internal-agent-contract-v0.md` |

---

## Implementation Plan (commit-sized steps)

### Step 1: Dev environment reproducibility

**Commit:** "chore: add setup-dev target and update Quick Start"

1. Добавить в `Makefile`:
   ```makefile
   setup-dev:
   	pip install -e ".[dev]"
   ```
2. Обновить `README.md` Quick Start:
   ```markdown
   ## Quick Start
   Python 3.11+ is required.
   ```bash
   make setup-dev   # install with dev dependencies
   make test        # run full test suite
   make test-core   # run minimal suite (no API deps)
   ```
   ```

**Verify:** `make setup-dev && make test-core` на чистом venv

---

### Step 2: CI pipeline

**Commit:** "ci: add GitHub Actions workflow for tests and contract validation"

Создать `.github/workflows/ci.yml`:
```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e ".[dev]"
      - name: Run tests
        run: python -m pytest tests/ -v --tb=short
      - name: Validate contracts
        run: python -m skills.contract_checker
      - name: Check schema version
        run: python -m skills.schema_bump check
      - name: Graph sanity
        run: python -m skills.graph_sanity
```

**Verify:** Push → Actions tab → green check

---

### Step 3: Golden dataset expansion

**Commit:** "test: expand golden dataset to 12+ fixtures covering all intents"

Добавить 12 новых fixture файлов в `skills/graph-sanity/fixtures/commands/`:

| Файл | Intent | Описание |
|------|--------|----------|
| `buy_milk.json` | add_shopping_item | "Купи молоко", one item, default list |
| `buy_bread_and_eggs.json` | add_shopping_item | "Купить хлеб и яйца", multi-item |
| `clean_bathroom.json` | create_task | "Убери ванную", explicit zone |
| `fix_faucet.json` | create_task | "Починить кран на кухне", repair |
| `empty_text.json` | clarify_needed | text = " ", edge case |
| `unknown_intent.json` | clarify_needed | "Что-то непонятное", ambiguous |
| `minimal_context.json` | clarify_needed | minimal household, no zones/lists |
| `shopping_no_list.json` | add_shopping_item | no shopping_lists in context |
| `task_no_zones.json` | create_task | no zones in context |
| `buy_apples_en.json` | add_shopping_item | "Buy apples", English text |
| `multiple_tasks.json` | clarify_needed | "Купи молоко и убери кухню", multi-intent |

Каждый fixture следует формату `command.schema.json` (поля: command_id, user_id, timestamp, text, capabilities, context).

**Verify:** `python -m skills.graph_sanity` — зелёный с новыми fixtures

---

### Step 4: Shared test fixtures (conftest.py)

**Commit:** "test: add shared pytest fixtures in conftest.py"

Создать `tests/conftest.py` с fixtures:
- `valid_command()` — минимальный валидный CommandDTO
- `valid_command_shopping()` — CommandDTO с text="Купи молоко"
- `valid_command_task()` — CommandDTO с text="Убери кухню"
- `household_context()` — полный context с members, zones, shopping_lists
- `minimal_context()` — минимальный context (только members)
- `command_schema()` — загруженная JSON schema из `contracts/schemas/command.schema.json`
- `decision_schema()` — загруженная JSON schema из `contracts/schemas/decision.schema.json`

**Verify:** `python -m pytest tests/test_contracts.py -v` — зелёный, fixtures импортируются

---

### Step 5: Planning templates

**Commit:** "docs: add planning templates for epic, story, workpack, sprint"

Создать 4 файла в `docs/planning/_templates/`:

**epic.md** — секции: Sources of Truth, Context, Goal, Scope (in/out), Stories (table), Dependencies, Risks, Flags (contract_impact, adr_needed, diagrams_needed)

**story.md** — секции: Sources of Truth, Description, Acceptance Criteria (Given/When/Then), Scope (in/out), Test Strategy (unit/integration), Flags, Blocked By

**workpack.md** — секции: Sources of Truth, Outcome, Acceptance Criteria, Files to Change (new/modified/deleted), Implementation Plan (commit-sized), Verification Commands, Tests, DoD Checklist, Risks, Rollback

**sprint.md** — секции: Sources of Truth, Sprint Goal, Committed Scope (table), Stretch, Out of Scope, Capacity Notes, Dependencies, Risks & Mitigations, Gate Ask

**Verify:** Файлы существуют и содержат все обязательные секции из `docs/_governance/dor.md` и `.claude/rules/planning.md`

---

### Step 6: Indexes and ADR cleanup

**Commit:** "docs: add initiatives index, update ADR index, remove ADR-005 duplicate"

1. Создать `docs/_indexes/initiatives-index.md`:
   - Таблица: ID, Title, Priority, Period, Status, Link
   - 8 инициатив из `docs/planning/initiatives/`

2. Обновить `docs/_indexes/adr-index.md`:
   - Добавить AI Platform ADRs (000-005) в таблицу
   - Ссылки на `docs/adr/ADR-0XX-*.md`

3. Удалить `docs/adr/ADR-005: Внутренний контракт агента v0 как ABI платформы.md` (дубликат)

**Verify:**
- Все ссылки в indexes валидны (файлы существуют)
- `ls docs/adr/ADR-005*` возвращает ровно 1 файл

---

## Verification Commands

```bash
# 1. Dev setup (from clean clone)
make setup-dev

# 2. Full test suite
python -m pytest tests/ -v --tb=short

# 3. Core tests (no API deps)
python -m pytest tests/test_contracts.py tests/test_graph_execution.py tests/test_skill_checks.py -v

# 4. Contract validation
python -m skills.contract_checker

# 5. Schema version check
python -m skills.schema_bump check

# 6. Graph sanity with expanded fixtures
python -m skills.graph_sanity

# 7. Release sanity (offline mode)
python -m skills.release_sanity

# 8. Fixture count check
ls skills/graph-sanity/fixtures/commands/*.json | wc -l
# Expected: >= 14 (2 existing + 12 new)

# 9. Template check
ls docs/planning/_templates/*.md | wc -l
# Expected: 4

# 10. ADR-005 duplicate check
ls docs/adr/ADR-005* | wc -l
# Expected: 1
```

---

## Tests

| Тест | Что проверяет | Ожидание |
|------|---------------|----------|
| `python -m pytest tests/ -v` | Все тесты проходят | 0 failures |
| `python -m skills.contract_checker` | Контракты валидны | exit 0 |
| `python -m skills.schema_bump check` | VERSION = 2.0.0, не нужен bump | exit 0 |
| `python -m skills.graph_sanity` | Все fixtures проходят через graph | exit 0 |
| Fixture count >= 14 | Golden dataset расширен | `ls ... | wc -l` >= 14 |
| Templates count = 4 | Все templates созданы | `ls ... | wc -l` = 4 |
| conftest.py importable | Fixtures работают | `python -c "import tests.conftest"` |
| CI workflow valid | YAML корректен | `actionlint .github/workflows/ci.yml` (опционально) |

---

## DoD Checklist

- [ ] `make setup-dev && make test` работает на чистом клоне с Python 3.11+
- [ ] CI workflow зелёный на main (pytest + contract_checker + schema_bump + graph_sanity)
- [ ] Golden dataset >= 14 fixtures (2 existing + 12 new)
- [ ] Все fixtures валидны по `command.schema.json`
- [ ] `tests/conftest.py` содержит shared fixtures
- [ ] `docs/planning/_templates/` содержит 4 шаблона (epic, story, workpack, sprint)
- [ ] `docs/_indexes/initiatives-index.md` ссылается на 8 инициатив
- [ ] `docs/_indexes/adr-index.md` содержит AI Platform ADRs (000-005)
- [ ] Дубликат ADR-005 удалён (1 файл, не 2)
- [ ] README.md обновлён (Quick Start с setup-dev)
- [ ] Makefile содержит target `setup-dev`
- [ ] Ни один существующий тест не сломан
- [ ] Контракты (`contracts/schemas/`) НЕ изменены
- [ ] `contracts/VERSION` = `2.0.0` (не тронут)

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| pytest зависимости не собираются в CI | Low | High | `pip install -e ".[dev]"` + pinned Python 3.11 |
| Новые fixtures ломают graph_sanity | Low | Medium | Каждый fixture = valid CommandDTO по schema; `detect_intent` детерминистичен |
| GitHub Actions недоступен (self-hosted) | Medium | Medium | Makefile targets работают локально как fallback |
| conftest.py конфликтует с existing тестами | Low | Medium | conftest.py добавляет НОВЫЕ fixtures, не переопределяет existing |
| ADR-005 deletion ломает ссылки | Low | Low | Grep по репо перед удалением; canonical = `ADR-005-internal-agent-contract-v0.md` |

---

## Rollback

- **CI:** Удалить `.github/workflows/ci.yml` (1 файл)
- **Fixtures:** Удалить новые JSON files из `skills/graph-sanity/fixtures/commands/`
- **conftest.py:** Удалить `tests/conftest.py`
- **Templates:** Удалить `docs/planning/_templates/`
- **Indexes:** Revert `docs/_indexes/adr-index.md` и удалить `docs/_indexes/initiatives-index.md`
- **Makefile/README:** Revert changes

Все изменения обратимы через `git revert` одного merge commit.

---

## APPLY Boundaries

### Allowed (Codex может трогать)

- `.github/workflows/ci.yml`
- `Makefile`
- `README.md`
- `tests/conftest.py`
- `docs/planning/_templates/*.md`
- `docs/_indexes/initiatives-index.md`
- `docs/_indexes/adr-index.md`
- `skills/graph-sanity/fixtures/commands/*.json` (только новые файлы)

### Forbidden (Codex НЕ трогает)

- `contracts/schemas/*.json` — публичные контракты
- `contracts/VERSION` — версия контрактов
- `routers/**` — routing logic
- `graphs/**` — core graph
- `app/**` — FastAPI app
- `llm_policy/**` — LLM policy config и runtime
- `agent_registry/**` — agent platform
- `agent_runner/**` — agent runner
- `docs/adr/ADR-0*.md` — ADR содержание (кроме удаления дубликата)
- `docs/planning/initiatives/**` — инициативы
- `docs/planning/releases/**` — release scopes
- `docs/planning/strategy/**` — strategy docs

### Invariants (НЕ нарушать)

- Все existing тесты проходят (`python -m pytest tests/ -v`)
- `contracts/VERSION` = `2.0.0`
- Command и Decision schemas не изменены
- `DECISION_ROUTER_STRATEGY` default = `v1`
- Все feature flags disabled by default
