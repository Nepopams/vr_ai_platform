# Codex APPLY Prompt — ST-023: .env.example and LLM Configuration Documentation

## Role
You are a senior developer creating documentation files for the AI Platform.

## Context (from PLAN findings)

- `.env.example` does not exist — create new.
- `docs/guides/` directory does not exist — create directory and file.
- `.gitignore` exists at project root, does NOT contain `.env` — add it.
- All env vars confirmed from 12 source files (see sections below).
- `LOG_USER_TEXT` is privacy-sensitive — mark in docs.
- `llm_runner_log.py` has no env vars (hardcoded path) — skip.

## Files to Create

### 1. `.env.example` (NEW)

Create this file with EXACT content:

```
# =============================================================================
# AI Platform — Environment Variables
# =============================================================================
# Copy this file to .env and fill in your values:
#   cp .env.example .env
#
# NEVER commit .env with real secrets!
# =============================================================================

# -----------------------------------------------------------------------------
# LLM Core (llm_policy/)
# -----------------------------------------------------------------------------
# Master switch for LLM policy. Set to "true" to enable LLM features.
LLM_POLICY_ENABLED=false

# API key for the LLM provider. REQUIRED when LLM_POLICY_ENABLED=true.
LLM_API_KEY=your-api-key-here

# Base URL for the LLM API (e.g. https://api.openai.com/v1).
LLM_BASE_URL=

# Policy routing profile ("cheap", "quality", etc.).
LLM_POLICY_PROFILE=cheap

# Path to custom policy YAML file. Leave empty for built-in policy.
LLM_POLICY_PATH=

# Allow placeholder responses instead of real LLM calls (dev/test only).
# Must be "false" for bootstrap to register a real caller.
LLM_POLICY_ALLOW_PLACEHOLDERS=false

# -----------------------------------------------------------------------------
# Agent Runner (agent_runner/)
# -----------------------------------------------------------------------------
# LLM provider name ("openai", "yandex").
LLM_PROVIDER=openai

# Model identifier.
LLM_MODEL=gpt-4o-mini

# LLM temperature (0.0 = deterministic, 1.0 = creative).
LLM_TEMPERATURE=0.1

# Request timeout in milliseconds (takes precedence over OPENAI_TIMEOUT_S).
# LLM_TIMEOUT_MS=

# Fallback timeout in seconds (used if LLM_TIMEOUT_MS is not set).
# OPENAI_TIMEOUT_S=15

# Maximum output tokens. Leave unset for provider default.
# LLM_MAX_OUTPUT_TOKENS=

# Whether to store completions on the provider side.
LLM_STORE=false

# Project identifier for the LLM provider.
LLM_PROJECT=

# Agent runner server host and port.
LLM_AGENT_RUNNER_HOST=0.0.0.0
LLM_AGENT_RUNNER_PORT=8089

# Agent runner URL for client connections.
LLM_AGENT_RUNNER_URL=

# -----------------------------------------------------------------------------
# Shadow Router (routers/shadow_config.py)
# -----------------------------------------------------------------------------
# Enable shadow LLM router (parallel LLM calls, no impact on decisions).
SHADOW_ROUTER_ENABLED=false

# Timeout for shadow router LLM calls (ms).
SHADOW_ROUTER_TIMEOUT_MS=150

# Shadow router log file path.
SHADOW_ROUTER_LOG_PATH=logs/shadow_router.jsonl

# Shadow router mode.
SHADOW_ROUTER_MODE=shadow

# -----------------------------------------------------------------------------
# Assist Mode (routers/assist/)
# -----------------------------------------------------------------------------
# Master switch for assist mode.
ASSIST_MODE_ENABLED=false

# Individual assist features (all require ASSIST_MODE_ENABLED=true).
ASSIST_NORMALIZATION_ENABLED=false
ASSIST_ENTITY_EXTRACTION_ENABLED=false
ASSIST_CLARIFY_ENABLED=false

# Timeout for assist LLM calls (ms).
ASSIST_TIMEOUT_MS=200

# Assist log file path.
ASSIST_LOG_PATH=logs/assist.jsonl

# -----------------------------------------------------------------------------
# Assist Agent Hints (routers/assist/)
# -----------------------------------------------------------------------------
# Enable agent-backed entity extraction hints.
ASSIST_AGENT_HINTS_ENABLED=false

# Agent ID for hints (from agent registry).
ASSIST_AGENT_HINTS_AGENT_ID=

# Capability to request from agent.
ASSIST_AGENT_HINTS_CAPABILITY=extract_entities.shopping

# Comma-separated allowlist of intents for agent hints.
ASSIST_AGENT_HINTS_ALLOWLIST=

# Sampling rate for agent hints (0.0 = off, 1.0 = all).
ASSIST_AGENT_HINTS_SAMPLE_RATE=0.0

# Timeout for agent hint calls (ms).
ASSIST_AGENT_HINTS_TIMEOUT_MS=120

# -----------------------------------------------------------------------------
# Partial Trust (routers/partial_trust_config.py)
# -----------------------------------------------------------------------------
# Enable partial trust corridor (LLM decisions accepted for allowed intents).
PARTIAL_TRUST_ENABLED=false

# Intent allowed for partial trust. Only "add_shopping_item" is supported.
PARTIAL_TRUST_INTENT=add_shopping_item

# Sampling rate for partial trust (0.0-1.0).
PARTIAL_TRUST_SAMPLE_RATE=0.01

# Timeout for partial trust LLM calls (ms).
PARTIAL_TRUST_TIMEOUT_MS=200

# Profile ID for partial trust (optional).
PARTIAL_TRUST_PROFILE_ID=

# Risk log file path for partial trust decisions.
PARTIAL_TRUST_RISK_LOG_PATH=logs/partial_trust_risk.jsonl

# -----------------------------------------------------------------------------
# Shadow Agent (routers/shadow_agent_config.py)
# -----------------------------------------------------------------------------
# Enable shadow agent invoker (parallel agent calls for comparison).
SHADOW_AGENT_INVOKER_ENABLED=false

# Path to agent registry YAML.
SHADOW_AGENT_REGISTRY_PATH=agent_registry/agent-registry-v0.yaml

# Comma-separated allowlist of agent IDs.
SHADOW_AGENT_ALLOWLIST=

# Sampling rate for shadow agent invocations (0.0-1.0).
SHADOW_AGENT_SAMPLE_RATE=0.0

# Timeout for shadow agent calls (ms).
SHADOW_AGENT_TIMEOUT_MS=150

# Enable diff logging for shadow agent results.
SHADOW_AGENT_DIFF_LOG_ENABLED=false

# Diff log file path.
SHADOW_AGENT_DIFF_LOG_PATH=logs/shadow_agent_diff.jsonl

# -----------------------------------------------------------------------------
# Agent Registry (agent_registry/)
# -----------------------------------------------------------------------------
# Enable agent registry.
AGENT_REGISTRY_ENABLED=false

# Path to agent registry YAML (overrides default).
# AGENT_REGISTRY_PATH=

# Enable agent registry integration in core pipeline.
AGENT_REGISTRY_CORE_ENABLED=false

# -----------------------------------------------------------------------------
# Shopping Extractor Client (app/llm/agent_runner_client.py)
# -----------------------------------------------------------------------------
# Enable LLM-based shopping extractor.
LLM_SHOPPING_EXTRACTOR_ENABLED=false

# Shopping extractor mode ("shadow" or "active").
LLM_SHOPPING_EXTRACTOR_MODE=shadow

# Timeout for shopping extractor calls (seconds).
LLM_SHOPPING_EXTRACTOR_TIMEOUT_S=5

# -----------------------------------------------------------------------------
# Pipeline Logging
# -----------------------------------------------------------------------------
# Pipeline latency instrumentation.
PIPELINE_LATENCY_LOG_ENABLED=true
PIPELINE_LATENCY_LOG_PATH=logs/pipeline_latency.jsonl

# Fallback metrics logging.
FALLBACK_METRICS_LOG_ENABLED=true
FALLBACK_METRICS_LOG_PATH=logs/fallback_metrics.jsonl

# Decision log paths.
DECISION_LOG_PATH=logs/decisions.jsonl
DECISION_TEXT_LOG_PATH=logs/decision_text.jsonl

# PRIVACY WARNING: Logs raw user text when enabled. Use only for debugging.
LOG_USER_TEXT=false

# Agent run log.
AGENT_RUN_LOG_ENABLED=false
AGENT_RUN_LOG_PATH=logs/agent_run.jsonl

# -----------------------------------------------------------------------------
# Routing
# -----------------------------------------------------------------------------
# Decision router strategy version.
DECISION_ROUTER_STRATEGY=v1
```

