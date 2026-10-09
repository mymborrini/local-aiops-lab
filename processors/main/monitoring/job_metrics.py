from prometheus_client import Counter, Gauge, Histogram

JOBS_PROCESSED = Counter(
    "jobs_processed_total",
    "Total number of job processing attempts",
    ["result"],
)

JOB_PROCESSING_DURATION = Histogram(
    "job_processing_duration_seconds",
    "Duration of job processing attempts in seconds",
)

JOB_RETRIES = Counter(
    "job_retries_total",
    "Total number of jobs requeued for retry",
)

JOBS_RUNNING = Gauge(
    "jobs_running",
    "Number of jobs currently being processed",
)
