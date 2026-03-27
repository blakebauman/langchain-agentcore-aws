"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    aws_profile: str = "default"
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "us.anthropic.claude-sonnet-4-20250514-v1:0"
    environment: str = "dev"
    log_level: str = "INFO"
    knowledge_base_id: str = ""
    s3_kb_bucket: str = ""

    # Chat UI settings
    chat_agent_type: str = "react"  # "react" or "planning"
    chat_port: int = 8000

    # AgentCore settings (all opt-in)
    agentcore_memory_enabled: bool = False
    agentcore_gateway_enabled: bool = False
    agentcore_observability_enabled: bool = False
    agentcore_runtime_port: int = 8080
    agentcore_agent_name: str = "agentic-ai"


settings = Settings()
