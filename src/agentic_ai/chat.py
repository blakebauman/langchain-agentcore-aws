"""Chainlit chat UI for interacting with the LangGraph agent.

Provides a web-based chat interface with streaming responses, conversation
memory, and multi-session support. Uses the same agent factories and memory
system as the CLI and runtime entry points.

Features:
- Streaming token-by-token responses
- Chat profiles for switching between ReAct and Planning agents
- Tool call visualization via expandable steps
- Planning/reasoning step display for DeepAgent
- Optional password authentication
- File upload support for knowledge base queries
- Configurable persistence (memory, SQLite, or AgentCore)

Run via: chainlit run src/agentic_ai/chat.py --port 8000
Or:      make run-chat
"""

from __future__ import annotations

import collections
import logging
import os
import time
import uuid

import chainlit as cl

from agentic_ai.config import settings
from agentic_ai.observability import configure_tracing, get_tracer

logger = logging.getLogger(__name__)

# Configure OpenTelemetry tracing (opt-in via AGENTCORE_OBSERVABILITY_ENABLED)
configure_tracing()

# Bridge CHAT_AUTH_SECRET to Chainlit's expected env var
if settings.chat_auth_secret:
    os.environ["CHAINLIT_AUTH_SECRET"] = settings.chat_auth_secret

# Register SQLite data layer for conversation history sidebar
if settings.chat_persistence == "sqlite":
    from agentic_ai.chat_data import SQLiteDataLayer

    @cl.data_layer
    def get_data_layer() -> SQLiteDataLayer:
        return SQLiteDataLayer(db_path=settings.chat_sqlite_path)


# --- Health check endpoint ---
# Chainlit exposes its FastAPI app via cl.server.app after initialization.
# We register the route at module scope since chat.py is loaded by Chainlit.

try:
    from chainlit.server import app as _chainlit_app
    from starlette.responses import JSONResponse

    @_chainlit_app.get("/health")
    async def health_check() -> JSONResponse:
        return JSONResponse({"status": "healthy", "version": "0.2.0"})
except ImportError:
    pass


