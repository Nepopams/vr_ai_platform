.PHONY: run_graph test validate_contracts contract-checker schema-bump fixtures-generator decision-log-audit graph-sanity release-sanity

run_graph:
	python -m graphs.core_graph

test:
	pytest

validate_contracts:
	pytest tests/test_contracts.py

contract-checker:
	python -m skills.contract_checker

schema-bump:
	python -m skills.schema_bump check

fixtures-generator:
	python -m skills.fixtures_generator

decision-log-audit:
	python -m skills.decision_log_audit

graph-sanity:
	python -m skills.graph_sanity

release-sanity:
	python -m skills.release_sanity
