"""AgentCore Runtime entrypoint.

Wraps the LangGraph agent with BedrockAgentCoreApp for deployment
to AgentCore Runtime via the AG-UI protocol.

Usage:
    python -m agentic_ai.runtime

Or via Makefile:
    make run-runtime
"""

from __future__ import annotations

import logging

from bedrock_agentcore import BedrockAgentCoreApp

from agentic_ai.agents.langgraph_agent import create_agent
from agentic_ai.config import settings
from agentic_ai.observability import configure_tracing

logger = logging.getLogger(__name__)

app = BedrockAgentCoreApp()


@app.entrypoint
async def handle_request(context: dict, message: str) -> str:
    """AG-UI entrypoint: receives a message and returns the agent's response."""
    agent = create_agent()
    result = agent.invoke({"messages": [("user", message)]})
    return result["messages"][-1].content


def main() -> None:
    """Start the AgentCore Runtime server."""
    configure_tracing()

    logger.info(
        "Starting AgentCore Runtime on port %d",
        settings.agentcore_runtime_port,
    )
    app.run(port=settings.agentcore_runtime_port)


if __name__ == "__main__":
    main()
