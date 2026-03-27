"""AgentCore built-in tools: Code Interpreter and Browser.

These are NOT included in get_default_tools() — import them explicitly
when building agents that need code execution or web browsing.

Usage:
    from agentic_ai.tools.agentcore_builtins import get_code_interpreter_tool
    from agentic_ai.agents.langgraph_agent import create_agent

    agent = create_agent(tools=[get_code_interpreter_tool()])
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agentic_ai.config import settings

if TYPE_CHECKING:
    from langchain_core.tools import BaseTool


def get_code_interpreter_tool() -> BaseTool:
    """Return an AgentCore Code Interpreter tool.

    Provides secure, sandboxed Python code execution.
    Requires AgentCore infrastructure to be deployed.
    """
    from bedrock_agentcore.tools import CodeInterpreterTool

    return CodeInterpreterTool(region_name=settings.aws_region)


def get_browser_tool() -> BaseTool:
    """Return an AgentCore Browser tool.

    Provides cloud-based web automation for agents.
    Requires AgentCore infrastructure to be deployed.
    """
    from bedrock_agentcore.tools import BrowserTool

    return BrowserTool(region_name=settings.aws_region)
