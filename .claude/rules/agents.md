---
paths:
  - "src/agentic_ai/agents/**/*.py"
  - "src/agentic_ai/memory.py"
  - "src/agentic_ai/runtime.py"
---

# Agent Conventions

- Agent factories return `CompiledStateGraph` from LangGraph. All agents share the same invocation interface: `agent.invoke({"messages": [("user", query)]})`.
- `create_agent()` (LangGraph ReAct) is for simple tool-calling. `create_planning_agent()` (DeepAgent) is for multi-step reasoning.
- Both factories accept optional `model_id`, `tools`, `system_prompt`, `checkpointer`, and `store` — defaulting to `settings.bedrock_model_id`, `get_default_tools()`, and memory from `get_checkpointer()`/`get_memory_store()`.
- The LLM is always `ChatBedrockConverse` from `langchain_aws`. Do not use `ChatBedrock` (legacy).
- Set `temperature=0` for deterministic agent behavior.
- Use the sentinel `...` (Ellipsis) as the default for `checkpointer` and `store` params so callers can explicitly pass `None` to disable memory.
- AgentCore Memory is opt-in: `get_checkpointer()` and `get_memory_store()` return `None` when `agentcore_memory_enabled=False`.
- AgentCore Runtime (`runtime.py`) wraps agents with `BedrockAgentCoreApp` using the `@app.entrypoint` decorator. Do not instantiate the agent inside the module scope — create it inside the handler function.
