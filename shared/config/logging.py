import json
import logging
from datetime import datetime, timezone
import urllib
import os
from shared.config.app_properties import SERVICE_NAME, LOKI_URL

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
        self.log.info(message, extra=kwargs)

    def error(self, message: str, **kwargs):
        self.log.error(message, extra=kwargs)


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

    logging.basicConfig(level=logging.INFO, handlers=handlers, force=True)

    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")
