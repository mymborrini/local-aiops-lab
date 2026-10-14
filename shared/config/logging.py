import json
import logging
from datetime import datetime, timezone
from shared.models import JobStatus


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


class AiOpsLog:
    def __init__(self, className):
        self.log = logging.getLogger(className)

    def info(self, message: str, **kwargs):
        self.log.info(message, extra=kwargs)

    def error(self, message: str, **kwargs):
        self.log.error(message, extra=kwargs)


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)

    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")
