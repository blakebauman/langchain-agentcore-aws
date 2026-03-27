---
name: run-runtime
description: Start the AgentCore Runtime server for AG-UI protocol serving
user-invocable: true
allowed-tools: Bash(make run-runtime *), Bash(source *), Read
---

# Run AgentCore Runtime

Start the BedrockAgentCoreApp server that serves the agent via the AG-UI protocol.

## Behavior

1. Run `make run-runtime`
2. The server starts on the port configured by `AGENTCORE_RUNTIME_PORT` (default 8080)
3. If it fails, diagnose the error:
   - Missing `bedrock-agentcore` package → `make install`
   - Port already in use → suggest changing `AGENTCORE_RUNTIME_PORT` in `.env`
   - AWS credential issues → check `aws configure` and `AWS_PROFILE` in `.env`
