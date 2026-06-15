"""Privacy-safe evaluator for HomeTusk Domain Planner v1 seed fixtures."""

from __future__ import annotations

import argparse
import ast
import copy
import json
import os
import re
import subprocess
import sys
from collections import Counter
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Set

from jsonschema import ValidationError, validate

try:
    import yaml
except ImportError:  # pragma: no cover - covered through environments without PyYAML
    yaml = None


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_DIR = Path(
    "C:/Users/user/Documents/projects/hometusk/hometusk/docs/research/"
    "ai-command-capabilities/domain-planner-v1-gate/golden-scenarios-fixtures-v0"
)
COMMAND_SCHEMA_PATH = REPO_ROOT / "contracts" / "schemas" / "command.schema.json"
DECISION_SCHEMA_PATH = REPO_ROOT / "contracts" / "schemas" / "decision.schema.json"
SCENARIO_FIXTURE_FILENAMES = (
    "golden-scenarios-v1.yaml",
    "golden-scenarios-v0.yaml",
)
CONTEXT_FIXTURE_FILENAMES = (
    "context-fixtures-v1.yaml",
    "context-fixtures-v0.yaml",
)

CURRENT_CAPABILITIES = [
    "start_job",
    "propose_create_task",
    "propose_add_shopping_item",
    "clarify",
    "reject",
]

FEATURE_FLAG_NAMES = [
    "DECISION_ROUTER_STRATEGY",
    "LOG_USER_TEXT",
    "PIPELINE_LATENCY_LOG_ENABLED",
    "FALLBACK_METRICS_LOG_ENABLED",
    "SHADOW_ROUTER_ENABLED",
    "ASSIST_MODE_ENABLED",
    "PARTIAL_TRUST_ENABLED",
    "LLM_POLICY_ENABLED",
]

EVAL_ENV_OVERRIDES = {
    "LOG_USER_TEXT": "false",
    "PIPELINE_LATENCY_LOG_ENABLED": "false",
    "FALLBACK_METRICS_LOG_ENABLED": "false",
    "SHADOW_ROUTER_ENABLED": "false",
    "ASSIST_MODE_ENABLED": "false",
    "PARTIAL_TRUST_ENABLED": "false",
}

BLOCKER_BUCKETS = {
    "schema_invalid",
    "wrong_outcome",
    "unsupported_auto_execute",
    "cross_household_reference",
    "unsafe_assignment_not_rejected",
    "answer_mutates_state",
}


DecisionFn = Callable[[Dict[str, Any]], Dict[str, Any]]


def load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Required fixture file not found: {path}")
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text) if yaml is not None else load_simple_yaml(text)
    if not isinstance(data, dict):
        raise ValueError(f"Fixture file must contain a YAML mapping: {path}")
    return data


def load_simple_yaml(text: str) -> Any:
    """Parse the basic YAML subset used by HomeTusk fixture files."""
    lines = [strip_yaml_comment(line.rstrip()) for line in text.splitlines()]
    value, index = parse_yaml_block(lines, 0, 0)
    while index < len(lines) and not lines[index].strip():
        index += 1
    if index != len(lines):
        raise ValueError("Unsupported YAML structure in fixture file.")
    return value


def strip_yaml_comment(line: str) -> str:
    quote: Optional[str] = None
    escaped = False
    for index, char in enumerate(line):
        if quote:
            if char == "\\" and quote == '"' and not escaped:
                escaped = True
                continue
            if char == quote and not escaped:
                quote = None
            escaped = False
            continue
        if char in {"'", '"'}:
            quote = char
            continue
        if char == "#" and (index == 0 or line[index - 1].isspace()):
            return line[:index].rstrip()
    return line


def yaml_indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def parse_yaml_block(lines: List[str], index: int, indent: int) -> tuple[Any, int]:
    while index < len(lines) and not lines[index].strip():
        index += 1
    if index >= len(lines) or yaml_indent(lines[index]) < indent:
        return None, index
    stripped = lines[index].strip()
    if stripped.startswith("-"):
        return parse_yaml_sequence(lines, index, indent)
    return parse_yaml_mapping(lines, index, indent)


