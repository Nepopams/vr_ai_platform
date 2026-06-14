> Legacy notice: active workflow now lives in AGENTS.md and docs/CODEX-WORKFLOW.md. This file or directory is historical reference only. Do not use it as active workflow authority.

# Lint

Check code formatting with Spotless.

```bash
cd services/backend && ./gradlew spotlessCheck
```

To auto-fix formatting issues:

```bash
cd services/backend && ./gradlew spotlessApply
```
