---
name: run-agent
description: Run the LangGraph agent with a query against AWS Bedrock
user-invocable: true
allowed-tools: Bash(make run-agent *), Bash(source *), Read
---

# Run Agent

Execute the LangGraph ReAct agent with a query.

## Behavior

1. Run `make run-agent QUERY="$ARGUMENTS"`
2. Display the agent's response
3. If it fails (missing credentials, model access, etc.), diagnose the error and suggest fixes
4. To run with AgentCore memory: `AGENTCORE_MEMORY_ENABLED=true make run-agent QUERY="..."`
5. To start the AG-UI runtime server instead, use `/run-runtime`
