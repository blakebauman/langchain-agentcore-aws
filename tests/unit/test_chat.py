"""Tests for chat UI module.

The _create_chat_agent helper is tested by mocking chainlit at import time,
since chat.py uses chainlit decorators at module scope.
"""

import sys
from unittest.mock import AsyncMock, MagicMock, patch

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
    mock_cl.data_layer = lambda f: f
    sys.modules["chainlit"] = mock_cl
    # Clear cached import so chat.py re-imports with mock
    sys.modules.pop("agentic_ai.chat", None)
    yield mock_cl
    sys.modules.pop("chainlit", None)
    sys.modules.pop("agentic_ai.chat", None)


class TestCreateChatAgent:
    @patch("agentic_ai.agents.langgraph_agent.ChatBedrockConverse")
    async def test_creates_react_agent_by_default(self, mock_model_cls: object) -> None:
        mock_cp = AsyncMock(return_value=InMemorySaver())
        with patch("agentic_ai.memory.get_chat_checkpointer", mock_cp):
            from agentic_ai.chat import _create_chat_agent

            agent = await _create_chat_agent()
            assert agent is not None

    @patch("agentic_ai.agents.langgraph_agent.ChatBedrockConverse")
    @patch("agentic_ai.memory.get_memory_store", return_value=None)
    @patch("agentic_ai.agents.langgraph_agent.create_react_agent")
    async def test_passes_checkpointer_from_factory(
        self,
        mock_react: MagicMock,
        mock_store: MagicMock,
        mock_model_cls: object,
    ) -> None:
        saver = InMemorySaver()
        mock_cp = AsyncMock(return_value=saver)
        with patch("agentic_ai.memory.get_chat_checkpointer", mock_cp):
            from agentic_ai.chat import _create_chat_agent

            await _create_chat_agent()
            call_kwargs = mock_react.call_args
            assert call_kwargs is not None
            all_kwargs = call_kwargs.kwargs or {}
            assert isinstance(all_kwargs.get("checkpointer"), InMemorySaver)

    @patch("agentic_ai.agents.langgraph_agent.ChatBedrockConverse")
    async def test_creates_planning_agent_when_requested(self, mock_model_cls: object) -> None:
        mock_cp = AsyncMock(return_value=InMemorySaver())
        with (
            patch("agentic_ai.memory.get_chat_checkpointer", mock_cp),
            patch("agentic_ai.memory.get_memory_store", return_value=None),
            patch("agentic_ai.agents.deep_agent.create_planning_agent") as mock_plan,
        ):
            mock_plan.return_value = MagicMock()
            from agentic_ai.chat import _create_chat_agent

            await _create_chat_agent(agent_type="planning")
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


class TestExtractText:
    def test_plain_string(self) -> None:
        from agentic_ai.chat import _extract_text

        assert _extract_text("hello") == "hello"

    def test_bedrock_content_blocks(self) -> None:
        from agentic_ai.chat import _extract_text

        blocks = [{"type": "text", "text": "Hello "}, {"type": "text", "text": "world"}]
        assert _extract_text(blocks) == "Hello world"

    def test_empty_list(self) -> None:
        from agentic_ai.chat import _extract_text

        assert _extract_text([]) == ""

    def test_none(self) -> None:
        from agentic_ai.chat import _extract_text

        assert _extract_text(None) == ""

    def test_mixed_blocks(self) -> None:
        from agentic_ai.chat import _extract_text

        blocks = [{"type": "text", "text": "hi"}, {"type": "tool_use", "id": "123"}]
        assert _extract_text(blocks) == "hi"


class TestRateLimiting:
    def test_allows_within_limit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("agentic_ai.config.settings.chat_rate_limit", 5)
        from agentic_ai.chat import _check_rate_limit, _rate_limit_windows

        _rate_limit_windows.clear()
        assert _check_rate_limit("test-thread") is True
        assert _check_rate_limit("test-thread") is True

    def test_blocks_over_limit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("agentic_ai.config.settings.chat_rate_limit", 2)
        from agentic_ai.chat import _check_rate_limit, _rate_limit_windows

        _rate_limit_windows.clear()
        assert _check_rate_limit("test-thread") is True
        assert _check_rate_limit("test-thread") is True
        assert _check_rate_limit("test-thread") is False

    def test_unlimited_when_zero(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("agentic_ai.config.settings.chat_rate_limit", 0)
        from agentic_ai.chat import _check_rate_limit, _rate_limit_windows

        _rate_limit_windows.clear()
        for _ in range(100):
            assert _check_rate_limit("test-thread") is True
