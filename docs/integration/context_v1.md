# Context v1 (HomeTask → AI Platform)

Документ описывает требования к полю `context` внутри CommandDTO.
Полный формат CommandDTO задан схемой: `contracts/schemas/command.schema.json`.

## Обязательные поля (минимум для интеграции v1)

В рамках интеграции v1 HomeTask всегда передаёт следующие поля:

- `household`
- `household.members`
- `household.zones`
- `defaults`

> Примечание: схема допускает часть из этих полей как опциональные, но
> интеграционный контракт v1 требует их присутствия для стабильной интерпретации.

## Опциональные поля

Поля, которые можно передавать при наличии данных:

- `household.household_id`
- `household.shopping_lists`
- `defaults.default_assignee_id`
- `defaults.default_list_id`
- `policies.quiet_hours`
- `policies.max_open_tasks_per_user`

## Требования к консистентности данных

- `household.members` должен содержать минимум одного участника.
- Идентификаторы (`user_id`, `zone_id`, `list_id`) должны быть стабильными и
  согласованными между собой.
- `defaults.default_assignee_id`, если указан, должен ссылаться на существующего участника.
- `defaults.default_list_id`, если указан, должен ссылаться на существующий список покупок.

## Лимиты размера и частоты

Рекомендуемые пределы для интеграции v1 (договорные ограничения):

- `household.members`: до 50 участников.
- `household.zones`: до 100 зон.
- `household.shopping_lists`: до 50 списков.
- Частота вызовов `/decide`: не чаще 5 RPS на домохозяйство.

При превышении лимитов качество решения может деградировать.

## Игнорируемые поля (future-proofing)

AI Platform интерпретирует только поля, описанные в схемах.
Любые дополнительные ключи в `context`:

- не используются в логике решения;
- могут быть отклонены строгой валидацией (из-за `additionalProperties: false`).

Рекомендуется не отправлять лишние поля.

## Минимальный пример `context`

```json
{
  "household": {
    "members": [
      {
        "user_id": "user_1",
        "display_name": "Анна",
        "role": "owner",
        "workload_score": 0.4
      }
    ],
    "zones": [
      {
        "zone_id": "zone_kitchen",
        "name": "Кухня"
      }
    ]
  },
  "defaults": {
    "default_assignee_id": "user_1",
    "default_list_id": "list_main"
  }
}
```
