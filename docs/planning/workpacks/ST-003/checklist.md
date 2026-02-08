# Checklist / ST-003: Document acceptance rules for assist-mode hints

**Story:** `docs/planning/epics/EP-002/stories/ST-003-acceptance-rules-documentation.md`
**DoD:** `docs/_governance/dod.md`

---

## Acceptance Criteria Verification

- [ ] **AC-1: Document exists**
  - File: `docs/contracts/assist-mode-acceptance-rules.md`

- [ ] **AC-2: Normalization rules**
  - Rejection: empty candidate, length exceeds max, no token overlap
  - Acceptance: re-detect intent, re-extract entities
  - Code ref: `_can_accept_normalized_text`

- [ ] **AC-3: Entity extraction rules**
  - When: intent=add_shopping_item, item_name missing
  - Agent > LLM priority
  - Substring check for items
  - Code refs: `_pick_matching_item`, agent hint functions

- [ ] **AC-4: Clarify suggestor rules**
  - Length checks (<5, >200)
  - Echo prevention
  - Intent-specific acceptance
  - missing_fields subset check in v2
  - Code refs: `_clarify_question_is_safe`, `_clarify_question`

- [ ] **AC-5: Fallback behavior**
  - Timeout mechanism, ASSIST_TIMEOUT_MS
  - Error → None → baseline proceeds
  - Feature flags table

- [ ] **AC-6: Code references**
  - Every rule references `file:function`

---

## Verification Commands

```bash
# 1. Document exists
test -f docs/contracts/assist-mode-acceptance-rules.md && echo "OK" || echo "MISSING"

# 2. Assist-mode tests pass
python3 -m pytest tests/test_assist_mode.py tests/test_assist_agent_hints.py -v

# 3. Full suite
python3 -m pytest tests/ -v
```

---

## Sign-off

- [ ] All AC verified
- [ ] All DoD criteria met
- [ ] Reviewer GO decision
