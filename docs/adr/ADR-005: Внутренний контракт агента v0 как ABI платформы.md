# ADR-005: Внутренний контракт агента v0 как ABI платформы (формат ДОРА)

## Статус
ACCEPTED

---

## 1) Декомпозиция

### 1.1 Контекст и цели
**Контекст.** ИИ-платформа Hometusk уже реализует “лестницу доверия” к LLM: **Shadow → Assist → Partial Trust corridor**. Параллельно ожидается готовность MVP-продукта, и платформа должна развиваться безопасно, не ломая ожидания продуктовой команды и не меняя публичные контракты.

**Проблема.** Без единого стандарта интеграции агентов мы быстро получим “агенты-снежинки”: разные форматы входов/выходов, разные правила валидации/логирования, разные зоны ответственности. Это блокирует масштабирование (оркестрация, ансамбли) и увеличивает техдолг.

**Цель.** Ввести **внутренний контракт агента v0** (internal ABI) как единый стандарт:
- описания агента (метаданные + capabilities),
- входов/выходов (AgentInput/AgentOutput),
- валидации (schema/shape + allowlist),
- приватности (no raw text by default),
- режимов (shadow/assist/partial_trust) с явными ограничениями.

**Ограничения (обязательные).**
- Нельзя менять публичные контракты: `contracts/`, `contracts/VERSION`, `contracts/schemas/*`, публичную семантику `DecisionDTO/CommandDTO`.
- Нельзя добавлять intents/actions в рамках данного ADR.
- Нельзя вводить execution-агентов/side-effects (это Фаза 6+).
- Нельзя включать “полную оркестрацию” в Фазе 4 — только подготовка основы.

### 1.2 Домены и подсистемы
**Затрагиваемые подсистемы:**
- **Router/Decision Engine** (deterministic baseline) — источник истины по умолчанию.
- **LLM Policy** (`llm_policy/*`) — профили/таски для LLM-бэкенд агентов (internal).
- **Agent Registry** (новая подсистема, file-based) — каталог `AgentSpec`.
- **Agent Runtime / Runner** (новая подсистема) — единый запуск: validate → run → validate → log.
- **Observability / Logging** — JSONL события запуска агента + risk events (privacy-safe).
- **Skills / QA** — сценарии/fixtures, которые нельзя ломать.

### 1.3 NFR (черновик)
- **Compatibility:** 0 изменений публичных контрактов; поведение RouterV2 без флагов не меняется.
- **Safety:** LLM outputs — не источник истины по умолчанию; режимы ограничены.
- **Privacy:** запрет raw user text / raw LLM output в логах по умолчанию.
- **Reliability:** best-effort таймауты, graceful fallback, стандартизированные reason codes.
- **Observability:** единый формат agent-run событий + корреляция `trace_id/command_id`.
- **Extensibility:** добавление агента через реестр без изменения кода (в идеале), либо минимум кода.
- **Maintainability:** единый toolkit валидации/allowlist; отсутствие “разных проверок везде”.

---

## 2) Оценка

### 2.1 Варианты
**Вариант A — “Без контракта, ad-hoc интеграции”**  
Добавляем агентов как получится: каждый агент сам определяет вход/выход и логику.

**Вариант B — “Публичный контракт (в `contracts/`)”**  
Формализуем AgentContract как публичный API, версионируем в `contracts/`.

**Вариант C — “Внутренний ABI (internal-only) + file registry + validation” (предлагаемый)**  
AgentContract v0 как внутренний стандарт, не публичный, хранится вне `contracts/`.

**Вариант D — “Полная оркестрация сейчас”**  
Сразу строим planner/router/critic/aggregator и т.д. как полноценную систему.

### 2.2 Критерии сравнения
1) **MVP safety / zero-impact:** можно ли развивать платформу без риска для продукта?
2) **Совместимость:** сохраняются ли публичные контракты?
3) **Контроль LLM-рисков:** есть ли единые правила validate/allowlist/privacy?
4) **Скорость расширения:** насколько быстро можно добавлять агента?
5) **Техдолг:** как быстро система превращается в “зоопарк”?
6) **Операбельность:** наблюдаемость, reason codes, трассировка.
7) **Гибкость:** можно ли менять внутренний контракт без внешних потребителей?

### 2.3 Trade-offs (сравнение)
- **A (ad-hoc)** выигрывает в скорости “сейчас”, но проигрывает по техдолгу и оркестрации почти сразу.
- **B (публичный контракт)** даёт формальность, но преждевременно фиксирует API и создаёт риск тормоза MVP.
- **C (internal ABI)** оптимален для MVP: даёт стандарты без заморозки публичного API.
- **D (полная оркестрация)** даёт иллюзию прогресса, но требует execution, SLA, retries — слишком рано.

**Вывод оценки:** Вариант C даёт максимальный ROI при минимальном риске для MVP.

---

## 3) Решение

### 3.1 Выбор архитектуры
Принять **Вариант C**: **Internal Agent Contract v0** как ABI платформы:
- Контракт **internal-only**, не размещается в `contracts/`.
- Агенты описываются в **file-based реестре** (YAML/JSON).
- У агента есть **режим**: `shadow | assist | partial_trust` (с ограничениями).
- Все outputs проходят единый pipeline:
  - validate (schema/shape) → allowlist → privacy-safe logging → return.
