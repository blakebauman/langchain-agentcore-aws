"""DeepAgent for complex, long-running agentic tasks.

DeepAgent extends LangGraph with planning (todo lists), sub-agent spawning,
filesystem-backed context management, and long-term memory. Use this for
research-style or multi-step tasks that benefit from structured planning.

For simple tool-calling interactions, use langgraph_agent.py instead.

Usage:
    from agentic_ai.agents.deep_agent import create_planning_agent

    agent = create_planning_agent()
    result = agent.invoke({"messages": [("user", "Research and summarize...")]})
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from langchain_aws import ChatBedrockConverse

from agentic_ai.config import settings
from agentic_ai.memory import get_checkpointer, get_memory_store
from agentic_ai.tools import get_default_tools

if TYPE_CHECKING:
    from langchain_core.tools import BaseTool
    from langgraph.checkpoint.base import BaseCheckpointSaver
    from langgraph.graph.state import CompiledStateGraph
    from langgraph.store.base import BaseStore


def create_planning_agent(
    model_id: str | None = None,
    tools: list[BaseTool] | None = None,
    system_prompt: str = (
        "You are an expert planner and researcher. "
        "Break complex tasks into steps and execute them methodically."
    ),
    checkpointer: BaseCheckpointSaver | None | object = ...,
    store: BaseStore | None | object = ...,
) -> CompiledStateGraph:
    """Create a DeepAgent for complex, multi-step tasks.

    Args:
        model_id: Bedrock model ID. Defaults to settings.bedrock_model_id.
        tools: List of LangChain tools. Defaults to get_default_tools().
        system_prompt: System prompt for the agent.
        checkpointer: State persistence. Defaults to AgentCore if enabled.
        store: Long-term memory store. Defaults to AgentCore if enabled.

    Returns:
        A compiled LangGraph graph with planning capabilities.
    """
    if checkpointer is ...:
        checkpointer = get_checkpointer()
    if store is ...:
        store = get_memory_store()

    from deepagents import create_deep_agent

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

    agent = create_deep_agent(**kwargs)

    return agent
