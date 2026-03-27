"""OpenTelemetry tracing integration for AgentCore.

When enabled, configures OTel tracing so all LangGraph/LangChain
invocations are traced and reported to AgentCore's observability backend.
"""

import logging

from agentic_ai.config import settings

logger = logging.getLogger(__name__)


def configure_tracing() -> None:
    """Set up OpenTelemetry tracing if agentcore_observability_enabled is True.

    Call this once at application startup (e.g., in runtime.py).
    No-ops when observability is disabled.
    """
    if not settings.agentcore_observability_enabled:
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor

        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))
        trace.set_tracer_provider(provider)

        logger.info("AgentCore OpenTelemetry tracing configured")
    except ImportError:
        logger.warning(
            "OpenTelemetry packages not installed. "
            "Install with: pip install opentelemetry-api opentelemetry-sdk "
            "opentelemetry-exporter-otlp-proto-grpc"
        )
