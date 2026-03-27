# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
