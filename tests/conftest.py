"""Shared test fixtures."""

import pytest


@pytest.fixture(autouse=True)
def _mock_aws_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set mock AWS credentials to prevent real API calls in tests."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("AWS_REGION", "us-east-1")


@pytest.fixture(autouse=True)
def _mock_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Override settings for testing."""
    monkeypatch.setenv("BEDROCK_MODEL_ID", "anthropic.claude-sonnet-4-20250514-v1:0")
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("KNOWLEDGE_BASE_ID", "")
