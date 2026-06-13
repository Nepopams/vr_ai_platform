# Cloud.ru LLM Setup

## Purpose

Cloud.ru Foundation Models can be used as an OpenAI-compatible LLM provider for
AI Platform LLM policy tasks.

ASR is not part of the AI Platform runtime in this setup. If ASR is required,
run it as external preprocessing: audio -> ASR -> text -> `/v1/decide`.

## Required env vars

```bash
LLM_POLICY_ENABLED=true
LLM_POLICY_PATH=llm_policy/llm-policy.cloudru.yaml
LLM_POLICY_PROFILE=cheap
LLM_POLICY_ALLOW_PLACEHOLDERS=false
LLM_API_KEY=<secret>
LLM_BASE_URL=https://foundation-models.api.cloud.ru/v1
LLM_PROVIDER=openai_compatible
LLM_MODEL=openai/gpt-oss-20b
LOG_USER_TEXT=false
```

`LLM_BASE_URL` must not include `/chat/completions`; `HttpLlmCaller` appends it
when sending the request.

## Security

- Store the API key only in env, secret manager, or systemd `EnvironmentFile`.
- Do not commit `.env`.
- Do not log raw user text. Keep `LOG_USER_TEXT=false` for UAT and production.

## Smoke checks

Run offline policy/bootstrap checks first:

```bash
python3 -m pytest tests/test_llm_policy_loader.py
python3 -m pytest tests/test_llm_bootstrap.py
python3 -m pytest tests/test_llm_runtime.py
python3 -m pytest tests/test_llm_tasks.py
```

Optional direct LLM smoke is manual-only on UAT with a real key. Use the
`extract_shopping_item_name()` path and keep raw request text out of logs.

## Service restart

```bash
sudo systemctl restart vr-ai-platform
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/ready
```

## Known limitations

- `top_p` and `presence_penalty` from Cloud.ru examples are not supported by
  `llm_policy` `CallSpec` or `HttpLlmCaller._build_body()` yet.
- This is not a UAT blocker for the current shopping extraction policy.
- If fine tuning of request parameters is needed, extend `CallSpec`, loader
  allowed keys, and `HttpLlmCaller._build_body()` in a separate task.

## Troubleshooting

- `timeout` on first smoke: check policy timeout values. Current Cloud.ru UAT
  defaults are `30000` ms for `cheap` and `45000` ms for `reliable`.
- `invalid_json`: cloud/open-weight models may return reasoning, prose, or
  markdown. Runtime now performs conservative JSON object extraction, while the
  HTTP caller and shopping prompt request JSON-only output.
- Numeric `quantity`: internal LLM output may contain numbers such as
  `"quantity": 2`; AI Platform normalizes quantity to a string before the
  DecisionDTO pipeline.
- ASR remains external preprocessing: audio -> ASR -> text -> `/v1/decide`.
