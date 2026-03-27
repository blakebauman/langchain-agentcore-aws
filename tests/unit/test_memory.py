"""Tests for memory factory functions."""

from unittest.mock import patch

import pytest


class TestGetCheckpointer:
    def test_returns_none_when_disabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("AGENTCORE_MEMORY_ENABLED", "false")
        # Re-import to pick up env change
        from agentic_ai.memory import get_checkpointer

        result = get_checkpointer()
        assert result is None

    @patch("agentic_ai.memory.AgentCoreMemorySaver", create=True)
    def test_returns_saver_when_enabled(
        self, mock_saver_cls: object, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr("agentic_ai.memory.settings.agentcore_memory_enabled", True)
        monkeypatch.setattr("agentic_ai.memory.settings.agentcore_agent_name", "test-agent")
        monkeypatch.setattr("agentic_ai.memory.settings.environment", "test")
        monkeypatch.setattr("agentic_ai.memory.settings.aws_region", "us-east-1")

        with (
            patch("agentic_ai.memory.AgentCoreMemorySaver", create=True) as mock_cls,
            patch.dict(
                "sys.modules",
                {"langgraph_checkpoint_aws": type("mod", (), {"AgentCoreMemorySaver": mock_cls})},
            ),
        ):
            from agentic_ai.memory import get_checkpointer

            result = get_checkpointer()
            mock_cls.assert_called_once_with(
                memory_id="test-agent-test",
                region_name="us-east-1",
            )
            assert result is not None


class TestGetMemoryStore:
    def test_returns_none_when_disabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("AGENTCORE_MEMORY_ENABLED", "false")
        from agentic_ai.memory import get_memory_store

        result = get_memory_store()
        assert result is None
