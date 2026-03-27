"""Memory factories for agent state persistence.

When AgentCore memory is enabled, agents get:
- Short-term memory (checkpointer): persists graph state across invocations
- Long-term memory (store): semantic search across conversation history

When disabled, agents use LangGraph's in-memory defaults.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agentic_ai.config import settings

if TYPE_CHECKING:
    from langgraph.checkpoint.base import BaseCheckpointSaver
    from langgraph.store.base import BaseStore


def get_checkpointer() -> BaseCheckpointSaver | None:
    """Return a checkpointer for agent state persistence.

    Returns AgentCoreMemorySaver when agentcore_memory_enabled=True,
    otherwise None (agent runs stateless).
    """
    if not settings.agentcore_memory_enabled:
        return None

    from langgraph_checkpoint_aws import AgentCoreMemorySaver

    return AgentCoreMemorySaver(
        memory_id=f"{settings.agentcore_agent_name}-{settings.environment}",
        region_name=settings.aws_region,
    )


def get_memory_store() -> BaseStore | None:
    """Return a long-term memory store for semantic search.

    Returns AgentCoreMemoryStore when agentcore_memory_enabled=True,
    otherwise None.
    """
    if not settings.agentcore_memory_enabled:
        return None

    from langgraph_checkpoint_aws import AgentCoreMemoryStore

    return AgentCoreMemoryStore(
        memory_id=f"{settings.agentcore_agent_name}-{settings.environment}",
        region_name=settings.aws_region,
    )
