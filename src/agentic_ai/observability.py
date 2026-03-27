"""OpenTelemetry tracing integration for AgentCore.

When enabled, configures OTel tracing so all LangGraph/LangChain
invocations are traced and reported to AgentCore's observability backend.

Supports both the AgentCore Runtime and the Chainlit chat UI.
"""

import logging

from agentic_ai.config import settings

logger = logging.getLogger(__name__)

_tracer = None


def configure_tracing() -> None:
    """Set up OpenTelemetry tracing if agentcore_observability_enabled is True.

    Call this once at application startup (e.g., in runtime.py or chat.py).
    No-ops when observability is disabled.
    """
    global _tracer  # noqa: PLW0603

    if not settings.agentcore_observability_enabled:
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor

        resource = Resource.create(
            {
                "service.name": f"{settings.agentcore_agent_name}-chat",
                "service.version": "0.2.0",
                "deployment.environment": settings.environment,
                "aws.region": settings.aws_region,
            }
        )

        provider = TracerProvider(resource=resource)
        provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))
        trace.set_tracer_provider(provider)
        _tracer = trace.get_tracer("agentic_ai.chat")

        logger.info("AgentCore OpenTelemetry tracing configured")
    except ImportError:
        logger.warning(
            "OpenTelemetry packages not installed. "
            "Install with: pip install opentelemetry-api opentelemetry-sdk "
            "opentelemetry-exporter-otlp-proto-grpc"
        )


def get_tracer():
    """Return the configured tracer, or None if tracing is disabled."""
    return _tracer
