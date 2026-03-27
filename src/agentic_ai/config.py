"""Application configuration loaded from environment variables.

Supports optional AWS Secrets Manager integration: set SECRETS_ARN to load
secrets (e.g., CHAT_AUTH_SECRET, CHAT_AUTH_PASSWORD) from a Secrets Manager
JSON secret instead of environment variables or .env files.
"""

from __future__ import annotations

import json
import logging
import os

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


def _load_secrets_from_arn(secret_arn: str) -> None:
    """Load secrets from AWS Secrets Manager into environment variables.

    The secret value must be a JSON object with key-value pairs that map
    to setting names (e.g., {"CHAT_AUTH_SECRET": "...", "CHAT_AUTH_PASSWORD": "..."}).
    Values are set as environment variables so Pydantic picks them up.
    """
    try:
        import boto3

        region = os.environ.get("AWS_REGION", "us-east-1")
        client = boto3.client("secretsmanager", region_name=region)
        response = client.get_secret_value(SecretId=secret_arn)
        secrets = json.loads(response["SecretString"])
        for key, value in secrets.items():
            os.environ.setdefault(key.upper(), str(value))
        logger.info("Loaded secrets from %s", secret_arn)
    except Exception:
        logger.warning("Failed to load secrets from %s", secret_arn, exc_info=True)


# Load secrets before Settings initialization if SECRETS_ARN is set
_secrets_arn = os.environ.get("SECRETS_ARN", "")
if _secrets_arn:
    _load_secrets_from_arn(_secrets_arn)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    aws_profile: str | None = None
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "us.anthropic.claude-sonnet-4-20250514-v1:0"
    environment: str = "dev"
    log_level: str = "INFO"
    knowledge_base_id: str = ""
    s3_kb_bucket: str = ""
    secrets_arn: str = ""  # AWS Secrets Manager ARN for loading secrets

    # Chat UI settings
    chat_agent_type: str = "react"  # "react" or "planning"
    chat_port: int = 8000
    chat_auth_secret: str = ""  # Set to enable password authentication
    chat_auth_username: str = "admin"
    chat_auth_password: str = ""  # Required when chat_auth_secret is set
    chat_persistence: str = "memory"  # "memory", "sqlite", or "agentcore"
    chat_sqlite_path: str = ".chat_history.db"
    chat_rate_limit: int = 0  # Max messages per minute per session (0 = unlimited)
    chat_theme: str = ""  # Path to custom CSS file (relative to public/)

    # AgentCore settings (all opt-in)
    agentcore_memory_enabled: bool = False
    agentcore_gateway_enabled: bool = False
    agentcore_observability_enabled: bool = False
    agentcore_runtime_port: int = 8080
    agentcore_agent_name: str = "agentic-ai"


settings = Settings()
