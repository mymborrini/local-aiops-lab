import logging

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from shared.config.app_properties import (
    OTEL_SERVICE_NAME,
    OTEL_EXPORTER_OTLP_TRACES_ENDPOINT,
)


def configure_tracing() -> None:

    if OTEL_EXPORTER_OTLP_TRACES_ENDPOINT == None:
        return

    resource = Resource.create(
        {
            "service.name": OTEL_SERVICE_NAME,
            "deployment.environment.name": "local",
        }
    )

    provider = TracerProvider(resource=resource)

    exporter = OTLPSpanExporter(endpoint=OTEL_EXPORTER_OTLP_TRACES_ENDPOINT)

    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    logger = logging.getLogger(__name__)
    logger.info("Tracing configured successfully")
