# Workpack: ST-047 — ASR Transcription Endpoint MVP

**Status:** Done (manual Cloud.ru UAT pending)
**Story:** `docs/planning/epics/EP-015/stories/ST-047-asr-transcription-endpoint-mvp.md`
**Owner:** Codex PLAN / Codex APPLY / read-only review gate

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Roadmap | `docs/planning/strategy/roadmap.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q2-asr-cloudru-whisper.md` |
| Epic | `docs/planning/epics/EP-015/epic.md` |
| Story | `docs/planning/epics/EP-015/stories/ST-047-asr-transcription-endpoint-mvp.md` |
| ADR | `docs/adr/ADR-008-asr-cloudru-whisper-mvp.md` |
| ASR API contract | `docs/contracts/asr-transcription-api.md` |
| Diagram | `docs/diagrams/asr-cloudru-whisper-flow.puml` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |
| Review / hardening summary | `docs/planning/workpacks/ST-047/review-report.md` |

---

## Outcome

Add a minimal ASR endpoint and Cloud.ru Whisper client that transcribes one uploaded
audio file and returns text without changing RouterV2 or DecisionDTO behavior.

## Artifact Gate Result

**APPROVED for APPLY under delegated user gate.**

| Gate | Result |
|------|--------|
| Contract | Additive public API endpoint. No CommandDTO/DecisionDTO schema edit. No `contracts/VERSION` bump. |
| ADR | ADR-008 accepted. |
| Diagram | ASR flow diagram added. |
| Security/privacy | Must add tests proving no audio/transcript/raw user text in logs. |
| Human Gate C | Delegated by user request: "human gates проходи сам принимая лучшие решения". Scope limited to this workpack. |

## Acceptance Criteria

1. `POST /v1/asr/transcribe` accepts one multipart `file` audio part.
2. ASR does not call `/v1/decide`, RouterV2, Assist Mode, or Partial Trust.
3. Cloud.ru provider/model/base URL/path/API key/timeout/max size are env-configured.
4. Client maps success to a typed result with transcript, provider, model, latency, and upstream status.
5. Controlled errors exist for timeout, auth error, unsupported media, file too large, upstream unavailable, and bad upstream response.
6. Safe ASR JSONL logs contain only metadata and never transcript/raw audio/raw user text.
7. Unit/integration tests mock Cloud.ru; no real API key is needed.
8. Existing decide API tests still pass.
9. Documentation covers local usage and manual UAT smoke.

## Files to Change

### New files

| File | Description |
|------|-------------|
| `app/asr/__init__.py` | ASR package marker. |
| `app/asr/config.py` | Env-driven ASR configuration. |
| `app/asr/client.py` | Cloud.ru/OpenAI-compatible transcription client. |
| `app/asr/errors.py` | Controlled ASR exceptions and error mapping. |
| `app/asr/multipart.py` | Bounded single-file multipart parser for MVP. |
| `app/logging/asr_log.py` | Privacy-safe ASR metadata log writer. |
| `app/models/asr_models.py` | Pydantic ASR response model. |
| `app/routes/asr.py` | `/asr/transcribe` router. |
| `tests/test_asr_config.py` | Config tests. |
| `tests/test_asr_client.py` | Mocked client tests. |
| `tests/test_asr_transcribe_api.py` | Endpoint tests. |
| `tests/test_asr_privacy.py` | Privacy log tests. |
| `tests/test_asr_integration_smoke.py` | Manual real Cloud.ru smoke test, skipped unless explicitly enabled. |
| `docs/guides/asr-cloudru-whisper.md` | Local and UAT guide. |

### Modified files

| File | Change |
|------|--------|
| `app/main.py` | Include ASR router under `/v1`. |
| `.env.example` | Add ASR env variables. |
| `docs/guides/cloudru-llm-setup.md` | Remove stale ASR external-only guidance and link to ASR guide. |

### Forbidden paths

- `contracts/schemas/**`
- `contracts/VERSION`
- `graphs/**`
- `routers/**`
- `agent_registry/**`
- `agent_runner/**`
- existing `.codex/skills/**`

## Implementation Plan

### Step 1: ASR config, errors, and safe logging

Create env config helpers, controlled error classes, and JSONL logging with metadata only.

### Step 2: Multipart boundary parser

Parse one bounded multipart body using standard library facilities. Reject missing file,
multiple file parts, malformed bodies, unsupported media type, and oversized body.

### Step 3: Cloud.ru ASR client

Use `httpx.Client` with bearer auth, multipart file upload, model form field, configurable
path, and typed result. Map timeout/auth/upstream/bad response to controlled errors.

### Step 4: Route and app registration

Add `POST /v1/asr/transcribe`, generate trace_id, call parser/client, append safe log, and
return typed response. Do not mount an unversioned ASR endpoint.

### Step 5: Tests and docs

Add focused tests for config, client, endpoint behavior, privacy logging, decide
regression, and a skipped-by-default real Cloud.ru smoke test. Add local/UAT docs.

## Verification Commands

```bash
python3 -m pytest tests/test_asr_config.py tests/test_asr_client.py tests/test_asr_transcribe_api.py tests/test_asr_privacy.py -v
python3 -m pytest tests/test_asr_integration_smoke.py -v
python3 -m pytest tests/test_api_decide.py tests/test_api_versioned.py -v
make validate_contracts
```

Full regression if time/environment allows:

```bash
python3 -m pytest tests/ -v
make release-sanity
```

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Cloud.ru ASR endpoint differs from OpenAI-compatible audio endpoint | Medium | High | `ASR_TRANSCRIBE_PATH` configurable; manual UAT smoke required. |
| Multipart parser accepts malformed data | Medium | Medium | Strict one-file parser and focused endpoint tests. |
| Transcript/audio leaks into logs | Low | High | Dedicated safe logger and privacy test. |
| ASR route accidentally impacts `/v1/decide` | Low | High | Separate router/service; regression tests for decide/versioned API. |

## Rollback

Remove new ASR package, ASR route/model/logging/tests/docs, remove ASR router import/include
from `app/main.py`, and remove ASR env block from `.env.example`.
