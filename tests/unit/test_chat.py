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
    mock_cl.set_chat_profiles = lambda f: f
    mock_cl.password_auth_callback = lambda f: f
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
    @patch("agentic_ai.memory.get_chat_checkpointer", return_value=InMemorySaver())
    @patch("agentic_ai.memory.get_memory_store", return_value=None)
    @patch("agentic_ai.agents.langgraph_agent.create_react_agent")
    def test_passes_checkpointer_from_factory(
        self,
        mock_react: MagicMock,
        mock_store: MagicMock,
        mock_cp: MagicMock,
        mock_model_cls: object,
    ) -> None:
        from agentic_ai.chat import _create_chat_agent

        _create_chat_agent()
        call_kwargs = mock_react.call_args
        assert call_kwargs is not None
        all_kwargs = call_kwargs.kwargs if call_kwargs.kwargs else {}
        assert isinstance(all_kwargs.get("checkpointer"), InMemorySaver)

    @patch("agentic_ai.agents.langgraph_agent.ChatBedrockConverse")
    def test_creates_planning_agent_when_requested(self, mock_model_cls: object) -> None:
        with (
            patch("agentic_ai.memory.get_chat_checkpointer", return_value=InMemorySaver()),
            patch("agentic_ai.memory.get_memory_store", return_value=None),
            patch("agentic_ai.agents.deep_agent.create_planning_agent") as mock_plan,
        ):
            mock_plan.return_value = MagicMock()
            from agentic_ai.chat import _create_chat_agent

            _create_chat_agent(agent_type="planning")
            mock_plan.assert_called_once()


class TestProfileMapping:
    def test_react_profile(self) -> None:
        from agentic_ai.chat import _profile_to_agent_type

        assert _profile_to_agent_type("ReAct Agent") == "react"

    def test_planning_profile(self) -> None:
        from agentic_ai.chat import _profile_to_agent_type

        assert _profile_to_agent_type("Planning Agent") == "planning"

    def test_none_defaults_to_react(self) -> None:
        from agentic_ai.chat import _profile_to_agent_type

        assert _profile_to_agent_type(None) == "react"


class TestChatProfiles:
    async def test_returns_two_profiles(self) -> None:
        from agentic_ai.chat import chat_profiles

        profiles = await chat_profiles()
        assert len(profiles) == 2
