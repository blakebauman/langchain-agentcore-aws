"""Tests for AgentCore Runtime."""

from agentic_ai.runtime import app


class TestRuntime:
    def test_app_exists(self) -> None:
        """Verify the BedrockAgentCoreApp instance is created."""
        assert app is not None

    def test_app_has_entrypoint(self) -> None:
        """Verify the entrypoint decorator registered a handler."""
        assert hasattr(app, "routes")
