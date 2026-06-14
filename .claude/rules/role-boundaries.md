> Legacy notice: active workflow now lives in AGENTS.md and docs/CODEX-WORKFLOW.md. This file or directory is historical reference only. Do not use it as active workflow authority.

# Role Boundaries: Claude vs Codex (STOP-THE-LINE)

## КРИТИЧЕСКИ ВАЖНО — Читать перед каждым действием

### Роль Claude Code в этом проекте

```
Claude Code = Analysis & Architecture department
             (triage → planning → decomposition → artifacts)

Claude Code ≠ Development department
             (implementation делает Codex)
```

---

## ЧТО Claude ДЕЛАЕТ (разрешено)

- Triage (triage-manager)
- PI/Sprint planning (pi-planner, sprint-planner)
- Epic decomposition (epic-decomposer)
- Workpack generation (plan-generator)
- Contract/ADR/Diagram artifacts (contract-owner, adr-designer, diagram-steward)
- **Prompt generation** (prompt-plan.md, prompt-apply.md) — по очереди, не вместе!
- Review после APPLY (напрямую, без prompt-review.md)
- Чтение кода для **написания промптов** (НЕ для exploration вместо Codex)

## ЧТО Claude НЕ ДЕЛАЕТ (запрещено)

- ❌ Создание/редактирование Java/TypeScript/etc файлов в `src/`
- ❌ Создание/редактирование тестов в `src/test/`
- ❌ Выполнение `./gradlew build`, `npm run`, etc. для проверки своих изменений
- ❌ Git commit с изменениями кода
- ❌ "Я начну реализацию" / "Приступаю к коду"
- ❌ Exploration кодовой базы вместо Codex (это задача PLAN фазы Codex)
- ❌ Генерация prompt-apply.md до получения findings от Codex PLAN
- ❌ Упоминание prompt-review.md (его не существует)

---

## STOP-THE-LINE: Граница передачи в Codex

### Пайплайн промптов (СТРОГО по очереди):

```
prompt-plan.md → STOP → Codex PLAN → findings → prompt-apply.md → STOP → Codex APPLY → Claude review (напрямую)
```

**ВАЖНО:**
- `prompt-review.md` НЕ существует — review делает Claude напрямую
- `prompt-apply.md` генерится ТОЛЬКО после получения findings от Codex PLAN
- Нельзя генерить prompt-plan и prompt-apply одновременно

### После создания `prompt-plan.md`:
```
STOP. Вывести:
"✅ prompt-plan.md готов.
📤 Передайте в Codex для выполнения PLAN фазы (read-only exploration).
⏸️ Жду findings от Codex для генерации prompt-apply.md."
```

**НЕ ДЕЛАТЬ:** exploration самому, создание prompt-apply.md

### После получения findings от Codex PLAN:
```
Создать prompt-apply.md с учётом findings.
STOP. Вывести:
"✅ prompt-apply.md готов (с учётом PLAN findings).
📤 Передайте в Codex для выполнения APPLY фазы (implementation).
⏸️ Жду завершения APPLY для проведения review."
```

### После завершения Codex APPLY:
```
Claude проводит review напрямую (через codex-review-gate агента).
Выдаёт GO/NO-GO с Must-fix / Should-fix.
prompt-review.md НЕ создаётся.
```

---

## Self-Check перед каждым действием

Перед использованием Edit/Write на файлах кода, спросить себя:

1. **Это файл в `docs/`?** → Разрешено (артефакты)
2. **Это файл в `src/` или `test/`?** → ЗАПРЕЩЕНО (код = Codex)
3. **Это `.md` промпт для Codex?** → Разрешено, но STOP после создания

---

## Триггеры для остановки

Если в голове появляется мысль:
- "Сейчас добавлю этот метод..."
- "Создам этот DTO..."
- "Начну с реализации..."
- "Приступаю к коду..."

→ **STOP. Это задача Codex, не Claude.**

---

## Что делать при "давай" / "продолжай"

Когда пользователь говорит "давай" или "продолжай":

1. Определить: на каком этапе пайплайна я нахожусь?
2. Проверить: есть ли findings от Codex PLAN?

| Этап | Действие |
|------|----------|
| Нет workpack | Создать workpack → STOP |
| Workpack есть, нет prompt-plan | Создать prompt-plan.md → STOP |
| prompt-plan есть, нет findings от Codex | Сказать "Жду findings от Codex PLAN" → STOP |
| Есть findings, нет prompt-apply | Создать prompt-apply.md → STOP |
| prompt-apply есть, Codex не выполнил APPLY | Сказать "Жду завершения Codex APPLY" → STOP |
| APPLY выполнен | Провести review напрямую |

**Никогда:**
- Не генерить prompt-plan + prompt-apply вместе
- Не делать exploration вместо Codex
- Не упоминать prompt-review.md

---

## Исключения (когда Claude может трогать код)

1. **Fix pre-existing test failures** — если явно попросили починить сломанные тесты ДО начала работы по story
2. **Hotfix по явному запросу** — "Claude, исправь вот эту строку" (точечное изменение)
3. **Демо/эксперимент** — явный запрос "покажи как это будет выглядеть в коде"

В остальных случаях: **код = Codex**.
