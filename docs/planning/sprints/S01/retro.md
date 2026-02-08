# Sprint S01 -- Retrospective

**Date:** 2026-02-08
**Facilitator:** Claude (Arch/BA)
**Attendees:** Human (PO), Claude (Arch/BA), Codex (Dev)

---

## Sprint Summary

| Metric | Value |
|--------|-------|
| Sprint Goal | Close NOW-phase gaps for Shadow Router and Assist-Mode initiatives |
| Stories committed | 4 |
| Stories completed | 4/4 |
| Stories carried over | 0 |
| Sprint Goal met? | **Yes** |

Обе инициативы NOW-фазы закрыты:
- INIT-2026Q1-shadow-router → Done
- INIT-2026Q1-assist-mode → Done

---

## What Went Well

- **Пайплайн работает end-to-end.** Все 4 истории прошли полный цикл: workpack → prompt-plan → Codex PLAN → prompt-apply → Codex APPLY → Claude review → merge. Ни одна не застряла.
- **STOP-THE-LINE сработал корректно.** ST-003: Codex PLAN обнаружил, что предполагаемые файлы (`normalization.py`, `entity_extraction.py`, etc.) не существуют — вся логика в `runner.py`. Пайплайн поймал ошибку до имплементации, promptы были исправлены и PLAN перезапущен.
- **Codex выдаёт quality output с первой попытки.** Все 4 APPLY прошли review без must-fix замечаний. Ни одного NO-GO.
- **Тесты стабильны.** 109/109 passed на протяжении всего спринта. Ни одной регрессии.
- **Быстрая скорость доставки.** Весь спринт (4 stories + housekeeping) завершён за одну сессию вместо запланированных 3-4 дней.

---

## What Did Not Go Well

- **Codex не может запустить pytest в sandbox.** Нет `.venv`, нет `pytest` — верификация всегда откладывается на фазу Claude review. Это удлиняет цикл и создаёт риск: Codex может сгенерировать код, который не компилируется/не проходит тесты, и мы узнаем это только на review.
- **`python` vs `python3`.** Codex пытался использовать `python` (не существует в среде). Исправлено добавлением Environment секции в AGENTS.md, но потребовало отдельного housekeeping коммита.
- **AGENTS.md содержал устаревшие ссылки.** Ссылался на `docs/mvp/AI_PLATFORM_MVP_v1.md` и `docs/diagrams/README.md` вместо pipeline-путей. Мог дезориентировать Codex. Исправлено полной перезаписью.
- **CODEX.md дублировал AGENTS.md.** Был строгим подмножеством — двойная загрузка контекста в Codex без пользы. Удалён.
- **ST-003 workpack содержал неверные пути к файлам.** Предположил раздельные файлы (`normalization.py`, `entity_extraction.py`, `clarify.py`, `agent_hints.py`), а на деле всё в одном `runner.py` (24KB). Потребовался повторный PLAN.
- **git push не прошёл.** Вероятно, требуется ручная аутентификация. 9 коммитов остаются непушенными.

---

## Action Items

| Action | Owner | Due |
|--------|-------|-----|
| Запушить 9 коммитов в origin/main | Human | Немедленно |
| Решить проблему pytest в Codex sandbox (sandbox config или post-APPLY hook) | Human + Claude | До S02 |
| Добавить в workpack-шаблон чеклист "проверить актуальность путей к файлам" | Claude | S02 planning |
| Обновить sprint.md статус на Done | Claude | Сейчас |

---

## Pipeline Observations

### Claude (Arch/BA) effectiveness
- **Workpack quality:** Хорошая для doc-only stories (ST-002, ST-003, ST-004). Для ST-001 (code) workpack создан в предыдущей сессии — тоже без проблем. Одна ошибка: ST-003 workpack содержал неверные пути.
- **Prompt quality (plan/apply):** prompt-plan стабильно полезен — все Codex PLAN дали нужные findings. prompt-apply с точным содержимым файлов — Codex воспроизводит 1:1.
- **Review thoroughness:** Все 4 review запускали полный тест-сьют + целевые тесты + grep на privacy. GO с первой попытки.
- **Bottlenecks:** Claude не может проверить код до Codex APPLY — зависимость от Human gate для запуска Codex.

### Codex (Dev) effectiveness
- **PLAN phase accuracy:** 3 из 4 — отличная. ST-003 (первый запуск) — STOP-THE-LINE по путям, что правильное поведение. После коррекции — 4/4.
- **APPLY phase quality:** 4/4 — все review GO без must-fix.
- **Deviation from workpack:** Нулевое отклонение. Codex строго следовал prompt-apply.
- **Bottlenecks:** Невозможность запуска тестов в sandbox. Все verification commands игнорируются (Codex сообщает "нет python").

### Human (PO) gate flow
- **Gate turnaround time:** Быстрый — все gates пройдены в одной сессии.
- **Blocking issues:** Нет блокеров со стороны PO.
- **Communication clarity:** Хорошая. PO вовремя сообщил о проблеме с python/AGENTS.md.

---

## Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| Stories completed | 4 | **4** |
| Tests passing | All (109) | **109/109** |
| DoD compliance | 100% | **100%** (docs-only stories; ST-001 code + tests) |
| Gate interactions per story | ~2 | **~3** (PLAN gate + APPLY gate + review) |
| Codex APPLY attempts | 4 | **5** (ST-003 потребовал повторный PLAN) |
| Must-fix issues on review | 0 | **0** |
| Initiatives closed | 2 | **2** (shadow-router + assist-mode) |

---

## Carry-Forward Items

- **git push** — 9 коммитов не запушены, требуется ручная аутентификация
- **Codex pytest в sandbox** — системная проблема, нужно решение до S02

---

## Next Sprint Candidates

Переход к NEXT-фазе (2026Q2) согласно roadmap:

| Инициатива | Приоритет | Комментарий |
|------------|-----------|-------------|
| INIT-2026Q2-partial-trust | Средний | Partial Trust для add_shopping_item (sampling 0.01→0.1) |
| INIT-2026Q2-multi-entity-extraction | Средний | Списки покупок, количества, атрибуты |
| INIT-2026Q2-improved-clarify | Средний | missing_fields, LLM-assist для вопросов |

Рекомендация: начать с **partial-trust** (наименьший scope, измеримый результат, базируется на уже закрытом shadow-router).
