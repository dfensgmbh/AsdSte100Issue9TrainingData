# Convenience aliases for common dev tasks. Run `make help` for the list.
#
# All real logic lives in scripts/ci-local.sh (and scripts/ci-local.ps1).
# This Makefile is just a thin wrapper so you can type `make ci` etc.
#
# On Windows, install make via Git Bash, MSYS2, Chocolatey, or Scoop; or
# call the ci-local scripts directly.

SHELL := /usr/bin/env bash
.DEFAULT_GOAL := help

# Path to the cross-platform CI runner.
CI := ./scripts/ci-local.sh

.PHONY: help ci ci-fast lint format test build sync hooks clean

help: ## Show this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage: make <target>\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

ci: ## Run the full CI pipeline locally (same as GitHub Actions).
	$(CI)

ci-fast: ## Run CI without pip-audit and build (the slow / network-heavy steps).
	$(CI) --skip pip-audit,build

sync: ## Install / refresh dev + test dependencies.
	uv sync --extra dev --extra test

lint: ## Run all linters and type checkers (no formatting changes).
	$(CI) --skip sync,pip-audit,tests,build

format: ## Apply black to fix formatting (the only auto-fixing step).
	uv run black .

test: ## Run unit tests with coverage.
	uv run coverage run -m unittest discover -v -s tests -t . -p 'test_*.py'
	uv run coverage report -m

build: ## Build sdist and wheel via `uv build`.
	uv build

hooks: ## Install git pre-push hook (runs ci-fast before each push).
	./scripts/install-hooks.sh

clean: ## Remove build artifacts and caches.
	rm -rf build/ dist/ *.egg-info src/*.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name .pytest_cache -prune -exec rm -rf {} +
	find . -type d -name .mypy_cache -prune -exec rm -rf {} +
	rm -f .coverage coverage.xml
