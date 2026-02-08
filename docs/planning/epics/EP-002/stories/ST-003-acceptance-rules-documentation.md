# ST-003: Document Acceptance Rules for Assist-Mode Hints

**Status:** Ready
**Epic:** `docs/planning/epics/EP-002/epic.md`
**Owner:** TBD

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Initiative | `docs/planning/initiatives/INIT-2026Q1-assist-mode.md` |
| Epic | `docs/planning/epics/EP-002/epic.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Description

The assist-mode initiative requires documented acceptance rules that describe how and when the deterministic baseline accepts or rejects each type of LLM hint. The rules are fully implemented in code but lack a human-readable documentation artifact.

**User value:** Developers, reviewers, and operators can understand the acceptance rules without reading source code. This is critical for auditing deterministic control guarantees and onboarding new team members.

## Acceptance Criteria

```gherkin
Scenario: Normalization acceptance rules are documented
  Given the documentation file exists at docs/contracts/assist-mode-acceptance-rules.md
  When a reader looks up normalization rules
  Then the document describes:
    - rejection when candidate text is empty
    - rejection when candidate length exceeds max(original_length * 2, 10)
    - rejection when no token overlap between original and candidate
    - on acceptance: re-detection of intent, re-extraction of item_name/task_title
  And each rule references the code location (file:function)

Scenario: Entity extraction acceptance rules are documented
  Given the documentation file exists
  When a reader looks up entity extraction rules
  Then the document describes:
    - entity hints apply only for intent=add_shopping_item when item_name is missing
    - agent hints have priority over LLM hints
    - item accepted only if lowercase text is substring of original text
    - agent candidate selection: allowlist filtering, capability matching, scoring/tiebreaking
  And each rule references the code location

Scenario: Clarify suggestor acceptance rules are documented
  Given the documentation file exists
  When a reader looks up clarify rules
  Then the document describes:
    - rejection when question is empty, <5 chars, or >200 chars
    - rejection when question contains original user text (echo prevention)
    - acceptance for known intents (add_shopping_item, create_task) if length checks pass
    - for unknown intents: require "?" in question
    - in v2 pipeline: missing_fields subset check before replacing default question
  And each rule references the code location

Scenario: Fallback behavior is documented
  Given the documentation file exists
  When a reader looks up error/timeout handling
  Then the document describes:
    - timeout mechanism (ThreadPoolExecutor, ASSIST_TIMEOUT_MS)
    - error -> None hint -> baseline proceeds without degradation
    - per-subsystem disable via feature flags
```

## Scope

### In scope

- Create `docs/contracts/assist-mode-acceptance-rules.md`
- Document acceptance/rejection rules for normalization, entity extraction, and clarify suggestor
- Document agent hint scoring and selection rules
- Document feature flags and their defaults
- Document error/timeout fallback behavior
- Reference code locations (file:function) for each rule

### Out of scope

- Code changes of any kind
- New tests
- Changes to existing acceptance rules
- Changes to public API contracts

## Test Strategy

### Verification

- Manual review: verify each documented rule matches the corresponding code function
- Checklist: every acceptance/rejection condition in `_can_accept_normalized_text`, `_pick_matching_item`, `_clarify_question_is_safe`, and `_clarify_question` is documented

## Flags

- contract_impact: no
- adr_needed: none
- diagrams_needed: none
- security_sensitive: no
- traceability_critical: no

## Blocked By

- None
