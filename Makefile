.PHONY: install lint fmt test test-integration infra-init infra-plan infra-apply run-agent run-runtime clean

PYTHON := python3
VENV := .venv
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
RUFF := $(VENV)/bin/ruff
ENV ?= dev

install:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"
	$(VENV)/bin/pre-commit install

lint:
	$(RUFF) check src/ tests/
	$(RUFF) format --check src/ tests/

fmt:
	$(RUFF) check --fix src/ tests/
	$(RUFF) format src/ tests/

test:
	$(PYTEST) tests/unit -v --cov=agentic_ai --cov-report=term-missing

test-integration:
	$(PYTEST) tests/integration -v

infra-init:
	terraform -chdir=infra/envs/$(ENV) init

infra-plan:
	terraform -chdir=infra/envs/$(ENV) plan

infra-apply:
	terraform -chdir=infra/envs/$(ENV) apply

infra-destroy:
	terraform -chdir=infra/envs/$(ENV) destroy

run-agent:
	$(VENV)/bin/python -m agentic_ai.agents.langgraph_agent "$(QUERY)"

run-runtime:
	$(VENV)/bin/python -m agentic_ai.runtime

clean:
	rm -rf $(VENV) dist/ build/ *.egg-info .pytest_cache .mypy_cache htmlcov .coverage
