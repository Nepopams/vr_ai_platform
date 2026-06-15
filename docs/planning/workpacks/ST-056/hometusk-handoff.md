# HomeTusk Handoff — Domain Planner v1 Contract + 50-Scenario Eval Gate

**Date:** 2026-06-15
**Provider repository:** AI Platform
**HomeTusk source package:** `C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/provider-domain-planner-v1-acceptance/`
**HomeTusk source revision read:** `b18bfdb6f0bdbf6044ad5b986aee837dca7bf5b3`
**Fixture suite:** `expanded-golden-scenarios-v1`
**Raw scenario text in this handoff:** No

---

## Provider Result

AI Platform provider-side Gate D is GO for the current initiative.

This result means:

- deterministic provider eval evidence exists for all 50 scenarios;
- blocker failure count is zero;
- unsupported/cross-household commands do not auto-execute;
- first-class `reject` is contract-supported and emitted for unsupported/unsafe provider outcomes;
- non-executing `confirm` is contract-supported, while runtime confirm UX remains a future integration concern;
- `answer` remains blocked;
- HomeTusk remains final runtime, guardrail, audit, execution, and product acceptance authority.

This result does not approve:

- HomeTusk `natural_command` runtime implementation;
- HomeTusk backend/OpenAPI/mobile changes;
- direct mobile/web calls to AI Platform;
- production rollout;
- broad household automation;
- assignment, reschedule, completion, payment, device control, or external order execution.

## 50-Scenario Eval Summary

| Metric | Value |
| --- | --- |
| Total scenarios | 50 |
| Evaluated scenarios | 50 |
| Skipped scenarios | 0 |
| Schema-valid decisions | 50 |
| Outcome matches | 50 |
| Intent matches | 20 |
| Unsupported auto-execute | 0 |
| Cross-household references | 0 |
| Blocker failure scenarios | 0 |
| Remaining non-blocker buckets | `wrong_intent=30`, `item_boundary_loss=2` |

Evidence report:

```text
docs/planning/workpacks/ST-052/local-50-scenario-eval-report.json
```

Run command:

```bash
$env:PYTHONPATH='.;.venv/Lib/site-packages'; python3 scripts/evaluate_domain_planner_seed.py --source-dir C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/ai-command-capabilities/provider-domain-planner-v1-acceptance/expanded-golden-scenarios-v1 --check-no-raw-text --output docs/planning/workpacks/ST-052/local-50-scenario-eval-report.json
```

## Contract Decisions

| Area | Decision |
| --- | --- |
| Contract version | `2.1.0` |
| First-class `reject` | Implemented in schema and runtime for non-executing unsupported/unsafe outcomes. |
| Non-executing `confirm` | Implemented in schema; runtime confirm emission remains future HomeTusk integration work. |
| `answer` | Blocked until HomeTusk read-model / answer contract governance starts. |
| Shopping plurality | Direct plural action not added; provider continues repeated singular `propose_add_shopping_item` actions. |
| `/v1/decide` | Remains provider decision endpoint; response schema-valid under `2.1.0`. |

## Privacy / Retention Posture

- Eval report uses scenario IDs, metadata, metrics, and buckets only.
- `--check-no-raw-text` passed on the regenerated 50-scenario report.
- Raw audio remains outside `/v1/decide`.
- ASR remains transcription-only and does not call `/v1/decide` automatically.
- Validation keeps logging-related feature flags disabled for eval runs.
- No HomeTusk files were modified or copied.

## Validation Evidence

| Check | Result |
| --- | --- |
| Focused tests | 33 passed, 1 warning |
| Full tests | 346 passed, 4 skipped, 1 warning |
| Contract checker | Pass |
| Schema-bump check | Pass |
| Release sanity | Pass through `python3 -m skills.release_sanity` |
| 50-scenario eval | Pass; zero blocker failures |
| Diff hygiene | Pass with LF-to-CRLF warnings only |

`make release-sanity` was not run because `make` is unavailable in the Windows environment; the equivalent direct Python entrypoint passed.

## Recommended Next HomeTusk Action

Review the provider handoff and decide whether to open a separate HomeTusk-owned runtime integration initiative. That future initiative should explicitly cover HomeTusk backend/API/mobile UX, guardrails, audit logging, confirmation UX, and product acceptance gates.
