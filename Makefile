.PHONY: install install-chat lint fmt test test-integration infra-init infra-plan infra-apply run-agent run-runtime run-chat deploy-chat clean

PYTHON := python3
VENV := .venv
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
RUFF := $(VENV)/bin/ruff
ENV ?= dev
# Chainlit requires Python <=3.13 (3.14 has async incompatibilities)
CHAT_PYTHON ?= python3.13
CHAT_VENV := .venv-chat

install:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"
	$(VENV)/bin/pre-commit install

install-chat:
	$(CHAT_PYTHON) -m venv $(CHAT_VENV)
	$(CHAT_VENV)/bin/pip install --upgrade pip
	$(CHAT_VENV)/bin/pip install -e ".[chat]"

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

run-chat:
	$(CHAT_VENV)/bin/chainlit run src/agentic_ai/chat.py --port 8000 --watch

deploy-chat:
	@echo "--- Building chat image ---"
	docker build --platform linux/amd64 -t agentic-ai-chat -f docker/Dockerfile.chat .
	@echo "--- Logging in to ECR ---"
	aws ecr get-login-password --region $(shell terraform -chdir=infra/envs/$(ENV) output -raw chat_ecr_repository_url | cut -d. -f4) | \
		docker login --username AWS --password-stdin $(shell terraform -chdir=infra/envs/$(ENV) output -raw chat_ecr_repository_url | cut -d/ -f1)
	@echo "--- Tagging and pushing ---"
	docker tag agentic-ai-chat:latest $(shell terraform -chdir=infra/envs/$(ENV) output -raw chat_ecr_repository_url):latest
	docker push $(shell terraform -chdir=infra/envs/$(ENV) output -raw chat_ecr_repository_url):latest
	@echo "--- Restarting ECS service ---"
	aws ecs update-service \
		--cluster $(shell terraform -chdir=infra/envs/$(ENV) output -raw chat_cluster_arn) \
		--service $(shell terraform -chdir=infra/envs/$(ENV) output -raw chat_service_name) \
		--force-new-deployment \
		--region $(shell terraform -chdir=infra/envs/$(ENV) output -raw chat_ecr_repository_url | cut -d. -f4) \
		--no-cli-pager
	@echo "--- Deploy complete ---"

clean:
	rm -rf $(VENV) $(CHAT_VENV) dist/ build/ *.egg-info .pytest_cache .mypy_cache htmlcov .coverage
