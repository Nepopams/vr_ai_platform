#!/usr/bin/env python3
"""Offline validation for Agent Platform v0 (privacy-safe, stdlib-only)."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict

from agent_registry.v0_loader import AgentRegistryV0Loader, load_capability_catalog


DANGEROUS_ALLOWLIST_KEYS = {
    "text",
    "user_text",
    "prompt",
    "output",
    "raw",
    "normalized_text",
    "question",
    "ui_message",
    "item_name",
}


@dataclass
class ValidationCounts:
    agents_total: int = 0
    agents_enabled_total: int = 0
    enabled_by_mode: Dict[str, int] = field(default_factory=lambda: {"shadow": 0, "assist": 0, "partial_trust": 0})
    catalog_capabilities_total: int = 0
    errors: Dict[str, int] = field(default_factory=dict)
    warnings: Dict[str, int] = field(default_factory=dict)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Agent Platform v0 (offline)")
    parser.add_argument("--registry", default="agent_registry/agent-registry-v0.yaml")
    parser.add_argument("--catalog", default="agent_registry/capabilities-v0.yaml")
    parser.add_argument("--report-json", default=None)
    parser.add_argument("--warnings-json", default=None)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def _inc(counter: Dict[str, int], key: str, value: int = 1) -> None:
    counter[key] = counter.get(key, 0) + value


def _validate(registry_path: Path, catalog_path: Path) -> tuple[ValidationCounts, int]:
    counts = ValidationCounts()
    try:
        registry = AgentRegistryV0Loader.load(
            path_override=str(registry_path),
            catalog_path_override=str(catalog_path),
        )
    except Exception:
        _inc(counts.errors, "registry_load_failed")
        return counts, 2

    try:
        catalog = load_capability_catalog(catalog_path_override=str(catalog_path))
    except Exception:
        _inc(counts.errors, "catalog_load_failed")
        return counts, 2

    counts.catalog_capabilities_total = len(catalog)

    if registry.registry_version != "v0":
        _inc(counts.errors, "invalid_registry_version")
    if registry.compat_adr != "ADR-005":
        _inc(counts.errors, "compat_adr_mismatch")

    seen_ids = set()
    duplicate_count = 0
    for agent in registry.agents:
        counts.agents_total += 1
        if agent.agent_id in seen_ids:
            duplicate_count += 1
        else:
            seen_ids.add(agent.agent_id)

        if agent.enabled:
            counts.agents_enabled_total += 1
            if agent.mode in counts.enabled_by_mode:
                counts.enabled_by_mode[agent.mode] += 1

        if not agent.capabilities:
            _inc(counts.errors, "missing_capability")
            continue
        capability_id = agent.capabilities[0].capability_id
        if capability_id not in catalog:
            _inc(counts.errors, "unknown_capability_id")

    if duplicate_count:
        _inc(counts.errors, "duplicate_agent_id", duplicate_count)

    if counts.agents_total == 0:
        _inc(counts.warnings, "empty_registry")

    if counts.agents_enabled_total > 0:
        _inc(counts.warnings, "enabled_agents_present", counts.agents_enabled_total)
        for mode, value in counts.enabled_by_mode.items():
            if value:
                _inc(counts.warnings, f"enabled_agents_{mode}", value)

    dangerous_hits = 0
    for entry in catalog.values():
        allowlist = entry.get("payload_allowlist") or set()
        if any(key in DANGEROUS_ALLOWLIST_KEYS for key in allowlist):
            dangerous_hits += 1
    if dangerous_hits:
        _inc(counts.errors, "dangerous_allowlist_keys_found", dangerous_hits)

    exit_code = 0
    if counts.errors:
        exit_code = 2
    elif counts.warnings:
        exit_code = 1
    return counts, exit_code


def _report_payload(counts: ValidationCounts, exit_code: int) -> Dict[str, object]:
    return {
        "files_checked": 2,
        "agents_total": counts.agents_total,
        "agents_enabled_total": counts.agents_enabled_total,
        "enabled_by_mode": counts.enabled_by_mode,
        "catalog_capabilities_total": counts.catalog_capabilities_total,
        "errors": counts.errors,
        "warnings": counts.warnings,
        "errors_count": sum(counts.errors.values()),
        "warnings_count": sum(counts.warnings.values()),
        "exit_code": exit_code,
    }


def _write_json(path: Path | None, payload: Dict[str, object]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _print_stdout(report: Dict[str, object]) -> None:
    print("agent platform validation (offline)")
    print(f"files_checked: {report.get('files_checked')}")
    print(f"agents_total: {report.get('agents_total')}")
    print(f"agents_enabled_total: {report.get('agents_enabled_total')}")
    enabled_by_mode = report.get("enabled_by_mode", {})
    print(
        "enabled_by_mode:"
        f" shadow={enabled_by_mode.get('shadow', 0)}"
        f" assist={enabled_by_mode.get('assist', 0)}"
        f" partial_trust={enabled_by_mode.get('partial_trust', 0)}"
    )
    print(f"catalog_capabilities_total: {report.get('catalog_capabilities_total')}")
    print(f"errors_count: {report.get('errors_count')}")
    print(f"warnings_count: {report.get('warnings_count')}")
    print(f"exit_code: {report.get('exit_code')}")


def _run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        registry_path = base / "registry.json"
        catalog_path = base / "catalog.json"
        secret = "SECRET_VALUE"

        valid_registry = {
            "registry_version": "v0",
            "compat": {"adr": "ADR-005", "note": "internal-only"},
            "agents": [
                {
                    "agent_id": secret,
                    "enabled": False,
                    "mode": "assist",
                    "capabilities": [
                        {
                            "capability_id": "extract_entities.shopping",
                            "allowed_intents": ["add_shopping_item"],
                        }
                    ],
                    "runner": {"kind": "python_module", "ref": "agents.baseline_shopping:run"},
                }
            ],
        }
        valid_catalog = {
            "catalog_version": "v0",
            "capabilities": [
                {
                    "capability_id": "extract_entities.shopping",
                    "purpose": "shopping",
                    "allowed_modes": ["assist"],
                    "risk_level": "low",
                    "payload_allowlist": ["items", "confidence"],
                    "contains_sensitive_text": True,
                }
            ],
        }
        registry_path.write_text(json.dumps(valid_registry), encoding="utf-8")
        catalog_path.write_text(json.dumps(valid_catalog), encoding="utf-8")

        counts, exit_code = _validate(registry_path, catalog_path)
        report = _report_payload(counts, exit_code)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            _print_stdout(report)
        output = buf.getvalue() + json.dumps(report, ensure_ascii=False)
        if secret in output:
            raise SystemExit("self-test failed: privacy leak detected")
        if report.get("exit_code") != 0:
            raise SystemExit("self-test failed: expected exit_code 0")

        invalid_catalog = {
            "catalog_version": "v0",
            "capabilities": [
                {
                    "capability_id": "extract_entities.shopping",
                    "purpose": "shopping",
                    "allowed_modes": ["assist"],
                    "risk_level": "low",
                    "payload_allowlist": ["text"],
                    "contains_sensitive_text": True,
                }
            ],
        }
        catalog_path.write_text(json.dumps(invalid_catalog), encoding="utf-8")
        counts, exit_code = _validate(registry_path, catalog_path)
        if exit_code != 2:
            raise SystemExit("self-test failed: expected exit_code 2 for dangerous allowlist keys")

        print("self-test ok")


def main() -> None:
    args = parse_args()
    if args.self_test:
        _run_self_test()
        return

    registry_path = Path(args.registry)
    catalog_path = Path(args.catalog)
    counts, exit_code = _validate(registry_path, catalog_path)
    report = _report_payload(counts, exit_code)

    report_path = Path(args.report_json) if args.report_json else None
    warnings_path = Path(args.warnings_json) if args.warnings_json else None
    _write_json(report_path, report)
    _write_json(warnings_path, counts.warnings)

    _print_stdout(report)
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
