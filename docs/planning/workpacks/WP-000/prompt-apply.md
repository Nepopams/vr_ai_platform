# WP-000 — APPLY Prompt (Implementation)

> **Mode: APPLY** — Implementation allowed.
> Create and modify files as specified below.
> **STOP-THE-LINE rule:** If any deviation from this plan is needed — STOP and report. Do NOT improvise.

---

## Anchor Block

Read these files FIRST:

```
cat docs/planning/workpacks/WP-000/workpack.md
cat docs/planning/workpacks/WP-000/checklist.md
cat .claude/rules/planning.md
cat docs/_governance/dor.md
cat docs/_governance/dod.md
```

---

## From PLAN Phase Verification

Key findings incorporated into this APPLY prompt:

- `setup-dev` target does NOT exist in Makefile — create it.
- `.github/` directory does NOT exist — create from scratch.
- `tests/conftest.py` does NOT exist — no naming conflicts with existing tests.
- `docs/planning/_templates/` does NOT exist — create from scratch.
- `docs/_indexes/initiatives-index.md` does NOT exist — create.
- Graph-sanity fixtures auto-discovered via `FIXTURE_DIR.glob("*.json")`, sorted. Any `*.json` works.
- Existing fixture command_id conventions: `cmd-graph-00X`, `cmd-10X`. New fixtures use `cmd-wp000-0XX`.
- Intent detection order: shopping checked FIRST (keywords: `куп`, `shopping`, `grocery`, `buy`, `add`), then task (`task`, `todo`, `сделай`, `сделать`, `нужно`, `починить`, `убраться`), then `clarify_needed`.
- Multi-intent text ("купи ... и убери ...") → shopping wins (checked first).
- Empty/whitespace text → clarify with `missing_fields=["text"]`, no crash.
- English "Buy apples" → shopping intent works (`buy` in keywords, `buy ` in extract patterns).
- ADR-005 duplicate safe to delete: no references outside WP-000 itself and the duplicate file.
- `contracts/VERSION` = `2.0.0` — do NOT touch.
- ADR index currently has legacy ADRs only (001-015), needs AI Platform ADRs (000-005) added.
- Existing tests use inline helpers, no `@pytest.fixture` — conftest.py won't conflict.

---

## APPLY Boundaries

### ALLOWED (create/modify)

```
.github/workflows/ci.yml                          (CREATE)
Makefile                                           (MODIFY)
README.md                                          (MODIFY)
tests/conftest.py                                  (CREATE)
docs/planning/_templates/epic.md                   (CREATE)
docs/planning/_templates/story.md                  (CREATE)
docs/planning/_templates/workpack.md               (CREATE)
docs/planning/_templates/sprint.md                 (CREATE)
docs/_indexes/initiatives-index.md                 (CREATE)
docs/_indexes/adr-index.md                         (MODIFY)
skills/graph-sanity/fixtures/commands/*.json        (CREATE new files only)
docs/adr/ADR-005: Внутренний контракт...           (DELETE)
```

### FORBIDDEN (do NOT touch)

```
contracts/schemas/*.json
contracts/VERSION
routers/**
graphs/**
app/**
llm_policy/**
agent_registry/**
agent_runner/**
docs/adr/ADR-0*.md (except deleting duplicate)
docs/planning/initiatives/**
docs/planning/releases/**
docs/planning/strategy/**
```

### INVARIANTS (verify after each commit)

- `python -m pytest tests/ -v` — 0 failures
- `python -m skills.contract_checker` — exit 0
- `python -m skills.schema_bump check` — exit 0
- `python -m skills.graph_sanity` — exit 0
- `contracts/VERSION` = `2.0.0`

---

## Step 1: Dev environment reproducibility

**Commit message:** `chore: add setup-dev target and update Quick Start`

### 1a. Modify `Makefile`

Add `setup-dev` target AFTER the existing `setup` target (line 4-5 area). Insert:

```makefile
setup-dev:
	pip install -e ".[dev]"
```

Also add `setup-dev` to the `.PHONY` line at the top.

### 1b. Modify `README.md`

Replace the current Quick Start section with:

```markdown
## Quick Start

Python 3.11+ is required.

```bash
make setup-dev   # install with dev dependencies (pytest)
make test        # run full test suite
make test-core   # run minimal suite (no API deps)
make run_graph   # run core graph with sample command
```
```

Keep all other sections unchanged.

### Verify Step 1:

```bash
grep "setup-dev" Makefile           # must exist
grep "setup-dev" README.md          # must exist
make setup-dev                      # must succeed
python -m pytest tests/test_contracts.py -v   # existing tests still pass
```

---

## Step 2: CI pipeline

**Commit message:** `ci: add GitHub Actions workflow for tests and contract validation`

### 2a. Create `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: Run tests
        run: python -m pytest tests/ -v --tb=short

      - name: Validate contracts
        run: python -m skills.contract_checker

      - name: Check schema version
        run: python -m skills.schema_bump check

      - name: Graph sanity
        run: python -m skills.graph_sanity
```

### Verify Step 2:

```bash
cat .github/workflows/ci.yml        # file exists, valid YAML
python -m pytest tests/ -v          # still passes
```

---

## Step 3: Golden dataset expansion

**Commit message:** `test: expand golden dataset to 14 fixtures covering all intents and edge cases`

Create 12 new JSON files in `skills/graph-sanity/fixtures/commands/`. Each must be valid against `contracts/schemas/command.schema.json`.

### 3a. `buy_milk.json` — shopping, single item, Russian

```json
{
  "command_id": "cmd-wp000-001",
  "user_id": "user-201",
  "timestamp": "2026-02-01T10:00:00+00:00",
  "text": "Купи молоко",
  "capabilities": ["start_job", "propose_create_task", "propose_add_shopping_item", "clarify"],
  "context": {
    "household": {
      "household_id": "house-201",
      "members": [{"user_id": "user-201", "display_name": "Анна"}],
      "shopping_lists": [{"list_id": "list-1", "name": "Продукты"}]
    },
    "defaults": {"default_list_id": "list-1"}
  }
}
```

### 3b. `buy_bread_and_eggs.json` — shopping, multi-item text

```json
{
  "command_id": "cmd-wp000-002",
  "user_id": "user-202",
  "timestamp": "2026-02-01T10:01:00+00:00",
  "text": "Купить хлеб и яйца",
  "capabilities": ["start_job", "propose_create_task", "propose_add_shopping_item", "clarify"],
  "context": {
    "household": {
      "household_id": "house-202",
      "members": [{"user_id": "user-202", "display_name": "Дима"}],
      "shopping_lists": [{"list_id": "list-2", "name": "Еженедельные"}]
    },
    "defaults": {"default_list_id": "list-2"}
  }
}
```

### 3c. `clean_bathroom.json` — task, explicit zone

```json
{
  "command_id": "cmd-wp000-003",
  "user_id": "user-203",
  "timestamp": "2026-02-01T10:02:00+00:00",
  "text": "Убраться в ванной",
  "capabilities": ["start_job", "propose_create_task", "propose_add_shopping_item", "clarify"],
  "context": {
    "household": {
      "household_id": "house-203",
      "members": [{"user_id": "user-203", "display_name": "Лена"}],
      "zones": [{"zone_id": "zone-bath", "name": "Ванная"}]
    },
    "defaults": {"default_assignee_id": "user-203"}
  }
}
```

### 3d. `fix_faucet.json` — task, repair type

```json
{
  "command_id": "cmd-wp000-004",
  "user_id": "user-204",
  "timestamp": "2026-02-01T10:03:00+00:00",
  "text": "Починить кран на кухне",
  "capabilities": ["start_job", "propose_create_task", "propose_add_shopping_item", "clarify"],
  "context": {
    "household": {
      "household_id": "house-204",
      "members": [{"user_id": "user-204", "display_name": "Макс"}],
      "zones": [{"zone_id": "zone-kitchen", "name": "Кухня"}]
    },
    "defaults": {"default_assignee_id": "user-204"}
  }
}
```

### 3e. `empty_text.json` — edge case, whitespace-only text

```json
{
  "command_id": "cmd-wp000-005",
  "user_id": "user-205",
  "timestamp": "2026-02-01T10:04:00+00:00",
  "text": "   ",
  "capabilities": ["start_job", "propose_create_task", "propose_add_shopping_item", "clarify"],
  "context": {
    "household": {
      "household_id": "house-205",
      "members": [{"user_id": "user-205", "display_name": "Коля"}]
    }
  }
}
```

### 3f. `unknown_intent.json` — edge case, ambiguous command

```json
{
  "command_id": "cmd-wp000-006",
  "user_id": "user-206",
  "timestamp": "2026-02-01T10:05:00+00:00",
  "text": "Что-то непонятное про погоду",
  "capabilities": ["start_job", "propose_create_task", "propose_add_shopping_item", "clarify"],
  "context": {
    "household": {
      "household_id": "house-206",
      "members": [{"user_id": "user-206", "display_name": "Саша"}]
    }
  }
}
```

### 3g. `minimal_context.json` — edge case, minimal household (members only)

```json
{
  "command_id": "cmd-wp000-007",
  "user_id": "user-207",
  "timestamp": "2026-02-01T10:06:00+00:00",
  "text": "Сделай что-нибудь полезное",
  "capabilities": ["start_job", "propose_create_task", "propose_add_shopping_item", "clarify"],
  "context": {
    "household": {
      "members": [{"user_id": "user-207"}]
    }
  }
}
```

### 3h. `shopping_no_list.json` — shopping, no shopping_lists in context

```json
{
  "command_id": "cmd-wp000-008",
  "user_id": "user-208",
  "timestamp": "2026-02-01T10:07:00+00:00",
  "text": "Купи бананы",
  "capabilities": ["start_job", "propose_create_task", "propose_add_shopping_item", "clarify"],
  "context": {
    "household": {
      "household_id": "house-208",
      "members": [{"user_id": "user-208", "display_name": "Вера"}]
    }
  }
}
```

### 3i. `task_no_zones.json` — task, no zones in context

```json
{
  "command_id": "cmd-wp000-009",
  "user_id": "user-209",
  "timestamp": "2026-02-01T10:08:00+00:00",
  "text": "Нужно помыть окна",
  "capabilities": ["start_job", "propose_create_task", "propose_add_shopping_item", "clarify"],
  "context": {
    "household": {
      "household_id": "house-209",
      "members": [{"user_id": "user-209", "display_name": "Петя"}]
    }
  }
}
```

### 3j. `buy_apples_en.json` — shopping, English text

```json
{
  "command_id": "cmd-wp000-010",
  "user_id": "user-210",
  "timestamp": "2026-02-01T10:09:00+00:00",
  "text": "Buy apples and oranges",
  "capabilities": ["start_job", "propose_create_task", "propose_add_shopping_item", "clarify"],
  "context": {
    "household": {
      "household_id": "house-210",
      "members": [{"user_id": "user-210", "display_name": "Alex"}],
      "shopping_lists": [{"list_id": "list-en", "name": "Groceries"}]
    },
    "defaults": {"default_list_id": "list-en"}
  }
}
```

### 3k. `multiple_tasks.json` — multi-intent (shopping wins, checked first)

```json
{
  "command_id": "cmd-wp000-011",
  "user_id": "user-211",
  "timestamp": "2026-02-01T10:10:00+00:00",
  "text": "Купи молоко и убери кухню",
  "capabilities": ["start_job", "propose_create_task", "propose_add_shopping_item", "clarify"],
  "context": {
    "household": {
      "household_id": "house-211",
      "members": [{"user_id": "user-211", "display_name": "Катя"}],
      "zones": [{"zone_id": "zone-kitchen", "name": "Кухня"}],
      "shopping_lists": [{"list_id": "list-3", "name": "Продукты"}]
    },
    "defaults": {"default_list_id": "list-3", "default_assignee_id": "user-211"}
  }
}
```

### 3l. `add_sugar_ru.json` — shopping via "добавь" pattern

```json
{
  "command_id": "cmd-wp000-012",
  "user_id": "user-212",
  "timestamp": "2026-02-01T10:11:00+00:00",
  "text": "Добавь сахар в список покупок",
  "capabilities": ["start_job", "propose_create_task", "propose_add_shopping_item", "clarify"],
  "context": {
    "household": {
      "household_id": "house-212",
      "members": [{"user_id": "user-212", "display_name": "Миша"}],
      "shopping_lists": [{"list_id": "list-4", "name": "Продукты"}]
    },
    "defaults": {"default_list_id": "list-4"}
  }
}
```

### Verify Step 3:

```bash
ls skills/graph-sanity/fixtures/commands/*.json | wc -l   # expected: 14
python -m skills.graph_sanity                               # must exit 0
python -m pytest tests/test_router_golden_like.py -v        # must pass
```

---

## Step 4: Shared pytest fixtures

**Commit message:** `test: add shared pytest fixtures in conftest.py`

### 4a. Create `tests/conftest.py`

```python
"""Shared pytest fixtures for HomeTask AI Platform tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
SCHEMA_DIR = BASE_DIR / "contracts" / "schemas"


@pytest.fixture()
def command_schema() -> Dict[str, Any]:
    """Load CommandDTO JSON schema."""
    return json.loads(
        (SCHEMA_DIR / "command.schema.json").read_text(encoding="utf-8")
    )


@pytest.fixture()
def decision_schema() -> Dict[str, Any]:
    """Load DecisionDTO JSON schema."""
    return json.loads(
        (SCHEMA_DIR / "decision.schema.json").read_text(encoding="utf-8")
    )


@pytest.fixture()
def household_context() -> Dict[str, Any]:
    """Full household context with members, zones, and shopping lists."""
    return {
        "household": {
            "household_id": "house-test-001",
            "members": [
                {"user_id": "user-test-001", "display_name": "Тест Юзер"}
            ],
            "zones": [
                {"zone_id": "zone-kitchen", "name": "Кухня"},
                {"zone_id": "zone-bath", "name": "Ванная"},
            ],
            "shopping_lists": [
                {"list_id": "list-test-001", "name": "Продукты"}
            ],
        },
        "defaults": {
            "default_assignee_id": "user-test-001",
            "default_list_id": "list-test-001",
        },
    }


@pytest.fixture()
def minimal_context() -> Dict[str, Any]:
    """Minimal valid context — only required fields."""
    return {
        "household": {
            "members": [{"user_id": "user-test-min"}]
        }
    }


@pytest.fixture()
def valid_command(household_context: Dict[str, Any]) -> Dict[str, Any]:
    """Minimal valid CommandDTO with full context."""
    return {
        "command_id": "cmd-test-001",
        "user_id": "user-test-001",
        "timestamp": "2026-01-01T12:00:00+00:00",
        "text": "Тестовая команда",
        "capabilities": [
            "start_job",
            "propose_create_task",
            "propose_add_shopping_item",
            "clarify",
        ],
        "context": household_context,
    }


@pytest.fixture()
def valid_command_shopping(household_context: Dict[str, Any]) -> Dict[str, Any]:
    """CommandDTO that triggers add_shopping_item intent."""
    return {
        "command_id": "cmd-test-shop-001",
        "user_id": "user-test-001",
        "timestamp": "2026-01-01T12:00:00+00:00",
        "text": "Купи молоко",
        "capabilities": [
            "start_job",
            "propose_create_task",
            "propose_add_shopping_item",
            "clarify",
        ],
        "context": household_context,
    }


@pytest.fixture()
def valid_command_task(household_context: Dict[str, Any]) -> Dict[str, Any]:
    """CommandDTO that triggers create_task intent."""
    return {
        "command_id": "cmd-test-task-001",
        "user_id": "user-test-001",
        "timestamp": "2026-01-01T12:00:00+00:00",
        "text": "Убери кухню",
        "capabilities": [
            "start_job",
            "propose_create_task",
            "propose_add_shopping_item",
            "clarify",
        ],
        "context": household_context,
    }
```

### Verify Step 4:

```bash
python -m pytest tests/ -v --tb=short    # all tests still pass, no conflicts
python -c "import tests.conftest"         # importable
```

---

## Step 5: Planning templates

**Commit message:** `docs: add planning templates for epic, story, workpack, sprint`

Create directory `docs/planning/_templates/` and 4 files.

### 5a. `docs/planning/_templates/epic.md`

```markdown
# EP-XXX: [Epic Title]

**Status:** Draft | Ready | In Progress | Done
**Initiative:** `docs/planning/initiatives/INIT-YYYYQN-slug.md`
**Owner:** TBD

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Context

[Why this epic exists. Link to initiative.]

## Goal

[What this epic delivers. 1-3 sentences.]

## Scope

### In scope

- [item]

### Out of scope

- [item]

## Stories

| Story ID | Title | Status | Flags |
|----------|-------|--------|-------|
| ST-XXX | [title] | Draft | contract_impact=no, adr_needed=none |

## Dependencies

- [dependency]

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| [risk] | Low/Med/High | Low/Med/High | [mitigation] |

## Flags

- contract_impact: no
- adr_needed: none
- diagrams_needed: none
```

### 5b. `docs/planning/_templates/story.md`

```markdown
# ST-XXX: [Story Title]

**Status:** Draft | Ready | In Progress | Done
**Epic:** `docs/planning/epics/EP-XXX/epic.md`
**Owner:** TBD

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Epic | `docs/planning/epics/EP-XXX/epic.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Description

[What this story delivers. User value. Expected behavior.]

## Acceptance Criteria

```gherkin
Given [precondition]
When [action]
Then [expected result]
And [additional check]
```

## Scope

### In scope

- [item]

### Out of scope

- [item]

## Test Strategy

### Unit tests

- [class/method to test]

### Integration tests

- [endpoint/flow to test]

### Test data

- [fixtures/datasets needed]

## Flags

- contract_impact: no | yes
- adr_needed: none | lite | full
- diagrams_needed: none | update | new
- security_sensitive: no | yes
- traceability_critical: no | yes

## Blocked By

- [blocker or "None"]
```

### 5c. `docs/planning/_templates/workpack.md`

```markdown
# WP / ST-XXX: [Workpack Title]

**Status:** Draft | Ready
**Story:** `docs/planning/epics/EP-XXX/stories/ST-XXX-slug.md`
**Owner:** Codex (implementation) / Claude (prompts + review)

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| Story | `docs/planning/epics/EP-XXX/stories/ST-XXX-slug.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Outcome

[What this workpack delivers. 1-3 sentences.]

## Acceptance Criteria

1. [Testable condition]
2. [Testable condition]

## Files to Change

### New files (create)

| File | Description |
|------|-------------|

### Modified files (update)

| File | Change |
|------|--------|

### Deleted files

| File | Reason |
|------|--------|

## Implementation Plan (commit-sized)

### Step 1: [title]

**Commit:** "[type]: [message]"

[Details]

## Verification Commands

```bash
[commands]
```

## Tests

| Test | Checks | Expected |
|------|--------|----------|

## DoD Checklist

- [ ] [item]

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|

## Rollback

- [how to revert]

## APPLY Boundaries

### Allowed

- [paths]

### Forbidden

- [paths]
```

### 5d. `docs/planning/_templates/sprint.md`

```markdown
# Sprint SXX: [Sprint Goal]

**PI:** [PI ID or "standalone"]
**Period:** YYYY-MM-DD — YYYY-MM-DD
**Status:** Planning | Active | Done

---

## Sources of Truth

| Artifact | Path |
|----------|------|
| Product goal | `docs/planning/strategy/product-goal.md` |
| Scope anchor | `docs/planning/releases/MVP.md` |
| DoR | `docs/_governance/dor.md` |
| DoD | `docs/_governance/dod.md` |

---

## Sprint Goal

[1-2 sentences: what this sprint achieves.]

## Committed Scope

| Story ID | Title | Epic | Status | Owner |
|----------|-------|------|--------|-------|
| ST-XXX | [title] | EP-XXX | Ready | TBD |

## Stretch

| Story ID | Title | Condition |
|----------|-------|-----------|
| ST-XXX | [title] | [when to pull in] |

## Out of Scope (explicit)

- [item — why excluded]

## Capacity Notes

- [team size, availability, buffer %]

## Dependencies

- [external dependency]

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation | ROAM |
|------|-------------|--------|------------|------|
| [risk] | Low/Med/High | Low/Med/High | [mitigation] | Resolved/Owned/Accepted/Mitigated |

## Gate Ask (Gate B)

[What decision is being requested from PO. E.g., "Approve sprint goal + committed scope."]
```

### Verify Step 5:

```bash
ls docs/planning/_templates/*.md | wc -l             # expected: 4
grep -l "Sources of Truth" docs/planning/_templates/*.md | wc -l   # expected: 4
```

---

## Step 6: Indexes and ADR cleanup

**Commit message:** `docs: add initiatives index, update ADR index, remove ADR-005 duplicate`

### 6a. Create `docs/_indexes/initiatives-index.md`

```markdown
# Initiatives Index

This index tracks all initiatives in the project. Update when creating new initiatives.

## Index

| ID | Title | Priority | Period | Status | Link |
|----|-------|----------|--------|--------|------|
| INIT-2026Q1-shadow-router | Shadow LLM-router и метрики | High | 2026Q1 | Proposed | [Link](../planning/initiatives/INIT-2026Q1-shadow-router.md) |
| INIT-2026Q1-assist-mode | Assist-режим | Medium | 2026Q1 | Proposed | [Link](../planning/initiatives/INIT-2026Q1-assist-mode.md) |
| INIT-2026Q2-partial-trust | Partial Trust для add_shopping_item | Medium | 2026Q2 | Proposed | [Link](../planning/initiatives/INIT-2026Q2-partial-trust.md) |
| INIT-2026Q2-multi-entity-extraction | Поддержка множественных сущностей | Medium | 2026Q2 | Proposed | [Link](../planning/initiatives/INIT-2026Q2-multi-entity-extraction.md) |
| INIT-2026Q2-improved-clarify | Улучшение вопросов Clarify | Medium | 2026Q2 | Proposed | [Link](../planning/initiatives/INIT-2026Q2-improved-clarify.md) |
| INIT-2026Q3-semver-and-ci | SemVer и CI-контроль контрактов | Low | 2026Q3 | Proposed | [Link](../planning/initiatives/INIT-2026Q3-semver-and-ci.md) |
| INIT-2026Q3-codex-integration | Интеграция с Codex-пайплайном | Low | 2026Q3 | Proposed | [Link](../planning/initiatives/INIT-2026Q3-codex-integration.md) |
| INIT-2026Q3-agent-registry-integration | Интеграция агентной платформы v0 | Low | 2026Q3 | Proposed | [Link](../planning/initiatives/INIT-2026Q3-agent-registry-integration.md) |

---

**Maintenance**: Update this index when creating or closing initiatives.
```

### 6b. Modify `docs/_indexes/adr-index.md`

Add AI Platform ADRs (000-005) to the existing table. Insert these rows AFTER the existing ADR-015 row (keep all existing rows intact):

```markdown
| ADR-000 | AI Platform — Contract-first Intent → Decision Engine | accepted | 2025-12-XX | [Link](../adr/ADR-000-ai-platform-intent-decision-engine.md) |
| ADR-001-P | Contract versioning & compatibility policy (Platform) | accepted | 2026-01-XX | [Link](../adr/ADR-001-contract-versioning-compatibility-policy.md) |
| ADR-002-P | Agent model & execution boundaries (MVP) | accepted | 2026-01-XX | [Link](../adr/ADR-002-agent-model-execution-boundaries-mvp.md) |
| ADR-003-P | LLM model policy registry & escalation | proposed | 2026-01-12 | [Link](../adr/ADR-003-llm-model-policy-registry-and-escalation.md) |
| ADR-004-P | Partial Trust corridor | draft | 2026-01-XX | [Link](../adr/ADR-004-partial-trust-corridor.md) |
| ADR-005-P | Internal Agent Contract v0 (ABI) | accepted | 2026-01-XX | [Link](../adr/ADR-005-internal-agent-contract-v0.md) |
```

Note: Use suffix `-P` for Platform ADRs to distinguish from legacy HomeTusk ADRs that share similar numbering.

### 6c. Delete ADR-005 duplicate

```bash
rm "docs/adr/ADR-005: Внутренний контракт агента v0 как ABI платформы.md"
```

Verify canonical file still exists:

```bash
ls docs/adr/ADR-005-internal-agent-contract-v0.md   # must exist
ls docs/adr/ADR-005*                                  # must show exactly 1 file
```

### Verify Step 6:

```bash
ls docs/_indexes/initiatives-index.md                  # exists
wc -l docs/_indexes/initiatives-index.md               # non-empty
grep "ADR-000" docs/_indexes/adr-index.md              # present
ls docs/adr/ADR-005* | wc -l                           # exactly 1
```

---

## Final Verification (run ALL after all steps)

```bash
# 1. All tests pass
python -m pytest tests/ -v --tb=short

# 2. Contract validation
python -m skills.contract_checker

# 3. Schema version
python -m skills.schema_bump check

# 4. Graph sanity (with 14 fixtures)
python -m skills.graph_sanity

# 5. Release sanity
python -m skills.release_sanity

# 6. Fixture count
ls skills/graph-sanity/fixtures/commands/*.json | wc -l
# Expected: 14 (2 existing + 12 new)

# 7. Template count
ls docs/planning/_templates/*.md | wc -l
# Expected: 4

# 8. ADR-005 single file
ls docs/adr/ADR-005* | wc -l
# Expected: 1

# 9. Invariants
cat contracts/VERSION
# Expected: 2.0.0

# 10. No forbidden files changed
git diff --name-only contracts/ routers/ graphs/ app/ llm_policy/ agent_registry/
# Expected: empty (no changes)
```

---

## STOP-THE-LINE Triggers

If ANY of these occur during implementation, STOP and report:

- Any existing test fails after your changes
- `python -m skills.graph_sanity` fails on a new fixture
- `python -m skills.contract_checker` fails
- You need to modify a file in the FORBIDDEN list
- A new fixture causes `process_command()` to raise an exception
- `conftest.py` fixture names collide with existing test helpers
- Any other deviation from this plan

Do NOT attempt to fix by modifying forbidden files. STOP and report the issue.