### 2. `docs/guides/llm-setup.md` (NEW)

Create directory `docs/guides/` first, then create this file with EXACT content:

```markdown
# LLM Setup Guide

This guide covers how to configure and run the AI Platform with a real LLM provider.

## Prerequisites

- Python 3.10+
- Virtual environment (`python3 -m venv .venv && source .venv/bin/activate`)
- An API key from an LLM provider (OpenAI, Yandex, or compatible)
- Platform dependencies installed (`pip install -r requirements.txt`)

## Quick Start

1. Copy the environment template:

   ```bash
   cp .env.example .env
   ```

2. Set your API key:

   ```
   LLM_API_KEY=sk-your-real-api-key
   ```

3. Set the base URL for your provider:

   ```
   LLM_BASE_URL=https://api.openai.com/v1
   ```

4. Enable LLM policy:

   ```
   LLM_POLICY_ENABLED=true
   ```

5. Ensure placeholders are disabled (required for real calls):

   ```
   LLM_POLICY_ALLOW_PLACEHOLDERS=false
   ```

## Environment Variable Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_POLICY_ENABLED` | `false` | Master switch. Must be `true` to use LLM. |
| `LLM_API_KEY` | *(none)* | API key for the LLM provider. **Required.** |
| `LLM_BASE_URL` | *(none)* | Base URL for the LLM API endpoint. |
| `LLM_POLICY_PROFILE` | `cheap` | Routing profile (`cheap`, `quality`). |
| `LLM_POLICY_PATH` | *(none)* | Path to custom policy YAML. |
| `LLM_POLICY_ALLOW_PLACEHOLDERS` | `false` | Must be `false` for real LLM calls. |
| `LLM_PROVIDER` | `openai` | Provider name (`openai`, `yandex`). |
| `LLM_MODEL` | `gpt-4o-mini` | Model identifier. |
| `LLM_TEMPERATURE` | `0.1` | Sampling temperature. |

## Enable/Disable Flow

### Enabling LLM

Set these three variables to activate the LLM caller at startup:

```
LLM_POLICY_ENABLED=true
LLM_POLICY_ALLOW_PLACEHOLDERS=false
LLM_API_KEY=sk-your-real-api-key
```

On startup, `bootstrap_llm_caller()` checks three guards in order:

1. **LLM_POLICY_ENABLED** must be `true` — otherwise skips silently.
2. **LLM_POLICY_ALLOW_PLACEHOLDERS** must be `false` — otherwise logs error and skips.
3. **LLM_API_KEY** must be set — otherwise logs warning and skips.

If all guards pass, the HTTP caller is registered and available for the pipeline.

### Disabling LLM (Kill-Switch)

To disable all LLM functionality immediately:

```
LLM_POLICY_ENABLED=false
```

This is the **kill-switch**. When set to `false`:

- No LLM caller is registered at startup.
- Shadow router, assist mode, and partial trust are effectively disabled.
- The platform runs in fully deterministic mode.
- All decisions use baseline (rule-based) logic only.
- **No degradation** in functionality — deterministic fallback handles everything.

### What Happens on Error

If the LLM is enabled but encounters an error at runtime:

- **Timeout**: LLM call is abandoned, deterministic fallback used.
- **API error**: Logged, deterministic fallback used.
- **Invalid response**: Logged, deterministic fallback used.

