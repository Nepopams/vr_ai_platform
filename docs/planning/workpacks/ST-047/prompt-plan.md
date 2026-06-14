# Codex PLAN Prompt — ST-047: ASR Transcription Endpoint MVP

## Role

You are a senior Python/FastAPI developer performing read-only exploration before ASR APPLY.

## Rules

- No file edits, no writes, no package installs, no runtime mutation.
- Inspect only repository state and public Cloud.ru contract evidence already recorded in ADR-008.
- Stop if the workpack conflicts with accepted ADRs or requires CommandDTO/DecisionDTO schema edits.

## Tasks

1. Confirm `app/main.py` router pattern and `/v1` middleware.
2. Confirm existing API model/test style.
3. Confirm `httpx` is available in `pyproject.toml`.
4. Confirm no `python-multipart` dependency is available locally; use workpack parser approach.
5. Confirm no ASR runtime files already exist.
6. Confirm forbidden paths can remain untouched.

## PLAN Findings

- `app/main.py` mounts routers under `/v1` and adds `API-Version: v1` for `/v1/*`.
- `app/models/api_models.py` uses Pydantic v2 models with `extra="forbid"`.
- Tests use `fastapi.testclient.TestClient(create_app())`.
- `httpx` is already declared in `pyproject.toml`.
- Local `python3 -c "import multipart"` fails; avoid FastAPI `UploadFile` dependency in this workpack.
- No ASR runtime package exists yet.
- No CommandDTO/DecisionDTO schema edits are needed.

## Readiness for Human Gate C

Ready. User delegated Human Gate C approval for this initiative. APPLY must stay within
`docs/planning/workpacks/ST-047/workpack.md`.
