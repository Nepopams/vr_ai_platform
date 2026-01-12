.PHONY: run_graph test validate_contracts

run_graph:
	python -m graphs.core_graph

test:
	pytest

validate_contracts:
	pytest tests/test_contracts.py
