"""Tool registry for agentic workflows."""

from langchain_core.tools import BaseTool

from agentic_ai.config import settings

from .calculator import calculator
from .web_search import web_search


def get_default_tools() -> list[BaseTool]:
    """Return the default set of tools available to agents.

    Includes local tools and, when enabled, tools discovered via AgentCore Gateway.
    The knowledge_base tool is excluded because it requires deployed infrastructure.
    """
    tools: list[BaseTool] = [calculator, web_search]

    if settings.agentcore_gateway_enabled:
        from .gateway import get_gateway_tools

        gateway_tools = get_gateway_tools()
        # Deduplicate by name — local tools take priority
        local_names = {t.name for t in tools}
        tools.extend(t for t in gateway_tools if t.name not in local_names)

    return tools
