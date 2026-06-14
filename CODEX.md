# CODEX.md

## Назначение

`CODEX.md` - короткий вход в активный Codex-only delivery workflow этого репозитория.

Главный machine-readable instruction-файл остается `AGENTS.md`. Подробная operating model живет в `docs/CODEX-WORKFLOW.md`.

## Active Workflow Authority

1. `AGENTS.md` - обязательные правила для Codex.
2. `CODEX.md` - короткий операционный вход и маршрут работы.
3. `docs/CODEX-WORKFLOW.md` - полное описание workflow, gates, skills и review gate.
4. `.agents/skills/**/SKILL.md` - reusable workflow instructions.
5. `.codex/agents/**` - read-only review agents.
6. `.codex/skills/**` - существующие project-specific deterministic / implementation-oriented skills.

`CLAUDE.md` и `.claude/**` являются legacy reference only.

## Рабочая Модель

Активная цепочка:

`intake -> planning -> artifact gate -> workpack -> Codex PLAN -> Human Gate C -> Codex APPLY -> read-only review gate -> Human Gate D`

## Как Работать

1. Начинай с `AGENTS.md` и этого файла.
2. Для деталей workflow открывай `docs/CODEX-WORKFLOW.md`.
3. Для intake/planning/workpack/review используй `.agents/skills/**`.
4. Для review используй только read-only `.codex/agents/**`.
5. Для deterministic проверок используй существующие `.codex/skills/**` и project scripts.

## Нельзя Обходить

- Нельзя переходить от PLAN к APPLY без Human Gate C.
- Нельзя завершать delivery без read-only review gate и Human Gate D.
- Нельзя менять `contracts/**`, schemas, public API, runtime behavior, ADR-significant architecture или diagrams без artifact gate.
- Нельзя редактировать production code в review gate.
- Нельзя переносить, удалять или переписывать существующие `.codex/skills/**` без отдельного workpack.

## Быстрые Команды

```bash
python3 -m pytest tests/ -v
make validate_contracts
make run_graph
make run_graph_suite
make audit_decisions
make release-sanity
```

## Legacy

Legacy Claude pipeline сохранен только как historical reference:

- `CLAUDE.md`
- `.claude/**`

Если legacy-файл противоречит `AGENTS.md`, `CODEX.md` или `docs/CODEX-WORKFLOW.md`, активными считаются Codex-only файлы.
