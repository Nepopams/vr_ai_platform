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


def _contains_placeholder(value: object) -> bool:
    if isinstance(value, str):
        return "${" in value or ("<" in value and ">" in value)
    if isinstance(value, dict):
        return any(_contains_placeholder(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_placeholder(item) for item in value)
    return False


def test_load_valid_policy() -> None:
    from llm_policy.loader import LlmPolicyLoader

    policy = LlmPolicyLoader.load(enabled=True, allow_placeholders=True)

    assert policy is not None
    assert policy.compat_adr == "ADR-003"


def test_load_cloudru_policy() -> None:
    from llm_policy.loader import LlmPolicyLoader

    policy_path = BASE_DIR / "llm_policy" / "llm-policy.cloudru.yaml"
    policy = LlmPolicyLoader.load(
        enabled=True,
        path_override=str(policy_path),
        allow_placeholders=False,
    )

    assert policy is not None
    assert policy.profiles == ("cheap", "reliable")
    assert "shopping_extraction" in policy.routing
    cheap = policy.routing["shopping_extraction"]["cheap"]
    reliable = policy.routing["shopping_extraction"]["reliable"]
    assert cheap.provider == "openai_compatible"
    assert cheap.model == "openai/gpt-oss-20b"
    assert cheap.temperature == 0.1
    assert cheap.max_tokens == 512
    assert cheap.timeout_ms == 8000
    assert cheap.base_url is None
    assert reliable.provider == "openai_compatible"
    assert reliable.model == "openai/gpt-oss-20b"
    assert reliable.timeout_ms == 10000


def test_cloudru_policy_has_no_placeholders_or_keys() -> None:
    policy_path = BASE_DIR / "llm_policy" / "llm-policy.cloudru.yaml"
    raw = policy_path.read_text(encoding="utf-8")
    payload = policy_loader._load_policy_payload(policy_path)

    assert not _contains_placeholder(payload)
    assert "LLM_API_KEY" not in raw
    assert "API_KEY" not in raw
    assert "sk-" not in raw


def test_invalid_missing_profile(tmp_path: Path) -> None:
    from llm_policy.loader import LlmPolicyLoader

    payload = _load_policy_payload()
    payload["profiles"].pop("cheap")
    policy_path = _write_policy(tmp_path / "invalid.yaml", payload)

    with pytest.raises(ValueError, match="profiles missing required profile"):
        LlmPolicyLoader.load(enabled=True, path_override=str(policy_path), allow_placeholders=True)


def test_invalid_extra_top_level_field(tmp_path: Path) -> None:
    from llm_policy.loader import LlmPolicyLoader

    payload = _load_policy_payload()
    payload["extra"] = "value"
    policy_path = _write_policy(tmp_path / "invalid.yaml", payload)

    with pytest.raises(ValueError, match="unexpected top-level fields"):
        LlmPolicyLoader.load(enabled=True, path_override=str(policy_path), allow_placeholders=True)


def test_disabled_policy_no_side_effects() -> None:
    for module in list(sys.modules):
        if module == "llm_policy" or module.startswith("llm_policy."):
            sys.modules.pop(module, None)

    from llm_policy.loader import LlmPolicyLoader

    assert LlmPolicyLoader.load(enabled=False) is None


def test_enabled_policy_rejects_placeholders(tmp_path: Path) -> None:
    from llm_policy.loader import LlmPolicyLoader

    payload = _load_policy_payload()
    payload["routing"]["shopping_extraction"]["cheap"]["model"] = "${MODEL_ID}"
    policy_path = _write_policy(tmp_path / "invalid.yaml", payload)

    with pytest.raises(ValueError, match="placeholders are not allowed"):
        LlmPolicyLoader.load(enabled=True, path_override=str(policy_path), allow_placeholders=False)


def test_enabled_policy_allows_placeholders_with_flag(tmp_path: Path) -> None:
    from llm_policy.loader import LlmPolicyLoader

    payload = _load_policy_payload()
    payload["routing"]["shopping_extraction"]["cheap"]["model"] = "${MODEL_ID}"
    policy_path = _write_policy(tmp_path / "valid.yaml", payload)

    policy = LlmPolicyLoader.load(
        enabled=True,
        path_override=str(policy_path),
        allow_placeholders=True,
    )

    assert policy is not None


def test_disabled_policy_does_not_read_file(monkeypatch: pytest.MonkeyPatch) -> None:
    from llm_policy.loader import LlmPolicyLoader

    def _boom(*_args: object, **_kwargs: object) -> str:
        raise AssertionError("unexpected file read")

    monkeypatch.setattr(Path, "read_text", _boom)

    assert LlmPolicyLoader.load(enabled=False) is None
