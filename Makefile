.PHONY: run_graph test validate_contracts audit_decisions bump_contract_version gen_fixtures run_graph_suite release_sanity

run_graph:
	python -m graphs.core_graph

test:
	pytest

validate_contracts:
	python skills/contract-checker/scripts/validate_contracts.py

audit_decisions:
	python skills/decision-log-audit/scripts/audit_decision_logs.py

bump_contract_version:
	python schema-bump/scripts/bump_version.py $(PART)

gen_fixtures:
	python fixtures-generator/scripts/generate_fixtures.py

run_graph_suite:
	python graph-sanity/scripts/run_graph_suite.py

release_sanity:
	python release-sanity/scripts/release_sanity.py
