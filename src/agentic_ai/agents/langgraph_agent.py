"""LangGraph ReAct agent powered by AWS Bedrock.

This is the primary agent factory. It uses ChatBedrockConverse (the Converse API)
for unified tool calling across all Bedrock models, and LangGraph's prebuilt
create_react_agent for the tool-calling loop.

When AgentCore memory is enabled, agents persist state across invocations
via AgentCoreMemorySaver (checkpointer) and AgentCoreMemoryStore (long-term).

Usage:
    from agentic_ai.agents.langgraph_agent import create_agent

    agent = create_agent()
    result = agent.invoke({"messages": [("user", "What is 42 * 17?")]})
    print(result["messages"][-1].content)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from langchain.agents import create_agent as create_react_agent
from langchain_aws import ChatBedrockConverse

from agentic_ai.config import settings
from agentic_ai.memory import get_checkpointer, get_memory_store
from agentic_ai.tools import get_default_tools

if TYPE_CHECKING:
    from langchain_core.tools import BaseTool
    from langgraph.checkpoint.base import BaseCheckpointSaver
    from langgraph.graph.state import CompiledStateGraph
    from langgraph.store.base import BaseStore


def create_agent(
    model_id: str | None = None,
    tools: list[BaseTool] | None = None,
    system_prompt: str = (
        "You are a helpful AI assistant with access to tools. "
        "Use them when needed to answer questions accurately."
    ),
    checkpointer: BaseCheckpointSaver | None | object = ...,
    store: BaseStore | None | object = ...,
) -> CompiledStateGraph:
    """Create a ReAct agent backed by AWS Bedrock.

    Args:
        model_id: Bedrock model ID. Defaults to settings.bedrock_model_id.
        tools: List of LangChain tools. Defaults to get_default_tools().
        system_prompt: System prompt for the agent.
        checkpointer: State persistence. Defaults to AgentCore if enabled.
        store: Long-term memory store. Defaults to AgentCore if enabled.

    Returns:
        A compiled LangGraph graph that can be invoked or streamed.
    """
    if checkpointer is ...:
        checkpointer = get_checkpointer()
    if store is ...:
        store = get_memory_store()

    model = ChatBedrockConverse(
        model=model_id or settings.bedrock_model_id,
        region_name=settings.aws_region,
        temperature=0,
    )

    kwargs: dict = {
        "model": model,
        "tools": tools or get_default_tools(),
        "system_prompt": system_prompt,
    }
    if checkpointer is not None:
        kwargs["checkpointer"] = checkpointer
    if store is not None:
        kwargs["store"] = store

    agent = create_react_agent(**kwargs)

    return agent


def main() -> None:
    """CLI entry point for quick testing."""
    import sys

    agent = create_agent()
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What is 42 * 17?"

    print(f"Query: {query}\n")
    result = agent.invoke({"messages": [("user", query)]})
    print(f"Response: {result['messages'][-1].content}")


if __name__ == "__main__":
    main()
