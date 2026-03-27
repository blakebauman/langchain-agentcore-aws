---
name: aws-bedrock-agentcore
description: Look up Bedrock AgentCore Runtime, Memory, Gateway, Observability, and built-in tools
user-invocable: true
allowed-tools: WebSearch, WebFetch(domain:docs.aws.amazon.com), WebFetch(domain:aws.amazon.com), WebFetch(domain:pypi.org), WebFetch(domain:github.com), Read, Grep, Glob
---

# AWS Bedrock AgentCore Guidance

Look up Bedrock AgentCore documentation for Runtime (AG-UI), Memory, Gateway, Observability, and built-in tools.

## Arguments

Topic or question: $ARGUMENTS

## Behavior

1. Search AgentCore documentation using WebSearch and fetch from docs.aws.amazon.com
2. Read project code to understand current AgentCore usage:
   - `src/agentic_ai/runtime.py` for BedrockAgentCoreApp and AG-UI protocol
   - `src/agentic_ai/memory.py` for AgentCoreMemorySaver and AgentCoreMemoryStore
   - `src/agentic_ai/tools/gateway.py` for Gateway tool discovery
   - `src/agentic_ai/observability.py` for OpenTelemetry tracing setup
   - `src/agentic_ai/tools/agentcore_builtins.py` for built-in tools (Code Interpreter, Browser)
   - `src/agentic_ai/config.py` for `agentcore_*` settings
3. All AgentCore features are opt-in via environment variables (default disabled). Remind users which env var enables the feature:
   - Runtime: always available, started via `make run-runtime`
   - Memory: `AGENTCORE_MEMORY_ENABLED=true`
   - Gateway: `AGENTCORE_GATEWAY_ENABLED=true`
   - Observability: `AGENTCORE_OBSERVABILITY_ENABLED=true`
4. For Memory questions, explain the two components: checkpointer (short-term state) and store (long-term semantic search), both namespaced by `{agent_name}-{environment}`
5. For Gateway questions, note it discovers MCP-compatible tools and appends them to local tools (local tools take priority when names collide)
6. Cite specific documentation URLs for every recommendation
