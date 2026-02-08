"""Tests for multi-item extraction (ST-009)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import patch

import pytest

# ---- helpers ----------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from graphs.core_graph import extract_item_name, extract_items  # noqa: E402


# ---- extract_items: single item ---------------------------------------------


def test_single_item_russian():
    result = extract_items("Купи молоко")
    assert len(result) == 1
    assert result[0]["name"] == "молоко"


def test_single_item_english():
    result = extract_items("Buy milk")
    assert len(result) == 1
    assert result[0]["name"] == "milk"


# ---- extract_items: multi-item ----------------------------------------------


def test_multi_item_comma_russian():
    result = extract_items("Купи молоко, хлеб, бананы")
    assert len(result) == 3
    names = [item["name"] for item in result]
    assert names == ["молоко", "хлеб", "бананы"]


def test_multi_item_conjunction_russian():
    result = extract_items("Купи хлеб и яйца")
    assert len(result) == 2
    names = [item["name"] for item in result]
    assert names == ["хлеб", "яйца"]


def test_multi_item_conjunction_english():
    result = extract_items("Buy apples and oranges")
    assert len(result) == 2
    names = [item["name"] for item in result]
    assert names == ["apples", "oranges"]


def test_multi_item_comma_and_conjunction():
    result = extract_items("Купи молоко, хлеб и бананы")
    assert len(result) == 3
    names = [item["name"] for item in result]
    assert names == ["молоко", "хлеб", "бананы"]


# ---- extract_items: quantity/unit -------------------------------------------


def test_quantity_and_unit_russian():
    result = extract_items("Купи 2 литра молока")
    assert len(result) == 1
    assert result[0]["name"] == "молока"
    assert result[0]["quantity"] == "2"
    assert result[0]["unit"] == "литра"


def test_quantity_no_unit():
    result = extract_items("Купи 3 яблока")
    assert len(result) == 1
    assert result[0]["name"] == "яблока"
    assert result[0]["quantity"] == "3"
    assert "unit" not in result[0]


# ---- extract_items: edge cases ----------------------------------------------


def test_empty_text():
    assert extract_items("") == []


def test_no_shopping_keyword():
    assert extract_items("Погода сегодня хорошая") == []


def test_trailing_context_removed():
    result = extract_items("Добавь сахар в список покупок")
    assert len(result) == 1
    assert result[0]["name"] == "сахар"


# ---- backward compat: extract_item_name unchanged ---------------------------


def test_backward_compat_extract_item_name_single():
    """extract_item_name still returns the full string (not split)."""
    result = extract_item_name("Купи молоко")
    assert result == "молоко"


def test_backward_compat_extract_item_name_multi():
    """extract_item_name returns FULL string after keyword (not split)."""
    result = extract_item_name("Купи хлеб и яйца")
    assert result == "хлеб и яйца"


# ---- agent_runner schema: quantity is string --------------------------------


def test_agent_runner_schema_quantity_type():
    from agent_runner.schemas import shopping_extraction_schema

    schema = shopping_extraction_schema()
    item_props = schema["properties"]["items"]["items"]["properties"]
    qty_type = item_props["quantity"]["type"]
    assert "string" in qty_type, f"quantity type should be string, got {qty_type}"
    assert "number" not in qty_type, f"quantity should not be number"


# ---- V2 normalize: items in normalized dict ---------------------------------


def test_normalize_has_items():
    """V2 normalize() returns 'items' in normalized dict."""
    from routers.v2 import RouterV2Pipeline

    pipeline = RouterV2Pipeline()
    command = {
        "text": "Купи хлеб и молоко",
        "capabilities": ["start_job", "propose_add_shopping_item"],
        "context": {"household": {"shopping_lists": []}},
    }
    with patch("routers.v2.extract_shopping_item_name") as mock_llm:
        mock_llm.return_value = type("R", (), {"item_name": "хлеб и молоко"})()
        with patch("routers.v2.runner_enabled", return_value=False):
            normalized = pipeline.normalize(command)

    assert "items" in normalized
    assert isinstance(normalized["items"], list)
    assert len(normalized["items"]) == 2
    names = [item["name"] for item in normalized["items"]]
    assert names == ["хлеб", "молоко"]


def test_normalize_item_name_backward_compat():
    """V2 normalize() still has 'item_name' from LLM extraction."""
    from routers.v2 import RouterV2Pipeline

    pipeline = RouterV2Pipeline()
    command = {
        "text": "Купи молоко",
        "capabilities": ["start_job"],
        "context": {"household": {"shopping_lists": []}},
    }
    with patch("routers.v2.extract_shopping_item_name") as mock_llm:
        mock_llm.return_value = type("R", (), {"item_name": "молоко"})()
        with patch("routers.v2.runner_enabled", return_value=False):
            normalized = pipeline.normalize(command)

    assert normalized["item_name"] == "молоко"
    assert len(normalized["items"]) == 1


# ---- baseline shopping agent: multi-item ------------------------------------


def test_baseline_shopping_multi_item():
    from agents.baseline_shopping import run

    result = run({"text": "Купи молоко и хлеб"})
    items = result["items"]
    assert len(items) == 2
    assert items[0]["name"] == "молоко"
    assert items[1]["name"] == "хлеб"


def test_baseline_shopping_empty():
    from agents.baseline_shopping import run

    result = run({"text": "Погода"})
    assert result["items"] == []
    assert result["confidence"] == 0.0