def parse_yaml_sequence(lines: List[str], index: int, indent: int) -> tuple[List[Any], int]:
    items: List[Any] = []
    while index < len(lines):
        if not lines[index].strip():
            index += 1
            continue
        current_indent = yaml_indent(lines[index])
        stripped = lines[index].strip()
        if current_indent < indent or current_indent != indent or not stripped.startswith("-"):
            break
        item_text = stripped[1:].strip()
        index += 1
        if not item_text:
            item, index = parse_yaml_block(lines, index, indent + 2)
            items.append(item)
            continue
        key_value = split_yaml_key_value(item_text)
        if key_value:
            key, raw_value = key_value
            item: Dict[str, Any] = {}
            if raw_value:
                item[key] = parse_yaml_scalar(raw_value)
            else:
                item[key], index = parse_yaml_block(lines, index, indent + 2)
            if index < len(lines) and yaml_indent(lines[index]) > indent:
                extra, index = parse_yaml_block(lines, index, indent + 2)
                if isinstance(extra, dict):
                    item.update(extra)
                elif extra is not None:
                    raise ValueError("Unsupported nested YAML sequence item.")
            items.append(item)
        else:
            items.append(parse_yaml_scalar(item_text))
    return items, index


def parse_yaml_mapping(lines: List[str], index: int, indent: int) -> tuple[Dict[str, Any], int]:
    mapping: Dict[str, Any] = {}
    while index < len(lines):
        if not lines[index].strip():
            index += 1
            continue
        current_indent = yaml_indent(lines[index])
        stripped = lines[index].strip()
        if current_indent < indent or current_indent != indent or stripped.startswith("-"):
            break
        key_value = split_yaml_key_value(stripped)
        if not key_value:
            raise ValueError(f"Unsupported YAML mapping line: {stripped}")
        key, raw_value = key_value
        index += 1
        if raw_value:
            mapping[key] = parse_yaml_scalar(raw_value)
        else:
            mapping[key], index = parse_yaml_block(lines, index, indent + 2)
    return mapping, index


def split_yaml_key_value(text: str) -> Optional[tuple[str, str]]:
    if not re.match(r"^[A-Za-z0-9_\"'-]+\s*:", text):
        return None
    quote: Optional[str] = None
    bracket_depth = 0
    brace_depth = 0
    escaped = False
    for index, char in enumerate(text):
        if quote:
            if char == "\\" and quote == '"' and not escaped:
                escaped = True
                continue
            if char == quote and not escaped:
                quote = None
            escaped = False
            continue
        if char in {"'", '"'}:
            quote = char
        elif char == "[":
            bracket_depth += 1
        elif char == "]":
            bracket_depth -= 1
        elif char == "{":
            brace_depth += 1
        elif char == "}":
            brace_depth -= 1
        elif char == ":" and bracket_depth == 0 and brace_depth == 0:
            return parse_yaml_key(text[:index]), text[index + 1 :].strip()
    return None


def parse_yaml_key(raw_key: str) -> str:
    key = raw_key.strip()
    if (key.startswith('"') and key.endswith('"')) or (key.startswith("'") and key.endswith("'")):
        return str(parse_yaml_scalar(key))
    return key


def parse_yaml_scalar(raw_value: str) -> Any:
    value = raw_value.strip()
    if value == "":
        return None
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_yaml_scalar(item) for item in split_top_level(inner)]
    if value.startswith("{") and value.endswith("}"):
        inner = value[1:-1].strip()
        if not inner:
            return {}
        result: Dict[str, Any] = {}
        for item in split_top_level(inner):
            key_value = split_yaml_key_value(item)
            if not key_value:
                raise ValueError(f"Unsupported YAML flow mapping item: {item}")
            key, nested_value = key_value
            result[key] = parse_yaml_scalar(nested_value)
        return result
    if value.startswith('"') and value.endswith('"'):
        return ast.literal_eval(value)
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "none", "~"}:
        return None
    if re.fullmatch(r"[-+]?\d+", value):
        return int(value)
    if re.fullmatch(r"[-+]?\d+\.\d+", value):
        return float(value)
    return value


