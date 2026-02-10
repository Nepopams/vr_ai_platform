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
