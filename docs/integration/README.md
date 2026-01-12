# Интеграция HomeTask ↔ AI Platform

Этот документ фиксирует минимальный интеграционный контракт для HomeTask и AI Platform (LangGraph).
Он описывает, как формировать запросы, как интерпретировать ответы и где проходят границы ответственности.

## Основные схемы (контракты)

- CommandDTO: `contracts/schemas/command.schema.json`
- DecisionDTO: `contracts/schemas/decision.schema.json`
- Версия контрактов: `contracts/VERSION`

## Формирование CommandDTO

Команда отправляется в виде JSON-объекта, полностью соответствующего схеме CommandDTO.
Ключевые требования:

- `command_id`: уникальный идентификатор команды (используйте для идемпотентности).
- `user_id`: пользователь-инициатор.
- `timestamp`: ISO-8601 дата/время.
- `text`: исходная пользовательская фраза.
- `capabilities`: список допустимых действий для этой команды.
- `context`: доменный контекст (см. `docs/integration/context_v1.md`).

Минимальные примеры CommandDTO находятся в `docs/integration/examples/*.json`.

## Вызов Decision API

**HTTP:** `POST /decide`

Рекомендуемые заголовки:

- `Content-Type: application/json`

Пример запроса:

```bash
curl -sS http://localhost:8000/decide \
  -H 'Content-Type: application/json' \
  -d @docs/integration/examples/create_task_start_job.json
```

## Выбор стратегии маршрутизации решений

По умолчанию используется стратегия v1 (поведение не меняется).
Чтобы включить скелет RouterV2, установите флаг окружения:

```bash
DECISION_ROUTER_STRATEGY=v2
```

## Локальный LLM runner (experimental, shadow-mode)

Платформа поддерживает локальный agent runner для оценки качества извлечения покупок.
По умолчанию функционал выключен и **не влияет** на DecisionDTO.

### Запуск runner

```bash
OPENAI_API_KEY=sk-*** \
OPENAI_MODEL=gpt-4o-mini \
OPENAI_STORE=false \
OPENAI_TIMEOUT_S=15 \
python -m agent_runner.server
```

### Конфигурация LLM provider

OpenAI (по умолчанию):

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-***
OPENAI_MODEL=gpt-4o-mini
```

Yandex AI Studio (OSS модели, OpenAI-compatible):

```bash
LLM_PROVIDER=yandex_ai_studio
LLM_API_KEY=***
LLM_PROJECT=<folder_id>
LLM_MODEL="gpt://<folder_id>/gpt-oss-120b/latest"
LLM_BASE_URL="https://llm.api.cloud.yandex.net/v1"
```

В режиме Yandex structured outputs на уровне API не гарантируются — используется
локальная валидация JSON и один retry на исправление формата.

### Включение shadow-mode в платформе

```bash
LLM_AGENT_RUNNER_URL=http://localhost:8089 \
LLM_SHOPPING_EXTRACTOR_ENABLED=true \
LLM_SHOPPING_EXTRACTOR_MODE=shadow \
DECISION_ROUTER_STRATEGY=v2 \
make run_graph
```

### Пример запроса к runner

```bash
curl -sS http://localhost:8089/a2a/v1/invoke \
  -H 'Content-Type: application/json' \
  -d '{
    "a2a_version": "a2a.v1",
    "message_id": "msg-1",
    "trace_id": "trace-1",
    "agent_id": "shopping-list-llm-extractor",
    "intent": "add_shopping_item",
    "input": {"text": "Купи молоко и хлеб", "context": {}},
    "constraints": {}
  }'
```

### Пример curl для Yandex Chat Completions

```bash
curl -sS https://llm.api.cloud.yandex.net/v1/chat/completions \
  -H "Authorization: Bearer ${LLM_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Project: ${LLM_PROJECT}" \
  -d '{
    "model": "gpt://<folder_id>/gpt-oss-120b/latest",
    "messages": [
      {"role": "system", "content": "Верни только JSON."},
      {"role": "user", "content": "Купи молоко"}
    ],
    "temperature": 0.1,
    "max_tokens": 200
  }'
```

## Интерпретация DecisionDTO

Ответ DecisionDTO всегда содержит `action` и `payload`, соответствующие схеме.
Важно различать:

### `start_job`

`action = "start_job"` означает, что AI Platform предлагает начать выполнение задания.
В `payload` содержатся:

- `job_id`: идентификатор задания.
- `job_type`: тип задания (`create_task`, `add_shopping_item`, `unknown`).
- `proposed_actions` (опционально): предложения по деталям (см. ниже).
- `ui_message` (опционально): текст для UI.

### `clarify`

`action = "clarify"` означает, что для продолжения нужны уточнения.
В `payload` содержатся:

- `question`: вопрос пользователю.
- `options` (опционально): варианты ответа.
- `missing_fields` (опционально): перечень недостающих полей.
- `job_id` (опционально): идентификатор контекста задания.

## Работа с `proposed_actions`

`proposed_actions` — это **предложение**, а не команда к выполнению.
HomeTask может:

- принять предложение и отобразить/выполнить;
- частично применить;
- проигнорировать и запросить уточнение.

AI Platform **не выполняет** эти действия сама — ответственность за исполнение лежит на HomeTask.

## Идемпотентность и ретраи (ответственность HomeTask)

- Используйте стабильный `command_id` для повторных отправок одной и той же команды.
- При сетевых ошибках допустимы ретраи с тем же `command_id`.
- Нельзя менять `command_id` при повторной отправке одной и той же команды.
- Ответственность за дедупликацию и безопасные ретраи полностью на стороне HomeTask.

## AI Platform НЕ гарантирует

- выполнение действий: платформа лишь возвращает решение;
- отсутствие `clarify` даже при схожих командах;
- неизменяемость `job_type` при повторной интерпретации разных команд;
- пригодность решения без учета актуальности вашего `context`;
- корректность при нарушении схемы запроса или при пустом/неконсистентном контексте.

## Связанные документы

- Контекст: `docs/integration/context_v1.md`
- Примеры: `docs/integration/examples/*.json`
