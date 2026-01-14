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

## LLM Model Policy (ADR-003)

- Это внутренний механизм платформы, не часть внешних контрактов.
- В MVP предполагается file-based реестр (llm-policy.yaml) и эскалация cheap → repair → reliable.
- До реализации политики допускается временная provider-level конфигурация, но любые расширения должны ориентироваться на ADR-003.
- Политика выключена по умолчанию и включается переменными окружения:
  - `LLM_POLICY_ENABLED=true`
  - `LLM_POLICY_PATH=llm_policy/llm-policy.yaml`
  - `LLM_POLICY_PROFILE=cheap`
  - `LLM_POLICY_ALLOW_PLACEHOLDERS=true` (только для шаблонных файлов, по умолчанию запрещено)
  - Для использования политики вызывайте high-level API (например, `llm_policy.tasks`), а не `runtime.py` напрямую.

## Agent Platform v0 (internal-only)

Internal-only контур агентной платформы по ADR-005. Он **не** подключён к runtime/RouterV2 и
не влияет на публичные контракты. Источник истины: `docs/adr/ADR-005-internal-agent-contract-v0.md`.

Компоненты:

- Registry v0: `agent_registry/agent-registry-v0.yaml` + loader `agent_registry/v0_loader.py`.
- Capability catalog v0: `agent_registry/capabilities-v0.yaml` (purpose/modes/risk/payload_allowlist).
- Validation toolkit: `agent_registry/validation.py` и `agent_registry/v0_reason_codes.py`.
- AgentRunner v0: `agent_registry/v0_runner.py` (`python_module`, `llm_policy_task`).
- Agent run logs (opt-in): `app/logging/agent_run_log.py`.

Валидация registry вручную:

```bash
python3 -c "from agent_registry.v0_loader import AgentRegistryV0Loader; AgentRegistryV0Loader.load()"
```

Agent run logs (agent_run.jsonl) включаются флагами:

- `AGENT_RUN_LOG_ENABLED=false`
- `AGENT_RUN_LOG_PATH=logs/agent_run.jsonl`

Правила приватности логов: никакого raw user text/LLM output; в `payload_summary` — только ключи,
счётчики и флаги (строковых значений нет, кроме имён ключей).

Baseline agents v0 (internal-only):

- `baseline-shopping-extractor` → `extract_entities.shopping`
- `baseline-clarify-suggestor` → `suggest_clarify`

Ручной запуск:

```bash
python3 scripts/run_agent_v0.py baseline-shopping-extractor docs/integration/examples/add_shopping_item_start_job.json
```

Агенты **не подключены** к RouterV2 и не влияют на MVP.

Пример минимального policy-файла (шаблон, реальные значения передаются через `LLM_POLICY_PATH`):

```yaml
schema_version: 1
compat:
  adr: "ADR-003"
  note: "internal-only"
profiles:
  cheap: {}
  reliable: {}
tasks:
  shopping_extraction: {}
routing:
  shopping_extraction:
    cheap:
      provider: "yandex_ai_studio"
      model: "gpt-oss-20b"
      temperature: 0.2
      max_tokens: 256
      timeout_ms: 2000
      project: "${YANDEX_FOLDER_ID}"
    reliable:
      provider: "yandex_ai_studio"
      model: "gpt-oss-120b"
      temperature: 0.2
      max_tokens: 256
      timeout_ms: 4000
      project: "${YANDEX_FOLDER_ID}"
fallback_chain:
  - event: "invalid_json"
    action: "repair_retry"
    max_retries: 1
  - event: "schema_validation_failed"
    action: "repair_retry"
    max_retries: 1
  - event: "invalid_json"
    action: "escalate_to"
    profile: "reliable"
  - event: "schema_validation_failed"
    action: "escalate_to"
    profile: "reliable"
  - event: "timeout"
    action: "return_error"
  - event: "llm_unavailable"
    action: "return_error"
  - event: "llm_error"
    action: "return_error"
```

## Shadow LLM Router (observability, zero-impact)

Shadow Router запускается параллельно RouterV2 и **никогда** не влияет на DecisionDTO.
Он работает в best-effort режиме и пишет только агрегированные метаданные.

### Флаги

- `SHADOW_ROUTER_ENABLED=false` — главный флаг включения.
- `SHADOW_ROUTER_TIMEOUT_MS=150` — soft-limit для метрики latency.
- `SHADOW_ROUTER_LOG_PATH=logs/shadow_router.jsonl` — путь к JSONL логам.
- `SHADOW_ROUTER_MODE=shadow` — допустимое значение (прочие режимы считаются invalid).

Shadow Router также учитывает `LLM_POLICY_ENABLED`. Если политика выключена —
пишется запись со статусом `skipped` и `error_type=policy_disabled`.

### Формат JSONL (shadow_router.jsonl)

Запись содержит только безопасные поля:

- `timestamp`, `trace_id`, `command_id`
- `router_version`, `router_strategy`
- `status` (`ok|skipped|error`), `latency_ms`, `error_type`
- `suggested_intent`, `missing_fields`, `clarify_question`
- `entities_summary` (только ключи/счётчики, без raw text)
- `confidence`, `model_meta`
- `baseline_intent`, `baseline_action`, `baseline_job_type`

**В логах нет** пользовательского текста и raw output LLM.

### Метрики из JSONL

- **intent_match_rate**: доля записей, где `suggested_intent == baseline_intent`.
- **entity_coverage**: доля записей, где `entities_summary.keys` содержит ожидаемые
  сущности для intent (например, `item` для `add_shopping_item`).
