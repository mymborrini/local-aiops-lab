from prometheus_client import Counter, Histogram, Gauge

OUTBOX_EVENTS_PROCESSED = Counter(
    "outbox_events_processed_total",
    "Total number of outbox events processed",
    ["result"],
)

OUTBOX_PROCESSING_DURATION = Histogram(
    "outbox_processing_duration_seconds",
    "Time spent processing outbox events",
)

OUTBOX_PENDING_EVENTS = Gauge(
    "outbox_pending_events",
    "Number of pending outbox events",
)