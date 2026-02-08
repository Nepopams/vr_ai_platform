# WP / ST-003: Document acceptance rules for assist-mode hints

**Status:** Ready
**Story:** `docs/planning/epics/EP-002/stories/ST-003-acceptance-rules-documentation.md`
**Owner:** Codex (implementation) / Claude (prompts + review)

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q1-assist-mode.md` |
| Epic | `docs/planning/epics/EP-002/epic.md` |
| Story | `docs/planning/epics/EP-002/stories/ST-003-acceptance-rules-documentation.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

Produce a human-readable document describing all acceptance/rejection rules for assist-mode hints (normalization, entity extraction, clarify suggestor), with code references. This enables initiative AC2 ("правила документированы") and unblocks ST-004 (retroactive verification).

## Acceptance Criteria

1. **AC-1**: File `docs/contracts/assist-mode-acceptance-rules.md` exists.
2. **AC-2**: Normalization rules documented — rejection conditions, acceptance behavior, code references.
3. **AC-3**: Entity extraction rules documented — when hints apply, agent vs LLM priority, substring check, scoring.
4. **AC-4**: Clarify suggestor rules documented — length checks, echo prevention, intent-specific behavior, missing_fields subset check.
5. **AC-5**: Fallback behavior documented — timeout mechanism, error handling, feature flags.
6. **AC-6**: Every rule references a code location (`file:function`).

## Files to Change

### New files (create)

| File | Description |
|------|-------------|
| `docs/contracts/assist-mode-acceptance-rules.md` | Acceptance rules documentation |

### Modified files

None.

## Implementation Plan

### Step 1: Create acceptance rules document

**Commit:** `docs(assist-mode): add acceptance rules documentation`

Create `docs/contracts/assist-mode-acceptance-rules.md` with sections:

1. **Overview** — what assist-mode is, deterministic-first principle
2. **Feature flags** — table of all assist-mode flags with defaults
3. **Normalization acceptance rules** — rules from `_can_accept_normalized_text`
4. **Entity extraction acceptance rules** — rules from `_pick_matching_item`, agent hints
5. **Clarify suggestor acceptance rules** — rules from `_clarify_question_is_safe`, `_clarify_question`
6. **Agent hint scoring** — allowlist, capability match, scoring/tiebreaking
7. **Timeout & error handling** — ThreadPoolExecutor, ASSIST_TIMEOUT_MS, fallback behavior
8. **Code reference index** — table of all referenced functions

**Key code to read during PLAN:**
- `routers/assist/normalization.py` — `_can_accept_normalized_text`
- `routers/assist/entity_extraction.py` — `_pick_matching_item`
- `routers/assist/clarify.py` — `_clarify_question_is_safe`, `_clarify_question`
- `routers/assist/config.py` — feature flags and defaults
- `routers/assist/agent_hints.py` — agent hint scoring and selection
- `routers/v2.py` — where assist steps are called in pipeline

## Verification Commands

```bash
# 1. Document exists
test -f docs/contracts/assist-mode-acceptance-rules.md && echo "OK" || echo "MISSING"

# 2. Assist-mode tests still pass (no regressions)
python3 -m pytest tests/test_assist_mode.py tests/test_assist_agent_hints.py -v

# 3. Full suite
python3 -m pytest tests/ -v
```

## DoD Checklist

- [ ] Document created at `docs/contracts/assist-mode-acceptance-rules.md`
- [ ] All normalization rules documented with code refs
- [ ] All entity extraction rules documented with code refs
- [ ] All clarify rules documented with code refs
- [ ] Feature flags and defaults documented
- [ ] Timeout/error handling documented
- [ ] No code changes (docs-only story)

## Risks

| Risk | P | I | Mitigation |
|------|---|---|------------|
| Code functions may have undocumented edge cases | Low | Low | PLAN phase reads actual code, not assumptions |
| Line numbers shift after refactoring | Low | Low | Reference function names primarily, line numbers secondary |

## Rollback

1 new file. Rollback = delete it. No code/config/DB changes.

## APPLY Boundaries

### Allowed
- `docs/contracts/assist-mode-acceptance-rules.md` (create)

### Forbidden
- `routers/**` (do not modify)
- `app/**` (do not modify)
- `tests/**` (do not modify)
- Any code files