- **latency p50/p95**: перцентили по `latency_ms` для `status=ok|error`.
- **error_classes**: распределение `error_type` по всем `status=error`.

Примечание: в MVP `fallback_chain` является декларативной схемой для будущего расширения; фактическая эскалация реализована фиксированным алгоритмом cheap → repair → reliable.

## Partial Trust (PHASE 1 scaffolding)

На этапе PHASE 1 добавлена инфраструктура (конфиг + risk-логгер) без влияния на DecisionDTO.
По умолчанию Partial Trust выключен.

### Флаги

- `PARTIAL_TRUST_ENABLED=false` — главный выключатель.
- `PARTIAL_TRUST_INTENT=add_shopping_item` — коридор (строго один intent).
- `PARTIAL_TRUST_SAMPLE_RATE=0.01` — доля команд для выборки.
- `PARTIAL_TRUST_TIMEOUT_MS=200` — таймаут LLM-first кандидата (для будущего этапа).
- `PARTIAL_TRUST_PROFILE_ID=` — профиль в `llm_policy` (для будущего этапа).
- `PARTIAL_TRUST_RISK_LOG_PATH=logs/partial_trust_risk.jsonl` — путь к risk JSONL логам.

### Stable sampling

Выборка выполняется детерминированно: берётся hash от `command_id` и сравнивается с `sample_rate`.
Одинаковый `command_id` всегда даёт одинаковое решение при одном и том же `sample_rate`.
`sample_rate=0` — никогда не выбирать, `sample_rate=1` — всегда выбирать.

### Формат risk logs (partial_trust_risk.jsonl)

Запись содержит только безопасные поля:

- `timestamp`, `trace_id`, `command_id`
- `corridor_intent`, `sample_rate`, `sampled`
- `status` (`accepted_llm|fallback_deterministic|skipped|error`)
- `reason_code`
- `latency_ms`
- `model_meta`
- `baseline_summary`, `llm_summary`, `diff_summary`

**В логах нет** пользовательского текста и raw output LLM.

LLM policy включает internal task `partial_trust_shopping` и профиль `partial_trust`.
Идентификатор профиля задаётся флагом `PARTIAL_TRUST_PROFILE_ID`.

### Как включать Partial Trust

Минимальный набор флагов:

- `PARTIAL_TRUST_ENABLED=true`
- `PARTIAL_TRUST_INTENT=add_shopping_item`
- `PARTIAL_TRUST_SAMPLE_RATE=0.01`
- `PARTIAL_TRUST_TIMEOUT_MS=200`
- `PARTIAL_TRUST_PROFILE_ID=partial_trust`
- `LLM_POLICY_ENABLED=true`

### Rollout (пример)

1) `PARTIAL_TRUST_SAMPLE_RATE=0.01`
2) `PARTIAL_TRUST_SAMPLE_RATE=0.05`
3) `PARTIAL_TRUST_SAMPLE_RATE=0.10`

Откат: установить `PARTIAL_TRUST_ENABLED=false`.

### Status/Reason codes в risk logs

Статусы:

- `accepted_llm` — LLM-кандидат принят.
- `fallback_deterministic` — LLM-кандидат отклонён, возвращён baseline.
- `skipped` — Partial Trust выключен/не применим (не коридор/нет политики).
- `not_sampled` — коридор подходит, но команда не попала в выборку.
- `error` — непредвиденная ошибка, возвращён baseline.

Причины (reason_code):

- `accepted`
- `corridor_mismatch`
- `capability_mismatch`
- `policy_disabled`
- `not_sampled`
- `timeout`
- `llm_error`
- `invalid_schema`
- `invalid_item_name`
- `list_id_unknown`
- `low_confidence`
- `candidate_missing`

## LLM Assist Mode (Normalizer++ / Entities / Clarify)

Assist Mode помогает улучшать нормализацию и извлечение сущностей, но **не влияет** на выбор `action`.
Финальное решение остаётся за детерминированным RouterV2.

### Флаги

- `ASSIST_MODE_ENABLED=false` — общий выключатель.
- `ASSIST_NORMALIZATION_ENABLED=false` — LLM Normalizer++.
- `ASSIST_ENTITY_EXTRACTION_ENABLED=false` — LLM Entity Assist.
- `ASSIST_CLARIFY_ENABLED=false` — LLM Clarify Suggestor.
- `ASSIST_TIMEOUT_MS=200` — best-effort таймаут для каждого шага.
- `ASSIST_LOG_PATH=logs/assist.jsonl` — JSONL лог assist-шага.

### Принципы

- LLM выдаёт **hints**, детерминированный слой решает, принимать ли их.
- Любые ошибки/таймауты → silent fallback на deterministic-only поведение.
- В логах **нет** raw user text и raw LLM output.

### Формат assist-логов (assist.jsonl)

- `step`: `normalizer|entities|clarify`
- `status`: `ok|skipped|error`
- `accepted`: принят ли hint детерминированным слоем
- `latency_ms`, `error_type`
- `entities_summary`, `missing_fields_count`, `clarify_used`
- `assist_version`

### Метрики assist-качества

- снижение числа `clarify` итераций;
- рост доли `start_job`;
- улучшение entity coverage (доля заполненных сущностей);
- latency p50/p95 по шагам assist;
- error_classes по `error_type`.

## Связанные документы

- Контекст: `docs/integration/context_v1.md`
- Примеры: `docs/integration/examples/*.json`
