"""Custom middleware for Prometheus metrics collection."""

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from prometheus_client import Counter, Histogram, Gauge

# Prometheus Metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests in progress",
    ["method", "endpoint"],
)

# Business Metrics
DEPLOYMENT_COUNT = Counter(
    "deployments_total",
    "Total deployments tracked",
    ["environment", "status"],
)

INCIDENT_COUNT = Counter(
    "incidents_total",
    "Total incidents tracked",
    ["severity", "status"],
)

MTTR_HISTOGRAM = Histogram(
    "incident_mttr_seconds",
    "Mean Time to Recovery in seconds",
    ["severity"],
    buckets=[60, 300, 900, 1800, 3600, 7200, 14400, 28800, 86400],
)

DEPLOYMENT_FREQUENCY = Gauge(
    "deployment_frequency_per_day",
    "Deployments per day (DORA metric)",
    ["environment"],
)

CHANGE_FAILURE_RATE = Gauge(
    "change_failure_rate",
    "Percentage of deployments causing failures (DORA metric)",
    ["environment"],
)


class RequestMetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to track request metrics for Prometheus."""

    async def dispatch(self, request: Request, call_next) -> Response:
        method = request.method
        endpoint = request.url.path

        # Skip metrics endpoint itself
        if endpoint == "/metrics":
            return await call_next(request)

        REQUESTS_IN_PROGRESS.labels(method=method, endpoint=endpoint).inc()
        start_time = time.time()

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as exc:
            status_code = 500
            raise exc
        finally:
            duration = time.time() - start_time
            REQUEST_COUNT.labels(
                method=method, endpoint=endpoint, status_code=status_code
            ).inc()
            REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)
            REQUESTS_IN_PROGRESS.labels(method=method, endpoint=endpoint).dec()

        return response
