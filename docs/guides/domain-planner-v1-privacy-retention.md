# Domain Planner v1 Privacy and Retention Posture

**Status:** ST-048 artifact gate output
**Date:** 2026-06-15
**Initiative:** `INIT-2026Q3-domain-planner-v1-narrow-household-command-corridor`

---

## Boundary

Domain Planner v1 may receive only reviewed command text and minimal household context required for the allowed capabilities. It must not receive raw audio, tokens, secrets, invite links, device tokens, emails, private comments, unrelated household history, or cross-household data.

ASR remains a separate transcription-only capability. `/v1/asr/transcribe` must not call `/v1/decide` automatically.

## Current AI Platform Logging Facts

| Area | Current behavior | Gate decision |
| --- | --- | --- |
| Decision log | `append_decision_log(decision)` writes DecisionDTO to `logs/decisions.jsonl` by default. | Allowed if DecisionDTO contains no raw prompt/LLM output and remains schema-valid. |
| Raw command text log | `append_decision_text(command, trace_id)` writes `command.text` only when `LOG_USER_TEXT` is explicitly enabled. Default is `false`. | HOLD for production planner flows unless privacy/security explicitly approves it. |
| ASR log | ASR safe metadata log excludes transcript/audio/raw user text by design. | Must remain separate from planner flow. |
| Eval reports | Existing eval patterns should emit metrics and IDs rather than raw text. | Required for ST-049/ST-051. |

## Required Answers

| Question | Current answer | Status |
| --- | --- | --- |
| Does AI Platform retain prompts and responses? | It retains DecisionDTO logs by default. Raw command text is opt-in through `LOG_USER_TEXT=false` default. Future LLM prompt/response retention is not defined. | Partial; prompt/response retention HOLD before production. |
| What retention period applies? | No retention period is defined in the repo for decision logs, text logs, traces, or eval logs. | HOLD. |
| Can HomeTusk request zero-data-retention behavior? | No repo-level provider policy is defined. | HOLD. |
| Are prompts/responses used for model training? | No training use is defined in this repo; external provider terms are not captured here. | HOLD if external LLM is used. |
| Where are logs stored by region? | Local file paths are defined; production region/storage is not defined. | HOLD. |
| Who can access raw prompt/response logs? | Access policy is not defined in this repo. | HOLD. |
| How are deletion requests handled? | Deletion workflow is not defined. | HOLD. |
| How are eval fixture runs retained? | ST-049 must define report paths and retention expectations. Reports should avoid raw scenario text. | Pending ST-049. |

## Planner Data Rules

- Use reviewed text only; never raw audio.
- Keep `LOG_USER_TEXT=false` for planner validation and production-like runs unless a separate privacy/security gate approves otherwise.
- Do not include raw scenario text in planning reports, review reports, eval summaries, or handoff notes.
- Use scenario IDs, fixture source metadata, mapped outcome, failure buckets, and metrics in reports.
- Keep prompt/model/provider provenance in trace metadata or logs only if it does not add raw prompt/response content.
- If an external LLM is used later, record provider, model, prompt version, retention posture, and training-use policy before Gate C.

## Gate Requirements For Later Stories

ST-049 must define:

- fixture source metadata;
- eval output path;
- report redaction rules;
- whether fixture text is copied into this repository or referenced read-only.

ST-050 must verify:

- no raw text in planner logs by default;
- no raw LLM output in logs;
- ASR does not call `/v1/decide`;
- unsafe/cross-household/unsupported scenarios do not execute.

ST-051 must review:

- privacy posture evidence;
- eval report redaction;
- any remaining HOLD items before Gate D.