The platform **never fails** due to LLM errors. Every LLM-assisted feature has a
deterministic fallback that activates automatically.

## Feature Flags

Individual LLM features can be controlled independently:

| Feature | Variable | Default | Requires |
|---------|----------|---------|----------|
| Shadow Router | `SHADOW_ROUTER_ENABLED` | `false` | `LLM_POLICY_ENABLED=true` |
| Assist Mode | `ASSIST_MODE_ENABLED` | `false` | `LLM_POLICY_ENABLED=true` |
| Partial Trust | `PARTIAL_TRUST_ENABLED` | `false` | `LLM_POLICY_ENABLED=true` |

Each feature is independently toggleable and has its own timeout configuration.

## Troubleshooting

### "LLM policy disabled, skipping bootstrap"

**Cause**: `LLM_POLICY_ENABLED` is not set to `true`.

**Fix**: Set `LLM_POLICY_ENABLED=true` in your `.env` file.

### "Cannot register real LLM caller with placeholders enabled"

**Cause**: `LLM_POLICY_ALLOW_PLACEHOLDERS` is set to `true`.

**Fix**: Set `LLM_POLICY_ALLOW_PLACEHOLDERS=false`. Placeholder mode and real LLM
calls are mutually exclusive.

### "LLM_API_KEY not set, LLM caller not registered"

**Cause**: `LLM_API_KEY` environment variable is empty or missing.

**Fix**: Set `LLM_API_KEY` to a valid API key from your LLM provider.

### "LLM caller registered successfully" but features don't work

**Cause**: Individual feature flags are still disabled.

**Fix**: Enable the specific feature you need:
- `SHADOW_ROUTER_ENABLED=true` for shadow routing
- `ASSIST_MODE_ENABLED=true` for assist mode
- `PARTIAL_TRUST_ENABLED=true` for partial trust

### Privacy note

`LOG_USER_TEXT` controls whether raw user text is written to decision logs.
It defaults to `false`. Only enable for debugging in non-production environments.
```

### 3. `.gitignore` (UPDATE)

Add the following BEFORE the existing first line (`# Runtime decision logs`):

```
# Secrets
.env

```

This adds `.env` to gitignore with a section header, followed by a blank line
before the existing content.

## Files NOT Modified (invariants)
- `llm_policy/*.py` — DO NOT CHANGE
- `routers/*.py` — DO NOT CHANGE
- `app/logging/*.py` — DO NOT CHANGE
- `agent_runner/*.py` — DO NOT CHANGE
- `tests/*` — DO NOT CHANGE

## Verification Commands

```bash
# Verify .env in .gitignore
grep -n "^\.env$" .gitignore

# Verify .env.example contains all AC-1 required vars
grep -c "LLM_POLICY_ENABLED\|LLM_API_KEY\|LLM_BASE_URL\|LLM_PROVIDER\|LLM_POLICY_PROFILE\|LLM_POLICY_PATH\|LLM_POLICY_ALLOW_PLACEHOLDERS\|SHADOW_ROUTER_ENABLED\|PARTIAL_TRUST_ENABLED" .env.example

# Verify guide exists
ls docs/guides/llm-setup.md

# Full test suite (no regression)
source .venv/bin/activate && python3 -m pytest --tb=short -q
```

## STOP-THE-LINE
If any of the following occur, STOP and report:
- Existing tests fail after your changes
- Any file listed as "DO NOT CHANGE" needs modification
- `.env.example` contains real API keys or secrets
