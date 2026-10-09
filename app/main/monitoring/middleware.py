from app.main.monitoring.metrics import *

from starlette.requests import Request
from starlette.responses import Response
import time

async def prometheus_middleware(
        request: Request,
        call_next,
) -> Response:

    start_time = time.perf_counter()

    response = await call_next(request)

    duration = time.perf_counter() - start_time

    method = request.method
    endpoint = request.scope.get("route")

    if endpoint is not None:
        endpoint = endpoint.path
    else:
        endpoint = "unmatched"

    status = str(response.status_code)

    HTTP_REQUESTS.labels(
        method=method,
        endpoint=endpoint,
        status=status,
    ).inc()

    HTTP_REQUEST_DURATION.labels(
        method=method,
        endpoint=endpoint,
    ).observe(duration)

    if response.status_code >= 400:
        HTTP_ERRORS.labels(
            method=method,
            endpoint=endpoint,
        ).inc()

    return response
