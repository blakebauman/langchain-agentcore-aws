# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.2.0] - 2026-03-26

### Added

- Chainlit chat UI with streaming responses and conversation memory
- Chat profiles for switching between ReAct and Planning agents in the UI
- Tool call visualization with expandable steps showing inputs and outputs
- Planning/reasoning step display for DeepAgent sub-graphs
- Optional password authentication for the chat UI (`CHAT_AUTH_SECRET`)
- Configurable chat persistence: memory, SQLite, or AgentCore (`CHAT_PERSISTENCE`)
- File upload support — uploaded text files are included in agent context
- Error handling with user-friendly messages on agent failures
- Auto-include knowledge base tool when `KNOWLEDGE_BASE_ID` is set
- Docker support for the chat service (`docker/Dockerfile.chat`)
- `make run-chat` command for local development

### Changed

- CI now installs chat dependencies for full lint coverage

## [0.1.0] - 2026-03-26

### Added

- LangGraph ReAct agent with ChatBedrockConverse for unified tool calling
- DeepAgent with planning, sub-agent spawning, and context management
- Bedrock AgentCore integration (Memory, Runtime, Gateway, Observability)
- Terraform modules for Bedrock agents, knowledge bases, Lambda action groups, and IAM
- Tool registry with calculator, web search, and AgentCore Gateway discovery
- RAG chain with Bedrock Knowledge Base retrieval
- Lambda handler for Bedrock Agent action group invocations
- CI pipeline with ruff linting, format checking, and pytest
- Makefile-based development workflow
- Docker support for local development and Lambda deployment
