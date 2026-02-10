# Codex PLAN — ST-017: Contract Governance Runbook

## Role
You are a read-only explorer. NO edits, NO file writes, NO network access.

## Allowed commands (whitelist)
- `ls`, `find`
- `cat`, `head`, `tail`
- `rg`, `grep`
- `sed -n`

## Forbidden
- Any file modifications
- Any network access
- `git commit/push`
- Package installs

## STOP-THE-LINE
If anything below is unclear or missing — STOP and report, do not guess.

---

## Context

Story ST-017 creates `docs/contracts/CONTRACT-GOVERNANCE-RUNBOOK.md` — a developer-facing
operational guide for contract changes, sourced from ADR-001.

This is a **docs-only story** (no code changes). The PLAN phase verifies all referenced
artifacts exist and captures exact content needed for the runbook.

## Exploration Tasks

### Task 1: Verify ADR-001 breaking/non-breaking rules
```bash
cat docs/adr/ADR-001-contract-versioning-compatibility-policy.md
```
**Report:** List all items from section 3.1 (non-breaking) and section 3.2 (breaking) verbatim.

### Task 2: Verify all skill script paths exist
```bash
ls -la skills/contract-checker/scripts/validate_contracts.py
ls -la skills/schema-bump/scripts/check_breaking_changes.py
ls -la skills/schema-bump/scripts/bump_version.py
ls -la skills/graph-sanity/scripts/run_graph_suite.py
ls -la skills/decision-log-audit/scripts/audit_decision_logs.py
ls -la skills/release-sanity/scripts/release_sanity.py
```
**Report:** Confirm each file exists. Note any missing files.

### Task 3: Check bump_version.py CLI interface
```bash
head -50 skills/schema-bump/scripts/bump_version.py
```
**Report:** What CLI arguments does `bump_version.py` accept? (e.g., `--schema`, `--part`)

### Task 4: Check check_breaking_changes.py CLI interface
```bash
head -50 skills/schema-bump/scripts/check_breaking_changes.py
```
**Report:** What CLI arguments does it accept? (e.g., `--old`, `--new`)

### Task 5: Verify contracts/VERSION exists and value
```bash
cat contracts/VERSION
```
**Report:** Current version value.

### Task 6: Check if docs/contracts/ directory exists
```bash
ls docs/contracts/ 2>/dev/null || echo "Directory does not exist"
```
**Report:** Does the directory exist? Any existing files?

### Task 7: Check existing CI workflow for reference
```bash
cat .github/workflows/ci.yml
```
**Report:** List current CI step names and commands (for "CI Checks Explained" section).

### Task 8: Check release_sanity.py CHECKS list
```bash
sed -n '1,40p' skills/release-sanity/scripts/release_sanity.py
```
**Report:** What checks are in the CHECKS list? (names and script paths)

---

## Expected output format

For each task, report:
1. Task number and description
2. Findings (exact paths, content, CLI args)
3. Any issues or missing items

End with a summary: "All prerequisites verified" or list of blockers.