- По умолчанию источником истины остаётся **deterministic baseline** (RouterV2).

### 3.2 Оформление артефактов
В рамках реализации (Фаза 4) должны появиться следующие артефакты:

1) **ADR-005 (этот документ)** — архитектурное правило.
2) **Agent Registry v0** (file-based):
   - файл `agents/registry.yaml` (точный путь определяется проектными правилами)
   - поле `registry_version: v0` (рекомендуется)
3) **Internal схемы/типы**:
   - `AgentSpec`, `AgentCapability`, `AgentInput`, `AgentOutput`, `RunnerSpec`
   - validator для реестра и outputs
4) **Observability**:
   - `agent_run.jsonl` (стандартизированный формат, privacy-safe)
5) **Guidelines**:
   - секция в `docs/integration/README.md` про internal contract, режимы, privacy.

### 3.3 Контракт (v0): минимальная модель
**AgentSpec (реестр):**
- `agent_id`, `version`, `title`, `description`, `owner`
- `enabled`, `mode`
- `capabilities[]`
- `runner` (python_module или llm_policy_task как минимум)
- `timeouts.timeout_ms`
- `privacy.allow_raw_logs=false`
- `llm_profile_id?`

**AgentCapability:**
- `capability_id`
- `allowed_intents[]` (только существующие intents)
- `risk_level`
- `required_context[]`
- `provides[]` (`entities_hint`, `clarify_hint`, `plan_proposal`, `decision_candidate`)

**AgentInput:**
- `trace_id`, `command_id`
- `text?` (чувствительно; передаётся агенту, но не логируется)
- `normalized_snapshot` (safe)
- `context_summary` (safe)
- `constraints` (timeout/mode/limits)

**AgentOutput:**
- `kind` (`hints|plan_proposal|decision_candidate`)
- `status` (`ok|rejected|error|skipped`)
- `reason_code`
- `payload` (validated + allowlisted)
- `confidence?`, `missing_fields?`, `clarify_question?` (только с фильтрами; raw не логировать)
- `meta.latency_ms`, `meta.model_meta?`, `meta.warnings?`

---

## 4) Аспекты (Consequences / Узкие места / Техдолг / Стандарты / SLA-SLO)

### 4.1 Consequences (плюсы/минусы)
**Плюсы:**
- Масштабируемость: новые агенты подключаются предсказуемо.
- Основа оркестрации: можно выбирать агентов по capabilities.
- Контроль рисков: единые validate/allowlist/privacy + reason codes.
- MVP safety: минимум воздействия на продукт.

**Минусы:**
- Увеличение upfront работы (реестр, валидаторы, схемы).
- Нужно сопровождать версии internal ABI (но это лучше, чем сопровождать хаос).

### 4.2 Узкие места и риски
1) **Дрейф контракта**: если v0 начнёт расширяться без контроля.  
   *Mitigation:* registry_version, explicit schema, “no unknown fields” (additionalProperties=false).

2) **Риск утечек**: агент может вернуть текст, который случайно попадёт в логи.  
   *Mitigation:* централизованный логгер только с summaries; запрет raw по умолчанию; audit tests.

3) **Разные allowlist/валидации**: если проверки будут размазаны по коду.  
   *Mitigation:* единый validation toolkit, единый набор reason_code.

4) **Сложность миграций ABI**: v1/v2 потребуются позже.  
   *Mitigation:* semver-like versioning, backward-compatible расширения, отдельные ADR на major.

### 4.3 Технический долг (что “сознательно оставляем”)
- Нет service-based registry (только file-based v0).
- Нет динамического hot-reload реестра.
- Нет execution и side-effect семантики.
- Нет полноценного планировщика/оркестратора (только подготовка).

### 4.4 Стандарты и правила (обязательные)
- **Deterministic-first:** RouterV2 baseline — источник истины по умолчанию.
- **Modes:** shadow/assist/partial_trust (partial_trust только corridor-limited).
- **Validation-first:** любые outputs агентов — через schema/allowlist.
- **Privacy-first:** no raw user text / no raw LLM output в логах по умолчанию.
- **Reason codes:** стандартизированные коды причин reject/error.
- **Traceability:** все события коррелируются `trace_id` + `command_id`.

### 4.5 SLA/SLO (черновик)
Поскольку в MVP нет execution, SLA/SLO вводим как черновик для внутреннего качества:
- **Latency budget (agent runtime):** best-effort таймауты (например p95 < 200–300ms для assist/shadow).
- **Reliability:** при любых ошибках агента baseline работает без деградации функционала.
- **Observability:** 100% agent runs → agent_run events (без raw).

---

## Приложение: Почему ADR-002 не нарушен
ADR-002 фиксирует запрет LLM как глобального источника решения. Этот ADR вводит **внутренний стандарт агента**
и режимы, где:
- `shadow` и `assist` не делают LLM “истиной”,
- `partial_trust` допускается только в corridor-режиме и должен быть описан отдельным ADR (например ADR-004),
  включая rollback, acceptance rules и risk logs.

Таким образом, базовая норма ADR-002 сохраняется, а исключения остаются строго ограниченными и измеримыми.
