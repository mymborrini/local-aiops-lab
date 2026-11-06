import json
import logging
from datetime import datetime, timezone
import urllib
from shared.config.app_properties import SERVICE_NAME, LOKI_URL, OTEL_EXPORTER_OTLP_LOGS_ENDPOINT, OTEL_SERVICE_NAME
from opentelemetry import trace

from opentelemetry import _logs
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from uuid import UUID


class JsonFormatter(logging.Formatter):
    RESERVED = {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
        "message",
        "taskName",
    }

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        span_context = trace.get_current_span().get_span_context()

        if span_context.is_valid:
            log_entry["trace_id"] = format(span_context.trace_id, "032x")
            log_entry["span_id"] = format(span_context.span_id, "016x")

        for key, value in record.__dict__.items():
            if key not in self.RESERVED and not key.startswith("_"):
                log_entry[key] = value

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, default=str)


class LokiHandler(logging.Handler):
    def __init__(self, url: str, service: str):
        super().__init__()
        self.url = f"{url.rstrip('/')}/loki/api/v1/push"
        self.service = service

    def emit(self, record: logging.LogRecord) -> None:
        try:
            log_line = self.format(record)

            payload = {
                "streams": [
                    {
                        "stream": {
                            "service": self.service,
                            "env": "local",
                        },
                        "values": [
                            [
                                str(int(record.created * 1_000_000_000)),
                                log_line,
                            ]
                        ],
                    }
                ]
            }

            request = urllib.request.Request(
                self.url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            with urllib.request.urlopen(request, timeout=1.5) as response:
                response.read()
        except Exception:
            self.handleError(record=record)


class AiOpsLog:
    def __init__(self, className):
        self.log = logging.getLogger(className)

    def info(self, message: str, **kwargs):
        self.log.info(message, extra=self.otel_attributes(**kwargs))

    def error(self, message: str, **kwargs):
        self.log.error(message, extra=self.otel_attributes(**kwargs))

    def otel_attributes(self, **kwargs) -> dict:
        return {
            key: str(value) if isinstance(value, UUID) else value
            for key, value in kwargs.items()
        }

class OTLPHanlder:

    def __init__(self, endpoint: str, service: str):
        self.endpoint = endpoint
        self.service = service

    def configure_otel_handler(self):
        if (OTEL_EXPORTER_OTLP_LOGS_ENDPOINT is None):
            return

        resource = Resource.create({
            "service.name": SERVICE_NAME,
            "deployment.environment.name": "local"
        })

        logging_provider = LoggerProvider(resource=resource)
        exporter = OTLPLogExporter(endpoint=OTEL_EXPORTER_OTLP_LOGS_ENDPOINT)

        # Export logs in batch
        logging_provider.add_log_record_processor(
            BatchLogRecordProcessor(exporter=exporter)
        )

        _logs.set_logger_provider(logger_provider=logging_provider)
        return LoggingHandler(
            level=logging.INFO,
            logger_provider=logging_provider
        )



def configure_logging() -> None:
    formatter = JsonFormatter()
    console_handler = logging.StreamHandler()

    console_handler.setFormatter(formatter)
    handlers = [console_handler]

    if LOKI_URL:
        loki_handler = LokiHandler(
            url=LOKI_URL,
            service=SERVICE_NAME,
        )
        loki_handler.setFormatter(formatter)
        handlers.append(loki_handler)

    elif OTEL_EXPORTER_OTLP_LOGS_ENDPOINT:
        otlp_handler = OTLPHanlder(endpoint=OTEL_EXPORTER_OTLP_LOGS_ENDPOINT, service=SERVICE_NAME).configure_otel_handler()
        handlers.append(otlp_handler)

    logging.basicConfig(level=logging.INFO, handlers=handlers, force=True)

    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")
