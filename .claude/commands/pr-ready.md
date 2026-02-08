# PR Ready

Pre-PR checklist - run before creating a pull request.

## Steps

1. **Run lint**
```bash
cd services/backend && ./gradlew spotlessApply
```

2. **Run tests**
```bash
cd services/backend && ./gradlew test
```

3. **Check documentation**
- [ ] service-catalog.md updated if services changed
- [ ] CLAUDE.md updated if architecture/stack changed
- [ ] API contracts updated if endpoints changed
- [ ] ADR created if significant decision made

## Definition of Done (Stage 1)

- [ ] `docker-compose up` starts postgres + keycloak + backend successfully
- [ ] `POST /api/v1/commands` with `create_task` works
- [ ] `POST /api/v1/commands` with `complete_task` works
- [ ] Invalid payload → 400 with SCHEMA_INVALID
- [ ] Non-member → 403 Forbidden
- [ ] correlationId present in response headers
- [ ] DecisionLog created for every command
- [ ] TaskActivity recorded for every action
- [ ] All tests pass
