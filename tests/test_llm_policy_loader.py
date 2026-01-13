import json
import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from llm_policy import loader as policy_loader


def _write_policy(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _load_policy_payload() -> dict:
    policy_path = BASE_DIR / "llm_policy" / "llm-policy.yaml"
    return policy_loader._load_policy_payload(policy_path)


def test_load_valid_policy() -> None:
    from llm_policy.loader import LlmPolicyLoader

    policy = LlmPolicyLoader.load(enabled=True)

    assert policy is not None
    assert policy.compat_adr == "ADR-003"


def test_invalid_missing_profile(tmp_path: Path) -> None:
    from llm_policy.loader import LlmPolicyLoader

    payload = _load_policy_payload()
    payload["profiles"].pop("cheap")
    policy_path = _write_policy(tmp_path / "invalid.yaml", payload)

    with pytest.raises(ValueError, match="profiles missing required profile"):
        LlmPolicyLoader.load(enabled=True, path_override=str(policy_path))


def test_invalid_extra_top_level_field(tmp_path: Path) -> None:
    from llm_policy.loader import LlmPolicyLoader

    payload = _load_policy_payload()
    payload["extra"] = "value"
    policy_path = _write_policy(tmp_path / "invalid.yaml", payload)

    with pytest.raises(ValueError, match="unexpected top-level fields"):
        LlmPolicyLoader.load(enabled=True, path_override=str(policy_path))


def test_disabled_policy_no_side_effects() -> None:
    for module in list(sys.modules):
        if module == "llm_policy" or module.startswith("llm_policy."):
            sys.modules.pop(module, None)

    from llm_policy.loader import LlmPolicyLoader

    assert LlmPolicyLoader.load(enabled=False) is None
