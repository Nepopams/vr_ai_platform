# Диаграммы

## Реестр PlantUML

| Файл | Тип | Назначение |
| --- | --- | --- |
| `1.puml` | другое (плейсхолдер) | Пустой файл, не содержит диаграммы. |
| `docs/plantuml/c4-lvl1.puml` | C4 L1 (System Context) | Контекст системы: User, клиент HomeTask, продуктовый backend и AI Platform. |
| `docs/plantuml/c4-lvl2.puml` | C4 L2 (Containers) | Контейнеры HomeTask Product и AI Platform, их взаимодействия и интерфейсы. |
| `docs/plantuml/c4-lvl3.puml` | C4 L3 (Components) | Компоненты Decision API и MVP-graph (nodes/runner/validator/trace). |
| `docs/plantuml/seq.puml` | Sequence | Сценарии MVP v1: happy path, clarify, запуск job. |

## Правила синхронизации

- Изменения **границ систем/контейнеров**, **контрактов** или **sequence** должны синхронно отражаться в коде **и** диаграммах.
- Если синхронизация невозможна сразу, изменение должно быть зафиксировано через соответствующий ADR, а диаграммы должны ссылаться на него при следующем обновлении.

## Рендеринг PlantUML

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

## Makefile

В текущем `Makefile` нет цели `diagrams`. Рекомендуется добавить `make diagrams`, который будет рендерить `docs/plantuml/*.puml`.
