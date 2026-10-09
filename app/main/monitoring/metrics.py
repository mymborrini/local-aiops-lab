from prometheus_client import Counter, Histogram

HTTP_REQUESTS = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"],
)

HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

HTTP_ERRORS = Counter(
    "http_errors_total",
    "Total number of HTTP errors",
    ["method", "endpoint"],
)
