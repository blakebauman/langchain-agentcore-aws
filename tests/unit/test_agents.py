"""Tests for agent factories."""

from unittest.mock import patch

from agentic_ai.tools.calculator import calculator


class TestCreateAgent:
    @patch("agentic_ai.agents.langgraph_agent.ChatBedrockConverse")
    def test_creates_agent_with_defaults(self, mock_model_cls: object) -> None:
        from agentic_ai.agents.langgraph_agent import create_agent

        agent = create_agent()
        assert agent is not None

    @patch("agentic_ai.agents.langgraph_agent.ChatBedrockConverse")
    def test_creates_agent_with_custom_tools(self, mock_model_cls: object) -> None:
        from agentic_ai.agents.langgraph_agent import create_agent

        agent = create_agent(tools=[calculator])
        assert agent is not None

    @patch("agentic_ai.agents.langgraph_agent.ChatBedrockConverse")
    def test_creates_agent_with_custom_prompt(self, mock_model_cls: object) -> None:
        from agentic_ai.agents.langgraph_agent import create_agent

        agent = create_agent(system_prompt="You are a math tutor.")
        assert agent is not None

    @patch("agentic_ai.agents.langgraph_agent.ChatBedrockConverse")
    def test_creates_agent_with_no_checkpointer(self, mock_model_cls: object) -> None:
        from agentic_ai.agents.langgraph_agent import create_agent

        agent = create_agent(checkpointer=None, store=None)
        assert agent is not None

    @patch("agentic_ai.agents.langgraph_agent.ChatBedrockConverse")
    def test_creates_agent_accepts_checkpointer(self, mock_model_cls: object) -> None:
        from langgraph.checkpoint.memory import InMemorySaver

        from agentic_ai.agents.langgraph_agent import create_agent

        agent = create_agent(checkpointer=InMemorySaver())
        assert agent is not None


class TestGetDefaultTools:
    def test_returns_expected_tools(self) -> None:
        from agentic_ai.tools import get_default_tools

        tools = get_default_tools()
        tool_names = [t.name for t in tools]
        assert "calculator" in tool_names
        assert "web_search" in tool_names

    def test_returns_list(self) -> None:
        from agentic_ai.tools import get_default_tools

        tools = get_default_tools()
        assert isinstance(tools, list)
        assert len(tools) >= 2