def _extract_text(content: object) -> str:
    """Extract plain text from LLM content (string or Bedrock content blocks)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(block.get("text", "") for block in content if isinstance(block, dict))
    return ""


async def _create_chat_agent(agent_type: str = "react"):
    """Create an agent configured for the chat UI.

    Uses get_chat_checkpointer() which returns the appropriate checkpointer
    based on the chat_persistence setting (memory, sqlite, or agentcore).
    When AgentCore memory is enabled, the MemoryStore provides per-user
    long-term semantic search across conversations.

    Args:
        agent_type: Which agent factory to use ("react" or "planning").
    """
    from agentic_ai.memory import get_chat_checkpointer, get_memory_store

    checkpointer = await get_chat_checkpointer()
    store = get_memory_store()

    if agent_type == "planning":
        from agentic_ai.agents.deep_agent import create_planning_agent

        return create_planning_agent(checkpointer=checkpointer, store=store)

    from agentic_ai.agents.langgraph_agent import create_agent

    return create_agent(checkpointer=checkpointer, store=store)


# --- Authentication (opt-in via CHAT_AUTH_SECRET + CHAT_AUTH_PASSWORD) ---


if settings.chat_auth_secret and settings.chat_auth_password:

    @cl.password_auth_callback
    async def auth_callback(username: str, password: str) -> cl.User | None:
        """Validate username/password when authentication is enabled."""
        if username == settings.chat_auth_username and password == settings.chat_auth_password:
            return cl.User(identifier=username, metadata={"role": "admin"})
        return None


# --- Chat profiles ---


@cl.set_chat_profiles
async def chat_profiles() -> list[cl.ChatProfile]:
    """Define selectable chat profiles for agent type switching."""
    return [
        cl.ChatProfile(
            name="ReAct Agent",
            markdown_description="Simple tool-calling agent for straightforward Q&A.",
            icon="https://cdn-icons-png.flaticon.com/512/4712/4712109.png",
            default=True,
        ),
        cl.ChatProfile(
            name="Planning Agent",
            markdown_description="Multi-step planning agent for complex research tasks.",
            icon="https://cdn-icons-png.flaticon.com/512/2620/2620389.png",
        ),
    ]


def _profile_to_agent_type(profile_name: str | None) -> str:
    """Map a chat profile name to an agent type string."""
    if profile_name == "Planning Agent":
        return "planning"
    return "react"


# --- Rate limiting ---

# Per-session sliding window of message timestamps
_rate_limit_windows: dict[str, collections.deque[float]] = {}


def _check_rate_limit(thread_id: str) -> bool:
    """Return True if the request is within rate limits, False if throttled."""
    if settings.chat_rate_limit <= 0:
        return True

    now = time.monotonic()
    window = _rate_limit_windows.setdefault(thread_id, collections.deque())

    # Remove timestamps older than 60 seconds
    while window and window[0] < now - 60:
        window.popleft()

    if len(window) >= settings.chat_rate_limit:
        return False

    window.append(now)
    return True


# --- Session lifecycle ---


@cl.on_chat_start
async def on_chat_start() -> None:
    """Initialize a new chat session with a fresh agent and thread ID."""
    profile = cl.user_session.get("chat_profile")
    agent_type = _profile_to_agent_type(profile)
    agent = await _create_chat_agent(agent_type)
    thread_id = str(uuid.uuid4())

    cl.user_session.set("agent", agent)
    cl.user_session.set("thread_id", thread_id)
    cl.user_session.set("agent_type", agent_type)

    logger.info(
        "Chat session started: thread_id=%s, agent_type=%s",
        thread_id,
        agent_type,
    )


@cl.on_message
async def on_message(msg: cl.Message) -> None:
    """Handle an incoming user message with streaming agent response."""
    agent = cl.user_session.get("agent")
    thread_id = cl.user_session.get("thread_id")

    if not _check_rate_limit(thread_id):
        await cl.Message(
            content=f"Rate limit exceeded ({settings.chat_rate_limit} messages/minute). "
            "Please wait before sending another message."
        ).send()
        return

    # Start OTel span for this conversation turn
    tracer = get_tracer()
    span = None
    if tracer:
        span = tracer.start_span(
            "chat.message",
            attributes={
                "chat.thread_id": thread_id,
                "chat.agent_type": cl.user_session.get("agent_type", "react"),
                "chat.message_length": len(msg.content),
            },
        )

    config = {"configurable": {"thread_id": thread_id}}

    # Build message content, including uploaded file text if present
    content = msg.content
    if msg.elements:
        file_texts = []
        for element in msg.elements:
            if hasattr(element, "path") and element.path:
                try:
                    with open(element.path) as f:
                        file_texts.append(f"[Uploaded file: {element.name}]\n{f.read()}")
                except (OSError, UnicodeDecodeError):
                    file_texts.append(
                        f"[Uploaded file: {element.name} — binary file, cannot read as text]"
                    )
        if file_texts:
            content = content + "\n\n" + "\n\n".join(file_texts)

    response = cl.Message(content="")
    active_steps: dict[str, cl.Step] = {}

    try:
        async for event in agent.astream_events(
            {"messages": [("user", content)]},
            config=config,
            version="v2",
        ):
            kind = event["event"]

            # Tool call started — open a step
            if kind == "on_tool_start":
                tool_name = event.get("name", "tool")
                run_id = event.get("run_id", "")
                step = cl.Step(name=tool_name, type="tool")
                step.input = str(event["data"].get("input", ""))
                await step.__aenter__()
                active_steps[run_id] = step

            # Tool call finished — close the step with output
            elif kind == "on_tool_end":
                run_id = event.get("run_id", "")
                step = active_steps.pop(run_id, None)
                if step:
                    step.output = str(event["data"].get("output", ""))
                    await step.__aexit__(None, None, None)

            # Planning/reasoning steps (DeepAgent sub-graphs)
            elif kind == "on_chain_start":
                chain_name = event.get("name", "")
                if chain_name and chain_name not in ("RunnableSequence", "LangGraph"):
                    run_id = event.get("run_id", "")
                    step = cl.Step(name=chain_name, type="run")
                    step.input = str(event["data"].get("input", ""))[:500]
                    await step.__aenter__()
                    active_steps[run_id] = step

            elif kind == "on_chain_end":
                run_id = event.get("run_id", "")
                step = active_steps.pop(run_id, None)
                if step:
                    output = event["data"].get("output", "")
                    step.output = str(output)[:500] if output else ""
                    await step.__aexit__(None, None, None)

            # LLM streaming tokens
            elif kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                token = _extract_text(chunk.content)
                if token:
                    await response.stream_token(token)

            # Capture final agent response as fallback
            elif kind == "on_chain_end" and event.get("name") == "LangGraph":
                output = event["data"].get("output", {})
                if isinstance(output, dict) and "messages" in output:
                    messages = output["messages"]
                    if messages:
                        last = messages[-1]
                        fallback = _extract_text(getattr(last, "content", ""))
                        if fallback and not response.content:
                            response.content = fallback

    except Exception:
        logger.exception("Error during agent invocation")
        if not response.content:
            response.content = (
                "Sorry, an error occurred while processing your request. Please try again."
            )
        if span:
            span.set_attribute("chat.error", True)
    finally:
        # Close any steps that didn't get an end event
        for step in active_steps.values():
            await step.__aexit__(None, None, None)
        if span:
            span.set_attribute("chat.response_length", len(response.content))
            span.end()

    await response.send()


@cl.on_chat_resume
async def on_chat_resume(thread: dict) -> None:
    """Resume a previous chat session by restoring the thread ID."""
    profile = cl.user_session.get("chat_profile")
    agent_type = _profile_to_agent_type(profile)
    agent = await _create_chat_agent(agent_type)
    thread_id = thread.get("id", str(uuid.uuid4()))

    cl.user_session.set("agent", agent)
    cl.user_session.set("thread_id", thread_id)
    cl.user_session.set("agent_type", agent_type)

    logger.info("Chat session resumed: thread_id=%s", thread_id)
