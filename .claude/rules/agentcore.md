---
paths:
  - "src/agentic_ai/memory.py"
  - "src/agentic_ai/runtime.py"
  - "src/agentic_ai/observability.py"
  - "src/agentic_ai/tools/gateway.py"
  - "src/agentic_ai/tools/agentcore_builtins.py"
  - "infra/modules/agentcore/**/*.tf"
---

# AgentCore Conventions

- All AgentCore features are opt-in via `settings.agentcore_*` flags (default `False`). Never make AgentCore a hard dependency.
- Use lazy imports for `bedrock_agentcore` and `langgraph_checkpoint_aws` — always inside function bodies, never at module top level.
- `BedrockAgentCoreApp` is instantiated at module scope in `runtime.py`, but the agent is created inside the `@app.entrypoint` handler (not at import time).
- Memory factory functions (`get_checkpointer`, `get_memory_store`) must return `None` when disabled, not raise errors.
- The `memory_id` for AgentCore Memory is constructed as `{agentcore_agent_name}-{environment}` to namespace per-environment.
- Gateway-discovered tools are appended to (not replacing) local tools. Deduplicate by name, local tools take priority.
- AgentCore built-in tools (Code Interpreter, Browser) are NOT added to `get_default_tools()` — they must be explicitly imported and passed to agent factories.
