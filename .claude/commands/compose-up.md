> Legacy notice: active workflow now lives in AGENTS.md and docs/CODEX-WORKFLOW.md. This file or directory is historical reference only. Do not use it as active workflow authority.

# Compose Up

Start local development infrastructure (PostgreSQL + Keycloak).

```bash
cd infra/compose && docker-compose up -d
```

Check status:
```bash
docker-compose ps
```

View logs:
```bash
docker-compose logs -f
```
