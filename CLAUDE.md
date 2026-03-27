# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Agentic AI framework on AWS Bedrock using LangGraph, DeepAgent, and **Bedrock AgentCore**. Two agent patterns (ReAct tool-calling and multi-step planning), backed by Knowledge Bases, Lambda action groups, and AgentCore services (Memory, Runtime, Gateway, Observability). Infrastructure managed with Terraform.

## Commands

```bash
make install          # Create venv, install deps + pre-commit hooks
make lint             # Ruff linting (E,F,I,N,UP,B,SIM,TCH rules)
make fmt              # Ruff auto-fix + format
make test             # Unit tests with coverage (pytest --cov=agentic_ai)
make test-integration # Integration tests (tests/integration/)
make infra-init       # Terraform init (infra/envs/dev)
make infra-plan       # Terraform plan
make infra-apply      # Terraform apply
make run-agent QUERY="your question"  # Run LangGraph agent locally
make run-runtime      # Start AgentCore Runtime server (AG-UI protocol)
make install-chat     # Create chat venv (Python <=3.13, Chainlit not 3.14 compatible)
make run-chat         # Start Chainlit chat UI (http://localhost:8000)
```

Run a single test: `python -m pytest tests/unit/test_tools.py::TestCalculator::test_addition -v`

## Architecture

**Two agent factories** in `src/agentic_ai/agents/`:
- `langgraph_agent.py` — ReAct agent via `create_react_agent()` from LangGraph + `ChatBedrockConverse`. Simple tool-calling loop. Returns `CompiledStateGraph`.
- `deep_agent.py` — Planning agent via `deepagents.create_deep_agent`. Multi-step reasoning with sub-agent spawning. Returns `CompiledStateGraph`.

Both agents share the same tool registry, accept optional `checkpointer`/`store` for memory, and are invoked identically: `agent.invoke({"messages": [("user", query)]})`.

**AgentCore Integration** (all opt-in via `AGENTCORE_*` env vars):
- `memory.py` — `get_checkpointer()` returns `AgentCoreMemorySaver` for state persistence; `get_memory_store()` returns `AgentCoreMemoryStore` for long-term semantic search. Both return `None` when disabled.
- `runtime.py` — Wraps agents with `BedrockAgentCoreApp` for AG-UI protocol serving. Entry point: `python -m agentic_ai.runtime`.
- `observability.py` — `configure_tracing()` sets up OpenTelemetry when enabled.
- `tools/gateway.py` — Discovers MCP-compatible tools from AgentCore Gateway.
- `tools/agentcore_builtins.py` — Code Interpreter and Browser tools (not in default tools, import explicitly).

**Chat UI** (`src/agentic_ai/chat.py`): Chainlit-based web chat interface. Supports streaming responses, chat profiles (ReAct/Planning agent switching), tool call visualization as expandable steps, optional password auth (`CHAT_AUTH_SECRET` + `CHAT_AUTH_PASSWORD`), and file uploads. Persistence configurable via `CHAT_PERSISTENCE` (memory/sqlite/agentcore). Optional dependency: `pip install -e ".[chat]"`.

**Tools** (`src/agentic_ai/tools/`): Registry in `__init__.py` exposes `get_default_tools()` → `[calculator, web_search]` + knowledge base tool when `KNOWLEDGE_BASE_ID` is set + gateway tools when enabled.

**Chains** (`src/agentic_ai/chains/rag_chain.py`): Non-agent RAG pattern (retrieve from KB → prompt → LLM).

**Lambda handler** (`src/agentic_ai/lambda_handlers/action_group_handler.py`): Routes Bedrock Agent action group invocations by `apiPath` (`/calculate`, `/health`). Returns Bedrock-formatted responses.

**Config** (`src/agentic_ai/config.py`): Pydantic `BaseSettings` loading from `.env`. Singleton `settings` instance used throughout. AgentCore settings default to disabled. Chat UI settings: `CHAT_AGENT_TYPE`, `CHAT_PORT`, `CHAT_AUTH_SECRET`, `CHAT_AUTH_USERNAME`, `CHAT_AUTH_PASSWORD`, `CHAT_PERSISTENCE`, `CHAT_SQLITE_PATH`.

## Infrastructure

Terraform modules in `infra/modules/`: `iam`, `bedrock-agent`, `knowledge-base` (S3 + OpenSearch Serverless), `lambda-action-group`, `agentcore` (IAM, ECR, CloudWatch). Composed in `infra/envs/dev/`. AgentCore module is commented out by default.

## Testing

Tests mock AWS credentials via `conftest.py` autouse fixtures — no real AWS calls in unit tests. Test files mirror source structure under `tests/unit/`. AgentCore SDK classes are mocked in tests.

## CI

GitHub Actions (`.github/workflows/ci.yml`): ruff lint + format check, unit tests on all pushes; Terraform fmt + validate on main branch only.

## Key Dependencies

- `langchain-aws` + `langgraph` — agent orchestration on Bedrock
- `deepagents` — planning agent pattern
- `bedrock-agentcore` — AgentCore Runtime SDK (AG-UI/A2A serving)
- `langgraph-checkpoint-aws` — AgentCore Memory integration (checkpointer + store)
- `boto3`/`botocore[crt]` — AWS SDK
- `pydantic-settings` — env-based configuration
- `chainlit` — chat UI (optional, `pip install -e ".[chat]"`)
- `langgraph-checkpoint-sqlite` — SQLite persistence for chat (optional, included in chat extras)
- Default model: Claude Sonnet 4 (`us.anthropic.claude-sonnet-4-20250514-v1:0`)