def split_top_level(text: str) -> List[str]:
    items: List[str] = []
    start = 0
    quote: Optional[str] = None
    bracket_depth = 0
    brace_depth = 0
    escaped = False
    for index, char in enumerate(text):
        if quote:
            if char == "\\" and quote == '"' and not escaped:
                escaped = True
                continue
            if char == quote and not escaped:
                quote = None
            escaped = False
            continue
        if char in {"'", '"'}:
            quote = char
        elif char == "[":
            bracket_depth += 1
        elif char == "]":
            bracket_depth -= 1
        elif char == "{":
            brace_depth += 1
        elif char == "}":
            brace_depth -= 1
        elif char == "," and bracket_depth == 0 and brace_depth == 0:
            items.append(text[start:index].strip())
            start = index + 1
    items.append(text[start:].strip())
    return [item for item in items if item]


def load_json_schema(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def find_fixture_file(source_dir: Path, candidates: Iterable[str]) -> Path:
    for filename in candidates:
        candidate = source_dir / filename
        if candidate.exists():
            return candidate
    expected = ", ".join(candidates)
    raise FileNotFoundError(f"Required fixture file not found in {source_dir}: {expected}")


def load_seed_source(source_dir: Path) -> Dict[str, Any]:
    scenario_path = find_fixture_file(source_dir, SCENARIO_FIXTURE_FILENAMES)
    context_path = find_fixture_file(source_dir, CONTEXT_FIXTURE_FILENAMES)
    scenario_doc = load_yaml(scenario_path)
    context_doc = load_yaml(context_path)
    return {
        "scenarios_doc": scenario_doc,
        "contexts_doc": context_doc,
        "contexts": resolve_contexts(context_doc),
        "scenario_file": scenario_path.name,
        "context_file": context_path.name,
    }


def resolve_contexts(context_doc: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    raw_contexts = {
        item["id"]: item
        for item in context_doc.get("contexts", [])
        if isinstance(item, dict) and item.get("id")
    }
    resolved: Dict[str, Dict[str, Any]] = {}

    def resolve(context_id: str, stack: Optional[List[str]] = None) -> Dict[str, Any]:
        if context_id in resolved:
            return copy.deepcopy(resolved[context_id])
        if context_id not in raw_contexts:
            raise KeyError(f"Unknown context fixture id: {context_id}")
        stack = stack or []
        if context_id in stack:
            raise ValueError(f"Cyclic context fixture inheritance: {context_id}")

        current = copy.deepcopy(raw_contexts[context_id])
        parent_id = current.pop("extends", None)
        if parent_id:
            merged = deep_merge(resolve(parent_id, stack + [context_id]), current)
        else:
            merged = current
        resolved[context_id] = copy.deepcopy(merged)
        return merged

    for context_id in raw_contexts:
        resolve(context_id)
    return resolved


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def compact_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in data.items() if value is not None}


def command_context_from_hometusk(context: Dict[str, Any]) -> Dict[str, Any]:
    household_source = context.get("household", {})
    household: Dict[str, Any] = {}
    household_id = household_source.get("household_id")
    if household_id:
        household["household_id"] = household_id

    household["members"] = [
        compact_dict(
            {
                "user_id": member.get("user_id"),
                "display_name": member.get("display_name"),
                "role": member.get("role"),
                "workload_score": member.get("workload_score"),
            }
        )
        for member in context.get("members", [])
    ]

    zones = [
        compact_dict({"zone_id": zone.get("zone_id"), "name": zone.get("name")})
        for zone in context.get("zones", [])
    ]
    if zones:
        household["zones"] = zones

    shopping_lists = [
        compact_dict(
            {
                "list_id": shopping_list.get("list_id"),
                "name": shopping_list.get("name"),
            }
        )
        for shopping_list in context.get("shopping_lists", [])
    ]
    if shopping_lists:
        household["shopping_lists"] = shopping_lists

    command_context: Dict[str, Any] = {"household": household}

    defaults = compact_dict(
        {
            "default_assignee_id": context.get("defaults", {}).get("default_assignee_id"),
            "default_list_id": context.get("defaults", {}).get("default_list_id"),
        }
    )
    if defaults:
        command_context["defaults"] = defaults

    policies = compact_dict(
        {
            "quiet_hours": context.get("policies", {}).get("quiet_hours"),
            "max_open_tasks_per_user": context.get("policies", {}).get("max_open_tasks_per_user"),
        }
    )
    if policies:
        command_context["policies"] = policies

    return command_context


def command_from_scenario(scenario: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    requester = context.get("requester", {})
    requester_id = requester.get("user_id")
    if not requester_id and context.get("members"):
        requester_id = context["members"][0].get("user_id")
    return {
        "command_id": f"hometusk-seed-{scenario['id']}",
        "user_id": requester_id or "unknown-requester",
        "timestamp": scenario.get("reference_instant") or "2026-06-15T12:00:00+03:00",
        "text": scenario.get("input_text", ""),
        "capabilities": list(CURRENT_CAPABILITIES),
        "context": command_context_from_hometusk(context),
    }


def default_decide(command: Dict[str, Any]) -> Dict[str, Any]:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from routers.factory import decide

    return decide(command)


@contextmanager
def eval_environment() -> Iterator[None]:
    previous = {key: os.environ.get(key) for key in EVAL_ENV_OVERRIDES}
    try:
        for key, value in EVAL_ENV_OVERRIDES.items():
            os.environ[key] = value
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def expected_outcomes(expected: str) -> Set[str]:
    mapping = {
        "execute": {"execute"},
        "execute_or_clarify": {"execute", "clarify"},
        "clarify": {"clarify"},
        "confirm": {"confirm", "clarify"},
        "confirm_or_clarify": {"confirm", "clarify"},
        "clarify_or_confirm": {"clarify", "confirm"},
        "clarify_then_confirm": {"clarify", "confirm"},
        "answer_blocked_or_clarify": {"clarify", "blocked"},
        "reject": {"reject", "reject_mapped_to_error"},
        "reject_or_clarify": {"reject", "reject_mapped_to_error", "clarify"},
    }
    return mapping.get(expected, {expected})


def expected_intents(expected: str) -> Set[str]:
    aliases = {
        "add_shopping_items": {"add_shopping_items", "add_shopping_item"},
        "task_shopping_linkage_or_shopping_context": {
            "task_shopping_linkage_or_shopping_context",
            "add_shopping_items",
            "add_shopping_item",
            "clarify_needed",
        },
        "answer_household_status": {"answer_household_status", "clarify_needed"},
    }
    return aliases.get(expected, {expected})


def provider_outcome(decision: Dict[str, Any]) -> str:
    action = decision.get("action")
    status = decision.get("status")
    decision_outcome = decision.get("decision_outcome")
    if decision_outcome in {"execute", "clarify", "reject", "confirm"}:
        return str(decision_outcome)
    if status == "error":
        return "reject_mapped_to_error"
    if action == "clarify":
        return "clarify"
    if action in {"start_job", "propose_create_task", "propose_add_shopping_item"}:
        return "execute"
    if action == "reject":
        return "reject"
    if action == "confirm":
        return "confirm"
    return "unknown"


def provider_intent(command: Dict[str, Any], decision: Dict[str, Any]) -> str:
    payload = decision.get("payload", {})
    if decision.get("action") == "start_job":
        job_type = payload.get("job_type")
        if job_type == "add_shopping_item":
            return "add_shopping_items"
        if job_type == "create_task":
            return "create_task"

    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from graphs.core_graph import detect_intent

    detected = detect_intent(command.get("text", ""))
    return "add_shopping_items" if detected == "add_shopping_item" else detected


def action_types(decision: Dict[str, Any]) -> List[str]:
    payload = decision.get("payload", {})
    proposed = payload.get("proposed_actions") or []
    if proposed:
        return [str(action.get("action", "unknown")) for action in proposed]
    return [str(decision.get("action", "unknown"))]


def trace_complete(decision: Dict[str, Any]) -> bool:
    required = ["decision_id", "trace_id", "schema_version", "decision_version", "created_at"]
    return all(bool(decision.get(key)) for key in required)


def expected_item_count(scenario: Dict[str, Any]) -> int:
    entities = scenario.get("expected_entities", {})
    items = entities.get("items")
    if isinstance(items, list):
        return len(items)
    for action in scenario.get("expected_actions", []):
        action_items = action.get("items")
        if isinstance(action_items, list):
            return len(action_items)
    return 0


def actual_shopping_action_count(decision: Dict[str, Any]) -> int:
    return sum(1 for item in action_types(decision) if item == "propose_add_shopping_item")


def has_cross_household_reference(decision: Dict[str, Any], command: Dict[str, Any]) -> bool:
    context = command.get("context", {})
    household = context.get("household", {})
    member_ids = {member.get("user_id") for member in household.get("members", [])}
    zone_ids = {zone.get("zone_id") for zone in household.get("zones", [])}
    list_ids = {item.get("list_id") for item in household.get("shopping_lists", [])}

    for payload in iter_payloads(decision):
        task = payload.get("task") if isinstance(payload.get("task"), dict) else {}
        item = payload.get("item") if isinstance(payload.get("item"), dict) else {}

        assignee_id = task.get("assignee_id")
        if assignee_id and assignee_id not in member_ids:
            return True
        zone_id = task.get("zone_id")
        if zone_id and zone_id not in zone_ids:
            return True
        list_id = item.get("list_id")
        if list_id and list_id not in list_ids:
            return True
    return False


def iter_payloads(decision: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    payload = decision.get("payload", {})
    proposed = payload.get("proposed_actions") or []
    if proposed:
        for action in proposed:
            action_payload = action.get("payload")
            if isinstance(action_payload, dict):
                yield action_payload
    elif isinstance(payload, dict):
        yield payload


def evaluate_scenario(
    scenario: Dict[str, Any],
    context: Dict[str, Any],
    *,
    command_schema: Dict[str, Any],
    decision_schema: Dict[str, Any],
    decide_fn: DecisionFn,
) -> Dict[str, Any]:
    scenario_id = scenario["id"]
    expected_outcome = scenario.get("expected_decision_outcome", "unknown")
    expected_intent = scenario.get("expected_intent", "unknown")
    command = command_from_scenario(scenario, context)
    result: Dict[str, Any] = {
        "scenario_id": scenario_id,
        "schema_valid": False,
        "expected_outcome": expected_outcome,
        "actual_outcome": "not_run",
        "outcome_match": False,
        "expected_intent": expected_intent,
        "actual_intent": "not_run",
        "intent_match": False,
        "actual_action_types": [],
        "expected_action_count": len(scenario.get("expected_actions", [])),
        "expected_item_count": expected_item_count(scenario),
        "actual_action_count": 0,
        "unsupported_auto_execute": False,
        "cross_household_reference": False,
        "trace_complete": False,
        "skipped": False,
        "skip_reason": None,
        "failure_buckets": [],
    }

    try:
        validate(instance=command, schema=command_schema)
        with eval_environment():
            decision = decide_fn(command)
        validate(instance=decision, schema=decision_schema)
    except ValidationError:
        result["failure_buckets"].append("schema_invalid")
        return result
    except Exception as exc:  # noqa: BLE001 - privacy-safe failure bucket only
        result["skipped"] = True
        result["skip_reason"] = type(exc).__name__
        result["failure_buckets"].append("runner_error")
        return result

    actual_outcome = provider_outcome(decision)
    actual_intent = provider_intent(command, decision)
    actual_actions = action_types(decision)

    result.update(
        {
            "schema_valid": True,
            "actual_outcome": actual_outcome,
            "outcome_match": actual_outcome in expected_outcomes(expected_outcome),
            "actual_intent": actual_intent,
            "intent_match": actual_intent in expected_intents(expected_intent),
            "actual_action_types": actual_actions,
            "actual_action_count": len(actual_actions),
            "unsupported_auto_execute": (
                actual_outcome == "execute"
                and "execute" not in expected_outcomes(expected_outcome)
            ),
            "cross_household_reference": has_cross_household_reference(decision, command),
            "trace_complete": trace_complete(decision),
        }
    )

    if not result["outcome_match"]:
        result["failure_buckets"].append("wrong_outcome")
    if not result["intent_match"]:
        result["failure_buckets"].append("wrong_intent")
    if result["unsupported_auto_execute"]:
        result["failure_buckets"].append("unsupported_auto_execute")
    if result["cross_household_reference"]:
        result["failure_buckets"].append("cross_household_reference")
    if result["expected_item_count"] > 1 and actual_shopping_action_count(decision) != result["expected_item_count"]:
        result["failure_buckets"].append("item_boundary_loss")
    if expected_outcome == "reject" and actual_outcome == "execute":
        result["failure_buckets"].append("unsafe_assignment_not_rejected")
    if expected_outcome == "answer_blocked_or_clarify" and actual_outcome == "execute":
        result["failure_buckets"].append("answer_mutates_state")
    if not result["trace_complete"]:
        result["failure_buckets"].append("trace_missing")

    result["decision_schema_version"] = decision.get("schema_version")
    result["decision_version"] = decision.get("decision_version")
    return result


def compute_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(results)
    failure_counts = Counter(
        bucket
        for result in results
        for bucket in result.get("failure_buckets", [])
    )
    blocker_failures = sum(
        1
        for result in results
        if BLOCKER_BUCKETS & set(result.get("failure_buckets", []))
    )
    return {
        "total_scenarios": total,
        "evaluated_scenarios": sum(1 for result in results if not result.get("skipped")),
        "skipped_scenarios": sum(1 for result in results if result.get("skipped")),
        "schema_valid_count": sum(1 for result in results if result.get("schema_valid")),
        "outcome_match_count": sum(1 for result in results if result.get("outcome_match")),
        "intent_match_count": sum(1 for result in results if result.get("intent_match")),
        "unsupported_auto_execute_count": sum(
            1 for result in results if result.get("unsupported_auto_execute")
        ),
        "cross_household_reference_count": sum(
            1 for result in results if result.get("cross_household_reference")
        ),
        "blocker_failure_scenarios": blocker_failures,
        "failure_bucket_counts": dict(sorted(failure_counts.items())),
    }


def detect_git_revision(path: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:  # noqa: BLE001 - best effort metadata
        return "unknown"
    return completed.stdout.strip() or "unknown"


def feature_flags() -> Dict[str, Optional[str]]:
    return {name: os.getenv(name) for name in FEATURE_FLAG_NAMES}


def build_report(
    *,
    source_dir: Path,
    source_revision: Optional[str] = None,
    planner_version: str = "current-provider-router",
    decide_fn: DecisionFn = default_decide,
    run_command: Optional[str] = None,
) -> Dict[str, Any]:
    seed = load_seed_source(source_dir)
    scenario_doc = seed["scenarios_doc"]
    context_doc = seed["contexts_doc"]
    command_schema = load_json_schema(COMMAND_SCHEMA_PATH)
    decision_schema = load_json_schema(DECISION_SCHEMA_PATH)

    results: List[Dict[str, Any]] = []
    for scenario in scenario_doc.get("scenarios", []):
        context_id = scenario.get("context_fixture_id")
        context = seed["contexts"].get(context_id)
        if context is None:
            results.append(
                {
                    "scenario_id": scenario.get("id", "unknown"),
                    "schema_valid": False,
                    "expected_outcome": scenario.get("expected_decision_outcome", "unknown"),
                    "actual_outcome": "not_run",
                    "outcome_match": False,
                    "expected_intent": scenario.get("expected_intent", "unknown"),
                    "actual_intent": "not_run",
                    "intent_match": False,
                    "actual_action_types": [],
                    "expected_action_count": len(scenario.get("expected_actions", [])),
                    "expected_item_count": expected_item_count(scenario),
                    "actual_action_count": 0,
                    "unsupported_auto_execute": False,
                    "cross_household_reference": False,
                    "trace_complete": False,
                    "skipped": True,
                    "skip_reason": "missing_context_fixture",
                    "failure_buckets": ["missing_context_fixture"],
                }
            )
            continue
        results.append(
            evaluate_scenario(
                scenario,
                context,
                command_schema=command_schema,
                decision_schema=decision_schema,
                decide_fn=decide_fn,
            )
        )

    decision_versions = sorted(
        {
            result["decision_version"]
            for result in results
            if result.get("decision_version")
        }
    )
    schema_versions = sorted(
        {
            result["decision_schema_version"]
            for result in results
            if result.get("decision_schema_version")
        }
    )
    return {
        "source": {
            "repo": "hometusk",
            "path": str(source_dir),
            "revision": source_revision or detect_git_revision(source_dir),
            "fixture_versions": {
                "scenarios": scenario_doc.get("schema_version"),
                "contexts": context_doc.get("schema_version"),
            },
            "fixture_files": {
                "scenarios": seed["scenario_file"],
                "contexts": seed["context_file"],
            },
            "scenario_count": len(scenario_doc.get("scenarios", [])),
            "context_count": len(context_doc.get("contexts", [])),
            "suite_policy": scenario_doc.get("suite_policy", {}),
            "minimum_before_domain_planner_acceptance": scenario_doc.get("suite_policy", {}).get(
                "minimum_before_domain_planner_acceptance"
            ),
        },
        "run": {
            "command": run_command,
            "planner_version": planner_version,
            "schema_versions": schema_versions,
            "decision_versions": decision_versions,
            "feature_flags": feature_flags(),
            "eval_env_overrides": dict(EVAL_ENV_OVERRIDES),
        },
        "results": results,
        "metrics": compute_metrics(results),
    }


def collect_sensitive_strings(*docs: Dict[str, Any]) -> Set[str]:
    sensitive_keys = {
        "input_text",
        "text",
        "name",
        "display_name",
        "aliases",
        "title",
        "ux_recommendation",
        "question",
        "message",
        "prompt",
        "label",
    }
    values: Set[str] = set()

    def visit(value: Any, key: Optional[str] = None) -> None:
        if isinstance(value, dict):
            for child_key, child_value in value.items():
                visit(child_value, str(child_key))
        elif isinstance(value, list):
            for child in value:
                visit(child, key)
        elif isinstance(value, str) and key in sensitive_keys and len(value.strip()) > 3:
            values.add(value.strip())

    for doc in docs:
        visit(doc)
    return values


def assert_no_sensitive_output(report_text: str, source_dir: Path) -> None:
    seed = load_seed_source(source_dir)
    sensitive_values = collect_sensitive_strings(seed["scenarios_doc"], seed["contexts_doc"])
    leaked = sorted(value for value in sensitive_values if value in report_text)
    if leaked:
        raise ValueError(f"Report contains raw fixture text ({len(leaked)} leak(s)).")


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--source-revision", default=None)
    parser.add_argument("--planner-version", default="current-provider-router")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--check-no-raw-text", action="store_true")
    return parser.parse_args(argv)


def run_command_from_args(args: argparse.Namespace) -> str:
    command = ["python3", "scripts/evaluate_domain_planner_seed.py"]
    if args.source_dir != DEFAULT_SOURCE_DIR:
        command.extend(["--source-dir", str(args.source_dir)])
    if args.source_revision:
        command.extend(["--source-revision", args.source_revision])
    if args.planner_version != "current-provider-router":
        command.extend(["--planner-version", args.planner_version])
    if args.output:
        command.extend(["--output", str(args.output)])
    if args.check_no_raw_text:
        command.append("--check-no-raw-text")
    return " ".join(command)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    report = build_report(
        source_dir=args.source_dir,
        source_revision=args.source_revision,
        planner_version=args.planner_version,
        run_command=run_command_from_args(args),
    )
    report_text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.check_no_raw_text:
        assert_no_sensitive_output(report_text, args.source_dir)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report_text + "\n", encoding="utf-8")
    else:
        print(report_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
