# INIT-2026Q1-api-integration — API & Integration: Production-Grade REST API

**Приоритет:** Высокий
**Период:** 2026Q1 (PI02)
**Статус:** Proposed
**Owner:** TBD

## Контекст

MVP платформы завершён: 30/30 историй, 270 тестов, 9/9 инициатив закрыты.
Платформа работает, но API не готов для реальных клиентов:
- Единственный endpoint `POST /decide` без версии в пути
- Нет Pydantic-моделей (raw dict I/O)
- Нет health/readiness endpoints
- Ошибки — ad-hoc HTTP exceptions без стандартного формата
- Нет auto-generated OpenAPI spec
- Нет webhook-механизма для push-уведомлений

## Цель

Сделать AI Platform пригодной для реальной интеграции с ConsumerApp:
- Версионированный REST API (`/v1/decide`)
- Типизированные request/response (Pydantic)
- Стандартные health/readiness probes
- Structured error responses (RFC 7807)
- Auto-generated OpenAPI spec с CI-контролем drift
- Webhook foundation для push-нотификаций

## Scope

### Epics

- **EP-011**: Versioned REST API (ST-032 — ST-036)
- **EP-012**: Webhook Notification Foundation (ST-037 — ST-039)

### Out of scope

- Authentication / authorization
- Rate limiting
- gRPC / GraphQL / WebSocket
- Multi-tenant API keys
- API gateway / reverse proxy
- Client SDK generation

## Acceptance criteria

1. `POST /v1/decide` принимает typed CommandRequest, возвращает typed DecisionResponse
2. `API-Version: v1` header на всех v1-ответах
3. `GET /health` и `GET /ready` работают
4. Ошибки в формате RFC 7807 (problem+json)
5. `contracts/openapi.json` auto-generated, CI-diff guard
6. Webhook dispatch на `decision_completed` (flag-gated, async, retry)
7. Все MVP exit criteria сохранены
8. Contract VERSION bump: 2.0.0 → 2.1.0 (additive, minor)

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Pydantic migration ломает существующих клиентов | Medium | Backward-compatible `/decide` path сохранён |
| OpenAPI spec drift | Low | CI step: generate + diff |
| Webhook dispatch добавляет latency | Medium | Async fire-and-forget, не блокирует response |

## Dependencies

- FastAPI framework (в pyproject.toml)
- Pydantic library (нужно добавить)
- httpx (для webhook dispatch, уже в pyproject.toml)
- ADR-001 (contract versioning policy) — Accepted
