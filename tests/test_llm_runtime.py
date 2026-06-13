import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from llm_policy.runtime import _parse_json


def test_parse_direct_json_object() -> None:
    assert _parse_json('{"items": [{"name": "молоко"}]}') == {
        "items": [{"name": "молоко"}]
    }


def test_parse_markdown_fenced_json_object() -> None:
    raw = """```json
{"items": [{"name": "молоко"}]}
```"""

    assert _parse_json(raw) == {"items": [{"name": "молоко"}]}


def test_parse_plain_fenced_json_object() -> None:
    raw = """```
{"items": [{"name": "молоко"}]}
```"""

    assert _parse_json(raw) == {"items": [{"name": "молоко"}]}


def test_parse_prose_with_single_json_object() -> None:
    raw = 'Ответ: {"items": [{"name": "кефир", "quantity": 2}]}'

    assert _parse_json(raw) == {"items": [{"name": "кефир", "quantity": 2}]}


def test_parse_invalid_text_returns_none() -> None:
    assert _parse_json("not json") is None


def test_parse_multiple_json_objects_returns_none() -> None:
    assert _parse_json('{"a": 1} {"b": 2}') is None


def test_parse_top_level_array_returns_none() -> None:
    assert _parse_json('[{"items": []}]') is None


def test_parse_prose_with_array_returns_none() -> None:
    assert _parse_json('Ответ: [{"items": []}]') is None
