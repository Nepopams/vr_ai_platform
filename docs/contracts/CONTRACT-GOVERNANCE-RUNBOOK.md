# Contract Governance Runbook

> Operational guide for making contract changes in vr_ai_platform.
> Sourced from [ADR-001](../adr/ADR-001-contract-versioning-compatibility-policy.md).

---

## 1. Breaking vs Non-Breaking Classification

### Non-breaking (allowed in MINOR/PATCH)

- Добавление необязательного поля (optional) в CommandDTO или DecisionDTO
- Добавление нового значения в расширяемые enums/union при соблюдении правил обработки неизвестного
- Добавление нового типа action если продукт обязан обрабатывать unknown actions безопасно (fallback)
- Расширение объекта context новыми optional подсекциями
- Добавление новых metadata полей (trace, latency_ms, prompt_version) как optional

### Breaking (requires MAJOR)

- Удаление поля
- Переименование поля
- Изменение типа поля (string → object, number → string, и т.п.)
- Изменение семантики поля так, что старый потребитель будет работать неверно
- Перевод optional → required
- Сужение допустимых значений (например, раньше принимали любой string, теперь enum)

> Source: ADR-001 sections 3.1 and 3.2.

---

## 2. Non-Breaking Change Workflow

When adding an optional field, extending enums, or adding optional metadata:

1. **Classify** — confirm the change is non-breaking per section 1 above
2. **Edit schema** — modify `contracts/schemas/command.schema.json` or `contracts/schemas/decision.schema.json`
3. **Update fixtures** — add/update fixtures in `skills/contract-checker/fixtures/` to cover the new field
4. **Run validate_contracts locally:**
   ```bash
   python3 skills/contract-checker/scripts/validate_contracts.py
   ```
5. **Run schema_bump check locally:**
   ```bash
   python3 skills/schema-bump/scripts/check_breaking_changes.py --old contracts/schemas/command.schema.json --new contracts/schemas/command.schema.json
   ```
   (Substitute the appropriate schema file. Expect: "No breaking changes detected.")
6. **Bump version** — MINOR for new functionality, PATCH for fix:
   ```bash
   # Edit contracts/VERSION directly:
   # e.g., 2.0.0 → 2.1.0 (minor) or 2.0.0 → 2.0.1 (patch)
   ```
7. **Update baseline** — if `contracts/schemas/.baseline/` exists, copy updated schemas there
8. **Submit PR** — include the PR checklist from section 6 below

---

## 3. Breaking Change Workflow

When removing a field, changing a type, renaming, or making optional → required:

1. **Confirm necessity** — is there no non-breaking alternative?
2. **Reference or create ADR** — document the rationale (link to existing ADR or create new one)
3. **Edit schema** — make the change in `contracts/schemas/*.schema.json`
4. **Bump MAJOR version:**
   ```bash
   # Edit contracts/VERSION:
   # e.g., 2.0.0 → 3.0.0
   ```
5. **Update baseline** — copy new schemas to `contracts/schemas/.baseline/`
6. **Update all fixtures** — ensure fixtures in `skills/contract-checker/fixtures/` match new schema
7. **Document migration** — describe how consumers should adapt (per ADR-001 section 6)
8. **Request approval** — breaking changes require explicit approval from contract owner before merge
9. **Submit PR** — include ADR reference and the PR checklist from section 6

---

## 4. Version Bump Procedure

### Where the version lives

- File: `contracts/VERSION` (current: 2.0.0)
- This value is returned as `schema_version` in every DecisionDTO

### When to bump

| Change type | Bump | Example |
|-------------|------|---------|
| Bug fix in schema description | PATCH | 2.0.0 → 2.0.1 |
| New optional field or capability | MINOR | 2.0.0 → 2.1.0 |
| Removed/renamed field, type change | MAJOR | 2.0.0 → 3.0.0 |

### How to bump

Edit `contracts/VERSION` directly — it's a plain text file with `MAJOR.MINOR.PATCH`.

The `bump_version.py` script bumps versions inside JSON schemas (the `x-version` field):
```bash
python3 skills/schema-bump/scripts/bump_version.py --schema contracts/schemas/command.schema.json --part minor
```
CLI args: `--schema` (path to JSON schema), `--part` (major|minor|patch).

### Baseline update

If `contracts/schemas/.baseline/` exists, copy the updated schemas there after bumping:
```bash
cp contracts/schemas/command.schema.json contracts/schemas/.baseline/
cp contracts/schemas/decision.schema.json contracts/schemas/.baseline/
```

---

## 5. CI Checks Explained

| Check | Script | What it validates | Local command | Common failures |
|-------|--------|-------------------|---------------|-----------------|
| **validate_contracts** | `skills/contract-checker/scripts/validate_contracts.py` | Fixtures match JSON schemas (Draft 2020-12) | `python3 skills/contract-checker/scripts/validate_contracts.py` | Fixture has extra/missing fields → fix fixture or schema |
| **check_breaking_changes** | `skills/schema-bump/scripts/check_breaking_changes.py` | No breaking changes between old and new schemas | `python3 skills/schema-bump/scripts/check_breaking_changes.py --old <old> --new <new>` | "BREAKING: Removed required field" → bump MAJOR |
| **graph_sanity** | `skills/graph-sanity/scripts/run_graph_suite.py` | Fixture commands produce valid DecisionDTOs | `python3 skills/graph-sanity/scripts/run_graph_suite.py` | DecisionDTO fails schema validation → fix graph output |
| **decision_log_audit** | `skills/decision-log-audit/scripts/audit_decision_logs.py` | JSONL decision logs validate against decision schema | `python3 skills/decision-log-audit/scripts/audit_decision_logs.py` | Log entry invalid JSON or schema violation → fix log format |
| **release_sanity** | `skills/release-sanity/scripts/release_sanity.py` | Orchestrator: runs contract-checker + decision-log-audit + graph-sanity | `python3 skills/release-sanity/scripts/release_sanity.py` | Sub-check fails → see individual check above |

---

## 6. PR Checklist for Contract Changes

Copy this checklist into your PR description:

```
- [ ] Change classified as breaking / non-breaking (see runbook section 1)
- [ ] JSON schema updated (`contracts/schemas/`)
- [ ] Fixtures updated (`skills/contract-checker/fixtures/`)
- [ ] Version bumped in `contracts/VERSION`
- [ ] Baseline updated (`contracts/schemas/.baseline/`) if exists
- [ ] Local CI checks pass (`validate_contracts`, `check_breaking_changes`, `graph_sanity`)
- [ ] ADR created/referenced (if breaking change)
- [ ] Migration documented (if breaking change)
```
