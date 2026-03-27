"""Memory factories for agent state persistence.

When AgentCore memory is enabled, agents get:
- Short-term memory (checkpointer): persists graph state across invocations
- Long-term memory (store): semantic search across conversation history

When disabled, agents use LangGraph's in-memory defaults.

For the chat UI, a SQLite checkpointer is available as a middle ground
between ephemeral in-memory and full AgentCore persistence.
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


def get_chat_checkpointer() -> BaseCheckpointSaver:
    """Return a checkpointer for chat UI persistence.

    Follows the chat_persistence setting:
    - "agentcore": uses AgentCore (delegates to get_checkpointer, falls back to memory)
    - "sqlite": persists to a local SQLite database
    - "memory": in-memory only (default, lost on restart)
    """
    if settings.chat_persistence == "agentcore":
        cp = get_checkpointer()
        if cp is not None:
            return cp

    if settings.chat_persistence == "sqlite":
        from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

        return AsyncSqliteSaver.from_conn_string(settings.chat_sqlite_path)

    from langgraph.checkpoint.memory import InMemorySaver

    return InMemorySaver()


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
