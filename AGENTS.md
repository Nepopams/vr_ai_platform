# Environment

- Python binary: **`python3`** (NOT `python`). The system does not have a `python` symlink.
- Virtual environment: `.venv/` (use `.venv/bin/python3` or `source .venv/bin/activate`).
- Test runner: `.venv/bin/pytest` or `python3 -m pytest`.
- All verification commands must use `python3`, not `python`.

# Base Rule

All explanations, summaries, reasoning, and descriptions of changes MUST be in Russian.
Code itself stays in its original language.

# Project Overview

HomeTask AI Platform routes user commands through a graph pipeline (`graphs/core_graph.py`)
to produce structured decisions (DecisionDTO). LLM enhances but never replaces deterministic rules.

# Sources of Truth

| Artifact | Canonical path |
|----------|---------------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Roadmap | `docs/planning/strategy/roadmap.md` |
| MVP scope | `docs/planning/releases/MVP.md` |
| Definition of Ready | `docs/_governance/dor.md` |
| Definition of Done | `docs/_governance/dod.md` |
| ADR archive | `docs/adr/` |
| ADR index | `docs/_indexes/adr-index.md` |
| Contract schemas | `contracts/schemas/` (JSON Schema) |
| Contract version | `contracts/VERSION` (semver) |
| Diagrams index | `docs/_indexes/diagrams-index.md` |
| Epics & stories | `docs/planning/epics/<EPIC_ID>/` |
| Workpacks | `docs/planning/workpacks/<STORY_ID>/` |

# Development Rules

## Contract & ADR compliance (single source)

- All inputs/outputs conform to `contracts/schemas/`.
- Contract changes must follow semver (ADR-001). Never remove/rename fields without versioned migration.
- New intents/agents/actions require ADR + semver bump.
- If a change conflicts with an ADR, stop and create a new ADR (Draft) instead of pushing code.
- Model policy / LLM selection must follow ADR-003.
- Safe handling of unknown `action` values and payload fields is mandatory (ADR-001).

Mandatory ADRs:
- ADR-000: Contract-first Intent -> Decision Engine
- ADR-001: Contract versioning & compatibility
- ADR-002: Agent model & execution boundaries
- ADR-003: LLM model policy registry & escalation
- ADR-005: Internal Agent Contract v0

## MVP compliance

Changes to `contracts/`, `graphs/`, `agents/`, `skills/` must conform to MVP scope.
New intents/actions/fields require: MVP scope update + ADR-001 semver + fixture/test updates.

## Privacy

No raw user text or raw LLM output in logs or reports.
Logging uses summaries/counters only. Sensitive fields: `text`, `question`, `item_name`,
`ui_message`, `raw`, `output`, `prompt`, `normalized_text`.

## Diagrams

If you change `contracts/`, `graphs/`, `agents/`, or `api/`, check whether diagrams
need updates (`docs/_indexes/diagrams-index.md`). Explain in commit if skipped.

# Agent Platform v0

## Architecture

- Agents are orchestrated by `graphs/core_graph.py`.
- Each agent accepts a command payload, returns a structured contribution to the decision.
- Agent Contract v0 (ADR-005): standardized inputs/outputs, no "snowflake" agents.

## Components

| Component | Path |
|-----------|------|
| Registry v0 | `agent_registry/agent-registry-v0.yaml` |
| Loader | `agent_registry/v0_loader.py` |
| Runner | `agent_registry/v0_runner.py` (modes: `python_module`, `llm_policy_task`) |
| Capabilities catalog | `agent_registry/capabilities-v0.yaml` |
| Validation toolkit | `agent_registry/validation.py`, `agent_registry/v0_reason_codes.py` |
| Baseline agents | `agents/baseline_shopping.py`, `agents/baseline_clarify.py` |
| Run logs | `app/logging/agent_run_log.py` (opt-in) |
| Manual runner | `scripts/run_agent_v0.py` |
| Config | `AGENT_REGISTRY_ENABLED=true`, `AGENT_REGISTRY_PATH=<path>` |

## Adding a new agent v0

1. Add AgentSpec to registry, `enabled: false` by default.
2. Define exactly 1 capability in the catalog (`payload_allowlist`, `contains_sensitive_text`).
3. Set `runner.ref` (valid module/task), ensure `mode` is allowed for the capability.
4. Output must pass validation toolkit. Logs: summaries/counters only, no raw data.
5. Test via `scripts/run_agent_v0.py` before enabling.

## Assist agent-hints

- Enabled by feature flags only; do not change `action/job_type` selection.
- Used as hints for missing entities; deterministic-first guardrails mandatory.

# Offline-friendly checks

- `make release-sanity` skips `api-sanity` if `fastapi` is unavailable.
- Full API sanity: `RUN_API_SANITY=1 make release-sanity`.

# Canonical Commands

```bash
python3 -m pytest tests/ -v        # full test suite
make validate_contracts             # contract validation
make run_graph                      # single graph run
make run_graph_suite                # full graph regression
make audit_decisions                # decision log audit
make release-sanity                 # release sanity check
```
