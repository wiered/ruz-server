.PHONY: help test test-repositories test-api test-helpers test-models test-ruzapi test-unit test-integration test-coverage install-test-deps clean

# Forward extra CLI args to pytest, e.g.:
# make test -- -q
# make test-api -- -q -k users
PYTEST_ARGS = $(filter-out $@,$(MAKECMDGOALS))

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install-test-deps: ## Install test dependencies
	pip install -e ".[test]"

test: ## Run all tests
	pytest $(PYTEST_ARGS)

test-repositories: ## Run repository tests only
	pytest -m repositories $(PYTEST_ARGS)

test-api: ## Run API tests only
	pytest -m api $(PYTEST_ARGS)

test-helpers: ## Run helper tests only
	pytest -m helpers $(PYTEST_ARGS)

test-models: ## Run model tests only
	pytest -m models $(PYTEST_ARGS)

test-ruzapi: ## Run ruz_api tests only
	pytest -m ruzapi $(PYTEST_ARGS)

test-unit: ## Run unit tests only
	pytest -m unit $(PYTEST_ARGS)

test-integration: ## Run integration tests only
	pytest -m integration $(PYTEST_ARGS)

test-coverage: ## Run tests with coverage report
	pytest --cov=src --cov-report=html --cov-report=term $(PYTEST_ARGS)

test-fast: ## Run fast tests (exclude slow tests)
	pytest -m "not slow" $(PYTEST_ARGS)

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/

# Swallow extra positional args passed after '--' so make does not fail.
%:
	@:
