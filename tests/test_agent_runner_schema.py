from jsonschema import validate

from agent_runner.schemas import shopping_extraction_schema


def test_schema_allows_basic_payload():
    schema = shopping_extraction_schema()
    payload = {"items": [{"name": "молоко", "quantity": 1, "unit": "л"}]}
    validate(instance=payload, schema=schema)


def test_schema_rejects_additional_properties():
    schema = shopping_extraction_schema()
    payload = {"items": [{"name": "молоко", "extra": "x"}]}
    try:
        validate(instance=payload, schema=schema)
    except Exception:
        assert True
    else:
        raise AssertionError("Schema should reject additional properties")
