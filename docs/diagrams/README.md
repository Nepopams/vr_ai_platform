# Диаграммы

## Реестр PlantUML

| Файл | Тип | Назначение |
| --- | --- | --- |
| `docs/plantuml/c4-lvl1.puml` | C4 L1 (System Context) | Контекст системы: User, клиент HomeTask, продуктовый backend и AI Platform. |
| `docs/plantuml/c4-lvl2.puml` | C4 L2 (Containers) | Контейнеры HomeTask Product и AI Platform, их взаимодействия и интерфейсы. |
| `docs/plantuml/c4-lvl3.puml` | C4 L3 (Components) | Компоненты Decision API и MVP-graph (nodes/runner/validator/trace). |
| `docs/plantuml/seq.puml` | Sequence | Сценарии MVP v1: happy path, clarify, запуск job. |

## Правила синхронизации

- Изменения **contracts/**, **graphs/**, **agents/**, **api/** или жизненного цикла
  `start_job/clarify` должны синхронно отражаться в коде **и** диаграммах.
- Если синхронизация невозможна сразу, зафиксируйте изменение через ADR (Draft) и
  обновите диаграммы при ближайшем релевантном изменении.
- Любые изменения вне MVP v1 допускаются только после обновления MVP (v2) и,
  при необходимости, новых ADR.

## Рендеринг PlantUML

### Вариант 0: Makefile

```bash
make diagrams
```

### Вариант 1: plantuml.jar

1. Скачайте `plantuml.jar` (например, с https://plantuml.com/download).
2. Сгенерируйте изображения:
   ```bash
   java -jar plantuml.jar -tpng docs/plantuml/*.puml
   ```

### Вариант 2: Docker

```bash
docker run --rm -v "$PWD":/workspace -w /workspace plantuml/plantuml -tpng docs/plantuml/*.puml
```
