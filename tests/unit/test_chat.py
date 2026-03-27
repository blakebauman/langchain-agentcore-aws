"""Tests for chat UI module.

The _create_chat_agent helper is tested by mocking chainlit at import time,
since chat.py uses chainlit decorators at module scope.
"""

import sys
from unittest.mock import MagicMock, patch

import pytest
from langgraph.checkpoint.memory import InMemorySaver


@pytest.fixture(autouse=True)
def _mock_chainlit():
    """Mock chainlit module to avoid config file loading during tests."""
    mock_cl = MagicMock()
    # Make decorators pass through the original function
    mock_cl.on_chat_start = lambda f: f
    mock_cl.on_message = lambda f: f
    mock_cl.on_chat_resume = lambda f: f
    sys.modules["chainlit"] = mock_cl
    # Clear cached import so chat.py re-imports with mock
    sys.modules.pop("agentic_ai.chat", None)
    yield mock_cl
    sys.modules.pop("chainlit", None)
    sys.modules.pop("agentic_ai.chat", None)


class TestCreateChatAgent:
    @patch("agentic_ai.agents.langgraph_agent.ChatBedrockConverse")
    def test_creates_react_agent_by_default(self, mock_model_cls: object) -> None:
        from agentic_ai.chat import _create_chat_agent

        agent = _create_chat_agent()
        assert agent is not None

    @patch("agentic_ai.agents.langgraph_agent.ChatBedrockConverse")
    def test_injects_in_memory_saver_when_agentcore_disabled(self, mock_model_cls: object) -> None:
        from agentic_ai.chat import _create_chat_agent

        with (
            patch("agentic_ai.memory.get_checkpointer", return_value=None),
            patch("agentic_ai.memory.get_memory_store", return_value=None),
            patch("agentic_ai.agents.langgraph_agent.create_react_agent") as mock_react,
        ):
            _create_chat_agent()
            call_kwargs = mock_react.call_args
            assert call_kwargs is not None
            all_kwargs = call_kwargs.kwargs if call_kwargs.kwargs else {}
            assert isinstance(all_kwargs.get("checkpointer"), InMemorySaver)

    @patch("agentic_ai.agents.langgraph_agent.ChatBedrockConverse")
    def test_uses_agentcore_checkpointer_when_provided(self, mock_model_cls: object) -> None:
        mock_checkpointer = MagicMock()

        with (
            patch("agentic_ai.memory.get_checkpointer", return_value=mock_checkpointer),
            patch("agentic_ai.memory.get_memory_store", return_value=None),
            patch("agentic_ai.agents.langgraph_agent.create_react_agent") as mock_react,
        ):
            from agentic_ai.chat import _create_chat_agent

            _create_chat_agent()
            call_kwargs = mock_react.call_args
            assert call_kwargs is not None
            all_kwargs = call_kwargs.kwargs if call_kwargs.kwargs else {}
            assert all_kwargs.get("checkpointer") is mock_checkpointer
