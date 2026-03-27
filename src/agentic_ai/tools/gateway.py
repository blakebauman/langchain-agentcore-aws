"""Tool discovery via AgentCore Gateway.

The Gateway transforms APIs and Lambda functions into MCP-compatible tools
with semantic discovery. When enabled, agents can dynamically discover
and use tools registered in the Gateway.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agentic_ai.config import settings

if TYPE_CHECKING:
    from langchain_core.tools import BaseTool


def get_gateway_tools() -> list[BaseTool]:
    """Discover tools from the AgentCore Gateway.

    Returns an empty list when agentcore_gateway_enabled is False.
    """
    if not settings.agentcore_gateway_enabled:
        return []

    # TODO: Replace with actual Gateway SDK integration once the
    # Gateway client API is available in bedrock-agentcore.
    # Expected pattern:
    #   from bedrock_agentcore.gateway import GatewayClient
    #   client = GatewayClient(region_name=settings.aws_region)
    #   return client.get_langchain_tools()
    return []
