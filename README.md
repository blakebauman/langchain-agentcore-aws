# Agentic AI AWS

[![CI](https://github.com/blakebauman/langchain-agentcore-aws/actions/workflows/ci.yml/badge.svg)](https://github.com/blakebauman/langchain-agentcore-aws/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Foundation for building agentic AI workflows on AWS Bedrock using LangGraph and DeepAgent.

## Architecture

- **LangGraph Agent** — ReAct-style agent using `ChatBedrockConverse` for unified tool calling across Bedrock models
- **DeepAgent** — Extended agent with planning, sub-agent spawning, and context management for complex tasks
- **Terraform** — Modular IaC for Bedrock agents, knowledge bases, Lambda action groups, and IAM

## Prerequisites

- Python 3.11+
- AWS account with Bedrock model access enabled (Claude, Titan Embeddings)
- Terraform >= 1.7
- AWS CLI configured (`aws configure`)

## Quick Start

```bash
# 1. Install dependencies
make install

# 2. Configure environment
cp .env.example .env
# Edit .env with your AWS settings

# 3. Run linter and tests
make lint && make test

# 4. Deploy infrastructure
make infra-init
make infra-plan
make infra-apply

# 5. Run the agent
make run-agent
```

## Project Structure

```
src/agentic_ai/
├── config.py              # Pydantic settings from env vars
├── agents/
│   ├── langgraph_agent.py # ReAct agent (simple tool calling)
│   └── deep_agent.py      # DeepAgent (complex planning tasks)
├── tools/                 # LangChain @tool definitions
├── chains/                # Non-agent chains (RAG, etc.)
└── lambda_handlers/       # Bedrock agent action group handlers

infra/
├── modules/               # Reusable Terraform modules
│   ├── iam/               # Bedrock + Lambda IAM roles
│   ├── bedrock-agent/     # Managed Bedrock agent
│   ├── knowledge-base/    # S3 + OpenSearch + KB
│   └── lambda-action-group/
└── envs/dev/              # Dev environment composition
```

## Adding a New Tool

```python
# src/agentic_ai/tools/my_tool.py
from langchain_core.tools import tool

@tool
def my_tool(query: str) -> str:
    """Description of what this tool does."""
    return "result"
```

Then register it in `src/agentic_ai/tools/__init__.py`.

## Adding a New Agent

```python
from agentic_ai.agents.langgraph_agent import create_agent
from agentic_ai.tools.my_tool import my_tool

agent = create_agent(
    tools=[my_tool],
    system_prompt="You are a specialized assistant.",
)
result = agent.invoke({"messages": [("user", "Hello")]})
```

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on bug reports, feature requests, and pull requests.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
