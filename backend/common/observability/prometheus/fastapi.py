from prometheus_client import Counter, Gauge, Histogram

from backend.core.conf import settings

_PROMETHEUS_FASTAPI_REQUEST_IN_PROGRESS_GAUGE = Gauge(
    name='fba_request_in_progress',
    documentation='Count in-progress FastAPI requests by method and path',
    labelnames=['app_name', 'method', 'path'],
)

_PROMETHEUS_FASTAPI_REQUEST_COUNTER = Counter(
    name='fba_request_total',
    documentation='Count total FastAPI requests by method and path',
    labelnames=['app_name', 'method', 'path'],
)

_PROMETHEUS_FASTAPI_REQUEST_COST_TIME_HISTOGRAM = Histogram(
    name='fba_request_cost_time',
    documentation='Histogram of FastAPI request duration by method and path (ms)',
    labelnames=['app_name', 'method', 'path'],
)

_PROMETHEUS_FASTAPI_EXCEPTION_COUNTER = Counter(
    name='fba_exception_total',
    documentation='Count FastAPI exceptions by method, path, and exception type',
    labelnames=['app_name', 'method', 'path', 'exception_type'],
)

_PROMETHEUS_FASTAPI_RESPONSE_COUNTER = Counter(
    name='fba_response_total',
    documentation='Count FastAPI responses by method, path, and status code',
    labelnames=['app_name', 'method', 'path', 'status_code'],
)


def inc_fastapi_request_in_progress(*, method: str, path: str) -> None:
    """Increment in-progress FastAPI request count"""
    _PROMETHEUS_FASTAPI_REQUEST_IN_PROGRESS_GAUGE.labels(
        app_name=settings.GRAFANA_PROMETHEUS_APP_NAME, method=method, path=path
    ).inc()


def dec_fastapi_request_in_progress(*, method: str, path: str) -> None:
    """Decrement in-progress FastAPI request count"""
    _PROMETHEUS_FASTAPI_REQUEST_IN_PROGRESS_GAUGE.labels(
        app_name=settings.GRAFANA_PROMETHEUS_APP_NAME, method=method, path=path
    ).dec()


def inc_fastapi_request(*, method: str, path: str) -> None:
    """Record total FastAPI requests"""
    _PROMETHEUS_FASTAPI_REQUEST_COUNTER.labels(
        app_name=settings.GRAFANA_PROMETHEUS_APP_NAME, method=method, path=path
    ).inc()


def observe_fastapi_request_cost_time(*, method: str, path: str, elapsed: float, trace_id: str) -> None:
    """Record FastAPI request duration"""
    _PROMETHEUS_FASTAPI_REQUEST_COST_TIME_HISTOGRAM.labels(
        app_name=settings.GRAFANA_PROMETHEUS_APP_NAME, method=method, path=path
    ).observe(amount=elapsed, exemplar={settings.GRAFANA_PROMETHEUS_EXEMPLAR_TRACE_ID_KEY: trace_id})


def inc_fastapi_exception(*, method: str, path: str, exception_type: str) -> None:
    """Record total FastAPI exceptions"""
    _PROMETHEUS_FASTAPI_EXCEPTION_COUNTER.labels(
        app_name=settings.GRAFANA_PROMETHEUS_APP_NAME, method=method, path=path, exception_type=exception_type
    ).inc()


def inc_fastapi_response(*, method: str, path: str, status_code: int | str) -> None:
    """Record total FastAPI responses"""
    _PROMETHEUS_FASTAPI_RESPONSE_COUNTER.labels(
        app_name=settings.GRAFANA_PROMETHEUS_APP_NAME, method=method, path=path, status_code=status_code
    ).inc()
