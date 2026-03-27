"""Chainlit chat UI for interacting with the LangGraph agent.

Provides a web-based chat interface with streaming responses, conversation
memory, and multi-session support. Uses the same agent factories and memory
system as the CLI and runtime entry points.

Run via: chainlit run src/agentic_ai/chat.py --port 8000
Or:      make run-chat
"""

from __future__ import annotations

import logging
import uuid

import chainlit as cl

from agentic_ai.config import settings

logger = logging.getLogger(__name__)


def _create_chat_agent():
    """Create an agent configured for the chat UI.

    Uses InMemorySaver as a fallback checkpointer when AgentCore memory is
    disabled, so conversation history is preserved within a running session.
    """
    from langgraph.checkpoint.memory import InMemorySaver

    from agentic_ai.memory import get_checkpointer, get_memory_store

    checkpointer = get_checkpointer()
    store = get_memory_store()

    # Fall back to in-memory checkpointer so chat history works locally
    if checkpointer is None:
        checkpointer = InMemorySaver()

    if settings.chat_agent_type == "planning":
        from agentic_ai.agents.deep_agent import create_planning_agent

        return create_planning_agent(checkpointer=checkpointer, store=store)

    from agentic_ai.agents.langgraph_agent import create_agent

    return create_agent(checkpointer=checkpointer, store=store)


@cl.on_chat_start
async def on_chat_start() -> None:
    """Initialize a new chat session with a fresh agent and thread ID."""
    agent = _create_chat_agent()
    thread_id = str(uuid.uuid4())

    cl.user_session.set("agent", agent)
    cl.user_session.set("thread_id", thread_id)

    logger.info(
        "Chat session started: thread_id=%s, agent_type=%s",
        thread_id,
        settings.chat_agent_type,
    )


@cl.on_message
async def on_message(msg: cl.Message) -> None:
    """Handle an incoming user message with streaming agent response."""
    agent = cl.user_session.get("agent")
    thread_id = cl.user_session.get("thread_id")
    config = {"configurable": {"thread_id": thread_id}}

    response = cl.Message(content="")

    async for event in agent.astream_events(
        {"messages": [("user", msg.content)]},
        config=config,
        version="v2",
    ):
        if event["event"] == "on_chat_model_stream":
            chunk = event["data"]["chunk"]
            token = chunk.content if isinstance(chunk.content, str) else ""
            if token:
                await response.stream_token(token)

    await response.send()


@cl.on_chat_resume
async def on_chat_resume(thread: dict) -> None:
    """Resume a previous chat session by restoring the thread ID."""
    agent = _create_chat_agent()
    thread_id = thread.get("id", str(uuid.uuid4()))

    cl.user_session.set("agent", agent)
    cl.user_session.set("thread_id", thread_id)

    logger.info("Chat session resumed: thread_id=%s", thread_id)
