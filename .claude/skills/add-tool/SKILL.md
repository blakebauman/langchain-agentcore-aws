---
name: add-tool
description: Scaffold a new LangChain tool with tests and registry integration
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(make test *), Bash(python -m pytest *)
---

# Add New Tool

Scaffold a new tool for the agent toolkit.

## Arguments

Tool name and description: $ARGUMENTS

## Steps

1. Create `src/agentic_ai/tools/{tool_name}.py`:
   - Import `from langchain_core.tools import tool`
   - Define the function with `@tool` decorator
   - Include a clear docstring (this becomes the LLM's tool description)
   - Use `settings` for any configuration values

2. Register in `src/agentic_ai/tools/__init__.py`:
   - Import the new tool
   - Add it to `get_default_tools()` if it should be available by default
   - Or document that it requires configuration (like `query_knowledge_base`)

3. Create `tests/unit/test_{tool_name}.py`:
   - Test the tool's core functionality
   - Test edge cases and error handling
   - Mock any external API calls

4. If the tool should be callable from Bedrock Agent action groups:
   - Add a handler route in `src/agentic_ai/lambda_handlers/action_group_handler.py`
   - Note that the OpenAPI schema in `infra/modules/bedrock-agent/main.tf` needs updating

5. If the tool should also be registered in AgentCore Gateway:
   - Note that the Gateway discovers tools automatically — no code change needed
   - For tools NOT in `get_default_tools()`, follow the pattern in `tools/agentcore_builtins.py`

6. Run `make test` to verify everything passes
