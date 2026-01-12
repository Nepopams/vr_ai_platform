.PHONY: setup run_graph test validate_contracts contract-checker schema-bump fixtures-generator decision-log-audit graph-sanity api-sanity release-sanity release-sanity-full diagrams

setup:
	pip install -e .

run_graph:
	python -m graphs.core_graph

test:
	pytest

test-core:
	pytest tests/test_contracts.py tests/test_graph_execution.py tests/test_skill_checks.py tests/test_agent_registry.py tests/test_router_strategy.py tests/test_router_golden_like.py

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

api-sanity:
	python scripts/api_sanity.py

release-sanity:
	python -m skills.release_sanity

release-sanity-full:
	RUN_API_SANITY=1 python -m skills.release_sanity

diagrams:
	@set -e; \
	mkdir -p docs/diagrams/out; \
	if command -v plantuml >/dev/null 2>&1; then \
		plantuml -tsvg -o docs/diagrams/out docs/plantuml/*.puml; \
	elif [ -f plantuml/plantuml.jar ]; then \
		java -jar plantuml/plantuml.jar -tsvg -o docs/diagrams/out docs/plantuml/*.puml; \
	else \
		echo "PlantUML not found. Install plantuml or place plantuml/plantuml.jar in the repo root."; \
		echo "Examples: brew install plantuml  |  apt-get install plantuml"; \
		exit 1; \
	fi
